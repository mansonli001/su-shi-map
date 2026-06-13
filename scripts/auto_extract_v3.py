#!/usr/bin/env python3
"""
贺野旅行地点精提取脚本 v3
核心改进：地点粒度以城市/景区为单位，不以文章标题为 place_name

策略：
1. 先识别每篇文章属于哪个城市/景区
2. 同一城市/景区的多篇文章合并为一个地点
3. 选最佳 excerpt（有感受、有画面、原文原话）
4. snacks 合并去重
5. trip_tag 按出行线路分配
"""

import json
import csv
import re
from pathlib import Path
from collections import defaultdict

TRAVEL_LIST = Path('/tmp/heye-prompts/travel_articles.txt')

# 城市/景区 → (province, city, place_name, search_term)
# 按优先级排序，长关键词优先匹配
CITY_PLACE_MAP = [
    # 2022 南下之旅 - 河北段
    ('保定', '河北', '保定市', '保定', '河北保定'),
    ('白洋淀', '河北', '安新县', '白洋淀', '河北安新白洋淀'),
    ('石家庄', '河北', '石家庄市', '石家庄', '河北石家庄'),
    ('邯郸', '河北', '邯郸市', '邯郸', '河北邯郸'),
    # 安徽段
    ('合肥', '安徽', '合肥市', '合肥', '安徽合肥'),
    ('九华山', '安徽', '池州市', '九华山', '安徽池州九华山'),
    ('查济', '安徽', '宣城市', '查济古镇', '安徽宣城查济古镇'),
    ('三河古镇', '安徽', '合肥市', '三河古镇', '安徽合肥三河古镇'),
    ('蚌埠', '安徽', '蚌埠市', '蚌埠', '安徽蚌埠'),
    # 江苏段
    ('扬州', '江苏', '扬州市', '扬州', '江苏扬州'),
    ('黎里', '江苏', '苏州市', '黎里古镇', '江苏苏州黎里古镇'),
    ('同里', '江苏', '苏州市', '同里古镇', '江苏苏州同里古镇'),
    ('甪直', '江苏', '苏州市', '甪直古镇', '江苏苏州甪直古镇'),
    ('苏州', '江苏', '苏州市', '苏州', '江苏苏州'),
    ('平江路', '江苏', '苏州市', '平江路', '江苏苏州平江路'),
    # 浙江段
    ('舟山', '浙江', '舟山市', '舟山', '浙江舟山'),
    ('嵊泗', '浙江', '嵊泗县', '嵊泗列岛', '浙江嵊泗'),
    ('朱家尖', '浙江', '舟山市', '朱家尖', '浙江舟山朱家尖'),
    ('宁波', '浙江', '宁波市', '宁波', '浙江宁波'),
    ('杭州', '浙江', '杭州市', '杭州', '浙江杭州'),
    ('温州', '浙江', '温州市', '温州', '浙江温州'),
    # 山西段
    ('晋阳湖', '山西', '太原市', '晋阳湖', '山西太原晋阳湖'),
    ('平遥', '山西', '平遥县', '平遥古城', '山西平遥古城'),
    ('太原', '山西', '太原市', '太原', '山西太原'),
    # 河南段
    ('开封', '河南', '开封市', '开封', '河南开封'),
    ('郑州', '河南', '郑州市', '郑州', '河南郑州'),
    ('洛阳', '河南', '洛阳市', '洛阳', '河南洛阳'),
    ('老君山', '河南', '洛阳市', '老君山', '河南洛阳老君山'),
    # 福建段
    ('武夷山', '福建', '武夷山市', '武夷山', '福建武夷山'),
    ('霞浦', '福建', '霞浦县', '霞浦', '福建霞浦'),
    ('平潭', '福建', '平潭县', '平潭岛', '福建平潭岛'),
    ('鼓浪屿', '福建', '厦门市', '鼓浪屿', '福建厦门鼓浪屿'),
    ('厦门', '福建', '厦门市', '厦门', '福建厦门'),
    ('南靖', '福建', '漳州市', '南靖土楼', '福建漳州南靖土楼'),
    ('福州', '福建', '福州市', '福州', '福建福州'),
    ('宁德', '福建', '宁德市', '宁德', '福建宁德'),
    ('婺源', '江西', '上饶市', '婺源', '江西上饶婺源'),
    # 广东段
    ('潮州', '广东', '潮州市', '潮州', '广东潮州'),
    ('广州', '广东', '广州市', '广州', '广东广州'),
    ('佛山', '广东', '佛山市', '佛山', '广东佛山'),
    ('湛江', '广东', '湛江市', '湛江', '广东湛江'),
    ('茂名', '广东', '茂名市', '茂名', '广东茂名'),
    ('阳江', '广东', '阳江市', '阳江', '广东阳江'),
    ('澳门', '广东', '澳门', '澳门', '澳门'),
    # 海南段
    ('三亚', '海南', '三亚市', '三亚', '海南三亚'),
    ('海口', '海南', '海口市', '海口', '海南海口'),
    ('五指山', '海南', '五指山市', '五指山', '海南五指山'),
    ('琼海', '海南', '琼海市', '琼海', '海南琼海'),
    ('乐东', '海南', '乐东县', '乐东九所', '海南乐东九所'),
    ('西岛', '海南', '三亚市', '西岛', '海南三亚西岛'),

    # 2023 东北自驾
    ('哈尔滨', '黑龙江', '哈尔滨市', '哈尔滨', '黑龙江哈尔滨'),
    ('呼伦贝尔', '内蒙古', '呼伦贝尔市', '呼伦贝尔', '内蒙古呼伦贝尔'),
    ('满洲里', '内蒙古', '满洲里市', '满洲里', '内蒙古满洲里'),
    ('阿尔山', '内蒙古', '阿尔山市', '阿尔山', '内蒙古阿尔山'),
    ('室韦', '内蒙古', '额尔古纳市', '室韦', '内蒙古额尔古纳室韦'),
    ('黑山头', '内蒙古', '额尔古纳市', '黑山头', '内蒙古额尔古纳黑山头'),
    ('建三江', '黑龙江', '佳木斯市', '建三江', '黑龙江佳木斯建三江'),
    ('阿城', '黑龙江', '哈尔滨市', '阿城', '黑龙江哈尔滨阿城'),

    # 2023 西北自驾
    ('德令哈', '青海', '德令哈市', '德令哈', '青海德令哈'),
    ('吐鲁番', '新疆', '吐鲁番市', '吐鲁番', '新疆吐鲁番'),
    ('大海道', '新疆', '哈密市', '大海道', '新疆哈密大海道'),
    ('喀纳斯', '新疆', '阿勒泰地区', '喀纳斯', '新疆阿勒泰喀纳斯'),
    ('白哈巴', '新疆', '阿勒泰地区', '白哈巴', '新疆阿勒泰白哈巴'),
    ('禾木', '新疆', '阿勒泰地区', '禾木', '新疆阿勒泰禾木'),
    ('赛里木湖', '新疆', '博乐市', '赛里木湖', '新疆博乐赛里木湖'),
    ('伊犁', '新疆', '伊宁市', '伊犁', '新疆伊犁'),
    ('独库公路', '新疆', '独山子区', '独库公路', '新疆独库公路'),
    ('乌鲁木齐', '新疆', '乌鲁木齐市', '乌鲁木齐', '新疆乌鲁木齐'),
    ('敦煌', '甘肃', '敦煌市', '敦煌', '甘肃敦煌'),

    # 2024 北上之旅
    ('克什克腾', '内蒙古', '克什克腾旗', '克什克腾旗', '内蒙古克什克腾旗'),
    ('达里湖', '内蒙古', '克什克腾旗', '达里湖', '内蒙古克什克腾旗达里湖'),
    ('阿斯哈图', '内蒙古', '克什克腾旗', '阿斯哈图石林', '内蒙古克什克腾旗阿斯哈图石林'),
    ('赤峰', '内蒙古', '赤峰市', '赤峰', '内蒙古赤峰'),

    # 2025 春节西藏
    ('拉萨', '西藏', '拉萨市', '拉萨', '西藏拉萨'),
    ('日喀则', '西藏', '日喀则市', '日喀则', '西藏日喀则'),
    ('雅鲁藏布', '西藏', '林芝市', '雅鲁藏布大峡谷', '西藏林芝雅鲁藏布大峡谷'),

    # 2025 云南之旅
    ('红河', '云南', '红河州', '红河哈尼梯田', '云南红河哈尼梯田'),
    ('元阳', '云南', '红河州', '元阳梯田', '云南元阳梯田'),

    # 2025-2026 带父南下
    ('景德镇', '江西', '景德镇市', '景德镇', '江西景德镇'),
    ('柳州', '广西', '柳州市', '柳州', '广西柳州'),
    ('北海', '广西', '北海市', '北海', '广西北海'),
    ('沈阳', '辽宁', '沈阳市', '沈阳', '辽宁沈阳'),
    ('长春', '吉林', '长春市', '长春', '吉林长春'),
    ('武汉', '湖北', '武汉市', '武汉', '湖北武汉'),
    ('襄阳', '湖北', '襄阳市', '襄阳', '湖北襄阳'),

    # 其他
    ('泸州', '四川', '泸州市', '泸州', '四川泸州'),
    ('赣州', '江西', '赣州市', '赣州', '江西赣州'),
    ('绿江村', '辽宁', '丹东市', '绿江村', '辽宁丹东绿江村'),
    ('重庆', '重庆', '重庆市', '重庆', '重庆'),
    ('上海', '上海', '上海市', '上海', '上海'),
    ('天津', '天津', '天津市', '天津', '天津'),

    # 海外
    ('马来西亚', '马来西亚', '', '马来西亚', '马来西亚'),
    ('日本', '日本', '', '日本', '日本'),
    ('仙本那', '马来西亚', '沙巴州', '仙本那', '马来西亚沙巴仙本那'),
    ('吉隆坡', '马来西亚', '吉隆坡', '吉隆坡', '马来西亚吉隆坡'),
    ('大阪', '日本', '大阪府', '大阪', '日本大阪'),
    ('京都', '日本', '京都府', '京都', '日本京都'),
]


