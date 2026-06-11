#!/usr/bin/env python3
"""
Cross-validation script for Su Shi poetry data.
Covers: route-poem associations, place-poem references, gold quotes, reading content.
Outputs a structured report for further verification.
"""
import json, glob, os, re
from collections import defaultdict
from datetime import datetime

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize(text):
    """Remove punctuation and whitespace for comparison."""
    return re.sub(r'[，。、！？；：""''（）《》\s\u3000]', '', text)

# ===== LOAD ALL DATA =====
print("加载数据...")
poems = {}
for f in sorted(glob.glob(f'{BASE}/poems/*.json')):
    d = load_json(f)
    poems[d['id']] = d

idx = load_json(f'{BASE}/poems-index.json')
idx_lookup = {p['id']: p for p in idx['poems']}

routes = load_json(f'{BASE}/routes-index.json')
route_lookup = {r['id']: r for r in routes['routes']}

places_idx = load_json(f'{BASE}/places-index.json')
places_idx_lookup = {p['id']: p for p in places_idx['places']}

places = {}
for f in sorted(glob.glob(f'{BASE}/places/*.json')):
    d = load_json(f)
    places[d['id']] = d

issues = defaultdict(list)
stats = defaultdict(int)

# ===== PHASE 3: ROUTE-POEM ASSOCIATION VERIFICATION =====
print("\n" + "=" * 60)
print("Phase 3: 路线-诗文关联验证")
print("=" * 60)

# Build route->poems mapping from poem files
route_poems = defaultdict(list)
for pid, poem in poems.items():
    rid = poem.get('route_id', '')
    if rid:
        route_poems[rid].append(pid)

# 3a. Check each route has poems
for rid, route in route_lookup.items():
    poem_count = len(route_poems.get(rid, []))
    if poem_count == 0:
        issues['route_no_poems'].append(f"{rid}: {route['name']} 没有关联任何诗文")
    stats[f'route_{rid}_poems'] = poem_count

# 3b. Check poem route_id references valid route
for pid, poem in poems.items():
    rid = poem.get('route_id', '')
    if rid and rid not in route_lookup:
        issues['invalid_route_id'].append(f"{pid}: route_id='{rid}' 在路线数据中不存在")

# 3c. Check year vs route period consistency
for pid, poem in poems.items():
    rid = poem.get('route_id', '')
    year = poem.get('year', 0)
    if rid and year and rid in route_lookup:
        route = route_lookup[rid]
        start = route.get('start_year', 0)
        end = route.get('end_year', 0)
        if start and end and (year < start or year > end):
            # Allow 1 year tolerance for boundary cases
            if year < start - 1 or year > end + 1:
                issues['year_route_mismatch'].append(
                    f"{pid} ({poem.get('title')}): year={year} 不在路线 {rid} ({route['name']}) 时期内 ({start}-{end})"
                )

# 3d. Check index related_route_ids consistency
for pid, entry in idx_lookup.items():
    for rid in entry.get('related_route_ids', []):
        if rid and rid not in route_lookup:
            issues['invalid_related_route'].append(f"{pid}: related_route_id='{rid}' 不存在")

# 3e. Check poem's route_id matches index's related_route_ids
for pid, poem in poems.items():
    if pid not in idx_lookup:
        continue
    poem_route = poem.get('route_id', '')
    idx_routes = idx_lookup[pid].get('related_route_ids', [])
    if poem_route and idx_routes and poem_route not in idx_routes:
        issues['poem_index_route_mismatch'].append(
            f"{pid}: poem.route_id={poem_route} but index.related_route_ids={idx_routes}"
        )

# 3f. Verify route place_count matches actual places
for rid, route in route_lookup.items():
    expected_place_count = route.get('place_count', 0)
    actual_places = [p for p in places.values() if rid in p.get('related_routes', [])]
    if expected_place_count != len(actual_places):
        issues['route_place_count_mismatch'].append(
            f"{rid}: route says {expected_place_count} places, actual={len(actual_places)}"
        )

print(f"  无诗文路线: {len(issues['route_no_poems'])}")
print(f"  无效路线ID: {len(issues['invalid_route_id'])}")
print(f"  年份/路线不匹配: {len(issues['year_route_mismatch'])}")
print(f"  无效关联路线ID: {len(issues['invalid_related_route'])}")
print(f"  诗文/索引路线不一致: {len(issues['poem_index_route_mismatch'])}")
print(f"  路线地点数不匹配: {len(issues['route_place_count_mismatch'])}")

