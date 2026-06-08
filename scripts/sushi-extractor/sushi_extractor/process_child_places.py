#!/usr/bin/env python3
"""
批量处理B级子地点型地点
这些地点是某个父城市的子地点，标记parent_place并设置主坐标
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STAGING_DIR = os.path.join(SCRIPT_DIR, 'staging')

# 子地点到父地点的映射
CHILD_PARENT_MAP = {
    # 汴京子地点
    'P009': {'parent': 'P008', 'parent_name': '汴京', 'name': '翰林院', 'type': 'scenic', 'desc': '苏轼任翰林学士时办公之所'},
    'P010': {'parent': 'P008', 'parent_name': '汴京', 'name': '太学', 'type': 'scenic', 'desc': '苏轼与太学相关活动'},
    'P011': {'parent': 'P008', 'parent_name': '汴京', 'name': '文德殿', 'type': 'scenic', 'desc': '苏轼朝见皇帝之所'},
    'P012': {'parent': 'P008', 'parent_name': '汴京', 'name': '御史台', 'type': 'scenic', 'desc': '乌台诗案审讯之所'},
    'P013': {'parent': 'P008', 'parent_name': '汴京', 'name': '御史台监狱', 'type': 'scenic', 'desc': '乌台诗案苏轼被关押之所'},
    'P014': {'parent': 'P008', 'parent_name': '汴京', 'name': '政事堂', 'type': 'scenic', 'desc': '苏轼任翰林学士时参与政事'},
    # 杭州子地点
    'P050': {'parent': 'P058', 'parent_name': '杭州', 'name': '孤山', 'type': 'scenic', 'desc': '西湖中孤山，苏轼常游之地'},
    'P106': {'parent': 'P058', 'parent_name': '杭州', 'name': '六井遗迹', 'type': 'scenic', 'desc': '苏轼疏浚六井遗迹'},
    'P148': {'parent': 'P058', 'parent_name': '杭州', 'name': '三潭印月', 'type': 'scenic', 'desc': '苏轼疏浚西湖后设三塔'},
    'P181': {'parent': 'P058', 'parent_name': '杭州', 'name': '西湖全域', 'type': 'scenic', 'desc': '苏轼两次任职杭州疏浚西湖'},
    'P182': {'parent': 'P058', 'parent_name': '杭州', 'name': '苏堤', 'type': 'scenic', 'desc': '苏轼疏浚西湖所筑长堤'},
    # 眉山子地点
    'P117': {'parent': 'P116', 'parent_name': '眉山', 'name': '玻璃江', 'type': 'scenic', 'desc': '眉山玻璃江，苏轼少年常游'},
    'P118': {'parent': 'P116', 'parent_name': '眉山', 'name': '眉山故居', 'type': 'residence', 'desc': '苏家故居'},
    'P147': {'parent': 'P116', 'parent_name': '眉山', 'name': '三苏祠', 'type': 'scenic', 'desc': '三苏父子故居及祠堂'},
    'P115': {'parent': 'P116', 'parent_name': '眉山', 'name': '蟆颐山蟆颐观', 'type': 'scenic', 'desc': '苏轼少年时常游之地'},
    # 金陵子地点
    'P090': {'parent': 'P089', 'parent_name': '金陵', 'name': '秦淮河', 'type': 'scenic', 'desc': '金陵秦淮河'},
    'P091': {'parent': 'P089', 'parent_name': '金陵', 'name': '钟山', 'type': 'scenic', 'desc': '金陵钟山（紫金山）'},
    # 扬州子地点
    'P199': {'parent': 'P198', 'parent_name': '扬州', 'name': '平山堂', 'type': 'scenic', 'desc': '欧阳修所建，苏轼常来凭吊'},
    'P200': {'parent': 'P198', 'parent_name': '扬州', 'name': '瘦西湖旧址', 'type': 'scenic', 'desc': '扬州瘦西湖'},
    # 徐州子地点
    'P196': {'parent': 'P195', 'parent_name': '徐州', 'name': '黄楼', 'type': 'scenic', 'desc': '苏轼守徐州时所建'},
    # 密州子地点
    'P120': {'parent': 'P119', 'parent_name': '密州', 'name': '超然台', 'type': 'scenic', 'desc': '苏轼修葺超然台，作《超然台记》'},
    # 惠州子地点
    'P001': {'parent': 'P075', 'parent_name': '惠州', 'name': '白鹤峰', 'type': 'residence', 'desc': '苏轼在惠州的白鹤峰新居'},
    'P074': {'parent': 'P075', 'parent_name': '惠州', 'name': '合江楼', 'type': 'residence', 'desc': '苏轼初到惠州的居所'},
    # 镇江子地点
    'P227': {'parent': 'P146', 'parent_name': '润州', 'name': '金山寺', 'type': 'scenic', 'desc': '苏轼《游金山寺》'},
    # 儋州子地点
    'P228': {'parent': 'P034', 'parent_name': '儋州', 'name': '中和古镇', 'type': 'scenic', 'desc': '儋州治所中和镇'},
    # 廉州子地点
    'P101': {'parent': 'P100', 'parent_name': '廉州', 'name': '白石镇', 'type': 'scenic', 'desc': '廉州白石镇'},
    # 凤翔子地点
    'P045': {'parent': 'P044', 'parent_name': '凤翔', 'name': '东湖', 'type': 'scenic', 'desc': '苏轼疏浚凤翔东湖'},
    # 庐山
    'P108': {'parent': None, 'parent_name': None, 'name': '庐山', 'type': 'scenic', 'desc': '苏轼游庐山，作《题西林壁》'},
    'P109': {'parent': 'P108', 'parent_name': '庐山', 'name': '庐山全山', 'type': 'scenic', 'desc': '苏轼游庐山诸峰'},
    # 渑池
    'P124': {'parent': None, 'parent_name': None, 'name': '渑池僧舍', 'type': 'scenic', 'desc': '苏轼《和子由渑池怀旧》'},
    # 瓜州
    'P051': {'parent': None, 'parent_name': None, 'name': '瓜州渡', 'type': 'scenic', 'desc': '苏轼《泊船瓜洲》'},
    'P052': {'parent': 'P051', 'parent_name': '瓜州渡', 'name': '瓜州古渡', 'type': 'scenic', 'desc': '瓜州古渡口'},
    # 定州子地点
    'P038': {'parent': 'P039', 'parent_name': '定州', 'name': '定州城', 'type': 'scenic', 'desc': '定州城内景点'},
}

def process_child_places():
    for place_id, info in CHILD_PARENT_MAP.items():
        staging_file = os.path.join(STAGING_DIR, f"{place_id}.json")
        
        if not os.path.exists(staging_file):
            print(f"  ⚠️ Staging不存在: {place_id}")
            continue
        
        with open(staging_file, 'r', encoding='utf-8') as f:
            staging = json.load(f)
        
        # 设置主坐标
        if not staging.get('main_coords') and staging.get('sub_places'):
            first_sp = staging['sub_places'][0]
            if first_sp.get('lat'):
                staging['main_coords'] = {
                    'name': info['name'],
                    'lat': first_sp['lat'],
                    'lng': first_sp['lng'],
                    'modern_address': first_sp.get('modern_address', ''),
                    'coordinate_source': first_sp.get('coordinate_source', ''),
                    'reason': f"{info['name']}为{'核心居住地' if info['type'] == 'residence' else '核心景点'}"
                }
        
        # 标记父地点
        if info['parent']:
            staging['report']['parent_place'] = info['parent']
            staging['report']['parent_place_name'] = info['parent_name']
            staging['report']['note'] = f"{info['name']}为{info['parent_name']}的子地点"
        
        staging['report']['methodology'] = 'sxzk-gps-methodology v1.0'
        
        with open(staging_file, 'w', encoding='utf-8') as f:
            json.dump(staging, f, ensure_ascii=False, indent=2)
        
        parent_info = f"→ {info['parent_name']}" if info['parent'] else "(独立地点)"
        print(f"  ✅ {place_id} {staging['ancient_name']}: {info['name']} {parent_info}")

if __name__ == '__main__':
    process_child_places()
