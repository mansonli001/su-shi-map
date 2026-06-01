#!/usr/bin/env python3
"""
A2.3 chinese-poetry 苏轼全集匹配注入器

数据源：/tmp/chinese-poetry/
  - 全唐诗/poet.song.*.json   2824 首苏轼诗（繁体）
  - 宋词/ci.song.*.json        362 首苏轼词（简体）

匹配策略：
  1. 简繁转换 → 统一简体
  2. 标题清洗（去括号/标点/"其X"等）
  3. 三层匹配：全等 → 包含 → 关键字
  4. 优先级：精确匹配 > 包含 > 模糊

输出：
  - public/data-v4/poems/W{nnn}.json  注入 fullText/coreVerse/background
  - 同步 internal data-v4/poems/
  - 更新 poems-index.json 的 has_full_text
"""
import json, glob, re, os
from pathlib import Path
import zhconv

ROOT = Path(__file__).resolve().parents[3]
PUB = ROOT / "public" / "data-v4"
INT = ROOT / "data-v4"
SOURCE = Path("/tmp/chinese-poetry")


def normalize(s: str) -> str:
    """简繁转换 + 标点清洗"""
    if not s:
        return ""
    s = zhconv.convert(s, "zh-cn")
    # 去常见标点
    s = re.sub(r"[（）()【】《》「」『』·•・\s,，。、！？；：·]", "", s)
    return s


def title_keys(title: str) -> list[str]:
    """生成用于匹配的标题关键字（多级）"""
    norm = normalize(title)
    keys = [norm]
    # 去"其一/其二/其X"
    base = re.sub(r"其[一二三四五六七八九十0-9]+$", "", norm)
    if base != norm:
        keys.append(base)
    # 取前 8 字（核心标题）
    if len(norm) > 8:
        keys.append(norm[:8])
    return keys


def load_chinese_poetry():
    """加载所有苏轼作品（诗+词），统一为简体"""
    works = []  # [{title_simp, paragraphs_simp, source, original_title}]
    # 1) 宋诗
    for f in sorted(glob.glob(str(SOURCE / "全唐诗/poet.song.*.json"))):
        try:
            for item in json.load(open(f, encoding="utf-8")):
                author = zhconv.convert(item.get("author", ""), "zh-cn")
                if author != "苏轼":
                    continue
                works.append({
                    "title_orig": item.get("title", ""),
                    "title_simp": zhconv.convert(item.get("title", ""), "zh-cn"),
                    "paragraphs_simp": [zhconv.convert(p, "zh-cn") for p in item.get("paragraphs", [])],
                    "source": "诗",
                })
        except Exception:
            pass
    # 2) 宋词
    for f in sorted(glob.glob(str(SOURCE / "宋词/ci.song.*.json"))):
        try:
            for item in json.load(open(f, encoding="utf-8")):
                if item.get("author") != "苏轼":
                    continue
                rh = item.get("rhythmic", "") or ""
                # 词的"标题"用词牌名
                works.append({
                    "title_orig": rh,
                    "title_simp": rh,
                    "paragraphs_simp": item.get("paragraphs", []),
                    "source": "词",
                })
        except Exception:
            pass
    return works


def build_index(works):
    """构建标题索引：normalize → list of works"""
    idx = {}  # norm_key -> [work_idx]
    for i, w in enumerate(works):
        norm = normalize(w["title_simp"])
        idx.setdefault(norm, []).append(i)
    return idx


def find_matches(target_title: str, works, idx, max_results=5):
    """返回最多 max_results 个候选（按匹配等级排序）"""
    keys = title_keys(target_title)
    matched = []  # (level, work_idx)
    seen = set()

    # Level 1: 精确（normalize 后全等）
    for k in keys:
        for wi in idx.get(k, []):
            if wi not in seen:
                matched.append((1, wi))
                seen.add(wi)

    # Level 2: 标题包含 target 的核心关键字（≥4 字）
    if len(matched) < max_results:
        core = keys[-1] if keys else normalize(target_title)
        if len(core) >= 4:
            for i, w in enumerate(works):
                if i in seen:
                    continue
                norm = normalize(w["title_simp"])
                if core in norm or norm.startswith(core[:6]):
                    matched.append((2, i))
                    seen.add(i)
                    if len(matched) >= max_results:
                        break

    # Level 3: target 包含 work 的核心
    if len(matched) < max_results:
        norm_target = normalize(target_title)
        for i, w in enumerate(works):
            if i in seen:
                continue
            norm = normalize(w["title_simp"])
            if norm and len(norm) >= 4 and norm in norm_target:
                matched.append((3, i))
                seen.add(i)
                if len(matched) >= max_results:
                    break

    # Level 4: target 关键短语在标题中（提取 3-5 字核心词）
    # 例如 "雪浪石" 匹配 "次韵滕大夫三首 雪浪石"
    if len(matched) < max_results:
        norm_target = normalize(target_title)
        # 提取候选关键短语：去前缀「次韵/和/题/送/赠/赋」等
        stripped = re.sub(r"^(次韵|和|题|送|赠|赋|寄|过|游|至|自)", "", norm_target)
        # 取前 3-5 字最有特征性的
        candidates_kw = []
        if len(stripped) >= 3:
            candidates_kw.append(stripped[:5])
            candidates_kw.append(stripped[:4])
            candidates_kw.append(stripped[:3])
        for kw in candidates_kw:
            if len(kw) < 3:
                continue
            for i, w in enumerate(works):
                if i in seen:
                    continue
                norm = normalize(w["title_simp"])
                if kw in norm:
                    matched.append((4, i))
                    seen.add(i)
                    if len(matched) >= max_results:
                        break
            if len(matched) >= max_results:
                break

    # Level 5: 词牌+正文内容双重匹配
    # 例如 "临江仙·昨夜扁舟京口" → 找词牌"临江仙"且 paragraphs[0] 含"昨夜扁舟京口"或"京口"
    if len(matched) < max_results and "·" in target_title:
        cipai, _, content_hint = target_title.partition("·")
        cipai_norm = normalize(cipai)
        hint_norm = normalize(content_hint)
        # 取 hint 前 4-5 字
        hints = []
        if len(hint_norm) >= 3:
            hints.append(hint_norm[:5])
            hints.append(hint_norm[:4])
            hints.append(hint_norm[:3])
        for hint in hints:
            if len(hint) < 3:
                continue
            for i, w in enumerate(works):
                if i in seen:
                    continue
                norm = normalize(w["title_simp"])
                # 词牌匹配
                if cipai_norm not in norm:
                    continue
                # 正文第一段是否含 hint
                first_para = w["paragraphs_simp"][0] if w["paragraphs_simp"] else ""
                first_norm = normalize(first_para)
                if hint in first_norm:
                    matched.append((5, i))
                    seen.add(i)
                    break
            if len(matched) >= max_results:
                break

    # Level 6: 「别名·真题名」切分匹配
    # 例如 "惠州一绝·梅花二首" → 单独搜 "梅花二首"
    if len(matched) < max_results and "·" in target_title:
        _, _, second = target_title.partition("·")
        second_norm = normalize(second)
        if len(second_norm) >= 3:
            for i, w in enumerate(works):
                if i in seen:
                    continue
                norm = normalize(w["title_simp"])
                if second_norm in norm or norm in second_norm:
                    matched.append((6, i))
                    seen.add(i)
                    if len(matched) >= max_results:
                        break

    return matched[:max_results]


