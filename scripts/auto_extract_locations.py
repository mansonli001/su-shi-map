#!/usr/bin/env python3
"""
贺野旅行地点自动提取脚本
从已筛选的旅行文章 prompt JSON 中，自动提取结构化地点数据。

策略：
1. 利用 PDF 元数据中的 region（IP归属地）确定省份
2. 利用标题中的地名确定具体地点
3. 利用正文中的食物描述提取 snacks
4. 利用正文中的感受句子提取 excerpt
5. 生成 search_term 供人工核实坐标

输出 CSV，需人工校验坐标和补充信息。
"""

import json
import csv
import re
import sys
from pathlib import Path

# 省份 → 简称映射（region 字段到标准省名）
REGION_TO_PROVINCE = {
    '北京': '北京', '天津': '天津', '上海': '上海', '重庆': '重庆',
    '河北': '河北', '山西': '山西', '辽宁': '辽宁', '吉林': '吉林',
    '黑龙江': '黑龙江', '江苏': '江苏', '浙江': '浙江', '安徽': '安徽',
    '福建': '福建', '江西': '江西', '山东': '山东', '河南': '河南',
    '湖北': '湖北', '湖南': '湖南', '广东': '广东', '海南': '海南',
    '四川': '四川', '贵州': '贵州', '云南': '云南', '陕西': '陕西',
    '甘肃': '甘肃', '青海': '青海', '台湾': '台湾',
    '内蒙古': '内蒙古', '广西': '广西', '西藏': '西藏',
    '宁夏': '宁夏', '新疆': '新疆',
    '马来西亚': '马来西亚', '日本': '日本',
}

# 标题中的地名 → (province, city, place_name) 映射
TITLE_PLACE_PATTERNS = [
    # 具体景区/城市
    (r'武夷山', ('福建', '武夷山市', '武夷山')),
    (r'九华山', ('安徽', '池州市', '九华山')),
    (r'查济', ('安徽', '宣城市', '查济古镇')),
    (r'三河古镇', ('安徽', '三河市', '三河古镇')),
    (r'笔架山', ('安徽', '池州市', '笔架山')),
    (r'扬州', ('江苏', '扬州市', '扬州')),
    (r'甪直', ('江苏', '苏州市', '甪直古镇')),
    (r'同里', ('江苏', '苏州市', '同里古镇')),
    (r'黎里', ('江苏', '苏州市', '黎里古镇')),
    (r'朱家尖', ('浙江', '舟山市', '朱家尖')),
    (r'嵊泗', ('浙江', '嵊泗县', '嵊泗列岛')),
    (r'宁波', ('浙江', '宁波市', '宁波')),
    (r'杭州', ('浙江', '杭州市', '杭州')),
    (r'鼓浪屿', ('福建', '厦门市', '鼓浪屿')),
    (r'霞浦', ('福建', '霞浦县', '霞浦')),
    (r'平潭', ('福建', '平潭县', '平潭岛')),
    (r'南靖土楼', ('福建', '漳州市', '南靖土楼')),
    (r'潮州', ('广东', '潮州市', '潮州')),
    (r'保定', ('河北', '保定市', '保定')),
    (r'白洋淀', ('河北', '安新县', '白洋淀')),
    (r'石家庄', ('河北', '石家庄市', '石家庄')),
    (r'河北省博物馆', ('河北', '石家庄市', '河北省博物馆')),
    (r'晋阳湖', ('山西', '太原市', '晋阳湖')),
    (r'平遥', ('山西', '平遥县', '平遥古城')),
    (r'开封', ('河南', '开封市', '开封')),
    (r'合肥', ('安徽', '合肥市', '合肥')),
    (r'曲江', ('陕西', '西安市', '曲江新区')),
    (r'未央宫', ('陕西', '西安市', '未央宫遗址')),
    (r'护国寺', ('北京', '西城区', '护国寺')),
    (r'德外', ('北京', '西城区', '德外老街区')),
    (r'西单', ('北京', '西城区', '西单')),
    (r'阿尔山', ('内蒙古', '阿尔山市', '阿尔山')),
    (r'呼伦贝尔', ('内蒙古', '呼伦贝尔市', '呼伦贝尔')),
    (r'满洲里', ('内蒙古', '满洲里市', '满洲里')),
    (r'室韦', ('内蒙古', '额尔古纳市', '室韦')),
    (r'黑山头', ('内蒙古', '额尔古纳市', '黑山头')),
    (r'哈尔滨', ('黑龙江', '哈尔滨市', '哈尔滨')),
    (r'阿城', ('黑龙江', '哈尔滨市', '阿城')),
    (r'绿江村', ('辽宁', '丹东市', '绿江村')),
    (r'德令哈', ('青海', '德令哈市', '德令哈')),
    (r'吐鲁番', ('新疆', '吐鲁番市', '吐鲁番')),
    (r'大海道', ('新疆', '哈密市', '大海道')),
    (r'柳州', ('广西', '柳州市', '柳州')),
    (r'赣州', ('江西', '赣州市', '赣州')),
    (r'佛山', ('广东', '佛山市', '佛山')),
    (r'广州', ('广东', '广州市', '广州')),
    (r'海南', ('海南', '三亚市', '三亚')),
    (r'景德镇', ('江西', '景德镇市', '景德镇')),
    (r'永州', ('湖南', '永州市', '永州')),
    (r'蚌埠', ('安徽', '蚌埠市', '蚌埠')),
    (r'眉州', ('四川', '眉山市', '眉州')),
    (r'泸州', ('四川', '泸州市', '泸州')),
    (r'日喀则', ('西藏', '日喀则市', '日喀则')),
    (r'红河', ('云南', '红河州', '红河哈尼梯田')),
    (r'沈阳', ('辽宁', '沈阳市', '沈阳')),
    (r'长春', ('吉林', '长春市', '长春')),
    (r'武汉', ('湖北', '武汉市', '武汉')),
    (r'郑州', ('河南', '郑州市', '郑州')),
    (r'澳门', ('广东', '澳门', '澳门')),
    (r'舟山', ('浙江', '舟山市', '舟山')),
    (r'苏州', ('江苏', '苏州市', '苏州')),
    (r'建三江', ('黑龙江', '佳木斯市', '建三江')),
    (r'老君山', ('河南', '洛阳市', '老君山')),
    (r'襄阳', ('湖北', '襄阳市', '襄阳')),
    (r'三亚', ('海南', '三亚市', '三亚')),
    (r'游轮', (None, None, None)),  # 特殊标记，需人工处理
]

