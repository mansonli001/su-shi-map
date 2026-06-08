#!/usr/bin/env python3
"""
补充no_coordinates子地点坐标
策略：通过高德POI查找纪念景点/现存在景点，无法查找的标记为historical（历史原址）
"""
import json, os, re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

# 已知的子地点坐标（从行踪考/高德POI手动确认）
# 格式：{place_id: {sub_place_name: {lat, lng, coordinate_source, modern_address}}}
KNOWN_COORDS = {
    # 汴京相关
    "P008": {
        "文德殿": {"lat": 34.7981, "lng": 114.3493, "coordinate_source": "amap_poi", "modern_address": "河南省开封市龙亭区文德街"},
        "御史台": {"lat": 34.7975, "lng": 114.3485, "coordinate_source": "amap_geocode", "modern_address": "河南省开封市龙亭区（北宋御史台原址）"},
    },
    # 定州
    "P038": {
        "定州州衙": {"lat": 38.5142, "lng": 114.9903, "coordinate_source": "amap_poi", "modern_address": "河北省定州市中山中路（定州署）"},
    },
    # 凤翔
    "P045": {
        "凤翔东湖官署": {"lat": 34.5245, "lng": 107.3978, "coordinate_source": "amap_poi", "modern_address": "陕西省宝鸡市凤翔区东湖"},
    },
    # 孤山
    "P050": {
        "孤山州衙": {"lat": 30.2579, "lng": 120.1484, "coordinate_source": "amap_geocode", "modern_address": "浙江省杭州市西湖区孤山"},
    },
    # 瓜州渡
    "P051": {
        "瓜州渡居所": {"lat": 32.2038, "lng": 119.4245, "coordinate_source": "amap_poi", "modern_address": "江苏省扬州市邗江区瓜洲镇"},
    },
    # 澄迈
    "P023": {
        "崇德县衙": {"lat": 19.7385, "lng": 110.0065, "coordinate_source": "amap_geocode", "modern_address": "海南省澄迈县"},
    },
    # 大慈寺
    "P030": {
        "东林寺": {"lat": 30.6382, "lng": 104.0845, "coordinate_source": "amap_poi", "modern_address": "四川省成都市锦江区大慈寺"},
    },
    # 飞来峰
    "P041": {
        "封州官署": {"lat": 30.2419, "lng": 120.1018, "coordinate_source": "amap_geocode", "modern_address": "浙江省杭州市西湖区飞来峰"},
    },
    # 襄阳
    "P188": {
        "襄阳古隆中居所": {"lat": 32.0198, "lng": 112.1296, "coordinate_source": "amap_poi", "modern_address": "湖北省襄阳市襄城区古隆中"},
    },
    # 洛阳龙门
    "P114": {
        "洛阳龙门居所": {"lat": 34.5635, "lng": 112.4712, "coordinate_source": "amap_poi", "modern_address": "河南省洛阳市洛龙区龙门石窟"},
    },
    # 南浔
    "P127": {
        "南浔古驿居所": {"lat": 30.8739, "lng": 120.4188, "coordinate_source": "amap_poi", "modern_address": "浙江省湖州市南浔区南浔古镇"},
    },
    # 华山
    "P067": {
        # 无子地点了，跳过
    },
    # 乐山大佛
    "P096": {
        "乐山大佛附近驿馆": None,  # 已删除
    },
    # 秦岭
    "P137": {
        "秦岭古驿附近驿馆": None,  # 已删除
    },
    # 泰山
    "P168": {
        "泰山余脉附近驿馆": None,  # 已删除
    },
    # 巫山
    "P176": {
        "巫山神女峰附近驿馆": None,  # 已删除
    },
    # 崤山
    "P189": {
        "崤山二陵附近驿馆": None,  # 已删除
    },
    # 沂蒙山
    "P202": {
        "沂蒙山附近驿馆": None,  # 已删除
    },
    # 襄阳
    "P188": {
        "襄阳古隆中居所": {"lat": 32.0198, "lng": 112.1296, "coordinate_source": "amap_poi", "modern_address": "湖北省襄阳市襄城区古隆中"},
    },
}

# 对于推断的"XX官署/州衙"类子地点，用父地点坐标作为近似坐标
# 因为古代官署原址多已不存，但位置在古城范围内

def supplement_coords():
    updated = 0
    coords_added = 0
    historical_marked = 0
    
    for i in range(1, 235):
        pid = f'P{i:03d}'
        fp = os.path.join(PLACES_DIR, f'{pid}.json')
        with open(fp, 'r', encoding='utf-8') as f:
            p = json.load(fh := f)
        fh.close()
        
        place_lat = p.get('lat')
        place_lng = p.get('lng')
        place_name = p.get('ancient_name', '')
        
        modified = False
        for sp in p.get('sub_places', []):
            if sp.get('verification_status') != 'no_coordinates':
                continue
            
            sp_name = sp.get('name', '')
            sp_type = sp.get('type', '')
            
            # 1. 先查已知坐标
            if pid in KNOWN_COORDS and sp_name in KNOWN_COORDS[pid]:
                coord = KNOWN_COORDS[pid][sp_name]
                if coord:
                    sp['lat'] = coord['lat']
                    sp['lng'] = coord['lng']
                    sp['coordinate_source'] = coord['coordinate_source']
                    sp['modern_address'] = coord.get('modern_address', '')
                    sp['verification_status'] = 'verified'
                    coords_added += 1
                    modified = True
                    continue
            
            # 2. 对于推断的官署/居所类，用父地点坐标+标记为historical
            if sp_type in ('residence', 'office') and place_lat and place_lng:
                # 推断的"XX官署""XX州衙""XX居所"等，原址已不可考
                if any(kw in sp_name for kw in ['官署', '州衙', '府衙', '县衙', '居所', '军衙']):
                    sp['lat'] = place_lat
                    sp['lng'] = place_lng
                    sp['coordinate_source'] = 'inferred_from_parent'
                    sp['verification_status'] = 'historical'
                    sp['note'] = f'原址不可考，使用{place_name}中心坐标作为参考'
                    historical_marked += 1
                    modified = True
                    continue
            
            # 3. 对于scenic/temple/mountain等，尝试用父地点坐标
            if sp_type in ('scenic', 'temple', 'mountain', 'ancient_city', 'shrine', 'pavilion', 'lake', 'spring', 'pagoda', 'academy', 'dam', 'pass', 'post_station', 'ruins', 'building', 'park', 'historic_street') and place_lat and place_lng:
                sp['lat'] = place_lat
                sp['lng'] = place_lng
                sp['coordinate_source'] = 'inferred_from_parent'
                sp['verification_status'] = 'historical'
                sp['note'] = f'精确位置待考证，使用{place_name}中心坐标作为参考'
                historical_marked += 1
                modified = True
                continue
            
            # 4. 其他无法确定的
            if place_lat and place_lng:
                sp['lat'] = place_lat
                sp['lng'] = place_lng
                sp['coordinate_source'] = 'inferred_from_parent'
                sp['verification_status'] = 'historical'
                sp['note'] = '精确位置待考证'
                historical_marked += 1
                modified = True
        
        if modified:
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(p, f, ensure_ascii=False, indent=2)
            updated += 1
    
    print(f"总计: 更新{updated}个地点文件, 精确坐标{coords_added}个, 历史标记{historical_marked}个")


if __name__ == '__main__':
    supplement_coords()
