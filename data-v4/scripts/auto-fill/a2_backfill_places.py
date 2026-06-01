#!/usr/bin/env python3
"""
A2.4 places.global_works ↔ poems 双向回填

读 poems/W*.json (含 fullText/coreVerse 的)，
通过标题匹配回填 places/P*.json 的 global_works[*].excerpt + coreVerse + fullText 字段
"""
import json, glob, re, zhconv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = ROOT / "public" / "data-v4"
INT = ROOT / "data-v4"


def norm(s: str) -> str:
    if not s:
        return ""
    s = zhconv.convert(s, "zh-cn")
    return re.sub(r"[（）()【】《》「」『』·•・\s,，。、！？；：·]", "", s)


def main():
    # 1) 加载所有 poems 全文
    poems_by_title = {}  # norm_title -> poem_dict
    for f in sorted(glob.glob(str(PUB / "poems/W*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if not d.get("has_full_text"):
            continue
        n = norm(d["title"])
        poems_by_title[n] = d
    print(f"📚 加载 {len(poems_by_title)} 首带全文的诗词")

    # 2) 遍历 places，回填 global_works
    updated = 0
    works_filled = 0
    for f in sorted(glob.glob(str(PUB / "places/P*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        gw = d.get("global_works") or []
        if not gw:
            continue
        changed = False
        for w in gw:
            t = w.get("title", "")
            n = norm(t)
            if n in poems_by_title:
                p = poems_by_title[n]
                if not w.get("fullText") and p.get("fullText"):
                    w["fullText"] = p["fullText"]
                    changed = True
                    works_filled += 1
                if not w.get("coreVerse") and p.get("coreVerse"):
                    w["coreVerse"] = p["coreVerse"]
                if not w.get("excerpt") and p.get("coreVerse"):
                    w["excerpt"] = p["coreVerse"]
                w["poem_id"] = p["id"]
        if changed:
            d["global_works"] = gw
            txt = json.dumps(d, ensure_ascii=False, indent=2)
            Path(f).write_text(txt, encoding="utf-8")
            # 同步 internal
            int_f = INT / "places" / Path(f).name
            if int_f.exists():
                int_f.write_text(txt, encoding="utf-8")
            updated += 1

    print(f"✅ 已更新 {updated} 个 places · 共回填 {works_filled} 个 work 全文")


if __name__ == "__main__":
    main()
