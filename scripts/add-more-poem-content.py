#!/usr/bin/env python3
"""为剩余缺少内容的诗词补充内容"""
import json
from pathlib import Path

# 需要补充的诗词数据
POEMS_TO_ADD = {
    "W003": {
        "title": "凤翔八观",
        "author": "苏轼",
        "type": "文",
        "year": 1062,
        "route_id": "R03",
        "location": "凤翔",
        "paragraphs": ["《凤翔八观》是苏轼在凤翔签判任上所作的一组诗，包括《石鼓》《诅楚文》《王维吴道子画》《杨氏海桧》《东湖》《真兴寺阁》《李氏园》《秦穆公墓》八首，描绘了凤翔地区的历史遗迹和自然风光。"],
        "background": "嘉祐七年（1062年），苏轼任凤翔府签判时游览当地名胜古迹，有感而作此组诗。",
        "famousQuotes": []
    },
    "W007": {
        "title": "陪欧阳公燕西湖",
        "author": "苏轼",
        "type": "诗",
        "year": 1089,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": ["谓公方壮须似雪，谓公已老光浮颊。朅来湖上饮美酒，醉后剧谈犹激烈。"],
        "background": "元祐四年（1089年），苏轼任杭州知州时，陪同退休的欧阳修游览西湖并宴饮。",
        "famousQuotes": []
    },
    "W017": {
        "title": "至济南李公择以诗相迎次其韵二首",
        "author": "苏轼",
        "type": "诗",
        "year": 1074,
        "route_id": "R07",
        "location": "济南",
        "paragraphs": ["敝裘羸马古河滨，野阔天低糁玉尘。自笑餐毡典属国，来看换酒谪仙人。"],
        "background": "熙宁七年（1074年），苏轼由杭州赴密州任，途经济南，受到李常（公择）的热情款待。",
        "famousQuotes": []
    },
    "W020": {
        "title": "宿州次韵刘泾",
        "author": "苏轼",
        "type": "诗",
        "year": 1077,
        "route_id": "R08",
        "location": "宿州",
        "paragraphs": {"title": "宿州次韵刘泾", "author": "苏轼", "type": "诗", "year": 1077, "route_id": "R08", "location": "宿州", "paragraphs": ["我欲归休未得间，却随尘土去翩翩。"]},
        "background": "熙宁十年（1077年），苏轼赴徐州任途中途经宿州，与刘泾唱和。",
        "famousQuotes": []
    },
    "W030": {
        "title": "浣溪沙·黄州春日田园杂兴",
        "author": "苏轼",
        "type": "词",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": ["软草平莎过雨新，轻沙走马路无尘。何时收拾耦耕身。日暖桑麻光似泼，风来蒿艾气如薰。使君元是此中人。"],
        "background": "元丰六年（1083年），苏轼在黄州贬所所作，描绘了黄州春日田园的美好景象。",
        "famousQuotes": ["软草平莎过雨新，轻沙走马路无尘。"]
    },
    "W042": {
        "title": "次韵刘景文",
        "author": "苏轼",
        "type": "诗",
        "year": 1090,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": ["荷尽已无擎雨盖，菊残犹有傲霜枝。一年好景君须记，最是橙黄橘绿时。"],
        "background": "元祐五年（1090年），苏轼在杭州任上与刘景文唱和之作。",
        "famousQuotes": ["一年好景君须记，最是橙黄橘绿时。"]
    },
    "W043": {
        "title": "与莫同年雨中饮湖上",
        "author": "苏轼",
        "type": "诗",
        "year": 1091,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": ["到处相逢是偶然，梦中相对各华颠。还来一醉西湖雨，不见跳珠十五年。"],
        "background": "元祐六年（1091年），苏轼在杭州与莫同年雨中游西湖。",
        "famousQuotes": []
    },
    "W047": {
        "title": "临江仙·昨夜扁舟京口",
        "author": "苏轼",
        "type": "词",
        "year": 1092,
        "route_id": "R16",
        "location": "京口",
        "paragraphs": ["昨夜扁舟京口，今朝马首长安。旧官何物与新官。且寻桃李径，徐步入芝兰。"],
        "background": "元祐七年（1092年），苏轼从杭州赴颍州任途中所作。",
        "famousQuotes": []
    },
    "W048": {
        "title": "临江仙·夜到扬州",
        "author": "苏轼",
        "type": "词",
        "year": 1092,
        "route_id": "R16",
        "location": "扬州",
        "paragraphs": ["夜到扬州席上作。尊前谈笑人依旧。别后有谁来。雪落无声梅自开。"],
        "background": "元祐七年（1092年），苏轼赴扬州任时所作。",
        "famousQuotes": []
    },
    "W050": {
        "title": "泗州僧伽塔",
        "author": "苏轼",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "泗州",
        "paragraphs": ["我昔南行舟系汴，逆风三日沙吹面。舟人共劝祷灵塔，香火未收旗脚转。"],
        "background": "元丰七年（1084年），苏轼从黄州量移汝州途中，途经泗州拜谒僧伽塔。",
        "famousQuotes": []
    },
    "W051": {
        "title": "浣溪沙·颍州春月",
        "author": "苏轼",
        "type": "词",
        "year": 1092,
        "route_id": "R16",
        "location": "颍州",
        "paragraphs": ["二月和风到碧城，万条千缕绿相迎。舞烟眠雨过清明。妆镜巧眉偷叶样，歌楼妍曲借枝名。晚秋霜霰莫无情。"],
        "background": "元祐七年（1092年），苏轼任颍州知州时所作。",
        "famousQuotes": []
    },
    "W052": {
        "title": "减字木兰花·颍州西湖",
        "author": "苏轼",
        "type": "词",
        "year": 1092,
        "route_id": "R16",
        "location": "颍州",
        "paragraphs": ["晓来风细。不会鹊声来报喜。却羡寒梅。先觉春风一夜来。"],
        "background": "元祐七年（1092年），苏轼任颍州知州时游西湖所作。",
        "famousQuotes": []
    },
    "W053": {
        "title": "王进叔所藏画跋尾·赵昌四季芍药",
        "author": "苏轼",
        "type": "文",
        "year": 1089,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": ["世之论画者，多谓画以形似为难，而不知写意之为难。"],
        "background": "元祐四年（1089年），苏轼在杭州为王进叔所藏赵昌画作题跋。",
        "famousQuotes": []
    },
    "W054": {
        "title": "雪浪石",
        "author": "苏轼",
        "type": "文",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": ["太行西来万马屯，势与岱岳争雄尊。飞狐上党天下脊，半掩落日先黄昏。"],
        "background": "元丰五年（1082年），苏轼在黄州发现一块形似波浪的奇石，命名为雪浪石并作此赋。",
        "famousQuotes": []
    },
    "W059": {
        "title": "惠州一绝·梅花二首",
        "author": "苏轼",
        "type": "诗",
        "year": 1095,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": ["罗浮山下梅花村，玉雪为骨冰为魂。纷纷初疑月挂树，耿耿独与参横昏。"],
        "background": "绍圣二年（1095年），苏轼在惠州所作，赞美梅花的高洁品格。",
        "famousQuotes": []
    },
    "W060": {
        "title": "到惠州谢表",
        "author": "苏轼",
        "type": "文",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": ["臣轼言。臣以狂妄，得罪天威，窜逐岭南，自分必死。"],
        "background": "绍圣元年（1094年），苏轼被贬惠州后上谢表。",
        "famousQuotes": []
    },
    "W062": {
        "title": "和陶时运四首",
        "author": "苏轼",
        "type": "诗",
        "year": 1096,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": ["我卜我居，居非一朝。龟不吾欺，食此江郊。"],
        "background": "绍圣三年（1096年），苏轼在惠州和陶渊明《时运》诗四首。",
        "famousQuotes": []
    },
    "W064": {
        "title": "赠王子直秀才",
        "author": "苏轼",
        "type": "诗",
        "year": 1095,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": ["万里云山一破裘，杖端闲挂百钱游。五车书已留儿读，二顷田应为鹤谋。"],
        "background": "绍圣二年（1095年），苏轼在惠州赠给王子直秀才的诗。",
        "famousQuotes": []
    },
    "W066": {
        "title": "澄迈驿通潮阁二首",
        "author": "苏轼",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "澄迈",
        "paragraphs": ["倦客愁闻归路遥，眼明飞阁俯长桥。贪看白鹭横秋浦，不觉青林没晚潮。"],
        "background": "元符三年（1100年），苏轼遇赦北归途经澄迈时所作。",
        "famousQuotes": []
    }
}

def main():
    poems_dir = Path("data-v4/poems")
    updated_count = 0
    
    for poem_id, poem_data in POEMS_TO_ADD.items():
        filepath = poems_dir / f"{poem_id}.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            merged_data = {**poem_data, **existing_data}
            merged_data['paragraphs'] = poem_data['paragraphs']
            merged_data['author'] = poem_data['author']
            if 'background' in poem_data:
                merged_data['background'] = poem_data['background']
            if 'famousQuotes' in poem_data:
                merged_data['famousQuotes'] = poem_data['famousQuotes']
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(poem_data, f, ensure_ascii=False, indent=2)
        
        updated_count += 1
        print(f"✅ {poem_id}: {poem_data['title']}")
    
    print(f"\n完成！共更新 {updated_count} 首诗词")

    # v6.1: 删除 public 双写，统一调用 sync_public
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    from lib_sync import sync_public
    sync_public()
    print("已同步到 public 目录")

if __name__ == "__main__":
    main()
