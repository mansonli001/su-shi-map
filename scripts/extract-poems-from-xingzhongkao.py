#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏轼行踪考 · 诗词关联提取脚本 v1.0

从行踪考 25 篇 markdown 中提取所有《xxx》标题，
对照 poems-index.json 已有 68 首，输出新增候选清单 + 自动关联 route_id。

输入：
- data-v4-source/行踪考-简体/*.md
- data-v4/poems-index.json

输出：
- data-v4-source/行踪考诗词候选/all-candidates.json     全量候选
- data-v4-source/行踪考诗词候选/new-only.json           仅新增（已去重已有 68 首）
- data-v4-source/行踪考诗词候选/by-route.md             按路线分组的人类可读清单
- data-v4-source/行踪考诗词候选/blacklist-suggested.json 建议过滤的（典籍/他人作品/书目等）
"""

import os
import re
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "data-v4-source" / "行踪考-简体"
OUT_DIR = PROJECT_ROOT / "data-v4-source" / "行踪考诗词候选"
EXISTING_POEMS = PROJECT_ROOT / "data-v4" / "poems-index.json"

# ============= 行踪考篇章 → route_id 映射 =============
# 基于章节内容，每篇主要对应的 route_id
CHAPTER_TO_ROUTE = {
    "02_苏轼行踪考序言": [],
    "03_目录与图示": [],
    "04_第一篇__绪论": [],
    "05_第二篇__眉山苏轼": ["R00"],
    "06_第三篇__第一次进京与母丧返乡": ["R01"],
    "07_第四篇__第二次出蜀与三苏《南行集》": ["R02"],
    "08_第五篇__第二次进京与凤翔府签判任": ["R03"],
    "09_第六篇__第三次入京与父丧返乡": ["R04"],
    "10_第七篇__第四次入京": ["R05"],
    "11_第八篇__任杭州倅": ["R06"],
    "12_第九篇_山东知密": ["R07"],
    "13_第十篇__江苏知徐": ["R08"],
    "14_第十一篇__浙江知湖与乌台诗案": ["R09"],
    "15_第十二篇__贬谪黄州": ["R10"],
    "16_第十三篇__万里来去，登州五日": ["R11", "R12"],
    "17_第十四篇_第六次入京": ["R13"],
    "18_第十五篇__浙江知杭": ["R14"],
    "19_第十六篇__第七次进京": ["R15"],
    "20_第十七篇__安徽知颍与江苏知杨": ["R16"],
    "21_第十八篇__第八次进京": ["R17"],
    "22_第十九篇_河北知定": ["R17"],
    "23_第二十篇__贬谪惠州": ["R18"],
    "24_第二十一篇__贬谪儋州": ["R18"],
    "25_第二十二篇___北归常州，葬于郏县": ["R19"],
    "26_第二十三篇__结论": [],
}

# ============= 黑名单：非苏轼作品/典籍/书目/地方志 =============
# 在行踪考中频繁被引用，但不是苏轼自己的作品
BLACKLIST_KEYWORDS = {
    # 典籍
    "诗经", "尚书", "易经", "论语", "孟子", "礼记", "春秋", "左传", "周易",
    "庄子", "老子", "孙子兵法",
    # 史书
    "宋史", "史记", "汉书", "后汉书", "三国志", "晋书", "唐书", "宋书",
    "续资治通鉴", "资治通鉴", "宋会要",
    # 苏轼相关传记/年谱（不是苏轼作品本身）
    "苏轼年谱", "东坡先生年谱", "苏文忠公诗合注", "苏文忠公诗编注集成",
    "孔凡礼苏轼年谱", "苏轼行踪考", "苏轼传", "东坡纪年录", "苏诗总案",
    "苏颍滨年表", "苏轼诗编年校注",
    # 苏轼作品集（容器，不是单首作品）
    "东坡七集", "东坡集", "东坡后集", "东坡续集", "东坡词", "东坡文集事略",
    "苏文忠公全集", "苏轼全集", "苏轼诗集", "苏轼文集", "全集校注",
    "苏轼诗集合注", "东坡志林", "南行集", "南行前集", "南行后集",
    "栾城集", "栾城后集", "嘉祐集",
    # 唐宋他人作品集
    "杜甫诗集", "李白诗集", "白居易集", "韩昌黎集", "柳河东集",
    "欧阳修全集", "王安石全集", "黄庭坚集",
    # 笔记小说/历史地理书（行踪考常引用）
    "东京梦华录", "入蜀记", "梦溪笔谈", "容斋随笔", "鹤林玉露",
    "蜀中广记", "宋稗类钞", "墨庄漫录", "石林燕语",
    "汴京遗迹志", "唐代交通图考",
    # 地方志
    "府志", "县志", "州志", "通志", "图经", "舆地纪胜", "方舆胜览", "太平寰宇记",
    "咸淳临安志", "咸淳毗陵志", "庐山志", "旧志", "新志",
    "元丰九域志", "寰宇记", "舆地广记", "水经注", "广舆记",
    # 杂书
    "全宋词", "全宋诗", "全唐诗", "宋诗钞", "宋诗纪事",
    # 行踪考自己的章节标题
    "行踪考", "苏轼行踪",
    # 苏辙作品（行踪考会大量引用三苏，但本项目只关注苏轼）
    "亡兄子瞻", "栾城遗言",
    # 书信集编号
    "七十一首", "二十首", "三十首", "五十首", "百首", "一百首",
    # 地理学/地志类常见后缀
    "总案",
}

# ============= 章节标题模式（行踪考自身结构）=============
CHAPTER_PATTERNS = [
    r"^第[一二三四五六七八九十百]+篇",  # 第X篇
    r"^第[一二三四五六七八九十百]+章",  # 第X章
    r"^第[一二三四五六七八九十百]+节",  # 第X节
]


def is_chapter_title(title: str) -> bool:
    """是否是行踪考章节标题（如《第八篇、任杭州倅》）"""
    for pat in CHAPTER_PATTERNS:
        if re.search(pat, title):
            return True
    return False


def is_book_or_atlas(title: str) -> bool:
    """是否是书目/方志/年谱类（非单首作品）"""
    suffixes_book = ["志", "录", "考", "记", "图", "表", "鉴", "案", "谱"]
    if len(title) >= 2 and title[-1] in suffixes_book:
        # 但要排除苏轼真实作品中的"记""赋""序"等
        # 真实苏轼作品常见结尾：
        if title[-1] == "记" and len(title) >= 4:
            # 喜雨亭记 / 凌虚台记 / 石钟山记 / 放鹤亭记 等是苏轼真品
            # 但 入蜀记 / 庐山记 / 寰宇记 是他人作品
            allowed = ["亭记", "台记", "山记", "堂记", "院记", "阁记", "楼记", "祠记", "庙记", "桥记",
                       "斋记", "轩记", "鹤记", "钟记", "潭记"]
            if any(title.endswith(a) for a in allowed):
                return False
            # 短的"X记"可能是杂记，保留
            if len(title) <= 3:
                return False
            return True
        if title[-1] == "志":
            return True  # 志一般是方志
    return False


def is_blacklisted(title: str) -> tuple[bool, str]:
    """返回 (是否黑名单, 命中关键词)"""
    # 1. 章节标题
    if is_chapter_title(title):
        return True, "章节标题"
    # 2. 书目/方志/年谱
    if is_book_or_atlas(title):
        return True, "书目/方志"
    # 3. 关键词命中
    for kw in BLACKLIST_KEYWORDS:
        if kw in title:
            return True, kw
    return False, ""


def normalize_title(title: str) -> str:
    """规范化标题：去除空白、全角空格"""
    return re.sub(r"\s+", "", title).strip()


def extract_poem_titles(md_text: str) -> list[str]:
    """从 markdown 提取所有 《xxx》 标题"""
    # 匹配 《...》，但排除内部还有《》的（嵌套不算）
    pattern = r"《([^《》]{2,30})》"
    return [normalize_title(m) for m in re.findall(pattern, md_text)]


def main():
    # 读已有 poems-index.json（68 首 v4 已关联）
    existing = json.load(EXISTING_POEMS.open(encoding="utf-8"))
    existing_titles = {normalize_title(p["title"]) for p in existing.get("poems", [])}
    print(f"📚 已有诗词 (poems-index): {len(existing_titles)} 首")

    # 读 chinese-poetry 苏轼作品集（白名单）
    cp_path = PROJECT_ROOT / "data" / "poems-sushi.json"
    cp_titles_full = set()  # 完整标题
    cp_titles_simplified = {}  # 简化标题 → 完整标题（用于模糊匹配）
    if cp_path.exists():
        cp_data = json.load(cp_path.open(encoding="utf-8"))
        for p in cp_data:
            title = normalize_title(p.get("title", ""))
            if not title:
                continue
            cp_titles_full.add(title)
            # 提取核心标题（去除"·xxx"、"·和xxx韵"、"二首之X"等后缀）
            simple = re.sub(r"[·．·][^·]*$", "", title)
            simple = re.sub(r"[一二三四五六七八九十]+首之[一二三四五六七八九十]+$", "", simple)
            simple = re.sub(r"其[一二三四五六七八九十]+$", "", simple)
            simple = simple.strip()
            if simple and simple != title:
                cp_titles_simplified.setdefault(simple, []).append(title)
        print(f"📚 chinese-poetry 白名单: {len(cp_titles_full)} 首苏轼作品")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 扫所有 markdown
    md_files = sorted(SRC_DIR.glob("*.md"))
    all_candidates = defaultdict(lambda: {"count": 0, "chapters": [], "route_ids": set()})

    for md in md_files:
        chapter = md.stem
        text = md.read_text(encoding="utf-8")
        titles = extract_poem_titles(text)
        route_ids = CHAPTER_TO_ROUTE.get(chapter, [])

        for t in titles:
            all_candidates[t]["count"] += 1
            if chapter not in all_candidates[t]["chapters"]:
                all_candidates[t]["chapters"].append(chapter)
            for rid in route_ids:
                all_candidates[t]["route_ids"].add(rid)

    # 分类
    new_high = {}     # 白名单精确命中（高置信，可直接入库）
    new_mid = {}      # 白名单部分命中（中置信，需审核）
    new_low = {}      # 仅在行踪考出现，无白名单命中（低置信，需人工）
    blacklisted = {}  # 黑名单
    already_exists = {}  # 已在 poems-index 中

    for title, info in all_candidates.items():
        info["route_ids"] = sorted(info["route_ids"])
        is_bl, bl_kw = is_blacklisted(title)

        # 1. 黑名单
        if is_bl:
            blacklisted[title] = {**info, "blacklist_reason": bl_kw}
            continue

        # 2. 已在 poems-index
        if title in existing_titles:
            already_exists[title] = info
            continue

        # 3. 白名单精确匹配（高置信）
        if title in cp_titles_full:
            new_high[title] = {**info, "match_type": "exact", "cp_match": title}
            continue

        # 4. 白名单部分匹配（候选标题作为某首长 title 的子串，或反之）
        partial_match = None
        for cp_t in cp_titles_full:
            if (title in cp_t and len(title) >= 3) or (cp_t in title and len(cp_t) >= 3):
                partial_match = cp_t
                break
        if partial_match:
            new_mid[title] = {**info, "match_type": "partial", "cp_match": partial_match}
            continue

        # 5. 无任何匹配，但通过黑名单过滤了 → 低置信
        new_low[title] = {**info, "match_type": "none"}

    # ─── 输出 1: 高置信新增（直接入库候选） ────────
    high_sorted = dict(sorted(new_high.items(), key=lambda x: (-x[1]["count"], x[0])))
    (OUT_DIR / "high-confidence.json").write_text(
        json.dumps({
            "_meta": {
                "total": len(new_high),
                "note": "白名单精确命中 chinese-poetry 苏轼集，可直接入库",
                "extracted_at": "2026-06-02",
            },
            "candidates": high_sorted,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ─── 输出 2: 中置信（部分匹配，需审核） ──────────
    mid_sorted = dict(sorted(new_mid.items(), key=lambda x: (-x[1]["count"], x[0])))
    (OUT_DIR / "mid-confidence.json").write_text(
        json.dumps({
            "_meta": {
                "total": len(new_mid),
                "note": "标题部分匹配 chinese-poetry，需人工核对是否同一作品",
                "extracted_at": "2026-06-02",
            },
            "candidates": mid_sorted,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ─── 输出 3: 低置信（仅在行踪考出现） ────────────
    low_sorted = dict(sorted(new_low.items(), key=lambda x: (-x[1]["count"], x[0])))
    (OUT_DIR / "low-confidence.json").write_text(
        json.dumps({
            "_meta": {
                "total": len(new_low),
                "note": "仅在行踪考出现，未匹配 chinese-poetry，可能是真品也可能是非苏轼。需审核",
                "extracted_at": "2026-06-02",
            },
            "candidates": low_sorted,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ─── 输出 4: 黑名单清单 ────────────────────────
    bl_data = {
        "_meta": {"total": len(blacklisted), "note": "建议过滤（典籍/他人作品/书目/方志/章节标题）"},
        "blacklisted": dict(sorted(blacklisted.items())),
    }
    (OUT_DIR / "blacklist-suggested.json").write_text(
        json.dumps(bl_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ─── 输出 5: 高置信按路线分组的人类可读 markdown ─
    # 加载 routes
    routes_idx = json.load((PROJECT_ROOT / "data-v4" / "routes-index.json").open(encoding="utf-8"))
    route_names = {r["id"]: r["name"] for r in routes_idx.get("routes", [])}

    by_route = defaultdict(list)
    for title, info in new_high.items():
        if info["route_ids"]:
            for rid in info["route_ids"]:
                by_route[rid].append((title, info["count"]))
        else:
            by_route["UNKNOWN"].append((title, info["count"]))

    md_lines = ["# 行踪考诗词候选 · 高置信清单（白名单精确命中）\n"]
    md_lines.append(f"> 共 **{len(new_high)} 首** 苏轼作品在行踪考中被提及，但目前 poems-index 未收录")
    md_lines.append(f"> 已与 chinese-poetry 苏轼集精确匹配，可直接入库")
    md_lines.append(f"> （已有 {len(existing_titles)} 首 + 新增 {len(new_high)} 首 = **{len(existing_titles) + len(new_high)} 首**总量）\n")

    for rid in sorted(by_route.keys()):
        items = sorted(by_route[rid], key=lambda x: -x[1])
        rname = route_names.get(rid, "未知路线") if rid != "UNKNOWN" else "（无对应路线）"
        if not items:
            continue
        md_lines.append(f"\n## {rid} · {rname}（{len(items)} 首）\n")
        for title, count in items:
            mark = "⭐" if count >= 3 else "✅"
            md_lines.append(f"- {mark} 《{title}》  · 提及 {count} 次")

    (OUT_DIR / "high-confidence-by-route.md").write_text("\n".join(md_lines), encoding="utf-8")

    # ─── 控制台报告 ────────────────────────────────
    print(f"\n{'='*60}")
    print(f"✨ 提取完成")
    print(f"  发现 {len(all_candidates)} 个唯一《》引用")
    print(f"  ├─ 已在 poems-index: {len(already_exists)} 首")
    print(f"  ├─ 黑名单（典籍/他人/方志）: {len(blacklisted)}")
    print(f"  ├─ 🟢 高置信新增（白名单精确）: {len(new_high)} ⭐")
    print(f"  ├─ 🟡 中置信（部分匹配）: {len(new_mid)}")
    print(f"  └─ 🔴 低置信（仅行踪考）: {len(new_low)}")
    print(f"\n📊 高置信入库后总诗词量: {len(existing_titles)} + {len(new_high)} = {len(existing_titles) + len(new_high)} 首")
    print(f"\n📂 输出目录: {OUT_DIR.relative_to(PROJECT_ROOT)}/")
    print(f"  ├─ high-confidence.json          🟢 可直接入库")
    print(f"  ├─ high-confidence-by-route.md   🟢 按路线人类可读")
    print(f"  ├─ mid-confidence.json           🟡 需审核（部分匹配）")
    print(f"  ├─ low-confidence.json           🔴 需审核（仅行踪考）")
    print(f"  └─ blacklist-suggested.json      ❌ 建议过滤")


if __name__ == "__main__":
    main()
