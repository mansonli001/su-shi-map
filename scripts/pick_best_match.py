#!/usr/bin/env python3
import json, os

poems_dir = 'public/data-v4/poems'

# Map sample -> best match ID (manually curated)
# Some have duplicates - pick the one with type=词 for ci, type=文 for fu/wen
matches = {
    "水调歌头·明月几时有": None,
    "念奴娇·赤壁怀古": None,
    "定风波·莫听穿林打叶声": None,
    "江城子·密州出猎": None,
    "题西林壁": None,
    "饮湖上初晴后雨": None,
    "赤壁赋": None,
    "后赤壁赋": None,
    "记承天寺夜游": None,
    "和子由渑池怀旧": None,
    "望江南·超然台作": None,
    "蝶恋花·春景": None,
    "六月二十七日望湖楼醉书": None,
    "惠崇春江晚景": None,
    "浣溪沙·游蕲水清泉寺": None,
    "水龙吟·次韵章质夫杨花词": None,
    "江城子·乙卯正月二十日夜记梦": None,
    "卜算子·黄州定慧院寓居作": None,
    "海棠": None,
    "行香子·述怀": None,
    "荔枝叹": None,
    "纵笔": None,
    "自题金山画像": None,
    "临江仙·夜归临皋": None,
    "洗儿诗": None,
}

# Candidate IDs from match
candidates = {
    "水调歌头·明月几时有": ["C012", "C013"],
    "念奴娇·赤壁怀古": ["C036"],
    "定风波·莫听穿林打叶声": ["C037"],
    "江城子·密州出猎": ["C002", "C005"],
    "题西林壁": ["S098", "S102", "S103"],
    "饮湖上初晴后雨": ["S021", "S036", "S038"],
    "赤壁赋": ["F002", "F004"],
    "后赤壁赋": ["F003", "F005"],
    "记承天寺夜游": ["W009"],
    "和子由渑池怀旧": ["S013"],
    "望江南·超然台作": [],
    "蝶恋花·春景": ["C033"],
    "六月二十七日望湖楼醉书": ["S017", "S022", "S023"],
    "惠崇春江晚景": ["S114"],
    "浣溪沙·游蕲水清泉寺": ["C038", "S292"],
    "水龙吟·次韵章质夫杨花词": ["C008", "C048"],
    "江城子·乙卯正月二十日夜记梦": ["C003", "C004"],
    "卜算子·黄州定慧院寓居作": ["C074"],
    "海棠": ["S080"],
    "行香子·述怀": ["C046"],
    "荔枝叹": ["S142"],
    "纵笔": ["S150"],
    "自题金山画像": ["S164"],
    "临江仙·夜归临皋": [],
    "洗儿诗": ["S078"],
}

# For each candidate, check type and pick best
for title, ids in candidates.items():
    if not ids:
        print(f"NO MATCH: {title}")
        continue
    best = None
    for pid in ids:
        fpath = os.path.join(poems_dir, f"{pid}.json")
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            p = json.load(f)
        ptype = p.get('type','')
        # Prefer exact type match
        if title in ["赤壁赋", "后赤壁赋", "记承天寺夜游"]:
            if ptype == '文':
                best = pid
                break
        elif '·' in title:  # ci
            if ptype == '词':
                best = pid
                break
        else:
            if ptype == '诗':
                best = pid
                break
        best = pid  # fallback
    print(f"{title}: {best}")
