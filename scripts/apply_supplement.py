#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补充数据(36篇)落库 + 全库去重重定向 + 优先排序 一体化脚本。
用法: python3 scripts/apply_supplement.py [--write]
不带 --write 为 dry-run，仅打印计划。
"""
import json, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public', 'data-v4')
SRC = os.path.join(ROOT, 'data-v4')
WRITE = '--write' in sys.argv

import opencc
_T2S = opencc.OpenCC('t2s')
def cn(s): return re.sub(r'[^\u4e00-\u9fff]', '', s or '')
def cns(s): return cn(_T2S.convert(s or ''))  # 转简体后只留汉字(用于繁简无关匹配)
def load(p): return json.load(open(p, encoding='utf-8'))

# ---------- 载入诗词文件与引用 ----------
poem_files = glob.glob(os.path.join(PUB, 'poems', '*.json'))
F = {os.path.basename(f)[:-5]: load(f) for f in poem_files}
def body(pid): return cns(''.join(F[pid].get('paragraphs') or []))  # 简体汉字串(繁简无关匹配)

ref_files = glob.glob(os.path.join(PUB,'routes','*.json'))+glob.glob(os.path.join(PUB,'places','*.json'))
refs = {}
for f in ref_files:
    txt = open(f, encoding='utf-8').read()
    for pid in re.findall(r'\b([CSFWZ]\d{3})\b', txt):
        refs.setdefault(pid, set()).add(f)
def nref(pid): return len(refs.get(pid, set()))

# ---------- 1. 精确正文重复组(去重用) ----------
from collections import defaultdict
groups = defaultdict(list)
for pid, d in F.items():
    n = re.sub(r'其[一二三四五六七八九十]+[：:]', '', ''.join(d.get('paragraphs') or []))
    n = cn(n)
    if len(n) >= 10:
        groups[n].append(pid)
dup_groups = [sorted(ids) for ids in groups.values() if len(ids) > 1]

# ---------- 2. 补充数据解析 ----------
md = open('/Users/mansonlee/Desktop/补充数据.MD', encoding='utf-8').read()
blocks = [b for b in md.split('\n---\n') if '《' in b]

def parse_block(b, canon_body):
    title = re.search(r'《(.+?)》', b).group(1).replace('（节选）','').replace('(节选)','')
    lines = [l.rstrip() for l in b.split('\n')]
    # meta + situation
    meta = next((l.strip() for l in lines if '苏轼' in l and '·' in l), '')
    age = ''
    if meta:
        parts = [x.strip() for x in meta.split('·')]
        if len(parts) >= 2: age = parts[1]
    # situation = meta 后第一段非空且非标题非《》
    situation = ''
    seen_meta = False
    for l in lines:
        s = l.strip()
        if not s: continue
        if s == meta: seen_meta = True; continue
        if seen_meta and not s.startswith('《') and s not in ('那时候','我觉得','这个人'):
            situation = s; break
    # 分节
    def section(name, nexts):
        out = []
        grab = False
        for l in lines:
            s = l.strip()
            if s == name: grab = True; continue
            if grab and (s in nexts or s.startswith('金句')): break
            if grab and s: out.append(s)
        return out
    scene_lines = section('那时候', ('我觉得','这个人'))
    feel_lines = section('我觉得', ('这个人',))
    person_lines = section('这个人', ())
    # person 去掉金句行
    person_lines = [l for l in person_lines if not l.startswith('金句')]
    scene = '\n'.join(scene_lines)
    person = '\n'.join(person_lines)
    # 我觉得 -> quote/explain：用正文判断 quote (繁简无关；支持省略号摘录)
    cb = canon_body  # 已是简体汉字串
    pairs = []
    for l in feel_lines:
        frag = re.split(r'……|\.{3,}|…', l)[0]   # 取省略号前一段做指纹
        cl = cns(frag)
        is_quote = len(cl) >= 4 and cl in cb
        if is_quote:
            pairs.append({'quote': l, 'explain': ''})
        else:
            if pairs:
                pairs[-1]['explain'] = (pairs[-1]['explain'] + ('\n' if pairs[-1]['explain'] else '') + l)
            # 无前导 quote 的句子忽略(极少)
    golds = re.findall(r'金句[:：]\s*(.+)', b)
    golds = [g.strip() for g in golds if g.strip()]
    gold_quote = '\n'.join(golds)
    return {'title':title,'age':age,'situation':situation,'scene':scene,
            'lines':pairs,'person':person,'gold_quote':gold_quote}

# ---------- 3. 补充数据 -> 权威ID 显式映射 ----------
# (经核实) 标题 -> (canonical_id 或 'NEW', 要设置的标题)
SUP_MAP = {
 '水调歌头·明月几时有': ('C012','水调歌头·明月几时有'),
 '念奴娇·赤壁怀古': ('C036','念奴娇·赤壁怀古'),
 '定风波·莫听穿林打叶声': ('C037','定风波·莫听穿林打叶声'),
 '江城子·乙卯正月二十日夜记梦': ('C004','江城子·乙卯正月二十日夜记梦'),
 '江城子·密州出猎': ('C002','江城子·密州出猎'),
 '题西林壁': ('S098','题西林壁'),
 '饮湖上初晴后雨': ('S036','饮湖上初晴后雨二首'),
 '赤壁赋': ('F002','赤壁赋'),
 '后赤壁赋': ('F005','后赤壁赋'),
 '记承天寺夜游': ('W009','记承天寺夜游'),
 '和子由渑池怀旧': ('S013','和子由渑池怀旧'),
 '卜算子·黄州定慧院寓居作': ('C074','卜算子·黄州定慧院寓居作'),
 '临江仙·夜归临皋': ('C039','临江仙·夜归临皋'),
 '浣溪沙·游蕲水清泉寺': ('C038','浣溪沙·游蕲水清泉寺'),
 '望江南·超然台作': ('NEW_WJN','望江南·超然台作'),
 '水龙吟·次韵章质夫杨花词': ('C048','水龙吟·次韵章质夫杨花词'),
 '蝶恋花·春景': ('C033','蝶恋花·春景'),
 '西江月·世事一场大梦': ('C035','西江月·世事一场大梦'),
 '满庭芳·蜗角虚名': ('C043','满庭芳·蜗角虚名'),
 '南乡子·重九涵辉楼呈徐君猷': ('C081','南乡子·重九涵辉楼呈徐君猷'),
 '行香子·述怀': ('C046','行香子·述怀'),
 '鹧鸪天·林断山明竹隐墙': ('C041','鹧鸪天·林断山明竹隐墙'),
 '六月二十七日望湖楼醉书': ('S022','六月二十七日望湖楼醉书五首'),
 '惠崇春江晚景': ('S114','惠崇春江晚景二首'),
 '东栏梨花': ('S075','东栏梨花'),
 '赠刘景文': ('S127','赠刘景文'),
 '春宵': ('S083','春宵'),
 '花影': ('S065','花影'),
 '自题金山画像': ('S164','自题金山画像'),
 '洗儿诗': ('S078','洗儿诗'),
 '初到黄州': ('S250','初到黄州'),
 '惠州一绝·食荔枝': ('S132','惠州一绝·食荔枝'),
 '汲江煎茶': ('NEW_JJ','汲江煎茶'),
 '澄迈驿通潮阁': ('S157','澄迈驿通潮阁二首'),
 '超然台记': ('W005','超然台记'),
 '答谢民师书': ('W220','答谢民师书'),
}
SKIP = {'纵笔·其一'}
# 新建诗词的权威正文
NEW_BODIES = {
 'NEW_WJN': {'id':'C200','type':'词','title':'望江南·超然台作','year':1076,
   'paragraphs':['春未老，风细柳斜斜。试上超然台上看，半壕春水一城花，烟雨暗千家。','寒食后，酒醒却咨嗟。休对故人思故国，且将新火试新茶。诗酒趁年华。']},
 'NEW_JJ': {'id':'S400','type':'诗','title':'汲江煎茶','year':1099,
   'paragraphs':['活水还须活火烹，自临钓石取深清。','大瓢贮月归春瓮，小杓分江入夜瓶。','雪乳已翻煎处脚，松风忽作泻时声。','枯肠未易禁三碗，坐听荒城长短更。']},
}

# ---------- 4. 计算去重(keep=max-ref) 与重定向 ----------
# 强制 keep: 补充数据 canonical id 必须是其组的 keep
force_keep = set()
for t,(cid,_) in SUP_MAP.items():
    if not cid.startswith('NEW'): force_keep.add(cid)

redirect = {}   # removed_id -> keep_id
keep_titles = {}  # keep_id -> 要设置的标题(若是补充数据)
removed = set()
for grp in dup_groups:
    fk = [g for g in grp if g in force_keep]
    if fk:
        keep = fk[0]
    else:
        keep = max(grp, key=lambda p:(nref(p), [-ord(c) for c in p]))
        # tie -> 较小id
        mx = max(nref(p) for p in grp)
        keep = sorted([p for p in grp if nref(p)==mx])[0]
    for g in grp:
        if g != keep:
            redirect[g] = keep
            removed.add(g)

# 标题映射: 补充数据 canonical -> 标题
for t,(cid,settitle) in SUP_MAP.items():
    if not cid.startswith('NEW'):
        keep_titles[cid] = settitle

# ---------- 5. 打印计划 ----------
print('=== A. 去重重定向计划 (removed -> keep) ===')
for r,k in sorted(redirect.items()):
    print(f'  {r}「{F[r].get("title")}」-> {k}「{F[k].get("title")}」 (引用{nref(r)}处需重定向)')
print(f'  去重: 删除 {len(removed)} 条, 保留组代表; 共 {len(dup_groups)} 组')

print('\n=== B. 36篇 解读落库计划 ===')
parsed_all={}
order=0
for b in blocks:
    title = re.search(r'《(.+?)》', b).group(1).replace('（节选）','').replace('(节选)','')
    if title in SKIP: continue
    if title not in SUP_MAP:
        print(f'  ⚠️ 未在映射表: {title}'); continue
    cid, settitle = SUP_MAP[title]
    if cid.startswith('NEW'):
        cb = cns(''.join(NEW_BODIES[cid]['paragraphs']))
    else:
        # canonical 若被并入(不会, force_keep保证), 取 cid 本身
        cb = body(cid)
    P = parse_block(b, cb)
    order += 1
    parsed_all[title]=(cid,settitle,P,order)
    qn=len(P['lines']); badq=[x['quote'] for x in P['lines'] if not x['explain']]
    print(f"  #{order:2d} {title} -> {cid} 标题『{settitle}』 age={P['age']} 现场{len(P['scene'])}字 人话{qn}组 这个人{len(P['person'])}字 金句={P['gold_quote'][:20]}")
    if badq: print(f'        ⚠️ 有quote无explain: {badq}')

print(f'\n  落库 {len(parsed_all)} 篇 | 跳过 {len(SKIP)} 篇')
print('\n=== C. 优先排序 ===')
print(f'  这 {len(parsed_all)} 篇 popularity_rank 按补充顺序 1..{len(parsed_all)}，其余保持原排序')
if not WRITE:
    print('\nDRY-RUN(未写入). 加 --write 执行。')
    sys.exit(0)

print('\n即将写入...')
from datetime import datetime
import glob as _glob

def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# ---------- W1. 36篇解读落库 (public) ----------
new_id_map = {'NEW_WJN': NEW_BODIES['NEW_WJN']['id'], 'NEW_JJ': NEW_BODIES['NEW_JJ']['id']}
rank_map = {}
for title,(cid,settitle,P,order) in parsed_all.items():
    if cid.startswith('NEW'):
        real = NEW_BODIES[cid]
        # 取一个同地点诗的 route_id
        d = {'id': real['id'], 'title': settitle, 'author': '苏轼', 'type': real['type'],
             'year': real['year'], 'paragraphs': real['paragraphs'],
             'age': P['age'], 'situation': P['situation'],
             'reading': {'scene': P['scene'], 'lines': P['lines'], 'person': P['person']},
             'gold_quote': P['gold_quote'], 'gold_quote_note': ''}
        rid = real['id']
        F[rid] = d
        rank_map[rid] = order
        write_json(os.path.join(PUB,'poems',f'{rid}.json'), d)
        print(f'  [新建] {rid} {settitle}')
    else:
        d = F[cid]
        d['title'] = settitle
        d['age'] = P['age']
        d['situation'] = P['situation']
        d['reading'] = {'scene': P['scene'], 'lines': P['lines'], 'person': P['person']}
        d['gold_quote'] = P['gold_quote']
        d['gold_quote_note'] = ''
        rank_map[cid] = order
        write_json(os.path.join(PUB,'poems',f'{cid}.json'), d)

# ---------- W2. 去重: 删除 removed 文件 + 引用重定向 ----------
# 删除 public/source removed 文件
for rid in removed:
    for base in (PUB, SRC):
        fp = os.path.join(base,'poems',f'{rid}.json')
        if os.path.exists(fp): os.remove(fp)
    F.pop(rid, None)

# 引用重定向: routes/places (public + source)，列表去重保序
def redirect_in_obj(o):
    if isinstance(o, list):
        seen=set(); out=[]
        for x in o:
            nx = redirect_in_obj(x)
            key = json.dumps(nx, ensure_ascii=False) if not isinstance(nx,str) else nx
            if isinstance(nx,str) and re.fullmatch(r'[CSFWZ]\d{3}', nx):
                if nx in seen: continue
                seen.add(nx)
            out.append(nx)
        return out
    if isinstance(o, dict):
        return {k: redirect_in_obj(v) for k,v in o.items()}
    if isinstance(o, str):
        return redirect.get(o, o)
    return o

changed_ref_files=0
for base in (PUB, SRC):
    for f in _glob.glob(os.path.join(base,'routes','*.json'))+_glob.glob(os.path.join(base,'places','*.json')):
        try: obj=load(f)
        except: continue
        new=redirect_in_obj(obj)
        if json.dumps(new,ensure_ascii=False)!=json.dumps(obj,ensure_ascii=False):
            write_json(f,new); changed_ref_files+=1
print(f'  去重: 删除 {len(removed)} 篇, 重定向引用文件 {changed_ref_files} 个')

# ---------- W3. popularity_rank: 36篇=1..N, 其余=999 ----------
for fp in _glob.glob(os.path.join(PUB,'poems','*.json')):
    pid=os.path.basename(fp)[:-5]
    d=load(fp)
    d['popularity_rank']=rank_map.get(pid,999)
    write_json(fp,d)

# ---------- W4. 同步 public/poems -> source/poems ----------
for fp in _glob.glob(os.path.join(PUB,'poems','*.json')):
    b=os.path.basename(fp)
    txt=open(fp,encoding='utf-8').read()
    sp=os.path.join(SRC,'poems',b)
    if (not os.path.exists(sp)) or open(sp,encoding='utf-8').read()!=txt:
        open(sp,'w',encoding='utf-8').write(txt)

# ---------- W5. 重建索引(public 文件) 写入 public + source ----------
old_idx={p['id']:p for p in load(os.path.join(PUB,'poems-index.json'))['poems']}
new_poems=[]; hft=0
for fp in sorted(_glob.glob(os.path.join(PUB,'poems','*.json'))):
    d=load(fp); pid=d['id'] if d.get('id') else os.path.basename(fp)[:-5]
    paras=d.get('paragraphs') or []; has=bool(paras)
    if has: hft+=1
    oe=old_idx.get(pid,{})
    rid=oe.get('route_id', d.get('route_id',''))
    rrel=[r for r in oe.get('related_route_ids',[rid] if rid else []) if r]
    cv=(d.get('famousQuotes') or [None])[0] or d.get('coreVerse') or oe.get('coreVerse','')
    new_poems.append({'id':pid,'title':d.get('title',''),'type':d.get('type',''),
        'year':d.get('year',0),'route_id':rid,'related_route_ids':rrel,
        'has_full_text':has,'popularity_rank':d.get('popularity_rank',999),'coreVerse':cv})
new_poems.sort(key=lambda x:x['id'])
idx={'total':len(new_poems),'has_full_text':hft,'pending_full_text':len(new_poems)-hft,
     'poems':new_poems,'generated_at':datetime.now().isoformat()}
out=json.dumps(idx,ensure_ascii=False,indent=2)
open(os.path.join(PUB,'poems-index.json'),'w',encoding='utf-8').write(out)
open(os.path.join(SRC,'poems-index.json'),'w',encoding='utf-8').write(out)
print(f'  索引重建: {len(new_poems)} 条 (含优先{len([p for p in new_poems if p["popularity_rank"]<900])}篇)')
print('完成。')