def write_both(rel: str, data):
    js = json.dumps(data, ensure_ascii=False, indent=2)
    for base in (PUB, INT):
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(js, encoding="utf-8")


def extract_core_verse(paragraphs: list) -> str:
    """从全文抽取核心名句（取首句或最有名的句子）"""
    if not paragraphs:
        return ""
    # 简单策略：返回第一段
    return paragraphs[0]


def main():
    print("📚 加载 chinese-poetry 苏轼全集…")
    works = load_chinese_poetry()
    idx = build_index(works)
    print(f"  ✓ 苏轼作品总数：{len(works)}（诗 {sum(1 for w in works if w['source']=='诗')} + 词 {sum(1 for w in works if w['source']=='词')}）")

    poems_idx_path = PUB / "poems-index.json"
    poems_idx = json.loads(poems_idx_path.read_text(encoding="utf-8"))

    matched_count = 0
    skipped_count = 0
    multiple_count = 0
    no_match = []
    multiple_log = []

    for poem_meta in poems_idx["poems"]:
        wid = poem_meta["id"]
        target_title = poem_meta["title"]
        # 已有全文（手动注入的 11 首）跳过保留
        path = PUB / "poems" / f"{wid}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("has_full_text") and d.get("fullText"):
            skipped_count += 1
            continue

        candidates = find_matches(target_title, works, idx, max_results=3)
        if not candidates:
            no_match.append((wid, target_title))
            continue

        # 取最高等级的第一个
        level, wi = candidates[0]
        w = works[wi]
        full = "\n".join(w["paragraphs_simp"])
        core_verse = extract_core_verse(w["paragraphs_simp"])

        d["fullText"] = full
        d["coreVerse"] = core_verse
        d["excerpt"] = core_verse
        d["has_full_text"] = True
        d["full_text_source"] = "chinese-poetry"
        d["full_text_match_level"] = level
        d["matched_title"] = w["title_orig"]
        if level >= 2 or len(candidates) > 1:
            # 候选 >1 标记需要复核
            d["full_text_needs_review"] = True
            multiple_log.append((wid, target_title, [(works[c[1]]["title_orig"], c[0]) for c in candidates]))
            multiple_count += 1

        write_both(f"poems/{wid}.json", d)
        matched_count += 1

    # 更新索引
    has_full = 0
    for p in poems_idx["poems"]:
        wid = p["id"]
        path = PUB / "poems" / f"{wid}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("has_full_text"):
            p["has_full_text"] = True
            p["coreVerse"] = d.get("coreVerse", "")
            has_full += 1
    poems_idx["has_full_text"] = has_full
    poems_idx["pending_full_text"] = poems_idx["total"] - has_full
    write_both("poems-index.json", poems_idx)

    print(f"\n📊 注入结果：")
    print(f"  ✅ 新匹配注入：{matched_count}")
    print(f"  ⏩ 已有全文跳过：{skipped_count}")
    print(f"  ⚠️ 多候选需复核：{multiple_count}")
    print(f"  ❌ 未匹配：{len(no_match)}")
    print(f"  📈 全文覆盖率：{has_full}/{poems_idx['total']} ({has_full*100//poems_idx['total']}%)")

    if no_match:
        print(f"\n❌ 未匹配清单（{len(no_match)} 首，可能是类目名/合集）：")
        for wid, t in no_match:
            print(f"  {wid}: {t}")

    # 写入复核日志
    if multiple_log:
        log_path = INT / "meta" / "auto-fill-results" / "a2-poems-multi-match-review.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("# A2 诗词全文匹配复核清单\n\n")
            f.write(f"## 多候选 / 模糊匹配（共 {len(multiple_log)} 首，需人工复核）\n\n")
            for wid, t, cands in multiple_log:
                f.write(f"### {wid} 目标：{t}\n")
                for ot, lv in cands:
                    f.write(f"  - L{lv}: {ot}\n")
                f.write("\n")
        print(f"\n📝 多候选复核清单已写出：{log_path}")


if __name__ == "__main__":
    main()
