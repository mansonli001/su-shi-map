#!/usr/bin/env python3
"""
Comprehensive self-check script for Su Shi poetry data.
Checks: title/content, quotes, route/place associations, reading content.
Outputs a structured report for further verification.
"""
import json, glob, os, re
from collections import defaultdict

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4"

# Load all data
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load poems
poems = {}
for f in sorted(glob.glob(f'{BASE}/poems/*.json')):
    d = load_json(f)
    poems[d['id']] = d

# Load index
idx = load_json(f'{BASE}/poems-index.json')
idx_lookup = {p['id']: p for p in idx['poems']}

# Load routes
routes = load_json(f'{BASE}/routes-index.json')
route_lookup = {r['id']: r for r in routes['routes']}

# Load places
places_idx = load_json(f'{BASE}/places-index.json')
places = {}
for f in sorted(glob.glob(f'{BASE}/places/*.json')):
    d = load_json(f)
    places[d['id']] = d

# ===== CHECK RESULTS =====
issues = defaultdict(list)
stats = defaultdict(int)

print("=" * 60)
print("苏轼诗文数据全面自检报告")
print("=" * 60)

# ===== 1. TITLE & CONTENT CHECKS =====
print("\n## 1. 题目与内容自检")

for pid, poem in poems.items():
    # 1a. Empty paragraphs
    if not poem.get('paragraphs') or len(poem.get('paragraphs', [])) == 0:
        issues['empty_paragraphs'].append(f"{pid}: {poem.get('title', '?')}")
    
    # 1b. Title mismatch between poem file and index
    if pid in idx_lookup:
        if poem.get('title', '') != idx_lookup[pid].get('title', ''):
            issues['title_mismatch'].append(
                f"{pid}: file='{poem.get('title')}' vs index='{idx_lookup[pid].get('title')}'"
            )
    
    # 1c. Year mismatch between poem file and index
    if pid in idx_lookup:
        file_year = poem.get('year', 0)
        idx_year = idx_lookup[pid].get('year', 0)
        if file_year != idx_year and file_year != 0 and idx_year != 0:
            issues['year_mismatch'].append(
                f"{pid}: file={file_year} vs index={idx_year}"
            )
    
    # 1d. Route_id mismatch
    if pid in idx_lookup:
        file_route = poem.get('route_id', '')
        idx_route = idx_lookup[pid].get('route_id', '')
        if file_route and idx_route and file_route != idx_route:
            issues['route_mismatch'].append(
                f"{pid}: file={file_route} vs index={idx_route}"
            )
    
    # 1e. Missing required fields
    for field in ['title', 'author', 'type', 'year', 'location']:
        if not poem.get(field) and field != 'year':
            issues[f'missing_{field}'].append(f"{pid}: {poem.get('title', '?')}")
        elif field == 'year' and poem.get('year', 0) == 0:
            issues['missing_year'].append(f"{pid}: {poem.get('title', '?')}")
    
    # 1f. Type inconsistency (S-prefix should be 诗, C-prefix should be 词, etc.)
    prefix = pid[0]
    expected_type = {'S': '诗', 'C': '词', 'W': '文', 'F': '赋'}.get(prefix, None)
    if expected_type and poem.get('type') != expected_type:
        issues['type_prefix_mismatch'].append(
            f"{pid}: prefix={prefix} expects '{expected_type}', got '{poem.get('type')}'"
        )
    
    # 1g. Paragraphs contain suspiciously short content (likely incomplete)
    for i, para in enumerate(poem.get('paragraphs', [])):
        if len(para) < 4 and not para.endswith(('。', '！', '？', '；', '，')):
            issues['suspicious_short_para'].append(
                f"{pid}[{i}]: '{para}'"
            )
    
    # 1h. Check for duplicate paragraphs
    paras = poem.get('paragraphs', [])
    if len(paras) != len(set(paras)):
        issues['duplicate_paragraphs'].append(f"{pid}: {poem.get('title')}")
    
    stats['total_poems'] += 1

# 1i. Check index has entries not in files
for pid in idx_lookup:
    if pid not in poems:
        issues['index_orphan'].append(f"{pid}: in index but no file")

# 1j. Check files not in index
for pid in poems:
    if pid not in idx_lookup:
        issues['file_not_in_index'].append(f"{pid}: file exists but not in index")

print(f"  Total poems: {stats['total_poems']}")
print(f"  Empty paragraphs: {len(issues['empty_paragraphs'])}")
print(f"  Title mismatches: {len(issues['title_mismatch'])}")
print(f"  Year mismatches: {len(issues['year_mismatch'])}")
print(f"  Route mismatches: {len(issues['route_mismatch'])}")
print(f"  Missing fields: title={len(issues['missing_title'])}, year={len(issues['missing_year'])}, location={len(issues['missing_location'])}")
print(f"  Type/prefix mismatches: {len(issues['type_prefix_mismatch'])}")
print(f"  Suspicious short paragraphs: {len(issues['suspicious_short_para'])}")
print(f"  Duplicate paragraphs: {len(issues['duplicate_paragraphs'])}")
print(f"  Index orphans: {len(issues['index_orphan'])}")
print(f"  Files not in index: {len(issues['file_not_in_index'])}")

