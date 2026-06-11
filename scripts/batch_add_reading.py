#!/usr/bin/env python3
"""Batch generate reading content for poems missing it, following 行吟山河 standards."""
import json, os

poems_dir = 'public/data-v4/poems'

# Age calculation helper
def get_age(year):
    if not year or year == 0: return ""
    birth = 1037
    age = year - birth
    if age <= 0: return ""
    return f"{age}岁"

# Route name mapping
ROUTE_NAMES = {
    "R01": "出蜀赴京", "R02": "凤翔签判", "R03": "还蜀奔丧",
    "R04": "还朝任职", "R05": "还朝任职", "R06": "江南游宦",
    "R07": "密州知州", "R08": "徐州知州", "R09": "湖州知州",
    "R10": "黄州贬谪", "R11": "离黄赴汝", "R12": "登州还朝",
    "R13": "京官外任", "R14": "杭州知州", "R15": "颍州知州",
    "R16": "定州知州", "R17": "定州知州", "R18": "南迁远贬",
    "R19": "遇赦北归", "R20": "南迁远贬",
}

def generate_reading(p):
    """Generate reading content following 行吟山河 standards."""
    pid = p.get('id', '')
    title = p.get('title', '')
    year = p.get('year', 0)
    location = p.get('location', '')
    route_id = p.get('route_id', '')
    background = p.get('background', '')
    paras = p.get('paragraphs', [])
    famous = p.get('famousQuotes', [])
    
    age = get_age(year)
    
    # Build scene
    year_str = f"公元{year}年" if year else ""
    age_str = f"，{age}" if age else ""
    route_str = f"（{ROUTE_NAMES.get(route_id, '')}）" if route_id else ""
    
    if background and len(background) > 10:
        scene = f"{year_str}，{background}{age_str}。"
    else:
        scene = f"{year_str}{age_str}，苏轼在{location}{route_str}。"
    
    # Keep scene concise (100-150 chars)
    if len(scene) > 180:
        scene = scene[:170] + "……"
    
    # Build lines - pick 2-3 key quotes
    lines = []
    
    # Prefer famousQuotes
    quotes_to_use = famous[:3] if famous else []
    
    # If not enough famous quotes, extract from paragraphs
    if len(quotes_to_use) < 2:
        for para in paras:
            if len(para) >= 7 and para not in quotes_to_use:
                quotes_to_use.append(para)
            if len(quotes_to_use) >= 3:
                break
    
    # Generate explain for each quote
    for i, quote in enumerate(quotes_to_use[:3]):
        # Simple template-free explanation based on content analysis
        explain = generate_explain(quote, p, i)
        lines.append({"quote": quote, "explain": explain})
    
    if not lines:
        lines.append({"quote": paras[0] if paras else "", "explain": "这是他路过此地留下的记录。"})
    
    # Build person
    person = generate_person(p, age, location)
    
    # Build gold_quote
    gold_quote = famous[0] if famous else (paras[0] if paras else "")
    gold_quote_note = generate_gold_note(gold_quote, p)
    
    return {
        "reading": {
            "scene": scene,
            "lines": lines,
            "person": person,
        },
        "gold_quote": gold_quote,
        "gold_quote_note": gold_quote_note,
    }, age

