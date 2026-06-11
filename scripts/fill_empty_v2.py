#!/usr/bin/env python3
"""Fill 86 empty poem entries using chinese-poetry database - fixed version."""
import json, glob, re, os

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"
CP = "/tmp/chinese-poetry"

def load_all_su_shi():
    """Load ALL 苏轼 poems from chinese-poetry"""
    poems = []
    # 宋诗
    for f in sorted(glob.glob(f'{CP}/全唐诗/poet.song.*.json')):
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        for p in data:
            author = p.get('author', '')
            if '苏轼' in author or '蘇軾' in author:
                poems.append(p)
    # 宋词
    for f in sorted(glob.glob(f'{CP}/宋词/ci.song.*.json')):
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        for p in data:
            author = p.get('author', '')
            if '苏轼' in author or '蘇軾' in author:
                poems.append(p)
    return poems

def to_simplified(text):
    try:
        import zhconv
        return zhconv.convert(text, 'zh-cn')
    except:
        return text

def normalize(s):
    if not s: return ""
    s = to_simplified(s)
    s = re.sub(r'[（）()【】《》「」『』·•・\s,，。、！？；：]', '', s)
    return s

def main():
    print("Loading chinese-poetry...")
    all_poems = load_all_su_shi()
    print(f"Total 苏轼 works: {len(all_poems)}")
    
    # Build title index (simplified)
    title_index = {}
    for p in all_poems:
        title = to_simplified(p.get('title', ''))
        norm = normalize(title)
        if norm:
            if norm not in title_index:
                title_index[norm] = []
            title_index[norm].append(p)
    
    # Load empty entries
    empty = []
    for f in sorted(glob.glob(f'{BASE}/*.json')):
        with open(f) as fp:
            d = json.load(fp)
        if not d.get('paragraphs') or len(d.get('paragraphs', [])) == 0:
            empty.append(d)
    
    print(f"Empty entries: {len(empty)}")
    
    matched = 0
    unmatched = []
    
    for d in empty:
        fid = d['id']
        title = d['title']
        norm_title = normalize(title)
        
        cp_match = None
        match_level = 0
        
        # Level 1: Exact normalized match
        if norm_title in title_index:
            candidates = title_index[norm_title]
            cp_match = candidates[0]
            match_level = 1
        
        # Level 2: Title contains (both directions)
        if not cp_match:
            for norm_key, candidates in title_index.items():
                if len(norm_title) >= 3 and (norm_title in norm_key or norm_key in norm_title):
                    cp_match = candidates[0]
                    match_level = 2
                    break
        
        # Level 3: Fuzzy - search by keywords
        if not cp_match:
            keywords = norm_title[:min(4, len(norm_title))]
            if len(keywords) >= 2:
                for norm_key, candidates in title_index.items():
                    if keywords in norm_key:
                        cp_match = candidates[0]
                        match_level = 3
                        break
        
        # Level 4: Very fuzzy - any 2-char substring
        if not cp_match and len(norm_title) >= 3:
            for i in range(len(norm_title) - 1):
                sub = norm_title[i:i+2]
                if len(sub) >= 2:
                    for norm_key, candidates in title_index.items():
                        if sub in norm_key and len(norm_key) < len(norm_title) + 5:
                            cp_match = candidates[0]
                            match_level = 4
                            break
                    if cp_match:
                        break
        
        if cp_match:
            paras = cp_match.get('paragraphs', [])
            if isinstance(paras, str):
                paras = [paras]
            paras = [to_simplified(p) for p in paras]
            
            if paras and any(len(p.strip()) > 0 for p in paras):
                d['paragraphs'] = paras
                # Extract core verse
                first_para = paras[0]
                core = ""
                for punct in ['。', '！', '？']:
                    idx = first_para.find(punct)
                    if idx > 0:
                        core = first_para[:idx+1]
                        break
                if not core:
                    core = first_para[:20]
                if core:
                    d['coreVerse'] = core
                    if not d.get('famousQuotes') or not d['famousQuotes']:
                        d['famousQuotes'] = [core]
                d['has_full_text'] = True
                d['full_text_source'] = 'chinese-poetry'
                d['full_text_match_level'] = match_level
                d['matched_title'] = to_simplified(cp_match.get('title', ''))
                
                with open(f'{BASE}/{fid}.json', 'w', encoding='utf-8') as fp:
                    json.dump(d, fp, ensure_ascii=False, indent=2)
                
                matched += 1
                matched_title = to_simplified(cp_match.get('title', ''))
                print(f"  ✓ {fid}: {title} → {matched_title} (L{match_level})")
            else:
                unmatched.append((fid, title, 'empty paragraphs'))
                print(f"  ✗ {fid}: {title} → empty paragraphs")
        else:
            unmatched.append((fid, title, 'no match'))
            print(f"  ✗ {fid}: {title} → no match")
    
    print(f"\n=== Results ===")
    print(f"Matched: {matched}")
    print(f"Unmatched: {len(unmatched)}")
    for fid, title, reason in unmatched:
        print(f"  {fid}: {title} ({reason})")

if __name__ == '__main__':
    main()
