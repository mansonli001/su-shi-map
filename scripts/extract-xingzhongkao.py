#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏轼行踪考 · Word → 简体 Markdown 批量提取脚本 v1.0

输入：~/Downloads/苏轼行踪考/Word版本/*.docx（26 篇繁体 docx）
输出：data-v4-source/行踪考-简体/*.md（简体 markdown，保留段落结构）

实现方式：
- Python 标准库 zipfile 解 docx（不需 mammoth）
- xml.etree.ElementTree 提取 <w:t> 文本节点
- opencc-python-reimplemented 繁→简（t2s 配方）
- 按段落输出，保留小节标题（识别 <w:pStyle> heading）

用法：
    python3 scripts/extract-xingzhongkao.py
"""

import os
import sys
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from opencc import OpenCC
except ImportError:
    print("❌ 请先安装: pip3 install opencc-python-reimplemented")
    sys.exit(1)

# ============= 配置 =============
SRC_DIR = Path.home() / "Downloads" / "苏轼行踪考" / "Word版本"
PROJECT_ROOT = Path(__file__).parent.parent
OUT_DIR = PROJECT_ROOT / "data-v4-source" / "行踪考-简体"

# Word XML 命名空间
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

# 繁→简转换器
cc = OpenCC("t2s")  # Traditional to Simplified


# ============= 提取函数 =============
def extract_paragraphs(docx_path: Path) -> list[dict]:
    """提取 docx 所有段落，返回 [{level, text}, ...]
    level: 0=普通段落 / 1-6=Heading 1~6
    """
    paragraphs = []
    with zipfile.ZipFile(docx_path) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            body = root.find("w:body", NS)
            if body is None:
                return []

            for p in body.findall("w:p", NS):
                # 获取段落样式（识别标题级别）
                level = 0
                pPr = p.find("w:pPr", NS)
                if pPr is not None:
                    pStyle = pPr.find("w:pStyle", NS)
                    if pStyle is not None:
                        style_val = pStyle.get(f"{{{NS['w']}}}val", "")
                        # 常见标题样式：Heading1, Heading2, 标题1, 标题2 等
                        m = re.search(r"[Hh]eading\s*([1-6])|标题\s*([1-6])", style_val)
                        if m:
                            level = int(m.group(1) or m.group(2))

                # 收集段落内所有文本片段
                texts = []
                for t in p.iter(f"{{{NS['w']}}}t"):
                    if t.text:
                        texts.append(t.text)
                text = "".join(texts).strip()

                if text:
                    paragraphs.append({"level": level, "text": text})

    return paragraphs


def detect_heading(text: str) -> int:
    """从段落内容识别隐式标题级别（兜底，当 docx 没标记 Heading 样式时）
    返回 0=普通段落 / 1=H1 / 2=H2 / 3=H3
    """
    # 常见行踪考标题模式
    if re.match(r"^第[一二三四五六七八九十百]+篇\s+", text) and len(text) < 30:
        return 1
    if re.match(r"^第[一二三四五六七八九十百]+章\s+", text) and len(text) < 30:
        return 2
    if re.match(r"^[一二三四五六七八九十]+、", text) and len(text) < 50:
        return 3
    if re.match(r"^[\(（][一二三四五六七八九十]+[\)）]", text) and len(text) < 50:
        return 4
    return 0


def to_markdown(paragraphs: list[dict], title: str) -> str:
    """段落数组 → Markdown 字符串"""
    lines = [f"# {title}\n"]
    for p in paragraphs:
        text = p["text"]
        # 优先用 docx 自带的 level，否则用启发式识别
        level = p["level"] or detect_heading(text)
        if level == 0:
            lines.append(text)
            lines.append("")  # 段落间空行
        else:
            prefix = "#" * (level + 1)  # 文档总标题已是 #，所以 +1
            lines.append(f"\n{prefix} {text}\n")
    return "\n".join(lines)


def clean_filename(stem: str) -> str:
    """处理 '01 封面' → '01_封面'"""
    s = stem.replace(" ", "_").replace("　", "_")
    s = re.sub(r"[\\/:*?\"<>|]", "", s)
    return s


# ============= 主流程 =============
def main():
    if not SRC_DIR.exists():
        print(f"❌ 找不到源目录: {SRC_DIR}")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    docx_files = sorted(SRC_DIR.glob("*.docx"))
    print(f"\n📚 发现 {len(docx_files)} 个 docx 文件")
    print(f"📂 输出目录: {OUT_DIR}\n")

    stats = {"ok": 0, "fail": 0, "char_total": 0, "para_total": 0}

    for docx in docx_files:
        stem = docx.stem
        try:
            # 1. 提取段落
            paragraphs = extract_paragraphs(docx)
            if not paragraphs:
                print(f"⚠️  {stem}: 0 段落，跳过")
                continue

            # 2. 文件名 + 标题繁→简
            out_stem = cc.convert(clean_filename(stem))
            md_title = cc.convert(stem)

            # 3. 段落文本繁→简
            for p in paragraphs:
                p["text"] = cc.convert(p["text"])

            # 4. 转 markdown
            md = to_markdown(paragraphs, md_title)

            # 5. 写文件
            out_path = OUT_DIR / f"{out_stem}.md"
            out_path.write_text(md, encoding="utf-8")

            char_count = sum(len(p["text"]) for p in paragraphs)
            stats["ok"] += 1
            stats["char_total"] += char_count
            stats["para_total"] += len(paragraphs)
            print(f"✅ {out_stem}.md  ({len(paragraphs)} 段, {char_count:,} 字)")

        except Exception as e:
            stats["fail"] += 1
            print(f"❌ {stem}: {e}")

    print(f"\n{'='*50}")
    print(f"✨ 提取完成")
    print(f"   成功: {stats['ok']} 个")
    print(f"   失败: {stats['fail']} 个")
    print(f"   总段落: {stats['para_total']:,}")
    print(f"   总字数: {stats['char_total']:,}")
    print(f"\n📂 输出: {OUT_DIR.relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