# ===== 2. FAMOUS QUOTES / GOLD QUOTE CHECKS =====
print("\n## 2. 金句提取验证")

for pid, poem in poems.items():
    paras_text = ' '.join(poem.get('paragraphs', []))
    famous = poem.get('famousQuotes', [])
    gold = poem.get('gold_quote', '')
    
    # 2a. famousQuotes not found in paragraphs
    for i, q in enumerate(famous):
        # Normalize for comparison (remove punctuation variations)
        q_norm = re.sub(r'[，。、！？；：""''（）\s]', '', q)
        para_norm = re.sub(r'[，。、！？；：""''（）\s]', '', paras_text)
        if q_norm and q_norm not in para_norm:
            issues['quote_not_in_text'].append(
                f"{pid}: famousQuotes[{i}]='{q}' not found in paragraphs"
            )
    
    # 2b. gold_quote not found in paragraphs
    if gold:
        gold_norm = re.sub(r'[，。、！？；：""''（）\s]', '', gold)
        para_norm = re.sub(r'[，。、！？；：""''（）\s]', '', paras_text)
        if gold_norm and gold_norm not in para_norm:
            issues['gold_not_in_text'].append(
                f"{pid}: gold_quote='{gold}' not found in paragraphs"
            )
    
    # 2c. gold_quote not in famousQuotes
    if gold and famous and gold not in famous:
        issues['gold_not_in_famous'].append(
            f"{pid}: gold_quote='{gold}' not in famousQuotes"
        )
    
    # 2d. coreVerse in index doesn't match
    if pid in idx_lookup:
        core = idx_lookup[pid].get('coreVerse', '')
        if core and famous:
            core_norm = re.sub(r'[，。、！？；：""''（）\s]', '', core)
            # Check if coreVerse matches any famousQuote
            matched = False
            for q in famous:
                q_norm = re.sub(r'[，。、！？；：""''（）\s]', '', q)
                if core_norm == q_norm or core_norm in q_norm:
                    matched = True
                    break
            if not matched and core_norm:
                # Check if coreVerse is in text
                para_norm = re.sub(r'[，。、！？；：""''（）\s]', '', paras_text)
                if core_norm not in para_norm:
                    issues['core_verse_not_in_text'].append(
                        f"{pid}: coreVerse='{core}' not in paragraphs"
                    )

print(f"  Quotes not in text: {len(issues['quote_not_in_text'])}")
print(f"  Gold quote not in text: {len(issues['gold_not_in_text'])}")
print(f"  Gold quote not in famousQuotes: {len(issues['gold_not_in_famous'])}")
print(f"  CoreVerse not in text: {len(issues['core_verse_not_in_text'])}")

# ===== 3. ROUTE ASSOCIATION CHECKS =====
print("\n## 3. 路线关联验证")

# Build route->poems mapping
route_poems = defaultdict(list)
for pid, poem in poems.items():
    rid = poem.get('route_id', '')
    if rid:
        route_poems[rid].append(pid)

# Check each route has poems
for rid, route in route_lookup.items():
    poem_count = len(route_poems.get(rid, []))
    if poem_count == 0:
        issues['route_no_poems'].append(f"{rid}: {route['name']} has no poems")
    
# Check poem route_id references valid route
for pid, poem in poems.items():
    rid = poem.get('route_id', '')
    if rid and rid not in route_lookup:
        issues['invalid_route_id'].append(f"{pid}: route_id='{rid}' not found in routes")

# Check related_route_ids in index
for pid, entry in idx_lookup.items():
    for rid in entry.get('related_route_ids', []):
        if rid and rid not in route_lookup:
            issues['invalid_related_route'].append(f"{pid}: related_route_id='{rid}' not found")

# Check year vs route period consistency
for pid, poem in poems.items():
    rid = poem.get('route_id', '')
    year = poem.get('year', 0)
    if rid and year and rid in route_lookup:
        route = route_lookup[rid]
        start = route.get('start_year', 0)
        end = route.get('end_year', 0)
        if start and end and (year < start or year > end):
            # Allow 1-2 year tolerance for boundary cases
            if year < start - 2 or year > end + 2:
                issues['year_route_mismatch'].append(
                    f"{pid}: year={year} outside route {rid} period ({start}-{end})"
                )

print(f"  Routes with no poems: {len(issues['route_no_poems'])}")
print(f"  Invalid route_ids: {len(issues['invalid_route_id'])}")
print(f"  Invalid related_route_ids: {len(issues['invalid_related_route'])}")
print(f"  Year/route period mismatches: {len(issues['year_route_mismatch'])}")