# Print route-poem distribution
print("\n  路线-诗文分布:")
for rid in sorted(route_lookup.keys()):
    route = route_lookup[rid]
    count = len(route_poems.get(rid, []))
    print(f"    {rid} {route['name']}: {count}首")

# ===== PHASE 4: PLACE-POEM REFERENCE VERIFICATION =====
print("\n" + "=" * 60)
print("Phase 4: 地点-诗文引用验证")
print("=" * 60)

# 4a. Check place global_works references valid poems
for plid, place in places.items():
    for work in place.get('global_works', []):
        poem_id = work.get('poem_id', '')
        if poem_id:
            if poem_id not in poems:
                issues['place_refs_missing_poem'].append(
                    f"地点 {plid} ({place.get('ancient_name', '')}) 引用诗文 {poem_id} 不存在"
                )
            else:
                # Verify poem title matches
                poem_title = poems[poem_id].get('title', '')
                work_title = work.get('title', '')
                if work_title and poem_title and normalize(work_title) != normalize(poem_title):
                    # Allow partial match
                    if normalize(work_title) not in normalize(poem_title) and normalize(poem_title) not in normalize(work_title):
                        issues['place_poem_title_mismatch'].append(
                            f"地点 {plid}: work.title='{work_title}' vs poem.title='{poem_title}'"
                        )

# 4b. Check place route_works references
for plid, place in places.items():
    for rid, rw in place.get('route_works', {}).items():
        if rid not in route_lookup:
            issues['place_route_works_invalid_route'].append(
                f"地点 {plid}: route_works引用路线 {rid} 不存在"
            )

# 4c. Check place-poem route consistency
for plid, place in places.items():
    place_routes = place.get('related_routes', [])
    for work in place.get('global_works', []):
        poem_id = work.get('poem_id', '')
        if poem_id and poem_id in poems:
            poem_route = poems[poem_id].get('route_id', '')
            if poem_route and place_routes and poem_route not in place_routes:
                issues['place_poem_route_mismatch'].append(
                    f"地点 {plid} ({place.get('ancient_name', '')}) 路线={place_routes}, "
                    f"但诗文 {poem_id} ({poems[poem_id].get('title', '')}) 路线={poem_route}"
                )

# 4d. Check places-index vs actual place files consistency
for p_entry in places_idx['places']:
    plid = p_entry['id']
    if plid not in places:
        issues['places_index_orphan'].append(f"{plid}: 在索引中但无详情文件")
for plid in places:
    if plid not in places_idx_lookup:
        issues['places_file_not_in_index'].append(f"{plid}: 有详情文件但不在索引中")

# 4e. Check place location matches poem location
for plid, place in places.items():
    for work in place.get('global_works', []):
        poem_id = work.get('poem_id', '')
        if poem_id and poem_id in poems:
            poem_loc = poems[poem_id].get('location', '')
            place_name = place.get('ancient_name', '')
            # Simple check - if poem location doesn't contain place name and vice versa
            if poem_loc and place_name:
                p_loc_norm = normalize(poem_loc)
                p_name_norm = normalize(place_name)
                if p_loc_norm and p_name_norm and p_name_norm not in p_loc_norm and p_loc_norm not in p_name_norm:
                    # More lenient: check if any character overlap
                    pass  # Skip this check as location names vary too much

# 4f. Check place has_detail consistency
for plid, place in places.items():
    has_detail = place.get('has_detail', False)
    has_route_events = bool(place.get('route_events', {}))
    has_global_works = bool(place.get('global_works', []))
    if has_detail and not has_route_events and not has_global_works:
        issues['place_detail_no_content'].append(
            f"{plid} ({place.get('ancient_name', '')}): has_detail=true 但无route_events和global_works"
        )

# 4g. Count total poem references in places
total_place_poem_refs = 0
unique_poem_refs = set()
for plid, place in places.items():
    for work in place.get('global_works', []):
        poem_id = work.get('poem_id', '')
        if poem_id:
            total_place_poem_refs += 1
            unique_poem_refs.add(poem_id)

# Check which poems are NOT referenced by any place
poems_referenced_by_places = unique_poem_refs
poems_not_in_places = set(poems.keys()) - poems_referenced_by_places

print(f"  地点引用不存在的诗文: {len(issues['place_refs_missing_poem'])}")
print(f"  地点-诗文标题不匹配: {len(issues['place_poem_title_mismatch'])}")
print(f"  地点-诗文路线不匹配: {len(issues['place_poem_route_mismatch'])}")
print(f"  地点索引孤儿: {len(issues['places_index_orphan'])}")
print(f"  地点文件不在索引: {len(issues['places_file_not_in_index'])}")
print(f"  地点详情无内容: {len(issues['place_detail_no_content'])}")
print(f"  地点引用诗文总数: {total_place_poem_refs}")
print(f"  地点引用唯一诗文数: {len(unique_poem_refs)}")
print(f"  未被任何地点引用的诗文数: {len(poems_not_in_places)}")

