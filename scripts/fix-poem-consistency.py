#!/usr/bin/env python3
"""修复诗词数据一致性问题"""
import json
from pathlib import Path

DATA_DIR = Path('data-v4')
POEMS_DIR = DATA_DIR / 'poems'

# 需要修复的数据
FIXES = {
    # C002: 应该是"江城子·密州出猎"，但当前文件是"桄榔庵记（铭）"
    'C002': {
        "id": "C002",
        "title": "江城子·密州出猎",
        "author": "苏轼",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "老夫聊发少年狂，左牵黄，右擎苍，锦帽貂裘，千骑卷平冈。为报倾城随太守，亲射虎，看孙郎。",
            "酒酣胸胆尚开张，鬓微霜，又何妨！持节云中，何日遣冯唐？会挽雕弓如满月，西北望，射天狼。"
        ],
        "background": "熙宁八年（1075年），苏轼在密州知州任上，出城打猎时写下这首豪放词。词中抒发了词人的壮志豪情和爱国情怀。",
        "famousQuotes": [
            "老夫聊发少年狂，左牵黄，右擎苍。",
            "会挽雕弓如满月，西北望，射天狼。"
        ]
    },
    # C012: 应该是"水调歌头·明月几时有"，但当前文件是"和陶归去来兮辞"
    'C012': {
        "id": "C012",
        "title": "水调歌头·明月几时有",
        "author": "苏轼",
        "type": "词",
        "year": 1076,
        "month": 9,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "丙辰中秋，欢饮达旦，大醉，作此篇，兼怀子由。",
            "明月几时有？把酒问青天。不知天上宫阙，今夕是何年。我欲乘风归去，又恐琼楼玉宇，高处不胜寒。起舞弄清影，何似在人间。",
            "转朱阁，低绮户，照无眠。不应有恨，何事长向别时圆？人有悲欢离合，月有阴晴圆缺，此事古难全。但愿人长久，千里共婵娟。"
        ],
        "background": "熙宁九年（1076年）中秋，苏轼在密州任上，思念弟弟苏辙，写下这首千古绝唱。词中表达了对亲人的思念和对人生的哲理思考。",
        "famousQuotes": [
            "明月几时有？把酒问青天。",
            "但愿人长久，千里共婵娟。"
        ]
    },
    # W014: 文件缺失，应该是"桄榔庵记（铭）"
    'W014': {
        "id": "W014",
        "title": "桄榔庵记（铭）",
        "author": "苏轼",
        "type": "文",
        "year": 1098,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "南方之地产桄榔，予至惠州一年，命工斩材而造室。",
            "桄榔叶大，干如柱，予之庵取其廉而直也。",
            "古之君子，居不求安，食不求饱，而于道味得之。予迁于南海，气序之变，饮食之难，无足怪者。然予以为此庵，可以安乐也。",
            "铭曰：桄榔为柱，直而不污。我作此庵，居之宴如。南海浩浩，吾道不孤。"
        ],
        "background": "绍圣五年（1098年），苏轼在惠州居住期间，亲手建造了一座桄榔庵，并作此铭文。文章表达了苏轼随遇而安、豁达乐观的人生态度。",
        "famousQuotes": [
            "桄榔为柱，直而不污。我作此庵，居之宴如。",
            "南海浩浩，吾道不孤。"
        ]
    },
    # W015: 文件缺失，应该是"和陶归去来兮辞"
    'W015': {
        "id": "W015",
        "title": "和陶归去来兮辞",
        "author": "苏轼",
        "type": "文",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "归去来兮，田园将芜胡不归。",
            "既自以心为形役，奚惆怅而独悲。",
            "悟已往之不谏，知来者之可追。",
            "实迷途其未远，觉今是而昨非。"
        ],
        "background": "元符元年（1098年）在儋州和陶渊明《归去来兮辞》。",
        "famousQuotes": [
            "悟已往之不谏，知来者之可追。",
            "实迷途其未远，觉今是而昨非。"
        ]
    }
}

def atomic_write_json(path: Path, data: dict):
    """原子写入JSON文件"""
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    import os
    os.replace(tmp, path)

def fix_consistency():
    print('=== 开始修复诗词数据一致性 ===')
    print('=' * 60)
    
    fixed_count = 0
    for pid, correct_data in FIXES.items():
        fpath = POEMS_DIR / f'{pid}.json'
        
        # 读取现有文件（如果存在）
        if fpath.exists():
            with open(fpath, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            current_title = current_data.get('title', '')
            correct_title = correct_data.get('title', '')
            
            if current_title != correct_title:
                print(f'修复 [{pid}]: "{current_title}" → "{correct_title}"')
                atomic_write_json(fpath, correct_data)
                fixed_count += 1
            else:
                print(f'跳过 [{pid}]: 标题已正确')
        else:
            print(f'创建 [{pid}]: "{correct_data["title"]}"')
            atomic_write_json(fpath, correct_data)
            fixed_count += 1
    
    print('=' * 60)
    print(f'修复完成，共修复 {fixed_count} 个文件')

if __name__ == '__main__':
    fix_consistency()