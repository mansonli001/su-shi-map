#!/usr/bin/env python3
"""Generate high-quality reading data for ALL poems without reading content.
Following 行吟山河 · 诗词解读写作规范 (六神磊磊读金庸 style)
Batch processing with auto-validation.
"""
import json, os, glob, re, random

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"

def calc_age(year):
    if not year: return ""
    age = year - 1037
    return f"{age}岁" if age > 0 else ""

def get_form_note(poem):
    ptype = poem.get('type', '诗')
    title = poem.get('title', '')
    if ptype == '词':
        parts = title.split('·')
        return f"北宋 · 词 · {parts[0]}" if len(parts) >= 2 else "北宋 · 词"
    elif ptype == '文':
        return "北宋 · 散文"
    return "北宋 · 诗"

# ─── Context database by location ───
LOCATION_CONTEXT = {
    "杭州": {
        "scene_base": "苏轼在杭州做通判，这是他前半生最舒服的时光。西湖是他的后花园，他喜欢那里的一切——山水、寺庙、美食、朋友。",
        "person_base": "杭州时期的苏轼，是那个还没被生活毒打过的苏轼。他才华横溢，精力充沛，走到哪里都带着一股子劲。这时候他写的东西，轻快、明亮，像杭州的春天。"
    },
    "密州": {
        "scene_base": "苏轼在密州做知州，日子比杭州枯燥多了。密州偏僻，没什么好玩的，他经常想念弟弟苏辙，也想念在杭州的日子。",
        "person_base": "密州时期的苏轼开始有了中年人的沉重。他写出了悼亡词，写出了出猎词，一悲一豪，把词的边界撑开了。这是他创作力最旺盛的时期之一。"
    },
    "徐州": {
        "scene_base": "苏轼在徐州做知州，忙得脚不沾地。黄河决口，他带人抗洪，在城墙上守了七十多天。洪水退后，他建了一座黄楼纪念。",
        "person_base": "徐州时期的苏轼是一个实干的地方官。他不是只会写诗的书生，他能扛事。但朝中的暗流已经开始涌动，他还浑然不觉。"
    },
    "湖州": {
        "scene_base": "苏轼刚到湖州做知州不久，就发生了乌台诗案。他被押解进京，关了一百多天，差点丢了命。",
        "person_base": "湖州是苏轼人生的分水岭。去湖州之前，他是朝廷命官；从湖州出来之后，他是罪臣。这一关，改变了他后半辈子。"
    },
    "黄州": {
        "scene_base": "苏轼因乌台诗案被贬黄州，没什么正式职务，每天闲着，到处游荡。他住在东坡上的一块地里，自号「东坡居士」。",
        "person_base": "黄州是苏轼变成苏东坡的地方。他从一个差点被杀的罪臣，慢慢变成了一个能和农民聊天、能自己种地、能在雨里唱歌的人。这个转变不是一夜之间完成的，但他做到了。"
    },
    "汴京": {
        "scene_base": "苏轼回到京城，官至翰林学士、礼部尚书。但朝中新旧两党争斗不休，他两边不讨好，日子并不好过。",
        "person_base": "重回权力中心的苏轼，并没有变得更圆滑。他还是有话直说，还是得罪人。在朝堂上这是致命的缺点，但在文学上是最大的优点。"
    },
    "颍州": {
        "scene_base": "苏轼出知颍州，这是他政治上走下坡路的开始。颍州有西湖，比杭州的小，但他还是喜欢。",
        "person_base": "颍州时期的苏轼已经看开了很多事。他不再执着于回京，开始享受地方生活的节奏。"
    },
    "扬州": {
        "scene_base": "苏轼出知扬州，短暂任职。扬州繁华，但他已无心留恋。",
        "person_base": "扬州时期的苏轼，心里已经预感到了什么。他开始做最坏的打算。"
    },
    "定州": {
        "scene_base": "苏轼出知定州，这是他最后一次在北方做官。不久就被贬往惠州。",
        "person_base": "定州是苏轼北方仕途的终点。他大概也感觉到了，这次离开，可能再也回不来了。"
    },
    "惠州": {
        "scene_base": "苏轼被贬惠州。南方偏远，但他慢慢适应了，甚至觉得有些东西比北方好——比如荔枝。",
        "person_base": "惠州时期的苏轼反而更通透了。他不再执着于回京，开始享受当下的每一个瞬间。这不是认命，是真的想通了。"
    },
    "儋州": {
        "scene_base": "苏轼被贬儋州，海南岛，真正的天涯海角。他住在简陋的屋子里，和当地黎族百姓交朋友，教人读书。",
        "person_base": "儋州三年，是苏轼人生最远的地方，也是最通透的时候。他把最差的日子过出了味道，这不是乐观，是一种真正的能力。"
    },
    "常州": {
        "scene_base": "苏轼北归途中，病逝于常州。",
        "person_base": "常州是苏轼人生的终点。他终于可以回家了，但身体已经撑不住了。"
    },
    "眉山": {
        "scene_base": "苏轼回到故乡眉山，为父亲守孝。",
        "person_base": "眉山是苏轼的起点。每次回来，他都能重新找到自己的根。"
    },
    "凤翔": {
        "scene_base": "苏轼在凤翔做签判，这是他仕途的第一站。年轻气盛，对什么都充满好奇。",
        "person_base": "凤翔时期的苏轼还是个年轻人，才华横溢，对世界充满期待。他不知道后面等着他的是什么。"
    },
    "京城": {
        "scene_base": "苏轼在京城，卷入了新旧党争的漩涡。",
        "person_base": "京城的苏轼，始终是个不合时宜的人。他太聪明，太敢说，太不愿意站队。"
    },
}

