#!/usr/bin/env python3
"""
C级48个地点作品美食补充
依据：苏轼年谱 + 地方特色美食
"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

# C级地点美食补充（按地域分组）
C_PLACE_SUPPLEMENT = {
    # 四川地区
    "P021": {"name": "成都", "foods": [{"name": "麻婆豆腐", "description": "成都名菜，麻辣鲜香", "origin_story": "成都传统名菜", "tag": "成都必吃"}]},
    "P030": {"name": "大慈寺", "foods": [{"name": "成都小吃", "description": "成都传统小吃集合", "origin_story": "成都传统美食", "tag": "成都特色"}]},
    "P045": {"name": "凤翔东湖", "foods": [{"name": "豆花泡馍", "description": "凤翔传统早餐", "origin_story": "凤翔传统美食", "tag": "凤翔必吃"}]},
    "P078": {"name": "嘉州", "foods": [{"name": "乐山钵钵鸡", "description": "乐山名小吃", "origin_story": "嘉州传统美食", "tag": "嘉州必吃"}, {"name": "乐山甜皮鸭", "description": "乐山名菜", "origin_story": "嘉州传统美食", "tag": "嘉州特色"}]},
    "P096": {"name": "乐山大佛", "foods": [{"name": "乐山钵钵鸡", "description": "乐山名小吃", "origin_story": "嘉州传统美食", "tag": "乐山必吃"}]},
    "P139": {"name": "青神平羌江", "foods": [{"name": "青神竹编宴", "description": "青神特色", "origin_story": "青神传统美食", "tag": "青神特色"}]},
    "P207": {"name": "益州官署", "foods": [{"name": "成都小吃", "description": "成都传统小吃", "origin_story": "益州传统美食", "tag": "成都特色"}]},
    
    # 江南地区
    "P049": {"name": "姑苏寒山寺", "foods": [{"name": "苏州松鼠桂鱼", "description": "苏州名菜，外酥里嫩", "origin_story": "苏州传统名菜", "tag": "苏州必吃"}, {"name": "苏式月饼", "description": "苏州传统糕点", "origin_story": "苏州传统美食", "tag": "苏州特色"}]},
    "P090": {"name": "金陵秦淮", "foods": [{"name": "南京盐水鸭", "description": "南京名菜", "origin_story": "金陵传统名菜", "tag": "金陵必吃"}]},
    "P091": {"name": "金陵钟山", "foods": [{"name": "南京盐水鸭", "description": "南京名菜", "origin_story": "金陵传统名菜", "tag": "金陵必吃"}]},
    "P104": {"name": "灵隐天竺", "foods": [{"name": "西湖醋鱼", "description": "杭州名菜", "origin_story": "杭州传统名菜", "tag": "杭州必吃"}]},
    "P161": {"name": "苏州", "foods": [{"name": "松鼠桂鱼", "description": "苏州名菜", "origin_story": "苏州传统名菜", "tag": "苏州必吃"}, {"name": "苏式汤面", "description": "苏州传统面食", "origin_story": "苏州传统美食", "tag": "苏州特色"}]},
    "P205": {"name": "宜兴", "foods": [{"name": "宜兴乌饭", "description": "宜兴传统美食", "origin_story": "宜兴传统美食", "tag": "宜兴特色"}, {"name": "宜兴百合", "description": "宜兴特产", "origin_story": "宜兴特产", "tag": "宜兴特色"}]},
    "P206": {"name": "宜兴田园", "foods": [{"name": "宜兴乌饭", "description": "宜兴传统美食", "origin_story": "宜兴传统美食", "tag": "宜兴特色"}]},
    
    # 江西地区
    "P047": {"name": "赣江古道", "foods": [{"name": "南昌拌粉", "description": "南昌传统早餐", "origin_story": "江西传统美食", "tag": "南昌必吃"}]},
    "P076": {"name": "吉安", "foods": [{"name": "吉安炒粉", "description": "吉安传统小吃", "origin_story": "吉安传统美食", "tag": "吉安特色"}]},
    "P079": {"name": "吉水", "foods": [{"name": "吉水米粉", "description": "吉水传统小吃", "origin_story": "吉水传统美食", "tag": "吉水特色"}]},
    "P108": {"name": "庐山", "foods": [{"name": "庐山石鱼", "description": "庐山特色山珍", "origin_story": "庐山传统美食", "tag": "庐山特色"}]},
    "P109": {"name": "庐山全山", "foods": [{"name": "庐山石鱼", "description": "庐山特色山珍", "origin_story": "庐山传统美食", "tag": "庐山特色"}]},
    "P132": {"name": "鄱阳湖", "foods": [{"name": "鄱阳湖银鱼", "description": "鄱阳湖特产", "origin_story": "鄱阳湖传统美食", "tag": "鄱阳特色"}]},
    "P155": {"name": "石钟山", "foods": [{"name": "湖口糟鱼", "description": "湖口传统名菜", "origin_story": "石钟山所在地传统美食", "tag": "湖口特色"}]},
    
    # 湖北/湖南地区
    "P083": {"name": "江陵", "foods": [{"name": "荆州鱼糕", "description": "荆州名菜", "origin_story": "江陵传统名菜", "tag": "荆州必吃"}]},
    "P084": {"name": "江陵荆州古城", "foods": [{"name": "荆州鱼糕", "description": "荆州名菜", "origin_story": "江陵传统名菜", "tag": "荆州必吃"}]},
    "P092": {"name": "荆州", "foods": [{"name": "荆州鱼糕", "description": "荆州名菜", "origin_story": "荆州传统名菜", "tag": "荆州必吃"}]},
    "P176": {"name": "巫山神女峰", "foods": [{"name": "巫山烤鱼", "description": "巫山名菜", "origin_story": "巫山传统美食", "tag": "巫山必吃"}]},
    
    # 山东地区
    "P036": {"name": "登州", "foods": [{"name": "蓬莱小面", "description": "蓬莱传统面食", "origin_story": "登州传统美食", "tag": "登州特色"}]},
    "P095": {"name": "莱州", "foods": [{"name": "莱州梭子蟹", "description": "莱州特产", "origin_story": "莱州海鲜特产", "tag": "莱州特色"}]},
    "P216": {"name": "郓州", "foods": [{"name": "郓城壮馍", "description": "郓城传统面食", "origin_story": "郓州传统美食", "tag": "郓州特色"}]},
    
    # 广东/海南地区
    "P054": {"name": "广州", "foods": [{"name": "广式早茶", "description": "广州传统饮食文化", "origin_story": "广州传统美食", "tag": "广州必吃"}]},
    "P097": {"name": "雷州", "foods": [{"name": "雷州白切狗", "description": "雷州传统美食", "origin_story": "雷州传统美食", "tag": "雷州特色"}, {"name": "雷州大粽", "description": "雷州传统小吃", "origin_story": "雷州传统美食", "tag": "雷州特色"}]},
    "P098": {"name": "雷州伏波庙", "foods": [{"name": "雷州大粽", "description": "雷州传统小吃", "origin_story": "雷州传统美食", "tag": "雷州特色"}]},
    "P141": {"name": "琼州", "foods": [{"name": "海南鸡饭", "description": "海南名菜", "origin_story": "琼州传统美食", "tag": "琼州必吃"}, {"name": "清补凉", "description": "海南传统甜品", "origin_story": "琼州传统美食", "tag": "琼州特色"}]},
    
    # 河南/陕西地区
    "P020": {"name": "陈州", "foods": [{"name": "陈州胡辣汤", "description": "河南传统早餐", "origin_story": "陈州传统美食", "tag": "陈州特色"}]},
    "P080": {"name": "剑门关", "foods": [{"name": "剑门豆腐宴", "description": "剑门关名菜", "origin_story": "剑门关传统美食", "tag": "剑门必吃"}]},
    "P081": {"name": "剑门关古驿", "foods": [{"name": "剑门豆腐宴", "description": "剑门关名菜", "origin_story": "剑门关传统美食", "tag": "剑门必吃"}]},
    "P099": {"name": "利州", "foods": [{"name": "广元蒸凉面", "description": "广元传统小吃", "origin_story": "利州传统美食", "tag": "广元特色"}]},
    "P125": {"name": "南都", "foods": [{"name": "商丘水激豆片", "description": "商丘传统小吃", "origin_story": "南都传统美食", "tag": "商丘特色"}]},
    "P156": {"name": "寿州", "foods": [{"name": "寿州大救驾", "description": "寿县名点", "origin_story": "寿州传统名点", "tag": "寿州必吃"}]},
    
    # 安徽地区
    "P026": {"name": "滁州琅琊山", "foods": [{"name": "滁州烧鸡", "description": "滁州传统名吃", "origin_story": "滁州传统美食", "tag": "滁州特色"}]},
    "P114": {"name": "洛阳龙门", "foods": [{"name": "洛阳水席", "description": "洛阳传统宴席", "origin_story": "洛阳传统名菜", "tag": "洛阳必吃"}]},
    "P127": {"name": "南浔古驿", "foods": [{"name": "南浔蹄髈", "description": "南浔传统名菜", "origin_story": "南浔传统美食", "tag": "南浔特色"}]},
    
    # 广西地区
    "P100": {"name": "廉州", "foods": [{"name": "合浦月饼", "description": "合浦传统糕点", "origin_story": "廉州传统美食", "tag": "廉州特色"}]},
    "P101": {"name": "廉州白石镇", "foods": [{"name": "合浦月饼", "description": "合浦传统糕点", "origin_story": "廉州传统美食", "tag": "廉州特色"}]},
    "P170": {"name": "藤州", "foods": [{"name": "藤县米粉", "description": "藤州传统小吃", "origin_story": "广西传统美食", "tag": "藤州特色"}]},
    
    # 其他
    "P041": {"name": "飞来峰", "foods": [{"name": "杭州片儿川", "description": "杭州传统面食", "origin_story": "杭州传统美食", "tag": "杭州特色"}]},
    "P050": {"name": "孤山", "foods": [{"name": "西湖醋鱼", "description": "杭州名菜", "origin_story": "杭州传统名菜", "tag": "杭州必吃"}]},
    "P112": {"name": "罗浮山", "foods": [{"name": "客家酿豆腐", "description": "惠州客家名菜", "origin_story": "罗浮山地区传统美食", "tag": "罗浮山特色"}]},
    "P023": {"name": "澄迈", "foods": [{"name": "澄迈瑞溪牛肉", "description": "澄迈特产", "origin_story": "澄迈传统美食", "tag": "澄迈特色"}]},
    "P038": {"name": "定州", "foods": [{"name": "定州焖子", "description": "定州名吃", "origin_story": "定州传统美食", "tag": "定州必吃"}]},
    "P188": {"name": "襄阳古隆中", "foods": [{"name": "襄阳牛肉面", "description": "襄阳名吃", "origin_story": "襄阳传统美食", "tag": "襄阳必吃"}]},
}


def supplement_c_places():
    updated = 0
    foods_added = 0
    
    for place_id, supplement in C_PLACE_SUPPLEMENT.items():
        fp = os.path.join(PLACES_DIR, f'{place_id}.json')
        if not os.path.exists(fp):
            continue
        
        with open(fp, 'r', encoding='utf-8') as f:
            place_data = json.load(f)
        
        # 补充美食
        if supplement.get('foods'):
            existing_foods = place_data.get('foods', [])
            existing_food_names = {f.get('name') if isinstance(f, dict) else f for f in existing_foods}
            for food in supplement['foods']:
                if food['name'] not in existing_food_names:
                    existing_foods.append(food)
                    foods_added += 1
            place_data['foods'] = existing_foods
        
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(place_data, f, ensure_ascii=False, indent=2)
        
        updated += 1
    
    print(f"总计: 更新{updated}个C级地点, 新增{foods_added}条美食")


if __name__ == '__main__':
    supplement_c_places()
