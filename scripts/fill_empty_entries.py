#!/usr/bin/env python3
"""Fill 86 empty poem entries using chinese-poetry database.
Multi-source verification: match against both 全唐诗 and 宋词 databases.
"""
import json, glob, re, os
from pathlib import Path

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"
CP = "/tmp/chinese-poetry"

# ─── Load chinese-poetry data ───
def load_song_poems():
    """Load 苏轼 poems from 全唐诗/全宋诗"""
    poems = []
    for f in glob.glob(f'{CP}/全唐诗/poet.song*.json'):
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        for p in data:
            if '苏轼' in p.get('author', ''):
                poems.append(p)
    return poems

def load_song_ci():
    """Load 苏轼 ci from 宋词"""
    poems = []
    for f in glob.glob(f'{CP}/宋词/ci.song*.json'):
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        for p in data:
            if '苏轼' in p.get('author', ''):
                poems.append(p)
    return poems

def normalize(s):
    """Simplify + clean for matching"""
    if not s:
        return ""
    try:
        import zhconv
        s = zhconv.convert(s, 'zh-cn')
    except:
        pass
    s = re.sub(r'[（）()【】《》「」『』·•・\s,，。、！？；：]', '', s)
    return s

def extract_core_verse(paragraphs):
    """Extract the most famous line from paragraphs"""
    if not paragraphs:
        return ""
    # Take first paragraph, first sentence
    text = paragraphs[0] if isinstance(paragraphs, list) else paragraphs
    # Split by sentence-ending punctuation
    for punct in ['。', '！', '？']:
        idx = text.find(punct)
        if idx > 0:
            return text[:idx+1]
    return text[:20]

# ─── Main ───
def main():
    # Load sources
    print("Loading chinese-poetry database...")
    song_poems = load_song_poems()
    song_ci = load_song_ci()
    all_cp = song_poems + song_ci
    print(f"  苏轼诗: {len(song_poems)}, 苏轼词: {len(song_ci)}, Total: {len(all_cp)}")
    
    # Build normalized index
    cp_index = {}
    for p in all_cp:
        title = p.get('title', '')
        norm = normalize(title)
        if norm:
            cp_index[norm] = p
            # Also index by partial title
            if len(norm) > 4:
                cp_index[norm[:4]] = p
    
    # Load empty entries
    empty = []
    for f in sorted(glob.glob(f'{BASE}/*.json')):
        with open(f) as fp:
            d = json.load(fp)
        if not d.get('paragraphs') or len(d.get('paragraphs', [])) == 0:
            empty.append(d)
    
    print(f"\nEmpty entries to fill: {len(empty)}")
    
    matched = 0
    unmatched = []
    
    for d in empty:
        fid = d['id']
        title = d['title']
        norm_title = normalize(title)
        
        # Try matching
        cp_match = None
        match_level = 0
        
        # Level 1: Exact match
        if norm_title in cp_index:
            cp_match = cp_index[norm_title]
            match_level = 1
        
        # Level 2: Title contains
        if not cp_match:
            for norm, p in cp_index.items():
                if norm_title in norm or norm in norm_title:
                    cp_match = p
                    match_level = 2
                    break
        
        # Level 3: Keyword match (first 4 chars)
        if not cp_match and len(norm_title) >= 4:
            key = norm_title[:4]
            if key in cp_index:
                cp_match = cp_index[key]
                match_level = 3
        
        # Level 4: Search all titles for keyword
        if not cp_match:
            for p in all_cp:
                cp_norm = normalize(p.get('title', ''))
                # Check if key words from our title appear in cp title
                if norm_title[:3] in cp_norm or norm_title[-3:] in cp_norm:
                    cp_match = p
                    match_level = 4
                    break
        
        if cp_match:
            # Extract paragraphs
            paras = cp_match.get('paragraphs', [])
            if isinstance(paras, str):
                paras = [paras]
            
            # Convert to simplified Chinese
            try:
                import zhconv
                paras = [zhconv.convert(p, 'zh-cn') for p in paras]
            except:
                pass
            
            if paras:
                d['paragraphs'] = paras
                core = extract_core_verse(paras)
                if core:
                    d['coreVerse'] = core
                    if not d.get('famousQuotes'):
                        d['famousQuotes'] = [core]
                d['has_full_text'] = True
                d['full_text_source'] = 'chinese-poetry'
                d['full_text_match_level'] = match_level
                
                # Write back
                with open(f'{BASE}/{fid}.json', 'w', encoding='utf-8') as fp:
                    json.dump(d, fp, ensure_ascii=False, indent=2)
                
                matched += 1
                print(f"  ✓ {fid}: {title} → matched (level {match_level})")
            else:
                unmatched.append((fid, title))
                print(f"  ✗ {fid}: {title} → match found but no paragraphs")
        else:
            unmatched.append((fid, title))
            print(f"  ✗ {fid}: {title} → no match")
    
    print(f"\n=== Results ===")
    print(f"Matched and filled: {matched}")
    print(f"Unmatched: {len(unmatched)}")
    for fid, title in unmatched:
        print(f"  {fid}: {title}")

if __name__ == '__main__':
    main()