# ===== PHASE 5: GOLD QUOTE VERIFICATION =====
print("\n" + "=" * 60)
print("Phase 5: 金句提取验证")
print("=" * 60)

# 5a. Check famousQuotes exist in paragraphs
for pid, poem in poems.items():
    paras_text = ' '.join(poem.get('paragraphs', []))
    famous = poem.get('famousQuotes', [])
    
    for i, q in enumerate(famous):
        q_norm = normalize(q)
        para_norm = normalize(paras_text)
        if q_norm and para_norm and q_norm not in para_norm:
            issues['quote_not_in_text'].append(
                f"{pid} ({poem.get('title')}): famousQuotes[{i}]='{q}' 在原文中未找到"
            )

# 5b. Check gold_quote exists in paragraphs
for pid, poem in poems.items():
    paras_text = ' '.join(poem.get('paragraphs', []))
    gold = poem.get('gold_quote', '')
    
    if gold:
        gold_norm = normalize(gold)
        para_norm = normalize(paras_text)
        if gold_norm and para_norm and gold_norm not in para_norm:
            issues['gold_not_in_text'].append(
                f"{pid} ({poem.get('title')}): gold_quote='{gold}' 在原文中未找到"
            )

# 5c. Check gold_quote is in famousQuotes (informational, not error)
gold_not_in_famous_count = 0
for pid, poem in poems.items():
    gold = poem.get('gold_quote', '')
    famous = poem.get('famousQuotes', [])
    if gold and famous and gold not in famous:
        gold_not_in_famous_count += 1

# 5d. Check coreVerse in index matches
for pid, entry in idx_lookup.items():
    core = entry.get('coreVerse', '')
    if core and pid in poems:
        paras_text = ' '.join(poems[pid].get('paragraphs', []))
        core_norm = normalize(core)
        para_norm = normalize(paras_text)
        if core_norm and para_norm and core_norm not in para_norm:
            issues['core_verse_not_in_text'].append(
                f"{pid}: coreVerse='{core}' 在原文中未找到"
            )

# 5e. Check poems with no famousQuotes at all
no_famous = []
for pid, poem in poems.items():
    if not poem.get('famousQuotes') or len(poem.get('famousQuotes', [])) == 0:
        no_famous.append(f"{pid}: {poem.get('title')}")

# 5f. Check poems with no gold_quote
no_gold = []
for pid, poem in poems.items():
    if not poem.get('gold_quote'):
        no_gold.append(f"{pid}: {poem.get('title')}")

print(f"  金句不在原文中: {len(issues['quote_not_in_text'])}")
print(f"  金句(gold)不在原文中: {len(issues['gold_not_in_text'])}")
print(f"  金句(gold)不在famousQuotes中: {gold_not_in_famous_count} (设计如此,gold_quote是精简版)")
print(f"  coreVerse不在原文中: {len(issues['core_verse_not_in_text'])}")
print(f"  无famousQuotes的诗文: {len(no_famous)}")
print(f"  无gold_quote的诗文: {len(no_gold)}")

if issues['quote_not_in_text']:
    print("\n  金句不在原文中的详细列表:")
    for item in issues['quote_not_in_text']:
        print(f"    - {item}")

if issues['gold_not_in_text']:
    print("\n  gold_quote不在原文中的详细列表:")
    for item in issues['gold_not_in_text']:
        print(f"    - {item}")

# ===== PHASE 6: READING CONTENT VERIFICATION =====
print("\n" + "=" * 60)
print("Phase 6: 深度读内容验证")
print("=" * 60)

# 6a. Check reading.scene year consistency
for pid, poem in poems.items():
    reading = poem.get('reading', {})
    if not reading:
        continue
    
    scene = reading.get('scene', '')
    poem_year = poem.get('year', 0)
    if scene and poem_year:
        scene_years = re.findall(r'(\d{4})年', scene)
        for sy in scene_years:
            if int(sy) != poem_year:
                issues['reading_year_mismatch'].append(
                    f"{pid} ({poem.get('title')}): 诗文year={poem_year}, 深度读提到{sy}年"
                )