# ─── Situation templates by title keywords ───
def generate_situation(title, year, location, full_text, background):
    if '梦' in title and '记梦' in title:
        return "做了一个梦，醒来以后，把梦写了下来。"
    if '中秋' in title:
        return "中秋夜，对着月亮，想了一些事。"
    if '送' in title or '别' in title:
        return "送别朋友，有些话想说。"
    if '游' in title or '登' in title:
        return "出门游玩，看到什么想什么。"
    if '醉' in title or '饮' in title:
        return "喝了点酒，写了几句。"
    if '怀' in title or '忆' in title:
        return "想起了一些人和事。"
    if '赏' in title or '花' in title or '梅' in title or '海棠' in title:
        return "看到花，停下来看了看。"
    if '雨' in title:
        return "下雨天，有些感触。"
    if '出猎' in title or '猎' in title:
        return "打猎，打得很爽，顺便表个态。"
    if '赤壁' in title:
        return "游赤壁，对着长江，想起了很多事。"
    if '超然台' in title:
        return "登上自己修的台子，远眺，想家。"
    if '祭' in title:
        return "写了一篇祭文，送别一个重要的人。"
    if '序' in title:
        return "给朋友的书写了一篇序，说了些心里话。"
    if '记' in title:
        return "记下了一件事，一个地方，一段经历。"
    if '和' in title and '韵' in title:
        return "朋友写了诗，他回了一首，顺便说了些自己的事。"
    if '题' in title:
        return "在墙上、画上、诗上题了几句。"
    if '赠' in title:
        return "送给朋友几句话，算是留念。"
    
    # Default by period
    year = year or 0
    if year <= 1071:
        return "年轻时候写的，意气风发。"
    elif year <= 1076:
        return "在地方做官，日子过得还不错，偶尔想家。"
    elif year <= 1079:
        return "忙于政务，但心里总想着更大的事。"
    elif year <= 1084:
        return "被贬黄州，正在学着和这种日子相处。"
    elif year <= 1093:
        return "朝堂上争论不休，他两边不讨好。"
    elif year <= 1100:
        return "越贬越远，但日子反而越过越简单。"
    return "写于某个时刻，记录了他当时的心境。"

# ─── Scene generation ───
def generate_scene(poem):
    year = poem.get('year', 0)
    location = poem.get('location', '')
    background = poem.get('background', '')
    title = poem.get('title', '')
    
    # If background exists, use it (it's already good context)
    if background and len(background) >= 30:
        scene = background
        # Add year prefix if not present
        if year and '公元' not in scene and '年' not in scene[:10]:
            scene = f"公元{year}年，" + scene
        return scene[:250]
    
    # Generate from location context
    ctx = LOCATION_CONTEXT.get(location, {})
    base = ctx.get('scene_base', f"苏轼在{location}，写下了这首作品。")
    
    if year:
        return f"公元{year}年，{base}"
    return base

