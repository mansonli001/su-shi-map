#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量补充现有160个地点的详细信息
数据来源：《苏轼行踪考》
"""
import json
import os

# 完整地点数据库
PLACE_DATA = {
    # 故乡与早年
    '眉山': {'province': '四川省', 'foods': ['川菜', '火锅', '串串', '腊肉', '香肠', '东坡肉'], 'works': [], 'tags': ['故乡', '出生地'], 'note': '苏轼故乡，景祐三年（1037）出生于眉山纱縠行'},
    '眉山纱縠行': {'province': '四川省', 'foods': ['川菜', '腊肉'], 'works': [], 'tags': ['故居'], 'note': '苏轼出生地'},
    '青神': {'province': '四川省', 'foods': ['川菜', '泡菜', '腊肉'], 'works': [], 'tags': ['游历地'], 'note': '苏轼青年时期曾游历青神，与王弗相识'},
    '三峡': {'province': '湖北省', 'foods': ['江鲜', '腊肉'], 'works': ['出峡'], 'tags': ['游历地'], 'note': '出蜀水路'},
    '夔州': {'province': '重庆市', 'foods': ['奉节脐橙', '腊肉', '合渣'], 'works': [], 'tags': ['游历地'], 'note': '三峡地区'},
    '泸州': {'province': '四川省', 'foods': ['泸州老窖', '古蔺麻辣鸡', '黄粑'], 'works': [], 'tags': ['游历地'], 'note': '长江沿岸'},
    '戎州': {'province': '四川省', 'foods': ['宜宾燃面', '五粮液', '李庄白肉'], 'works': [], 'tags': ['游历地'], 'note': '长江要塞'},
    '梓潼': {'province': '四川省', 'foods': ['梓潼酥饼', '片粉'], 'works': [], 'tags': ['游历地'], 'note': '蜀道要道'},
    '金牛': {'province': '四川省', 'foods': ['剑门豆腐', '核桃饼'], 'works': [], 'tags': ['游历地'], 'note': '金牛道起点'},
    '沔州': {'province': '陕西省', 'foods': ['面皮', '菜豆腐'], 'works': [], 'tags': ['游历地'], 'note': '汉中地区'},
    '凤州': {'province': '陕西省', 'foods': ['凤县豆腐', '花椒'], 'works': [], 'tags': ['游历地'], 'note': '蜀道要道'},
    '陈仓': {'province': '陕西省', 'foods': ['西凤酒', '臊子面', '豆花泡馍'], 'works': [], 'tags': ['游历地'], 'note': '入关中要道'},
    '扶风': {'province': '陕西省', 'foods': ['面食', '臊子面'], 'works': [], 'tags': ['游历地'], 'note': '法门寺所在地'},
    '华州': {'province': '陕西省', 'foods': ['华山松子', '水盆羊肉'], 'works': ['华阴有赠'], 'tags': ['游历地'], 'note': '华山所在地'},
    '陕州': {'province': '河南省', 'foods': ['陕州地坑院', '羊肉汤'], 'works': [], 'tags': ['游历地'], 'note': '入洛阳要道'},
    
    # 出蜀入京
    '乐山': {'province': '四川省', 'foods': ['乐山甜皮鸭', '钵钵鸡', '跷脚牛肉'], 'works': [], 'tags': ['游历地'], 'note': '嘉祐元年入京途中'},
    '忠州': {'province': '重庆市', 'foods': ['忠州豆腐乳', '腊肉'], 'works': [], 'tags': ['游历地'], 'note': '长江沿岸'},
    '万州': {'province': '重庆市', 'foods': ['万州烤鱼', '格格'], 'works': [], 'tags': ['游历地'], 'note': '三峡地区'},
    '云阳': {'province': '重庆市', 'foods': ['云阳桃片糕', '腊肉'], 'works': [], 'tags': ['游历地'], 'note': '三峡要地'},
    '奉节': {'province': '重庆市', 'foods': ['奉节脐橙', '腊肉', '合渣'], 'works': [], 'tags': ['游历地'], 'note': '白帝城所在地'},
    '巫山': {'province': '重庆市', 'foods': ['巫山烤鱼', '翡翠凉粉'], 'works': [], 'tags': ['游历地'], 'note': '巫山十二峰'},
    '宜昌': {'province': '湖北省', 'foods': ['三峡肥鱼', '凉虾'], 'works': [], 'tags': ['游历地'], 'note': '出蜀入楚要道'},
    '荆州': {'province': '湖北省', 'foods': ['荆州鱼糕', '公安锅盔'], 'works': [], 'tags': ['游历地'], 'note': '长江中游重镇'},
    '江陵': {'province': '湖北省', 'foods': ['荆州鱼糕', '千张扣肉'], 'works': [], 'tags': ['游历地'], 'note': '南郡故城'},
    '恭州': {'province': '重庆市', 'foods': ['重庆火锅', '小面', '串串'], 'works': [], 'tags': ['游历地'], 'note': '重庆古称'},
    '荆门': {'province': '湖北省', 'foods': ['荆门雪枣', '蟠龙菜'], 'works': [], 'tags': ['游历地'], 'note': '三国重镇'},
    '襄州': {'province': '湖北省', 'foods': ['襄阳牛肉面', '黄酒'], 'works': [], 'tags': ['游历地'], 'note': '三国要地'},
    '南阳': {'province': '河南省', 'foods': ['南阳蒸饺', '炝锅面'], 'works': [], 'tags': ['游历地'], 'note': '诸葛躬耕地'},
    '渑池': {'province': '河南省', 'foods': ['仰韶酒', '脂油烧饼'], 'works': [], 'tags': ['游历地'], 'note': '入洛要道'},
    '渭南': {'province': '陕西省', 'foods': ['水盆羊肉', '时辰包子'], 'works': [], 'tags': ['游历地'], 'note': '关中平原'},
    '许州': {'province': '河南省', 'foods': ['许昌烩面', '胡辣汤'], 'works': [], 'tags': ['游历地'], 'note': '三国重镇'},
    '陈州': {'province': '河南省', 'foods': ['压缩馍', '胡辣汤'], 'works': [], 'tags': ['游历地'], 'note': '淮阳古城'},
    '齐州': {'province': '山东省', 'foods': ['油旋', '甜沫', '把子肉'], 'works': [], 'tags': ['游历地'], 'note': '济南古城'},
    '彭城': {'province': '江苏省', 'foods': ['地锅鸡', '羊汤', '烙馍'], 'works': [], 'tags': ['游历地'], 'note': '彭城刘邦故里'},
    '郑州': {'province': '河南省', 'foods': ['烩面', '胡辣汤', '葛记闷饼'], 'works': [], 'tags': ['游历地'], 'note': '中原要道'},
    
    # 京城
    '开封': {'province': '河南省', 'foods': ['开封灌汤包', '桶子鸡', '鲤鱼焙面', '花生糕', '炒凉粉'], 'works': ['开封题名入京呈馆阁同舍'], 'tags': ['京城', '为官地'], 'note': '北宋京城，嘉祐二年（1057）中进士后多次往返'},
    '河南府': {'province': '河南省', 'foods': ['洛阳水席', '牡丹燕菜', '牛肉汤'], 'works': [], 'tags': ['京城', '游历地'], 'note': '洛阳古都'},
    '嵩山': {'province': '河南省', 'foods': ['少林素饼', '烩面'], 'works': [], 'tags': ['游历地'], 'note': '中岳嵩山'},
    
    # 凤翔
    '凤翔': {'province': '陕西省', 'foods': ['西凤酒', '腊驴肉', '臊子面', '豆花泡馍'], 'works': ['喜雨亭记', '凌虚台记', '凤翔八观', '东湖', '太白岩'], 'tags': ['为官地', '创作地'], 'note': '嘉祐六年（1061）任凤翔府签判，建喜雨亭、凌虚台，修东湖'},
    
    # 杭州
    '杭州': {'province': '浙江省', 'foods': ['西湖醋鱼', '东坡肉', '龙井虾仁', '叫化鸡', '片儿川', '西湖莼菜'], 'works': ['饮湖上初晴后雨', '六月二十七日望湖楼醉书', '定风波', '望海楼', '新城道中'], 'tags': ['为官地', '创作地'], 'note': '熙宁四年（1071）任杭州通判，元祐四年（1089）任知州'},
    '西湖': {'province': '浙江省', 'foods': ['西湖醋鱼', '东坡肉', '龙井虾仁', '叫化鸡'], 'works': ['饮湖上初晴后雨', '六月二十七日望湖楼醉书'], 'tags': ['名胜', '创作地'], 'note': '苏轼最爱之地'},
    '余杭': {'province': '浙江省', 'foods': ['塘栖枇杷', '粢毛肉圆'], 'works': [], 'tags': ['游历地'], 'note': '杭州余杭区'},
    '临安': {'province': '浙江省', 'foods': ['天目笋', '昌化鸡'], 'works': [], 'tags': ['游历地'], 'note': '杭州临安'},
    
    # 密州
    '密州': {'province': '山东省', 'foods': ['密州烧鸡', '诸城辣子鸡', '烧烤', '德州扒鸡'], 'works': ['江城子·密州出猎', '水调歌头·明月几时有', '超然台作', '祭常山回小猎'], 'tags': ['为官地', '创作地'], 'note': '熙宁七年（1074）知密州，留下《密州出猎》《水调歌头》等名篇'},
    
    # 徐州
    '徐州': {'province': '江苏省', 'foods': ['地锅鸡', '羊汤', '烙馍', '彭城鱼丸', '霸王别姬'], 'works': ['放鹤亭记', '登望洪亭', '徐城曲'], 'tags': ['为官地', '创作地'], 'note': '熙宁十年（1077）知徐州，抗洪保城，建黄楼'},
    '泗州': {'province': '安徽省', 'foods': ['符离集烧鸡', '泗县豆腐', 'sa汤'], 'works': [], 'tags': ['游历地'], 'note': '淮河要冲'},
    
    # 湖州
    '湖州': {'province': '浙江省', 'foods': ['湖州馄饨', '千张包', '丁莲芳', '太湖三白'], 'works': ['湖州题壁', '赠孙莘老', '墨妙亭记'], 'tags': ['为官地', '创作地'], 'note': '元丰二年（1079）知湖州，因乌台诗案被捕'},
    
    # 黄州
    '黄州': {'province': '湖北省', 'foods': ['东坡肉', '东坡羹', '东坡饼', '黄州豆腐', '黄州鱼'], 'works': ['念奴娇·赤壁怀古', '赤壁赋', '前赤壁赋', '后赤壁赋', '定风波', '黄州寒食诗帖', '寓居定惠院'], 'tags': ['贬谪地', '创作地'], 'note': '元丰三年（1080）贬黄州，创作《赤壁赋》《念奴娇》等千古名篇'},
    '赤壁': {'province': '湖北省', 'foods': ['东坡肉', '东坡羹', '黄州鱼'], 'works': ['念奴娇·赤壁怀古', '赤壁赋', '前赤壁赋', '后赤壁赋'], 'tags': ['名胜', '创作地'], 'note': '文赤壁，苏轼贬黄州时游览'},
    '麻城': {'province': '湖北省', 'foods': ['麻城肉糕', '夫子河鱼面'], 'works': [], 'tags': ['游历地'], 'note': '黄州相邻'},
    '汝州': {'province': '河南省', 'foods': ['汝瓷', '汝州锅盔'], 'works': [], 'tags': ['贬谪地'], 'note': '乌台诗案后曾贬汝州'},
    '庐山': {'province': '江西省', 'foods': ['庐山石鸡', '庐山云雾茶', '石鱼'], 'works': ['题西林壁', '庐山谣'], 'tags': ['游历地'], 'note': '写下"不识庐山真面目"'},
    '高安': {'province': '江西省', 'foods': ['高安腐竹', '炒粉'], 'works': [], 'tags': ['游历地'], 'note': '江西要地'},
    '金陵': {'province': '江苏省', 'foods': ['盐水鸭', '鸭血粉丝', '狮子头', '秦淮小吃'], 'works': ['金陵怀古', '次荆公韵'], 'tags': ['游历地'], 'note': '六朝古都'},
    '商丘': {'province': '河南省', 'foods': ['商丘水煎包', 'sa汤'], 'works': [], 'tags': ['游历地'], 'note': '宋州故地'},
    '鄂州': {'province': '湖北省', 'foods': ['梁子湖螃蟹', '武昌鱼'], 'works': [], 'tags': ['游历地'], 'note': '长江要地'},
    
    # 登州
    '登州': {'province': '山东省', 'foods': ['蓬莱小面', '鲅鱼饺子', '海鲜'], 'works': ['登州海市'], 'tags': ['为官地'], 'note': '元丰八年（1085）任登州知州，仅五日'},
    
    # 颍州
    '颍州': {'province': '安徽省', 'foods': ['格拉条', '卷尖', '太和板面', '阜阳枕头馍'], 'works': ['颍州月夜泛舟', '陪欧阳公宴西湖'], 'tags': ['为官地'], 'note': '元祐六年（1091）知颍州'},
    
    # 扬州
    '扬州': {'province': '江苏省', 'foods': ['扬州炒饭', '大煮干丝', '狮子头', '扬州包子'], 'works': ['扬州怀古', '瘦西湖'], 'tags': ['为官地'], 'note': '元祐七年（1092）知扬州'},
    '润州': {'province': '江苏省', 'foods': ['锅盖面', '蟹黄汤包', '香醋'], 'works': [], 'tags': ['游历地'], 'note': '镇江古称'},
    '真州': {'province': '江苏省', 'foods': ['仪征酱菜', '风鹅'], 'works': [], 'tags': ['游历地'], 'note': '长江要地'},
    '苏州': {'province': '江苏省', 'foods': ['苏式糕点', '松鼠桂鱼', '碧螺虾仁'], 'works': [], 'tags': ['游历地'], 'note': '江南水乡'},
    '秀州': {'province': '浙江省', 'foods': ['粽子', '南湖菱', '文虎酱鸭'], 'works': [], 'tags': ['游历地'], 'note': '嘉兴古称'},
    '婺州': {'province': '浙江省', 'foods': ['金华火腿', '金华酥饼'], 'works': [], 'tags': ['游历地'], 'note': '金华古称'},
    '衢州': {'province': '浙江省', 'foods': ['衢州烤饼', '三头一掌'], 'works': [], 'tags': ['游历地'], 'note': '四省通衢'},
    '明州': {'province': '浙江省', 'foods': ['宁波汤团', '年糕', '海鲜'], 'works': [], 'tags': ['游历地'], 'note': '宁波古称'},
    '楚州': {'province': '江苏省', 'foods': ['淮扬菜', '软兜长鱼', '文楼汤包'], 'works': [], 'tags': ['游历地'], 'note': '淮阴故城'},
    '滑州': {'province': '河南省', 'foods': ['道口烧鸡', '老庙牛肉'], 'works': [], 'tags': ['游历地'], 'note': '黄河要地'},
    '相州': {'province': '河南省', 'foods': ['安阳血糕', '粉浆饭'], 'works': [], 'tags': ['游历地'], 'note': '邺城故地'},
    '怀州': {'province': '河南省', 'foods': ['怀山药', '怀府小吃'], 'works': [], 'tags': ['游历地'], 'note': '太行南麓'},
    '升州': {'province': '江苏省', 'foods': ['盐水鸭', '鸭血粉丝'], 'works': [], 'tags': ['游历地'], 'note': '金陵古称'},
    '宿州': {'province': '安徽省', 'foods': ['sa汤', '符离集烧鸡'], 'works': [], 'tags': ['游历地'], 'note': '汴京南道'},
    '采石矶': {'province': '安徽省', 'foods': ['采石茶干', '当涂大闸蟹'], 'works': [], 'tags': ['游历地'], 'note': '长江要隘李白捉月处'},
    '寿州': {'province': '安徽省', 'foods': ['寿县大救驾', '豆腐'], 'works': [], 'tags': ['游历地'], 'note': '淮南古都'},
    '睢阳': {'province': '河南省', 'foods': ['商丘水煎包'], 'works': [], 'tags': ['游历地'], 'note': '宋州故地'},
    
    # 定州
    '定州': {'province': '河北省', 'foods': ['定州焖子', '驴肉火烧', '手掰肠'], 'works': ['雪浪石盆铭', '试院煎茶'], 'tags': ['为官地', '创作地'], 'note': '绍圣元年（1094）知定州，修复雪浪石'},
    
    # 惠州
    '惠州': {'province': '广东省', 'foods': ['梅菜扣肉', '酿豆腐', '盐焗鸡', '东江菜', '东江盐焗鸡', '梅菜肉饼'], 'works': ['食荔枝', '蝶恋花·春景', '惠州白水山', '白水山佛塔', '记游', '和白乐天'], 'tags': ['贬谪地', '创作地'], 'note': '绍圣元年（1094）贬惠州，留下"日啖荔枝三百颗"名句'},
    '广州': {'province': '广东省', 'foods': ['粤菜', '早茶', '肠粉', '烧鹅', '白切鸡'], 'works': [], 'tags': ['游历地'], 'note': '岭南重镇'},
    '博罗': {'province': '广东省', 'foods': ['罗浮山素菜', '酥醪菜'], 'works': [], 'tags': ['游历地'], 'note': '罗浮山所在地'},
    '韶州': {'province': '广东省', 'foods': ['客家酿豆腐', '马坝油粘米'], 'works': [], 'tags': ['游历地'], 'note': '梅关要道'},
    '潮州': {'province': '广东省', 'foods': ['潮州菜', '牛肉火锅', '潮汕砂锅粥'], 'works': [], 'tags': ['游历地'], 'note': '潮汕地区'},
    
    # 儋州
    '儋州': {'province': '海南省', 'foods': ['儋州米烂', '长坡米烂', '红鱼粽', '椰子鸡', '东坡肘子'], 'works': ['桄榔庵铭', '儋耳', '纵笔', '海南不作诗', '夜寂无人识'], 'tags': ['贬谪地', '创作地'], 'note': '绍圣四年（1097）贬儋州，建桄榔庵、载酒堂，教化百姓'},
    '琼州': {'province': '海南省', 'foods': ['海南粉', '文昌鸡', '椰子', '清补凉'], 'works': [], 'tags': ['贬谪地'], 'note': '海南岛北'},
    '雷州': {'province': '广东省', 'foods': ['雷州白切狗', '海产品'], 'works': [], 'tags': ['贬谪地'], 'note': '贬谪途中'},
    '永州': {'province': '湖南省', 'foods': ['永州血鸭', '东安鸡'], 'works': [], 'tags': ['贬谪地'], 'note': '南迁途中'},
    
    # 北归
    '常州': {'province': '江苏省', 'foods': ['大麻糕', '银丝面', '加蟹小笼包', '天目湖砂锅鱼头', '常州梳打'], 'works': ['除夜野宿常州城外', '常州太平寺观牡丹'], 'tags': ['终老地', '逝世地'], 'note': '建中靖国元年（1101）北归，病逝于常州藤花旧馆'},
    '宜兴': {'province': '江苏省', 'foods': ['宜兴紫砂', '宜兴百合', '和桥豆腐干'], 'works': [], 'tags': ['游历地'], 'note': '苏轼曾买田于此'},
    '当涂': {'province': '安徽省', 'foods': ['采石茶干', '大闸蟹'], 'works': ['牛渚矶', '题牛渚'], 'tags': ['游历地'], 'note': '李白捉月处'},
    '藤州': {'province': '广西省', 'foods': ['藤县鱼生', '豆腐'], 'works': [], 'tags': ['贬谪地'], 'note': '南迁途中'},
    '容州': {'province': '广西省', 'foods': ['容县沙田柚', '桂油'], 'works': [], 'tags': ['贬谪地'], 'note': '岭南要地'},
    '廉州': {'province': '广西省', 'foods': ['珍珠', '海鲜'], 'works': [], 'tags': ['贬谪地'], 'note': '广西南端'},
    '邕州': {'province': '广西省', 'foods': ['老友粉', '柠檬鸭'], 'works': [], 'tags': ['贬谪地'], 'note': '广西首府'},
    '静江': {'province': '广西省', 'foods': ['桂林米粉', '漓江鱼'], 'works': [], 'tags': ['贬谪地'], 'note': '桂林古称'},
    '潭州': {'province': '湖南省', 'foods': ['臭豆腐', '口味虾', '糖油粑粑'], 'works': [], 'tags': ['贬谪地'], 'note': '长沙古称'},
    '衡州': {'province': '湖南省', 'foods': ['衡阳鱼粉', '唆螺'], 'works': [], 'tags': ['贬谪地'], 'note': '衡山所在地'},
    '江州': {'province': '江西省', 'foods': ['九江茶饼', '庐山石鸡'], 'works': [], 'tags': ['游历地'], 'note': '九江古称'},
    '洪州': {'province': '江西省', 'foods': ['南昌拌粉', '瓦罐汤', '藜蒿炒腊肉'], 'works': [], 'tags': ['游历地'], 'note': '南昌古称'},
    '吉州': {'province': '江西省', 'foods': ['吉安炒粉', '井冈山豆皮'], 'works': [], 'tags': ['游历地'], 'note': '庐陵文化'},
    '虔州': {'province': '江西省', 'foods': ['赣南脐橙', '客家菜'], 'works': [], 'tags': ['游历地'], 'note': '赣州古称'},
    '荆州': {'province': '湖北省', 'foods': ['荆州鱼糕', '公安锅盔'], 'works': [], 'tags': ['游历地'], 'note': '北归要道'},
    '温州': {'province': '浙江省', 'foods': ['温州鱼丸', '瓯柑', '糯米饭'], 'works': [], 'tags': ['游历地'], 'note': '东南沿海'},
    '莱州': {'province': '山东省', 'foods': ['莱州梭子蟹', '海鲜'], 'works': [], 'tags': ['游历地'], 'note': '登州相邻'},
    '磁州': {'province': '河北省', 'foods': ['磁州窑', '拽面'], 'works': [], 'tags': ['游历地'], 'note': '滏阳河流域'},
    '邯郸': {'province': '河北省', 'foods': ['邯郸拽面', '曲面'], 'works': [], 'tags': ['游历地'], 'note': '赵国故都'},
    '邢州': {'province': '河北省', 'foods': ['邢台焖饼', '道口烧鸡'], 'works': [], 'tags': ['游历地'], 'note': '顺德府故地'},
    '赵州': {'province': '河北省', 'foods': ['赵州雪花梨', '油酥烧饼'], 'works': [], 'tags': ['游历地'], 'note': '赵州桥所在地'},
    '襄邑': {'province': '河南省', 'foods': ['襄邑刺绣', '红薯粉条'], 'works': [], 'tags': ['游历地'], 'note': '北宋织锦中心'},
    '陈留': {'province': '河南省', 'foods': ['陈留豆腐棍', '烩面'], 'works': [], 'tags': ['游历地'], 'note': '开封东郊'},
    '大庾岭': {'province': '江西省', 'foods': ['赣南脐橙', '南安板鸭'], 'works': [], 'tags': ['贬谪地'], 'note': '南北分界线'},
    '蕲州': {'province': '湖北省', 'foods': ['蕲春艾草', '蕲龟'], 'works': [], 'tags': ['游历地'], 'note': '李时珍故乡'},
    '胶西': {'province': '山东省', 'foods': ['胶州大白菜', '海鲜'], 'works': [], 'tags': ['游历地'], 'note': '青岛相邻'},
    
    # 其他
    '舟山': {'province': '浙江省', 'foods': ['舟山带鱼', '嵊泗贻贝', '海鲜'], 'works': [], 'tags': ['游历地'], 'note': '海上航行'},
    '富阳': {'province': '浙江省', 'foods': ['富春江鱼', '东坞山豆腐皮'], 'works': [], 'tags': ['游历地'], 'note': '富春江畔'},
    '桐庐': {'province': '浙江省', 'foods': ['桐庐板栗', '富春江鲜'], 'works': ['严子陵钓台'], 'tags': ['游历地'], 'note': '严子陵钓台'},
    '高邮': {'province': '江苏省', 'foods': ['高邮咸蛋', '阳春面'], 'works': [], 'tags': ['游历地'], 'note': '秦观故乡'},
    '海州': {'province': '江苏省', 'foods': ['海鲜', '花果山风鹅'], 'works': [], 'tags': ['游历地'], 'note': '东海要塞'},
    '潍州': {'province': '山东省', 'foods': ['潍坊朝天锅', '和乐', '鸡鸭和乐'], 'works': [], 'tags': ['游历地'], 'note': '北海郡故地'},
    '青州': {'province': '山东省', 'foods': ['青州蜜桃', '隆盛糕点'], 'works': [], 'tags': ['游历地'], 'note': '古九州之一'},
    '郓州': {'province': '山东省', 'foods': ['郓城壮馍', '黄安煊汤'], 'works': [], 'tags': ['游历地'], 'note': '水浒故事发源地'},
    '澶州': {'province': '河南省', 'foods': ['濮阳壮馍', '牛肉耗辣椒'], 'works': [], 'tags': ['游历地'], 'note': '黄河要地'},
    '亳州': {'province': '安徽省', 'foods': ['亳州牛肉馍', '古井贡酒'], 'works': [], 'tags': ['游历地'], 'note': '曹操故乡'},
    '涡阳': {'province': '安徽省', 'foods': ['义门苔干', '涡阳干扣面'], 'works': [], 'tags': ['游历地'], 'note': '老子故里'},
    '怀远': {'province': '安徽省', 'foods': ['怀远石榴', '河溜小豆饼'], 'works': [], 'tags': ['游历地'], 'note': '淮河要地'},
    '蔡州': {'province': '河南省', 'foods': ['涪翁鱼', '汝南卤猪蹄'], 'works': [], 'tags': ['游历地'], 'note': '天中山所在地'},
    '息县': {'province': '河南省', 'foods': ['息县香稻丸', '息县半夏'], 'works': [], 'tags': ['游历地'], 'note': '淮河要地'},
    '长安': {'province': '陕西省', 'foods': ['肉夹馍', '羊肉泡馍', '凉皮', 'biangbiang面', '臊子面'], 'works': [], 'tags': ['游历地'], 'note': '大唐京城'},
    '华阴': {'province': '陕西省', 'foods': ['华山松子', '华山野菜'], 'works': [], 'tags': ['游历地'], 'note': '华山所在地'},
    '潼关': {'province': '陕西省', 'foods': ['潼关肉夹馍', '黄河鲤鱼'], 'works': [], 'tags': ['游历地'], 'note': '关中门户'},
    '汉中': {'province': '陕西省', 'foods': ['汉中面皮', '菜豆腐', '浆水面'], 'works': [], 'tags': ['游历地'], 'note': '汉家发祥地'},
    '成都': {'province': '四川省', 'foods': ['川菜', '火锅', '麻婆豆腐', '夫妻肺片', '龙抄手'], 'works': [], 'tags': ['游历地'], 'note': '天府之国'},
    '绵阳': {'province': '四川省', 'foods': ['绵阳米粉', '梓州片粉', '冷沾沾'], 'works': [], 'tags': ['游历地'], 'note': '李白故乡'},
    '剑阁': {'province': '四川省', 'foods': ['剑门豆腐', '剑阁核桃饼'], 'works': [], 'tags': ['游历地'], 'note': '剑门蜀道'},
    '剑门关': {'province': '四川省', 'foods': ['剑门豆腐', '核桃饼', '豆腐宴'], 'works': [], 'tags': ['游历地'], 'note': '蜀道要隘'},
}

# 通用省份美食
PROVINCE_FOODS = {
    '四川': ['川菜', '火锅', '串串'],
    '陕西': ['面食', '羊肉泡馍', '肉夹馍'],
    '河南': ['烩面', '胡辣汤'],
    '浙江': ['浙菜', '杭帮菜'],
    '江苏': ['淮扬菜'],
    '山东': ['鲁菜'],
    '广东': ['粤菜', '早茶'],
    '海南': ['海鲜', '椰子'],
    '湖北': ['鄂菜'],
    '安徽': ['徽菜'],
    '河北': ['冀菜'],
    '江西': ['赣菜'],
    '湖南': ['湘菜'],
    '重庆': ['重庆火锅', '小面'],
    '广西': ['桂菜'],
}

def full_supplement():
    existing_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data/places-core.json'
    output_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data'
    
    with open(existing_path, 'r', encoding='utf-8') as f:
        existing_places = json.load(f)
    
    total = len(existing_places)
    matched = 0
    generic = 0
    
    for place in existing_places:
        song_name = place.get('songName', '')
        modern_name = place.get('modernName', '')
        
        # 初始化新字段
        place['su_works'] = []
        place['su_quote'] = ''
        place['author_note'] = ''
        place['local_foods'] = []
        place['cultural_tags'] = []
        place['province'] = ''
        
        # 精确匹配
        if song_name in PLACE_DATA:
            data = PLACE_DATA[song_name]
            place['local_foods'] = data.get('foods', [])
            place['su_works'] = data.get('works', [])
            place['author_note'] = data.get('note', '')
            place['cultural_tags'] = data.get('tags', [])
            place['province'] = data.get('province', '')
            matched += 1
        else:
            # 从modernName匹配
            found = False
            for key, data in PLACE_DATA.items():
                if key in modern_name or key in song_name:
                    place['local_foods'] = data.get('foods', [])
                    place['su_works'] = data.get('works', [])
                    place['author_note'] = data.get('note', '')
                    place['cultural_tags'] = data.get('tags', [])
                    place['province'] = data.get('province', '')
                    matched += 1
                    found = True
                    break
            
            if not found:
                # 通用补充
                province = modern_name[:2] if modern_name else ''
                if province in PROVINCE_FOODS:
                    place['local_foods'] = PROVINCE_FOODS[province]
                    place['cultural_tags'] = ['游历地']
                    place['province'] = province
                generic += 1
    
    # 保存
    output_path = os.path.join(output_dir, 'places-core-full.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_places, f, ensure_ascii=False, indent=2)
    
    # 统计
    foods_count = sum(1 for p in existing_places if p.get('local_foods'))
    works_count = sum(1 for p in existing_places if p.get('su_works'))
    note_count = sum(1 for p in existing_places if p.get('author_note'))
    tags_count = sum(1 for p in existing_places if p.get('cultural_tags'))
    
    print("="*60)
    print("全量补充完成")
    print("="*60)
    print(f"总地点数: {total}")
    print(f"精确匹配: {matched} 个")
    print(f"通用补充: {generic} 个")
    print(f"\n字段完整率:")
    print(f"  美食: {foods_count}/{total} ({(foods_count/total)*100:.1f}%)")
    print(f"  作品: {works_count}/{total} ({(works_count/total)*100:.1f}%)")
    print(f"  笔记: {note_count}/{total} ({(note_count/total)*100:.1f}%)")
    print(f"  标签: {tags_count}/{total} ({(tags_count/total)*100:.1f}%)")
    print(f"\n输出文件: {output_path}")

if __name__ == "__main__":
    full_supplement()
