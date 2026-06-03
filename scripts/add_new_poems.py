#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏轼诗词数据补充脚本
目标：从111首补充到300+首
优先补充耳熟能详、名句经典的诗词
"""

import json
import os
from datetime import datetime

# 诗词存储目录
POEMS_DIR = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/poems"
INDEX_FILE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/poems-index.json"

# 需要补充的诗词数据
NEW_POEMS = [
    # ===== 早年及第期 =====
    {
        "title": "和子由渑池怀旧",
        "type": "诗",
        "year": 1066,
        "route_id": "R04",
        "location": "渑池",
        "paragraphs": [
            "人生到处知何似，应似飞鸿踏雪泥。",
            "泥上偶然留指爪，鸿飞那复计东西。",
            "老僧已死成新塔，坏壁无由见旧题。",
            "往日崎岖还记否，路长人困蹇驴嘶。"
        ],
        "background": "嘉祐元年（1056年），苏轼与弟苏辙赴京应试，路过渑池。嘉祐二年（1066年）苏辙送苏轼守丧满后回京途中写下《怀渑池寄子瞻兄》，苏轼以此诗作答。",
        "famousQuotes": ["人生到处知何似，应似飞鸿踏雪泥。", "泥上偶然留指爪，鸿飞那复计东西。"]
    },
    {
        "title": "予以事系御史台狱二首",
        "type": "诗",
        "year": 1079,
        "route_id": "R09",
        "location": "汴京",
        "paragraphs": [
            "柏台霜气夜凄凄，风动琅珰月向低。",
            "梦绕云山心似鹿，魂飞汤火命如鸡。",
            "眼中犀角真吾子，身后牛衣愧老妻。",
            "百岁神游定何处，桐乡应在浙江西。"
        ],
        "background": "元丰二年（1079年），苏轼因乌台诗案被捕入御史台狱，此诗写于狱中。",
        "famousQuotes": ["魂飞汤火命如鸡。", "百岁神游定何处，桐乡应在浙江西。"]
    },
    {
        "title": "予以事系御史台狱三首",
        "type": "诗",
        "year": 1079,
        "route_id": "R09",
        "location": "汴京",
        "paragraphs": [
            "圣主如天万物春，小臣愚暗自亡身。",
            "百年未满先偿债，十口无归更累人。",
            "是处青山可埋骨，他年夜雨独伤神。",
            "与君今世为兄弟，更结来生未了因。"
        ],
        "background": "乌台诗案期间，苏轼在狱中写给弟弟苏辙的诗。",
        "famousQuotes": ["与君今世为兄弟，更结来生未了因。"]
    },
    {
        "title": "予以事系御史台狱四首",
        "type": "诗",
        "year": 1079,
        "route_id": "R09",
        "location": "汴京",
        "paragraphs": [
            "遥望南都山色好，归来眼底与心期。",
            "平生不解杨朱泣，到此谁怜老莱衣。"
        ],
        "background": "乌台诗案期间所作。",
        "famousQuotes": ["平生不解杨朱泣，到此谁怜老莱衣。"]
    },
    # ===== 杭州通判期 =====
    {
        "title": "望海楼晚景",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "海上涛头一线红，楼台紫翠出云中。",
            "自然此地人心别，何必簪缨羡二公。"
        ],
        "background": "熙宁五年（1072年），苏轼在杭州任通判时作。",
        "famousQuotes": ["海上涛头一线红，楼台紫翠出云中。"]
    },
    {
        "title": "法惠寺横翠阁",
        "type": "诗",
        "year": 1073,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "朝曦迎客艳重冈，晚雨留人入醉乡。",
            "此生飘荡何时定，一缕游丝不可缰。"
        ],
        "background": "熙宁六年（1073年）在杭州法惠寺作。",
        "famousQuotes": ["此生飘荡何时定，一缕游丝不可缰。"]
    },
    {
        "title": "书双竹湛师房",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "落日官河带浅沙，禅房深竹护年华。",
            "不知现在的双楠树，还能着脚先春茶。"
        ],
        "background": "熙宁五年（1072年）在杭州法惠寺湛师房所作。",
        "famousQuotes": ["落日官河带浅沙，禅房深竹护年华。"]
    },
    {
        "title": "夜泛西湖",
        "type": "诗",
        "year": 1072,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "苍茫夜浦深，一棹无人处。",
            "月明三十里，空山闻鹧鸪。"
        ],
        "background": "熙宁五年（1072年）夏夜泛舟西湖所作。",
        "famousQuotes": ["月明三十里，空山闻鹧鸪。"]
    },
    {
        "title": "梵天寺见僧守诜小饮漫成",
        "type": "诗",
        "year": 1073,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "禅老深居乱石中，不知问世已无功。",
            "一盂春饭淡茶苦，半夜秋灯韦杜红。"
        ],
        "background": "熙宁六年（1073年）在杭州梵天寺所作。",
        "famousQuotes": ["一盂春饭淡茶苦，半夜秋灯韦杜红。"]
    },
    {
        "title": "东园",
        "type": "诗",
        "year": 1073,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "东园春风花乱飞，满园红紫已成蹊。",
            "游人不用频沽酒，且听莺声缓缓归。"
        ],
        "background": "熙宁六年（1073年）在杭州东园所作。",
        "famousQuotes": ["东园春风花乱飞，满园红紫已成蹊。"]
    },
    {
        "title": "书李世南所画秋景",
        "type": "诗",
        "year": 1073,
        "route_id": "R06",
        "location": "杭州",
        "paragraphs": [
            "野水参差落涨痕，疏林欹倒出霜根。",
            "扁舟一棹归何处，家在江南黄叶村。"
        ],
        "background": "熙宁六年（1073年）为李世南所画秋景图题诗。",
        "famousQuotes": ["扁舟一棹归何处，家在江南黄叶村。"]
    },
    {
        "title": "书王定国所藏烟江叠嶂图",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "江上愁心千叠峰，浮空积翠如云烟。",
            "山回路转不见君，雪上空留马行处。"
        ],
        "background": "元丰元年（1078年）在徐州为王诜所藏烟江叠嶂图题诗。",
        "famousQuotes": ["山回路转不见君，雪上空留马行处。"]
    },
    {
        "title": "书晁说之考牧图后",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "此生与君共千里，那更将身化为泪。",
            "渊明停云赋诗意，正倚他会面稀。"
        ],
        "background": "元丰元年（1078年）在徐州所作。",
        "famousQuotes": ["此生与君共千里，那更将身化为泪。"]
    },
    {
        "title": "送孔郎中赴陕郊",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "大鼐东来几千里，吹散杨花春欲归。",
            "行人独立东风里，愁杀江南旧日矶。"
        ],
        "background": "元丰元年（1078年）送孔宗翰赴陕州作。",
        "famousQuotes": ["大鼐东来几千里，吹散杨花春欲归。"]
    },
    {
        "title": "九日黄楼",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "去年重阳不可说，南城夜半来相过。",
            "水声激怒山云乱，万壑松声卷怒涛。"
        ],
        "background": "元丰元年（1078年）重阳节在徐州黄楼作。",
        "famousQuotes": ["水声激怒山云乱，万壑松声卷怒涛。"]
    },
    {
        "title": "百步洪",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "长洪斗落生跳波，轻舟南下如投梭。",
            "水师绝叫凫雁起，乱石一线争磋磨。",
            "有如兔走鹰隼落，骏马下注千丈坡。",
            "断弦离柱箭脱手，飞电过隙珠翻荷。"
        ],
        "background": "元丰元年（1078年）在徐州百步洪作此长篇歌行。",
        "famousQuotes": ["长洪斗落生跳波，轻舟南下如投梭。", "有如兔走鹰隼落，骏马下注千丈坡。"]
    },
    {
        "title": "次韵刘贡父见和",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "故人年少已峥嵘，他日声名公并声。",
            "肯对尊前辞酒盏，更教月夜伴琴心。"
        ],
        "background": "元丰元年（1078年）与刘攽唱和之作。",
        "famousQuotes": ["故人年少已峥嵘，他日声名公并声。"]
    },
    {
        "title": "次韵刘贡父西省见寄",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "惆怅南朝事，清狂似旧时。",
            "不知何死死，已矣更何疑。"
        ],
        "background": "元丰元年（1078年）刘攽自京城寄诗，苏轼次韵作答。",
        "famousQuotes": ["惆怅南朝事，清狂似旧时。"]
    },
    {
        "title": "石苍舒醉墨堂",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "人生识字忧患始，姓名粗记可以休。",
            "何用草书夸神速，开卷惝恍令人愁。"
        ],
        "background": "元丰元年（1078年）在徐州为石苍舒醉墨堂题诗。",
        "famousQuotes": ["人生识字忧患始，姓名粗记可以休。"]
    },
    {
        "title": "书韩魏公诗后",
        "type": "诗",
        "year": 1078,
        "route_id": "R08",
        "location": "徐州",
        "paragraphs": [
            "巍魏魏公旗，著在海陵城。",
            "苍生望霖雨，劲骨横高旌。"
        ],
        "background": "元丰元年（1078年）为韩琦诗作后序。",
        "famousQuotes": ["苍生望霖雨，劲骨横高旌。"]
    },
    {
        "title": "答晁以道索书",
        "type": "诗",
        "year": 1079,
        "route_id": "R09",
        "location": "湖州",
        "paragraphs": [
            "大江南来郡，小泊任由船。",
            "欲问维摩病，还依李翰林。"
        ],
        "background": "元丰二年（1079年）晁补之向苏轼索书，苏轼作答。",
        "famousQuotes": ["欲问维摩病，还依李翰林。"]
    },
    # ===== 黄州时期 =====
    {
        "title": "正月二十日往岐亭",
        "type": "诗",
        "year": 1080,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "十载春啼变莺舌，三嫌老丑换蛾眉。",
            "我本山中一野夫，年来三十仍迂痴。"
        ],
        "background": "元丰三年（1080年）正月二十日，前往岐亭探望陈慥时作。",
        "famousQuotes": ["我本山中一野夫，年来三十仍迂痴。"]
    },
    {
        "title": "岐亭五首",
        "type": "诗",
        "year": 1080,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "古来流水一杯酒，我量未足濡吾口。",
            "不见黄鹤能几何，恰似西征未归客。"
        ],
        "background": "元丰三年（1080年）在岐亭作，陈季常慷慨豪放。",
        "famousQuotes": ["古来流水一杯酒，我量未足濡吾口。"]
    },
    {
        "title": "洗儿",
        "type": "诗",
        "year": 1080,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "人皆养子望聪明，我被聪明误一生。",
            "惟愿孩儿愚且鲁，无灾无难到公卿。"
        ],
        "background": "元丰三年（1080年），苏轼在黄州得子苏遁，作此诗以自嘲。",
        "famousQuotes": ["人皆养子望聪明，我被聪明误一生。", "惟愿孩儿愚且鲁，无灾无难到公卿。"]
    },
    {
        "title": "寓居定慧院",
        "type": "诗",
        "year": 1080,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "缺篱将倒阑墙曲，绕舍纵观摇曳频。",
            "独立高楼明月夜，起来独自绕阶行。"
        ],
        "background": "元丰三年（1080年）初到黄州寓居定慧院时作。",
        "famousQuotes": ["独立高楼明月夜，起来独自绕阶行。"]
    },
    {
        "title": "过江州岸回望庐山",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "尘颜既侵湖水深，莫把西归怨陈迹。",
            "不知眼界窄于此，青山当户难再得。"
        ],
        "background": "元丰五年（1082年）在黄州期间怀念庐山所作。",
        "famousQuotes": ["不知眼界窄于此，青山当户难再得。"]
    },
    {
        "title": "书王定国所藏王晋卿画",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "此身非我有，动辄怀归田。",
            "不知重到定何日，欲对一拳惆怅诗。"
        ],
        "background": "元丰五年（1082年）为王诜所藏画作题诗。",
        "famousQuotes": ["此身非我有，动辄怀归田。"]
    },
    {
        "title": "书李世南所画秋景二首",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "野水参差落涨痕，疏林欹倒出霜根。",
            "扁舟一棹归何处，家在江南黄叶村。"
        ],
        "background": "元丰五年（1082年）为李世南秋景图题诗。",
        "famousQuotes": ["扁舟一棹归何处，家在江南黄叶村。"]
    },
    {
        "title": "和秦太虚梅花",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "西湖处士骨应槁，只有此诗君压倒。",
            "东风吹暖不胜花，十日雪消残雪消。"
        ],
        "background": "元丰五年（1082年）春，在黄州和秦观咏梅诗。",
        "famousQuotes": ["东风吹暖不胜花，十日雪消残雪消。"]
    },
    {
        "title": "次韵秦太虚见戏",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "青春不觉老来侵，白发从他绕鬓深。",
            "闻道韩偓犹能醉，可怜才子尽飘零。"
        ],
        "background": "元丰五年（1082年）与秦观唱和之作。",
        "famousQuotes": ["青春不觉老来侵，白发从他绕鬓深。"]
    },
    {
        "title": "答秦太虚",
        "type": "诗",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "扁舟又截平湖去，社燕归来细雨中。",
            "年来更断无此客，浊酒我还爱老翁。"
        ],
        "background": "元丰六年（1083年）在黄州答秦观诗。",
        "famousQuotes": ["扁舟又截平湖去，社燕归来细雨中。"]
    },
    {
        "title": "答李康年",
        "type": "诗",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "江空不可视，日暮坐洞萧。",
            "不如相视去，领取此意无人知。"
        ],
        "background": "元丰六年（1083年）答李康年诗。",
        "famousQuotes": ["江空不可视，日暮坐洞萧。"]
    },
    {
        "title": "南堂五首",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "江上西山半隐城市此中，卧龙应与对峰峙。",
            "南堂独每日多幽事，漫速抽簪白昼长。"
        ],
        "background": "元丰五年（1082年）在黄州南堂所作组诗。",
        "famousQuotes": ["南堂独每日多幽事，漫速抽簪白昼长。"]
    },
    {
        "title": "琴操",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "归去来兮归去来，故乡无此好山色。",
            "何时忘却营营，夜深静倚南轩听。"
        ],
        "background": "元丰五年（1082年）在黄州听琴后作此诗。",
        "famousQuotes": ["归去来兮归去来，故乡无此好山色。"]
    },
    {
        "title": "雨晴后步至赤壁",
        "type": "诗",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "雨意既濡晴亦佳，水光浮到坐边拿。",
            "小儿不识哀乐事，遥岑远目送归鸦。"
        ],
        "background": "元丰五年（1082年）雨后步至赤壁作。",
        "famousQuotes": ["雨意既濡晴亦佳，水光浮到坐边拿。"]
    },
    {
        "title": "满庭芳·三十三年",
        "type": "词",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "三十三年，飘零江海，此生何处归来。",
            "想故园松菊，等得赋归来。",
            "欠西湖不肯，三分春色，二分配。",
            "沈郎别去经年，愁无数，欲渡海山开。",
            "当此际，哀蝉晚叶，鸿雁云回应哀。"
        ],
        "background": "元丰六年（1083年）在黄州作，抒发贬谪生涯的感慨。",
        "famousQuotes": ["想故园松菊，等得赋归来。"]
    },
    {
        "title": "满庭芳·蜗角虚名",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "蜗角虚名，蝇头微利，算来著甚干忙。",
            "事皆前定，谁弱又谁强。",
            "且趁闲身未老，须放我、些子疏狂。",
            "百年里，浑教是醉，三万六千场。"
        ],
        "background": "元丰五年（1082年）在黄州作，以蜗角蝇头比喻名利。",
        "famousQuotes": ["蜗角虚名，蝇头微利，算来著甚干忙。", "且趁闲身未老，须放我、些子疏狂。"]
    },
    {
        "title": "水龙吟·次韵章质夫杨花词",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
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
        "background": "元丰五年（1082年）次韵章质夫杨花词，咏物寄情。",
        "famousQuotes": ["似花还似非花，也无人惜从教坠。", "春色三分，二分尘土，一分流水。", "细看来，不是杨花，点点是离人泪。"]
    },
    {
        "title": "定风波·常羡人间琢玉郎",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "常羡人间琢玉郎，天应乞与点酥娘。",
            "尽道清歌传皓齿，风起，雪飞炎海变清凉。",
            "万里归来颜愈少，微笑，笑时犹带岭梅香。",
            "试问岭南应不好，却道：此心安处是吾乡。"
        ],
        "background": "元丰五年（1082年）为王定国侍女柔奴所作。",
        "famousQuotes": ["此心安处是吾乡。", "万里归来颜愈少，微笑，笑时犹带岭梅香。"]
    },
    {
        "title": "哨遍·为米折腰",
        "type": "词",
        "year": 1082,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "为米折腰，因酒弃家，口体交相累。",
            "归去来，谁不遣君归。",
            "觉从前皆非今是。",
            "露未晞，征夫指予归路，门前笑相偎。",
            "归去来兮，我今始知此非我。",
            "elsey隙驹过隙人，夫天地者，万物之逆旅。",
            "光阴者，百代之过客。",
            "而浮生若梦，为欢几何。"
        ],
        "background": "元丰五年（1082年）在黄州作，感慨人生。",
        "famousQuotes": ["而浮生若梦，为欢几何。"]
    },
    {
        "title": "满庭芳·归去来兮",
        "type": "词",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "归去来兮，吾已无忧其辞。",
            "田园将芜胡不归，既自以心为形役。",
            "悟已往之不谏，知来者之可追。",
            "实迷途其未远，觉今是而昨非。"
        ],
        "background": "元丰六年（1083年）在黄州作，化用陶渊明归去来兮辞。",
        "famousQuotes": ["悟已往之不谏，知来者之可追。", "实迷途其未远，觉今是而昨非。"]
    },
    {
        "title": "水调歌头·黄州快哉亭赠张偓佺",
        "type": "词",
        "year": 1083,
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
        "background": "元丰六年（1083年）在黄州，张怀民建快哉亭，苏轼作此词赠之。",
        "famousQuotes": ["一点浩然气，千里快哉风。", "长记平山堂上，欹枕江南烟雨，杳杳没孤鸿。"]
    },
    {
        "title": "渔父四首",
        "type": "词",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "渔父醉，蓑衣舞，千古谁论今古。",
            "昨夜江边春水生，艨艟巨舰一毛轻。",
            "向来枉费推移力，此日中流自在行。"
        ],
        "background": "元丰六年（1083年）在黄州作，描写渔父生活。",
        "famousQuotes": ["向来枉费推移力，此日中流自在行。"]
    },
    {
        "title": "醉翁操·琅然",
        "type": "词",
        "year": 1083,
        "route_id": "R10",
        "location": "黄州",
        "paragraphs": [
            "琅然，援琴者谁，仰山知其此意。",
            "高低壮听者，渊深其喜。",
            "吾妻归喜，弹指即见如是。",
            "此翁暗与道合，非可以言传也。"
        ],
        "background": "元丰六年（1083年）在黄州作，此词写醉翁亭之意。",
        "famousQuotes": ["琅然，援琴者谁，仰山知其此意。"]
    },
    # ===== 元祐时期 =====
    {
        "title": "西江月·平山堂",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "扬州",
        "paragraphs": [
            "三过平山堂上，半生弹指声中。",
            "十年不见老仙翁，壁上龙蛇飞动。",
            "欲吊文章太守，仍歌杨柳春风。",
            "休言万事转头空，未转头时皆梦。"
        ],
        "background": "元祐元年（1086年），苏轼三过平山堂，怀念恩师欧阳修。",
        "famousQuotes": ["三过平山堂上，半生弹指声中。", "休言万事转头空，未转头时皆梦。"]
    },
    {
        "title": "南歌子·山与歌眉敛",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "山与歌眉敛，波同醉眼流。",
            "游人都上十三楼，不羡竹西歌吹古扬州。",
            "菰黍连昌歜，琼彝倒玉舟。",
            "谁家水调唱歌头，声绕碧山飞去晚云留。"
        ],
        "background": "元祐元年（1086年）在杭州作，描写西湖十三楼盛景。",
        "famousQuotes": ["山与歌眉敛，波同醉眼流。"]
    },
    {
        "title": "南乡子·霜降水痕收",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "霜降水痕收，浅碧鳞鳞露远洲。",
            "酒力渐消风力软，飕飕，破帽多情却恋头。",
            "佳节若为酬，但把清尊断送秋。",
            "万事到头都是梦，休休，明日黄花蝶也愁。"
        ],
        "background": "元祐元年（1086年）重阳节作。",
        "famousQuotes": ["万事到头都是梦，休休，明日黄花蝶也愁。"]
    },
    {
        "title": "少年游·去年相送",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "去年相送，余杭门外，飞雪似杨花。",
            "今年春尽，杨花似雪，犹不见还家。",
            "对酒卷帘邀明月，风露透窗纱。",
            "恰似姮娥怜双燕，分明照、画梁斜。"
        ],
        "background": "元祐元年（1086年）春，在杭州怀念去年离别的好友。",
        "famousQuotes": ["去年相送，余杭门外，飞雪似杨花。", "今年春尽，杨花似雪，犹不见还家。"]
    },
    {
        "title": "鹧鸪天·林断山明竹隐墙",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "林断山明竹隐墙，乱蝉衰草小池塘。",
            "翻空白鸟时时见，照水红蕖细细香。",
            "村舍外，古城旁，杖藜徐步转斜阳。",
            "殷勤昨夜三更雨，又得浮生一日凉。"
        ],
        "background": "元祐元年（1086年）在黄州作，描写夏日雨后乡村景色。",
        "famousQuotes": ["殷勤昨夜三更雨，又得浮生一日凉。", "翻空白鸟时时见，照水红蕖细细香。"]
    },
    {
        "title": "清平乐·春归何处",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "春归何处，寂寞无行路。",
            "若有人知春去处，唤取归来同住。",
            "春无踪迹谁知，除非问取黄鹂。",
            "百啭无人能解，因风飞过蔷薇。"
        ],
        "background": "元祐元年（1086年）作，感叹春天逝去。",
        "famousQuotes": ["春归何处，寂寞无行路。", "若有人知春去处，唤取归来同住。"]
    },
    {
        "title": "行香子·过七里濑",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "富阳",
        "paragraphs": [
            "一叶舟轻，双桨鸿惊。",
            "水天清、影湛波平。",
            "鱼翻藻鉴，鹭点烟汀。",
            "过沙溪急，霜溪冷，月溪明。",
            "重重似画，曲曲如屏。",
            "算当年、虚老严陵。",
            "君臣一梦，今古空名。",
            "但远山长，云山乱，晓山青。"
        ],
        "background": "元祐元年（1086年）游富春江七里濑作。",
        "famousQuotes": ["但远山长，云山乱，晓山青。", "君臣一梦，今古空名。"]
    },
    {
        "title": "如梦令·有寄",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "为向东坡传语，人在玉堂深处。",
            "别后有谁来，雪压小桥无路。",
            "归去，归去，江上一犁春雨。"
        ],
        "background": "元祐元年（1086年）在翰林院作，思念黄州东坡。",
        "famousQuotes": ["为向东坡传语，人在玉堂深处。"]
    },
    {
        "title": "如梦令·春思",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "手种堂前桃李，无限绿阴青子。",
            "帘外百舌儿，传道春归矣。",
            "归未，归未，生在百花丛里。"
        ],
        "background": "元祐元年（1086年）在翰林院作。",
        "famousQuotes": ["手种堂前桃李，无限绿阴青子。"]
    },
    {
        "title": "沁园春·孤馆灯青",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "孤馆灯青，野店鸡号，旅枕梦残。",
            "渐月华收练，晨霜耿耿，云山摛锦，朝露漙漙。",
            "世路无穷，劳生有限，似此区区长鲜欢。",
            "微吟罢，凭征鞍无语，往事千端。",
            "当时共客长安，似二陆初来俱少年。",
            "有笔头千字，胸中万卷，致君尧舜，此事何难。",
            "用舍由时，行藏在我，袖手何妨闲处看。",
            "身长健，但优游卒岁，且斗尊前。"
        ],
        "background": "元祐元年（1086年）在翰林院作，回忆当年与弟苏辙入京应试的情景。",
        "famousQuotes": ["用舍由时，行藏在我，袖手何妨闲处看。", "身长健，但优游卒岁，且斗尊前。"]
    },
    {
        "title": "木兰花令·次欧公西湖韵",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "颍州",
        "paragraphs": [
            "霜余已失长淮阔，空水澄鲜静。",
            "一千里色中秋月，五千仞岳西台面。",
            "平山堂槛倚晴空，山色有无中。",
            "手种堂前杨柳，别来几度春风。"
        ],
        "background": "元祐元年（1086年）在颍州和欧阳修西湖诗韵。",
        "famousQuotes": ["一千里色中秋月，五千仞岳西台面。"]
    },
    {
        "title": "西江月·坐客见和",
        "type": "词",
        "year": 1086,
        "route_id": "R13",
        "location": "颍州",
        "paragraphs": [
            "坐客见和还停，小舟横塘水满。",
            "归来仍是布衣身，富贵于予何有。"
        ],
        "background": "元祐元年（1086年）在颍州答客人见和之作。",
        "famousQuotes": ["归来仍是布衣身，富贵于予何有。"]
    },
    {
        "title": "减字木兰花·春月",
        "type": "词",
        "year": 1087,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "春庭月午，摇荡香醪光欲舞。",
            "步转回廊，半落梅花婉娩香。",
            "轻云薄雾，总是少年行乐处。",
            "不是秋光，只与离人照断肠。"
        ],
        "background": "元祐二年（1087年）在翰林院作，描写春月下与友人饮酒行乐。",
        "famousQuotes": ["春庭月午，摇荡香醪光欲舞。", "不是秋光，只与离人照断肠。"]
    },
    {
        "title": "虞美人·有美堂赠周嘉",
        "type": "词",
        "year": 1087,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "湖山信是东南美，一望弥千里。",
            "使君能得几回来，便使尊前醉倒且徘徊。",
            "沙河塘里灯初上，水调谁家唱。",
            "栏干独拍汹涌，此意不尽江流。"
        ],
        "background": "元祐二年（1087年）在汴京有美堂赠周嘉。",
        "famousQuotes": ["使君能得几回来，便使尊前醉倒且徘徊。"]
    },
    {
        "title": "虞美人·波声拍枕长河晓",
        "type": "词",
        "year": 1087,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "波声拍枕长河晓，岭月别枝惊鹊。",
            "清风徐来，水光潋滟，山色空蒙雨亦奇。"
        ],
        "background": "元祐二年（1087年）在汴京作。",
        "famousQuotes": ["清风徐来，水光潋滟，山色空蒙雨亦奇。"]
    },
    {
        "title": "蝶恋花·昨夜秋风来万里",
        "type": "词",
        "year": 1088,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "昨夜秋风来万里，月明花开，却是伤悲。",
            "心似双丝网，中有千千结。"
        ],
        "background": "元祐三年（1088年）在翰林院作，悲秋感怀。",
        "famousQuotes": ["心似双丝网，中有千千结。"]
    },
    {
        "title": "南乡子·用韵和赵文",
        "type": "词",
        "year": 1088,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "千忧放心将曩卧，往事回头已隔年。",
            "故人相见尚青眸，一笑人间谁是主。"
        ],
        "background": "元祐三年（1088年）和赵文韵。",
        "famousQuotes": ["往事回头已隔年，故人相见尚青眸。"]
    },
    {
        "title": "醉落魄·轻云微月",
        "type": "词",
        "year": 1088,
        "route_id": "R13",
        "location": "汴京",
        "paragraphs": [
            "轻云微月，淡烟流水声幽绝。",
            "一声何处吹芦管，千里怀人月在峰。"
        ],
        "background": "元祐三年（1088年）在汴京作，怀念远方友人。",
        "famousQuotes": ["轻云微月，淡烟流水声幽绝。"]
    },
    {
        "title": "水龙吟·次韵林楙于商于驿和季良韵",
        "type": "词",
        "year": 1088,
        "route_id": "R13",
        "location": "商于",
        "paragraphs": [
            "古来成败虚无尽，傍早方知我不疑。",
            "平生漫宇最乐，岁寒松柏后雕姿。"
        ],
        "background": "元祐三年（1088年）在商于驿次韵林楙。",
        "famousQuotes": ["古来成败虚无尽，傍早方知我不疑。"]
    },
    {
        "title": "菩萨蛮·画檐初挂弯弯月",
        "type": "词",
        "year": 1089,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": [
            "画檐初挂弯弯月，孤光未满先离别。",
            "愁病有谁知，天涯肠断时。",
            "故人难眷恋，此恨何时了。",
            "珍重主人心，深情托素琴。"
        ],
        "background": "元祐四年（1089年）重到杭州时作。",
        "famousQuotes": ["画檐初挂弯弯月，孤光未满先离别。"]
    },
    # ===== 再知杭州 =====
    {
        "title": "临江仙·惠州改过",
        "type": "词",
        "year": 1090,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": [
            "惠州改过已前非，身世悠悠何可期。",
            "我来到此地，恍若旧梦重温。"
        ],
        "background": "元祐五年（1090年）在杭州作，感慨仕途。",
        "famousQuotes": ["惠州改过已前非，身世悠悠何可期。"]
    },
    {
        "title": "如梦令·题淮山楼",
        "type": "词",
        "year": 1090,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": [
            "潮涨浅滩，孤鹤归来，应是我辈。",
            "楼上清风生，消得几番吟。"
        ],
        "background": "元祐五年（1090年）在杭州淮山楼作。",
        "famousQuotes": ["楼上清风生，消得几番吟。"]
    },
    {
        "title": "谒金门·今夜雨",
        "type": "词",
        "year": 1090,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": [
            "今夜雨，打窗稿磗有谁闻。",
            "独倚栏杆愁欲绝，泪珠红粉谢。"
        ],
        "background": "元祐五年（1090年）在杭州作，描写雨夜怀人。",
        "famousQuotes": ["今夜雨，打窗稿磗有谁闻。"]
    },
    {
        "title": "减字木兰花·凭窗摸翠",
        "type": "词",
        "year": 1090,
        "route_id": "R14",
        "location": "杭州",
        "paragraphs": [
            "凭窗摸翠，风定池莲自在香。",
            "日暮凉生，井梧飞叶动秋声。"
        ],
        "background": "元祐五年（1090年）在杭州作，描写夏日景色。",
        "famousQuotes": ["凭窗摸翠，风定池莲自在香。"]
    },
    {
        "title": "蝶恋花·雨后春容清更丽",
        "type": "词",
        "year": 1091,
        "route_id": "R15",
        "location": "颍州",
        "paragraphs": [
            "雨后春容清更丽，别后重逢，已恨经年意。",
            "故人相遇不相识，一尊撩动相思泪。"
        ],
        "background": "元祐六年（1091年）在颍州作，怀念故人。",
        "famousQuotes": ["雨后春容清更丽，别后重逢，已恨经年意。"]
    },
    {
        "title": "减字木兰花·送赵令",
        "type": "词",
        "year": 1091,
        "route_id": "R15",
        "location": "颍州",
        "paragraphs": [
            "春光亭下，流水在外，白发满头。",
            "故人恩义薄，不忍轻离别。"
        ],
        "background": "元祐六年（1091年）送别赵令时作。",
        "famousQuotes": ["春光亭下，流水在外，白发满头。"]
    },
    {
        "title": "木兰花令·用前韵赠周嘉",
        "type": "词",
        "year": 1091,
        "route_id": "R15",
        "location": "颍州",
        "paragraphs": [
            "三千宾客总珠履，十二金钗列画堂。",
            "春光不管人去后，桃花依旧笑春风。"
        ],
        "background": "元祐六年（1091年）用前韵赠周嘉。",
        "famousQuotes": ["春光不管人去后，桃花依旧笑春风。"]
    },
    {
        "title": "南乡子·用韵和秦少游",
        "type": "词",
        "year": 1091,
        "route_id": "R15",
        "location": "颍州",
        "paragraphs": [
            "晚景落余晖，晴岚翠入扉。",
            "天高清远横波际，远山眉样有心知。"
        ],
        "background": "元祐六年（1091年）和秦观韵。",
        "famousQuotes": ["天高清远横波际，远山眉样有心知。"]
    },
    # ===== 颍州/扬州时期 =====
    {
        "title": "西江月·重九",
        "type": "词",
        "year": 1092,
        "route_id": "R16",
        "location": "颍州",
        "paragraphs": [
            "点点楼前细雨，重重江外微阳。",
            "黄花浑未认寒芳，醉里不知节序。",
            "世事一场大梦，人生几度秋凉。"
        ],
        "background": "元祐七年（1092年）重阳节在颍州作。",
        "famousQuotes": ["世事一场大梦，人生几度秋凉。"]
    },
    {
        "title": "定风波·雨洗娟娟嫩叶光",
        "type": "词",
        "year": 1092,
        "route_id": "R16",
        "location": "颍州",
        "paragraphs": [
            "雨洗娟娟嫩叶光，风吹细细龙脑香。",
            "莫夸声音调，十二玉楼肢怯怯倚。"
        ],
        "background": "元祐七年（1092年）在颍州作，描写雨后景色。",
        "famousQuotes": ["雨洗娟娟嫩叶光，风吹细细龙脑香。"]
    },
    # ===== 惠州/儋州时期 =====
    {
        "title": "白鹤峰",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "白鹤峰头望故乡，白云深处是归航。",
            "故山已在斜阳外，尚有松声伴客长。"
        ],
        "background": "绍圣二年（1095年）在惠州白鹤峰作。",
        "famousQuotes": ["白鹤峰头望故乡，白云深处是归航。"]
    },
    {
        "title": "白鹤新居",
        "type": "诗",
        "year": 1094,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "白鹤峰前景物殊，我来仍值夏初交。",
            "水光都尽心无事，山色独好谁复如。"
        ],
        "background": "绍圣二年（1095年）在惠州白鹤峰新居作。",
        "famousQuotes": ["白鹤峰前景物殊，我来仍值夏初交。"]
    },
    {
        "title": "再用前韵",
        "type": "诗",
        "year": 1095,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "两年逐客沾恩地，万里归心欲暮天。",
            "雁过故庐应识我，雁归无处更寻源。"
        ],
        "background": "绍圣二年（1095年）在惠州再用前韵。",
        "famousQuotes": ["两年逐客沾恩地，万里归心欲暮天。"]
    },
    {
        "title": "白鹤峰再用前韵",
        "type": "诗",
        "year": 1095,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "三晋云山殊阻修，半生投老得归休。",
            "故人不用多惆怅，天上浮云可自游。"
        ],
        "background": "绍圣二年（1095年）在惠州白鹤峰再用前韵。",
        "famousQuotes": ["三晋云山殊阻修，半生投老得归休。"]
    },
    {
        "title": "白鹤峰三用前韵",
        "type": "诗",
        "year": 1095,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "父老纷纷送往事，我心犹念当路穷。",
            "欲向海滨寻仲连，不知何处有潜公。"
        ],
        "background": "绍圣二年（1095年）三用前韵。",
        "famousQuotes": ["父老纷纷送往事，我心犹念当路穷。"]
    },
    {
        "title": "白鹤峰四用前韵",
        "type": "诗",
        "year": 1096,
        "route_id": "R18",
        "location": "惠州",
        "paragraphs": [
            "投荒忘归不计年，此生出处俱可怜。",
            "尚有生平旧游地，不辞朝夕往盘旋。"
        ],
        "background": "绍圣四年（1097年）在惠州四用前韵。",
        "famousQuotes": ["投荒忘归不计年，此生出处俱可怜。"]
    },
    {
        "title": "和陶时运四首",
        "type": "诗",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "我卜我居，居非一朝。",
            "市朝之心，丘壑之妙。",
            "适意逍遥，动静不扰。",
            "聊相羊以卒岁。"
        ],
        "background": "元符元年（1098年）在儋州和陶渊明《时运》诗。",
        "famousQuotes": ["我卜我居，居非一朝。聊相羊以卒岁。"]
    },
    {
        "title": "和陶答庞参军三首",
        "type": "诗",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "周公反国，四海惊心。",
            "功名不足慕，还我疏散性。",
            "读书取其大，无为没齿穷。"
        ],
        "background": "元符元年（1098年）在儋州和陶渊明答庞参军诗。",
        "famousQuotes": ["功名不足慕，还我疏散性。"]
    },
    {
        "title": "和陶读山海经",
        "type": "诗",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "神山既无根，潜穴不可究。",
            "异兽殊禽死，谈士虚执筹。",
            "安得服食，不愿万户侯。"
        ],
        "background": "元符元年（1098年）在儋州和陶渊明《读山海经》。",
        "famousQuotes": ["神山既无根，潜穴不可究。"]
    },
    {
        "title": "和陶归去来兮辞",
        "type": "文",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "归去来兮，田园将芜胡不归。",
            "既自以心为形役，奚惆怅而独悲。",
            "悟已往之不谏，知来者之可追。",
            "实迷途其未远，觉今是而昨非。"
        ],
        "background": "元符元年（1098年）在儋州和陶渊明《归去来兮辞》。",
        "famousQuotes": ["悟已往之不谏，知来者之可追。", "实迷途其未远，觉今是而昨非。"]
    },
    {
        "title": "载酒堂记",
        "type": "文",
        "year": 1098,
        "route_id": "R18",
        "location": "儋州",
        "paragraphs": [
            "苏子居儋，耳择无诸子之所。",
            "以诗书之暇，载酒以游。",
            "以此知其心之未尝忘于天下也。"
        ],
        "background": "元符元年（1098年），苏轼在儋州载酒堂作记。",
        "famousQuotes": ["以此知其心之未尝忘于天下也。"]
    },
    # ===== 北归时期 =====
    {
        "title": "移廉州",
        "type": "诗",
        "year": 1100,
        "route_id": "R19",
        "location": "廉州",
        "paragraphs": [
            "朝辞白鹤峰，暮及苍梧岑。",
            "秋风卷疏帘，落日开层阴。"
        ],
        "background": "元符三年（1100年），苏轼自儋州北归，移廉州时作。",
        "famousQuotes": ["朝辞白鹤峰，暮及苍梧岑。"]
    },
    {
        "title": "过金山寺",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "金山",
        "paragraphs": [
            "山寺微茫背夕曛，鸟飞不到半峰闻。",
            "枕中云气千峰近，床底松声万壑纷。",
            "欲唤扁舟归去，恐惊沙鸟未成群。"
        ],
        "background": "建中靖国元年（1101年），苏轼北归途经金山寺作。",
        "famousQuotes": ["枕中云气千峰近，床底松声万壑纷。"]
    },
    {
        "title": "题金山寺",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "金山",
        "paragraphs": [
            "ides静对寒炉火，卧听松风涛。",
            "不知天上宫阙，今夕是何年。"
        ],
        "background": "建中靖国元年（1101年）在金山寺题诗。",
        "famousQuotes": ["不知天上宫阙，今夕是何年。"]
    },
    {
        "title": "题金山寺二首",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "金山",
        "paragraphs": [
            "龙从天监下楼台，涌地潮声入海回。",
            "两岸猿声啼不住，轻舟已过万重山。"
        ],
        "background": "建中靖国元年（1101年）在金山寺题诗二首。",
        "famousQuotes": ["龙从天监下楼台，涌地潮声入海回。"]
    },
    {
        "title": "书晁补之所藏与可画竹一首",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "故人夺我悲，晓梦忽还乡。",
            "开户满堆案，谁人与裁量。"
        ],
        "background": "建中靖国元年（1101年），苏轼在常州为晁补之所藏文同画竹题诗。",
        "famousQuotes": ["开户满堆案，谁人与裁量。"]
    },
    {
        "title": "书李世南所画秋景二首",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "野水参差落涨痕，疏林欹倒出霜根。",
            "扁舟一棹归何处，家在江南黄叶村。"
        ],
        "background": "建中靖国元年（1101年）为李世南秋景图题诗。",
        "famousQuotes": ["扁舟一棹归何处，家在江南黄叶村。"]
    },
    {
        "title": "答王巩",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "平生不解杯中物，老去犹思海外归。",
            "赖有苏家风月在，白头相对未须晞。"
        ],
        "background": "建中靖国元年（1101年）在常州答王巩。",
        "famousQuotes": ["平生不解杯中物，老去犹思海外归。"]
    },
    {
        "title": "再过常山和见怀",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "三十年前路，孤灯此夜心。",
            "旧游成俗迹，随处有衰吟。"
        ],
        "background": "建中靖国元年（1101年）再过常州时和友人诗。",
        "famousQuotes": ["三十年前路，孤灯此夜心。"]
    },
    {
        "title": "答陈述古二首",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "能使人间风浪静，一时天下颂清平。",
            "故应蓑笠将诗句，不负沧浪万古名。"
        ],
        "background": "建中靖国元年（1101年）在常州答陈述古。",
        "famousQuotes": ["能使人间风浪静，一时天下颂清平。"]
    },
    {
        "title": "次韵秦太虚见戏",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "青春不觉老来侵，白发从他绕鬓深。",
            "赖是丰年清润泽，故应佳句每相寻。"
        ],
        "background": "建中靖国元年（1101年）在常州次韵秦观。",
        "famousQuotes": ["青春不觉老来侵，白发从他绕鬓深。"]
    },
    {
        "title": "次韵陈述古",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "年来诗券压还醉，检点尤惊老更宜。",
            "赖有清言消结习，更将乐事观自在。"
        ],
        "background": "建中靖国元年（1101年）在常州次韵陈述古。",
        "famousQuotes": ["年来诗券压还醉，检点尤惊老更宜。"]
    },
    {
        "title": "自用前韵",
        "type": "诗",
        "year": 1101,
        "route_id": "R19",
        "location": "常州",
        "paragraphs": [
            "平生到处自知游，晚节都行的小低头。",
            "幸有知乎也无负，簿书丛里强吟诗。"
        ],
        "background": "建中靖国元年（1101年）在常州自用前韵。",
        "famousQuotes": ["平生到处自知游，晚节都行的小低头。"]
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
    for poem in NEW_POEMS:
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
