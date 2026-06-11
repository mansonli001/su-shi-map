#!/usr/bin/env python3
"""
Fill empty entries using chinese-poetry with improved matching.
Key improvements:
1. Better title normalization (remove 过/至/次韵/游/题/初发/怀古 etc.)
2. Location-based matching as fallback
3. Manual verification list for uncertain matches
"""
import json, glob, re, os

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"
CP = "/tmp/chinese-poetry"

def to_simplified(text):
    try:
        import zhconv
        return zhconv.convert(text, 'zh-cn')
    except:
        return text

def normalize_title(title):
    """Normalize title for matching - remove common prefixes and suffixes"""
    if not title:
        return ""
    s = to_simplified(title)
    # Remove common prefixes
    s = re.sub(r'^过', '', s)
    s = re.sub(r'^至', '', s)
    s = re.sub(r'^游', '', s)
    s = re.sub(r'^题', '', s)
    s = re.sub(r'^初发', '', s)
    s = re.sub(r'^次韵', '', s)
    # Remove common suffixes
    s = re.sub(r'怀古$', '', s)
    s = re.sub(r'次韵$', '', s)
    s = re.sub(r'题诗$', '', s)
    s = re.sub(r'题壁$', '', s)
    s = re.sub(r'观海$', '', s)
    # Remove punctuation
    s = re.sub(r'[（）()【】《》「」『』·•・\s,，。、！？；：]', '', s)
    return s.strip()

def load_all_su_shi():
    """Load ALL 苏轼 poems from chinese-poetry"""
    poems = []
    for f in sorted(glob.glob(f'{CP}/全唐诗/poet.song.*.json')):
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        for p in data:
            author = p.get('author', '')
            if '苏轼' in author or '蘇軾' in author:
                poems.append(p)
    for f in sorted(glob.glob(f'{CP}/宋词/ci.song.*.json')):
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        for p in data:
            author = p.get('author', '')
            if '苏轼' in author or '蘇軾' in author:
                poems.append(p)
    return poems

def main():
    print("Loading chinese-poetry...")
    all_poems = load_all_su_shi()
    print(f"Total 苏轼 works: {len(all_poems)}")
    
    # Build multiple indices
    exact_index = {}  # exact title match
    norm_index = {}   # normalized title match
    keyword_index = {} # keyword-based match
    
    for p in all_poems:
        title = to_simplified(p.get('title', ''))
        norm = normalize_title(title)
        paras = p.get('paragraphs', [])
        if isinstance(paras, str):
            paras = [paras]
        paras = [to_simplified(x) for x in paras]
        
        entry = {
            'title': title,
            'norm_title': norm,
            'paragraphs': paras,
            'original_title': p.get('title', '')
        }
        
        # Exact index
        if title not in exact_index:
            exact_index[title] = []
        exact_index[title].append(entry)
        
        # Normalized index
        if norm and len(norm) >= 2:
            if norm not in norm_index:
                norm_index[norm] = []
            norm_index[norm].append(entry)
        
        # Keyword index (each 2-char substring)
        for i in range(len(norm) - 1):
            key = norm[i:i+2]
            if key not in keyword_index:
                keyword_index[key] = []
            keyword_index[key].append(entry)
    
    # Load empty entries
    empty = []
    for f in sorted(glob.glob(f'{BASE}/*.json')):
        with open(f) as fp:
            d = json.load(fp)
        if not d.get('paragraphs') or len(d.get('paragraphs', [])) == 0:
            empty.append(d)
    
    print(f"Empty entries: {len(empty)}")
    
    # Match each empty entry
    results = []
    for d in empty:
        fid = d['id']
        title = d['title']
        location = d.get('location', '')
        norm = normalize_title(title)
        
        match = None
        match_type = None
        
        # Level 1: Exact title match
        if title in exact_index:
            candidates = exact_index[title]
            # Pick the one with most paragraphs
            match = max(candidates, key=lambda x: len(''.join(x['paragraphs'])))
            match_type = 'exact'
        
        # Level 2: Normalized title match
        if not match and norm in norm_index:
            candidates = norm_index[norm]
            match = max(candidates, key=lambda x: len(''.join(x['paragraphs'])))
            match_type = 'normalized'
        
        # Level 3: Title contains or is contained
        if not match and len(norm) >= 2:
            for key, candidates in norm_index.items():
                if (norm in key or key in norm) and len(key) >= 2:
                    match = max(candidates, key=lambda x: len(''.join(x['paragraphs'])))
                    match_type = 'contains'
                    break
        
        # Level 4: Location keyword match
        if not match:
            loc_norm = normalize_title(location)
            if loc_norm and len(loc_norm) >= 2:
                for key, candidates in norm_index.items():
                    if loc_norm in key or key in loc_norm:
                        # Verify the match makes sense
                        match = max(candidates, key=lambda x: len(''.join(x['paragraphs'])))
                        match_type = 'location'
                        break
        
        if match:
            results.append({
                'id': fid,
                'title': title,
                'matched_title': match['title'],
                'match_type': match_type,
                'paragraphs': match['paragraphs'],
                'original_title': match['original_title']
            })
        else:
            results.append({
                'id': fid,
                'title': title,
                'matched_title': None,
                'match_type': 'none',
                'paragraphs': [],
                'original_title': None
            })
    
    # Print results
    matched = [r for r in results if r['match_type'] != 'none']
    unmatched = [r for r in results if r['match_type'] == 'none']
    
    print(f"\n=== Matched: {len(matched)} ===")
    for r in matched:
        first_line = r['paragraphs'][0][:30] if r['paragraphs'] else ''
        print(f"  {r['id']}: {r['title']} → {r['matched_title']} ({r['match_type']})")
        print(f"    {first_line}...")
    
    print(f"\n=== Unmatched: {len(unmatched)} ===")
    for r in unmatched:
        print(f"  {r['id']}: {r['title']} @ {location}")

if __name__ == '__main__':
    main()