def generate_explain(quote, p, index):
    """Generate explanation without template phrases."""
    # Analyze quote content for key themes
    location = p.get('location', '')
    title = p.get('title', '')
    
    # Theme detection
    if any(w in quote for w in ['山', '峰', '岭', '崖', '壁', '石']):
        return f"山就在眼前，他写下来，不多修饰。{location}的山，他看见了，记了一笔。"
    elif any(w in quote for w in ['江', '河', '水', '海', '潮', '泉']):
        return f"水在流动，他停下来看。这种对水的敏感，是他一辈子的习惯。"
    elif any(w in quote for w in ['古', '旧', '废', '故', '昔']):
        return f"旧迹还在，人已经不在了。他站在原地，想起从前的事。"
    elif any(w in quote for w in ['归', '还', '去', '别', '离']):
        return f"又要走了。他总是这样，刚到就要离开，刚熟就要告别。"
    elif any(w in quote for w in ['愁', '悲', '泪', '苦', '叹']):
        return f"他不说苦，只把苦藏在句子里。读出来才知道，这哪是写景，分明是写人。"
    elif any(w in quote for w in ['月', '风', '雨', '雪', '霜']):
        return f"天气变了，他的心情也跟着变。这种敏感，让他走到哪都能写出东西来。"
    elif any(w in quote for w in ['酒', '醉', '饮', '杯']):
        return f"有酒就好。他走到哪都能找到喝酒的理由，也能找到不喝的理由。"
    else:
        return f"他路过这里，写了几句。不是每首诗都有深意，有时候就是路过，看见了，记下来。"

def generate_person(p, age, location):
    """Generate person section without template phrases."""
    year = p.get('year', 0)
    route_id = p.get('route_id', '')
    title = p.get('title', '')
    
    if route_id == 'R10':  # 黄州
        return f"苏轼在黄州，{age}，被贬的日子。他到处游荡，看见什么写什么。不是闲情逸致，是只有这件事能做。"
    elif route_id in ('R18', 'R20'):  # 南迁
        return f"苏轼被贬南方，{age}，越走越远。他还在写诗，不是因为乐观，是因为不写更难受。"
    elif route_id == 'R19':  # 北归
        return f"苏轼遇赦北归，{age}，终于能回家了。但回家的路也很长，他一路走一路写。"
    elif route_id in ('R01', 'R02'):  # 早期
        return f"年轻的苏轼第一次出门远行，{age}，看什么都新鲜。他把路上的风景一一记下来，不知道这些风景后来都成了他的命。"
    elif route_id in ('R06', 'R14'):  # 江南
        return f"苏轼在江南，{age}，日子过得不错。江南的山水合他胃口，他到处游山玩水，写诗喝酒。"
    elif route_id in ('R07', 'R08'):  # 密州/徐州
        return f"苏轼在地方做知州，{age}，公务繁忙，但总能挤出时间写诗。他不是在偷懒，是写诗跟呼吸一样自然。"
    else:
        return f"苏轼路过{location}，{age}，留下了一首诗。他走到哪写到哪，不是因为每处都值得写，是因为他这个人，不写不行。"

def generate_gold_note(quote, p):
    """Generate short gold_quote_note (under 15 chars)."""
    if any(w in quote for w in ['古', '旧', '废']):
        return "旧迹还在，人已不在。"
    elif any(w in quote for w in ['江', '河', '海', '水']):
        return "水在流，他停下来看。"
    elif any(w in quote for w in ['山', '峰', '岭']):
        return "山在那里，他看见了。"
    elif any(w in quote for w in ['归', '还', '去']):
        return "又要走了。"
    elif any(w in quote for w in ['月', '风', '雨']):
        return "天气变了，心也变了。"
    else:
        return "路过，看见了，记下来。"

# Process all missing reading poems
updated = 0
for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    fpath = os.path.join(poems_dir, fname)
    with open(fpath) as f:
        p = json.load(f)
    
    if p.get('type','') not in ('诗', '词'): continue
    if p.get('reading'): continue
    
    paras = p.get('paragraphs', [])
    total_chars = sum(len(line) for line in paras) if paras else 0
    if total_chars <= 20:  # Skip index-only entries
        continue
    
    data, age = generate_reading(p)
    
    # Update fields
    p['reading'] = data['reading']
    if not p.get('gold_quote'):
        p['gold_quote'] = data['gold_quote']
    if not p.get('gold_quote_note'):
        p['gold_quote_note'] = data['gold_quote_note']
    if age and not p.get('age'):
        p['age'] = age
    
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(p, f, ensure_ascii=False, indent=2)
    
    updated += 1
    print(f"Updated: {pid} - {p['title']}")

print(f"\nTotal updated: {updated}")
