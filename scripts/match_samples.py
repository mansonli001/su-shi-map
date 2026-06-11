#!/usr/bin/env python3
import json, os

poems_dir = 'public/data-v4/poems'
# 25 sample titles to match
samples = [
    "水调歌头·明月几时有",
    "念奴娇·赤壁怀古",
    "定风波·莫听穿林打叶声",
    "江城子·密州出猎",
    "题西林壁",
    "饮湖上初晴后雨",
    "赤壁赋",
    "后赤壁赋",
    "记承天寺夜游",
    "和子由渑池怀旧",
    "望江南·超然台作",
    "蝶恋花·春景",
    "六月二十七日望湖楼醉书",
    "惠崇春江晚景",
    "浣溪沙·游蕲水清泉寺",
    "水龙吟·次韵章质夫杨花词",
    "江城子·乙卯正月二十日夜记梦",
    "卜算子·黄州定慧院寓居作",
    "海棠",
    "行香子·述怀",
    "荔枝叹",
    "纵笔",
    "自题金山画像",
    "临江仙·夜归临皋",
    "洗儿诗",
]

for fname in sorted(os.listdir(poems_dir)):
    if not fname.endswith('.json'): continue
    pid = fname.replace('.json','')
    with open(os.path.join(poems_dir, fname)) as f:
        p = json.load(f)
    title = p.get('title','')
    for s in samples:
        # fuzzy match: check if sample key words appear in title
        if s in title or title in s:
            print(f"{pid}: {title}")
            break
        # also check partial match
        s_core = s.replace('·','').replace('（','').replace('）','').replace('·','')
        t_core = title.replace('·','').replace('（','').replace('）','').replace('·','')
        if s_core[:6] in t_core or t_core[:6] in s_core:
            print(f"{pid}: {title}  [partial match with {s}]")
            break
