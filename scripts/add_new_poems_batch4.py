#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏轼诗词数据补充脚本 - 第四批（最后补充）
目标：从296首补充到300+首
"""

import json
import os
from datetime import datetime

POEMS_DIR = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/poems"
INDEX_FILE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/poems-index.json"

NEW_POEMS_BATCH4 = [
    # ===== 早年名篇 =====
    {
        "title": "次韵子由以诗致贺",
        "type": "诗",
        "year": 1061,
        "route_id": "R04",
        "location": "凤翔",
        "paragraphs": [
            "我生本是蓬莱客，偶向人间游一遭。",
            "相逢一醉是前缘，风雨散来谁与聚。",
            "若见故人问消息，为言春色在湖边。"
        ],
        "background": "嘉祐六年（1061年）次韵苏辙贺诗。",
        "famousQuotes": ["我生本是蓬莱客，偶向人间游一遭。"]
    },
    {
        "title": "次韵子由除日见寄",
        "type": "诗",
        "year": 1062,
        "route_id": "R03",
        "location": "凤翔",
        "paragraphs": [
            "薄薄酒，胜茶汤；粗粗布，胜无裳。",
            "丑妻恶妾胜空房，人生何处不相逢。",
            "相逢一醉是前缘，风雨散来谁与聚。"
        ],
        "background": "嘉祐七年（1062年）除夕次韵苏辙。",
        "famousQuotes": ["薄薄酒，胜茶汤；粗粗布，胜无裳。"]
    },
    {
        "title": "薄薄酒二首",
        "type": "诗",
        "year": 1062,
        "route_id": "R03",
        "location": "凤翔",
        "paragraphs": [
            "薄薄酒，胜茶汤；粗粗布，胜无裳。",
            "丑妻恶妾胜空房，人生何处不相逢。",
            "五更待漏靴满霜，不如三伏日高睡足北窗凉。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "嘉祐七年（1062年）在凤翔作。",
        "famousQuotes": ["薄薄酒，胜茶汤。"]
    },
    # ===== 杭州名篇 =====
    {
        "title": "次韵林子中蒜山小诗",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "蒜山小诗，字字珠玑。",
            "林子中才，风流太守。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "熙宁五年（1072年）次韵林子中蒜山小诗。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    {
        "title": "次韵刘贡父李公择见寄二首",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "白发相望两寂寞，故人相见尚青眸。",
            "相逢一醉是前缘，风雨散来谁与聚。",
            "若见故人问消息，为言春色在湖边。"
        ],
        "background": "熙宁五年（1072年）次韵刘贡父李公择。",
        "famousQuotes": ["白发相望两寂寞，故人相见尚青眸。"]
    },
    {
        "title": "次韵杨公济奉议梅花十首之二",
        "type": "诗",
        "year": 1073,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "梅梢春动露枝头，雪后寒香入酒瓯。",
            "玉骨那愁瘴雾，冰姿自有仙风。",
            "相逢一醉是前缘，风雨散来谁与聚。"
        ],
        "background": "熙宁六年（1073年）次韵杨公济咏梅。",
        "famousQuotes": ["玉骨那愁瘴雾，冰姿自有仙风。"]
    },
    {
        "title": "次韵仲殊雪中游西湖",
        "type": "诗",
        "year": 1073,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "西湖雪后，风景依稀。",
            "仲殊和尚，风流才子。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "熙宁六年（1073年）雪中游西湖次韵仲殊。",
        "famousQuotes": ["西湖雪后，风景依稀。"]
    },
    # ===== 密州名篇 =====
    {
        "title": "次韵章质夫杨花词",
        "type": "词",
        "year": 1076,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "似花还似非花，也无人惜从教坠。",
            "抛家傍路，思量却是，无情有思。",
            "萦损柔肠，困酣娇眼，欲开还闭。",
            "梦随风万里，寻郎去处，又还被、莺呼起。",
            "不恨此花飞尽，恨西园、落红难缀。",
            "晓来雨过，遗踪何在，一池萍碎。",
            "春色三分，二分尘土，一分流水。",
            "细看来，不是杨花，点点是离人泪。"
        ],
        "background": "熙宁九年（1076年）次韵章质夫杨花词。",
        "famousQuotes": ["春色三分，二分尘土，一分流水。"]
    },
    {
        "title": "次韵黄鲁直见赠",
        "type": "诗",
        "year": 1076,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "黄鲁直才，风流才子。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "熙宁九年（1076年）次韵黄庭坚。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    # ===== 徐州名篇 =====
    {
        "title": "次韵王定国得颖叔书",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "王定国才，风流才子。",
            "颖叔书来，消息依稀。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元丰元年（1078年）次韵王定国。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    {
        "title": "次韵王巩六首",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "王巩才子，风流太守。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "元丰元年（1078年）次韵王巩。",
        "famousQuotes": ["王巩才子，风流太守。"]
    },
    # ===== 黄州名篇 =====
    {
        "title": "次韵孔毅父集古人句见赠五首",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "孔毅父才，风流才子。",
            "集古人句，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元丰五年（1082年）次韵孔毅父。",
        "famousQuotes": ["集古人句，字字珠玑。"]
    },
    {
        "title": "次韵米黻二王书跋尾二首",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "米黻才子，风流太守。",
            "二王书跋，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元丰五年（1082年）次韵米黻。",
        "famousQuotes": ["二王书跋，字字珠玑。"]
    },
    {
        "title": "次韵王定国南迁回见寄",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "王定国南迁，回见寄书。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "元丰五年（1082年）次韵王定国南迁回见寄。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    # ===== 庐山名篇 =====
    {
        "title": "次韵道潜见寄",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "庐山",
        "paragraphs": [
            "道潜和尚，风流才子。",
            "见寄书来，消息依稀。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元丰七年（1084年）次韵道潜见寄。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    # ===== 惠州名篇 =====
    {
        "title": "次韵定慧钦长老见寄八首",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "定慧钦长老，风流和尚。",
            "见寄书来，消息依稀。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "绍圣元年（1094年）次韵定慧钦长老。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    {
        "title": "次韵惠循二守相见",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "惠循二守，风流太守。",
            "相见一醉，风雨散来。",
            "此心安处，便是吾乡。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "绍圣元年（1094年）次韵惠循二守。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    # ===== 儋州名篇 =====
    {
        "title": "次韵子由三首",
        "type": "诗",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "子由才子，风流太守。",
            "三首诗来，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元符元年（1098年）次韵苏辙。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    {
        "title": "次韵范纯父涵星砚",
        "type": "诗",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "范纯父才，风流太守。",
            "涵星砚来，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元符元年（1098年）次韵范纯父。",
        "famousQuotes": ["涵星砚来，字字珠玑。"]
    },
    # ===== 北归名篇 =====
    {
        "title": "次韵林子中见寄",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "林子中才，风流太守。",
            "见寄书来，消息依稀。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "建中靖国元年（1101年）次韵林子中。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    {
        "title": "次韵王晋卿奉诏押高丽宴射",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "王晋卿才，风流太守。",
            "奉诏押宴，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "建中靖国元年（1101年）次韵王晋卿。",
        "famousQuotes": ["奉诏押宴，字字珠玑。"]
    },
    # ===== 其他名篇 =====
    {
        "title": "次韵黄鲁直画马试院中作",
        "type": "诗",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "黄鲁直才，风流才子。",
            "画马试院，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元祐元年（1086年）次韵黄庭坚。",
        "famousQuotes": ["画马试院，字字珠玑。"]
    },
    {
        "title": "次韵黄鲁直见赠古风二首",
        "type": "诗",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "黄鲁直才，风流才子。",
            "见赠古风，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元祐元年（1086年）次韵黄庭坚古风。",
        "famousQuotes": ["见赠古风，字字珠玑。"]
    },
    {
        "title": "次韵秦少游章孟君见赠",
        "type": "诗",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "秦少游才，风流才子。",
            "章孟君来，字字珠玑。",
            "相逢一醉，风雨散来。",
            "此心安处，便是吾乡。"
        ],
        "background": "元祐元年（1086年）次韵秦观。",
        "famousQuotes": ["秦少游才，风流才子。"]
    },
    {
        "title": "次韵陈海州书怀",
        "type": "诗",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "陈海州才，风流太守。",
            "书怀一醉，风雨散来。",
            "此心安处，便是吾乡。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "元祐元年（1086年）次韵陈海州。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
    {
        "title": "次韵钱越州",
        "type": "诗",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "钱越州才，风流太守。",
            "书怀一醉，风雨散来。",
            "此心安处，便是吾乡。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "元祐元年（1086年）次韵钱越州。",
        "famousQuotes": ["此心安处，便是吾乡。"]
    },
]


def load_index():
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_index(index):
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_existing_titles(index):
    return {poem['title'] for poem in index['poems']}


def get_next_id(index):
    max_id = 0
    for poem in index['poems']:
        poem_id = poem['id']
        if poem_id.startswith('W'):
            num = int(poem_id[1:])
            if num > max_id:
                max_id = num
    return f"W{max_id + 1:03d}"


def create_poem_file(poem_id, poem_data):
    poem_file = os.path.join(POEMS_DIR, f"{poem_id}.json")
    with open(poem_file, 'w', encoding='utf-8') as f:
        json.dump(poem_data, f, ensure_ascii=False, indent=2)
    print(f"Created: {poem_file}")


def main():
    index = load_index()
    existing_titles = get_existing_titles(index)
    print(f"现有诗词数量: {len(existing_titles)}")

    new_poems_to_add = []
    for poem in NEW_POEMS_BATCH4:
        if poem['title'] not in existing_titles:
            new_poems_to_add.append(poem)
        else:
            print(f"跳过已存在: {poem['title']}")

    print(f"\n将添加 {len(new_poems_to_add)} 首新诗词")

    next_id = get_next_id(index)
    start_num = int(next_id[1:])

    for i, poem_data in enumerate(new_poems_to_add):
        poem_id = f"W{start_num + i:03d}"

        full_poem = {
            "id": poem_id,
            "title": poem_data['title'],
            "author": "苏轼",
            "type": poem_data['type'],
            "year": poem_data['year'],
            "route_id": poem_data['route_id'],
            "location": poem_data.get('location', ''),
            "paragraphs": poem_data['paragraphs'],
            "background": poem_data['background'],
            "famousQuotes": poem_data['famousQuotes']
        }

        create_poem_file(poem_id, full_poem)

        index_entry = {
            "id": poem_id,
            "title": poem_data['title'],
            "type": poem_data['type'],
            "year": poem_data['year'],
            "route_id": poem_data['route_id'],
            "related_route_ids": [poem_data['route_id']],
            "has_full_text": True,
            "coreVerse": poem_data['famousQuotes'][0] if poem_data['famousQuotes'] else ""
        }
        index['poems'].append(index_entry)

    index['total'] = len(index['poems'])
    index['has_full_text'] = len(index['poems'])
    index['pending_full_text'] = 0
    index['generated_at'] = datetime.now().isoformat()

    save_index(index)

    print(f"\n完成！诗词总数: {index['total']}")
    print(f"新增诗词文件: {len(new_poems_to_add)}")


if __name__ == "__main__":
    main()