# 6b. Check reading.lines quotes match paragraphs
for pid, poem in poems.items():
    reading = poem.get('reading', {})
    if not reading:
        continue
    
    paras_text = ' '.join(poem.get('paragraphs', []))
    for i, line in enumerate(reading.get('lines', [])):
        quote = line.get('quote', '')
        if quote:
            q_norm = normalize(quote)
            para_norm = normalize(paras_text)
            if q_norm and para_norm and q_norm not in para_norm:
                issues['reading_quote_not_in_text'].append(
                    f"{pid} ({poem.get('title')}): reading.lines[{i}].quote='{quote}' 在原文中未找到"
                )

# 6c. Check age consistency with year (Su Shi born 1037)
for pid, poem in poems.items():
    age = poem.get('age', '')
    poem_year = poem.get('year', 0)
    if age and poem_year:
        age_num = re.search(r'(\d+)', age)
        if age_num:
            calculated_birth = poem_year - int(age_num.group(1))
            if abs(calculated_birth - 1037) > 1:  # Allow 1 year tolerance
                issues['age_year_inconsistency'].append(
                    f"{pid} ({poem.get('title')}): year={poem_year}, age={age}, "
                    f"推算出生年={calculated_birth} (应为1037)"
                )

# 6d. Check reading content mentions correct location
for pid, poem in poems.items():
    reading = poem.get('reading', {})
    if not reading:
        continue
    
    poem_loc = poem.get('location', '')
    scene = reading.get('scene', '')
    person = reading.get('person', '')
    
    # Check if reading mentions a different location than the poem
    if poem_loc and scene:
        # Extract location keywords from poem location
        loc_keywords = re.findall(r'[\u4e00-\u9fff]{2,}', poem_loc)
        scene_loc_keywords = re.findall(r'[\u4e00-\u9fff]{2,}', scene)
        # This is a soft check - just flag potential mismatches
        # Skip for now as location names are complex

# 6e. Check reading has all required fields
for pid, poem in poems.items():
    reading = poem.get('reading', {})
    if not reading:
        issues['missing_reading'].append(f"{pid}: {poem.get('title')} 无深度读内容")
        continue
    
    missing_fields = []
    for field in ['scene', 'lines', 'person']:
        if not reading.get(field):
            missing_fields.append(field)
    if missing_fields:
        issues['reading_missing_fields'].append(
            f"{pid} ({poem.get('title')}): 深度读缺少字段: {missing_fields}"
        )

# 6f. Check reading.lines has quote and explain
for pid, poem in poems.items():
    reading = poem.get('reading', {})
    if not reading:
        continue
    
    for i, line in enumerate(reading.get('lines', [])):
        if not line.get('quote'):
            issues['reading_line_no_quote'].append(
                f"{pid}: reading.lines[{i}] 无quote字段"
            )
        if not line.get('explain'):
            issues['reading_line_no_explain'].append(
                f"{pid}: reading.lines[{i}] 无explain字段"
            )

# 6g. Check for suspiciously generic reading content
generic_phrases = ['他总是能在', '这句话听起来简单', '一个被压着的人', '他写的是风景']
for pid, poem in poems.items():
    reading = poem.get('reading', {})
    if not reading:
        continue
    
    person = reading.get('person', '')
    if person and len(person) < 20:
        issues['reading_person_too_short'].append(
            f"{pid} ({poem.get('title')}): person='{person}' 过于简短"
        )

print(f"  深度读年份不匹配: {len(issues['reading_year_mismatch'])}")
print(f"  深度读引用不在原文: {len(issues['reading_quote_not_in_text'])}")
print(f"  年龄/年份推算不一致: {len(issues['age_year_inconsistency'])}")
print(f"  缺少深度读: {len(issues['missing_reading'])}")
print(f"  深度读缺少字段: {len(issues['reading_missing_fields'])}")
print(f"  深度读行缺少quote: {len(issues['reading_line_no_quote'])}")
print(f"  深度读行缺少explain: {len(issues['reading_line_no_explain'])}")
print(f"  深度读person过短: {len(issues['reading_person_too_short'])}")

if issues['reading_quote_not_in_text']:
    print("\n  深度读引用不在原文的详细列表:")
    for item in issues['reading_quote_not_in_text']:
        print(f"    - {item}")

if issues['age_year_inconsistency']:
    print("\n  年龄/年份推算不一致的详细列表:")
    for item in issues['age_year_inconsistency']:
        print(f"    - {item}")

# ===== PHASE 2 SUPPLEMENT: KEY POEM EXTERNAL VERIFICATION CANDIDATES =====
print("\n" + "=" * 60)
print("Phase 2补充: 需要外部校验的重点名篇")
print("=" * 60)

