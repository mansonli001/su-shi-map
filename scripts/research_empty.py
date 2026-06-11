#!/usr/bin/env python3
"""Research and fill 86 empty poem entries.
Uses web search to find original text, verify authorship, and fill data.
"""
import json, os, glob, re

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"

# Get all empty entries
empty = []
for f in sorted(glob.glob(f'{BASE}/*.json')):
    with open(f) as fp:
        d = json.load(fp)
    if not d.get('paragraphs') or len(d.get('paragraphs', [])) == 0:
        empty.append(d)

print(f"Total empty entries: {len(empty)}")
print("\nTitles for research:")
for d in empty:
    print(f"  {d['id']}: {d['title']} ({d.get('type','')}) @ {d.get('location','')}")

# Known problematic entries (not actually by Su Shi or disputed)
DISPUTED = {
    'S270': '雷州八首 - 实为秦观作，查慎行已考证',
    'S266': '江州重别薛六柳八二员外 - 疑为刘长卿作',
}

print(f"\nDisputed entries: {len(DISPUTED)}")
for k, v in DISPUTED.items():
    print(f"  {k}: {v}")