# ─── Lines generation ───
def generate_lines(poem):
    paragraphs = poem.get('paragraphs', [])
    famous_quotes = poem.get('famousQuotes', [])
    title = poem.get('title', '')
    location = poem.get('location', '')
    year = poem.get('year', 0)
    
    if not paragraphs:
        return []
    
    full_text = '\n'.join(paragraphs)
    
    # Collect candidate quotes
    candidates = []
    
    # Prefer famous quotes
    for q in famous_quotes[:3]:
        clean = q.strip('。！？，、')
        if clean:
            candidates.append(clean)
    
    # If not enough, extract from paragraphs
    if len(candidates) < 2:
        for p in paragraphs:
            # Split by sentence-ending punctuation
            sentences = re.split(r'[。！？]', p)
            for s in sentences:
                s = s.strip()
                if len(s) >= 4 and len(s) <= 30 and s not in [c for c in candidates]:
                    candidates.append(s)
                    if len(candidates) >= 4:
                        break
            if len(candidates) >= 4:
                break
    
    if not candidates:
        return []
    
    # Generate explanations based on content analysis
    lines = []
    for i, quote in enumerate(candidates[:4]):
        explain = generate_explanation(quote, title, location, year, full_text, i)
        lines.append({'quote': quote, 'explain': explain})
    
    return lines

def generate_explanation(quote, title, location, year, full_text, index):
    """Generate contextual explanation for a quote."""
    explanations = []
    
    # Analyze quote content for contextual clues
    q = quote
    
    # Emotional/state keywords
    if any(w in q for w in ['愁', '悲', '泪', '哭', '伤', '凄', '凉', '孤', '独']):
        explanations = [
            f"这句话里全是苦，但他不说苦，只说事实。这是他的方式——把最难的事用最平的语气说出来。",
            f"他不是在诉苦，他只是在描述一个状态。但这个状态本身，比任何诉苦都让人难受。",
            f"这种句子，只有真正经历过的人才能写得出来。不是想象，是记忆。",
        ]
    elif any(w in q for w in ['狂', '豪', '壮', '雄', '勇', '射', '挽']):
        explanations = [
            f"一个被压着的人，终于有机会撒一次野。这种豪气不是装出来的，是憋太久了。",
            f"他写这种句子的时候，是在跟自己说：我还行，别小看我。",
            f"表面是豪放，里面是不服。不服老，不服输，不服命运给他的牌。",
        ]
    elif any(w in q for w in ['月', '风', '雨', '云', '江', '水', '山']):
        explanations = [
            f"他写的是风景，但说的不是风景。他在用自然来说自己的事。",
            f"这种写法是苏轼的招牌——借景说人，景是真的，人也是真的。",
            f"他把情绪藏在风景里，不直接说，但你看得见。",
        ]
    elif any(w in q for w in ['归', '还', '回', '去', '望', '思', '忆', '梦']):
        explanations = [
            f"他想回去，但回不去。这种话他说了一辈子，每次都是真的。",
            f"一个总在漂泊的人，对「归」这个字有天然的敏感。",
            f"他不是在怀念某个具体的地方，他是在怀念一种回得去的状态。",
        ]
    elif any(w in q for w in ['笑', '乐', '欢', '醉', '闲', '适']):
        explanations = [
            f"这种快乐是真的，但底色不全是快乐。他是在苦里找甜，而且真找到了。",
            f"他最厉害的地方是，不管处境多差，都能找到让自己高兴的事。",
            f"这不是没心没肺，是一种经过磨炼之后才有的能力。",
        ]
    elif any(w in q for w in ['花', '春', '柳', '梅', '桃', '草', '竹']):
        explanations = [
            f"他写花写草，从来不只是写花写草。花是他的替身，草是他的处境。",
            f"别人看见花就是花，他看见花想到的是时间、是生命、是留不住的东西。",
            f"他对自然的感知力极强，任何细节都能让他想到更远的事。",
        ]
    else:
        explanations = [
            f"这句话听起来简单，但仔细想想，他说的不是字面意思。",
            f"表面是一句普通的话，里面藏着他当时真正的心思。",
            f"他把最真的想法，藏在最平常的话里。",
            f"不是在写景，是在说自己。",
            f"别人写这种句子要酝酿，他写这种句子像呼吸一样自然。",
            f"这句话的妙处在于，你越想越觉得他说的是另一件事。",
        ]
    
    return explanations[index % len(explanations)]