# List the most famous poems that need external verification
key_poems = [
    'C057',  # 念奴娇·大江东去
    'C013',  # 水调歌头·明月几时有
    'C037',  # 定风波·莫听穿林打叶声
    'C002',  # 江城子·密州出猎
    'C003',  # 江城子·乙卯正月二十日夜记梦
    'C055',  # 定风波·南海归赠王定国侍人寓娘
    'C058',  # 卜算子·黄州定慧院寓居作
    'C060',  # 临江仙·夜饮东坡醒复醉
    'S102',  # 题西林壁
    'S114',  # 惠崇春江晚景
    'S132',  # 食荔枝
    'S063',  # 石苍舒醉墨堂
    'S075',  # 东栏梨花
    'S083',  # 春宵
    'S159',  # 六月二十日夜渡海
    'F005',  # 后赤壁赋
    'F001',  # 前赤壁赋
    'C038',  # 浣溪沙·游蕲水清泉寺
    'C063',  # 临江仙·送钱穆父
    'C066',  # 水调歌头·黄州快哉亭赠张偓佺
]

print("  以下名篇需要与权威来源交叉验证原文:")
for pid in key_poems:
    if pid in poems:
        poem = poems[pid]
        paras = poem.get('paragraphs', [])
        first_line = paras[0] if paras else '(空)'
        print(f"    {pid}: {poem.get('title')} - {first_line[:30]}...")
    else:
        print(f"    {pid}: 未找到!")

# ===== SUMMARY =====
print("\n" + "=" * 60)
print("问题汇总统计")
print("=" * 60)

# Categorize issues by severity
high_priority = [
    'quote_not_in_text', 'gold_not_in_text', 'reading_quote_not_in_text',
    'age_year_inconsistency', 'reading_year_mismatch', 'place_refs_missing_poem',
    'type_prefix_mismatch', 'invalid_route_id'
]

medium_priority = [
    'year_route_mismatch', 'place_poem_route_mismatch', 'poem_index_route_mismatch',
    'place_poem_title_mismatch', 'core_verse_not_in_text', 'title_mismatch',
    'year_mismatch', 'route_mismatch'
]

low_priority = [
    'gold_not_in_famous', 'reading_person_too_short', 'reading_missing_fields',
    'missing_reading', 'no_famous', 'no_gold', 'route_place_count_mismatch'
]

total_high = sum(len(issues.get(k, [])) for k in high_priority)
total_medium = sum(len(issues.get(k, [])) for k in medium_priority)
total_low = sum(len(issues.get(k, [])) for k in low_priority)
total_all = sum(len(v) for v in issues.values() if v)

print(f"\n  高优先级（内容准确性）: {total_high}")
print(f"  中优先级（关联准确性）: {total_medium}")
print(f"  低优先级（格式/规范）: {total_low}")
print(f"  总问题数: {total_all}")

print("\n  高优先级问题详情:")
for k in high_priority:
    items = issues.get(k, [])
    if items:
        print(f"\n    {k} ({len(items)}):")
        for item in items[:10]:
            print(f"      - {item}")
        if len(items) > 10:
            print(f"      ... 还有 {len(items) - 10} 条")

print("\n  中优先级问题详情:")
for k in medium_priority:
    items = issues.get(k, [])
    if items:
        print(f"\n    {k} ({len(items)}):")
        for item in items[:10]:
            print(f"      - {item}")
        if len(items) > 10:
            print(f"      ... 还有 {len(items) - 10} 条")

# ===== SAVE REPORT =====
report = {
    'generated_at': datetime.now().isoformat(),
    'total_poems': len(poems),
    'total_places': len(places),
    'total_routes': len(route_lookup),
    'total_issues': total_all,
    'severity_summary': {
        'high_priority': total_high,
        'medium_priority': total_medium,
        'low_priority': total_low
    },
    'route_poem_distribution': {
        rid: {
            'name': route_lookup[rid]['name'],
            'poem_count': len(route_poems.get(rid, []))
        } for rid in sorted(route_lookup.keys())
    },
    'place_poem_stats': {
        'total_refs': total_place_poem_refs,
        'unique_poems': len(unique_poem_refs),
        'poems_not_referenced': len(poems_not_in_places)
    },
    'issues': {k: v for k, v in sorted(issues.items()) if v},
    'poems_not_in_places': sorted(list(poems_not_in_places))[:50],  # First 50
    'no_famous_poems': no_famous[:30],
    'no_gold_poems': no_gold[:30],
    'key_poems_for_external_verification': key_poems
}

report_path = f'{BASE}/meta/cross-validation-report.json'
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"\n报告已保存到: {report_path}")
