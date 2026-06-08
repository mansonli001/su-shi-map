#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作品补充系统 - 从《苏轼行踪考》提取苏轼诗词作品
"""
import json
import os
import re

# 配置
SOURCE_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4-source/行踪考-简体'
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
V4_INDEX_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'

# 已知苏轼作品标题（用于过滤）
KNOWN_WORKS = {
    '赤壁赋', '前赤壁赋', '后赤壁赋', '念奴娇·赤壁怀古', '水调歌头',
    '江城子·密州出猎', '江城子·乙卯正月二十日夜记梦', '定风波',
    '浣溪沙', '蝶恋花', '题西林壁', '饮湖上初晴后雨', '惠崇春江晚景',
    '赠刘景文', '海棠', '六月二十七日望湖楼醉书', '记承天寺夜游',
    '黄州寒食帖', '食荔枝', '惠州一绝', '题西林壁', '江城子',
    '满江红', '西江月', '卜算子·黄州定慧院寓居作', '临江仙',
    '南乡子', '望江南', '昭君怨', '虞美人', '鹧鸪天',
    '踏莎行', '青玉案', '千秋岁', '醉翁操', '哨遍',
    '水龙吟', '满庭芳', '八声甘州', '桂枝香', '洞仙歌',
    '永遇乐', '贺新郎', '摸鱼儿', '沁园春', '声声慢',
    '清平乐', '鹊桥仙', '减字木兰花', '菩萨蛮', '相见欢',
    '如梦令', '采桑子', '诉衷情', '阮郎归', '画堂春',
    '武陵春', '长相思', '浣溪沙', '点绛唇', '霜天晓角',
    '小重山', '临江仙', '鹧鸪天', '虞美人', '南歌子',
    '踏莎行', '蝶恋花', '渔家傲', '苏幕遮', '御街行',
    '菩萨蛮', '浣溪沙', '清平乐', '木兰花', '千秋岁引',
    '雨霖铃', '望海潮', '八声甘州', '风流子', '木兰花慢',
    '水龙吟', '齐天乐', '庆春宫', '西平乐', '曲玉管',
    '渡江云', '解连环', '望梅', '暗香', '疏影',
    '长亭怨慢', '莺啼序', '高阳台', '声声慢', '汉宫春',
    '一萼红', '宴山亭', '念奴娇', '绕佛阁', '渡江云',
    '琵琶仙', '八归', '石湖仙', '暗香', '疏影',
    '惜黄花慢', '眉妩', '齐天乐', '湘江静', '法曲献仙音',
    '大酺', '花犯', '瑞鹤仙', '齐天乐', '永遇乐',
    '绮罗香', '南浦', '声声慢', '尉迟杯', '渡江云',
    '解语花', '解连环', '夜合花', '拜星月慢', '水龙吟',
    '西河', '望远行', '法曲第二', '玉蝴蝶', '八声甘州',
    '满江红', '玉楼春', '蝶恋花', '清平乐', '临江仙',
    '鹧鸪天', '虞美人', '南歌子', '踏莎行', '浣溪沙',
    '菩萨蛮', '木兰花', '千秋岁', '醉翁操', '哨遍',
    '水龙吟', '满庭芳', '八声甘州', '桂枝香', '洞仙歌',
    '永遇乐', '贺新郎', '摸鱼儿', '沁园春', '声声慢',
}

def read_chapter(filepath):
    """读取章节内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_works(text):
    """从文本中提取作品信息"""
    works = []
    
    # 模式1："苏轼《作品名》"
    pattern1 = re.compile(r'苏轼[《「]([^》」]+)[》」]')
    for match in pattern1.findall(text):
        title = match.strip()
        if title and len(title) > 2 and len(title) < 50:
            works.append(title)
    
    # 模式2："作《作品名》"
    pattern2 = re.compile(r'[作写赋][《「]([^》」]+)[》」]')
    for match in pattern2.findall(text):
        title = match.strip()
        if title and len(title) > 2 and len(title) < 50:
            works.append(title)
    
    # 模式3："《作品名》" 单独出现（上下文有苏轼）
    pattern3 = re.compile(r'[《「]([^》」]+)[》」]')
    for match in pattern3.findall(text):
        title = match.strip()
        if title in KNOWN_WORKS:
            works.append(title)
    
    # 去重并过滤
    filtered = []
    for work in list(set(works)):
        # 过滤掉明显不是作品的内容
        if len(work) < 2:
            continue
        if any(keyword in work for keyword in ['图', '表', '注', '卷', '篇', '章', '书', '传']):
            continue
        filtered.append(work)
    
    return filtered