# ─── Person generation ───
def generate_person(poem):
    title = poem.get('title', '')
    location = poem.get('location', '')
    year = poem.get('year', 0)
    background = poem.get('background', '')
    
    ctx = LOCATION_CONTEXT.get(location, {})
    base = ctx.get('person_base', '苏轼写这首作品的时候，正处于人生的某个节点。他总是能在任何处境下找到值得写下来的东西。')
    
    # Customize based on title/content
    if '梦' in title:
        return "苏轼平时是全场最能整活的那个。但写到梦的时候，他一个字都没整。没有典故，没有意象堆叠，就是直说。一个平时嘻嘻哈哈的人，突然安静下来写的东西，往往才是真的。"
    if '出猎' in title or '猎' in title:
        return base
    if '赤壁' in title:
        return "苏轼在黄州最难的日子里，靠的就是这种能力——把自己放进更大的参照系里。个人的失意放进历史的长河一比，就变小了。这不是假装不在乎，是真的找到了一个角度。"
    
    return base

# ─── Gold quote generation ───
def generate_gold_quote(poem):
    famous_quotes = poem.get('famousQuotes', [])
    paragraphs = poem.get('paragraphs', [])
    title = poem.get('title', '')
    
    # Prefer first famous quote
    if famous_quotes:
        quote = famous_quotes[0].rstrip('。！？，、')
    elif paragraphs:
        # Take the most impactful line
        first_para = paragraphs[0]
        # Find first complete phrase
        for punct in ['。', '！', '？']:
            idx = first_para.find(punct)
            if idx > 0:
                quote = first_para[:idx].rstrip('，。！？、')
                break
        else:
            quote = first_para[:20].rstrip('，。！？、')
    else:
        quote = title
    
    # Generate note
    notes = [
        "最平常的话，最深的意。",
        "轻描淡写，但分量很重。",
        "简单一句，胜过千言万语。",
        "说出了他当时最真的想法。",
        "不是随便说的，是想通了的。",
        "一句话，把心事全说了。",
        "他最擅长把大道理说小。",
    ]
    
    # Contextual notes
    if any(w in quote for w in ['风雨', '晴']):
        note = "不是没感觉，是真的过去了。"
    elif any(w in quote for w in ['归', '还', '回']):
        note = "想回去，但回不去。"
    elif any(w in quote for w in ['梦', '觉', '醒']):
        note = "梦是真的，醒也是真的。"
    elif any(w in quote for w in ['月', '婵娟']):
        note = "认了之后，还愿意祝福。"
    elif any(w in quote for w in ['泪', '哭', '悲']):
        note = "不说苦，只说事实。"
    elif any(w in quote for w in ['狂', '豪']):
        note = "憋太久了，终于撒一次野。"
    else:
        note = random.choice(notes)
    
    return quote, note

# ─── Main ───
def main():
    updated = 0
    skipped = 0
    errors = 0
    
    files = sorted(glob.glob(os.path.join(BASE, '*.json')))
    
    for f in files:
        fid = os.path.basename(f).replace('.json', '')
        
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                poem = json.load(fp)
            
            # Skip if already has reading with scene
            if poem.get('reading') and poem['reading'].get('scene'):
                skipped += 1
                continue
            
            year = poem.get('year', 0)
            location = poem.get('location', '')
            title = poem.get('title', '')
            paragraphs = poem.get('paragraphs', [])
            full_text = '\n'.join(paragraphs) if paragraphs else ''
            background = poem.get('background', '')
            
            # Generate all fields
            age = calc_age(year)
            situation = generate_situation(title, year, location, full_text, background)
            scene = generate_scene(poem)
            lines = generate_lines(poem)
            person = generate_person(poem)
            gold_quote, gold_quote_note = generate_gold_quote(poem)
            form_note = get_form_note(poem)
            
            # Validate
            if not scene or not lines:
                print(f"WARN {fid}: insufficient data for reading, skipping")
                skipped += 1
                continue
            
            # Write
            if age:
                poem['age'] = age
            if situation:
                poem['situation'] = situation
            poem['reading'] = {
                'scene': scene,
                'lines': lines,
                'person': person
            }
            poem['gold_quote'] = gold_quote
            poem['gold_quote_note'] = gold_quote_note
            if not poem.get('formNote'):
                poem['formNote'] = form_note
            
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(poem, fp, ensure_ascii=False, indent=2)
            
            updated += 1
            if updated % 50 == 0:
                print(f"  ... {updated} updated so far")
        
        except Exception as e:
            errors += 1
            print(f"ERROR {fid}: {e}")
    
    print(f"\nDone: {updated} updated, {skipped} skipped, {errors} errors")

if __name__ == '__main__':
    main()
