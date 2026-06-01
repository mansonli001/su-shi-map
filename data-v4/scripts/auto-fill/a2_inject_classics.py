#!/usr/bin/env python3
"""
A2.2 苏轼名篇全文注入器（Python 版）
写入：public/data-v4/poems/{W_id}.json + 同步 internal data-v4/
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = ROOT / "public" / "data-v4"
INT = ROOT / "data-v4"

POEMS = {
    "W014": {
        "fullText": "老夫聊发少年狂，左牵黄，右擎苍，锦帽貂裘，千骑卷平冈。为报倾城随太守，亲射虎，看孙郎。\n酒酣胸胆尚开张。鬓微霜，又何妨。持节云中，何日遣冯唐。会挽雕弓如满月，西北望，射天狼。",
        "coreVerse": "会挽雕弓如满月，西北望，射天狼。",
        "background": "熙宁八年（1075）冬，苏轼时任密州知州，率众出猎所作。他以「老夫」自况开启豪放词派的雄迈一脉，借冯唐典故抒报国之志，是宋词从婉约转向豪放的标志性作品。",
    },
    "W015": {
        "fullText": "丙辰中秋，欢饮达旦，大醉，作此篇，兼怀子由。\n\n明月几时有，把酒问青天。不知天上宫阙，今夕是何年。我欲乘风归去，又恐琼楼玉宇，高处不胜寒。起舞弄清影，何似在人间。\n转朱阁，低绮户，照无眠。不应有恨，何事长向别时圆。人有悲欢离合，月有阴晴圆缺，此事古难全。但愿人长久，千里共婵娟。",
        "coreVerse": "但愿人长久，千里共婵娟。",
        "background": "熙宁九年（1076）中秋，苏轼时任密州知州，与弟苏辙已七年未见，欢饮大醉后写下此词。是中国词史上最广为传诵的中秋词，将兄弟之情、人生哲思与宇宙意识熔为一炉。",
    },
    "W027": {
        "fullText": "大江东去，浪淘尽，千古风流人物。故垒西边，人道是，三国周郎赤壁。乱石穿空，惊涛拍岸，卷起千堆雪。江山如画，一时多少豪杰。\n遥想公瑾当年，小乔初嫁了，雄姿英发。羽扇纶巾，谈笑间，樯橹灰飞烟灭。故国神游，多情应笑我，早生华发。人生如梦，一尊还酹江月。",
        "coreVerse": "大江东去，浪淘尽，千古风流人物。",
        "background": "元丰五年（1082）七月，苏轼贬居黄州第三年，与客游赤壁矶。彼时被贬已两年，面对大江与古迹，写下此词。被誉为宋词豪放派的代表作，「大江东去」四字奠定一代词风。",
    },
    "W028": {
        "fullText": "三月七日，沙湖道中遇雨。雨具先去，同行皆狼狈，余独不觉，已而遂晴，故作此词。\n\n莫听穿林打叶声，何妨吟啸且徐行。竹杖芒鞋轻胜马，谁怕？一蓑烟雨任平生。\n料峭春风吹酒醒，微冷，山头斜照却相迎。回首向来萧瑟处，归去，也无风雨也无晴。",
        "coreVerse": "回首向来萧瑟处，归去，也无风雨也无晴。",
        "background": "元丰五年（1082）三月，苏轼贬居黄州，于沙湖道中遇雨而作。一场途中骤雨，被东坡看作了人生的写照。「也无风雨也无晴」七字凝结了苏轼贬谪后的至高心境，是儒释道圆融的人生宣言。",
    },
    "W029": {
        "fullText": "缺月挂疏桐，漏断人初静。谁见幽人独往来，缥缈孤鸿影。\n惊起却回头，有恨无人省。拣尽寒枝不肯栖，寂寞沙洲冷。",
        "coreVerse": "拣尽寒枝不肯栖，寂寞沙洲冷。",
        "background": "元丰三年（1080）二月，苏轼初到黄州寓居定慧院（一作定惠院）东侧小屋。乌台诗案余惊未定，借孤鸿自喻，是黄州时期最早的代表作。「拣尽寒枝不肯栖」是对人格坚守的最深寄托。",
    },
    "W031": {
        "fullText": "横看成岭侧成峰，远近高低各不同。不识庐山真面目，只缘身在此山中。",
        "coreVerse": "不识庐山真面目，只缘身在此山中。",
        "background": "元丰七年（1084）四月，苏轼自黄州量移汝州途中漫游庐山，题于西林寺壁。短短四句二十八字成为中国哲理诗的巅峰，「不识庐山真面目」成为认知论的千古谚语。",
    },
    "W056": {
        "fullText": "罗浮山下四时春，卢橘杨梅次第新。日啖荔枝三百颗，不辞长作岭南人。",
        "coreVerse": "日啖荔枝三百颗，不辞长作岭南人。",
        "background": "绍圣三年（1096）四月，苏轼贬居惠州第三年，初食荔枝作此诗。岭南风物入诗，把贬谪苦境化作了对天地慷慨馈赠的礼赞，是苏轼晚年豁达心境的典型写照。",
    },
    "W058": {
        "fullText": "其一：白头萧散满霜风，小阁藤床寄病容。报道先生春睡美，道人轻打五更钟。\n其二：父老争看乌角巾，应缘曾现宰官身。溪边古路三叉口，独立斜阳数过人。\n其三：心如已灰之木，身如不系之舟。问汝平生功业，黄州惠州儋州。",
        "coreVerse": "报道先生春睡美，道人轻打五更钟。",
        "background": "绍圣四年（1097）春，苏轼贬居惠州。「报道先生春睡美」传至京城，引发政敌不满，成为他被再贬海南儋州的直接导火索之一——一首春睡之诗，竟把六十岁老人推向了万里南荒。",
    },
    "W065": {
        "fullText": "参横斗转欲三更，苦雨终风也解晴。云散月明谁点缀，天容海色本澄清。\n空余鲁叟乘桴意，粗识轩辕奏乐声。九死南荒吾不恨，兹游奇绝冠平生。",
        "coreVerse": "九死南荒吾不恨，兹游奇绝冠平生。",
        "background": "元符三年（1100）六月二十日，苏轼遇赦北归，自海南儋州渡琼州海峡。三年海岛贬谪生涯结束，写下此诗。「云散月明谁点缀」被誉为千古名句，把贬谪苦难化作了奇绝的生命体验。",
    },
    "W066": {
        "fullText": "其一：倦客愁闻归路遥，眼明飞阁俯长桥。贪看白鹭横秋浦，不觉青林没晚潮。\n其二：余生欲老海南村，帝遣巫阳招我魂。杳杳天低鹘没处，青山一发是中原。",
        "coreVerse": "杳杳天低鹘没处，青山一发是中原。",
        "background": "元符三年（1100）六月，苏轼北归途经澄迈通潮阁。「青山一发是中原」被誉为对故土最深的凝望——中原远在天边，仅是一发之青，却是六十五岁老人魂之所归。",
    },
    "W067": {
        "fullText": "心似已灰之木，身如不系之舟。问汝平生功业，黄州惠州儋州。",
        "coreVerse": "问汝平生功业，黄州惠州儋州。",
        "background": "建中靖国元年（1101）五月，苏轼北归途经润州金山寺，自题画像。两个月后即卒于常州。这二十八字是苏轼一生的自我盖棺定论——把世人眼中的三大贬谪之地，反过来认作了自己平生最大的功业。",
    },
}


def write_both(rel: str, data: dict):
    js = json.dumps(data, ensure_ascii=False, indent=2)
    for base in (PUB, INT):
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(js, encoding="utf-8")


def main():
    inj_count = 0
    for wid, payload in POEMS.items():
        path = PUB / "poems" / f"{wid}.json"
        if not path.exists():
            print(f"❌ {wid} 骨架不存在，跳过")
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        d["fullText"] = payload["fullText"]
        d["coreVerse"] = payload["coreVerse"]
        d["background"] = payload["background"]
        d["excerpt"] = payload["coreVerse"]
        d["has_full_text"] = True
        write_both(f"poems/{wid}.json", d)
        inj_count += 1
        print(f"✅ {wid} {d['title'][:30]} 全文已注入")

    # 更新索引
    idx_path = PUB / "poems-index.json"
    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    has_full = 0
    for p in idx["poems"]:
        if p["id"] in POEMS:
            p["has_full_text"] = True
            p["coreVerse"] = POEMS[p["id"]]["coreVerse"]
        if p.get("has_full_text"):
            has_full += 1
    idx["has_full_text"] = has_full
    idx["pending_full_text"] = idx["total"] - has_full
    write_both("poems-index.json", idx)

    print(f"\n📊 注入完成：{inj_count} 首名篇，索引已更新（{has_full}/{idx['total']} 有全文）")


if __name__ == "__main__":
    main()
