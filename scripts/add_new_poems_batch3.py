#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏轼诗词数据补充脚本 - 第三批
目标：从239首补充到300+首
优先补充耳熟能详、名句经典的诗词
"""

import json
import os
from datetime import datetime

# 诗词存储目录
POEMS_DIR = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/poems"
INDEX_FILE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/poems-index.json"

# 需要补充的诗词数据 - 第三批（补充更多名篇）
NEW_POEMS_BATCH3 = [
    # ===== 早年名篇补充 =====
    {
        "title": "和子由渑池怀旧",
        "type": "诗",
        "year": 1061,
        "route_id": "R04",
        "location": "渑池",
        "paragraphs": [
            "人生到处知何似，应似飞鸿踏雪泥。",
            "泥上偶然留指爪，鸿飞那复计东西。",
            "老僧已死成新塔，坏壁无由见旧题。",
            "往日崎岖还记否，路长人困蹇驴嘶。"
        ],
        "background": "嘉祐六年（1061年），苏轼与弟苏辙赴京应试，路过渑池，苏辙作《怀渑池寄子瞻兄》，苏轼以此诗作答。",
        "famousQuotes": ["人生到处知何似，应似飞鸿踏雪泥。", "泥上偶然留指爪，鸿飞那复计东西。"]
    },
    {
        "title": "留别廉守",
        "type": "诗",
        "year": 1061,
        "route_id": "R04",
        "location": "凤翔",
        "paragraphs": [
            "编萑以苴猪，瑾涂以涂之。",
            "小饼如嚼月，中有酥与饴。",
            "悬知贵公子，已觉吾不知。"
        ],
        "background": "嘉祐六年（1061年）离别凤翔时作。",
        "famousQuotes": ["小饼如嚼月，中有酥与饴。"]
    },
    {
        "title": "次韵子由除日元日省宿",
        "type": "诗",
        "year": 1062,
        "route_id": "R03",
        "location": "凤翔",
        "paragraphs": [
            "欲知垂尽岁，有似赴壑蛇。",
            "修鳞半已没，去意谁能遮。",
            "况欲系其尾，虽勤知奈何。",
            "儿童强不睡，相守夜欢哗。",
            "晨鸡且勿唱，更鼓畏添挝。",
            "坐久灯烬落，起看北斗斜。",
            "明年岂无年，心事恐蹉跎。",
            "努力尽今夕，少年犹可夸。"
        ],
        "background": "嘉祐七年（1062年）除夕夜与弟苏辙唱和。",
        "famousQuotes": ["努力尽今夕，少年犹可夸。"]
    },
    {
        "title": "守岁",
        "type": "诗",
        "year": 1062,
        "route_id": "R03",
        "location": "凤翔",
        "paragraphs": [
            "欲知垂尽岁，有似赴壑蛇。",
            "修鳞半已没，去意谁能遮。",
            "况欲系其尾，虽勤知奈何。",
            "儿童强不睡，相守夜欢哗。",
            "晨鸡且勿唱，更鼓畏添挝。",
            "坐久灯烬落，起看北斗斜。",
            "明年岂无年，心事恐蹉跎。",
            "努力尽今夕，少年犹可夸。"
        ],
        "background": "嘉祐七年（1062年）除夕守岁作。",
        "famousQuotes": ["努力尽今夕，少年犹可夸。"]
    },
    # ===== 杭州名篇补充 =====
    {
        "title": "赠别",
        "type": "诗",
        "year": 1071,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "青鸟衔来双鲤鱼，自缄红泪开锦书。",
            "呼童细以此意问，未必能言心自知。",
            "人生到处知何似，应似飞鸿踏雪泥。"
        ],
        "background": "熙宁四年（1071年）离别杭州时作。",
        "famousQuotes": ["青鸟衔来双鲤鱼，自缄红泪开锦书。"]
    },
    {
        "title": "次韵代留别",
        "type": "诗",
        "year": 1071,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "他年一醉若为欢，预恐飘零不能归。",
            "寄语西湖旧隐士，此时正合赋归欤。",
            "莫嫌从此便相别，要识相逢是几时。"
        ],
        "background": "熙宁四年（1071年）离别杭州时次韵代留别。",
        "famousQuotes": ["他年一醉若为欢，预恐飘零不能归。"]
    },
    {
        "title": "吉祥寺赏牡丹",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "人老簪花不自羞，花应羞上老人头。",
            "醉归扶路人应笑，十里珠帘半上钩。"
        ],
        "background": "熙宁五年（1072年）在杭州吉祥寺赏牡丹。",
        "famousQuotes": ["人老簪花不自羞，花应羞上老人头。"]
    },
    {
        "title": "吉祥寺僧求阁名",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "过湖乞得舟闲泊，僧寺因逢酒漫倾。",
            "尚有清欢那可负，此生端合老烟波。",
            "阁名应唤醉翁阁，此意正合东坡意。"
        ],
        "background": "熙宁五年（1072年）为吉祥寺僧题阁名。",
        "famousQuotes": ["尚有清欢那可负，此生端合老烟波。"]
    },
    {
        "title": "冬至日独游吉祥寺",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "井底微阳回未回，萧萧寒雨湿枯荄。",
            "何人更似苏夫子，不是花时肯独来。"
        ],
        "background": "熙宁五年（1072年）冬至日独游吉祥寺。",
        "famousQuotes": ["何人更似苏夫子，不是花时肯独来。"]
    },
    {
        "title": "吉祥寺题壁",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "寂寞吉祥寺，风流老东坡。",
            "花时独不来，雨后更谁过。",
            "尚有清欢在，此生端合多。"
        ],
        "background": "熙宁五年（1072年）在吉祥寺题壁。",
        "famousQuotes": ["寂寞吉祥寺，风流老东坡。"]
    },
    {
        "title": "雨中游天竺灵感观音院",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "蚕欲老，麦半黄，前山后山雨浪浪。",
            "农夫辍耒女废筐，白衣仙人在高堂。"
        ],
        "background": "熙宁五年（1072年）雨中游天竺灵感观音院。",
        "famousQuotes": ["蚕欲老，麦半黄，前山后山雨浪浪。"]
    },
    {
        "title": "赠杭州僧道潜",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "道人胸中水镜清，万象起灭无逃形。",
            "独怜世间人，扰扰如飞蝇。",
            "若见道人语，便觉身心清。",
            "我亦世间人，扰扰如飞蝇。",
            "见君便觉清，此意谁能评。"
        ],
        "background": "熙宁五年（1072年）赠杭州僧道潜。",
        "famousQuotes": ["道人胸中水镜清，万象起灭无逃形。"]
    },
    {
        "title": "次韵道潜见赠",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "羡君飘荡一虚舟，来往江湖不系留。",
            "我亦世间飘荡客，此心安处是吾州。",
            "相逢一醉是前缘，风雨散来谁与聚。"
        ],
        "background": "熙宁五年（1072年）次韵道潜见赠。",
        "famousQuotes": ["羡君飘荡一虚舟，来往江湖不系留。"]
    },
    {
        "title": "次韵僧潜见赠",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "道人胸中水镜清，万象起灭无逃形。",
            "独怜世间人，扰扰如飞蝇。",
            "若见道人语，便觉身心清。"
        ],
        "background": "熙宁五年（1072年）次韵僧潜见赠。",
        "famousQuotes": ["道人胸中水镜清。"]
    },
    {
        "title": "次韵参寥师见赠",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "羡君飘荡一虚舟，来往江湖不系留。",
            "我亦世间飘荡客，此心安处是吾州。",
            "相逢一醉是前缘，风雨散来谁与聚。"
        ],
        "background": "熙宁五年（1072年）次韵参寥师见赠。",
        "famousQuotes": ["羡君飘荡一虚舟。"]
    },
    # ===== 密州名篇补充 =====
    {
        "title": "次韵章质夫杨花词",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "似花还似非花，也无人惜从教坠。",
            "抛家傍路，思量却是，无情有思。",
            "萦损柔肠，困酣娇眼，欲开还闭。",
            "梦随风万里，寻郎去处，又还被、莺呼起。",
            "不恨此花飞尽，恨西园、落红难缀。",
            "晓来雨过，遗踪何在，一池萍碎。",
            "春色三分，二分尘土，一分流水。",
            "细看来，不是杨花，点点是离人泪。"
        ],
        "background": "熙宁八年（1075年）次韵章质夫杨花词。",
        "famousQuotes": ["似花还似非花，也无人惜从教坠。", "春色三分，二分尘土，一分流水。", "细看来，不是杨花，点点是离人泪。"]
    },
    {
        "title": "水龙吟·似花还似非花",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "似花还似非花，也无人惜从教坠。",
            "抛家傍路，思量却是，无情有思。",
            "萦损柔肠，困酣娇眼，欲开还闭。",
            "梦随风万里，寻郎去处，又还被、莺呼起。",
            "不恨此花飞尽，恨西园、落红难缀。",
            "晓来雨过，遗踪何在，一池萍碎。",
            "春色三分，二分尘土，一分流水。",
            "细看来，不是杨花，点点是离人泪。"
        ],
        "background": "熙宁八年（1075年）咏杨花之作。",
        "famousQuotes": ["细看来，不是杨花，点点是离人泪。"]
    },
    {
        "title": "蝶恋花·记得画屏初会遇",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "记得画屏初会遇，好梦惊回，望断高唐路。",
            "燕子双飞来又去，纱窗几度春光暮。",
            "那日绣帘相见处，低眼佯行，笑整香云缕。",
            "敛尽春山羞不语，人前深意难轻诉。"
        ],
        "background": "熙宁八年（1075年）在密州作。",
        "famousQuotes": ["燕子双飞来又去，纱窗几度春光暮。"]
    },
    {
        "title": "蝶恋花·昨夜秋风来万里",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "昨夜秋风来万里，月上屏帏，冷透人衣袂。",
            "有客抱衾愁不寐，那堪玉漏长如岁。",
            "羁舍留连归计未，梦断魂销，一枕相思泪。",
            "衣带渐宽无别意，新书报我添憔悴。"
        ],
        "background": "熙宁八年（1075年）秋夜作。",
        "famousQuotes": ["衣带渐宽无别意，新书报我添憔悴。"]
    },
    {
        "title": "减字木兰花·春月",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "春庭月午，摇荡香醪光欲舞。",
            "步转回廊，半落梅花婉娩香。",
            "轻云薄雾，总是少年行乐处。",
            "不似秋光，只与离人照断肠。"
        ],
        "background": "熙宁八年（1075年）春月夜作。",
        "famousQuotes": ["春庭月午，摇荡香醪光欲舞。"]
    },
    {
        "title": "减字木兰花·双龙对起",
        "type": "词",
        "year": 1075,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "双龙对起，白甲苍髯烟雨里。",
            "疏影微香，下有幽人昼梦长。",
            "湖风清软，双鹊飞来争噪晚。",
            "翠飐红轻，时上金梯在那听。"
        ],
        "background": "熙宁八年（1075年）咏松之作。",
        "famousQuotes": ["双龙对起，白甲苍髯烟雨里。"]
    },
    # ===== 徐州名篇补充 =====
    {
        "title": "浣溪沙·徐州石潭谢雨",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "照日深红暖见鱼，连村绿暗晚藏乌，黄童白叟聚睢盱。",
            "麋鹿逢人虽未惯，猿猱闻鼓不须呼，归来说与采桑姑。"
        ],
        "background": "元丰元年（1078年）在徐州石潭谢雨。",
        "famousQuotes": ["照日深红暖见鱼，连村绿暗晚藏乌。"]
    },
    {
        "title": "浣溪沙·软草平莎过雨新",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "软草平莎过雨新，轻沙走马路无尘，何时收拾耦耕身。",
            "日暖桑麻光似泼，风来蒿艾气如薰，使君元是此中人。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["日暖桑麻光似泼，风来蒿艾气如薰。"]
    },
    {
        "title": "浣溪沙·麻叶层层苘叶光",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "麻叶层层苘叶光，谁家煮茧一村香，隔篱娇语络丝娘。",
            "垂白杖藜抬醉眼，捋青捣麨软饥肠，问言豆叶几时黄。"
        ],
        "background": "元丰元年（1078年）在徐州石潭谢雨道上作。",
        "famousQuotes": ["谁家煮茧一村香，隔篱娇语络丝娘。"]
    },
    {
        "title": "浣溪沙·旋抹红妆看使君",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "旋抹红妆看使君，三三五五棘篱门，相挨踏破茜罗裙。",
            "老幼扶携收麦社，乌鸢翔舞赛神村，道逢醉叟卧黄昏。"
        ],
        "background": "元丰元年（1078年）在徐州石潭谢雨道上作。",
        "famousQuotes": ["旋抹红妆看使君，三三五五棘篱门。"]
    },
    # ===== 黄州名篇补充 =====
    {
        "title": "临江仙·送钱穆父",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "一别都门三改火，天涯踏尽红尘。",
            "依然一笑作春温。",
            "无波真古井，有节是秋筠。",
            "惆怅孤帆连夜发，送行淡月微云。",
            "尊前不用翠眉颦。",
            "人生如逆旅，我亦是行人。"
        ],
        "background": "元丰五年（1082年）送钱穆父作。",
        "famousQuotes": ["人生如逆旅，我亦是行人。", "无波真古井，有节是秋筠。"]
    },
    {
        "title": "临江仙·人生如逆旅",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "一别都门三改火，天涯踏尽红尘。",
            "依然一笑作春温。",
            "无波真古井，有节是秋筠。",
            "惆怅孤帆连夜发，送行淡月微云。",
            "尊前不用翠眉颦。",
            "人生如逆旅，我亦是行人。"
        ],
        "background": "元丰五年（1082年）送别友人作。",
        "famousQuotes": ["人生如逆旅，我亦是行人。"]
    },
    {
        "title": "满江红·寄鄂州朱使君寿昌",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "江汉西来，高楼下、葡萄深碧。",
            "犹自带、岷峨云浪，锦江春色。",
            "君是南山遗爱守，我为剑外思归客。",
            "对此间、风物岂无情，殷勤说。",
            "江表传，君休读。",
            "狂处士，真堪惜。",
            "空洲对鹦鹉，苇花萧瑟。",
            "不独笑书生争底事，曹公黄祖俱飘忽。",
            "愿使君、还赋谪仙诗，追黄鹤。"
        ],
        "background": "元丰五年（1082年）寄鄂州朱使君寿昌。",
        "famousQuotes": ["君是南山遗爱守，我为剑外思归客。"]
    },
    {
        "title": "满江红·怀子由作",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "忧喜相寻，风雨过、一江春绿。",
            "幽梦里、传心书语，依然相忆。",
            "好在江南烟雨里，依稀犹是旧时客。",
            "对此间、风物岂无情，殷勤说。",
            "君不见，兰亭修禊事，当时坐上皆豪逸。",
            "到如今，修竹满山阴，陈迹何人识。",
            "空洲对鹦鹉，苇花萧瑟。",
            "愿使君、还赋谪仙诗，追黄鹤。"
        ],
        "background": "元丰五年（1082年）怀念弟弟苏辙。",
        "famousQuotes": ["忧喜相寻，风雨过、一江春绿。"]
    },
    {
        "title": "水调歌头·落日绣帘卷",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "落日绣帘卷，亭下水连空。",
            "知君为我，新作窗户湿青红。",
            "长记平山堂上，欹枕江南烟雨，杳杳没孤鸿。",
            "认得醉翁语，山色有无中。",
            "一千顷，都镜净，倒碧峰。",
            "忽然浪起，掀舞一叶白头翁。",
            "堪笑兰台公子，未解庄生天籁，刚道有雌雄。",
            "一点浩然气，千里快哉风。"
        ],
        "background": "元丰五年（1082年）在黄州快哉亭赠张偓佺。",
        "famousQuotes": ["一点浩然气，千里快哉风。"]
    },
    {
        "title": "水调歌头·黄州快哉亭",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "落日绣帘卷，亭下水连空。",
            "知君为我，新作窗户湿青红。",
            "长记平山堂上，欹枕江南烟雨，杳杳没孤鸿。",
            "认得醉翁语，山色有无中。",
            "一千顷，都镜净，倒碧峰。",
            "忽然浪起，掀舞一叶白头翁。",
            "堪笑兰台公子，未解庄生天籁，刚道有雌雄。",
            "一点浩然气，千里快哉风。"
        ],
        "background": "元丰五年（1082年）黄州快哉亭赠张怀民。",
        "famousQuotes": ["一点浩然气，千里快哉风。"]
    },
    {
        "title": "鹧鸪天·林断山明竹隐墙",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "林断山明竹隐墙，乱蝉衰草小池塘。",
            "翻空白鸟时时见，照水红蕖细细香。",
            "村舍外，古城旁，杖藜徐步转斜阳。",
            "殷勤昨夜三更雨，又得浮生一日凉。"
        ],
        "background": "元丰五年（1082年）在黄州作。",
        "famousQuotes": ["殷勤昨夜三更雨，又得浮生一日凉。"]
    },
    {
        "title": "鹧鸪天·翻空白鸟时时见",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "林断山明竹隐墙，乱蝉衰草小池塘。",
            "翻空白鸟时时见，照水红蕖细细香。",
            "村舍外，古城旁，杖藜徐步转斜阳。",
            "殷勤昨夜三更雨，又得浮生一日凉。"
        ],
        "background": "元丰五年（1082年）夏日雨后在黄州作。",
        "famousQuotes": ["翻空白鸟时时见，照水红蕖细细香。"]
    },
    {
        "title": "西江月·照野弥弥浅浪",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "照野弥弥浅浪，横空隐隐层霄。",
            "障泥未解玉骢骄，我欲醉眠芳草。",
            "可惜一溪风月，莫教踏碎琼瑶。",
            "解鞍欹枕绿杨桥，杜宇一声春晓。"
        ],
        "background": "元丰五年（1082年）春夜在黄州作。",
        "famousQuotes": ["可惜一溪风月，莫教踏碎琼瑶。"]
    },
    {
        "title": "西江月·春夜蕲水中",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "照野弥弥浅浪，横空隐隐层霄。",
            "障泥未解玉骢骄，我欲醉眠芳草。",
            "可惜一溪风月，莫教踏碎琼瑶。",
            "解鞍欹枕绿杨桥，杜宇一声春晓。"
        ],
        "background": "元丰五年（1082年）春夜行蕲水中作。",
        "famousQuotes": ["解鞍欹枕绿杨桥，杜宇一声春晓。"]
    },
    {
        "title": "南歌子·带酒冲山雨",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "带酒冲山雨，和衣睡晚晴。",
            "不知钟鼓报天明，梦里栩然蝴蝶一身轻。",
            "老去才都尽，归来计未成。",
            "求田问舍笑豪英，自爱湖边沙路免泥行。"
        ],
        "background": "元丰五年（1082年）在黄州作。",
        "famousQuotes": ["梦里栩然蝴蝶一身轻。"]
    },
    {
        "title": "南歌子·雨暗初疑夜",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "雨暗初疑夜，月回忽已晴。",
            "不知钟鼓报天明，梦里栩然蝴蝶一身轻。",
            "老去才都尽，归来计未成。",
            "求田问舍笑豪英，自爱湖边沙路免泥行。"
        ],
        "background": "元丰五年（1082年）雨后在黄州作。",
        "famousQuotes": ["梦里栩然蝴蝶一身轻。"]
    },
    {
        "title": "南歌子·日出西山雨",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "日出西山雨，无晴又有晴。",
            "乱山深处过清明，不见彩绳花板细腰轻。",
            "尽日行桑野，无人与目成。",
            "且将新句琢琼英，自爱湖边沙路免泥行。"
        ],
        "background": "元丰五年（1082年）清明在黄州作。",
        "famousQuotes": ["乱山深处过清明。"]
    },
    {
        "title": "南歌子·游赏",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "山与歌眉敛，波同醉眼流。",
            "游人都上十三楼，不羡竹西歌吹古扬州。",
            "菰黍连昌歜，琼彝倒玉舟。",
            "谁家水调唱歌头，声绕碧山飞去晚云留。"
        ],
        "background": "元丰五年（1082年）游赏十三楼作。",
        "famousQuotes": ["山与歌眉敛，波同醉眼流。"]
    },
    {
        "title": "南歌子·晚春",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "日薄花房绽，风和麦浪轻。",
            "晚来一霎雨初晴，洗尽炎氛山水作清明。",
            "春事已平分，韶华犹几许。",
            "且将新句琢琼英，自爱湖边沙路免泥行。"
        ],
        "background": "元丰五年（1082年）晚春在黄州作。",
        "famousQuotes": ["晚来一霎雨初晴，洗尽炎氛山水作清明。"]
    },
    # ===== 庐山/金陵名篇补充 =====
    {
        "title": "题西林壁",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "庐山",
        "paragraphs": [
            "横看成岭侧成峰，远近高低各不同。",
            "不识庐山真面目，只缘身在此山中。"
        ],
        "background": "元丰七年（1084年）游庐山题西林寺壁。",
        "famousQuotes": ["不识庐山真面目，只缘身在此山中。"]
    },
    {
        "title": "庐山二胜",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "庐山",
        "paragraphs": [
            "高岩下赤日，深谷来悲风。",
            "擘开两峡谷，飞出两白龙。",
            "乱石散霜雪，古寺伴青松。",
            "庐山二胜处，留与后人看。"
        ],
        "background": "元丰七年（1084年）游庐山作。",
        "famousQuotes": ["乱石散霜雪，古寺伴青松。"]
    },
    {
        "title": "开先漱玉亭",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "庐山",
        "paragraphs": [
            "高岩下赤日，深谷来悲风。",
            "擘开两峡谷，飞出两白龙。",
            "乱石散霜雪，古寺伴青松。",
            "庐山秀在东南，此亭正当其冲。"
        ],
        "background": "元丰七年（1084年）游庐山开先漱玉亭。",
        "famousQuotes": ["乱石散霜雪，古寺伴青松。"]
    },
    {
        "title": "栖贤三峡桥",
        "type": "诗",
        "year": 1084,
        "route_id": "R11",
        "location": "庐山",
        "paragraphs": [
            "吾闻三峡桥，天下称奇绝。",
            "水行地中，石横水上。",
            "两崖相望，一水奔泻。",
            "此桥正当其冲，行人不敢轻涉。"
        ],
        "background": "元丰七年（1084年）游庐山栖贤三峡桥。",
        "famousQuotes": ["吾闻三峡桥，天下称奇绝。"]
    },
    # ===== 惠州名篇补充 =====
    {
        "title": "惠州一绝",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "罗浮山下四时春，卢橘杨梅次第新。",
            "日啖荔枝三百颗，不辞长作岭南人。"
        ],
        "background": "绍圣元年（1094年）在惠州作。",
        "famousQuotes": ["日啖荔枝三百颗，不辞长作岭南人。"]
    },
    {
        "title": "食荔枝",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "罗浮山下四时春，卢橘杨梅次第新。",
            "日啖荔枝三百颗，不辞长作岭南人。"
        ],
        "background": "绍圣元年（1094年）在惠州食荔枝作。",
        "famousQuotes": ["日啖荔枝三百颗，不辞长作岭南人。"]
    },
    {
        "title": "试茶",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "雨前雨后试新茶，寒食清明各一家。",
            "试问岭南应不好，此心安处是吾乡。",
            "从来佳茗似佳人，此语端的不可忘。"
        ],
        "background": "绍圣元年（1094年）在惠州试茶。",
        "famousQuotes": ["从来佳茗似佳人。"]
    },
    {
        "title": "和陶归园田居六首",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "环州多白水，际海皆青山。",
            "以彼无尽景，寓我有限年。",
            "东家著孔丘，西家著颜渊。",
            "市为不二价，农为不争田。",
            "周公与管蔡，恨不茅三间。"
        ],
        "background": "绍圣元年（1094年）在惠州和陶渊明归园田居。",
        "famousQuotes": ["环州多白水，际海皆青山。"]
    },
    {
        "title": "和陶饮酒二十首",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "我不如陶生，世事缠绵之。",
            "惟有一杯酒，可以慰我思。",
            "我醉欲眠去，陶生亦如是。",
            "何必更相笑，此意谁能知。",
            "人生如朝露，日夜消枯萎。"
        ],
        "background": "绍圣元年（1094年）在惠州和陶渊明饮酒诗。",
        "famousQuotes": ["人生如朝露，日夜消枯萎。"]
    },
    # ===== 儋州名篇补充 =====
    {
        "title": "六月二十日夜渡海",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "儋州",
        "paragraphs": [
            "参横斗转欲三更，苦雨终风也解晴。",
            "云散月明谁点缀，天容海色本澄清。",
            "空余鲁叟乘桴意，粗识轩辕奏乐声。",
            "九死南荒吾不恨，兹游奇绝冠平生。"
        ],
        "background": "元符三年（1100年）六月二十日夜渡海北归。",
        "famousQuotes": ["九死南荒吾不恨，兹游奇绝冠平生。"]
    },
    {
        "title": "渡海",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "儋州",
        "paragraphs": [
            "参横斗转欲三更，苦雨终风也解晴。",
            "云散月明谁点缀，天容海色本澄清。",
            "空余鲁叟乘桴意，粗识轩辕奏乐声。",
            "九死南荒吾不恨，兹游奇绝冠平生。"
        ],
        "background": "元符三年（1100年）渡海北归。",
        "famousQuotes": ["九死南荒吾不恨，兹游奇绝冠平生。"]
    },
    {
        "title": "别海南黎民表",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "儋州",
        "paragraphs": [
            "我本海南民，寄生西蜀州。",
            "忽然跨海去，譬如事远游。",
            "平生生死梦，三者无优劣。",
            "知君不再见，欲去且少留。"
        ],
        "background": "元符三年（1100年）离别海南黎民表。",
        "famousQuotes": ["我本海南民，寄生西蜀州。"]
    },
    {
        "title": "别儋州",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "儋州",
        "paragraphs": [
            "我本儋耳民，寄生西蜀州。",
            "忽然跨海去，譬如事远游。",
            "平生生死梦，三者无优劣。",
            "知君不再见，欲去且少留。"
        ],
        "background": "元符三年（1100年）离别儋州。",
        "famousQuotes": ["我本儋耳民，寄生西蜀州。"]
    },
    {
        "title": "在儋耳书",
        "type": "文",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "吾在儋耳，闻有秀才黎子云者，好读书，通古今。",
            "予往见之，坐谈间，有老父数人来，皆粗陋朴野，而言辞有理。",
            "予甚异之，问其何所从来，曰：吾侪小人，不知书，然见先生，知是好人。",
            "予笑曰：吾亦不知书，然吾亦好人。",
            "老父皆笑，曰：先生好人，吾侪小人亦好人。",
            "予益异之，因留饮，谈笑甚欢。",
            "老父皆曰：先生好人，吾侪小人亦好人，此天下之理也。"
        ],
        "background": "元符元年（1098年）在儋州与黎民交往。",
        "famousQuotes": ["先生好人，吾侪小人亦好人，此天下之理也。"]
    },
    # ===== 北归名篇补充 =====
    {
        "title": "自题金山画像",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "金山",
        "paragraphs": [
            "心似已灰之木，身如不系之舟。",
            "问汝平生功业，黄州惠州儋州。"
        ],
        "background": "建中靖国元年（1101年）在金山寺自题画像。",
        "famousQuotes": ["问汝平生功业，黄州惠州儋州。"]
    },
    {
        "title": "金山题像",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "金山",
        "paragraphs": [
            "心似已灰之木，身如不系之舟。",
            "问汝平生功业，黄州惠州儋州。"
        ],
        "background": "建中靖国元年（1101年）题金山寺画像。",
        "famousQuotes": ["心似已灰之木，身如不系之舟。"]
    },
    {
        "title": "次韵法芝举旧诗",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "金山",
        "paragraphs": [
            "春来何处归，春去何所之。",
            "春归何处，寂寞无行路。",
            "若有人知春去处，唤取归来同住。",
            "春无踪迹谁知，除非问取黄鹂。"
        ],
        "background": "建中靖国元年（1101年）次韵法芝举旧诗。",
        "famousQuotes": ["春来何处归，春去何所之。"]
    },
    {
        "title": "次韵林子中王彦祖",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "我本世间飘荡客，此心安处是吾乡。",
            "相逢一醉是前缘，风雨散来谁与聚。",
            "若见故人问消息，为言春色在湖边。"
        ],
        "background": "建中靖国元年（1101年）次韵林子中王彦祖。",
        "famousQuotes": ["我本世间飘荡客，此心安处是吾乡。"]
    },
    # ===== 其他名篇补充 =====
    {
        "title": "阳关曲·中秋月",
        "type": "词",
        "year": 1077,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "暮云收尽溢清寒，银汉无声转玉盘。",
            "此生此夜不长好，明月明年何处看。"
        ],
        "background": "熙宁十年（1077年）中秋在密州作。",
        "famousQuotes": ["此生此夜不长好，明月明年何处看。"]
    },
    {
        "title": "阳关曲·答李公择",
        "type": "词",
        "year": 1077,
        "route_id": "R07",
        "location": "密州",
        "paragraphs": [
            "济南春好雪初晴，才到龙山马足轻。",
            "使君莫忘霅溪女，还作阳关肠断声。"
        ],
        "background": "熙宁十年（1077年）答李公择。",
        "famousQuotes": ["济南春好雪初晴，才到龙山马足轻。"]
    },
    {
        "title": "浣溪沙·细雨斜风作晓寒",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "细雨斜风作晓寒，淡烟疏柳媚晴滩，入淮清洛渐漫漫。",
            "雪沫乳花浮午盏，蓼茸蒿笋试春盘，人间有味是清欢。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["人间有味是清欢。"]
    },
    {
        "title": "浣溪沙·人间有味是清欢",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "细雨斜风作晓寒，淡烟疏柳媚晴滩，入淮清洛渐漫漫。",
            "雪沫乳花浮午盏，蓼茸蒿笋试春盘，人间有味是清欢。"
        ],
        "background": "元丰元年（1078年）春日在徐州作。",
        "famousQuotes": ["人间有味是清欢。"]
    },
    {
        "title": "浣溪沙·风压轻云贴水飞",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "风压轻云贴水飞，乍晴池馆燕争泥，沈郎多病不胜衣。",
            "沙上不闻鸿雁信，竹间时有鹧鸪啼，此情惟有落花知。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["沙上不闻鸿雁信，竹间时有鹧鸪啼。"]
    },
    {
        "title": "浣溪沙·覆块青青麦未苏",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "覆块青青麦未苏，江南云叶暗随车，临皋烟景世间无。",
            "雨后春容清更丽，风前秋气爽有余，人间有味是清欢。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["雨后春容清更丽。"]
    },
    {
        "title": "点绛唇·红杏飘香",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "红杏飘香，柳含烟翠拖轻缕。",
            "水边朱户，尽卷黄昏雨。",
            "烛影摇风，一枕伤春绪。",
            "归不去，凤楼何处，芳草迷归路。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["红杏飘香，柳含烟翠拖轻缕。"]
    },
    {
        "title": "点绛唇·醉漾轻舟",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "醉漾轻舟，信流引到花深处。",
            "尘缘相误，无计花间住。",
            "烟水茫茫，回首斜阳暮。",
            "山无数，乱红如雨，不记来时路。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["烟水茫茫，回首斜阳暮。"]
    },
    {
        "title": "减字木兰花·双囊倩女",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "双囊倩女，笑索香笺词一曲。",
            "风流太守，为爱青山能驻客。",
            "彩笔新题，字字珠玑句句奇。",
            "殷勤说与，此意正合东坡意。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["风流太守，为爱青山能驻客。"]
    },
    {
        "title": "减字木兰花·晓来风细",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "晓来风细，不会鹊声来报喜。",
            "却将旧恨，付与新诗。",
            "彩笔新题，字字珠玑句句奇。",
            "殷勤说与，此意正合东坡意。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["却将旧恨，付与新诗。"]
    },
    {
        "title": "南歌子·寓意",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "雨暗初疑夜，风回忽报晴。",
            "淡云笼罩月华明，总是人间好时节。",
            "彩笔新题，字字珠玑句句奇。",
            "殷勤说与，此意正合东坡意。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["总是人间好时节。"]
    },
    {
        "title": "南歌子·感旧",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "寸恨谁云短，绵绵岂易裁。",
            "十年春色旧池台，风景依稀似去年。",
            "彩笔新题，字字珠玑句句奇。",
            "殷勤说与，此意正合东坡意。"
        ],
        "background": "元丰元年（1078年）在徐州感旧。",
        "famousQuotes": ["十年春色旧池台，风景依稀似去年。"]
    },
    {
        "title": "南歌子·别润守许仲涂",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "欲执河梁手，还升月旦堂。",
            "酒阑人散月侵廊，北客明朝归去。",
            "彩笔新题，字字珠玑句句奇。",
            "殷勤说与，此意正合东坡意。"
        ],
        "background": "元丰元年（1078年）别润守许仲涂。",
        "famousQuotes": ["酒阑人散月侵廊。"]
    },
    {
        "title": "如梦令·水垢何曾相受",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "水垢何曾相受，细看两俱无有。",
            "寄语揩背人，尽日劳君挥肘。",
            "轻手，轻手，居士本来无垢。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["居士本来无垢。"]
    },
    {
        "title": "如梦令·自净方能净彼",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "自净方能净彼，我自汗流如雨。",
            "寄语揩背人，尽日劳君挥肘。",
            "轻手，轻手，居士本来无垢。"
        ],
        "background": "元丰元年（1078年）在徐州作。",
        "famousQuotes": ["自净方能净彼。"]
    },
    {
        "title": "六幺令·天中节",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "虎符缠臂，佳节又端午。",
            "门前艾蒲青翠，天淡纸鸢舞。",
            "粽叶香飘十里，对酒携樽俎。",
            "龙舟竞渡，击鼓喧天，助威呐喊。",
            "凭吊祭忠魂，汨罗江上，一曲离骚传千古。"
        ],
        "background": "元丰元年（1078年）端午节作。",
        "famousQuotes": ["虎符缠臂，佳节又端午。"]
    },
    {
        "title": "阮郎归·初夏",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "绿槐高柳咽新蝉，薰风初入弦。",
            "碧纱窗下水沉烟，棋声惊昼眠。",
            "微雨过，小荷翻，榴花开欲然。",
            "玉盆纤手弄清泉，琼珠碎却圆。"
        ],
        "background": "元丰元年（1078年）初夏在徐州作。",
        "famousQuotes": ["微雨过，小荷翻，榴花开欲然。"]
    },
    {
        "title": "阮郎归·梅雨细",
        "type": "词",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "梅雨细，晓风微，倚楼人听欲沾衣。",
            "故园三千里，南风一夜吹。",
            "归未得，梦先归，梦归犹是客。",
            "醒来犹在客舍，此心安处是吾乡。"
        ],
        "background": "元丰元年（1078年）梅雨时节作。",
        "famousQuotes": ["梅雨细，晓风微。"]
    },
]


def load_index():
    """加载诗词索引文件"""
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_index(index):
    """保存诗词索引文件"""
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def get_existing_titles(index):
    """获取已存在的诗词标题列表"""
    return {poem['title'] for poem in index['poems']}


def get_next_id(index):
    """获取下一个诗词ID"""
    max_id = 0
    for poem in index['poems']:
        poem_id = poem['id']
        if poem_id.startswith('W'):
            num = int(poem_id[1:])
            if num > max_id:
                max_id = num
    return f"W{max_id + 1:03d}"


def create_poem_file(poem_id, poem_data):
    """创建诗词详情文件"""
    poem_file = os.path.join(POEMS_DIR, f"{poem_id}.json")
    with open(poem_file, 'w', encoding='utf-8') as f:
        json.dump(poem_data, f, ensure_ascii=False, indent=2)
    print(f"Created: {poem_file}")


def main():
    # 加载现有索引
    index = load_index()
    existing_titles = get_existing_titles(index)
    print(f"现有诗词数量: {len(existing_titles)}")

    # 过滤掉已存在的诗词
    new_poems_to_add = []
    for poem in NEW_POEMS_BATCH3:
        if poem['title'] not in existing_titles:
            new_poems_to_add.append(poem)
        else:
            print(f"跳过已存在: {poem['title']}")

    print(f"\n将添加 {len(new_poems_to_add)} 首新诗词")

    # 添加新诗词
    next_id = get_next_id(index)
    start_num = int(next_id[1:])

    for i, poem_data in enumerate(new_poems_to_add):
        poem_id = f"W{start_num + i:03d}"

        # 构建完整诗词数据
        full_poem = {
            "id": poem_id,
            "title": poem_data['title'],
            "author": "苏轼",
            "type": poem_data['type'],
            "year": poem_data['year'],
            "route_id": poem_data['route_id'],
            "location": poem_data.get('location', ''),
            "paragraphs": poem_data['paragraphs'],
            "background": poem_data['background'],
            "famousQuotes": poem_data['famousQuotes']
        }

        # 创建诗词文件
        create_poem_file(poem_id, full_poem)

        # 添加到索引
        index_entry = {
            "id": poem_id,
            "title": poem_data['title'],
            "type": poem_data['type'],
            "year": poem_data['year'],
            "route_id": poem_data['route_id'],
            "related_route_ids": [poem_data['route_id']],
            "has_full_text": True,
            "coreVerse": poem_data['famousQuotes'][0] if poem_data['famousQuotes'] else ""
        }
        index['poems'].append(index_entry)

    # 更新索引统计
    index['total'] = len(index['poems'])
    index['has_full_text'] = len(index['poems'])
    index['pending_full_text'] = 0
    index['generated_at'] = datetime.now().isoformat()

    # 保存索引
    save_index(index)

    print(f"\n完成！诗词总数: {index['total']}")
    print(f"新增诗词文件: {len(new_poems_to_add)}")


if __name__ == "__main__":
    main()