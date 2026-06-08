#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补充v4中缺少美食的地点
"""
import json
import os

V4_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'

# 补充缺失的美食
MISSING_FOODS = {
    '陈仓': ['宝鸡擀面皮', '豆花泡馍', '西凤酒'],
    '大别山边缘古道': ['山区特产', '土猪肉', '笋干'],
    '大庾岭': ['南安板鸭', '赣州脐橙', '客家菜'],
    '洪州': ['南昌拌粉', '瓦罐汤', '藜蒿炒腊肉'],
    '淮水': ['淮扬菜', '鱼鲜', '河蟹'],
    '嘉州': ['乐山甜皮鸭', '钵钵鸡', '跷脚牛肉'],
    '江淮水乡驿道': ['淮扬菜', '蟹黄汤包', '扬州炒饭'],
    '江南运河': ['苏式糕点', '太湖三白', '阳澄湖大闸蟹'],
    '江南运河全线': ['苏式糕点', '浙菜', '淮扬菜'],
    '江州': ['九江茶饼', '庐山石鸡', '鄱阳湖鱼'],
    '利州': ['广元凉面', '剑门豆腐', '昭化古城小吃'],
    '廉州': ['合浦月饼', '北海海鲜', '珍珠'],
    '庐州': ['合肥烘糕', '庐州小吃', '巢湖银鱼'],
    '南都': ['商丘糟鱼', '归德府小吃', '胡辣汤'],
    '虔州': ['赣州鱼饼', '宁都肉丸', '赣南脐橙'],
    '戎州': ['宜宾燃面', '竹筒酒', '李庄白肉'],
    '润州': ['锅盖面', '蟹黄汤包', '香醋'],
    '太湖西岸古村落': ['太湖三白', '阳澄湖大闸蟹', '苏式糕点'],
    '太湖沿岸': ['太湖三白', '太湖银鱼', '阳澄湖大闸蟹'],
    '相州': ['安阳血糕', '道口烧鸡', '安阳皮渣'],
    '兴元': ['汉中面皮', '菜豆腐', '浆水面'],
    '益州官署': ['川菜', '火锅', '成都小吃'],
    '郁林': ['玉林牛巴', '陆川猪脚', '博白空心菜'],
    '筠州': ['高安腐竹', '宜春扎粉', '赣菜'],
    '运河全线风光': ['京杭大运河沿线美食'],
    '长江': ['江鲜', '河鱼', '水产'],
    '长江下游全线': ['江鲜', '太湖三白', '阳澄湖大闸蟹'],
    '长江沿岸渡口': ['江鲜', '渡口特色小吃'],
    '真定': ['正定八大碗', '马家卤鸡', '崩肝'],
}

def supplement_missing():
    files = sorted([f for f in os.listdir(V4_DIR) if f.endswith('.json')])
    
    updated = 0
    for filename in files:
        path = os.path.join(V4_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        ancient_name = data.get('ancient_name', '')
        
        if not data.get('foods') and ancient_name in MISSING_FOODS:
            data['foods'] = MISSING_FOODS[ancient_name]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            updated += 1
    
    # 验证
    foods_count = 0
    for filename in files:
        path = os.path.join(V4_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('foods'):
            foods_count += 1
    
    print(f"补充完成: {updated} 个")
    print(f"现有美食地点: {foods_count}/{len(files)}")

if __name__ == "__main__":
    supplement_missing()
