#!/usr/bin/env python3
"""为缺少全文的诗词补充内容"""
import json
from pathlib import Path

# 需要补充的诗词数据
POEMS_TO_ADD = {
    "W014": {
        "title": "江城子·密州出猎",
        "author": "苏轼",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": ["老夫聊发少年狂，左牵黄，右擎苍，锦帽貂裘，千骑卷平冈。为报倾城随太守，亲射虎，看孙郎。", "酒酣胸胆尚开张，鬓微霜，又何妨！持节云中，何日遣冯唐？会挽雕弓如满月，西北望，射天狼。"],
        "background": "熙宁八年（1075年），苏轼在密州任知州时所作。词中抒发了作者的爱国情怀和壮志豪情。",
        "famousQuotes": ["会挽雕弓如满月，西北望，射天狼。"]
    },
    "W031": {
        "title": "题西林壁",
        "author": "苏轼",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "庐山",
        "paragraphs": ["横看成岭侧成峰，远近高低各不同。不识庐山真面目，只缘身在此山中。"],
        "background": "元丰七年（1084年），苏轼由黄州贬所改迁汝州团练副使，途中游庐山时所作。这首诗蕴含深刻的哲理。",
        "famousQuotes": ["不识庐山真面目，只缘身在此山中。"]
    },
    "W029": {
        "title": "卜算子·黄州定慧院寓居作",
        "author": "苏轼",
        "type": "词",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": ["缺月挂疏桐，漏断人初静。谁见幽人独往来，缥缈孤鸿影。", "惊起却回头，有恨无人省。拣尽寒枝不肯栖，寂寞沙洲冷。"],
        "background": "元丰六年（1083年），苏轼在黄州贬所所作。词中借孤鸿自喻，表达了作者孤独寂寞的心境。",
        "famousQuotes": ["拣尽寒枝不肯栖，寂寞沙洲冷。"]
    },
    "W011": {
        "title": "有美堂暴雨",
        "author": "苏轼",
        "type": "诗",
        "year": 1089,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": ["游人脚底一声雷，满座顽云拨不开。天外黑风吹海立，浙东飞雨过江来。", "十分潋滟金尊凸，千杖敲铿羯鼓催。唤起谪仙泉洒面，倒倾鲛室泻琼瑰。"],
        "background": "元祐四年（1089年），苏轼任杭州知州时所作。描绘了暴雨来临的壮观景象。",
        "famousQuotes": ["天外黑风吹海立，浙东飞雨过江来。"]
    },
    "W056": {
        "title": "食荔枝",
        "author": "苏轼",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": ["罗浮山下四时春，卢橘杨梅次第新。日啖荔枝三百颗，不辞长作岭南人。"],
        "background": "绍圣元年（1094年），苏轼被贬惠州时所作。表达了作者随遇而安的乐观态度。",
        "famousQuotes": ["日啖荔枝三百颗，不辞长作岭南人。"]
    },
    "W067": {
        "title": "自题金山画像",
        "author": "苏轼",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": ["心似已灰之木，身如不系之舟。问汝平生功业，黄州惠州儋州。"],
        "background": "建中靖国元年（1101年），苏轼遇赦北归，途经金山寺，看到自己的画像时所作。这是他对自己一生的总结。",
        "famousQuotes": ["问汝平生功业，黄州惠州儋州。"]
    },
    "W046": {
        "title": "临江仙·送钱穆父",
        "author": "苏轼",
        "type": "词",
        "year": 1091,
        "route_id": "R15",
        "location": "杭州",
        "paragraphs": ["一别都门三改火，天涯踏尽红尘。依然一笑作春温。无波真古井，有节是秋筠。", "惆怅孤帆连夜发，送行淡月微云。尊前不用翠眉颦。人生如逆旅，我亦是行人。"],
        "background": "元祐六年（1091年），苏轼在杭州送别钱穆父时所作。表达了豁达的人生态度。",
        "famousQuotes": ["人生如逆旅，我亦是行人。"]
    },
    "W058": {
        "title": "纵笔三首",
        "author": "苏轼",
        "type": "诗",
        "year": 1097,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": ["寂寂东坡一病翁，白须萧散满霜风。小儿误喜朱颜在，一笑那知是酒红。", "父老争看乌角巾，应缘曾现宰官身。溪边古路三叉口，独立斜阳数过人。", "北船不到米如珠，醉饱萧条半月无。明日东家知祀灶，只鸡斗酒定膰吾。"],
        "background": "绍圣四年（1097年），苏轼被贬儋州时所作。描写了他在儋州的生活状况。",
        "famousQuotes": ["寂寂东坡一病翁，白须萧散满霜风。"]
    },
    "W002": {
        "title": "初发嘉州",
        "author": "苏轼",
        "type": "诗",
        "year": 1059,
        "route_id": "R02",
        "location": "嘉州",
        "paragraphs": ["朝发鼓阗阗，西风猎画旃。故乡飘已远，往意浩无边。", "锦水细不见，蛮江清可怜。奔腾过佛脚，旷荡造平川。", "野市有禅客，钓台寻暮烟。相期定先到，久立水潺潺。"],
        "background": "嘉祐四年（1059年），苏轼与苏辙随父苏洵出蜀赴京，途经嘉州（今四川乐山）时所作。",
        "famousQuotes": ["故乡飘已远，往意浩无边。"]
    },
    "W036": {
        "title": "蓬莱阁记所见",
        "author": "苏轼",
        "type": "诗",
        "year": 1085,
        "route_id": "R12",
        "location": "登州",
        "paragraphs": ["东方云海空复空，群仙出没空明中。荡摇浮世生万象，岂有贝阙藏珠宫。", "心知所见皆幻影，敢以耳目烦神工。岁寒水冷天地闭，为我起蛰鞭鱼龙。", "重楼翠阜出霜晓，异事惊倒百岁翁。人间所得容力取，世外无物谁为雄。", "率然有请不我拒，信我人厄非天穷。潮阳太守南迁归，喜见石廪堆祝融。", "自言正直动山鬼，岂知造物哀龙钟。伸眉一笑岂易得，神之报汝亦已丰。", "斜阳万里孤鸟没，但见碧海磨青铜。新诗绮语亦安用，相与变灭随东风。"],
        "background": "元丰八年（1085年），苏轼任登州知州时所作。描写了在蓬莱阁所见的壮丽景色。",
        "famousQuotes": ["东方云海空复空，群仙出没空明中。"]
    }
}

def main():
    poems_dir = Path("data-v4/poems")
    updated_count = 0
    
    for poem_id, poem_data in POEMS_TO_ADD.items():
        filepath = poems_dir / f"{poem_id}.json"
        
        if filepath.exists():
            # 如果文件已存在，读取并更新
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # 合并数据，优先保留已有的内容
            merged_data = {**poem_data, **existing_data}
            
            # 但强制更新 paragraphs 和相关字段
            merged_data['paragraphs'] = poem_data['paragraphs']
            merged_data['author'] = poem_data['author']
            if 'background' in poem_data:
                merged_data['background'] = poem_data['background']
            if 'famousQuotes' in poem_data:
                merged_data['famousQuotes'] = poem_data['famousQuotes']
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
        else:
            # 创建新文件
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
