#!/usr/bin/env python3
"""
筛选贺野旅行文章
规则：
1. 2022年1月以后
2. 地区标签不是"北京"的，优先级最高（明确在外地发布）
3. 地区标签是"北京"但标题含旅行关键词的
4. 排除明显非旅行文章（看病、住院、小说、转载等）
"""

import json
import re
import sys
from pathlib import Path

# 旅行关键词
TRAVEL_KEYWORDS = [
    '旅行', '自驾', '旅途', '出行', '出差', '游学',
    '古镇', '古城', '山水', '草原', '海岛', '沙漠',
    '武夷山', '九华山', '黄山', '泰山', '华山',
    '平遥', '开封', '扬州', '苏州', '杭州', '宁波',
    '厦门', '鼓浪屿', '潮州', '福州', '泉州',
    '保定', '石家庄', '太原', '合肥', '蚌埠',
    '舟山', '嵊泗', '朱家尖', '甪直', '同里', '黎里',
    '查济', '三河', '白洋淀', '晋阳湖',
    '平潭', '霞浦', '南靖', '土楼',
    '北上之旅', '南下', '福建行', '西北',
    '西藏', '新疆', '云南', '海南', '广西',
    '哈尔滨', '阿尔山', '呼伦贝尔', '满洲里',
    '青海', '甘肃', '宁夏', '陕西',
    '柳州', '赣州', '佛山', '广州',
    '澳门', '游轮', '三亚',
    '景德镇', '永州', '蚌埠', '眉州',
    '雅鲁藏布', '日喀则', '红河', '梯田',
    '沈阳', '西塔',
]

# 排除关键词
EXCLUDE_KEYWORDS = [
    '看病', '住院', '手术', '体检', '医保', '药', '甲钴胺',
    '小说', '魔方世界', '转载', '「转」',
    '抑郁', '焦虑', '失眠',
    '手机', '护眼灯', '打印机', '保健品',
    '春节', '过年', '除夕', '元宵',  # 除非明确旅行
    '回忆', '往事', '记忆',  # 除非明确旅行
    '孩子', '儿子', '小学', '作业', '考试',  # 除非明确旅行
    '失业', '公司', '工作',  # 除非明确旅行
]


def is_travel_article(prompt_data: dict) -> tuple[bool, str]:
    """判断是否为旅行文章，返回 (是否旅行, 原因)"""
    title = prompt_data.get('title', '')
    region = prompt_data.get('region', '')
    date = prompt_data.get('date', '')
    body = prompt_data.get('body', '')[:2000]  # 只看前2000字

    # 排除明显非旅行
    for kw in EXCLUDE_KEYWORDS:
        if kw in title:
            return False, f'排除关键词: {kw}'

    # 地区标签不是北京 → 很可能旅行
    if region and region != '北京':
        # 但需要排除一些非旅行的外地发布
        for kw in EXCLUDE_KEYWORDS:
            if kw in body[:500]:
                return False, f'外地发布但排除关键词: {kw}'
        return True, f'地区标签: {region}'

    # 标题含旅行关键词
    for kw in TRAVEL_KEYWORDS:
        if kw in title:
            return True, f'标题关键词: {kw}'

    # 正文前500字含旅行线索
    travel_signals = ['到了', '去了', '来到', '抵达', '出发', '开车到', '自驾到', '坐车到']
    place_signals = ['景区', '门票', '景点', '古镇', '古城墙', '竹筏', '漂流']
    has_travel = any(s in body[:500] for s in travel_signals)
    has_place = any(s in body[:500] for s in place_signals)
    if has_travel and has_place:
        return True, '正文含旅行+地点信号'

    return False, '无旅行信号'


def main():
    prompts_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/heye-prompts')

    # 只看2022年1月以后的
    files = sorted(prompts_dir.glob('*_prompt.json'))

    travel_articles = []
    non_travel = []

    for f in files:
        # 从文件名提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
        if not date_match:
            continue
        date_str = date_match.group(1)
        year = int(date_str[:4])

        # 只看2022年及以后
        if year < 2022:
            continue

        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except:
            continue

        is_travel, reason = is_travel_article(data)

        if is_travel:
            travel_articles.append({
                'file': f.name,
                'date': date_str,
                'title': data.get('title', ''),
                'region': data.get('region', ''),
                'reason': reason,
            })
        else:
            non_travel.append({
                'file': f.name,
                'date': date_str,
                'title': data.get('title', ''),
                'region': data.get('region', ''),
                'reason': reason,
            })

    # 输出旅行文章列表
    print(f"=== 旅行文章: {len(travel_articles)} 篇 ===\n")

    # 按时间分组
    current_month = ''
    for a in travel_articles:
        month = a['date'][:7]
        if month != current_month:
            current_month = month
            print(f"\n--- {month} ---")
        print(f"  {a['date']} | {a['region']:6s} | {a['title'][:40]}  ({a['reason']})")

    # 输出文件列表供后续处理
    list_file = prompts_dir / 'travel_articles.txt'
    with open(list_file, 'w', encoding='utf-8') as fh:
        for a in travel_articles:
            # 输出对应的 prompt 文件路径
            prompt_file = prompts_dir / a['file']
            fh.write(str(prompt_file) + '\n')

    print(f"\n旅行文章文件列表已保存至: {list_file}")

    # 统计
    print(f"\n=== 统计 ===")
    print(f"旅行文章: {len(travel_articles)} 篇")
    print(f"非旅行文章: {len(non_travel)} 篇")

    # 按地区统计
    regions = {}
    for a in travel_articles:
        r = a['region'] or '未知'
        regions[r] = regions.get(r, 0) + 1
    print(f"\n按地区:")
    for r, c in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {r}: {c} 篇")


if __name__ == '__main__':
    main()