# ===== 4. PLACE-POEM ASSOCIATION CHECKS =====
print("\n## 4. 地点-诗文关联验证")

# Build place->poem references from places data
place_poem_refs = defaultdict(list)
for plid, place in places.items():
    # Check global_works references
    for work in place.get('global_works', []):
        poem_id = work.get('poem_id', '')
        if poem_id:
            place_poem_refs[plid].append(poem_id)
            if poem_id not in poems:
                issues['place_refs_missing_poem'].append(
                    f"Place {plid} ({place.get('ancient_name', '')}) refs poem {poem_id} which doesn't exist"
                )

# Check poem location matches any place
poem_locations = defaultdict(list)
for pid, poem in poems.items():
    loc = poem.get('location', '')
    if loc:
        poem_locations[loc].append(pid)

# Check places that reference poems but poem's route doesn't match place's route
for plid, place in places.items():
    place_routes = place.get('related_routes', [])
    for work in place.get('global_works', []):
        poem_id = work.get('poem_id', '')
        if poem_id and poem_id in poems:
            poem_route = poems[poem_id].get('route_id', '')
            if poem_route and place_routes and poem_route not in place_routes:
                issues['place_poem_route_mismatch'].append(
                    f"Place {plid} routes={place_routes} but poem {poem_id} route={poem_route}"
                )

print(f"  Place refs to missing poems: {len(issues['place_refs_missing_poem'])}")
print(f"  Place-poem route mismatches: {len(issues['place_poem_route_mismatch'])}")

# ===== 5. READING CONTENT CHECKS =====
print("\n## 5. 深度读内容验证")

for pid, poem in poems.items():
    reading = poem.get('reading', {})
    if not reading:
        continue
    
    # 5a. Check reading.scene mentions same year as poem
    scene = reading.get('scene', '')
    poem_year = poem.get('year', 0)
    if scene and poem_year:
        # Extract years from scene text
        scene_years = re.findall(r'(\d{4})年', scene)
        for sy in scene_years:
            if int(sy) != poem_year:
                issues['reading_year_mismatch'].append(
                    f"{pid}: poem year={poem_year}, reading mentions {sy}年"
                )
    
    # 5b. Check reading.lines quotes match famousQuotes/paragraphs
    for i, line in enumerate(reading.get('lines', [])):
        quote = line.get('quote', '')
        if quote:
            q_norm = re.sub(r'[，。、！？；：""''（）\s]', '', quote)
            paras_text = ' '.join(poem.get('paragraphs', []))
            para_norm = re.sub(r'[，。、！？；：""''（）\s]', '', paras_text)
            if q_norm and para_norm and q_norm not in para_norm:
                issues['reading_quote_not_in_text'].append(
                    f"{pid}: reading.lines[{i}].quote='{quote}' not in paragraphs"
                )
    
    # 5c. Check reading.person is not empty/generic
    person = reading.get('person', '')
    if person and len(person) < 10:
        issues['reading_person_too_short'].append(
            f"{pid}: person='{person}'"
        )
    
    # 5d. Check age consistency with year
    age = poem.get('age', '')
    if age and poem_year:
        age_num = re.search(r'(\d+)', age)
        if age_num:
            calculated_birth = poem_year - int(age_num.group(1))
            if calculated_birth != 1037:  # Su Shi born 1037
                issues['age_year_inconsistency'].append(
                    f"{pid}: year={poem_year}, age={age}, implies birth={calculated_birth} (should be 1037)"
                )

print(f"  Reading year mismatches: {len(issues['reading_year_mismatch'])}")
print(f"  Reading quote not in text: {len(issues['reading_quote_not_in_text'])}")
print(f"  Reading person too short: {len(issues['reading_person_too_short'])}")
print(f"  Age/year inconsistencies: {len(issues['age_year_inconsistency'])}")

# ===== 6. DISPUTED WORKS =====
print("\n## 6. 争议作品标记")

for pid, poem in poems.items():
    if poem.get('disputed'):
        issues['disputed_works'].append(
            f"{pid}: {poem.get('title')} - {poem.get('dispute_note', 'no note')}"
        )

print(f"  Disputed works: {len(issues['disputed_works'])}")

# ===== SUMMARY =====
print("\n" + "=" * 60)
print("问题汇总")
print("=" * 60)

total_issues = 0
for category, items in sorted(issues.items()):
    if items:
        print(f"\n### {category} ({len(items)} issues)")
        for item in items[:20]:  # Show first 20
            print(f"  - {item}")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")
        total_issues += len(items)

print(f"\n总问题数: {total_issues}")

# ===== SAVE REPORT =====
report = {
    'generated_at': __import__('datetime').datetime.now().isoformat(),
    'total_poems': stats['total_poems'],
    'total_issues': total_issues,
    'issues': {k: v for k, v in sorted(issues.items()) if v}
}

report_path = f'{BASE}/meta/validation-report.json'
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"\nReport saved to: {report_path}")
