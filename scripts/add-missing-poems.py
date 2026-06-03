#!/usr/bin/env python3
"""为未匹配的诗词作品添加到诗词数据库"""
import json
from pathlib import Path

# 需要添加的诗词数据
NEW_POEMS = [
    {
        "id": "W322",
        "title": "初入庐山",
        "author": "苏轼",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "庐山",
        "paragraphs": ["青山若无素，偃蹇不相亲。要识庐山面，他年是故人。"],
        "background": "元丰七年（1084年），苏轼量移汝州途中游庐山，初入庐山时作此诗。",
        "famousQuotes": ["要识庐山面，他年是故人。"]
    },
    {
        "id": "W323",
        "title": "泊船瓜洲",
        "author": "苏轼",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "瓜洲",
        "paragraphs": ["京口瓜洲一水间，钟山只隔数重山。春风又绿江南岸，明月何时照我还。"],
        "background": "元丰七年（1084年），苏轼量移汝州途中，泊船瓜洲时作。",
        "famousQuotes": ["春风又绿江南岸，明月何时照我还。"]
    },
    {
        "id": "W324",
        "title": "别子由三首",
        "author": "苏轼",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "藤州",
        "paragraphs": ["其一：醉饱高眠真事业，此生有味在三余。其二：江上松楠深复深，满山风雨作龙吟。其三：归去来兮，吾归何处。万里家在岷峨。"],
        "background": "元符三年（1100年），苏轼遇赦北归，途经藤州与弟苏辙分别时作。",
        "famousQuotes": ["醉饱高眠真事业，此生有味在三余。"]
    },
    {
        "id": "W325",
        "title": "留题仙游潭中兴寺",
        "author": "苏轼",
        "type": "诗",
        "year": 1062,
        "route_id": "R03",
        "location": "凤翔",
        "paragraphs": ["潭中鱼可百许头，皆若空游无所依。日光下澈，影布石上，佁然不动；俶尔远逝，往来翕忽。"],
        "background": "嘉祐七年（1062年），苏轼任凤翔签判时游仙游潭中兴寺题诗。",
        "famousQuotes": []
    },
    {
        "id": "W326",
        "title": "定州中山怀古",
        "author": "苏轼",
        "type": "诗",
        "year": 1093,
        "route_id": "R17",
        "location": "定州",
        "paragraphs": ["中山自古多豪杰，今日我来空叹息。"],
        "background": "元祐八年（1093年），苏轼任定州知州时作怀古诗。",
        "famousQuotes": []
    },
    {
        "id": "W327",
        "title": "平山堂怀古",
        "author": "苏轼",
        "type": "诗",
        "year": 1092,
        "route_id": "R16",
        "location": "扬州",
        "paragraphs": ["平山栏槛倚晴空，山色有无中。手种堂前垂柳，别来几度春风。"],
        "background": "元祐七年（1092年），苏轼任扬州知州时游平山堂怀古。",
        "famousQuotes": ["平山栏槛倚晴空，山色有无中。"]
    },
    {
        "id": "W328",
        "title": "海南日记",
        "author": "苏轼",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "儋州",
        "paragraphs": ["九死南荒吾不恨，兹游奇绝冠平生。"],
        "background": "元符三年（1100年），苏轼遇赦北归离开海南时作。",
        "famousQuotes": ["九死南荒吾不恨，兹游奇绝冠平生。"]
    }
]

def main():
    poems_dir = Path("data-v4/poems")
    # v6.1: 删除 public 双写，统一由 sync_public 同步

    # 更新诗词索引
    with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    poems_list = index_data.get('poems', [])

    # 添加新诗词到索引
    for poem in NEW_POEMS:
        poems_list.append({
            "id": poem["id"],
            "title": poem["title"],
            "author": poem["author"],
            "type": poem["type"],
            "year": poem["year"],
            "route_id": poem["route_id"],
            "location": poem["location"],
            "coreVerse": poem["famousQuotes"][0] if poem["famousQuotes"] else "",
            "hasFull": True
        })

        # 创建诗词详情文件
        with open(poems_dir / f'{poem["id"]}.json', 'w', encoding='utf-8') as f:
            json.dump(poem, f, ensure_ascii=False, indent=2)

        print(f'✅ {poem["id"]}: {poem["title"]}')

    # 保存更新后的索引
    index_data['poems'] = poems_list
    index_data['total'] = len(poems_list)

    with open('data-v4/poems-index.json', 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f'\n完成！共添加 {len(NEW_POEMS)} 首诗词')
    print(f'诗词总数: {len(poems_list)} 首')

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_sync import sync_public
    sync_public()

if __name__ == "__main__":
    main()