def match_city(title: str, body_500: str, region: str) -> dict:
    """匹配文章对应的城市/景区"""
    text = title + ' ' + body_500

    # 优先匹配长关键词
    for keyword, province, city, place_name, search_term in CITY_PLACE_MAP:
        if keyword in text:
            return {
                'province': province,
                'city': city,
                'place_name': place_name,
                'search_term': search_term,
            }

    # 兜底：用 region
    region_map = {
        '北京': None,  # 北京文章单独处理
        '天津': {'province': '天津', 'city': '天津市', 'place_name': '天津', 'search_term': '天津'},
        '上海': {'province': '上海', 'city': '上海市', 'place_name': '上海', 'search_term': '上海'},
    }
    if region in region_map:
        return region_map[region]

    return None


def extract_excerpt_v3(body: str, place_name: str) -> str:
    """精确 excerpt 提取：必须是原文原话"""
    # 去掉标题行和元数据
    lines = body.split('\n')
    content = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('原创') or '有生余年' in line:
            continue
        if re.match(r'^\d{4}-\d{2}-\d{2}', line):
            continue
        content.append(line)

    full_text = '\n'.join(content)

    # 按句号/感叹号/问号分句
    sentences = re.split(r'(?<=[。！？])', full_text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) >= 15]

    # 评分
    def score(s):
        sc = 0
        # 含"我"加分（个人视角）
        if '我' in s:
            sc += 3
        # 感受词加分
        feeling = ['觉得', '爱死', '简直', '多么', '震撼', '远超', '难忘',
                   '不想走', '想住', '想留', '一生', '永远', '太美', '真好',
                   '治愈', '温暖', '孤独', '寂寞', '矫情', '羞愧',
                   '爱', '喜欢', '感动', '美', '绝', '牛', '棒']
        for w in feeling:
            if w in s:
                sc += 2
        # 画面感加分
        visual = ['阳光', '月光', '海风', '落日', '晚霞', '星空',
                  '溪流', '山', '水', '花', '树', '雨', '雪', '海']
        for w in visual:
            if w in s:
                sc += 1
        # 长度适中
        if 30 <= len(s) <= 100:
            sc += 2
        elif 20 <= len(s) <= 120:
            sc += 1
        # 排除纯攻略/价格
        if re.search(r'\d+元|\d+块|门票|开放时间|攻略|交通|路线|住宿推荐', s):
            sc -= 5
        # 排除太长的引用/历史描述
        if len(s) > 150:
            sc -= 2
        return sc

    scored = [(score(s), s) for s in sentences]
    scored.sort(key=lambda x: -x[0])

    # 取得分最高的
    if scored and scored[0][0] >= 3:
        excerpt = scored[0][1]
        # 确保不超过 150 字
        if len(excerpt) > 150:
            excerpt = excerpt[:147] + '…'
        return excerpt

    # 兜底：取含"我"的第一句
    for s in sentences:
        if '我' in s and len(s) <= 150:
            return s

    return ''


