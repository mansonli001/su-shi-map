#!/usr/bin/env python3
"""
从已提取的 prompt JSON 文件中读取正文，
按规则提取结构化地点数据，直接输出 CSV。

这个脚本作为 IDE 内置 LLM 的辅助工具，
将文章正文整理成便于 LLM 处理的格式。
"""

import json
import csv
import sys
import re
from pathlib import Path

# 旅行文章列表（由 filter_travel.py 筛选）
TRAVEL_LIST = Path('/tmp/heye-prompts/travel_articles.txt')

# CSV 字段
CSV_FIELDS = [
    "id", "province", "city", "place_name", "full_name", "region",
    "visit_date", "trip_tag", "excerpt", "snacks", "search_term",
    "lat", "lng", "image_url", "article_url", "featured",
    "source_file", "source_title", "extractor_notes", "human_reviewed",
]


def load_travel_files():
    """加载旅行文章文件列表"""
    if not TRAVEL_LIST.exists():
        print("[!] 旅行文章列表不存在，请先运行 filter_travel.py")
        return []

    files = []
    with open(TRAVEL_LIST, 'r') as f:
        for line in f:
            line = line.strip()
            if line and Path(line).exists():
                files.append(line)
    return files


def batch_articles(files, batch_size=5):
    """将文章分批，每批生成一个合并的 prompt"""
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        articles = []
        for f in batch:
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                articles.append(data)
            except:
                continue
        yield articles


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'

    if cmd == 'list':
        # 列出旅行文章
        files = load_travel_files()
        print(f"共 {len(files)} 篇旅行文章")
        for f in files[:20]:
            print(f"  {Path(f).name}")
        if len(files) > 20:
            print(f"  ... 还有 {len(files)-20} 篇")

    elif cmd == 'batch':
        # 生成批处理 prompt
        batch_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 5

        files = load_travel_files()
        batches = list(batch_articles(files, batch_size))

        if batch_idx >= len(batches):
            print(f"[!] 批次 {batch_idx} 不存在，共 {len(batches)} 批")
            return

        batch = batches[batch_idx]
        combined = []
        for a in batch:
            combined.append({
                'source_file': a.get('source_file', ''),
                'title': a.get('title', ''),
                'date': a.get('date', ''),
                'region': a.get('region', ''),
                'body_preview': a.get('body', '')[:3000],
            })

        output = json.dumps(combined, ensure_ascii=False, indent=2)
        print(output)

    elif cmd == 'count':
        files = load_travel_files()
        print(f"旅行文章总数: {len(files)}")
        batches = list(batch_articles(files, 5))
        print(f"批次数（每批5篇）: {len(batches)}")

    else:
        print("用法: python travel_data_tool.py [list|batch|count]")
        print("  list   - 列出旅行文章")
        print("  batch N [SIZE] - 生成第N批文章的合并prompt")
        print("  count  - 统计数量")


if __name__ == '__main__':
    main()
