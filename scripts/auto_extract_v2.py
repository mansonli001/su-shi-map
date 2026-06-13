#!/usr/bin/env python3
"""
贺野旅行地点精提取脚本 v2
从 prompt JSON 中读取正文，使用更智能的规则提取高质量地点数据。

核心改进：
1. 智能去重：同一城市多篇文章合并为1个地点，选最佳 excerpt
2. 精确 excerpt：优先选含"我"且有感受的原文句子
3. snacks 精提取：只收录明确"吃了""喝了"的食物
4. trip_tag 自动推断：根据日期连续性和地区变化
5. 北京精简：只保留有实质旅行内容的北京地点
"""

import json
import csv
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

# 旅行文章列表
TRAVEL_LIST = Path('/tmp/heye-prompts/travel_articles.txt')

# 省份映射
REGION_MAP = {
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

# 关键旅行线路定义（按时间顺序）
TRIP_ROUTES = [
    {
        'tag': '2022南下之旅',
        'start': '2022-08-16', 'end': '2022-12-31',
        'description': '从北京出发，经河北→安徽→江苏→浙江→山西→河南→福建→广东→海南',
    },
    {
        'tag': '2023东北自驾',
        'start': '2023-06-20', 'end': '2023-07-20',
        'description': '东北自驾：哈尔滨→呼伦贝尔→满洲里→阿尔山',
    },
    {
        'tag': '2023西北自驾',
        'start': '2023-08-01', 'end': '2023-09-15',
        'description': '西北自驾：青海→新疆→甘肃',
    },
    {
        'tag': '2024北上之旅',
        'start': '2024-07-01', 'end': '2024-08-15',
        'description': '北上之旅：内蒙古→黑龙江→吉林',
    },
    {
        'tag': '2025春节西藏',
        'start': '2025-01-20', 'end': '2025-02-10',
        'description': '春节西藏行',
    },
    {
        'tag': '2025云南之旅',
        'start': '2025-08-20', 'end': '2025-09-15',
        'description': '云南之旅',
    },
    {
        'tag': '2025-2026带父南下',
        'start': '2025-12-20', 'end': '2026-04-30',
        'description': '带老爹自驾南下：山东→安徽→江西→广西→海南→广东→澳门',
    },
]

# 地点识别规则：标题关键词 → (province, city, place_name, search_term)
PLACE_RULES = [
    # 2022 南下之旅
    ('保定', '河北', '保定市', '保定', '河北保定市'),
    ('白洋淀', '河北', '安新县', '白洋淀', '河北安新县白洋淀景区'),
    ('石家庄', '河北', '石家庄市', '石家庄', '河北石家庄市'),
    ('河北省博', '河北', '石家庄市', '河北省博物馆', '河北石家庄河北省博物馆'),
    ('九华山', '安徽', '池州市', '九华山', '安徽池州九华山风景区'),
    ('查济', '安徽', '宣城市', '查济古镇', '安徽宣城查济古镇'),
    ('三河古镇', '安徽', '合肥市', '三河古镇', '安徽合肥三河古镇'),
    ('合肥', '安徽', '合肥市', '合肥', '安徽合肥市'),
    ('笔架山', '安徽', '池州市', '笔架山', '安徽池州笔架山'),
    ('扬州', '江苏', '扬州市', '扬州', '江苏扬州市'),
    ('黎里', '江苏', '苏州市', '黎里古镇', '江苏苏州黎里古镇'),
    ('同里', '江苏', '苏州市', '同里古镇', '江苏苏州同里古镇'),
    ('甪直', '江苏', '苏州市', '甪直古镇', '江苏苏州甪直古镇'),
    ('苏州', '江苏', '苏州市', '苏州', '江苏苏州市'),
    ('平江路', '江苏', '苏州市', '平江路', '江苏苏州平江路'),
    ('舟山', '浙江', '舟山市', '舟山', '浙江舟山市'),
    ('嵊泗', '浙江', '嵊泗县', '嵊泗列岛', '浙江嵊泗列岛'),
    ('朱家尖', '浙江', '舟山市', '朱家尖', '浙江舟山朱家尖'),
    ('宁波', '浙江', '宁波市', '宁波', '浙江宁波市'),
    ('杭州', '浙江', '杭州市', '杭州', '浙江杭州市'),
    ('晋阳湖', '山西', '太原市', '晋阳湖', '山西太原晋阳湖'),
    ('平遥', '山西', '平遥县', '平遥古城', '山西平遥古城'),
    ('太原', '山西', '太原市', '太原', '山西太原市'),
    ('开封', '河南', '开封市', '开封', '河南开封市'),
    ('武夷山', '福建', '武夷山市', '武夷山', '福建武夷山风景区'),
    ('霞浦', '福建', '霞浦县', '霞浦', '福建霞浦县'),
    ('平潭', '福建', '平潭县', '平潭岛', '福建平潭岛'),
    ('鼓浪屿', '福建', '厦门市', '鼓浪屿', '福建厦门鼓浪屿'),
    ('南靖土楼', '福建', '漳州市', '南靖土楼', '福建漳州南靖土楼'),
    ('潮州', '广东', '潮州市', '潮州', '广东潮州市'),
    ('三亚', '海南', '三亚市', '三亚', '海南三亚市'),

    # 2023 东北自驾
    ('哈尔滨', '黑龙江', '哈尔滨市', '哈尔滨', '黑龙江哈尔滨市'),
    ('呼伦贝尔', '内蒙古', '呼伦贝尔市', '呼伦贝尔', '内蒙古呼伦贝尔市'),
    ('满洲里', '内蒙古', '满洲里市', '满洲里', '内蒙古满洲里市'),
    ('阿尔山', '内蒙古', '阿尔山市', '阿尔山', '内蒙古阿尔山市'),
    ('室韦', '内蒙古', '额尔古纳市', '室韦', '内蒙古额尔古纳室韦'),
    ('黑山头', '内蒙古', '额尔古纳市', '黑山头', '内蒙古额尔古纳黑山头'),

    # 2023 西北自驾
    ('德令哈', '青海', '德令哈市', '德令哈', '青海德令哈市'),
    ('吐鲁番', '新疆', '吐鲁番市', '吐鲁番', '新疆吐鲁番市'),
    ('大海道', '新疆', '哈密市', '大海道', '新疆哈密大海道'),
    ('喀纳斯', '新疆', '阿勒泰市', '喀纳斯', '新疆阿勒泰喀纳斯'),
    ('白哈巴', '新疆', '阿勒泰市', '白哈巴', '新疆阿勒泰白哈巴'),
    ('禾木', '新疆', '阿勒泰市', '禾木', '新疆阿勒泰禾木'),
    ('赛里木湖', '新疆', '博乐市', '赛里木湖', '新疆博乐赛里木湖'),
    ('伊犁', '新疆', '伊宁市', '伊犁', '新疆伊犁'),
    ('独库公路', '新疆', '独山子区', '独库公路', '新疆独库公路'),

    # 2024 北上之旅
    ('克什克腾', '内蒙古', '克什克腾旗', '克什克腾旗', '内蒙古克什克腾旗'),
    ('达里湖', '内蒙古', '克什克腾旗', '达里湖', '内蒙古克什克腾旗达里湖'),
    ('阿斯哈图', '内蒙古', '克什克腾旗', '阿斯哈图石林', '内蒙古克什克腾旗阿斯哈图石林'),

    # 2025 春节西藏
    ('拉萨', '西藏', '拉萨市', '拉萨', '西藏拉萨市'),
    ('日喀则', '西藏', '日喀则市', '日喀则', '西藏日喀则市'),
    ('雅鲁藏布', '西藏', '林芝市', '雅鲁藏布大峡谷', '西藏林芝雅鲁藏布大峡谷'),

    # 2025 云南之旅
    ('红河', '云南', '红河州', '红河哈尼梯田', '云南红河哈尼梯田'),

    # 2025-2026 带父南下
    ('景德镇', '江西', '景德镇市', '景德镇', '江西景德镇市'),
    ('柳州', '广西', '柳州市', '柳州', '广西柳州市'),
    ('北海', '广西', '北海市', '北海', '广西北海市'),
    ('澳门', '广东', '澳门', '澳门', '广东澳门'),
    ('湛江', '广东', '湛江市', '湛江', '广东湛江市'),
    ('沈阳', '辽宁', '沈阳市', '沈阳', '辽宁沈阳市'),
    ('长春', '吉林', '长春市', '长春', '吉林长春市'),
    ('武汉', '湖北', '武汉市', '武汉', '湖北武汉市'),
    ('郑州', '河南', '郑州市', '郑州', '河南郑州市'),
    ('温州', '浙江', '温州市', '温州', '浙江温州市'),

    # 其他
    ('老君山', '河南', '洛阳市', '老君山', '河南洛阳老君山'),
    ('襄阳', '湖北', '襄阳市', '襄阳', '湖北襄阳市'),
    ('泸州', '四川', '泸州市', '泸州', '四川泸州市'),
    ('赣州', '江西', '赣州市', '赣州', '江西赣州市'),
    ('佛山', '广东', '佛山市', '佛山', '广东佛山市'),
    ('广州', '广东', '广州市', '广州', '广东广州市'),
    ('建三江', '黑龙江', '佳木斯市', '建三江', '黑龙江佳木斯建三江'),
    ('蚌埠', '安徽', '蚌埠市', '蚌埠', '安徽蚌埠市'),
    ('绿江村', '辽宁', '丹东市', '绿江村', '辽宁丹东绿江村'),
    ('阿城', '黑龙江', '哈尔滨市', '阿城', '黑龙江哈尔滨阿城'),
]


def match_place(title: str, region: str) -> dict:
    """根据标题匹配地点"""
    for keyword, province, city, place_name, search_term in PLACE_RULES:
        if keyword in title:
            return {
                'province': province,
                'city': city,
                'place_name': place_name,
                'search_term': search_term,
            }
    # 兜底：用 region
    province = REGION_MAP.get(region, '')
    if province and province != '北京':
        return {
            'province': province,
            'city': '',
            'place_name': title[:15],
            'search_term': f'{province}{title[:15]}',
        }
    return None


def extract_excerpt_v2(body: str) -> str:
    """更精确的 excerpt 提取"""
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
    sentences = [s.strip() for s in sentences if s.strip()]

    # 评分函数
    def score_sentence(s):
        sc = 0
        if '我' in s:
            sc += 3
        feeling_words = ['觉得', '爱', '喜欢', '简直', '多么', '震撼', '感动', '难忘',
                        '远超', '太', '真', '超', '绝', '美', '牛', '棒', '好',
                        '不想走', '不想离', '想住', '想留', '一生', '永远',
                        '羞愧', '矫情', '孤独', '寂寞', '绝望', '温暖', '治愈']
        for w in feeling_words:
            if w in s:
                sc += 2
        # 长度适中
        if 30 <= len(s) <= 120:
            sc += 2
        elif 20 <= len(s) <= 150:
            sc += 1
        # 有画面感
        visual_words = ['看到', '听到', '闻到', '感到', '阳光', '月光', '海风',
                       '落日', '晚霞', '星空', '溪流', '山', '水', '花', '树']
        for w in visual_words:
            if w in s:
                sc += 1
        # 排除纯攻略性
        if re.search(r'\d+元|\d+块|门票|开放时间|攻略|交通', s):
            sc -= 3
        return sc

    # 评分排序
    scored = [(score_sentence(s), s) for s in sentences if len(s) >= 15]
    scored.sort(key=lambda x: -x[0])

    if scored and scored[0][0] > 3:
        return scored[0][1]

    # 兜底：取第一段有"我"的
    for line in content:
        if '我' in line and len(line) > 20:
            # 截取到第一个句号
            match = re.search(r'[^。！？]+[。！？]', line)
            if match:
                return match.group()
            return line[:120]

    return ''


def extract_snacks_v2(body: str) -> list:
    """更精确的食物提取"""
    snacks = []

    # 模式1：吃了/喝了 + 食物名
    patterns = [
        r'吃了[一]?[个份碗盘碟瓶杯壶]?([\u4e00-\u9fff]{2,8}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|火锅|串|丸|粥|饭|羹|卷|酥|冻|干|馍|火烧|豆腐|豆花|奶茶|茶|酒))',
        r'喝了[一]?[个份碗盘碟瓶杯壶]?([\u4e00-\u9fff]{2,8}(?:汤|茶|酒|汁|浆|奶茶))',
        r'要了[一]?[个份碗盘碟瓶杯壶]?([\u4e00-\u9fff]{2,8}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|火锅|串|丸|粥|饭|羹|卷|酥|冻|干|馍|火烧|豆腐|豆花|奶茶|茶|酒))',
        r'点了[一]?[个份碗盘碟瓶杯壶]?([\u4e00-\u9fff]{2,8}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|火锅|串|丸|粥|饭|羹|卷|酥|冻|干|馍|火烧|豆腐|豆花|奶茶|茶|酒))',
        r'买了[一]?[个份碗盘碟瓶杯壶]?([\u4e00-\u9fff]{2,8}(?:汤|面|粉|饼|糕|包|饺|肉|鱼|虾|蟹|鹅|鸡|鸭|火锅|串|丸|粥|饭|羹|卷|酥|冻|干|馍|火烧|豆腐|豆花|奶茶|茶|酒))',
        r'([\u4e00-\u9fff]{2,4}火烧)',  # 特殊：驴火等
        r'([\u4e00-\u9fff]{2,4}火锅)',
    ]

    exclude = {'东西', '午饭', '晚饭', '早餐', '早饭', '晚餐', '午餐', '点心',
               '零食', '美食', '饭菜', '很多酒', '点啤酒', '这么多酒', '一顿羊肉',
               '一顿椰子鸡', '一顿饭'}

    for pattern in patterns:
        matches = re.findall(pattern, body)
        for m in matches:
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


def assign_trip_tag(date: str, title: str, body: str) -> str:
    """分配 trip_tag"""
    # 先从标题判断
    if '北上之旅' in title or '北上之旅' in body[:500]:
        return '2024北上之旅'
    if '带老爸' in title or '带老爹' in title or '带倔强' in title:
        return '2025-2026带父南下'
    if '南下' in title:
        return '2022南下之旅'

    # 按日期范围判断
    for route in TRIP_ROUTES:
        if route['start'] <= date <= route['end']:
            return route['tag']

    return ''


def is_beijing_travel(title: str, body: str) -> bool:
    """判断北京文章是否为旅行内容"""
    travel_signals = ['Citywalk', 'citywalk', '自驾', '周边', '冰场', '沙滩',
                     '古镇', '景区', '公园', '胡同', '博物馆', '老街']
    for s in travel_signals:
        if s in title or s in body[:500]:
            return True
    return False


def main():
    # 加载旅行文章
    files = []
    with open(TRAVEL_LIST, 'r') as f:
        for line in f:
            line = line.strip()
            if line and Path(line).exists():
                files.append(line)

    print(f"加载 {len(files)} 篇旅行文章")

    # 按地点分组
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

        # 跳过 2022 年前的
        if date < '2022-01-01':
            continue

        # 北京文章过滤
        if region == '北京' and not is_beijing_travel(title, body):
            continue

        # 匹配地点
        place = match_place(title, region)
        if not place:
            continue

        # 提取数据
        excerpt = extract_excerpt_v2(body)
        snacks = extract_snacks_v2(body)
        trip_tag = assign_trip_tag(date, title, body)

        # 按地点分组
        key = f"{place['province']}_{place['place_name']}"
        place_groups[key].append({
            'province': place['province'],
            'city': place['city'],
            'place_name': place['place_name'],
            'search_term': place['search_term'],
            'full_name': f"{place['province']}·{place['place_name']}",
            'region': region,
            'visit_date': f"{date[:4]}年{int(date[5:7])}月" if date else '',
            'trip_tag': trip_tag,
            'excerpt': excerpt,
            'snacks': snacks,
            'source_title': title,
            'source_date': date,
            'body_len': len(body),
        })

    # 合并同一地点的多篇文章
    rows = []
    counter = 1

    for key, articles in place_groups.items():
        # 选 excerpt 最长的作为主条目
        best = max(articles, key=lambda a: len(a.get('excerpt', '')))

        # 合并 snacks
        all_snacks = []
        seen = set()
        for a in articles:
            for s in a.get('snacks', []):
                if s not in seen:
                    seen.add(s)
                    all_snacks.append(s)

        # 合并 trip_tag（取第一个非空的）
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

        row = {
            'id': f'HY{counter:03d}',
            'province': best['province'],
            'city': best['city'],
            'place_name': best['place_name'],
            'full_name': best['full_name'],
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
            'featured': 'false',
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

    out_path = '/tmp/heye-prompts/heye_locations_v2.csv'
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    # 统计
    provinces = set(r['province'] for r in rows)
    tags = Counter(r['trip_tag'] for r in rows if r['trip_tag'])
    empty_exc = sum(1 for r in rows if not r.get('excerpt', '').strip())
    empty_snacks = sum(1 for r in rows if r.get('snacks', '[]') == '[]')

    print(f"\n✅ 精提取完成！")
    print(f"   地点数: {len(rows)}")
    print(f"   覆盖省份: {len(provinces)} — {', '.join(sorted(provinces))}")
    print(f"   空 excerpt: {empty_exc}/{len(rows)}")
    print(f"   空 snacks: {empty_snacks}/{len(rows)}")
    print(f"\n   出行标签:")
    for t, c in tags.most_common():
        print(f"     {t}: {c} 个地点")
    print(f"\n   输出: {out_path}")


if __name__ == '__main__':
    main()
