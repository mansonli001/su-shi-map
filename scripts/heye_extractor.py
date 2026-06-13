#!/usr/bin/env python3
"""
贺野文章批量提取脚本（零外部 API 依赖版）

工作流程（两步分离）：
  步骤 1 — 提取文本：PDF → 清洗文本 → 生成 LLM prompt 文件
  步骤 2 — 合并结果：LLM 输出的 JSON → 合并到 CSV

不调用任何外部 API 服务，LLM 提取步骤由 IDE 内置 LLM 完成。

用法：
    # 步骤 1：提取 PDF 文本，生成 prompt 文件
    python heye_extractor.py extract --dir ./pdfs --out-dir ./prompts
    python heye_extractor.py extract --file 某篇文章.pdf --out-dir ./prompts

    # 步骤 2：将 IDE 内置 LLM 的 JSON 输出合并到 CSV
    python heye_extractor.py merge --json ./prompts/HY001_result.json --out heye_locations.csv
    python heye_extractor.py merge --json-dir ./prompts --out heye_locations.csv
"""

import os
import re
import csv
import json
import argparse
import pdfplumber
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# 1. 从 PDF 提取并清洗文本
# ─────────────────────────────────────────────

TAIL_PATTERNS = [
    r'往期回顾',
    r'BREAKAWAY',
    r'《有生余年》读者精选',
    r'关注得独家',
    r'扫码关注我',
]


def extract_text(pdf_path: str) -> dict:
    """
    返回：{
        title, date, region,   # 从第一行解析
        body,                  # 清洗后正文
        raw_chars,             # 原始字符数（用于debug）
    }
    """
    raw = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                raw += t + "\n"

    # 截断尾部模板
    tail_re = "|".join(TAIL_PATTERNS)
    body = re.split(tail_re, raw)[0]

    # 去掉"点击关注 真实的生活与旅行"这类固定短语
    body = re.sub(r'点击关注\s*真实的生活与旅行', '', body)

    # 压缩空行
    body = re.sub(r'\n{3,}', '\n\n', body).strip()

    # 解析第一行（标题）和第二行（元数据）
    lines = body.split('\n')
    title = lines[0].strip() if lines else ""

    date, region = "", ""
    if len(lines) > 1:
        meta = lines[1]
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', meta)
        if date_match:
            date = date_match.group(1)
        region_match = re.search(r'\d{2}:\d{2}:\d{2}\s+(.+)$', meta)
        if region_match:
            region = region_match.group(1).strip()

    return {
        "title": title,
        "date": date,
        "region": region,
        "body": body,
        "raw_chars": len(raw),
    }


# ─────────────────────────────────────────────
# 2. LLM Prompt（供 IDE 内置 LLM 使用）
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """你是一个数据提取助手，负责从贺野（公众号"有生余年"）的旅行文章中提取结构化地点信息。

提取规则：
1. 地点候选：一篇文章可能涉及多个地点。判断是否单独建条目的标准：
   - 有独立GPS可定位的地名（景区、城市、具体地点）✓
   - 贺野在此停留并有实质描述（不只是路过一提）✓
   - 纯粹过路、仅提及地名但无任何感受描写 ✗
   - 最多拆5个条目，宁少勿多

2. excerpt选取规则（最重要）：
   - 必须是原文原话，一个字都不能改
   - 允许取相邻2-3句拼成一段，不允许跨段落跳接
   - 选有温度、有画面感、有贺野个人视角的句子
   - 避免纯描述性、攻略性、套话性句子
   - 长度控制在50-150字之间

3. snacks提取规则：
   - 只收录贺野明确亲自吃了或买了的食物
   - 路过看到的招牌、景区介绍牌上的名字、别人在吃的 → 不收录
   - 只写食物名，不写描述，如：["扁肉", "拌粉", "葱爆羊肉"]
   - 没有符合条件的食物 → 返回空数组 []

4. 坐标处理：
   - 不要猜测经纬度
   - 给出一个精准的高德地图搜索词（search_term），用于人工核实坐标
   - 格式：省市+具体地名，如"福建武夷山九曲溪"、"内蒙古克什克腾旗达里湖"

5. trip_tag：
   - 如果文章标题或内容暗示是某次连续出行的一部分（如"北上之旅第X天"），提取出行标签
   - 格式简短，如"2024北上之旅"、"2022福建行"
   - 不确定就填 null

输出格式：只返回JSON，不要任何其他文字，不要markdown代码块。
格式如下（locations是数组，可以有多个条目）：

{
  "locations": [
    {
      "province": "省份",
      "city": "城市",
      "place_name": "具体地点名",
      "full_name": "城市·地点名",
      "visit_date": "YYYY年M月（模糊即可，不确定填null）",
      "trip_tag": "出行标签或null",
      "excerpt": "原文原话，50-150字",
      "snacks": ["食物1", "食物2"],
      "search_term": "高德搜索词",
      "extractor_notes": "提取时遇到的任何不确定情况，简要说明"
    }
  ]
}"""