def extract_snacks_v3(body: str) -> list:
    """精确食物提取"""
    snacks = []

    # 只匹配明确吃了/喝了/点了/要了/买了的食物
    patterns = [
        r'吃了[一]?[个份碗盘碟]?([\u4e00-\u9fff]{2,6}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|串|丸|粥|饭|羹|卷|酥|冻|馍|豆腐|豆花|奶茶))',
        r'喝了[一]?[个份碗杯]?([\u4e00-\u9fff]{2,6}(?:汤|茶|酒|汁|奶茶))',
        r'要了[一]?[个份碗盘碟]?([\u4e00-\u9fff]{2,6}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|串|丸|粥|饭|羹|卷|酥|冻|馍|豆腐|豆花|奶茶|茶|酒))',
        r'点了[一]?[个份碗盘碟]?([\u4e00-\u9fff]{2,6}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|串|丸|粥|饭|羹|卷|酥|冻|馍|豆腐|豆花|奶茶|茶|酒))',
        r'买了[一]?[个份碗]?([\u4e00-\u9fff]{2,6}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|串|丸|粥|饭|羹|卷|酥|冻|馍|豆腐|豆花|奶茶|茶|酒))',
        # 特殊格式：XX火烧
        r'([\u4e00-\u9fff]{2,4}火烧)',
        # 特殊格式：XX火锅
        r'([\u4e00-\u9fff]{2,4}火锅)',
        # 特殊格式：XX米线
        r'([\u4e00-\u9fff]{2,4}米线)',
        # 特殊格式：XX奶茶
        r'([\u4e00-\u9fff]{2,4}奶茶)',
    ]

    exclude = {'东西', '午饭', '晚饭', '早餐', '早饭', '晚餐', '午餐',
               '点心', '零食', '美食', '饭菜', '很多酒', '点啤酒',
               '这么多酒', '一顿羊肉', '一顿椰子鸡', '一顿饭',
               '一个肋板火烧', '一个板肠火烧',
               '便饭', '顿午饭', '顿晚饭', '顿饭', '顿早餐',
               '堆的水果面包', '点当地的白酒', '两瓶啤酒', '两瓶柠檬茶',
               '们在用柴火锅', '馄饨和俩包', '啤酒',
               }

    for pattern in patterns:
        matches = re.findall(pattern, body)
        for m in matches:
            # 清理：去掉量词前缀
            m = re.sub(r'^[一个份碗盘碟瓶杯壶两几]', '', m)
            # 清理：去掉"顿""堆"等量词
            m = re.sub(r'^[顿堆些]', '', m)
            # 清理：去掉"的"字
            m = m.replace('的', '')
            if m not in exclude and 2 <= len(m) <= 8:
                snacks.append(m)

    # 去重
    seen = set()
    result = []
    for s in snacks:
        if s not in seen:
            seen.add(s)
            result.append(s)

    return result[:5]


