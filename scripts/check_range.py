#!/usr/bin/env python3
import json, os

poems_dir = 'public/data-v4/poems'
missing = []
template = []
TEMPLATE_PHRASES = [
    '他写的是风景，但说的不是风景',
    '表面是一句普通的话，里面藏着他当时真正的心思',
    '他对自然的感知力极强',
    '这句话听起来简单，但仔细想想',
    '正处于人生的某个节点',
    '他总是能在任何处境下找到值得写下来的东西',
    '他不是在诉苦，他只是在描述一个状态',
    '但这个状态本身，比任何诉苦都让人难受',
]

for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    if not pid.startswith('S'): continue
    num = int(pid[1:])
    if num < 95 or num > 181: continue
    with open(os.path.join(poems_dir, fname)) as f:
        p = json.load(f)
    if p.get('type','') not in ('诗','词'): continue
    reading = p.get('reading')
    if not reading:
        missing.append(pid)
    else:
        is_template = False
        for line in reading.get('lines', []):
            explain = line.get('explain', '')
            for tp in TEMPLATE_PHRASES:
                if tp in explain:
                    is_template = True; break
            if is_template: break
        person = reading.get('person', '')
        for tp in TEMPLATE_PHRASES:
            if tp in person:
                is_template = True; break
        if is_template:
            template.append(pid)

print(f'缺失深度读: {len(missing)}')
print(','.join(missing))
print(f'模板化深度读: {len(template)}')
print(','.join(template))