def batch_extract_works():
    """批量提取所有章节的作品"""
    chapter_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    all_works = {}
    
    for filename in chapter_files:
        if filename.startswith('02_') or filename.startswith('03_') or filename.startswith('04_'):
            continue
        
        filepath = os.path.join(SOURCE_DIR, filename)
        text = read_chapter(filepath)
        works = extract_works(text)
        
        if works:
            chapter_name = filename.replace('.md', '').replace('_', ' ')
            all_works[chapter_name] = works
            print(f"📄 {filename}: 提取到 {len(works)} 篇作品")
    
    return all_works

def update_works():
    """更新v4地点的作品信息"""
    # 加载v4索引
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        v4_index = json.load(f)
    
    # 提取所有作品
    all_works = batch_extract_works()
    
    updated_count = 0
    total_added = 0
    
    for place in v4_index['places']:
        place_id = place['id']
        ancient_name = place['ancient_name']
        modern_name = place['modern_name']
        place_file = os.path.join(OUTPUT_DIR, f"{place_id}.json")
        
        if not os.path.exists(place_file):
            continue
        
        # 查找匹配的作品
        matched_works = []
        for chapter, works in all_works.items():
            # 检查章节是否与地点相关
            if ancient_name in chapter or any(keyword in chapter for keyword in ancient_name.split()):
                matched_works.extend(works)
        
        if matched_works:
            # 读取地点文件
            with open(place_file, 'r', encoding='utf-8') as f:
                place_data = json.load(f)
            
            # 获取已有的作品标题
            existing_titles = {w.get('title', '') for w in place_data.get('global_works', [])}
            
            # 添加新作品
            added_count = 0
            for work_title in matched_works[:10]:  # 最多添加10篇
                if work_title not in existing_titles:
                    place_data.setdefault('global_works', []).append({
                        'id': f"{place_id}-work-{len(place_data['global_works'])+1}",
                        'title': work_title,
                        'content': '',
                        'excerpt': '',
                        'type': '词' if '·' in work_title or '子' in work_title[-1] else '诗',
                        'date': '',
                        'location': ancient_name,
                        'background': '',
                        'fullText': '',
                        'coreVerse': '',
                        'poem_id': f"S{len(place_data['global_works'])+1:03d}"
                    })
                    added_count += 1
                    existing_titles.add(work_title)
            
            if added_count > 0:
                # 保存更新
                with open(place_file, 'w', encoding='utf-8') as f:
                    json.dump(place_data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
                total_added += added_count
                print(f"✅ {place_id}: {ancient_name} - 添加 {added_count} 篇作品")
    
    print(f"\n📊 作品补充完成")
    print(f"   更新地点: {updated_count} 个")
    print(f"   添加作品: {total_added} 篇")
    
    return updated_count, total_added

def main():
    print("="*60)
    print("作品补充系统 - 从《苏轼行踪考》提取诗词")
    print("="*60)
    
    print("\n【1】开始提取作品...")
    all_works = batch_extract_works()
    
    total_works = sum(len(works) for works in all_works.values())
    print(f"\n【2】共提取到 {total_works} 篇作品")
    
    print("\n【3】开始更新地点作品...")
    update_works()
    
    print("\n✅ 作品补充完成！")

if __name__ == "__main__":
    main()
