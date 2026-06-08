#!/usr/bin/env python3
"""
阶段1：87个完全空白地点数据补充
从行踪考提取信息并改写，补充 global_events + background
"""
import json, os, copy
from collections import defaultdict

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 87个空白地点的补充数据（按路线从行踪考提取并改写）
# 格式：place_id -> { global_events, background_enhanced }
SUPPLEMENTS = {
    # ── R00 眉山故里 ──
    "P130": {
        "background": "彭山江口，岷江与府河交汇之处，水势平缓、舟楫云集。少年苏轼随父兄自眉山顺岷江北上，经此入蜀水路要冲，两岸青山夹江、古渡繁忙，是出蜀入京的起点水门。",
        "global_events": [
            {"id": "p130-001", "date": "1056年", "title": "出蜀北上经江口", "description": "苏轼随父苏洵携弟苏辙自眉山出发，经彭山江口入岷江主流，开启首次进京赶考之旅", "significance": "出蜀起点"}
        ]
    },

    # ── R01 首次进京 ──
    "P043": {
        "background": "凤县地处秦岭西段南麓，自古为蜀道要冲。苏轼首次进京经此，山势渐陡、栈道蜿蜒，北望秦岭云横、南顾蜀道盘旋，是出蜀入关中的咽喉之地。",
        "global_events": [
            {"id": "p043-001", "date": "1056年", "title": "经凤县入秦岭", "description": "苏轼随父经凤县入秦岭栈道，初历蜀道之险", "significance": "初历蜀道"}
        ]
    },
    "P046": {
        "background": "扶风为周原故地、法门寺所在，关中平原西端重镇。苏轼进京途经此邑，平原沃野、周秦遗风，法门寺塔影遥遥可见，是自蜀入关中后首见中原气象之地。",
        "global_events": [
            {"id": "p046-001", "date": "1056年", "title": "经扶风入关中", "description": "苏轼出秦岭后经扶风，初见关中平原广袤气象", "significance": "初入中原"}
        ]
    },
    "P113": {
        "background": "洛阳为九朝古都、天下之中，伊洛二水汇流其间。苏轼多次途经洛阳，牡丹盛名甲天下、龙门石窟临伊水，每过此城皆叹历史兴亡、人文荟萃。",
        "global_events": [
            {"id": "p113-001", "date": "1056年", "title": "首次途经洛阳", "description": "苏轼首次进京途经洛阳，观古都气象", "significance": "初识中原文化"},
            {"id": "p113-002", "date": "1061年", "title": "二次途经洛阳", "description": "苏轼赴凤翔任途经洛阳", "significance": "再经古都"}
        ]
    },
    "P121": {
        "background": "绵州位于涪江中游、蜀道要冲，李白故里。苏轼出蜀北上必经此州，涪江两岸丘陵起伏、竹林掩映，是蜀中通往关中的中继站。",
        "global_events": [
            {"id": "p121-001", "date": "1056年", "title": "经绵州北上", "description": "苏轼随父自眉山出发经绵州，沿蜀道北上赴京", "significance": "出蜀中继"}
        ]
    },
    "P122": {
        "background": "勉县为汉中盆地西端、定军山所在，三国蜀汉故地。苏轼经此入蜀道，武侯墓祠在望、汉水悠悠，是自蜀入秦的门户。",
        "global_events": [
            {"id": "p122-001", "date": "1056年", "title": "经勉县入栈道", "description": "苏轼经勉县入金牛道栈道，穿越秦岭", "significance": "入栈道起点"}
        ]
    },
    "P128": {
        "background": "宁强位于汉江源头、秦蜀交界，金牛道要冲。苏轼经此穿越秦岭，山高谷深、栈道悬壁，是蜀道最险峻的路段之一。",
        "global_events": [
            {"id": "p128-001", "date": "1056年", "title": "经宁强穿越秦岭", "description": "苏轼经宁强入秦岭深处，栈道险峻", "significance": "蜀道险段"}
        ]
    },
    "P151": {
        "background": "陕州即今三门峡，黄河中游要津、崤函古道所在。苏轼多次途经陕州，黄河浊浪东去、函谷关雄峙，是自关中入中原的咽喉。",
        "global_events": [
            {"id": "p151-001", "date": "1056年", "title": "经陕州入中原", "description": "苏轼出关中经陕州函谷关，进入中原大地", "significance": "入中原门户"}
        ]
    },
    "P152": {
        "background": "陕州硖石为崤山峡谷要隘，古道穿石壁而过。苏轼途经此峡，两岸石壁如削、古道幽深，是崤函古道最险要的路段。",
        "global_events": [
            {"id": "p152-001", "date": "1056年", "title": "过硖石险隘", "description": "苏轼经陕州硖石峡谷，穿越崤函古道险段", "significance": "崤函险隘"}
        ]
    },
    "P171": {
        "background": "潼关为关中门户、黄河渭河交汇之处，自古兵家必争。苏轼多次出入潼关，北望黄河、南倚华山，是关中与中原的分界。",
        "global_events": [
            {"id": "p171-001", "date": "1056年", "title": "首次出潼关", "description": "苏轼首次经潼关出关中，入中原赴京", "significance": "出关中门户"},
            {"id": "p171-002", "date": "1061年", "title": "再经潼关", "description": "苏轼赴凤翔任经潼关入关中", "significance": "入关中"}
        ]
    },
    "P172": {
        "background": "潼关渡口为黄河古渡，连接秦晋两岸。苏轼渡黄河经此，河面宽阔、浊浪翻涌，渡船在急流中穿行，是出关入晋的水路要津。",
        "global_events": [
            {"id": "p172-001", "date": "1056年", "title": "渡黄河潼关渡口", "description": "苏轼在潼关渡口渡黄河，感受大河奔涌之势", "significance": "渡河要津"}
        ]
    },
    "P189": {
        "background": "崤山二陵为崤山古道最险处，晋秦争霸古战场。苏轼途经此段，山势陡峭、古道盘旋，两壁夹峙如门，是中原通往关中的天险。",
        "global_events": [
            {"id": "p189-001", "date": "1056年", "title": "过崤山二陵", "description": "苏轼穿越崤山二陵天险，感受古道之险", "significance": "崤函天险"}
        ]
    },
    "P234": {
        "background": "梓潼位于蜀道金牛道上、七曲山大庙所在。苏轼出蜀经此，翠云廊古柏夹道、文昌帝君祖庭在望，是蜀道文化积淀最深厚的一段。",
        "global_events": [
            {"id": "p234-001", "date": "1056年", "title": "经梓潼翠云廊", "description": "苏轼经梓潼七曲山，观古柏长廊", "significance": "蜀道文化"}
        ]
    },

    # ── R02 岷江长江出蜀 ──
    "P093": {
        "background": "夔门三峡为长江三峡西入口，瞿塘峡两岸绝壁对峙、江水奔涌如雷。苏轼出蜀顺流而下经此，夔门天下雄、赤甲白盐两山夹江，是蜀中与中原的水路分界。",
        "global_events": [
            {"id": "p093-001", "date": "1059年", "title": "出蜀过夔门", "description": "苏轼随父携弟顺岷江入长江，经夔门三峡出蜀，感受长江雄险", "significance": "出蜀水路门户"}
        ]
    },
    "P094": {
        "background": "夔州即今奉节，为三峡起点、蜀中门户。苏轼出蜀经此，白帝城高踞山头、瞿塘峡口雄关在望，是入三峡的第一大邑。",
        "global_events": [
            {"id": "p094-001", "date": "1059年", "title": "经夔州入三峡", "description": "苏轼经夔州白帝城，入瞿塘峡顺流东下", "significance": "三峡起点"},
            {"id": "p094-002", "date": "1066年", "title": "扶柩返蜀经夔州", "description": "苏轼扶父丧自汴京溯江而上经夔州返蜀", "significance": "扶柩归途"}
        ]
    },
    "P111": {
        "background": "泸州位于沱江汇入长江之处，蜀南重镇、酒乡名邑。苏轼出蜀顺流经此，两江交汇、舟楫如织，是岷江入长江后的第一重镇。",
        "global_events": [
            {"id": "p111-001", "date": "1059年", "title": "经泸州顺流东下", "description": "苏轼出蜀经泸州，沿长江东下赴京", "significance": "长江中继"}
        ]
    },
    "P175": {
        "background": "巫山为巫峡所在、神女峰闻名天下。苏轼出蜀经此，巫峡云雨迷蒙、十二峰若隐若现，是三峡中最幽深秀美的一段。",
        "global_events": [
            {"id": "p175-001", "date": "1059年", "title": "过巫峡巫山", "description": "苏轼经巫山巫峡，观神女峰云雨", "significance": "巫峡胜景"}
        ]
    },
    "P204": {
        "background": "宜宾为岷江汇入长江之处，蜀南门户、万里长江第一城。苏轼出蜀经此，岷江清流与长江浊浪交汇，是水路出蜀的关键节点。",
        "global_events": [
            {"id": "p204-001", "date": "1059年", "title": "经宜宾入长江", "description": "苏轼自眉山顺岷江至宜宾，转入长江东下", "significance": "岷江入长江口"}
        ]
    },
    "P211": {
        "background": "渝州即今重庆，嘉陵江与长江交汇之处，山城雄踞。苏轼出蜀经此，两江环抱、山城层叠，是长江上游最大都会。",
        "global_events": [
            {"id": "p211-001", "date": "1059年", "title": "经渝州东下", "description": "苏轼经渝州沿长江东下出蜀", "significance": "山城中继"}
        ]
    },
    "P225": {
        "background": "长江沿岸渡口为三峡水路要津，两岸渡船往来、纤夫号子回荡。苏轼出蜀经此，渡口繁忙、江风猎猎，是水路行旅的日常景象。",
        "global_events": [
            {"id": "p225-001", "date": "1059年", "title": "经长江沿岸渡口", "description": "苏轼沿长江东下，经沿岸各渡口", "significance": "水路行旅"}
        ]
    },
    "P230": {
        "background": "忠州位于长江北岸、石宝寨所在。苏轼出蜀经此，江岸峭壁、石寨凌空，是三峡水路的中继要邑。",
        "global_events": [
            {"id": "p230-001", "date": "1059年", "title": "经忠州东下", "description": "苏轼经忠州沿长江东下", "significance": "三峡中继"}
        ]
    },
    "P233": {
        "background": "秭归为屈原故里、西陵峡所在。苏轼出蜀经此，屈原祠临江而立、峡江风光壮美，是三峡东段的起点。",
        "global_events": [
            {"id": "p233-001", "date": "1059年", "title": "经秭归出三峡", "description": "苏轼经秭归屈原故里，出西陵峡入江汉平原", "significance": "出三峡门户"}
        ]
    },

    # ── R03 二次进京·赴凤翔 ──
    "P037": {
        "background": "邓州位于南阳盆地、范仲淹曾知此州。苏轼赴凤翔途经此邑，盆地沃野、汉水支流蜿蜒，是中原通往关中的南道要冲。",
        "global_events": [
            {"id": "p037-001", "date": "1061年", "title": "经邓州赴凤翔", "description": "苏轼赴凤翔签判任途经邓州", "significance": "赴任途经"}
        ]
    },
    "P067": {
        "background": "华山为五岳之西岳、天下险绝。苏轼途经华阴远眺华山，莲花峰、落雁峰云遮雾绕，虽未登临亦叹其雄奇。",
        "global_events": [
            {"id": "p067-001", "date": "1061年", "title": "远眺华山", "description": "苏轼经华阴远眺西岳华山，叹其雄险", "significance": "西岳远眺"}
        ]
    },
    "P163": {
        "background": "太白山为秦岭主峰、关中名山。苏轼赴凤翔途经太白山麓，积雪皑皑、山势巍峨，是关中平原的天然屏障。",
        "global_events": [
            {"id": "p163-001", "date": "1061年", "title": "经太白山麓", "description": "苏轼赴凤翔途经太白山麓，远望秦岭主峰", "significance": "秦岭主峰"}
        ]
    },
    "P169": {
        "background": "唐州位于南阳盆地东北、淮河上游。苏轼赴凤翔途经此州，丘陵起伏、淮水源头，是中原通往荆襄的通道。",
        "global_events": [
            {"id": "p169-001", "date": "1061年", "title": "经唐州赴任", "description": "苏轼赴凤翔途经唐州", "significance": "赴任途经"}
        ]
    },
    "P174": {
        "background": "尉氏为开封府属县、中原腹地。苏轼赴凤翔经此，平原广袤、驿道笔直，是汴京西出的首站。",
        "global_events": [
            {"id": "p174-001", "date": "1061年", "title": "经尉氏西行", "description": "苏轼自汴京出发经尉氏西行赴凤翔", "significance": "京西首站"}
        ]
    },
    "P186": {
        "background": "襄城位于许州之西、伏牛山余脉东麓。苏轼赴凤翔经此，丘陵与平原交汇、古道通衢，是中原西行的中继站。",
        "global_events": [
            {"id": "p186-001", "date": "1061年", "title": "经襄城西行", "description": "苏轼经襄城西行赴凤翔", "significance": "西行中继"}
        ]
    },
    "P187": {
        "background": "襄阳为汉水中游重镇、南北通衢。苏轼赴凤翔途经襄阳，汉水穿城、岘山在望，是荆楚通往关中的要道。",
        "global_events": [
            {"id": "p187-001", "date": "1061年", "title": "经襄阳入关中道", "description": "苏轼经襄阳沿汉水北上入关中", "significance": "南北通衢"}
        ]
    },
    "P190": {
        "background": "崤山古道为中原通往关中的天险要道，山高谷深、古道盘旋。苏轼赴凤翔经此，崤函险峻、行旅艰难，是关中与中原的分界。",
        "global_events": [
            {"id": "p190-001", "date": "1061年", "title": "过崤山古道", "description": "苏轼穿越崤山古道入关中赴凤翔", "significance": "崤函天险"}
        ]
    },
    "P197": {
        "background": "许州即今许昌、中原腹地。苏轼赴凤翔经此，平原沃野、曹魏故都遗风犹存，是汴京西行的必经之地。",
        "global_events": [
            {"id": "p197-001", "date": "1061年", "title": "经许州西行", "description": "苏轼经许州西行赴凤翔", "significance": "中原中继"}
        ]
    },
    "P201": {
        "background": "叶县位于伏牛山东麓、南阳盆地北缘。苏轼赴凤翔经此，丘陵起伏、古道蜿蜒，是中原通往荆襄的通道。",
        "global_events": [
            {"id": "p201-001", "date": "1061年", "title": "经叶县南下", "description": "苏轼经叶县南下赴凤翔", "significance": "赴任途经"}
        ]
    },

    # ── R04 扶柩归蜀 ──
    "P007": {
        "background": "汴河漕运古道为北宋南北水路大动脉，自汴京东通淮泗。苏轼扶父丧沿汴河乘船南下，两岸柳堤、漕船如织，是归蜀水路的第一段。",
        "global_events": [
            {"id": "p007-001", "date": "1066年", "title": "沿汴河南下", "description": "苏轼扶父丧自汴京沿汴河水路南下归蜀", "significance": "扶柩水路起点"}
        ]
    },
    "P071": {
        "background": "淮水中游为南北水路要津，苏轼扶柩经此，河面宽阔、渡船往来，是汴河入长江的中转水道。",
        "global_events": [
            {"id": "p071-001", "date": "1066年", "title": "渡淮水南行", "description": "苏轼扶柩渡淮水沿长江溯流归蜀", "significance": "南北水路中转"}
        ]
    },
    "P149": {
        "background": "三峡全程为长江最险峻河段，瞿塘雄、巫峡秀、西陵险。苏轼扶柩溯江而上经三峡全段，逆水行舟、纤夫拉纤，归蜀之路艰辛漫长。",
        "global_events": [
            {"id": "p149-001", "date": "1066年", "title": "溯江过三峡归蜀", "description": "苏轼扶柩溯长江过三峡全段归蜀，逆水行舟艰辛异常", "significance": "归蜀险途"}
        ]
    },
    "P222": {
        "background": "长江中游为荆楚水路要道，江面宽阔、支流纵横。苏轼扶柩溯江经此，大江东去、舟行逆水，是归蜀水路的中段。",
        "global_events": [
            {"id": "p222-001", "date": "1066年", "title": "溯长江中游西行", "description": "苏轼扶柩溯长江中游西行归蜀", "significance": "归蜀水路中段"}
        ]
    },

    # ── R05 守丧毕再赴京 ──
    "P057": {
        "background": "汉中栈道为蜀道精华，悬壁凿孔、栈木横空。苏轼守丧毕再赴京经此，栈道凌空、下临深谷，是蜀道最惊心动魄的路段。",
        "global_events": [
            {"id": "p057-001", "date": "1069年", "title": "经汉中栈道出蜀", "description": "苏轼守丧毕经汉中栈道出蜀赴京", "significance": "蜀道险段"}
        ]
    },
    "P137": {
        "background": "秦岭古驿为蜀道关中段要冲，驿站相连、驿道盘旋。苏轼出蜀经此，秦岭云横、驿马嘶风，是出蜀入关中的必经驿站。",
        "global_events": [
            {"id": "p137-001", "date": "1069年", "title": "经秦岭古驿入关中", "description": "苏轼经秦岭古驿出蜀入关中", "significance": "蜀道驿站"}
        ]
    },
    "P193": {
        "background": "兴元即今汉中，汉江上游、蜀道枢纽。苏轼出蜀经此，汉中盆地沃野千里、汉水悠悠，是蜀道北段的重要中转。",
        "global_events": [
            {"id": "p193-001", "date": "1069年", "title": "经兴元出蜀", "description": "苏轼经兴元沿蜀道出蜀赴京", "significance": "蜀道中转"}
        ]
    },

    # ── R06 杭州通判 ──
    "P110": {
        "background": "庐州即今合肥，江淮之间重镇。苏轼赴杭州通判任途经庐州，江淮平原、巢湖烟波，是汴京南下的中继站。",
        "global_events": [
            {"id": "p110-001", "date": "1071年", "title": "经庐州赴杭州", "description": "苏轼赴杭州通判任途经庐州", "significance": "赴任中继"}
        ]
    },

    # ── R07 密州知州 ──
    "P165": {
        "background": "太湖沿岸烟波浩渺、鱼米之乡。苏轼自杭州调任密州途经太湖，湖光山色、渔帆点点，是江南最秀美的水路风景。",
        "global_events": [
            {"id": "p165-001", "date": "1074年", "title": "经太湖沿岸北上", "description": "苏轼自杭州调密州途经太湖沿岸", "significance": "江南水路"}
        ]
    },
    "P177": {
        "background": "无锡为太湖明珠、惠山泉天下第二。苏轼途经无锡，惠山泉清冽甘美、太湖风光旖旎，是江南文人心向往之的品茗胜地。",
        "global_events": [
            {"id": "p177-001", "date": "1074年", "title": "经无锡品惠山泉", "description": "苏轼途经无锡，品惠山天下第二泉", "significance": "品茗胜地"}
        ]
    },

    # ── R08 徐州知州 ──
    "P102": {
        "background": "临沂为琅琊故地、书圣之乡。苏轼自密州调徐州途经临沂，沂蒙山水、琅琊古风，是齐鲁南部的文化重镇。",
        "global_events": [
            {"id": "p102-001", "date": "1077年", "title": "经临沂赴徐州", "description": "苏轼自密州调徐州途经临沂", "significance": "赴任途经"}
        ]
    },
    "P157": {
        "background": "泗水古道为齐鲁南北水路要道，孔子讲学之地。苏轼经此，泗水悠悠、洙泗遗风，是儒学发源地的文化象征。",
        "global_events": [
            {"id": "p157-001", "date": "1077年", "title": "经泗水古道", "description": "苏轼经泗水古道赴徐州", "significance": "儒学故地"}
        ]
    },
    "P202": {
        "background": "沂蒙山为齐鲁屋脊、革命老区。苏轼经此，群山连绵、沂水蜿蜒，是齐鲁大地最雄浑壮阔的山岳景观。",
        "global_events": [
            {"id": "p202-001", "date": "1077年", "title": "经沂蒙山赴徐州", "description": "苏轼经沂蒙山区赴徐州任", "significance": "齐鲁山岳"}
        ]
    },

    # ── R09 乌台诗案 ──
    "P059": {
        "background": "濠州即今凤阳、朱元璋故里。苏轼乌台诗案押解途中经此，淮水北岸、钟离古邑，是押解进京的途经之地。",
        "global_events": [
            {"id": "p059-001", "date": "1079年", "title": "押解经濠州", "description": "苏轼因乌台诗案被押解进京途经濠州", "significance": "押解途中"}
        ]
    },
    "P215": {
        "background": "运河全线为南北水路大动脉，自杭州至汴京千里通衢。苏轼押解沿运河北上，两岸柳堤、漕船如织，是北宋最繁忙的水路。",
        "global_events": [
            {"id": "p215-001", "date": "1079年", "title": "沿运河押解北上", "description": "苏轼沿京杭大运河被押解北上进京", "significance": "押解水路"}
        ]
    },

    # ── R10 贬谪黄州 ──
    "P070": {
        "background": "淮河南岸古驿为贬谪黄州途经之地，淮水南岸、驿道蜿蜒。苏轼贬谪经此，淮水悠悠、南望大别山，是入黄州前的最后一段驿路。",
        "global_events": [
            {"id": "p070-001", "date": "1080年", "title": "经淮河南岸古驿赴黄州", "description": "苏轼贬谪黄州途经淮河南岸古驿道", "significance": "贬谪途中"}
        ]
    },
    "P134": {
        "background": "岐亭为黄州西北重镇、陈季常隐居之地。苏轼贬谪黄州后与陈季常交往甚密，方山子故事流传千古，岐亭是黄州时期最重要的社交据点。",
        "global_events": [
            {"id": "p134-001", "date": "1080年", "title": "访陈季常于岐亭", "description": "苏轼贬谪黄州后常访陈季常于岐亭，作《方山子传》", "significance": "黄州至交"}
        ]
    },
    "P135": {
        "background": "蕲水即今浠水，黄州近邻。苏轼在黄州时常游蕲水，蕲水清流、兰溪竹影，是黄州周边最常游历之地。",
        "global_events": [
            {"id": "p135-001", "date": "1082年", "title": "游蕲水兰溪", "description": "苏轼游蕲水兰溪，观溪水清流竹影", "significance": "黄州近游"}
        ]
    },
    "P180": {
        "background": "武昌樊山即今鄂州西山，与黄州隔江相望。苏轼常渡江游武昌，樊山苍翠、吴王城遗址在望，是黄州时期隔江远眺的风景。",
        "global_events": [
            {"id": "p180-001", "date": "1080-1084年", "title": "渡江游武昌樊山", "description": "苏轼在黄州时常渡江游武昌樊山，观吴王城遗址", "significance": "隔江胜景"}
        ]
    },
    "P223": {
        "background": "长江南岸渡口为黄州通往武昌的水路要津。苏轼常从此渡口渡江游武昌，江风猎猎、渡船摇曳，是黄州与武昌之间的日常通道。",
        "global_events": [
            {"id": "p223-001", "date": "1080-1084年", "title": "渡江往来", "description": "苏轼在黄州时常从长江南岸渡口渡江往来武昌", "significance": "日常渡口"}
        ]
    },

    # ── R11 量移汝州 ──
    "P164": {
        "background": "太湖西岸古村落散布于宜兴、长兴之间，水乡泽国、桑田鱼塘。苏轼量移途中经此，太湖烟波、渔舟唱晚，是江南最宁静的水乡风光。",
        "global_events": [
            {"id": "p164-001", "date": "1084年", "title": "经太湖西岸", "description": "苏轼量移汝州途中经太湖西岸古村落", "significance": "江南水乡"}
        ]
    },

    # ── R12 赴登州 ──
    "P088": {
        "background": "胶东半岛古道为齐鲁东部沿海驿道，山海相连。苏轼赴登州经此，黄海在望、丘陵起伏，是赴登州的沿海通道。",
        "global_events": [
            {"id": "p088-001", "date": "1085年", "title": "经胶东半岛赴登州", "description": "苏轼赴登州任途经胶东半岛沿海古道", "significance": "沿海驿道"}
        ]
    },
    "P160": {
        "background": "苏北沿海驿道为淮扬至胶东的通道，盐场遍布、海风咸涩。苏轼赴登州经此，沿海滩涂、盐田如镜，是苏北至山东的沿海通道。",
        "global_events": [
            {"id": "p160-001", "date": "1085年", "title": "经苏北沿海赴登州", "description": "苏轼经苏北沿海驿道赴登州", "significance": "沿海通道"}
        ]
    },
    "P221": {
        "background": "长岛渡口为胶东半岛至登州的海路要津，庙岛群岛横列海峡。苏轼赴登州经此渡海，海天一色、岛礁点点，是赴登州的海上通道。",
        "global_events": [
            {"id": "p221-001", "date": "1085年", "title": "渡海经长岛赴登州", "description": "苏轼经长岛渡口渡海赴登州", "significance": "海上通道"}
        ]
    },

    # ── R13 元祐还朝 ──
    "P015": {
        "background": "曹州即今菏泽，牡丹之都。苏轼还朝途经曹州，平原广袤、牡丹盛开，是中原腹地的花乡名邑。",
        "global_events": [
            {"id": "p015-001", "date": "1086年", "title": "经曹州还朝", "description": "苏轼自登州还朝途经曹州", "significance": "还朝途经"}
        ]
    },
    "P077": {
        "background": "济南为齐鲁都会、泉城名邑，七十二泉天下闻名。苏轼还朝途经济南，趵突泉涌、大明湖碧，是齐鲁文化的中心。",
        "global_events": [
            {"id": "p077-001", "date": "1086年", "title": "经济南还朝", "description": "苏轼自登州还朝途经济南，观趵突泉", "significance": "泉城途经"}
        ]
    },
    "P140": {
        "background": "青州为古九州之一、海岱之间重镇。苏轼还朝途经青州，云门山摩崖、古州城遗存，是齐鲁东部的文化重镇。",
        "global_events": [
            {"id": "p140-001", "date": "1086年", "title": "经青州还朝", "description": "苏轼自登州还朝途经青州", "significance": "古州途经"}
        ]
    },
    "P168": {
        "background": "泰山余脉绵延于齐鲁大地，五岳之首的气势延伸至此。苏轼途经泰山余脉，山势渐起、松柏苍翠，是东岳泰山的余韵。",
        "global_events": [
            {"id": "p168-001", "date": "1086年", "title": "经泰山余脉", "description": "苏轼还朝途经泰山余脉，感受东岳气象", "significance": "东岳余韵"}
        ]
    },
    "P232": {
        "background": "淄州即今淄博，齐文化故地、陶瓷之乡。苏轼还朝途经淄州，齐长城遗址、临淄故城在望，是齐文化的核心区域。",
        "global_events": [
            {"id": "p232-001", "date": "1086年", "title": "经淄州还朝", "description": "苏轼自登州还朝途经淄州", "significance": "齐文化故地"}
        ]
    },

    # ── R14 再知杭州 ──
    "P082": {
        "background": "江淮水乡驿道为汴京至杭州的通道，河网密布、水乡泽国。苏轼再知杭州经此，小桥流水、稻田如画，是南北交通的水乡画廊。",
        "global_events": [
            {"id": "p082-001", "date": "1089年", "title": "经江淮水乡赴杭州", "description": "苏轼再知杭州途经江淮水乡驿道", "significance": "水乡通道"}
        ]
    },
    "P085": {
        "background": "江南运河苏州段为运河最繁忙的河段，桥街相连、商贾云集。苏轼再知杭州经此，运河两岸市井繁华、舟楫如织，是江南运河的精华段。",
        "global_events": [
            {"id": "p085-001", "date": "1089年", "title": "经江南运河赴杭州", "description": "苏轼经江南运河苏州段赴杭州", "significance": "运河精华段"}
        ]
    },

    # ── R15 杭州还朝 ──
    "P063": {
        "background": "洪泽湖沿岸为淮河下游水路要道，烟波浩渺、芦苇丛生。苏轼自杭州还朝经此，湖面辽阔、水天一色，是南北水路的中转。",
        "global_events": [
            {"id": "p063-001", "date": "1091年", "title": "经洪泽湖还朝", "description": "苏轼自杭州还朝途经洪泽湖沿岸", "significance": "水路中转"}
        ]
    },
    "P086": {
        "background": "江南运河全线自杭州至镇江，贯通南北水路。苏轼还朝沿运河北上，运河两岸城镇繁华、水路繁忙，是北宋最繁忙的交通线。",
        "global_events": [
            {"id": "p086-001", "date": "1091年", "title": "沿运河全线还朝", "description": "苏轼沿江南运河全线北上还朝", "significance": "运河全线"}
        ]
    },

    # ── R16 颍州扬州 ──
    "P061": {
        "background": "洪泽湖为淮河下游巨浸、南北水路要津。苏轼赴颍州经此，湖面浩渺、渔帆点点，是淮河流域最大的湖泊。",
        "global_events": [
            {"id": "p061-001", "date": "1091年", "title": "经洪泽湖赴颍州", "description": "苏轼赴颍州任途经洪泽湖", "significance": "赴任途经"}
        ]
    },
    "P062": {
        "background": "洪泽湖古渡口为淮河水路要津，南北往来舟楫必经。苏轼经此渡湖，渡口繁忙、湖风猎猎，是淮河水路的咽喉。",
        "global_events": [
            {"id": "p062-001", "date": "1091年", "title": "渡洪泽湖古渡口", "description": "苏轼渡洪泽湖古渡口赴颍州", "significance": "淮河渡口"}
        ]
    },
    "P069": {
        "background": "淮河南岸驿道为中原至江淮的通道，淮水悠悠、驿路蜿蜒。苏轼赴颍州经此，淮河为界、南北风物各异，是中原与江南的分界线。",
        "global_events": [
            {"id": "p069-001", "date": "1091年", "title": "经淮河南岸赴颍州", "description": "苏轼经淮河南岸驿道赴颍州", "significance": "南北分界"}
        ]
    },

    # ── R17 外放定州 ──
    "P028": {
        "background": "磁州为河北重镇、磁州窑名天下。苏轼外放定州途经磁州，滏阳河畔、窑火千年，是河北南部的文化重镇。",
        "global_events": [
            {"id": "p028-001", "date": "1093年", "title": "经磁州赴定州", "description": "苏轼外放定州途经磁州", "significance": "赴任途经"}
        ]
    },
    "P060": {
        "background": "河北平原古驿为中原至河北的通道，平原辽阔、驿道笔直。苏轼外放定州经此，华北平原一望无际、秋风萧瑟，是北国苍茫的行旅。",
        "global_events": [
            {"id": "p060-001", "date": "1093年", "title": "经河北平原赴定州", "description": "苏轼经河北平原古驿赴定州", "significance": "北国行旅"}
        ]
    },
    "P166": {
        "background": "太行山东麓为华北平原西缘，太行巍峨、东麓沃野。苏轼外放定州经此，太行山影西横、平原东展，是河北西部的地理分界。",
        "global_events": [
            {"id": "p166-001", "date": "1093年", "title": "经太行山东麓", "description": "苏轼外放定州途经太行山东麓", "significance": "太行东麓"}
        ]
    },
    "P185": {
        "background": "相州即今安阳，殷墟故地、邺城遗址。苏轼外放定州途经相州，殷商遗风、邺下文章，是中原北部的文化古都。",
        "global_events": [
            {"id": "p185-001", "date": "1093年", "title": "经相州赴定州", "description": "苏轼外放定州途经相州安阳", "significance": "殷墟故地"}
        ]
    },
    "P191": {
        "background": "邢州即今邢台，河北中南部重镇。苏轼外放定州途经邢州，太行东麓、百泉竞涌，是河北平原的交通要冲。",
        "global_events": [
            {"id": "p191-001", "date": "1093年", "title": "经邢州赴定州", "description": "苏轼外放定州途经邢州", "significance": "河北中继"}
        ]
    },
    "P218": {
        "background": "漳河渡口为河北南北交通要津，漳河横亘、渡船往来。苏轼外放定州经此渡河，漳河浊浪、北风萧瑟，是入河北腹地的水路关卡。",
        "global_events": [
            {"id": "p218-001", "date": "1093年", "title": "渡漳河赴定州", "description": "苏轼渡漳河赴定州", "significance": "河北渡口"}
        ]
    },
    "P226": {
        "background": "真定即今正定，河北重镇、隆兴寺名天下。苏轼外放定州途经真定，古城雄踞、佛塔凌空，是河北中部的文化中心。",
        "global_events": [
            {"id": "p226-001", "date": "1093年", "title": "经真定赴定州", "description": "苏轼外放定州途经真定正定", "significance": "河北文化中心"}
        ]
    },

    # ── R18 南贬岭南 ──
    "P005": {
        "background": "北江为岭南水路要道，自韶州南下至广州。苏轼南贬经此，北江两岸丹霞地貌、碧水红岩，是岭南最壮美的水路。",
        "global_events": [
            {"id": "p005-001", "date": "1094年", "title": "沿北江南下", "description": "苏轼南贬沿北江南下赴惠州", "significance": "岭南水路"}
        ]
    },
    "P064": {
        "background": "洪州即今南昌，赣江中游重镇、滕王阁名天下。苏轼南贬经此，赣江穿城、滕王阁高耸，是岭南贬谪路上的中转站。",
        "global_events": [
            {"id": "p064-001", "date": "1094年", "title": "经洪州南贬", "description": "苏轼南贬途经洪州南昌", "significance": "贬谪中转"}
        ]
    },
    "P126": {
        "background": "南雄为梅关古道南端、岭南入粤门户。苏轼南贬翻越梅岭经南雄入粤，梅关险峻、珠玑巷古，是中原入岭南的咽喉。",
        "global_events": [
            {"id": "p126-001", "date": "1094年", "title": "翻梅关经南雄入粤", "description": "苏轼南贬翻越梅关古道经南雄入岭南", "significance": "入粤门户"}
        ]
    },
    "P145": {
        "background": "汝州为中原重镇、汝瓷名天下。苏轼南贬前曾量移汝州，汝河穿城、青瓷如玉，是黄州量移后的短暂驻地。",
        "global_events": [
            {"id": "p145-001", "date": "1084年", "title": "量移汝州", "description": "苏轼自黄州量移汝州团练副使", "significance": "量移驻地"}
        ]
    },
    "P183": {
        "background": "西江山水为岭南最壮美的河段，碧水丹山、峰林如画。苏轼南贬经此，西江两岸喀斯特地貌、碧水倒映，是岭南贬谪路上唯一的山水慰藉。",
        "global_events": [
            {"id": "p183-001", "date": "1094年", "title": "经西江山水南下", "description": "苏轼南贬经西江山水南下赴惠州", "significance": "岭南山水"}
        ]
    },

    # ── R19 北归终老 ──
    "P002": {
        "background": "白州即今博白，岭南边陲之地。苏轼北归途中经此，南国边邑、瘴疠之乡，是贬谪生涯最偏远的地方之一。",
        "global_events": [
            {"id": "p002-001", "date": "1100年", "title": "经白州北归", "description": "苏轼遇赦北归途经白州", "significance": "北归途经"}
        ]
    },
    "P004": {
        "background": "北部湾海岸为岭南最南端的海岸线，碧海银沙、椰林摇曳。苏轼北归经此，南海浩渺、天涯海角之感，是贬谪生涯最南端的记忆。",
        "global_events": [
            {"id": "p004-001", "date": "1100年", "title": "经北部湾海岸北归", "description": "苏轼北归途经北部湾海岸", "significance": "天涯海角"}
        ]
    },
    "P105": {
        "background": "岭南西江水路为粤桂交通要道，西江碧水、两岸青山。苏轼北归沿西江水路北上，江风拂面、归心似箭，是北归路上的水路通道。",
        "global_events": [
            {"id": "p105-001", "date": "1100年", "title": "沿西江水路北归", "description": "苏轼沿岭南西江水路北归", "significance": "北归水路"}
        ]
    },
    "P192": {
        "background": "兴廉村净行院为雷州半岛古刹，苏轼北归途中曾在此驻留。寺院清幽、梵音阵阵，是北归路上短暂歇脚的禅修之地。",
        "global_events": [
            {"id": "p192-001", "date": "1100年", "title": "驻留兴廉村净行院", "description": "苏轼北归途中驻留兴廉村净行院", "significance": "北归歇脚"}
        ]
    },
    "P212": {
        "background": "郁林即今玉林，岭南中部重镇。苏轼北归经此，南国丘陵、荔枝飘香，是岭南归途的中转站。",
        "global_events": [
            {"id": "p212-001", "date": "1100年", "title": "经郁林北归", "description": "苏轼北归途经郁林玉林", "significance": "归途中转"}
        ]
    },
    "P224": {
        "background": "长江下游全线为江南水路大动脉，自九江至入海口千里通衢。苏轼北归沿长江东下，江面宽阔、两岸繁华，是归途最顺畅的水路。",
        "global_events": [
            {"id": "p224-001", "date": "1100年", "title": "沿长江下游北归", "description": "苏轼沿长江下游全线东下北归", "significance": "归途水路"}
        ]
    },
}

# 执行补充
updated = 0
for pid, supp in SUPPLEMENTS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        print(f"  SKIP {pid} - 文件不存在")
        continue
    
    with open(pf) as f:
        pd = json.load(f)
    
    changed = False
    
    # 补充 global_events
    if supp.get('global_events') and not pd.get('global_events'):
        pd['global_events'] = supp['global_events']
        changed = True
    
    # 增强 background
    if supp.get('background') and (not pd.get('background') or len(pd.get('background','')) < 30):
        pd['background'] = supp['background']
        changed = True
    
    if changed:
        with open(pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
        # 同步到 public
        pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
        if os.path.exists(pub_pf):
            with open(pub_pf, 'w', encoding='utf-8') as f:
                json.dump(pd, f, ensure_ascii=False, indent=2)
        updated += 1
        print(f"  OK {pid} {pd.get('ancient_name','')}")

print(f"\n共更新 {updated} 个地点")