# 食物提取模式
FOOD_PATTERNS = [
    r'吃了?([\u4e00-\u9fff]{2,6}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|火锅|串|丸|粥|饭|羹|卷|酥|冻|干|饼|馍|火烧|豆腐|豆花))',
    r'喝了?([\u4e00-\u9fff]{2,6}(?:汤|茶|酒|汁|浆))',
    r'([\u4e00-\u9fff]{2,4}火烧)',
    r'([\u4e00-\u9fff]{2,4}火锅)',
    r'([\u4e00-\u9fff]{2,4}炒饭)',
    r'([\u4e00-\u9fff]{2,4}汤包)',
    r'([\u4e00-\u9fff]{2,4}米线)',
]

# 排除的食物词
FOOD_EXCLUDE = {'东西', '午饭', '晚饭', '早餐', '早饭', '晚餐', '午餐', '点心', '零食', '小吃', '美食', '饭菜'}


def extract_place_from_title(title: str, region: str) -> dict:
    """从标题提取地点信息"""
    for pattern, (prov, city, place) in TITLE_PLACE_PATTERNS:
        if re.search(pattern, title):
            if prov is None:
                return None  # 需人工处理
            return {'province': prov, 'city': city, 'place_name': place}

    # 如果标题没有匹配到，用 region 作为省份
    province = REGION_TO_PROVINCE.get(region, '')
    if province:
        # 尝试从标题提取城市名
        return {'province': province, 'city': '', 'place_name': title[:20]}

    return None


def extract_snacks(body: str) -> list:
    """从正文提取食物"""
    snacks = set()
    for pattern in FOOD_PATTERNS:
        matches = re.findall(pattern, body)
        for m in matches:
            if m not in FOOD_EXCLUDE and len(m) >= 2:
                snacks.add(m)
    return list(snacks)[:5]  # 最多5个


def extract_excerpt(body: str) -> str:
    """从正文提取有感受的句子作为 excerpt"""
    # 去掉标题行和元数据行
    lines = body.split('\n')
    content_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 跳过标题和元数据
        if line.startswith('原创') or '有生余年' in line:
            continue
        if re.match(r'^\d{4}-\d{2}-\d{2}', line):
            continue
        content_lines.append(line)

    # 寻找有感受的句子（含"我"字且有描述性内容）
    feeling_patterns = [
        r'我觉得',
        r'我[爱喜欢]',
        r'让我',
        r'我简直',
        r'我多么',
        r'我一生',
        r'我甚至',
        r'真[是的好美棒绝酷牛]',
        r'太[好美棒绝酷牛美]',
        r'超[出过美棒绝酷牛]',
        r'远超',
        r'震撼',
        r'感动',
        r'难忘',
        r'不想走',
        r'不想离',
        r'想住',
        r'想留',
    ]

    candidates = []
    full_text = ' '.join(content_lines)
    sentences = re.split(r'[。！？]', full_text)

    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 150:
            continue
        # 必须含"我"或有强烈感受词
        has_feeling = any(re.search(p, s) for p in feeling_patterns)
        has_me = '我' in s
        if has_feeling or (has_me and len(s) > 30):
            candidates.append(s)

    if candidates:
        # 优先选有感受词的
        for c in candidates:
            if any(re.search(p, c) for p in feeling_patterns):
                return c + '。'
        return candidates[0] + '。'

    # 兜底：取第一段有实质内容的
    for line in content_lines:
        if len(line) > 30 and '我' in line:
            return line[:150]

    return ''