def build_user_prompt(article: dict) -> str:
    """构建用户 prompt"""
    return f"""文章标题：{article['title']}
发布日期：{article['date']}
地区标签：{article['region']}

文章正文：
{article['body']}"""


# ─────────────────────────────────────────────
# 3. 生成 ID
# ─────────────────────────────────────────────

_id_counter = 0


def generate_id(counter: int) -> str:
    return f"HY{counter:03d}"


# ─────────────────────────────────────────────
# 4. CSV 字段与写入
# ─────────────────────────────────────────────

CSV_FIELDS = [
    "id",
    "province",
    "city",
    "place_name",
    "full_name",
    "region",
    "visit_date",
    "trip_tag",
    "excerpt",
    "snacks",
    "search_term",
    "lat",
    "lng",
    "image_url",
    "article_url",
    "featured",
    "source_file",
    "source_title",
    "extractor_notes",
    "human_reviewed",
]


def write_csv(rows: list[dict], out_path: str, append: bool = False):
    mode = "a" if append else "w"
    write_header = not append or not Path(out_path).exists()
    with open(out_path, mode, newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


# ─────────────────────────────────────────────
# 5. 步骤 1：提取文本 + 生成 prompt
# ─────────────────────────────────────────────

def cmd_extract(args):
    """提取 PDF 文本，生成 prompt 文件供 IDE 内置 LLM 使用"""
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 收集 PDF 列表
    if args.file:
        pdf_list = [args.file]
    elif args.dir:
        pdf_list = sorted(str(p) for p in Path(args.dir).glob("*.pdf"))
    else:
        print("[!] 请指定 --file 或 --dir")
        return

    print(f"共 {len(pdf_list)} 个 PDF，prompt 输出至: {out_dir}")

    for i, pdf_path in enumerate(pdf_list):
        fname = Path(pdf_path).name
        print(f"\n▶ [{i+1}/{len(pdf_list)}] {fname}")

        article = extract_text(pdf_path)
        print(f"  标题: {article['title']}")
        print(f"  日期: {article['date']}  地区: {article['region']}  字数: {article['raw_chars']}")

        # 生成 prompt 文件
        stem = Path(pdf_path).stem
        prompt_file = out_dir / f"{stem}_prompt.json"

        prompt_data = {
            "source_file": fname,
            "title": article["title"],
            "date": article["date"],
            "region": article["region"],
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt": build_user_prompt(article),
            "body": article["body"],
        }

        with open(prompt_file, "w", encoding="utf-8") as f:
            json.dump(prompt_data, f, ensure_ascii=False, indent=2)

        print(f"  ✅ prompt 已保存: {prompt_file}")

        # 同时输出纯文本版本（方便直接复制到 IDE LLM）
        text_file = out_dir / f"{stem}_text.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(f"=== System Prompt ===\n{SYSTEM_PROMPT}\n\n")
            f.write(f"=== User Prompt ===\n{build_user_prompt(article)}\n")

        print(f"  ✅ 文本 prompt: {text_file}")

    print(f"\n✅ 步骤 1 完成！共生成 {len(pdf_list)} 组 prompt 文件")
    print(f"   下一步：将 prompt 文件内容复制到 IDE 内置 LLM，获取 JSON 输出后保存为 *_result.json")
    print(f"   然后运行：python heye_extractor.py merge --json-dir {out_dir} --out heye_locations.csv")


# ─────────────────────────────────────────────
# 6. 步骤 2：合并 LLM JSON 输出到 CSV
# ─────────────────────────────────────────────

def parse_llm_json(raw_text: str) -> list[dict]:
    """解析 LLM 输出的 JSON，兼容 markdown 代码块包裹"""
    text = raw_text.strip()
    # 去掉 markdown 代码块
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)

    data = json.loads(text)
    return data.get("locations", [])