def assign_trip_tag(date: str, title: str) -> str:
    """分配 trip_tag"""
    # 从标题判断
    if '北上之旅' in title:
        return '2024北上之旅'
    if '带老爸' in title or '带老爹' in title or '带倔强' in title:
        return '2025-2026带父南下'
    if '南下' in title:
        return '2022南下之旅'

    # 按日期范围
    if '2022-08' <= date <= '2022-12':
        return '2022南下之旅'
    if '2023-06' <= date <= '2023-07':
        return '2023东北自驾'
    if '2023-08' <= date <= '2023-09':
        return '2023西北自驾'
    if '2024-07' <= date <= '2024-08':
        return '2024北上之旅'
    if '2025-01' <= date <= '2025-02':
        return '2025春节西藏'
    if '2025-08' <= date <= '2025-09':
        return '2025云南之旅'
    if '2025-12' <= date or '2026-01' <= date <= '2026-04':
        return '2025-2026带父南下'

    return ''


def main():
    files = []
    with open(TRAVEL_LIST, 'r') as f:
        for line in f:
            line = line.strip()
            if line and Path(line).exists():
                files.append(line)

    print(f"加载 {len(files)} 篇旅行文章")

    # 按城市/景区分组
    place_groups = defaultdict(list)

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

        if date < '2022-01-01':
            continue

        # 匹配城市/景区
        place = match_city(title, body[:500], region)
        if not place:
            continue

        # 提取数据
        excerpt = extract_excerpt_v3(body, place['place_name'])
        snacks = extract_snacks_v3(body)
        trip_tag = assign_trip_tag(date, title)

        key = f"{place['province']}_{place['place_name']}"
        place_groups[key].append({
            **place,
            'region': region,
            'visit_date': f"{date[:4]}年{int(date[5:7])}月" if date else '',
            'trip_tag': trip_tag,
            'excerpt': excerpt,
            'snacks': snacks,
            'source_title': title,
            'source_date': date,
        })

    # 合并同一地点
    rows = []
    counter = 1

    for key, articles in sorted(place_groups.items()):
        # 选 excerpt 质量最好的
        best = max(articles, key=lambda a: len(a.get('excerpt', '')))

        # 合并 snacks
        all_snacks = []
        seen = set()
        for a in articles:
            for s in a.get('snacks', []):
                if s not in seen:
                    seen.add(s)
                    all_snacks.append(s)

        # 合并 trip_tag
        trip_tag = ''
        for a in articles:
            if a.get('trip_tag'):
                trip_tag = a['trip_tag']
                break

        # 合并 visit_date（取最早的）
        dates = [a['source_date'] for a in articles if a.get('source_date')]
        visit_date = best['visit_date']
        if dates:
            earliest = min(dates)
            visit_date = f"{earliest[:4]}年{int(earliest[5:7])}月"

        # 判断是否 featured（文章数 >= 3 或有好的 excerpt）
        featured = len(articles) >= 3 or len(best.get('excerpt', '')) >= 50

        row = {
            'id': f'HY{counter:03d}',
            'province': best['province'],
            'city': best['city'],
            'place_name': best['place_name'],
            'full_name': f"{best['province']}·{best['place_name']}",
            'region': best['region'],
            'visit_date': visit_date,
            'trip_tag': trip_tag,
            'excerpt': best['excerpt'],
            'snacks': json.dumps(all_snacks[:5], ensure_ascii=False),
            'search_term': best['search_term'],
            'lat': '',
            'lng': '',
            'image_url': '',
            'article_url': '',
            'featured': str(featured).lower(),
            'source_file': best['source_title'],
            'source_title': best['source_title'],
            'article_count': len(articles),
            'extractor_notes': f'合并自{len(articles)}篇文章',
            'human_reviewed': 'N',
        }
        rows.append(row)
        counter += 1

    # 写入 CSV
    CSV_FIELDS = [
        "id", "province", "city", "place_name", "full_name", "region",
        "visit_date", "trip_tag", "excerpt", "snacks", "search_term",
        "lat", "lng", "image_url", "article_url", "featured",
        "source_file", "source_title", "article_count", "extractor_notes", "human_reviewed",
    ]

    out_path = '/tmp/heye-prompts/heye_locations_v3.csv'
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    # 统计
    provinces = set(r['province'] for r in rows)
    tags = defaultdict(int)
    for r in rows:
        if r['trip_tag']:
            tags[r['trip_tag']] += 1
        else:
            tags['无标签'] += 1
    empty_exc = sum(1 for r in rows if not r.get('excerpt', '').strip())
    empty_snacks = sum(1 for r in rows if r.get('snacks', '[]') == '[]')
    featured_count = sum(1 for r in rows if r['featured'] == 'true')

    print(f"\n✅ v3 精提取完成！")
    print(f"   地点数: {len(rows)}")
    print(f"   覆盖省份: {len(provinces)}")
    print(f"   精选地点: {featured_count}")
    print(f"   空 excerpt: {empty_exc}/{len(rows)}")
    print(f"   空 snacks: {empty_snacks}/{len(rows)}")
    print(f"\n   出行标签:")
    for t in sorted(tags.keys()):
        print(f"     {t}: {tags[t]} 个地点")
    print(f"\n   输出: {out_path}")

    # 输出前10个地点的 excerpt 供检查
    print(f"\n=== 前10个地点 excerpt 抽检 ===")
    for r in rows[:10]:
        exc = r['excerpt'][:60]
        print(f"  {r['full_name']:20s} | {exc}...")
        print(f"  {'':20s} | snacks: {r['snacks'][:40]}")


if __name__ == '__main__':
    main()