def determine_trip_tag(date: str, title: str, body: str) -> str:
    """判断 trip_tag"""
    # 从标题判断
    if '北上之旅' in title or '北上之旅' in body[:500]:
        return '2024北上之旅'
    if '南下' in title or '南下之旅' in body[:500]:
        return '2022南下之旅'
    if '福建行' in title:
        return '2022福建行'
    if '寒假' in title and ('自驾' in title or '海南' in title):
        return '2024寒假自驾'
    if '游轮' in title or '海洋光谱' in title:
        return '2024游轮之旅'
    if '西藏' in title or '拉萨' in title:
        return '2025春节西藏'
    if '床车' in title or '自驾' in body[:200]:
        # 2023年夏季东北自驾
        if '2023-06' in date or '2023-07' in date:
            return '2023东北自驾'
        if '2023-08' in date:
            return '2023西北自驾'
    if '带老爸' in title or '带老爹' in title or '带倔强' in title:
        return '2025-2026带父南下'
    if '云南' in title or '云南' in body[:200]:
        if '2025-08' in date or '2025-09' in date:
            return '2025云南之旅'

    return ''


def process_travel_articles():
    """处理旅行文章，生成 CSV"""
    travel_list = Path('/tmp/heye-prompts/travel_articles.txt')
    if not travel_list.exists():
        print("[!] 请先运行 filter_travel.py")
        return

    files = []
    with open(travel_list, 'r') as f:
        for line in f:
            line = line.strip()
            if line and Path(line).exists():
                files.append(line)

    print(f"共 {len(files)} 篇旅行文章待处理")

    rows = []
    counter = 1
    skipped = 0

    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except:
            continue

        title = data.get('title', '')
        date = data.get('date', '')
        region = data.get('region', '')
        body = data.get('body', '')

        # 提取地点
        place_info = extract_place_from_title(title, region)
        if not place_info:
            skipped += 1
            continue

        # 提取食物
        snacks = extract_snacks(body)

        # 提取 excerpt
        excerpt = extract_excerpt(body)

        # 判断 trip_tag
        trip_tag = determine_trip_tag(date, title, body)

        # 生成 full_name
        full_name = f"{place_info['province']}·{place_info['place_name']}"

        # 生成 search_term
        search_term = f"{place_info['province']}{place_info['city']}{place_info['place_name']}"

        # 格式化 visit_date
        visit_date = ''
        if date:
            try:
                parts = date.split('-')
                visit_date = f"{parts[0]}年{int(parts[1])}月"
            except:
                pass

        row = {
            'id': f'HY{counter:03d}',
            'province': place_info['province'],
            'city': place_info['city'],
            'place_name': place_info['place_name'],
            'full_name': full_name,
            'region': region,
            'visit_date': visit_date,
            'trip_tag': trip_tag or '',
            'excerpt': excerpt,
            'snacks': json.dumps(snacks, ensure_ascii=False),
            'search_term': search_term,
            'lat': '',
            'lng': '',
            'image_url': '',
            'article_url': '',
            'featured': 'false',
            'source_file': data.get('source_file', ''),
            'source_title': title,
            'extractor_notes': '自动提取，需人工校验',
            'human_reviewed': 'N',
        }
        rows.append(row)
        counter += 1

    # 写入 CSV
    out_path = '/tmp/heye-prompts/heye_locations_auto.csv'
    CSV_FIELDS = [
        "id", "province", "city", "place_name", "full_name", "region",
        "visit_date", "trip_tag", "excerpt", "snacks", "search_term",
        "lat", "lng", "image_url", "article_url", "featured",
        "source_file", "source_title", "extractor_notes", "human_reviewed",
    ]

    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ 提取完成！")
    print(f"   成功: {len(rows)} 条")
    print(f"   跳过: {skipped} 条")
    print(f"   输出: {out_path}")

    # 统计
    provinces = set(r['province'] for r in rows if r['province'])
    trip_tags = set(r['trip_tag'] for r in rows if r['trip_tag'])
    print(f"\n   覆盖省份: {len(provinces)} 个 — {', '.join(sorted(provinces))}")
    print(f"   出行标签: {len(trip_tags)} 个 — {', '.join(sorted(trip_tags))}")


if __name__ == '__main__':
    process_travel_articles()