def cmd_merge(args):
    """将 IDE 内置 LLM 的 JSON 输出合并到 CSV"""
    out_path = args.out
    id_start = args.id_start

    # 收集 JSON 文件
    json_files = []
    if args.json:
        json_files = [args.json]
    elif args.json_dir:
        json_files = sorted(str(p) for p in Path(args.json_dir).glob("*_result.json"))
    else:
        print("[!] 请指定 --json 或 --json-dir")
        return

    if not json_files:
        print("[!] 未找到任何 *_result.json 文件")
        return

    print(f"共 {len(json_files)} 个 JSON 结果文件，输出至: {out_path}")
    print(f"ID 起始: HY{id_start:03d}")

    counter = id_start
    all_rows = []

    for i, json_path in enumerate(json_files):
        print(f"\n▶ [{i+1}/{len(json_files)}] {Path(json_path).name}")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw = f.read()
            locations = parse_llm_json(raw)
        except json.JSONDecodeError as e:
            print(f"  [!] JSON 解析失败: {e}")
            continue
        except Exception as e:
            print(f"  [!] 读取失败: {e}")
            continue

        # 尝试从 prompt 文件获取 source 信息
        stem = Path(json_path).stem.replace("_result", "")
        prompt_file = Path(json_path).parent / f"{stem}_prompt.json"
        source_file = ""
        source_title = ""
        region = ""

        if prompt_file.exists():
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    prompt_data = json.load(f)
                source_file = prompt_data.get("source_file", "")
                source_title = prompt_data.get("title", "")
                region = prompt_data.get("region", "")
            except Exception:
                pass

        print(f"  → 解析到 {len(locations)} 个地点")

        for loc in locations:
            row = {
                "id": generate_id(counter),
                "province": loc.get("province", ""),
                "city": loc.get("city", ""),
                "place_name": loc.get("place_name", ""),
                "full_name": loc.get("full_name", ""),
                "region": region,
                "visit_date": loc.get("visit_date", ""),
                "trip_tag": loc.get("trip_tag", ""),
                "excerpt": loc.get("excerpt", ""),
                "snacks": json.dumps(loc.get("snacks", []), ensure_ascii=False),
                "search_term": loc.get("search_term", ""),
                "lat": "",
                "lng": "",
                "image_url": "",
                "article_url": "",
                "featured": "false",
                "source_file": source_file,
                "source_title": source_title,
                "extractor_notes": loc.get("extractor_notes", ""),
                "human_reviewed": "N",
            }
            print(f"    [{row['id']}] {row['full_name']} | snacks: {row['snacks']} | excerpt前30字: {row['excerpt'][:30]}...")
            all_rows.append(row)
            counter += 1

        # 追加写入
        append = (i > 0) or (id_start > 1)
        write_csv(all_rows, out_path, append=False)

    if all_rows:
        # 最终写入
        write_csv(all_rows, out_path, append=False)
        print(f"\n✅ 步骤 2 完成！共合并 {len(all_rows)} 条地点记录")
        print(f"   输出文件: {out_path}")
        print(f"   下次追加时使用 --id-start {counter}")
    else:
        print("\n❌ 无有效记录")


# ─────────────────────────────────────────────
# 7. 辅助命令：仅提取文本（不生成 prompt）
# ─────────────────────────────────────────────

def cmd_text(args):
    """仅提取 PDF 文本，输出到 stdout 或文件"""
    if args.file:
        article = extract_text(args.file)
        print(f"标题: {article['title']}")
        print(f"日期: {article['date']}  地区: {article['region']}")
        print(f"字数: {article['raw_chars']}")
        print("---")
        print(article['body'])
    elif args.dir:
        pdf_list = sorted(str(p) for p in Path(args.dir).glob("*.pdf"))
        for pdf_path in pdf_list:
            article = extract_text(pdf_path)
            print(f"\n{'='*60}")
            print(f"文件: {Path(pdf_path).name}")
            print(f"标题: {article['title']}")
            print(f"日期: {article['date']}  地区: {article['region']}")
            print(f"字数: {article['raw_chars']}")
            print(f"{'='*60}")
            print(article['body'][:500])
            print("...")
    else:
        print("[!] 请指定 --file 或 --dir")


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="贺野文章批量提取（零外部 API 依赖版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 步骤 1：提取 PDF 文本，生成 prompt
  python heye_extractor.py extract --dir ./pdfs --out-dir ./prompts

  # 步骤 2：合并 LLM JSON 输出到 CSV
  python heye_extractor.py merge --json-dir ./prompts --out heye_locations.csv

  # 仅查看 PDF 文本
  python heye_extractor.py text --file 某篇文章.pdf
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # extract 子命令
    p_extract = subparsers.add_parser("extract", help="提取 PDF 文本，生成 LLM prompt")
    p_extract.add_argument("--dir", help="PDF 所在目录，批量处理")
    p_extract.add_argument("--file", help="单个 PDF 文件路径")
    p_extract.add_argument("--out-dir", default="./prompts", help="prompt 输出目录")

    # merge 子命令
    p_merge = subparsers.add_parser("merge", help="合并 LLM JSON 输出到 CSV")
    p_merge.add_argument("--json", help="单个 LLM 结果 JSON 文件")
    p_merge.add_argument("--json-dir", help="LLM 结果 JSON 所在目录（匹配 *_result.json）")
    p_merge.add_argument("--out", default="heye_locations.csv", help="输出 CSV 路径")
    p_merge.add_argument("--id-start", type=int, default=1, help="ID 起始编号")

    # text 子命令
    p_text = subparsers.add_parser("text", help="仅提取 PDF 文本（不生成 prompt）")
    p_text.add_argument("--dir", help="PDF 所在目录")
    p_text.add_argument("--file", help="单个 PDF 文件路径")

    args = parser.parse_args()

    if args.command == "extract":
        cmd_extract(args)
    elif args.command == "merge":
        cmd_merge(args)
    elif args.command == "text":
        cmd_text(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
