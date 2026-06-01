#!/usr/bin/env python3
"""
苏轼行踪数据库构建脚本 V3
支持全局+路线特定数据分离

每个地点有全局唯一ID，全局事件/著作在所有路线中显示，
路线特定事件/著作按route_id区分，景点、美食等可复用。
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Work:
    """作品"""
    id: str
    title: str
    content: str
    excerpt: str
    type: str
    date: Optional[str] = None
    location: Optional[str] = None
    background: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemorialSite:
    """纪念景点"""
    id: str
    name: str
    type: str
    location: str
    description: str
    opening_hours: str = ""
    ticket: str = ""
    suggested_duration: str = ""
    photos: List[str] = field(default_factory=list)
    url: str = ""
    rating: str = ""
    distance: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Food:
    """特色美食"""
    id: str
    name: str
    description: str
    origin_story: str = ""
    restaurants: List[str] = field(default_factory=list)
    price_range: str = ""
    tag: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Transport:
    """交通指引"""
    train: str = ""
    bus: str = ""
    car: str = ""
    airport: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Event:
    """事件"""
    id: str
    date: str
    title: str
    description: str
    significance: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SubPlace:
    """子地点/小景点"""
    id: str
    name_song: str
    name_modern: str
    latitude: float
    longitude: float
    parent_place_id: str
    type: str = ""
    summary: str = ""
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PlaceDetail:
    """
    地点详情 V3
    支持全局+路线特定数据分离
    """
    place_id: str
    name_song: str
    name_modern: str
    name_pinyin: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    place_type: str = ""
    tags: List[str] = field(default_factory=list)
    summary: str = ""
    background: str = ""
    global_events: List[Event] = field(default_factory=list)
    global_works: List[Work] = field(default_factory=list)
    route_events: Dict[str, List[Event]] = field(default_factory=dict)
    route_works: Dict[str, List[Work]] = field(default_factory=dict)
    route_order: Dict[str, int] = field(default_factory=dict)
    route_arrival: Dict[str, str] = field(default_factory=dict)
    route_departure: Dict[str, str] = field(default_factory=dict)
    route_duration: Dict[str, int] = field(default_factory=dict)
    memorial_sites: List[MemorialSite] = field(default_factory=list)
    foods: List[Food] = field(default_factory=list)
    transport: Transport = field(default_factory=Transport)
    sub_places: List[SubPlace] = field(default_factory=list)
    source: str = ""

    def get_all_events(self, route_id: str = None) -> List[Event]:
        events = list(self.global_events)
        if route_id and route_id in self.route_events:
            events.extend(self.route_events[route_id])
        return events

    def get_all_works(self, route_id: str = None) -> List[Work]:
        works = list(self.global_works)
        if route_id and route_id in self.route_works:
            works.extend(self.route_works[route_id])
        return works

    def to_dict(self) -> dict:
        result = asdict(self)
        result['global_events'] = [e.to_dict() for e in self.global_events]
        result['global_works'] = [w.to_dict() for w in self.global_works]
        for key in result['route_events']:
            result['route_events'][key] = [e.to_dict() for e in self.route_events[key]]
        for key in result['route_works']:
            result['route_works'][key] = [w.to_dict() for w in self.route_works[key]]
        result['memorial_sites'] = [s.to_dict() for s in self.memorial_sites]
        result['foods'] = [f.to_dict() for f in self.foods]
        result['transport'] = self.transport.to_dict() if self.transport else {}
        result['sub_places'] = [sp.to_dict() for sp in self.sub_places]
        return result


def create_meishan() -> PlaceDetail:
    """眉山 - 出生地"""
    memorial_sites = [
        MemorialSite(id="ms-s001", name="三苏祠", type="祠堂",
                     location="四川省眉山市东坡区纱縠行南街86号",
                     description="三苏父子故居及祠堂，全国重点文物保护单位",
                     opening_hours="全年 09:00-18:00", ticket="¥40",
                     suggested_duration="2-3小时", distance="市中心",
                     url="https://www.sscbwg.com/"),
        MemorialSite(id="ms-s002", name="纱縠行", type="历史街区",
                     location="四川省眉山市东坡区",
                     description="宋代苏家老宅所在地，丝绸布匹交易市场",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    return PlaceDetail(
        place_id="meishan",
        name_song="眉州/眉山",
        name_modern="四川省眉山市",
        name_pinyin="Meishan",
        latitude=30.0574,
        longitude=103.8486,
        place_type="出生/安葬",
        tags=["出生地", "故乡", "三苏祠"],
        summary="苏轼出生地，在此生活约32年直至进京科举",
        background="眉山是苏轼的出生地和故乡，纱縠行是苏家老宅所在地",
        global_events=[
            Event(id="ms-001", date="景祐三年（1037年）十二月十九日",
                  title="苏轼出生", description="苏轼生于眉山县纱縠行私第",
                  significance="北宋文学巨匠诞生"),
            Event(id="ms-004", date="治平三年（1066年）四月",
                  title="护送父丧归蜀", description="苏洵在汴京去世，苏轼兄弟护送灵柩归眉安葬",
                  significance="回乡守孝"),
        ],
        route_events={
            "route01": [
                Event(id="ms-002", date="嘉祐元年（1056年）三月",
                      title="第一次出蜀赴京",
                      description="苏轼随父苏洵、弟苏辙从眉山出发，经成都赴汴京参加科举考试",
                      significance="人生转折点"),
            ],
            "route02": [
                Event(id="ms-005", date="熙宁元年（1068年）十二月",
                      title="第二次出蜀赴京",
                      description="为父苏洵守丧期满后，苏轼携家眷从眉山出发，第二次出蜀",
                      significance="重返仕途，永别故乡"),
            ],
            "route05": [
                Event(id="ms-006", date="熙宁元年（1068年）十一二月",
                      title="第四次出蜀赴京",
                      description="为父苏洵守丧期满后，苏轼携家眷从眉山出发，第四次出蜀",
                      significance="永别故乡，再未归乡"),
            ],
        },
        route_order={"route01": 1, "route02": 1, "route05": 1},
        route_arrival={"route01": "1037年1月8日", "route02": "熙宁元年十二月", "route05": "熙宁元年十一十二月"},
        route_departure={"route01": "嘉祐元年（1056年）三月", "route02": "熙宁元年（1068年）十二月", "route05": "熙宁元年（1068年）十一十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="眉山站 / 眉山东站", bus="眉山客运中心", car="成乐高速"),
        source="李常生《苏轼行踪考》"
    )


def create_chengdu() -> PlaceDetail:
    """成都 - 游历地"""
    memorial_sites = [
        MemorialSite(id="cd-s001", name="三苏纪念馆", type="博物馆",
                     location="四川省成都市青羊区",
                     description="展示三苏生平",
                     opening_hours="09:00-17:00", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="chengdu",
        name_song="益州/成都",
        name_modern="四川省成都市",
        name_pinyin="Chengdu",
        latitude=30.5728,
        longitude=104.0668,
        place_type="游历地",
        tags=["游历地", "途经"],
        summary="三苏出蜀途经成都，拜访亲友",
        background="成都是四川首府，三苏从眉州出蜀必经过成都",
        global_events=[
            Event(id="cd-001", date="嘉祐元年（1056年）三月",
                  title="第一次到成都",
                  description="三苏出蜀途经成都，拜访成都知府王素（王龙图）",
                  significance="途经成都"),
        ],
        route_events={
            "route01": [
                Event(id="cd-002", date="嘉祐四年（1059年）十月",
                      title="第二次到成都",
                      description="苏轼兄弟南下嘉州，途经成都，与亲友欢聚",
                      significance="途经成都"),
            ],
            "route02": [
                Event(id="cd-003", date="熙宁元年（1068年）十二月",
                      title="第三次到成都",
                      description="苏轼第二次出蜀，途经成都，与亲友告别",
                      significance="途经成都"),
            ],
        },
        route_order={"route01": 2, "route02": 2},
        route_arrival={"route01": "嘉祐元年（1056年）三月", "route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="成都站 / 成都东站", bus="成都新南门汽车站",
                           car="成渝高速 / 京昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_langzhong() -> PlaceDetail:
    """阆中 - 游历地"""
    memorial_sites = [
        MemorialSite(id="lz-s001", name="阆中古城", type="古城",
                     location="四川省阆中市",
                     description="中国四大古城之一，有2300多年历史",
                     opening_hours="全天开放", ticket="古城免费，景点联票¥120",
                     suggested_duration="1-2天", rating="AAAAA"),
        MemorialSite(id="lz-s002", name="状元洞", type="遗址",
                     location="四川省阆中市城东嘉陵江对岸东山园林",
                     description="北宋三陈少时读书处，洞口有苏轼手书'将相堂'",
                     opening_hours="08:00-18:00", ticket="包含在景点联票内"),
    ]

    return PlaceDetail(
        place_id="langzhong",
        name_song="阆州/阆中",
        name_modern="四川省阆中市",
        name_pinyin="Langzhong",
        latitude=31.5518,
        longitude=106.1228,
        place_type="游历地",
        tags=["阆中", "苏涣", "科举"],
        summary="苏轼三次经过阆中，伯父苏涣曾在此任官",
        background="阆中是苏轼伯父苏涣长期为官之地，苏轼多次在此停留，留有'将相堂'等题字",
        global_events=[
            Event(id="lz-001", date="嘉祐元年（1056年）三月",
                  title="第一次过阆中",
                  description="三苏从成都出发，经阆中翻越米仓山，沿褒斜道入关中",
                  significance="route01争议点"),
        ],
        route_events={
            "route01": [
                Event(id="lz-002", date="治平三年（1066年）四月",
                      title="护送父丧归蜀",
                      description="苏洵在汴京去世，苏轼兄弟护送灵柩归蜀，途经阆中",
                      significance="第二次经过阆中"),
            ],
            "route02": [
                Event(id="lz-003", date="熙宁元年（1068年）十二月",
                      title="第三次过阆中",
                      description="为父丧服满，苏轼兄弟携眷返京，再次途经阆中",
                      significance="最后一次经过阆中"),
            ],
        },
        route_order={"route01": 3, "route02": 5},
        route_arrival={"route01": "嘉祐元年（1056年）三月", "route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        foods=[Food(id="lz-f001", name="张飞牛肉", description="阆中特产名吃",
                    origin_story="阆中传统美食", price_range="¥50-100/斤")],
        transport=Transport(train="阆中站", bus="阆中客运中心", car="G75兰海高速"),
        source="李常生《苏轼行踪考》"
    )


def create_jianmen() -> PlaceDetail:
    """剑门关 - 游历地"""
    memorial_sites = [
        MemorialSite(id="jm-s001", name="剑门关", type="关隘",
                     location="四川省广元市剑阁县",
                     description="蜀道第一关，自古兵家必争之地",
                     opening_hours="08:00-18:00", ticket="¥100",
                     suggested_duration="2-3小时", rating="AAAAA"),
    ]

    return PlaceDetail(
        place_id="jianmen",
        name_song="剑门关",
        name_modern="四川省广元市剑阁县",
        name_pinyin="Jianmen",
        latitude=32.2249,
        longitude=105.4919,
        place_type="游历地",
        tags=["蜀道", "剑门"],
        summary="蜀道第一关，三苏出蜀必经之地",
        background="剑门关是蜀道第一关，自古兵家必争之地，三苏出蜀必过剑门",
        global_events=[
            Event(id="jm-001", date="嘉祐元年（1056年）三月",
                  title="第一次过剑门关",
                  description="三苏出蜀途经剑门关，这是蜀道第一关",
                  significance="蜀道第一关"),
        ],
        route_events={
            "route01": [
                Event(id="jm-002", date="嘉祐元年（1056年）三月",
                      title="第一次过剑门关",
                      description="三苏出蜀途经剑门关",
                      significance="蜀道第一关"),
            ],
            "route02": [
                Event(id="jm-003", date="熙宁元年（1068年）十二月",
                      title="第二次过剑门关",
                      description="苏轼第二次出蜀，途经剑门关",
                      significance="蜀道第一关"),
            ],
        },
        route_order={"route01": 4, "route02": 6},
        route_arrival={"route01": "嘉祐元年（1056年）三月", "route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="剑门关站", bus="剑阁汽车站", car="京昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_lizhou() -> PlaceDetail:
    """利州/昭化 - 游历地"""
    memorial_sites = [
        MemorialSite(id="lz2-s001", name="昭化古城", type="古城",
                     location="四川省广元市昭化区",
                     description="蜀道重要节点，有2000多年历史",
                     opening_hours="全天", ticket="¥58", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="lizhou",
        name_song="利州/益昌",
        name_modern="四川省广元市昭化区",
        name_pinyin="Lizhou",
        latitude=32.2947,
        longitude=105.8148,
        place_type="游历地",
        tags=["蜀道", "利州"],
        summary="蜀道重要节点，三苏出蜀必经之地",
        background="利州（今昭化）是蜀道重要节点，自古交通要道",
        global_events=[
            Event(id="lz2-001", date="嘉祐元年（1056年）三月",
                  title="第一次过利州",
                  description="三苏出蜀途经利州（昭化），是蜀道重要节点",
                  significance="蜀道节点"),
        ],
        route_events={
            "route01": [
                Event(id="lz2-002", date="嘉祐元年（1056年）三月",
                      title="第一次过利州",
                      description="三苏出蜀途经利州（昭化）",
                      significance="蜀道节点"),
            ],
            "route02": [
                Event(id="lz2-003", date="熙宁元年（1068年）十二月",
                      title="第二次过利州",
                      description="苏轼第二次出蜀，途经利州",
                      significance="蜀道节点"),
            ],
        },
        route_order={"route01": 5, "route02": 7},
        route_arrival={"route01": "嘉祐元年（1056年）三月", "route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="广元站", bus="昭化客运中心", car="京昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_fengxiang() -> PlaceDetail:
    """凤翔府 - 游历地/任职地"""
    memorial_sites = [
        MemorialSite(id="fx-s001", name="凤翔东湖", type="公园",
                     location="陕西省宝鸡市凤翔区",
                     description="苏轼在凤翔时疏浚的湖，纪念苏轼",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
        MemorialSite(id="fx-s002", name="凤鸣驿", type="驿站",
                     location="陕西省宝鸡市凤翔区",
                     description="苏轼《凤鸣驿记》记载的驿站",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
        MemorialSite(id="fx-s003", name="仙游潭中兴寺", type="寺庙",
                     location="陕西省宝鸡市凤翔区",
                     description="苏轼《留题仙游潭中兴寺》，有玉女洞、马融读书石室",
                     opening_hours="全天", ticket="免费", suggested_duration="2小时"),
    ]

    works = [
        Work(id="fx-w001", title="留题仙游潭中兴寺",
             content="清潭百丈皎无泥，山木阴阴谷鸟啼。蜀客曾游明月峡，秦人今在武陵溪。独攀书室窥岩窦，还访仙姝欸石闺。犹有爱山心未至，不将双脚踏飞梯。",
             excerpt="清潭百丈皎无泥，山木阴阴谷鸟啼。",
             type="诗", date="嘉祐七年（1062年）三月",
             location="凤翔府仙游潭中兴寺",
             background="游仙游潭中兴寺作"),
    ]

    return PlaceDetail(
        place_id="fengxiang",
        name_song="凤翔府",
        name_modern="陕西省宝鸡市凤翔区",
        name_pinyin="Fengxiang",
        latitude=34.5228,
        longitude=107.4046,
        place_type="游历地/任职地",
        tags=["凤翔", "仕途起点", "签判"],
        summary="苏轼任凤翔府签判两年，这是他正式仕途起点",
        background="凤翔府是关中重要城市，苏轼嘉祐六年任大理评事签书凤翔府判官，在此期间创作多篇诗文",
        global_events=[
            Event(id="fx-001", date="嘉祐元年（1056年）",
                  title="第一次过凤翔",
                  description="三苏出蜀途经凤翔府，是关中重要城市",
                  significance="途经凤翔"),
        ],
        global_works=works,
        route_events={
            "route01": [
                Event(id="fx-002", date="嘉祐六年（1061年）十一月",
                      title="赴任凤翔签判",
                      description="苏轼任大理评事签书凤翔府判官，正式开始仕途",
                      significance="仕途起点"),
            ],
            "route04": [
                Event(id="fx-003", date="熙宁元年（1068年）十一二月",
                      title="第四次出蜀过凤翔",
                      description="苏轼第四次出蜀，途经凤翔",
                      significance="途经凤翔"),
            ],
        },
        route_order={"route01": 6, "route02": 8, "route04": 3},
        route_arrival={"route01": "嘉祐元年（1056年）", "route02": "熙宁元年（1068年）十二月", "route04": "熙宁元年（1068年）十一二月"},
        route_departure={"route01": "嘉祐六年（1061年）十一月", "route02": "熙宁二年（约1069年）", "route04": "熙宁元年（1068年）十一二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="凤翔站 / 宝鸡站", bus="凤翔汽车站", car="连霍高速"),
        source="李常生《苏轼行踪考》"
    )


def create_changan() -> PlaceDetail:
    """长安/京兆府 - 游历地"""
    memorial_sites = [
        MemorialSite(id="ca-s001", name="西安碑林", type="博物馆",
                     location="陕西省西安市",
                     description="全国最大石质书库，有苏轼书法碑刻",
                     opening_hours="08:00-18:00", ticket="¥65",
                     suggested_duration="2-3小时", rating="AAAAA"),
    ]

    return PlaceDetail(
        place_id="changan",
        name_song="京兆府/长安",
        name_modern="陕西省西安市",
        name_pinyin="Chang'an",
        latitude=34.3416,
        longitude=108.9398,
        place_type="游历地",
        tags=["长安", "古都"],
        summary="北宋西北重镇，三苏出蜀途经长安",
        background="长安是汉唐古都，北宋时称京兆府，是西北重镇",
        global_events=[
            Event(id="ca-001", date="嘉祐元年（1056年）",
                  title="第一次到长安",
                  description="三苏出蜀途经长安，这是北宋西北重镇",
                  significance="途经长安"),
        ],
        route_events={
            "route01": [
                Event(id="ca-002", date="嘉祐元年（1056年）",
                      title="第一次到长安",
                      description="三苏出蜀途经长安",
                      significance="途经长安"),
            ],
            "route02": [
                Event(id="ca-003", date="熙宁元年（1068年）十二月",
                      title="第二次到长安",
                      description="苏轼第二次出蜀，途经长安",
                      significance="途经长安"),
            ],
            "route04": [
                Event(id="ca-004", date="熙宁元年（1068年）十二月",
                      title="第四次出蜀过长安",
                      description="苏轼第四次出蜀，途经长安，与友人会面",
                      significance="途经长安"),
            ],
        },
        route_order={"route01": 7, "route02": 9, "route04": 4},
        route_arrival={"route01": "嘉祐元年（1056年）", "route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="西安站 / 西安北站", bus="西安城南客运站",
                           car="京昆高速 / 连霍高速"),
        source="李常生《苏轼行踪考》"
    )


def create_mianchi() -> PlaceDetail:
    """渑池 - 游历地"""
    memorial_sites = [
        MemorialSite(id="mc-s001", name="秦赵会盟台", type="遗址",
                     location="河南省渑池县",
                     description="战国时期秦赵会盟之地",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    works = [
        Work(id="mc-w001", title="和子由渑池怀旧",
             content="人生到处知何似，应似飞鸿踏雪泥。泥上偶然留指爪，鸿飞那复计东西。老僧已死成新塔，坏壁无由见旧题。往日崎岖还记否，路长人困蹇驴嘶。",
             excerpt="人生到处知何似，应似飞鸿踏雪泥。",
             type="诗", date="嘉祐六年（1061年）十一月",
             location="渑池",
             background="与苏辙分别后过渑池作，表达对往事的感怀"),
    ]

    return PlaceDetail(
        place_id="mianchi",
        name_song="渑池",
        name_modern="河南省渑池县",
        name_pinyin="Mianchi",
        latitude=34.7670,
        longitude=111.7642,
        place_type="游历地",
        tags=["怀旧", "名篇", "渑池"],
        summary="苏轼两次经过渑池，留下名篇《和子由渑池怀旧》",
        background="'人生到处知何似，应似飞鸿踏雪泥' - 苏轼在渑池写下这篇千古名篇",
        global_events=[
            Event(id="mc-001", date="嘉祐元年（1056年）",
                  title="第一次过渑池",
                  description="三苏出蜀途经渑池",
                  significance="途经渑池"),
        ],
        global_works=works,
        route_events={
            "route01": [
                Event(id="mc-002", date="嘉祐六年（1061年）十一月",
                      title="赴凤翔任途中",
                      description="苏轼任大理评事签书凤翔府判官，送苏辙至郑州西门外别后，经渑池一路西行",
                      significance="名作《和子由渑池怀旧》创作地"),
            ],
        },
        route_order={"route01": 8, "route02": 10},
        route_arrival={"route01": "嘉祐元年（1056年）", "route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="渑池站 / 渑池南站", bus="渑池汽车站", car="连霍高速"),
        source="李常生《苏轼行踪考》"
    )


def create_bianjing() -> PlaceDetail:
    """汴京/东京 - 仕途地"""
    memorial_sites = [
        MemorialSite(id="bj-s001", name="开封相国寺", type="寺庙",
                     location="河南省开封市鼓楼区自由路西段",
                     description="中国十大名寺之一，北宋皇家寺院",
                     opening_hours="08:00-18:00", ticket="¥45",
                     suggested_duration="1-2小时", rating="AAAA"),
        MemorialSite(id="bj-s002", name="开封府", type="遗址",
                     location="河南省开封市",
                     description="北宋开封府衙，包拯曾在此任知府",
                     opening_hours="08:00-18:00", ticket="¥65",
                     suggested_duration="2小时", rating="AAAA"),
    ]

    works = [
        Work(id="bj-w001", title="兴国寺浴室院六祖画赞",
             content="嘉祐元年十一月，轼自蜀来，始与子由过此观六祖之像。",
             excerpt="六祖之像，在浴室院。",
             type="文", date="嘉祐元年（1056年）十一月",
             location="汴京兴国寺浴室院",
             background="在兴国寺浴室院观六祖画像作"),
    ]

    return PlaceDetail(
        place_id="bianjing",
        name_song="汴京/东京",
        name_modern="河南省开封市",
        name_pinyin="Bianjing",
        latitude=34.8037,
        longitude=114.3126,
        place_type="仕途地",
        tags=["都城", "科举", "兴国寺"],
        summary="北宋都城，三苏在此科举及第，名动京师",
        background="汴京是北宋都城，今河南开封，三苏在此科举及第，名动京师",
        global_events=[
            Event(id="bj-001", date="嘉祐元年（1056年）五六月间",
                  title="初到汴京",
                  description="三苏到汴京，寓居兴国寺浴室院，京师遇大雨，蔡河中夜决",
                  significance="初到京师"),
            Event(id="bj-002", date="嘉祐二年（1057年）三月",
                  title="科举及第",
                  description="欧阳修知贡举，苏轼、苏辙兄弟同登进士第，名动京师",
                  significance="仕途起点"),
        ],
        global_works=works,
        route_events={
            "route01": [
                Event(id="bj-003", date="嘉祐二年（1057年）四月",
                      title="母丧归蜀",
                      description="程夫人在眉山去世，三苏奔丧归蜀",
                      significance="回乡守孝"),
            ],
            "route04": [
                Event(id="bj-004", date="熙宁二年（1069年）二月初",
                      title="第四次抵达汴京",
                      description="苏轼第四次入京，抵达汴京",
                      significance="重返京师"),
                Event(id="bj-005", date="熙宁二年（1069年）",
                      title="居南园",
                      description="苏轼在南园居住，在宜秋门内",
                      significance="汴京居所"),
                Event(id="bj-006", date="熙宁二年（1069年）",
                      title="任判官告院兼尚书祠部",
                      description="除判官告院兼判尚书祠部，王安石方用事",
                      significance="正式任职"),
            ],
            "route06": [
                Event(id="bj-007", date="熙宁四年（1071年）七月上旬",
                      title="离京赴杭州倅",
                      description="苏轼离京赴陈州，南下任杭州通判",
                      significance="离京南下"),
            ],
        },
        route_order={"route01": 9, "route02": 11, "route04": 5, "route05": 1},
        route_arrival={"route01": "嘉祐元年（1056年）五六月间", "route02": "熙宁元年（1068年）十二月", "route04": "熙宁二年（1069年）二月初"},
        route_departure={"route01": "嘉祐二年（1057年）四月", "route02": "熙宁二年（约1069年）", "route04": "熙宁四年（1071年）"},
        route_duration={"route01": 180},
        memorial_sites=memorial_sites,
        transport=Transport(train="开封站 / 开封北站", bus="开封汽车中心站",
                           car="连霍高速 / 大广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_zizhou() -> PlaceDetail:
    """梓州 - route02新增"""
    memorial_sites = [
        MemorialSite(id="zz-s001", name="郪江古镇", type="古镇",
                     location="四川省绵阳市三台县郪江镇",
                     description="郪江是古代郪国都城，历史文化悠久",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="zizhou",
        name_song="梓州",
        name_modern="四川省绵阳市三台县",
        name_pinyin="Zizhou",
        latitude=31.095826,
        longitude=105.093722,
        place_type="游历地",
        tags=["梓州", "蜀道"],
        summary="梓州是蜀道重要节点，苏轼第二次出蜀途经此地",
        background="梓州今四川三台，是蜀中重镇，苏轼第二次出蜀途经此地",
        global_events=[
            Event(id="zz-001", date="熙宁元年（1068年）十二月",
                  title="第二次出蜀过梓州",
                  description="苏轼为父守丧期满后，携家眷第二次出蜀，途经梓州",
                  significance="route02新增地点"),
        ],
        route_order={"route02": 3},
        route_arrival={"route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="三台站", bus="三台客运中心", car="成巴高速"),
        source="李常生《苏轼行踪考》"
    )


def create_yanting() -> PlaceDetail:
    """盐亭 - route02新增"""
    memorial_sites = [
        MemorialSite(id="yt-s001", name="文同墓", type="墓地",
                     location="四川省绵阳市盐亭县",
                     description="文同墓，表兄文同长眠之地",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    works = [
        Work(id="yt-w001", title="墨君堂",
             content="嗜酒好睡，往往过君君不出闻。",
             excerpt="嗜酒好睡，往往过君君不出闻。",
             type="文", date="熙宁元年（1068年）",
             location="盐亭",
             background="拜访文同时作"),
    ]

    return PlaceDetail(
        place_id="yanting",
        name_song="盐亭",
        name_modern="四川省绵阳市盐亭县",
        name_pinyin="Yanting",
        latitude=31.208362,
        longitude=105.389453,
        place_type="游历地",
        tags=["文同", "表兄"],
        summary="苏轼第二次出蜀途经盐亭，拜访表兄文同",
        background="盐亭是苏轼表兄文同的故乡，苏轼第二次出蜀时专程拜访，文同作《墨君堂记》记此事",
        global_events=[
            Event(id="yt-001", date="熙宁元年（1068年）十二月",
                  title="拜访表兄文同",
                  description="苏轼第二次出蜀，途经盐亭拜访表兄文同，文同作《墨君堂记》",
                  significance="route02关键事件，与文同相聚"),
        ],
        global_works=works,
        route_order={"route02": 4},
        route_arrival={"route02": "熙宁元年（1068年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="盐亭站", bus="盐亭客运中心", car="成巴高速"),
        source="李常生《苏轼行踪考》"
    )


def create_huangzhou() -> PlaceDetail:
    """黄州 - 贬谪地"""
    works = [
        Work(id="hz-w001", title="卜算子·缺月挂疏桐",
             content="缺月挂疏桐，漏断人初静。时见幽人独往来，缥缈孤鸿影。惊起却回头，有恨无人省。拣尽寒枝不肯栖，寂寞沙洲冷。",
             excerpt="拣尽寒枝不肯栖，寂寞沙洲冷。",
             type="词", date="1080年2月", location="黄州定慧院",
             background="初到黄州，寓居定慧院，心境孤寂"),
        Work(id="hz-w002", title="念奴娇·赤壁怀古",
             content="大江东去，浪淘尽，千古风流人物。故垒西边，人道是，三国周郎赤壁。乱石穿空，惊涛拍岸，卷起千堆雪。江山如画，一时多少豪杰。",
             excerpt="大江东去，浪淘尽，千古风流人物。",
             type="词", date="1082年7月", location="黄州赤壁",
             background="游赤壁怀古"),
        Work(id="hz-w003", title="前赤壁赋",
             content="壬戌之秋，七月既望，苏子与客泛舟游于赤壁之下。清风徐来，水波不兴。举酒属客，诵明月之诗，歌窈窕之章。",
             excerpt="寄蜉蝣于天地，渺沧海之一粟。",
             type="文", date="1082年7月", location="黄州赤壁",
             background="七月十六夜游赤壁"),
        Work(id="hz-w004", title="定风波·莫听穿林打叶声",
             content="莫听穿林打叶声，何妨吟啸且徐行。竹杖芒鞋轻胜马，谁怕？一蓑烟雨任平生。",
             excerpt="一蓑烟雨任平生。",
             type="词", date="1082年3月", location="黄州沙湖道中",
             background="沙湖道中遇雨"),
    ]

    memorial_sites = [
        MemorialSite(id="hz-s001", name="东坡赤壁", type="公园/遗址",
                     location="湖北省黄冈市黄州区赤壁路",
                     description="文赤壁，苏轼写下千古名篇处。全国重点文物保护单位。",
                     opening_hours="07:00-17:30", ticket="免费",
                     suggested_duration="2-3小时", distance="距市区步行可达",
                     url="https://www.huanggang.gov.cn", rating="AAAA"),
        MemorialSite(id="hz-s002", name="东坡纪念馆", type="博物馆",
                     location="湖北省黄冈市黄州区赤壁山",
                     description="展示苏轼生平与黄州时期创作",
                     opening_hours="08:00-17:00", ticket="免费",
                     suggested_duration="1-2小时"),
    ]

    foods = [
        Food(id="hz-f001", name="东坡肉", description="黄州东坡肉，苏轼发明。慢著火，少著水，火候足时它自美。",
             origin_story="苏轼在黄州时发明", restaurants=["黄州老字号", "东坡酒楼"],
             price_range="¥50-80", tag="黄州必吃"),
    ]

    return PlaceDetail(
        place_id="huangzhou",
        name_song="黄州",
        name_modern="湖北省黄冈市黄州区",
        name_pinyin="Huangzhou",
        latitude=30.4474,
        longitude=114.8780,
        place_type="贬谪地",
        tags=["贬谪地", "东坡居士", "赤壁怀古"],
        summary="苏轼贬谪地，在此躬耕自号东坡居士，创作千古名篇",
        background="黄州是苏轼人生重要转折点，乌台诗案后被贬黄州四年多，在此完成文学创作高峰",
        global_events=[
            Event(id="hz-001", date="1080年2月", title="被贬黄州",
                  description="苏轼因乌台诗案被贬黄州团练副使，本州安置，不得签书公事",
                  significance="人生重要转折点，文学创作高峰期"),
            Event(id="hz-002", date="1080年2月", title="初到黄州",
                  description="初到黄州寓居定慧院，作《卜算子·缺月挂疏桐》",
                  significance="心境写照"),
            Event(id="hz-003", date="1081年2月", title="东坡躬耕",
                  description="故人马孟卿为苏轼请得故营地，苏轼在此躬耕，自号东坡居士",
                  significance="东坡之号由此始"),
            Event(id="hz-004", date="1082年7月", title="赤壁怀古",
                  description="苏轼两次游赤壁，写下《念奴娇·赤壁怀古》和前后《赤壁赋》",
                  significance="千古名篇"),
            Event(id="hz-005", date="1084年4月", title="离开黄州",
                  description="神宗手札，命苏轼移汝州团练副使，苏轼离开黄州",
                  significance="结束黄州贬谪生活"),
        ],
        global_works=works,
        route_order={"route12": 4},
        route_arrival={"route11": "1080年2月"},
        route_departure={"route11": "1084年4月"},
        route_duration={"route11": 1520},
        memorial_sites=memorial_sites,
        foods=foods,
        transport=Transport(train="黄冈站 / 黄冈东站", bus="黄州客运站",
                           car="大广高速 / 沪渝高速"),
        source="李常生《苏轼行踪考》"
    )


def create_guangzhou_henan() -> PlaceDetail:
    """光州 - Route11途经"""
    memorial_sites = [
        MemorialSite(id="gzh-s001", name="光州古城", type="古城",
                     location="河南省潢川县",
                     description="苏轼被贬黄州途经光州",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="guangzhou_henan",
        name_song="光州",
        name_modern="河南省潢川县",
        name_pinyin="Guangzhou",
        latitude=32.1315,
        longitude=115.0516,
        place_type="游历地",
        tags=["光州", "潢川"],
        summary="苏轼被贬黄州途经光州",
        background="光州今河南潢川，苏轼从汴京被贬往黄州时途经此地",
        global_events=[
            Event(id="gzh-001", date="元丰三年（1080年）",
                  title="过光州赴黄州",
                  description="苏轼被贬黄州，途经光州",
                  significance="途经光州"),
        ],
        route_order={"route11": 2},
        route_arrival={"route11": "元丰三年（1080年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="潢川站", bus="潢川汽车站",
                          car="沪陕高速"),
        source="李常生《苏轼行踪考》"
    )


def create_macheng() -> PlaceDetail:
    """麻城 - Route11途经"""
    memorial_sites = [
        MemorialSite(id="mc-s001", name="歧亭", type="亭",
                     location="湖北省麻城市",
                     description="苏轼途经麻城时访陈季常",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="macheng",
        name_song="麻城",
        name_modern="湖北省麻城市",
        name_pinyin="Macheng",
        latitude=31.1173,
        longitude=115.0085,
        place_type="游历地",
        tags=["麻城", "歧亭"],
        summary="苏轼被贬黄州途经麻城，访陈季常",
        background="麻城今湖北麻城，苏轼从汴京被贬往黄州时途经此地，并访好友陈季常",
        global_events=[
            Event(id="mc-001", date="元丰三年（1080年）",
                  title="过麻城赴黄州",
                  description="苏轼被贬黄州，途经麻城访陈季常",
                  significance="途经麻城"),
        ],
        route_order={"route11": 3},
        route_arrival={"route11": "元丰三年（1080年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="麻城站", bus="麻城汽车站",
                          car="沪蓉高速"),
        source="李常生《苏轼行踪考》"
    )


def create_laizhou() -> PlaceDetail:
    """莱州 - Route13途经"""
    memorial_sites = [
        MemorialSite(id="lz-s001", name="云峰山", type="山",
                     location="山东省莱州市",
                     description="苏轼曾至此",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="laizhou",
        name_song="莱州",
        name_modern="山东省莱州市",
        name_pinyin="Laizhou",
        latitude=37.1771,
        longitude=119.9423,
        place_type="途经地",
        tags=["莱州", "掖县"],
        summary="苏轼知登州时途经莱州",
        background="莱州今山东莱州，苏轼元丰八年北上知登州时途经此地",
        global_events=[
            Event(id="lz-001", date="元丰八年（1085年）",
                  title="过莱州赴登州",
                  description="苏轼北上知登州，途经莱州",
                  significance="途经莱州"),
        ],
        route_order={"route14": 4},
        route_arrival={"route13": "元丰八年（1085年）十月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="莱州站", bus="莱州汽车站",
                          car="荣乌高速"),
        source="李常生《苏轼行踪考》"
    )


def create_nandu() -> PlaceDetail:
    """南都 - Route13出发地"""
    memorial_sites = [
        MemorialSite(id="nd-s001", name="应天府书院", type="书院",
                     location="河南省商丘市",
                     description="宋代四大书院之一",
                     opening_hours="08:00-18:00", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="nandu",
        name_song="南都/宋城",
        name_modern="河南省商丘市",
        name_pinyin="Nandu",
        latitude=34.2555,
        longitude=115.6565,
        place_type="途经地",
        tags=["南都", "商丘", "应天府"],
        summary="苏轼起知登州时在南都接诰命",
        background="南都即今河南商丘，宋代为应天府，苏轼元丰八年在此接诰命起知登州",
        global_events=[
            Event(id="nd-001", date="元丰八年（1085年）",
                  title="南都接诰知登州",
                  description="苏轼在南都接诰命，起知登州",
                  significance="起知登州"),
        ],
        route_order={"route13": 1},
        route_arrival={"route13": "元丰八年（1085年）六月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="商丘站/商丘东站", bus="商丘汽车站",
                          car="连霍高速"),
        source="李常生《苏轼行踪考》"
    )


def create_tanzhou() -> PlaceDetail:
    """潭州 - Route03游历地"""
    memorial_sites = [
        MemorialSite(id="tz-s001", name="岳麓书院", type="书院",
                     location="湖南省长沙市岳麓区麓山路",
                     description="中国古代四大书院之一",
                     opening_hours="07:30-18:00", ticket="¥50",
                     suggested_duration="2-3小时", rating="AAAAA"),
    ]

    return PlaceDetail(
        place_id="tanzhou",
        name_song="潭州",
        name_modern="湖南省长沙市",
        name_pinyin="Tanzhou",
        latitude=28.2282,
        longitude=112.9388,
        place_type="游历地",
        tags=["潭州", "长沙"],
        summary="苏轼第三次入京途经潭州",
        background="潭州即今长沙，苏轼第三次入京时途经此地",
        global_events=[
            Event(id="tz-001", date="治平元年（1064年）",
                  title="第三次入京过潭州",
                  description="苏轼第三次入京，途经潭州",
                  significance="route03途经"),
        ],
        route_order={"route03": 1},
        route_arrival={"route03": "治平元年（1064年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="长沙站 / 长沙南站", bus="长沙汽车站",
                           car="京港澳高速"),
        source="李常生《苏轼行踪考》"
    )


def create_huaqing() -> PlaceDetail:
    """华清宫 - Route03游历地"""
    memorial_sites = [
        MemorialSite(id="hq-s001", name="华清宫", type="宫殿",
                     location="陕西省西安市临潼区华清路",
                     description="唐代皇家温泉行宫，唐玄宗与杨贵妃爱情故事发生地",
                     opening_hours="07:00-19:00", ticket="¥120",
                     suggested_duration="3-4小时", rating="AAAAA"),
        MemorialSite(id="hq-s002", name="朝元阁", type="遗址",
                     location="陕西省西安市临潼区骊山",
                     description="华清宫内著名道观遗址",
                     opening_hours="07:00-19:00", ticket="包含在华清宫门票内",
                     suggested_duration="1小时"),
    ]

    return PlaceDetail(
        place_id="huaqing",
        name_song="华清宫",
        name_modern="陕西省西安市临潼区",
        name_pinyin="Huaqing",
        latitude=34.3653,
        longitude=109.2136,
        place_type="游历地",
        tags=["华清宫", "骊山", "温泉"],
        summary="唐玄宗与杨贵妃爱情故事发生地，苏轼第三次入京途经",
        background="华清宫是唐代皇家温泉行宫，位于骊山脚下，苏轼第三次入京途经此地",
        global_events=[
            Event(id="hq-001", date="治平元年（1064年）",
                  title="第三次入京过华清宫",
                  description="苏轼第三次入京，途经华清宫",
                  significance="route03途经"),
        ],
        route_order={"route03": 2},
        route_arrival={"route03": "治平元年（1064年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="西安站 / 西安北站", bus="西安城东客运站",
                           car="京昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_huazhou() -> PlaceDetail:
    """华州 - Route03游历地"""
    memorial_sites = [
        MemorialSite(id="haz-s001", name="华山", type="名山",
                     location="陕西省渭南市华阴市",
                     description="五岳之一，以险著称",
                     opening_hours="08:00-18:00", ticket="¥160",
                     suggested_duration="1-2天", rating="AAAAA"),
    ]

    return PlaceDetail(
        place_id="huazhou",
        name_song="华州",
        name_modern="陕西省渭南市华阴市",
        name_pinyin="Huazhou",
        latitude=34.5659,
        longitude=110.0266,
        place_type="游历地",
        tags=["华州", "华山"],
        summary="苏轼第三次入京途经华州，登华山",
        background="华州即今华阴，苏轼第三次入京途经此地，登游华山",
        global_events=[
            Event(id="haz-001", date="治平元年（1064年）",
                  title="第三次入京过华州",
                  description="苏轼第三次入京，途经华州，登游华山",
                  significance="route03途经"),
        ],
        route_order={"route03": 3},
        route_arrival={"route03": "治平元年（1064年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="华山站 / 华山北站", bus="华阴汽车站",
                           car="连霍高速"),
        source="李常生《苏轼行踪考》"
    )


def create_damingfu() -> PlaceDetail:
    """大名府 - Route03回程地点"""
    memorial_sites = [
        MemorialSite(id="dmf-s001", name="大名府古城", type="古城",
                     location="河北省邯郸市大名县",
                     description="北宋北京，宋代重要陪都",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="damingfu",
        name_song="大名府",
        name_modern="河北省邯郸市大名县",
        name_pinyin="Damingfu",
        latitude=36.2833,
        longitude=115.4167,
        place_type="游历地",
        tags=["大名府", "北京"],
        summary="北宋北京，苏轼父丧回乡途经大名府",
        background="大名府为北宋北京，是重要的交通枢纽，苏轼父丧回乡途经此地",
        global_events=[
            Event(id="dmf-001", date="治平三年（1066年）",
                  title="父丧返乡过大名府",
                  description="苏洵在汴京去世，苏轼兄弟护送灵柩回乡，途经大名府",
                  significance="route03回程"),
        ],
        route_order={"route03": 10},
        route_arrival={"route03": "治平三年（1066年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="大名站 / 邯郸站", bus="大名汽车站",
                           car="大广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_sizhou() -> PlaceDetail:
    """泗州 - Route03回程地点"""
    memorial_sites = [
        MemorialSite(id="sz-s001", name="泗州城遗址", type="遗址",
                     location="江苏省淮安市盱眙县",
                     description="淹没于洪泽湖下的千年古城",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="sizhou",
        name_song="泗州",
        name_modern="江苏省淮安市盱眙县",
        name_pinyin="Sizhou",
        latitude=33.0092,
        longitude=118.6072,
        place_type="游历地",
        tags=["泗州", "古城"],
        summary="苏轼父丧回乡途经泗州",
        background="泗州位于洪泽湖畔，是古代南北交通要道，苏轼父丧回乡途经此地",
        global_events=[
            Event(id="sz-001", date="治平三年（1066年）",
                  title="父丧返乡过泗州",
                  description="苏洵在汴京去世，苏轼兄弟护送灵柩回乡，途经泗州",
                  significance="route03回程"),
        ],
        route_order={"route03": 11},
        route_arrival={"route03": "治平三年（1066年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="盱眙站", bus="盱眙汽车站",
                           car="宁连高速"),
        source="李常生《苏轼行踪考》"
    )


def create_xuyi() -> PlaceDetail:
    """盱眙 - Route03回程地点"""
    memorial_sites = [
        MemorialSite(id="xy-s001", name="第一山", type="名山",
                     location="江苏省淮安市盱眙县",
                     description="苏轼手迹石刻处",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="2小时"),
    ]

    works = [
        Work(id="xy-w001", title="行香子·过七里滩",
             content="一叶舟轻，双桨鸿惊。水天清、影湛波平。鱼翻藻鉴，鹭点烟汀。过沙溪急，霜溪冷，月溪明。重重似画，曲曲如屏。算当年、虚老严陵。君臣一梦，今古空名。但远山长，云山乱，晓山青。",
             excerpt="但远山长，云山乱，晓山青。",
             type="词", date="治平年间",
             location="盱眙",
             background="过盱眙作"),
    ]

    return PlaceDetail(
        place_id="xuyi",
        name_song="盱眙",
        name_modern="江苏省淮安市盱眙县",
        name_pinyin="Xuyi",
        latitude=33.0092,
        longitude=118.6072,
        place_type="游历地",
        tags=["盱眙", "第一山"],
        summary="苏轼父丧回乡途经盱眙，第一山有苏轼手迹",
        background="盱眙位于洪泽湖畔，第一山有苏轼手迹石刻，苏轼父丧回乡途经此地",
        global_events=[
            Event(id="xy-001", date="治平三年（1066年）",
                  title="父丧返乡过盱眙",
                  description="苏洵在汴京去世，苏轼兄弟护送灵柩回乡，途经盱眙",
                  significance="route03回程"),
        ],
        global_works=works,
        route_order={"route03": 12},
        route_arrival={"route03": "治平三年（1066年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="盱眙站", bus="盱眙汽车站",
                           car="宁连高速"),
        source="李常生《苏轼行踪考》"
    )


def create_jiangling() -> PlaceDetail:
    """江陵 - Route03回程地点"""
    memorial_sites = [
        MemorialSite(id="jl-s001", name="荆州古城", type="古城",
                     location="湖北省荆州市荆州区",
                     description="古代兵家必争之地",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="2-3小时", rating="AAAAA"),
    ]

    return PlaceDetail(
        place_id="jiangling",
        name_song="江陵府",
        name_modern="湖北省荆州市",
        name_pinyin="Jiangling",
        latitude=30.3260,
        longitude=112.2394,
        place_type="游历地",
        tags=["江陵", "荆州"],
        summary="苏轼父丧回乡途经江陵",
        background="江陵即今荆州，是古代南北交通要道，苏轼父丧回乡途经此地",
        global_events=[
            Event(id="jl-001", date="治平三年（1066年）",
                  title="父丧返乡过江陵",
                  description="苏洵在汴京去世，苏轼兄弟护送灵柩回乡，途经江陵",
                  significance="route03回程"),
        ],
        route_order={"route03": 13},
        route_arrival={"route03": "治平三年（1066年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="荆州站", bus="荆州汽车站",
                           car="沪渝高速"),
        source="李常生《苏轼行踪考》"
    )


def create_fengdu() -> PlaceDetail:
    """丰都 - Route03回程地点"""
    memorial_sites = [
        MemorialSite(id="fd-s001", name="丰都鬼城", type="景区",
                     location="重庆市丰都县名山镇",
                     description="中国鬼文化发源地",
                     opening_hours="08:30-17:30", ticket="¥80",
                     suggested_duration="2-3小时", rating="AAAA"),
    ]

    return PlaceDetail(
        place_id="fengdu",
        name_song="丰都",
        name_modern="重庆市丰都县",
        name_pinyin="Fengdu",
        latitude=29.9738,
        longitude=107.9497,
        place_type="游历地",
        tags=["丰都", "鬼城"],
        summary="苏轼父丧回乡途经丰都",
        background="丰都是古代著名古城，苏轼父丧回乡途经此地",
        global_events=[
            Event(id="fd-001", date="治平三年（1066年）",
                  title="父丧返乡过丰都",
                  description="苏洵在汴京去世，苏轼兄弟护送灵柩回乡，途经丰都",
                  significance="route03回程"),
        ],
        route_order={"route03": 14},
        route_arrival={"route03": "治平三年（1066年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="丰都站", bus="丰都汽车站",
                           car="沪渝高速"),
        source="李常生《苏轼行踪考》"
    )


def create_wenan() -> PlaceDetail:
    """文安县 - Route03新增"""
    memorial_sites = [
        MemorialSite(id="wa-s001", name="文安古城", type="古城",
                     location="河北省廊坊市文安县",
                     description="苏洵曾任文安县主簿，编纂《太常因革礼》",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="wenan",
        name_song="文安县",
        name_modern="河北省廊坊市文安县",
        name_pinyin="Wenan",
        latitude=38.8750,
        longitude=116.4783,
        place_type="游历地",
        tags=["文安", "苏洵"],
        summary="苏洵曾任文安县主簿，苏轼随父经过此地",
        background="文安县属霸州管辖，苏洵曾任文安县主簿编纂《太常因革礼》，苏轼随父经过此地",
        global_events=[
            Event(id="wa-001", date="治平二年（1065年）",
                  title="随父经过文安",
                  description="苏轼随父苏洵经过文安县，时苏洵任文安县主簿编纂礼书",
                  significance="route03途经"),
        ],
        route_order={"route03": 1},
        route_arrival={"route03": "治平二年（1065年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="文安站", bus="文安汽车站",
                           car="京台高速"),
        source="李常生《苏轼行踪考》"
    )


def create_xiaoyan() -> PlaceDetail:
    """下岩/云安 - Route03回程新增"""
    memorial_sites = [
        MemorialSite(id="xr-s001", name="下岩寺", type="寺庙",
                     location="重庆市云阳县",
                     description="苏轼兄弟曾泊舟于此",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="xiaoyan",
        name_song="下岩/云安",
        name_modern="重庆市云阳县",
        name_pinyin="Xiaoyan",
        latitude=30.9317,
        longitude=108.6972,
        place_type="游历地",
        tags=["下岩", "云安"],
        summary="苏轼父丧返乡途经下岩寺",
        background="苏轼父丧返乡时泊舟下岩寺，作《题云安下岩》",
        global_events=[
            Event(id="xr-001", date="治平四年（1067年）正月二十日",
                  title="父丧返乡过云安下岩",
                  description="苏轼兄弟护丧还蜀，泊舟下岩寺",
                  significance="route03回程重要地点"),
        ],
        route_order={"route03": 15},
        route_arrival={"route03": "治平四年（1067年）正月二十日"},
        memorial_sites=memorial_sites,
        transport=Transport(train="云阳站", bus="云阳汽车站",
                           car="沪蓉高速"),
        source="李常生《苏轼行踪考》"
    )


def create_xiandushan() -> PlaceDetail:
    """仙都山 - Route03回程新增"""
    memorial_sites = [
        MemorialSite(id="xds-s001", name="仙都山", type="名山",
                     location="重庆市丰都县",
                     description="苏辙曾泊舟于此",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="xiandushan",
        name_song="仙都山",
        name_modern="重庆市丰都县",
        name_pinyin="Xiandushan",
        latitude=29.8500,
        longitude=107.8500,
        place_type="游历地",
        tags=["仙都山"],
        summary="苏轼父丧返乡途经仙都山",
        background="苏辙泊舟仙都山下，有道士以《长生金丹诀》相示",
        global_events=[
            Event(id="xds-001", date="治平四年（1067年）二月",
                  title="父丧返乡过仙都山",
                  description="苏辙泊舟仙都山下，有道士以《阴真君长生金丹诀》相示",
                  significance="route03回程"),
        ],
        route_order={"route03": 16},
        route_arrival={"route03": "治平四年（1067年）二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="丰都站", bus="丰都汽车站",
                           car="沪渝高速"),
        source="李常生《苏轼行踪考》"
    )


def create_fankou() -> PlaceDetail:
    """樊口 - Route03回程新增"""
    memorial_sites = [
        MemorialSite(id="fak-s001", name="樊口", type="渡口",
                     location="湖北省鄂州市樊口街道",
                     description="长江南岸渡口，苏轼多次经过",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="1-2小时"),
    ]

    works = [
        Work(id="fak-w001", title="次韵前篇",
             content="忆昔还乡溯巴峡，落帆樊口高桅亚。长江衮衮空自流，白发纷纷宁少借。",
             excerpt="落帆樊口高桅亚。",
             type="诗", date="元丰三年（1080年）",
             location="黄州樊口",
             background="回忆父丧返乡过樊口"),
    ]

    return PlaceDetail(
        place_id="fankou",
        name_song="樊口",
        name_modern="湖北省鄂州市樊口街道",
        name_pinyin="Fankou",
        latitude=30.4000,
        longitude=114.9000,
        place_type="游历地",
        tags=["樊口", "黄州"],
        summary="苏轼父丧返乡途经樊口，长江南岸渡口",
        background="樊口在黄州长江南岸，苏轼多次经过此地",
        global_events=[
            Event(id="fak-001", date="治平三年（1066年）秋冬",
                  title="父丧返乡过樊口",
                  description="苏轼兄弟护丧还蜀，过樊口",
                  significance="route03回程"),
        ],
        global_works=works,
        route_order={"route03": 10},
        route_arrival={"route03": "治平三年（1066年）秋冬"},
        memorial_sites=memorial_sites,
        transport=Transport(train="鄂州站", bus="鄂州汽车站",
                           car="沪渝高速"),
        source="李常生《苏轼行踪考》"
    )


def create_guishan() -> PlaceDetail:
    """龟山 - Route03回程新增"""
    memorial_sites = [
        MemorialSite(id="gsh-s001", name="龟山", type="山",
                     location="江苏省淮安市盱眙县",
                     description="苏轼多次经过此山",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="2-3小时"),
    ]

    works = [
        Work(id="gsh-w001", title="龟山",
             content="生飘荡去何求，再过龟山岁五周。身行万里半天下，僧卧一庵初白头。地隔中原劳北望，潮连沧海欲东游。元嘉旧事无人记，故垒摧颓今在不。",
             excerpt="身行万里半天下，僧卧一庵初白头。",
             type="诗", date="熙宁四年（1071年）十月",
             location="龟山",
             background="再过龟山怀古"),
    ]

    return PlaceDetail(
        place_id="guishan",
        name_song="龟山",
        name_modern="江苏省淮安市盱眙县",
        name_pinyin="Guishan",
        latitude=33.2000,
        longitude=118.5000,
        place_type="游历地",
        tags=["龟山", "盱眙"],
        summary="苏轼父丧返乡途经龟山",
        background="龟山在盱眙县北三十里，苏轼多次经过此地",
        global_events=[
            Event(id="gsh-001", date="治平三年（1066年）七月",
                  title="父丧返乡过龟山",
                  description="苏轼兄弟护丧还蜀，过龟山",
                  significance="route03回程"),
        ],
        global_works=works,
        route_order={"route03": 9},
        route_arrival={"route03": "治平三年（1066年）七月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="盱眙站", bus="盱眙汽车站",
                           car="宁连高速"),
        source="李常生《苏轼行踪考》"
    )


def create_zhaohua() -> PlaceDetail:
    """昭化(益昌) - Route04新增"""
    memorial_sites = [
        MemorialSite(id="zh-s001", name="昭化古城", type="古城",
                     location="四川省广元市昭化区",
                     description="古益昌县，苏轼出蜀途经此地",
                     opening_hours="全天", ticket="免费",
                     suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="zhaohua",
        name_song="昭化/益昌",
        name_modern="四川省广元市昭化区",
        name_pinyin="Zhaohua",
        latitude=32.3400,
        longitude=105.6500,
        place_type="游历地",
        tags=["昭化", "益昌", "蜀道"],
        summary="北宋开宝五年改益昌县为昭化县，苏轼出蜀必经之地",
        background="昭化古称益昌，北宋开宝五年(972年)改益昌县为昭化县，属利州管辖，是苏轼出蜀的必经之地",
        global_events=[
            Event(id="zh-001", date="熙宁元年（1068年）十一二月",
                  title="第四次出蜀过昭化",
                  description="苏轼第四次出蜀，途经昭化(益昌)",
                  significance="route04途经"),
        ],
        route_order={"route04": 1},
        route_arrival={"route04": "熙宁元年（1068年）十一二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="广元站", bus="昭化汽车站",
                           car="京昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_hangzhou() -> PlaceDetail:
    """杭州 - 任职地/游历地"""
    memorial_sites = [
        MemorialSite(id="hz-s001", name="西湖苏堤", type="堤坝",
                     location="浙江省杭州市西湖区",
                     description="苏轼任杭州通判时疏浚西湖，堆筑苏堤",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
        MemorialSite(id="hz-s002", name="六一泉", type="泉水",
                     location="浙江省杭州市西湖区孤山",
                     description="苏轼命名纪念欧阳修",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
        MemorialSite(id="hz-s003", name="灵隐寺", type="寺庙",
                     location="浙江省杭州市西湖区灵隐路",
                     description="杭州最著名的寺庙之一，苏轼常游此地",
                     opening_hours="07:00-18:00", ticket="¥45", suggested_duration="2-3小时"),
    ]

    works = [
        Work(id="hz-w001", title="饮湖上初晴后雨",
             content="水光潋滟晴方好，山色空蒙雨亦奇。欲把西湖比西子，淡妆浓抹总相宜。",
             excerpt="水光潋滟晴方好，山色空蒙雨亦奇。",
             type="诗", date="熙宁四年（1071年）",
             location="杭州西湖",
             background="描写西湖美景的千古绝唱"),
    ]

    return PlaceDetail(
        place_id="hangzhou",
        name_song="杭州/临安",
        name_modern="浙江省杭州市",
        name_pinyin="Hangzhou",
        latitude=30.2741,
        longitude=120.1551,
        place_type="任职地/游历地",
        tags=["杭州", "西湖", "通判", "苏堤"],
        summary="苏轼任杭州通判期间疏浚西湖、堆筑苏堤，留下千古名篇",
        background="杭州是北宋重要商业城市，西湖风景秀丽，苏轼任杭州通判两年期间创作大量诗文",
        global_events=[
            Event(id="hz-001", date="熙宁四年（1071年）十一月二十八日",
                  title="任杭州通判",
                  description="苏轼到杭州任通判，寓居凤凰山",
                  significance="杭州仕途"),
        ],
        global_works=works,
        route_events={
            "route05": [
                Event(id="hz-002", date="熙宁四年（1071年）十一月二十八日",
                      title="抵达杭州任通判",
                      description="苏轼到杭州任通判",
                      significance="任杭州倅"),
                Event(id="hz-003", date="熙宁五年（1072年）",
                      title="疏浚西湖",
                      description="苏轼疏浚西湖，堆筑苏堤",
                      significance="治理西湖"),
            ],
            "route07": [
                Event(id="hz-004", date="熙宁七年（1074年）九月下旬",
                      title="离杭州赴密州",
                      description="苏轼离开杭州，赴密州任知州",
                      significance="离杭赴密"),
            ],
        },
        route_order={"route05": 10, "route06": 1},
        route_arrival={"route05": "熙宁四年（1071年）十一月二十八日", "route06": "熙宁七年（1074年）九月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="杭州站/杭州东站", bus="杭州汽车站",
                          car="沪杭高速/杭宁高速"),
        source="李常生《苏轼行踪考》"
    )


def create_chengzhou() -> PlaceDetail:
    """陈州/淮阳 - Route05途经"""
    memorial_sites = [
        MemorialSite(id="cz-s001", name="柳湖", type="湖泊",
                     location="河南省淮阳区西北隅",
                     description="苏轼在陈州时常游柳湖",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
        MemorialSite(id="cz-s002", name="铁墓", type="墓葬",
                     location="河南省淮阳区",
                     description="陈胡公墓，苏轼《记铁墓厄台》记载",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    return PlaceDetail(
        place_id="chengzhou",
        name_song="陈州/宛丘",
        name_modern="河南省周口市淮阳区",
        name_pinyin="Chengzhou",
        latitude=33.7400,
        longitude=114.8920,
        place_type="游历地",
        tags=["陈州", "淮阳", "张方平"],
        summary="苏轼赴杭州途经陈州，拜访张方平、会见苏辙",
        background="陈州今河南淮阳，苏轼南下任杭州通判时途经此地，拜访致仕的张方平，并与在此任教授的苏辙相见",
        global_events=[
            Event(id="cz-001", date="熙宁四年（1071年）七月",
                  title="过陈州见张方平",
                  description="苏轼过陈州，拜访张方平",
                  significance="途经陈州"),
        ],
        route_events={
            "route05": [
                Event(id="cz-002", date="熙宁四年（1071年）七月",
                      title="过陈州拜访张方平",
                      description="苏轼离京南下，先至陈州拜访致仕的张方平",
                      significance="途经陈州"),
                Event(id="cz-003", date="熙宁四年（1071年）七月",
                      title="陈州会见苏辙",
                      description="苏轼在陈州与任教授的苏辙会面",
                      significance="兄弟相见"),
            ],
        },
        route_order={"route05": 2},
        route_arrival={"route05": "熙宁四年（1071年）七月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="淮阳站", bus="淮阳汽车站",
                          car="商周高速"),
        source="李常生《苏轼行踪考》"
    )


def create_yingzhou() -> PlaceDetail:
    """颍州 - Route05途经"""
    memorial_sites = [
        MemorialSite(id="yz-s001", name="西湖", type="湖泊",
                     location="安徽省阜阳市颍州区",
                     description="欧阳修退隐颍州，常游西湖",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="yingzhou",
        name_song="颍州",
        name_modern="安徽省阜阳市",
        name_pinyin="Yingzhou",
        latitude=32.8900,
        longitude=115.8200,
        place_type="游历地",
        tags=["颍州", "欧阳修"],
        summary="苏轼南下途经颍州，拜访退隐的欧阳修",
        background="颍州今安徽阜阳，欧阳修晚年退隐于此，苏轼南下任杭州通判时绕道拜访",
        global_events=[
            Event(id="yz-001", date="熙宁四年（1071年）",
                  title="过颍州拜望欧阳修",
                  description="苏轼顺颍河南下，至颍州拜望退隐的欧阳修",
                  significance="途经颍州"),
        ],
        route_events={
            "route05": [
                Event(id="yz-002", date="熙宁四年（1071年）",
                      title="颍州拜望欧阳修",
                      description="苏轼至颍州拜望退隐的欧阳修，相与相处月余",
                      significance="拜访恩师"),
            ],
        },
        route_order={"route05": 3},
        route_arrival={"route05": "熙宁四年（1071年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="阜阳站", bus="阜阳汽车站",
                          car="济广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_shouzhou() -> PlaceDetail:
    """寿州 - Route05途经"""
    memorial_sites = [
        MemorialSite(id="sz-s001", name="八公山", type="山",
                     location="安徽省淮南市寿县",
                     description="著名的道教圣地，豆腐发源地",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="shouzhou",
        name_song="寿州",
        name_modern="安徽省淮南市寿县",
        name_pinyin="Shouzhou",
        latitude=32.5734,
        longitude=116.9977,
        place_type="游历地",
        tags=["寿州", "八公山"],
        summary="苏轼南下途经寿州",
        background="寿州今安徽寿县，苏轼南下杭州途经此地",
        global_events=[
            Event(id="sz-001", date="熙宁四年（1071年）",
                  title="过寿州",
                  description="苏轼南下途经寿州",
                  significance="途经寿州"),
        ],
        route_order={"route05": 4},
        route_arrival={"route05": "熙宁四年（1071年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="寿县站", bus="寿县汽车站",
                            car="济广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_yangzhou() -> PlaceDetail:
    """扬州 - Route05途经"""
    memorial_sites = [
        MemorialSite(id="yy-s001", name="平山堂", type="建筑",
                     location="江苏省扬州市邗江区",
                     description="欧阳修所建，苏轼常来此凭吊",
                     opening_hours="08:00-17:00", ticket="¥45", suggested_duration="1-2小时"),
        MemorialSite(id="yy-s002", name="瘦西湖", type="湖泊",
                     location="江苏省扬州市",
                     description="扬州著名的湖泊风景区",
                     opening_hours="06:00-18:00", ticket="¥60", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="yangzhou",
        name_song="扬州/广陵",
        name_modern="江苏省扬州市",
        name_pinyin="Yangzhou",
        latitude=32.3912,
        longitude=119.4213,
        place_type="游历地",
        tags=["扬州", "广陵", "平山堂"],
        summary="苏轼南下途经扬州，凭吊欧阳修所建平山堂",
        background="扬州是北宋重要商业城市，苏轼南下杭州途经此地，曾凭吊欧阳修所建平山堂",
        global_events=[
            Event(id="yy-001", date="熙宁四年（1071年）",
                  title="过扬州",
                  description="苏轼南下途经扬州",
                  significance="途经扬州"),
        ],
        route_events={
            "route05": [
                Event(id="yy-002", date="熙宁四年（1071年）",
                      title="扬州凭吊平山堂",
                      description="苏轼至扬州，凭吊欧阳修所建平山堂",
                      significance="途经扬州"),
            ],
        },
        route_order={"route05": 6},
        route_arrival={"route05": "熙宁四年（1071年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="扬州站/扬州东站", bus="扬州汽车站",
                            car="京沪高速/沪陕高速"),
        source="李常生《苏轼行踪考》"
    )


def create_runzhou() -> PlaceDetail:
    """润州/镇江 - Route05途经"""
    memorial_sites = [
        MemorialSite(id="rz-s001", name="金山寺", type="寺庙",
                     location="江苏省镇江市润州区",
                     description="苏轼《金山梦中作》所在地",
                     opening_hours="07:30-17:30", ticket="¥50", suggested_duration="2小时"),
        MemorialSite(id="rz-s002", name="北固山", type="山",
                     location="江苏省镇江市京口区",
                     description="刘备、孙权试剑地，甘露寺所在",
                     opening_hours="07:30-17:30", ticket="¥40", suggested_duration="2小时"),
    ]

    return PlaceDetail(
        place_id="runzhou",
        name_song="润州/镇江",
        name_modern="江苏省镇江市",
        name_pinyin="Runzhou",
        latitude=32.1889,
        longitude=119.4550,
        place_type="游历地",
        tags=["润州", "镇江", "金山寺"],
        summary="苏轼南下途经润州，游金山寺、北固山",
        background="润州今江苏镇江，是长江南岸重要渡口，苏轼南下杭州途经此地",
        global_events=[
            Event(id="rz-001", date="熙宁四年（1071年）",
                  title="过润州",
                  description="苏轼南下途经润州",
                  significance="途经润州"),
        ],
        route_events={
            "route05": [
                Event(id="rz-002", date="熙宁四年（1071年）",
                      title="润州游金山寺",
                      description="苏轼至润州，游金山寺",
                      significance="途经润州"),
            ],
            "route06": [
                Event(id="rz-003", date="熙宁七年（1074年）",
                      title="润州北行过境",
                      description="苏轼北行赴密州，途经润州",
                      significance="途经润州"),
            ],
        },
        route_order={"route05": 7, "route06": 2},
        route_arrival={"route05": "熙宁四年（1071年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="镇江站/镇江南站", bus="镇江汽车站",
                            car="京沪高速"),
        source="李常生《苏轼行踪考》"
    )


def create_suzhou() -> PlaceDetail:
    """苏州 - Route05途经"""
    memorial_sites = [
        MemorialSite(id="sz-s001", name="虎丘", type="风景",
                     location="江苏省苏州市姑苏区",
                     description="苏州著名风景名胜，有云岩寺塔",
                     opening_hours="07:30-17:30", ticket="¥60", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="suzhou",
        name_song="苏州/平江府",
        name_modern="江苏省苏州市",
        name_pinyin="Suzhou",
        latitude=31.2989,
        longitude=120.5853,
        place_type="游历地",
        tags=["苏州", "虎丘", "园林"],
        summary="苏轼南下途经苏州，游虎丘",
        background="苏州是北宋重要商业城市，风景秀丽，苏轼南下杭州途经此地",
        global_events=[
            Event(id="sz-001", date="熙宁四年（1071年）",
                  title="过苏州",
                  description="苏轼南下途经苏州",
                  significance="途经苏州"),
        ],
        route_events={
            "route05": [
                Event(id="sz-002", date="熙宁四年（1071年）",
                      title="苏州游虎丘",
                      description="苏轼至苏州，游虎丘",
                      significance="途经苏州"),
            ],
        },
        route_order={"route05": 8},
        route_arrival={"route05": "熙宁四年（1071年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="苏州站/苏州北站", bus="苏州汽车站",
                            car="京沪高速/沪常高速"),
        source="李常生《苏轼行踪考》"
    )


def create_gaoyou() -> PlaceDetail:
    """高邮 - Route06途经"""
    memorial_sites = [
        MemorialSite(id="gy-s001", name="文游台", type="古迹",
                     location="江苏省高邮市",
                     description="苏轼过高邮时曾游此地",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="gaoyou",
        name_song="高邮",
        name_modern="江苏省高邮市",
        name_pinyin="Gaoyou",
        latitude=32.7800,
        longitude=119.4600,
        place_type="游历地",
        tags=["高邮", "文游台"],
        summary="苏轼北行途经高邮",
        background="高邮今江苏高邮，苏轼北行赴密州途经此地",
        global_events=[
            Event(id="gy-001", date="熙宁七年（1074年）",
                  title="过高邮",
                  description="苏轼北行途经高邮",
                  significance="途经高邮"),
        ],
        route_order={"route06": 3},
        route_arrival={"route06": "熙宁七年（1074年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="高邮站", bus="高邮汽车站",
                          car="京沪高速"),
        source="李常生《苏轼行踪考》"
    )


def create_haizhou() -> PlaceDetail:
    """海州 - Route06途经"""
    memorial_sites = [
        MemorialSite(id="hz-s001", name="孔望山", type="山",
                     location="江苏省连云港市海州区",
                     description="苏轼北行途经海州，曾游孔望山",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="haizhou",
        name_song="海州",
        name_modern="江苏省连云港市",
        name_pinyin="Haizhou",
        latitude=34.5967,
        longitude=119.2217,
        place_type="游历地",
        tags=["海州", "孔望山"],
        summary="苏轼北行途经海州，游孔望山",
        background="海州今江苏连云港，苏轼北行赴密州途经此地",
        global_events=[
            Event(id="ha-001", date="熙宁七年（1074年）",
                  title="过海州",
                  description="苏轼北行途经海州",
                  significance="途经海州"),
        ],
        route_events={
            "route06": [
                Event(id="ha-002", date="熙宁七年（1074年）",
                      title="过海州赴密州",
                      description="苏轼北行途经海州，赴密州任知州",
                      significance="途经海州"),
            ],
            "route13": [
                Event(id="ha-003", date="元丰八年（1085年）",
                      title="过海州赴登州",
                      description="苏轼北上知登州，途经海州",
                      significance="途经海州"),
            ],
        },
        route_order={"route06": 4, "route13": 2},
        route_arrival={"route06": "熙宁七年（1074年）", "route13": "元丰八年（1085年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="连云港站", bus="连云港汽车站",
                          car="沈海高速"),
        source="李常生《苏轼行踪考》"
    )


def create_mizhou() -> PlaceDetail:
    """密州/诸城 - 任职地"""
    memorial_sites = [
        MemorialSite(id="mz-s001", name="超然台", type="建筑",
                     location="山东省诸城市",
                     description="苏轼在密州时命名超然台，作《超然台记》",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
        MemorialSite(id="mz-s002", name="常山", type="山",
                     location="山东省诸城市",
                     description="苏轼在密州时常祭常山",
                     opening_hours="全天", ticket="免费", suggested_duration="2小时"),
        MemorialSite(id="mz-s003", name="黄茅岗", type="岗",
                     location="山东省诸城市",
                     description="苏轼《江城子·密州出猎》提及",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    works = [
        Work(id="mz-w001", title="水调歌头·明月几时有",
             content="明月几时有，把酒问青天。不知天上宫阙，今夕是何年？",
             excerpt="明月几时有，把酒问青天。",
             type="词", date="熙宁九年（1076年）中秋",
             location="密州超然台",
             background="苏轼在密州中秋欢饮达旦，大醉作此篇，兼怀子由"),
        Work(id="mz-w002", title="江城子·密州出猎",
             content="老夫聊发少年狂，左牵黄，右擎苍，锦帽貂裘，千骑卷平冈。",
             excerpt="老夫聊发少年狂，左牵黄，右擎苍。",
             type="词", date="熙宁七年（1074年）",
             location="密州",
             background="苏轼在密州出猎所作"),
    ]

    return PlaceDetail(
        place_id="mizhou",
        name_song="密州",
        name_modern="山东省诸城市",
        name_pinyin="Mizhou",
        latitude=35.9958,
        longitude=119.4108,
        place_type="任职地",
        tags=["密州", "诸城", "知州", "超然台"],
        summary="苏轼任密州知州两年，期间创作《水调歌头》《江城子》等名篇",
        background="密州今山东诸城，苏轼于熙宁七年任知州，在此两年期间创作大量诗文",
        global_events=[
            Event(id="mz-001", date="熙宁七年（1074年）十一月三日",
                  title="任密州知州",
                  description="苏轼到密州任知州",
                  significance="密州仕途"),
        ],
        global_works=works,
        route_events={
            "route06": [
                Event(id="mz-002", date="熙宁七年（1074年）十一月三日",
                      title="到密州任知州",
                      description="苏轼抵达密州任知州",
                      significance="任密州知州"),
                Event(id="mz-003", date="熙宁七年（1074年）",
                      title="密州出猎",
                      description="苏轼在密州出猎，作《江城子·密州出猎》",
                      significance="密州出猎"),
                Event(id="mz-004", date="熙宁九年（1076年）中秋",
                      title="超然台欢饮",
                      description="苏轼在密州超然台欢饮达旦，作《水调歌头》",
                      significance="中秋词"),
                Event(id="mz-005", date="熙宁九年（1076年）十二月",
                      title="罢密州赴徐州",
                      description="苏轼罢密州，赴徐州任知州",
                      significance="离密赴徐"),
            ],
            "route13": [
                Event(id="mz-013", date="元丰八年（1085年）",
                      title="过密州赴登州",
                      description="苏轼北上知登州，途经密州",
                      significance="途经密州"),
            ],
        },
        route_order={"route06": 5, "route08": 1, "route13": 3},
        route_arrival={"route06": "熙宁七年（1074年）十一月三日"},
        route_departure={"route06": "熙宁九年（1076年）十二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="诸城站", bus="诸城汽车站",
                          car="青兰高速"),
        source="李常生《苏轼行踪考》"
    )


def create_yuncheng() -> PlaceDetail:
    """郓州 - Route07途经"""
    memorial_sites = [
        MemorialSite(id="yc-s001", name="郓州古城", type="古城",
                     location="山东省郓城县",
                     description="苏轼北上途经郓州",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="yuncheng",
        name_song="郓州",
        name_modern="山东省郓城县",
        name_pinyin="Yuncheng",
        latitude=35.5975,
        longitude=115.9311,
        place_type="游历地",
        tags=["郓州", "东平"],
        summary="苏轼北上途经郓州，改知徐州",
        background="郓州今山东郓城，苏轼自密州北上前住徐州途经此地",
        global_events=[
            Event(id="yc-001", date="熙宁十年（1077年）二月",
                  title="过郓州改知徐州",
                  description="苏轼行至郓州，改知徐州",
                  significance="途经郓州"),
        ],
        route_order={"route07": 2},
        route_arrival={"route07": "熙宁十年（1077年）二月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="郓城站", bus="郓城汽车站",
                          car="济广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_xuzhou() -> PlaceDetail:
    """徐州 - 任职地"""
    memorial_sites = [
        MemorialSite(id="xz-s001", name="黄楼", type="建筑",
                     location="江苏省徐州市云龙区",
                     description="苏轼在徐州抗洪后建黄楼纪念",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
        MemorialSite(id="xz-s002", name="云龙山放鹤亭", type="亭",
                     location="江苏省徐州市云龙区",
                     description="苏轼常在此与客会饮",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
        MemorialSite(id="xz-s003", name="燕子楼", type="楼",
                     location="江苏省徐州市云龙区",
                     description="苏轼梦入燕子楼，作《永遇乐》",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    works = [
        Work(id="xz-w001", title="永遇乐·彭城夜宿燕子楼",
             content="明月如霜，好风如水，清景无限。曲港跳鱼，圆荷泻露，寂寞无人见。",
             excerpt="明月如霜，好风如水，清景无限。",
             type="词", date="元丰元年（1078年）",
             location="徐州燕子楼",
             background="苏轼梦入燕子楼，作此词"),
        Work(id="xz-w002", title="放鹤亭记",
             content="《放鹤亭记》是苏轼在徐州时所作，记述云龙山人张天骥之事",
             excerpt="《放鹤亭记》",
             type="文", date="元丰元年（1078年）",
             location="徐州云龙山",
             background="苏轼在云龙山为张天骥作《放鹤亭记》"),
    ]

    return PlaceDetail(
        place_id="xuzhou",
        name_song="徐州/彭城",
        name_modern="江苏省徐州市",
        name_pinyin="Xuzhou",
        latitude=34.2044,
        longitude=117.2857,
        place_type="任职地",
        tags=["徐州", "彭城", "知州", "黄楼"],
        summary="苏轼任徐州知州一年十个月，抗洪建黄楼，留下众多名篇",
        background="徐州今江苏徐州，苏轼于熙宁十年任知州，期间率民抗洪，建黄楼，创作众多诗文",
        global_events=[
            Event(id="xz-001", date="熙宁十年（1077年）四月二十一日",
                  title="任徐州知州",
                  description="苏轼到徐州任知州",
                  significance="徐州仕途"),
        ],
        global_works=works,
        route_events={
            "route08": [
                Event(id="xz-002", date="熙宁十年（1077年）四月二十一日",
                      title="到徐州任知州",
                      description="苏轼抵达徐州任知州",
                      significance="任徐州知州"),
                Event(id="xz-003", date="熙宁十年（1077年）九月",
                      title="徐州抗洪",
                      description="黄河决口于曹村，水穿徐州城下，苏轼率吏民筑堤抗洪",
                      significance="率民抗洪"),
                Event(id="xz-004", date="元丰元年（1078年）",
                      title="建黄楼",
                      description="苏轼在徐州东门之上建黄楼，子由撰《黄楼赋》",
                      significance="建黄楼"),
                Event(id="xz-005", date="元丰元年（1078年）秋",
                      title="梦入燕子楼",
                      description="苏轼梦登燕子楼，作《永遇乐》",
                      significance="燕子楼梦"),
            ],
            "route09": [
                Event(id="xz-006", date="元丰二年（1079年）二三月",
                      title="罢徐州知湖州",
                      description="苏轼罢徐州，南下知湖州",
                      significance="离徐赴湖"),
            ],
        },
        route_order={"route07": 3, "route08": 1},
        route_arrival={"route07": "熙宁十年（1077年）四月二十一日"},
        route_departure={"route07": "元丰二年（1079年）二三月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="徐州站/徐州东站", bus="徐州汽车站",
                          car="京沪高速/连霍高速"),
        source="李常生《苏轼行踪考》"
    )


def create_huzhou() -> PlaceDetail:
    """湖州 - 任职地"""
    works = [
        Work(id="hz2-w001", title="题西林壁",
             content="横看成岭侧成峰，远近高低各不同。不识庐山真面目，只缘身在此山中。",
             excerpt="不识庐山真面目，只缘身在此山中。",
             type="诗", date="元丰七年（1084年）",
             location="庐山",
             background="题于西林寺墙壁"),
    ]

    memorial_sites = [
        MemorialSite(id="hz2-s001", name="湖州苏湾", type="遗址",
                     location="浙江省湖州市",
                     description="苏轼在湖州时常至苏湾",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="huzhou",
        name_song="湖州",
        name_modern="浙江省湖州市",
        name_pinyin="Huzhou",
        latitude=30.8673,
        longitude=120.0930,
        place_type="任职地",
        tags=["湖州", "知州"],
        summary="苏轼知湖州三月，因乌台诗案被捕",
        background="湖州是苏轼元丰二年任知州地，仅三月即因乌台诗案被捕",
        global_events=[
            Event(id="hz2-001", date="元丰二年（1079年）三月",
                  title="任湖州知州",
                  description="苏轼任湖州知州",
                  significance="湖州仕途"),
        ],
        route_events={
            "route08": [
                Event(id="hz2-002", date="元丰二年（1079年）三月",
                      title="到湖州任知州",
                      description="苏轼从徐州南下知湖州",
                      significance="任湖州知州"),
                Event(id="hz2-006", date="元丰二年（1079年）七月",
                      title="乌台诗案被捕",
                      description="苏轼因诗获罪，被押解至汴京",
                      significance="乌台诗案"),
            ],
            "route16": [
                Event(id="hz2-005", date="元祐六年（1091年）",
                      title="移知颍州途经湖州",
                      description="苏轼离杭移知颍州，途经湖州",
                      significance="途经湖州"),
            ],
        },
        route_order={"route08": 3, "route15": 2},
        route_arrival={"route08": "元丰二年（1079年）三月", "route15": "元祐六年（1091年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="湖州站", bus="湖州汽车站", car="申嘉湖高速"),
        source="李常生《苏轼行踪考》"
    )


def create_huaian() -> PlaceDetail:
    """淮安 - 游历地"""
    memorial_sites = [
        MemorialSite(id="ha-s001", name="镇淮楼", type="建筑",
                     location="江苏省淮安市",
                     description="淮安古城楼",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    return PlaceDetail(
        place_id="huaian",
        name_song="楚州/淮安",
        name_modern="江苏省淮安市",
        name_pinyin="Huaian",
        latitude=33.5517,
        longitude=119.0153,
        place_type="游历地",
        tags=["淮安", "楚州"],
        summary="苏轼多次途经淮安",
        background="淮安古称楚州，苏轼从杭州北返或南下时多次途经此地",
        global_events=[
            Event(id="ha-001", date="熙宁四年（1071年）",
                  title="离京南下途经淮安",
                  description="苏轼离京赴杭州倅，途经淮安",
                  significance="途经淮安"),
        ],
        route_events={
            "route07": [
                Event(id="ha-002", date="熙宁四年（1071年）",
                      title="南下途经淮安",
                      description="苏轼南下赴杭州，途经淮安",
                      significance="途经淮安"),
            ],
            "route08": [
                Event(id="ha-003", date="元丰二年（1079年）",
                      title="南下知湖州途经淮安",
                      description="苏轼从徐州南下知湖州，途经淮安",
                      significance="途经淮安"),
            ],
            "route15": [
                Event(id="ha-006", date="元祐六年（1091年）",
                      title="移知颍州途经淮安",
                      description="苏轼移知颍州，途经淮安",
                      significance="途经淮安"),
            ],
            "route19": [
                Event(id="ha-007", date="绍圣元年（1094年）",
                      title="贬惠州途经淮安",
                      description="苏轼贬惠州，途经淮安",
                      significance="途经淮安"),
            ],
        },
        route_order={"route07": 5, "route08": 4, "route15": 5, "route18": 4},
        route_arrival={"route07": "熙宁四年（1071年）", "route08": "元丰二年（1079年）", "route15": "元祐六年（1091年）", "route18": "绍圣元年（1094年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="淮安站 / 淮安东站", bus="淮安汽车站", car="京沪高速"),
        source="李常生《苏轼行踪考》"
    )


def create_yizhou() -> PlaceDetail:
    """沂州/临沂 - 游历地"""
    memorial_sites = [
        MemorialSite(id="yz-s001", name="沂州古城", type="遗址",
                     location="山东省临沂市",
                     description="苏轼途经沂州",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="yizhou",
        name_song="沂州",
        name_modern="山东省临沂市",
        name_pinyin="Yizhou",
        latitude=35.1041,
        longitude=118.3565,
        place_type="游历地",
        tags=["沂州", "临沂"],
        summary="苏轼移知徐州途经沂州",
        background="沂州今山东临沂，苏轼从密州移知徐州时途经此地",
        route_events={
            "route07": [
                Event(id="yz-001", date="熙宁十年（1077年）",
                      title="移知徐州途经沂州",
                      description="苏轼从密州移知徐州，途经沂州",
                      significance="途经沂州"),
            ],
        },
        route_order={"route07": 2},
        route_arrival={"route07": "熙宁十年（1077年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="临沂站", bus="临沂汽车站", car="京沪高速"),
        source="李常生《苏轼行踪考》"
    )


def create_lushan() -> PlaceDetail:
    """庐山 - 游览地"""
    works = [
        Work(id="ls-w001", title="题西林壁",
             content="横看成岭侧成峰，远近高低各不同。不识庐山真面目，只缘身在此山中。",
             excerpt="不识庐山真面目，只缘身在此山中。",
             type="诗", date="元丰七年（1084年）五月",
             location="庐山西林寺",
             background="苏轼游庐山题诗于西林寺壁"),
        Work(id="ls-w002", title="初入庐山",
             content="青山若无素，偃蹇不相亲。要识庐山面，他年是故人。",
             excerpt="要识庐山面，他年是故人。",
             type="诗", date="元丰七年（1084年）五月",
             location="庐山",
             background="苏轼初入庐山时作"),
    ]

    memorial_sites = [
        MemorialSite(id="ls-s001", name="庐山", type="山",
                     location="江西省九江市",
                     description="苏轼游庐山",
                     opening_hours="全天", ticket="景区通票¥160", suggested_duration="1-3天", rating="AAAAA"),
        MemorialSite(id="ls-s002", name="西林寺", type="寺庙",
                     location="江西省九江市庐山",
                     description="苏轼题诗处",
                     opening_hours="08:00-17:00", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="lushan",
        name_song="庐山",
        name_modern="江西省九江市庐山",
        name_pinyin="Lushan",
        latitude=29.5728,
        longitude=115.9872,
        place_type="游览地",
        tags=["庐山", "山", "瀑布"],
        summary="苏轼游庐山，留下'不识庐山真面目'千古名句",
        background="庐山是苏轼元丰七年游历地，在此留下多篇诗作",
        global_events=[
            Event(id="ls-001", date="元丰七年（1084年）五月",
                  title="游庐山",
                  description="苏轼游庐山，作诗多首",
                  significance="庐山之游"),
        ],
        global_works=works,
        route_events={
            "route13": [
                Event(id="ls-002", date="元丰七年（1084年）五月",
                      title="游庐山",
                      description="苏轼量移汝州途中游庐山",
                      significance="庐山之游"),
            ],
        },
        route_order={"route12": 2},
        route_arrival={"route12": "元丰七年（1084年）五月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="九江站", bus="庐山汽车站", car="福银高速"),
        source="李常生《苏轼行踪考》"
    )


def create_gaoan() -> PlaceDetail:
    """高安 - 拜访地"""
    memorial_sites = [
        MemorialSite(id="ga-s001", name="大观楼", type="建筑",
                     location="江西省高安市",
                     description="高安古城楼",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    return PlaceDetail(
        place_id="gaoan",
        name_song="高安",
        name_modern="江西省高安市",
        name_pinyin="Gaoan",
        latitude=28.4252,
        longitude=115.3621,
        place_type="拜访地",
        tags=["高安", "好友"],
        summary="苏轼量移汝州途中访好友",
        background="高安是苏轼访好友的地方，苏轼元丰七年量移汝州途中经过此地",
        route_events={
            "route12": [
                Event(id="ga-001", date="元丰七年（1084年）",
                      title="访高安好友",
                      description="苏轼量移汝州途中拜访高安好友",
                      significance="途经高安"),
            ],
        },
        route_order={"route12": 3},
        route_arrival={"route12": "元丰七年（1084年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="高安站", bus="高安汽车站", car="沪昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_jinling() -> PlaceDetail:
    """金陵/江宁 - 拜访地"""
    works = [
        Work(id="jl-w001", title="泊船瓜洲",
             content="京口瓜洲一水间，钟山只隔数重山。春风又绿江南岸，明月何时照我还。",
             excerpt="春风又绿江南岸，明月何时照我还。",
             type="诗", date="元丰七年（1084年）",
             location="金陵/江宁",
             background="泊船瓜洲"),
    ]

    memorial_sites = [
        MemorialSite(id="jl-s001", name="钟山", type="山",
                     location="江苏省南京市",
                     description="钟山即紫金山",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
        MemorialSite(id="jl-s002", name="清凉寺", type="寺庙",
                     location="江苏省南京市",
                     description="苏轼曾游清凉寺",
                     opening_hours="08:00-17:00", ticket="¥10", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="jinling",
        name_song="金陵/江宁",
        name_modern="江苏省南京市",
        name_pinyin="Jinling",
        latitude=32.0603,
        longitude=118.7969,
        place_type="拜访地",
        tags=["金陵", "江宁", "王安石"],
        summary="苏轼拜访王安石于金陵",
        background="金陵即今南京，苏轼元丰七年量移汝州途中拜访退隐的王安石",
        global_events=[
            Event(id="jl-001", date="元丰七年（1084年）",
                  title="拜访王安石",
                  description="苏轼在金陵拜访退隐的王安石",
                  significance="王苏会面"),
        ],
        global_works=works,
        route_events={
            "route12": [
                Event(id="jl-002", date="元丰七年（1084年）",
                      title="拜访王安石",
                      description="苏轼量移汝州途中拜访王安石于金陵",
                      significance="王苏会面"),
            ],
            "route19": [
                Event(id="jl-003", date="建中靖国元年（1101年）",
                      title="北归途经金陵",
                      description="苏轼北归常州，途经金陵",
                      significance="途经金陵"),
            ],
        },
        route_order={"route12": 4, "route19": 13},
        route_arrival={"route12": "元丰七年（1084年）", "route19": "建中靖国元年（1101年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="南京站 / 南京南站", bus="南京汽车站", car="沪宁高速"),
        source="李常生《苏轼行踪考》"
    )


def create_dengzhou() -> PlaceDetail:
    """登州 - 任职地"""
    works = [
        Work(id="dz-w001", title="登州文庙",
             content="参观登州文庙",
             excerpt="登州文庙",
             type="文", date="元丰八年（1085年）",
             location="登州",
             background="登州文庙"),
    ]

    memorial_sites = [
        MemorialSite(id="dz-s001", name="蓬莱阁", type="阁",
                     location="山东省蓬莱市",
                     description="苏轼在登州常游蓬莱阁",
                     opening_hours="08:00-17:00", ticket="¥140", suggested_duration="2-3小时", rating="AAAAA"),
    ]

    return PlaceDetail(
        place_id="dengzhou",
        name_song="登州",
        name_modern="山东省蓬莱市",
        name_pinyin="Dengzhou",
        latitude=37.8043,
        longitude=120.7545,
        place_type="任职地",
        tags=["登州", "蓬莱", "知州"],
        summary="苏轼知登州仅五日即被召回",
        background="登州今山东蓬莱，苏轼元丰八年任知州，仅五日即被召回汴京",
        global_events=[
            Event(id="dz-001", date="元丰八年（1085年）",
                  title="任登州知州",
                  description="苏轼任登州知州",
                  significance="登州仕途"),
        ],
        global_works=works,
        route_events={
            "route13": [
                Event(id="dz-002", date="元丰八年（1085年）",
                      title="任登州知州仅五日",
                      description="苏轼到登州任知州，仅五日即被召回",
                      significance="任登州知州"),
            ],
        },
        route_order={"route13": 5},
        route_arrival={"route13": "元丰八年（1085年）"},
        route_departure={"route13": "元丰八年（1085年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="蓬莱站", bus="蓬莱汽车站", car="荣乌高速"),
        source="李常生《苏轼行踪考》"
    )


def create_dingzhou() -> PlaceDetail:
    """定州 - Route17知州"""
    memorial_sites = [
        MemorialSite(id="dz-s001", name="定州古塔", type="塔",
                     location="河北省定州市",
                     description="苏轼在定州时所建或相关",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="dingzhou",
        name_song="定州",
        name_modern="河北省定州市",
        name_pinyin="Dingzhou",
        latitude=38.5195,
        longitude=114.6774,
        place_type="任职地",
        tags=["定州", "中山"],
        summary="苏轼知定州",
        background="定州今河北定州，苏轼元祐八年知定州",
        global_events=[
            Event(id="dingzhou-001", date="元祐八年（1093年）",
                  title="知定州",
                  description="苏轼知定州",
                  significance="知定州"),
        ],
        route_events={
            "route18": [
                Event(id="dingzhou-002", date="元祐八年（1093年）",
                      title="知定州",
                      description="苏轼任知定州",
                      significance="知定州"),
            ],
        },
        route_order={"route17": 1},
        route_arrival={"route17": "元祐八年（1093年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="定州站", bus="定州汽车站",
                          car="京港澳高速"),
        source="李常生《苏轼行踪考》"
    )


def create_yinzhou() -> PlaceDetail:
    """英州 - Route18途经"""
    memorial_sites = [
        MemorialSite(id="yzz-s001", name="英德南山", type="山",
                     location="广东省英德市",
                     description="苏轼途经英州",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="yinzhou",
        name_song="英州",
        name_modern="广东省英德市",
        name_pinyin="Yinzhou",
        latitude=24.1855,
        longitude=113.4012,
        place_type="途经地",
        tags=["英州", "英德"],
        summary="苏轼贬惠州途经英州",
        background="英州今广东英德，苏轼贬惠州时途经此地",
        global_events=[
            Event(id="yzz-001", date="绍圣元年（1094年）",
                  title="过英州",
                  description="苏轼贬惠州，途经英州",
                  significance="途经英州"),
        ],
        route_events={
            "route18": [
                Event(id="yzz-002", date="绍圣元年（1094年）",
                      title="过英州赴惠州",
                      description="苏轼贬惠州，途经英州",
                      significance="途经英州"),
            ],
            "route19": [
                Event(id="yzz-003", date="元符三年（1100年）",
                      title="北归途经英州",
                      description="苏轼北归，途经英州",
                      significance="途经英州"),
            ],
        },
        route_order={"route18": 2, "route19": 5},
        route_arrival={"route18": "绍圣元年（1094年）", "route19": "元符三年（1100年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="英德站", bus="英德汽车站",
                          car="许广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_huizhou() -> PlaceDetail:
    """惠州 - Route18贬谪地"""
    works = [
        Work(id="hz-w001", title="食荔枝",
             content="罗浮山下四时春，卢橘杨梅次第新。日啖荔枝三百颗，不辞长作岭南人。",
             excerpt="日啖荔枝三百颗，不辞长作岭南人。",
             type="诗", date="绍圣二年（1095年）",
             location="惠州",
             background="苏轼在惠州食荔枝作此诗"),
    ]

    memorial_sites = [
        MemorialSite(id="hzh-s001", name="白鹤峰", type="山峰",
                     location="广东省惠州市惠城区",
                     description="苏轼在惠州时居于此",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
        MemorialSite(id="hzh-s002", name="西湖", type="湖泊",
                     location="广东省惠州市惠城区",
                     description="苏轼常游惠州西湖",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="huizhou",
        name_song="惠州",
        name_modern="广东省惠州市",
        name_pinyin="Huizhou",
        latitude=23.1115,
        longitude=114.4158,
        place_type="贬谪地",
        tags=["惠州", "岭南"],
        summary="苏轼贬惠州两年多，作《食荔枝》等诗",
        background="惠州今广东惠州，苏轼于绍圣元年贬惠州安置两年多",
        global_events=[
            Event(id="hzh-001", date="绍圣元年（1094年）十月二日",
                  title="到惠州贬所",
                  description="苏轼到惠州贬所",
                  significance="到惠州"),
        ],
        global_works=works,
        route_events={
            "route18": [
                Event(id="hzh-002", date="绍圣元年（1094年）十月二日",
                      title="到惠州贬所",
                      description="苏轼到惠州贬所",
                      significance="到惠州"),
                Event(id="hzh-003", date="绍圣四年（1097年）四月",
                      title="再贬儋州",
                      description="苏轼再贬儋州",
                      significance="再贬儋州"),
            ],
        },
        route_order={"route18": 3},
        route_arrival={"route18": "绍圣元年（1094年）十月"},
        route_departure={"route18": "绍圣四年（1097年）四月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="惠州站", bus="惠州汽车站",
                          car="济广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_danzhou() -> PlaceDetail:
    """儋州 - Route19贬谪地"""
    memorial_sites = [
        MemorialSite(id="danz-s001", name="桄榔庵", type="庵",
                     location="海南省儋州市",
                     description="苏轼在儋州时居所",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
        MemorialSite(id="danz-s002", name="载酒堂", type="堂",
                     location="海南省儋州市",
                     description="苏轼在儋州讲学之所",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="danzhou",
        name_song="儋州",
        name_modern="海南省儋州市",
        name_pinyin="Danzhou",
        latitude=19.5176,
        longitude=109.5806,
        place_type="贬谪地",
        tags=["儋州", "海南"],
        summary="苏轼贬儋州三年，在载酒堂讲学",
        background="儋州今海南儋州，苏轼于绍圣四年贬儋州，元符三年遇赦北归",
        global_events=[
            Event(id="danz-001", date="绍圣四年（1097年）四月",
                  title="到儋州贬所",
                  description="苏轼到儋州贬所",
                  significance="到儋州"),
        ],
        route_events={
            "route19": [
                Event(id="danz-002", date="绍圣四年（1097年）四月",
                      title="到儋州贬所",
                      description="苏轼到儋州贬所",
                      significance="到儋州"),
                Event(id="danz-003", date="元符三年（1100年）六月",
                      title="离儋州北归",
                      description="苏轼遇赦，离儋州北归",
                      significance="离儋州"),
            ],
        },
        route_order={"route19": 1},
        route_arrival={"route19": "绍圣四年（1097年）四月"},
        route_departure={"route19": "元符三年（1100年）六月"},
        memorial_sites=memorial_sites,
        transport=Transport(plane="海口美兰机场", bus="儋州汽车站",
                          car="海南环岛高速"),
        source="李常生《苏轼行踪考》"
    )


def create_leizhou() -> PlaceDetail:
    """雷州 - Route19途经"""
    memorial_sites = [
        MemorialSite(id="leiz-s001", name="苏公亭", type="亭",
                     location="广东省雷州市",
                     description="纪念苏轼而建",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="leizhou",
        name_song="雷州",
        name_modern="广东省雷州市",
        name_pinyin="Leizhou",
        latitude=20.9140,
        longitude=110.1026,
        place_type="途经地",
        tags=["雷州", "海康"],
        summary="苏轼北归途经雷州",
        background="雷州今广东雷州，苏轼北归时途经此地",
        global_events=[
            Event(id="leiz-001", date="元符三年（1100年）",
                  title="过雷州",
                  description="苏轼北归，途经雷州",
                  significance="途经雷州"),
        ],
        route_events={
            "route19": [
                Event(id="leiz-002", date="元符三年（1100年）七月",
                      title="过雷州",
                      description="苏轼北归，途经雷州",
                      significance="途经雷州"),
            ],
        },
        route_order={"route19": 2},
        route_arrival={"route19": "元符三年（1100年）七月"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="雷州汽车站", car="沈海高速"),
        source="李常生《苏轼行踪考》"
    )


def create_lianzhou() -> PlaceDetail:
    """廉州 - Route19途经"""
    memorial_sites = [
        MemorialSite(id="lianz-s001", name="海角亭", type="亭",
                     location="广西壮族自治区合浦县",
                     description="苏轼曾至此",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="lianzhou",
        name_song="廉州",
        name_modern="广西壮族自治区合浦县",
        name_pinyin="Lianzhou",
        latitude=21.6226,
        longitude=109.2065,
        place_type="途经地",
        tags=["廉州", "合浦"],
        summary="苏轼北归途经廉州",
        background="廉州今广西合浦，苏轼北归时途经此地并任知州",
        global_events=[
            Event(id="lianz-001", date="元符三年（1100年）",
                  title="知廉州",
                  description="苏轼北归，授知廉州",
                  significance="知廉州"),
        ],
        route_events={
            "route19": [
                Event(id="lianz-002", date="元符三年（1100年）七月",
                      title="到廉州",
                      description="苏轼到廉州",
                      significance="到廉州"),
            ],
        },
        route_order={"route19": 3},
        route_arrival={"route19": "元符三年（1100年）七月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="合浦站", bus="合浦汽车站",
                          car="兰海高速"),
        source="李常生《苏轼行踪考》"
    )


def create_changzhou_route() -> PlaceDetail:
    """常州 - Route19终点"""
    memorial_sites = [
        MemorialSite(id="changz-s001", name="藤花旧馆", type="遗址",
                     location="江苏省常州市",
                     description="苏轼卒于此",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
        MemorialSite(id="changz-s002", name="东坡公园", type="公园",
                     location="江苏省常州市",
                     description="纪念苏轼而建",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="changzhou",
        name_song="常州",
        name_modern="江苏省常州市",
        name_pinyin="Changzhou",
        latitude=31.8106,
        longitude=119.9741,
        place_type="终点",
        tags=["常州", "毗陵"],
        summary="苏轼北归卒于常州",
        background="常州今江苏常州，苏轼建中靖国元年卒于此",
        global_events=[
            Event(id="changz-001", date="建中靖国元年（1101年）七月二十八日",
                  title="卒于常州",
                  description="苏轼卒于常州",
                  significance="卒于常州"),
        ],
        route_events={
            "route19": [
                Event(id="changz-002", date="建中靖国元年（1101年）七月",
                      title="到常州",
                      description="苏轼北归至常州",
                      significance="到常州"),
                Event(id="changz-003", date="建中靖国元年（1101年）七月二十八日",
                      title="卒于常州",
                      description="苏轼卒于常州孙氏公馆",
                      significance="卒于常州"),
            ],
        },
        route_order={"route19": 10},
        route_arrival={"route19": "建中靖国元年（1101年）七月"},
        memorial_sites=memorial_sites,
        transport=Transport(train="常州站/常州北站", bus="常州汽车站",
                          car="沪宁高速"),
        source="李常生《苏轼行踪考》"
    )


def create_zhenjiang() -> PlaceDetail:
    """镇江/润州 - 游历地"""
    works = [
        Work(id="zj-w001", title="游金山寺",
             content="金山何时去，此地去金山。",
             excerpt="金山何时去，此地去金山。",
             type="诗", date="熙宁四年（1071年）",
             location="镇江金山寺",
             background="游金山寺"),
    ]

    memorial_sites = [
        MemorialSite(id="zj-s001", name="金山寺", type="寺庙",
                     location="江苏省镇江市",
                     description="金山寺是镇江名刹",
                     opening_hours="08:00-17:00", ticket="¥50", suggested_duration="2-3小时"),
        MemorialSite(id="zj-s002", name="焦山", type="山",
                     location="江苏省镇江市",
                     description="苏轼常游焦山",
                     opening_hours="08:00-17:00", ticket="¥65", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="zhenjiang",
        name_song="润州/镇江",
        name_modern="江苏省镇江市",
        name_pinyin="Zhenjiang",
        latitude=32.2044,
        longitude=119.4556,
        place_type="游历地",
        tags=["镇江", "润州", "金山寺"],
        summary="苏轼多次途经镇江，游金山寺",
        background="镇江古称润州，是苏轼从杭州北上或南下的重要中转地",
        global_events=[
            Event(id="zj-001", date="熙宁四年（1071年）",
                  title="南下途经镇江",
                  description="苏轼南下赴杭州倅，途经润州游金山寺",
                  significance="途经镇江"),
        ],
        global_works=works,
        route_events={
            "route07": [
                Event(id="zj-002", date="熙宁四年（1071年）",
                      title="南下途经润州",
                      description="苏轼南下赴杭州，途经润州",
                      significance="途经润州"),
            ],
        },
        route_order={"route07": 6},
        route_arrival={"route07": "熙宁四年（1071年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="镇江站 / 镇江南站", bus="镇江汽车站", car="沪宁高速"),
        source="李常生《苏轼行踪考》"
    )


def create_chuzhou() -> PlaceDetail:
    """滁州 - 游历地"""
    memorial_sites = [
        MemorialSite(id="cz-s001", name="琅琊山", type="山",
                     location="安徽省滁州市",
                     description="欧阳修《醉翁亭记》所在地",
                     opening_hours="全天", ticket="免费", suggested_duration="3-4小时"),
        MemorialSite(id="cz-s002", name="醉翁亭", type="亭",
                     location="安徽省滁州市琅琊山",
                     description="欧阳修《醉翁亭记》",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="chuzhou",
        name_song="滁州",
        name_modern="安徽省滁州市",
        name_pinyin="Chuzhou",
        latitude=32.3018,
        longitude=118.3126,
        place_type="游历地",
        tags=["滁州", "醉翁亭", "欧阳修"],
        summary="苏轼移知扬州途经滁州，游琅琊山",
        background="滁州是欧阳修《醉翁亭记》所在地，苏轼元祐七年移知扬州时途经此地",
        route_events={
            "route17": [
                Event(id="cz-001", date="元祐七年（1092年）",
                      title="移知扬州途经滁州",
                      description="苏轼移知扬州，途经滁州游琅琊山",
                      significance="途经滁州"),
            ],
        },
        route_order={"route16": 2},
        route_arrival={"route16": "元祐七年（1092年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="滁州站", bus="滁州汽车站", car="宁洛高速"),
        source="李常生《苏轼行踪考》"
    )


def create_jiangzhou() -> PlaceDetail:
    """江州/九江 - 游历地"""
    memorial_sites = [
        MemorialSite(id="jz-s001", name="琵琶亭", type="亭",
                     location="江西省九江市",
                     description="白居易《琵琶行》所在地",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    return PlaceDetail(
        place_id="jiangzhou",
        name_song="江州/九江",
        name_modern="江西省九江市",
        name_pinyin="Jiangzhou",
        latitude=29.7052,
        longitude=116.0012,
        place_type="游历地",
        tags=["江州", "九江", "琵琶亭"],
        summary="苏轼贬惠州途经江州",
        background="江州即今九江，是苏轼贬惠州南下的重要中转地",
        route_events={
            "route18": [
                Event(id="jz-001", date="绍圣元年（1094年）",
                      title="贬惠州途经江州",
                      description="苏轼贬惠州，途经江州",
                      significance="途经江州"),
            ],
        },
        route_order={"route18": 5},
        route_arrival={"route18": "绍圣元年（1094年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="九江站", bus="九江汽车站", car="福银高速"),
        source="李常生《苏轼行踪考》"
    )


def create_ganzhou() -> PlaceDetail:
    """赣州 - 游历地"""
    memorial_sites = [
        MemorialSite(id="gz-s001", name="郁孤台", type="台",
                     location="江西省赣州市",
                     description="苏轼游郁孤台",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="ganzhou",
        name_song="赣州",
        name_modern="江西省赣州市",
        name_pinyin="Ganzhou",
        latitude=25.8312,
        longitude=114.9312,
        place_type="途经地",
        tags=["赣州", "虔州"],
        summary="苏轼贬惠州及北归均途经赣州",
        background="赣州古称虔州，苏轼贬惠州南行及北归时均途经此地",
        route_events={
            "route18": [
                Event(id="gz-001", date="绍圣元年（1094年）",
                      title="贬惠州途经赣州",
                      description="苏轼贬惠州，途经赣州",
                      significance="途经赣州"),
            ],
            "route19": [
                Event(id="gz-002", date="元符三年（1100年）",
                      title="北归途经赣州",
                      description="苏轼北归，途经赣州",
                      significance="途经赣州"),
            ],
        },
        route_order={"route18": 6, "route19": 7},
        route_arrival={"route18": "绍圣元年（1094年）", "route19": "元符三年（1100年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="赣州站", bus="赣州汽车站", car="大广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_dayuling() -> PlaceDetail:
    """大庾岭 - 途经地"""
    memorial_sites = [
        MemorialSite(id="dyl-s001", name="梅岭", type="岭",
                     location="江西省大余县",
                     description="大庾岭即梅岭",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="dayuling",
        name_song="大庾岭",
        name_modern="江西省大余县/广东省南雄市",
        name_pinyin="Dayuling",
        latitude=25.3912,
        longitude=114.3512,
        place_type="途经地",
        tags=["大庾岭", "梅岭", "南下"],
        summary="苏轼越过大庾岭南行入粤",
        background="大庾岭即梅岭，是苏轼贬惠州南下的必经之路，越过此岭即进入广东",
        route_events={
            "route18": [
                Event(id="dyl-001", date="绍圣元年（1094年）",
                      title="越大庾岭南行",
                      description="苏轼贬惠州，越大庾岭进入广东",
                      significance="越岭南下"),
            ],
        },
        route_order={"route18": 7},
        route_arrival={"route18": "绍圣元年（1094年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="梅岭汽车站", car="赣韶高速"),
        source="李常生《苏轼行踪考》"
    )


def create_nankang() -> PlaceDetail:
    """南康 - 途经地"""
    return PlaceDetail(
        place_id="nankang",
        name_song="南康军",
        name_modern="江西省南康市",
        name_pinyin="Nankang",
        latitude=25.6812,
        longitude=114.7512,
        place_type="途经地",
        tags=["南康", "赣州"],
        summary="苏轼贬惠州途经南康",
        background="南康军今江西南康，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="nk-001", date="绍圣元年（1094年）",
                      title="贬惠州途经南康",
                      description="苏轼贬惠州，途经南康",
                      significance="途经南康"),
            ],
        },
        route_order={"route18": 6},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(bus="南康汽车站", car="大广高速"),
        source="李常生《苏轼行踪考》"
    )


def create_pengli() -> PlaceDetail:
    """彭蠡 - 途经地"""
    return PlaceDetail(
        place_id="pengli",
        name_song="彭蠡湖",
        name_modern="江西省鄱阳湖",
        name_pinyin="Pengli",
        latitude=29.3312,
        longitude=116.0912,
        place_type="途经地",
        tags=["彭蠡", "鄱阳湖"],
        summary="苏轼贬惠州途经彭蠡湖",
        background="彭蠡湖即今鄱阳湖，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="pl-001", date="绍圣元年（1094年）",
                      title="贬惠州途经彭蠡",
                      description="苏轼贬惠州，途经彭蠡湖",
                      significance="途经彭蠡"),
            ],
        },
        route_order={"route18": 5},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(bus="鄱阳汽车站", car="杭瑞高速"),
        source="李常生《苏轼行踪考》"
    )


def create_hukou() -> PlaceDetail:
    """湖口 - 途经地"""
    return PlaceDetail(
        place_id="hukou",
        name_song="湖口",
        name_modern="江西省湖口县",
        name_pinyin="Hukou",
        latitude=29.7512,
        longitude=116.2212,
        place_type="途经地",
        tags=["湖口", "石钟山"],
        summary="苏轼贬惠州途经湖口",
        background="湖口今江西湖口，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="hk-001", date="绍圣元年（1094年）",
                      title="贬惠州途经湖口",
                      description="苏轼贬惠州，途经湖口",
                      significance="途经湖口"),
            ],
        },
        route_order={"route18": 4},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(bus="湖口汽车站", car="杭瑞高速"),
        source="李常生《苏轼行踪考》"
    )


def create_dangtu() -> PlaceDetail:
    """当涂 - 途经地"""
    return PlaceDetail(
        place_id="dangtu",
        name_song="当涂",
        name_modern="安徽省当涂县",
        name_pinyin="Dangtu",
        latitude=31.5512,
        longitude=118.4912,
        place_type="途经地",
        tags=["当涂", "采石矶"],
        summary="苏轼贬惠州途经当涂",
        background="当涂今安徽当涂，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="dt-001", date="绍圣元年（1094年）",
                      title="贬惠州途经当涂",
                      description="苏轼贬惠州，途经当涂",
                      significance="途经当涂"),
            ],
        },
        route_order={"route18": 3},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(bus="当涂汽车站", car="宁芜高速"),
        source="李常生《苏轼行踪考》"
    )


def create_changlu() -> PlaceDetail:
    """长芦 - 途经地"""
    return PlaceDetail(
        place_id="changlu",
        name_song="长芦",
        name_modern="江苏省南京市六合区",
        name_pinyin="Changlu",
        latitude=32.3112,
        longitude=118.8212,
        place_type="途经地",
        tags=["长芦", "六合"],
        summary="苏轼贬惠州途经长芦",
        background="长芦今江苏六合，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="cl-001", date="绍圣元年（1094年）",
                      title="贬惠州途经长芦",
                      description="苏轼贬惠州，途经长芦",
                      significance="途经长芦"),
            ],
        },
        route_order={"route18": 2},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(bus="六合汽车站", car="宁洛高速"),
        source="李常生《苏轼行踪考》"
    )


def create_zhenzhou() -> PlaceDetail:
    """真州 - 途经地"""
    return PlaceDetail(
        place_id="zhenzhou",
        name_song="真州",
        name_modern="江苏省仪征市",
        name_pinyin="Zhenzhou",
        latitude=32.2712,
        longitude=119.1812,
        place_type="途经地",
        tags=["真州", "仪征"],
        summary="苏轼贬惠州途经真州",
        background="真州今江苏仪征，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="zz-001", date="绍圣元年（1094年）",
                      title="贬惠州途经真州",
                      description="苏轼贬惠州，途经真州",
                      significance="途经真州"),
            ],
        },
        route_order={"route18": 1},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(bus="仪征汽车站", car="宁扬高速"),
        source="李常生《苏轼行踪考》"
    )


def create_nanxiongzhou() -> PlaceDetail:
    """南雄州 - 途经地"""
    return PlaceDetail(
        place_id="nanxiongzhou",
        name_song="南雄州",
        name_modern="广东省南雄市",
        name_pinyin="Nanxiongzhou",
        latitude=25.1312,
        longitude=114.3112,
        place_type="途经地",
        tags=["南雄", "梅关"],
        summary="苏轼贬惠州途经南雄州",
        background="南雄州今广东南雄，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="nxz-001", date="绍圣元年（1094年）",
                      title="贬惠州途经南雄州",
                      description="苏轼贬惠州，途经南雄州",
                      significance="途经南雄州"),
            ],
        },
        route_order={"route18": 8},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(bus="南雄汽车站", car="赣韶高速"),
        source="李常生《苏轼行踪考》"
    )


def create_shaozhou() -> PlaceDetail:
    """韶州 - 途经地"""
    return PlaceDetail(
        place_id="shaozhou",
        name_song="韶州",
        name_modern="广东省韶关市",
        name_pinyin="Shaozhou",
        latitude=24.8012,
        longitude=113.5912,
        place_type="途经地",
        tags=["韶州", "韶关"],
        summary="苏轼贬惠州途经韶州",
        background="韶州今广东韶关，苏轼贬惠州时途经此地",
        route_events={
            "route18": [
                Event(id="sz-001", date="绍圣元年（1094年）",
                      title="贬惠州途经韶州",
                      description="苏轼贬惠州，途经韶州",
                      significance="途经韶州"),
            ],
        },
        route_order={"route18": 9},
        route_arrival={"route18": "绍圣元年（1094年）"},
        transport=Transport(train="韶关站", bus="韶关汽车站", car="京港澳高速"),
        source="李常生《苏轼行踪考》"
    )


def create_chengmai() -> PlaceDetail:
    """澄迈 - 途经地"""
    return PlaceDetail(
        place_id="chengmai",
        name_song="澄迈",
        name_modern="海南省澄迈县",
        name_pinyin="Chengmai",
        latitude=19.7512,
        longitude=110.0212,
        place_type="途经地",
        tags=["澄迈", "渡海"],
        summary="苏轼北归途经澄迈",
        background="澄迈今海南澄迈，苏轼北归时途经此地渡海",
        route_events={
            "route19": [
                Event(id="cm-001", date="元符三年（1100年）",
                      title="北归途经澄迈",
                      description="苏轼北归，途经澄迈渡海",
                      significance="渡海北上"),
            ],
        },
        route_order={"route19": 1},
        route_arrival={"route19": "元符三年（1100年）"},
        transport=Transport(bus="澄迈汽车站", car="海南环岛高速"),
        source="李常生《苏轼行踪考》"
    )


def create_guangzhou() -> PlaceDetail:
    """广州 - 途经地"""
    memorial_sites = [
        MemorialSite(id="gz2-s001", name="镇海楼", type="楼",
                     location="广东省广州市越秀山",
                     description="广州古城标志建筑",
                     opening_hours="09:00-17:00", ticket="¥10", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="guangzhou",
        name_song="广州",
        name_modern="广东省广州市",
        name_pinyin="Guangzhou",
        latitude=23.1291,
        longitude=113.2644,
        place_type="途经地",
        tags=["广州", "岭南"],
        summary="苏轼贬惠州、儋州时途经广州",
        background="广州是岭南重镇，苏轼南贬时多次途经此地",
        route_events={
            "route18": [
                Event(id="gz2-001", date="绍圣元年（1094年）",
                      title="贬惠州途经广州",
                      description="苏轼贬惠州，途经广州",
                      significance="途经广州"),
            ],
            "route19": [
                Event(id="gz2-002", date="绍圣四年（1097年）",
                      title="贬儋州途经广州",
                      description="苏轼贬儋州，途经广州",
                      significance="途经广州"),
                Event(id="gz2-003", date="元符三年（1100年）",
                      title="北归途经广州",
                      description="苏轼北归，途经广州",
                      significance="途经广州"),
            ],
        },
        route_order={"route18": 8, "route19": 2, "route19": 5},
        route_arrival={"route18": "绍圣元年（1094年）", "route19": "绍圣四年（1097年）", "route19": "元符三年（1100年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="广州站 / 广州南站", bus="广州市汽车站", car="京港澳高速"),
        source="李常生《苏轼行踪考》"
    )


def create_heshan() -> PlaceDetail:
    """鹤山 - 途经地"""
    memorial_sites = [
        MemorialSite(id="hs-s001", name="坡亭", type="亭",
                     location="广东省鹤山市",
                     description="苏轼泊舟避汐处",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
    ]

    return PlaceDetail(
        place_id="heshan",
        name_song="鹤山/石螺岗",
        name_modern="广东省鹤山市",
        name_pinyin="Heshan",
        latitude=22.7612,
        longitude=112.9512,
        place_type="途经地",
        tags=["鹤山", "坡亭"],
        summary="苏轼贬儋州途经鹤山泊舟",
        background="鹤山古称石螺岗，苏轼贬儋州时曾在此泊舟避汐",
        route_events={
            "route19": [
                Event(id="hs-001", date="绍圣四年（1097年）",
                      title="贬儋州途经鹤山",
                      description="苏轼贬儋州，途经鹤山泊舟避汐",
                      significance="途经鹤山"),
            ],
        },
        route_order={"route19": 3},
        route_arrival={"route19": "绍圣四年（1097年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="鹤山汽车站", car="沈海高速"),
        source="李常生《苏轼行踪考》"
    )


def create_zhaoqing() -> PlaceDetail:
    """肇庆 - 途经地"""
    memorial_sites = [
        MemorialSite(id="zq-s001", name="七星岩", type="岩",
                     location="广东省肇庆市",
                     description="肇庆著名风景区",
                     opening_hours="08:00-18:00", ticket="¥78", suggested_duration="3-4小时", rating="AAAAA"),
    ]

    return PlaceDetail(
        place_id="zhaoqing",
        name_song="肇庆/康州",
        name_modern="广东省肇庆市",
        name_pinyin="Zhaoqing",
        latitude=23.0512,
        longitude=112.4712,
        place_type="途经地",
        tags=["肇庆", "康州", "七星岩"],
        summary="苏轼贬儋州途经肇庆",
        background="肇庆古称康州，苏轼贬儋州时途经此地",
        route_events={
            "route19": [
                Event(id="zq-001", date="绍圣四年（1097年）",
                      title="贬儋州途经肇庆",
                      description="苏轼贬儋州，途经肇庆",
                      significance="途经肇庆"),
            ],
        },
        route_order={"route19": 4},
        route_arrival={"route19": "绍圣四年（1097年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="肇庆站", bus="肇庆汽车站", car="广昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_deqing() -> PlaceDetail:
    """德庆 - 途经地"""
    memorial_sites = [
        MemorialSite(id="dq-s001", name="德庆古城", type="城",
                     location="广东省德庆县",
                     description="德庆古城",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="deqing",
        name_song="德庆/康州",
        name_modern="广东省德庆县",
        name_pinyin="Deqing",
        latitude=23.1412,
        longitude=111.7712,
        place_type="途经地",
        tags=["德庆", "康州"],
        summary="苏轼贬儋州途经德庆",
        background="德庆古称康州，苏轼贬儋州时途经此地",
        route_events={
            "route19": [
                Event(id="dq-001", date="绍圣四年（1097年）",
                      title="贬儋州途经德庆",
                      description="苏轼贬儋州，途经德庆",
                      significance="途经德庆"),
            ],
        },
        route_order={"route19": 5},
        route_arrival={"route19": "绍圣四年（1097年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="德庆汽车站", car="广昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_wuzhou() -> PlaceDetail:
    """梧州 - 途经地"""
    memorial_sites = [
        MemorialSite(id="wz-s001", name="白云山", type="山",
                     location="广西梧州市",
                     description="梧州白云山",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="wuzhou",
        name_song="梧州",
        name_modern="广西梧州市",
        name_pinyin="Wuzhou",
        latitude=23.4712,
        longitude=111.2812,
        place_type="途经地",
        tags=["梧州", "桂江"],
        summary="苏轼贬儋州途经梧州",
        background="梧州是岭南重镇，苏轼贬儋州时途经此地",
        route_events={
            "route19": [
                Event(id="wz-001", date="绍圣四年（1097年）",
                      title="贬儋州途经梧州",
                      description="苏轼贬儋州，途经梧州",
                      significance="途经梧州"),
            ],
        },
        route_order={"route19": 6},
        route_arrival={"route19": "绍圣四年（1097年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="梧州站", bus="梧州汽车站", car="包茂高速"),
        source="李常生《苏轼行踪考》"
    )


def create_tengzhou() -> PlaceDetail:
    """藤州 - 途经地"""
    memorial_sites = [
        MemorialSite(id="tengz-s001", name="藤州古城", type="城",
                     location="广西藤县",
                     description="藤州古城遗址",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="tengzhou",
        name_song="藤州",
        name_modern="广西藤县",
        name_pinyin="Tengzhou",
        latitude=23.4112,
        longitude=110.8112,
        place_type="途经地",
        tags=["藤州", "藤县"],
        summary="苏轼贬儋州途经藤州，与苏辙相遇",
        background="藤州今广西藤县，苏轼贬儋州时途经此地，与苏辙相遇",
        route_events={
            "route19": [
                Event(id="tengz-001", date="绍圣四年（1097年）",
                      title="贬儋州途经藤州",
                      description="苏轼贬儋州，途经藤州与苏辙相遇",
                      significance="兄弟相遇"),
            ],
        },
        route_order={"route19": 7},
        route_arrival={"route19": "绍圣四年（1097年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="藤县汽车站", car="包茂高速"),
        source="李常生《苏轼行踪考》"
    )


def create_rongzhou() -> PlaceDetail:
    """容州 - 途经地"""
    memorial_sites = [
        MemorialSite(id="rongz-s001", name="容州古城", type="城",
                     location="广西容县",
                     description="容州古城",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="rongzhou",
        name_song="容州",
        name_modern="广西容县",
        name_pinyin="Rongzhou",
        latitude=22.8512,
        longitude=110.5512,
        place_type="途经地",
        tags=["容州", "容县"],
        summary="苏轼贬儋州途经容州",
        background="容州今广西容县，苏轼贬儋州时途经此地",
        route_events={
            "route19": [
                Event(id="rongz-001", date="绍圣四年（1097年）",
                      title="贬儋州途经容州",
                      description="苏轼贬儋州，途经容州",
                      significance="途经容州"),
            ],
        },
        route_order={"route19": 8},
        route_arrival={"route19": "绍圣四年（1097年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="容县汽车站", car="广昆高速"),
        source="李常生《苏轼行踪考》"
    )


def create_leizhou() -> PlaceDetail:
    """雷州 - 途经地"""
    memorial_sites = [
        MemorialSite(id="leiz-s001", name="雷州古城", type="城",
                     location="广东省雷州市",
                     description="雷州古城",
                     opening_hours="全天", ticket="免费", suggested_duration="2-3小时"),
    ]

    return PlaceDetail(
        place_id="leizhou",
        name_song="雷州",
        name_modern="广东省雷州市",
        name_pinyin="Leizhou",
        latitude=20.9112,
        longitude=110.0912,
        place_type="途经地",
        tags=["雷州", "半岛"],
        summary="苏轼贬儋州途经雷州半岛",
        background="雷州今广东雷州市，苏轼贬儋州时途经此地",
        route_events={
            "route19": [
                Event(id="leiz-001", date="绍圣四年（1097年）",
                      title="贬儋州途经雷州",
                      description="苏轼贬儋州，途经雷州",
                      significance="途经雷州"),
                Event(id="leiz-002", date="元符三年（1100年）",
                      title="北归途经雷州",
                      description="苏轼北归，途经雷州",
                      significance="途经雷州"),
            ],
        },
        route_order={"route19": 9, "route19": 4},
        route_arrival={"route19": "绍圣四年（1097年）", "route19": "元符三年（1100年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="雷州汽车站", car="沈海高速"),
        source="李常生《苏轼行踪考》"
    )


def create_xuwen() -> PlaceDetail:
    """徐闻 - 渡海地"""
    memorial_sites = [
        MemorialSite(id="xw-s001", name="徐闻古城", type="城",
                     location="广东省徐闻县",
                     description="苏轼渡海出发地",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="xuwen",
        name_song="徐闻",
        name_modern="广东省徐闻县",
        name_pinyin="Xuwen",
        latitude=20.3312,
        longitude=110.1712,
        place_type="渡海地",
        tags=["徐闻", "渡海", "海峡"],
        summary="苏轼渡琼州海峡的出发地",
        background="徐闻是苏轼渡琼州海峡前往海南的出发地",
        route_events={
            "route19": [
                Event(id="xw-001", date="绍圣四年（1097年）",
                      title="渡海前往儋州",
                      description="苏轼从徐闻渡海前往儋州",
                      significance="渡海南下"),
                Event(id="xw-002", date="元符三年（1100年）",
                      title="渡海北归",
                      description="苏轼从徐闻渡海北归",
                      significance="渡海北归"),
            ],
        },
        route_order={"route19": 10, "route19": 3},
        route_arrival={"route19": "绍圣四年（1097年）", "route19": "元符三年（1100年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="徐闻汽车站", car="沈海高速"),
        source="李常生《苏轼行踪考》"
    )


def create_qiongzhou() -> PlaceDetail:
    """琼州/海口 - 途经地"""
    memorial_sites = [
        MemorialSite(id="qiongz-s001", name="五公祠", type="祠",
                     location="海南省海口市",
                     description="纪念苏轼五公",
                     opening_hours="08:00-18:00", ticket="¥20", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="qiongzhou",
        name_song="琼州/海口",
        name_modern="海南省海口市",
        name_pinyin="Qiongzhou",
        latitude=20.0412,
        longitude=110.3212,
        place_type="途经地",
        tags=["琼州", "海口", "海南"],
        summary="苏轼渡海后在琼州停留",
        background="琼州即今海口，苏轼渡海后在此停留，然后前往儋州",
        route_events={
            "route19": [
                Event(id="qiongz-001", date="绍圣四年（1097年）",
                      title="渡海至琼州",
                      description="苏轼从徐闻渡海至琼州",
                      significance="渡海抵琼"),
                Event(id="qiongz-002", date="元符三年（1100年）",
                      title="北归途经琼州",
                      description="苏轼北归，途经琼州",
                      significance="途经琼州"),
            ],
        },
        route_order={"route19": 11, "route19": 2},
        route_arrival={"route19": "绍圣四年（1097年）", "route19": "元符三年（1100年）"},
        memorial_sites=memorial_sites,
        transport=Transport(train="海口站", bus="海口汽车站", car="海南环岛高速"),
        source="李常生《苏轼行踪考》"
    )


def create_danzhou() -> PlaceDetail:
    """儋州 - 贬谪地"""
    works = [
        Work(id="dz2-w001", title="海南日记",
             content="九死南荒吾不恨，兹游奇绝冠平生。",
             excerpt="九死南荒吾不恨，兹游奇绝冠平生。",
             type="诗", date="元符三年（1100年）",
             location="儋州",
             background="苏轼离海南诗"),
        Work(id="dz2-w002", title="答谢民师书",
             content="《答谢民师书》",
             excerpt="轼顿首。",
             type="文", date="元符三年（1100年）",
             location="儋州",
             background="在儋州所作"),
    ]

    memorial_sites = [
        MemorialSite(id="dz2-s001", name="东坡书院", type="书院",
                     location="海南省儋州市中和镇",
                     description="苏轼在儋州讲学授徒处",
                     opening_hours="08:00-18:00", ticket="¥25", suggested_duration="1-2小时"),
        MemorialSite(id="dz2-s002", name="桄榔庵", type="庵",
                     location="海南省儋州市",
                     description="苏轼在儋州的居所",
                     opening_hours="全天", ticket="免费", suggested_duration="1小时"),
        MemorialSite(id="dz2-s003", name="载酒堂", type="堂",
                     location="海南省儋州市",
                     description="苏轼以文会友处",
                     opening_hours="全天", ticket="免费", suggested_duration="1-2小时"),
    ]

    return PlaceDetail(
        place_id="danzhou",
        name_song="儋州",
        name_modern="海南省儋州市",
        name_pinyin="Danzhou",
        latitude=19.5112,
        longitude=109.5812,
        place_type="贬谪地",
        tags=["儋州", "海南", "贬谪", "讲学"],
        summary="苏轼贬谪海南儋州三年，在此讲学授徒",
        background="儋州是苏轼最后一个贬谪地，在此三年讲学授徒，对海南文化影响深远",
        global_events=[
            Event(id="dz2-001", date="绍圣四年（1097年）",
                  title="贬谪儋州",
                  description="苏轼再贬儋州",
                  significance="再贬岭南"),
            Event(id="dz2-002", date="元符三年（1100年）",
                  title="赦还北归",
                  description="苏轼遇赦北归",
                  significance="北归"),
        ],
        global_works=works,
        route_events={
            "route19": [
                Event(id="dz2-003", date="绍圣四年（1097年）",
                      title="到儋州",
                      description="苏轼抵达儋州",
                      significance="抵儋州"),
                Event(id="dz2-004", date="绍圣四年至元符三年（1097-1100年）",
                      title="讲学授徒",
                      description="苏轼在儋州讲学授徒",
                      significance="儋州讲学"),
            ],
        },
        route_order={"route19": 12},
        route_arrival={"route19": "绍圣四年（1097年）"},
        route_departure={"route19": "元符三年（1100年）"},
        memorial_sites=memorial_sites,
        transport=Transport(bus="儋州汽车站", car="海南环岛高速"),
        source="李常生《苏轼行踪考》"
    )


def create_places_dataset() -> Dict:
    """创建完整地点数据集"""
    places = [
        create_meishan(),
        create_chengdu(),
        create_langzhong(),
        create_jianmen(),
        create_lizhou(),
        create_fengxiang(),
        create_changan(),
        create_mianchi(),
        create_bianjing(),
        create_zizhou(),
        create_yanting(),
        create_huangzhou(),
        create_guangzhou_henan(),
        create_macheng(),
        create_laizhou(),
        create_nandu(),
        create_tanzhou(),
        create_huaqing(),
        create_huazhou(),
        create_damingfu(),
        create_sizhou(),
        create_xuyi(),
        create_jiangling(),
        create_fengdu(),
        create_wenan(),
        create_xiaoyan(),
        create_xiandushan(),
        create_fankou(),
        create_guishan(),
        create_zhaohua(),
        create_hangzhou(),
        create_chengzhou(),
        create_yingzhou(),
        create_shouzhou(),
        create_yangzhou(),
        create_runzhou(),
        create_suzhou(),
        create_gaoyou(),
        create_haizhou(),
        create_mizhou(),
        create_yizhou(),
        create_yuncheng(),
        create_xuzhou(),
        create_huzhou(),
        create_huaian(),
        create_lushan(),
        create_gaoan(),
        create_jinling(),
        create_dengzhou(),
        create_dingzhou(),
        create_yinzhou(),
        create_huizhou(),
        create_leizhou(),
        create_lianzhou(),
        create_changzhou_route(),
        create_zhenjiang(),
        create_chuzhou(),
        create_jiangzhou(),
        create_ganzhou(),
        create_dayuling(),
        create_nankang(),
        create_pengli(),
        create_hukou(),
        create_dangtu(),
        create_changlu(),
        create_zhenzhou(),
        create_nanxiongzhou(),
        create_shaozhou(),
        create_chengmai(),
        create_wuzhou(),
        create_guangzhou(),
        create_deqing(),
        create_tengzhou(),
        create_rongzhou(),
        create_xuwen(),
        create_qiongzhou(),
        create_danzhou(),
    ]

    return {
        "version": "4.0",
        "created_at": datetime.now().isoformat(),
        "places": {p.place_id: p.to_dict() for p in places},
        "source": "李常生《苏轼行踪考》"
    }


def create_routes_dataset() -> Dict:
    """创建路线数据集"""
    routes = {
        "route01": {
            "route_id": "route01",
            "route_name": "第一次出蜀赴京",
            "start_date": "嘉祐元年（1056年）三月",
            "end_date": "嘉祐二年（1057年）四月",
            "description": "嘉祐元年三月，三苏从眉州出发，沿蜀道出蜀，经成都、阆中、剑门关、利州、凤翔、长安、渑池，五六月到汴京。嘉祐二年三月科举及第，四月奔母丧归蜀。",
            "place_ids": ["meishan", "chengdu", "langzhong", "jianmen", "lizhou",
                         "fengxiang", "changan", "mianchi", "bianjing"],
            "source": "李常生《苏轼行踪考》"
        },
        "route02": {
            "route_id": "route02",
            "route_name": "第二次出蜀与三苏《南行集》",
            "start_date": "嘉祐四年（1059年）十月",
            "end_date": "嘉祐五年（1060年）二月",
            "description": "嘉祐四年十月，三苏自眉州出发，取道长江水路出蜀。经嘉州、戎州、泸州、恭州、夔州，穿越三峡，经峡州、江陵、荆门、襄州、南阳、颍昌，嘉祐五年二月二十五日抵达汴京。途中父子三人创作《南行集》。",
            "place_ids": ["meishan", "chengdu", "langzhong", "jianmen", "lizhou", 
                         "fengxiang", "changan", "mianchi", "bianjing"],
            "source": "李常生《苏轼行踪考》"
        },
        "route03": {
            "route_id": "route03",
            "route_name": "第二次进京与凤翔签判",
            "start_date": "嘉祐六年（1061年）十一月十九日",
            "end_date": "嘉祐六年（1061年）十二月十四日",
            "description": "嘉祐六年十一月十九日，苏轼与苏辙别于郑州西门外。苏轼赴凤翔府任签书判官，经洛阳、渑池、陕州、华州、渭南、长安、扶风，十二月十四日到凤翔任。途中作《和子由渑池怀旧》。",
            "place_ids": ["bianjing", "zhengzhou", "luoyang", "mianchi", "shanzhou",
                         "huazhou", "weinan", "changan", "fufeng", "fengxiang"],
            "source": "李常生《苏轼行踪考》"
        },
        "route04": {
            "route_id": "route04",
            "route_name": "第三次入京与父丧返乡",
            "start_date": "治平元年（1064年）正月",
            "end_date": "治平四年（1067年）四月",
            "description": "治平元年正月，苏轼自凤翔入京。三月至京，寓居景德寺。治平四年(1067年)正月，英宗即位。三月护送英宗向后山陵。治平三年（1066年）四月，苏洵病逝于京，苏轼兄弟护丧归蜀。回程经大名府、泗州、龟山、洪泽、樊口、江陵、下岩、仙都山、丰都，治平四年四月回到眉山。",
            "place_ids": ["fengxiang", "changan", "huaqing", "huazhou", "bianjing",
                         "wenan", "damingfu", "sizhou", "guishan", "fankou",
                         "jiangling", "xiaoyan", "xiandushan", "fengdu", "meishan"],
            "source": "李常生《苏轼行踪考》"
        },
        "route05": {
            "route_id": "route05",
            "route_name": "第四次出蜀赴京",
            "start_date": "熙宁元年（1068年）十一二月",
            "end_date": "熙宁二年（1069年）二月初",
            "description": "熙宁元年十一月底、十二月初，苏轼为父苏洵守丧期满后，携家眷从眉山出发，第四次出蜀赴京。经过益昌(昭化)、凤翔、长安，约于熙宁二年二月初抵达汴京。居南园，除判官告院兼判尚书祠部。",
            "place_ids": ["meishan", "zhaohua", "fengxiang", "changan", "bianjing"],
            "source": "李常生《苏轼行踪考》"
        },
        "route06": {
            "route_id": "route06",
            "route_name": "任杭州倅",
            "start_date": "熙宁四年（1071年）七月上旬",
            "end_date": "熙宁四年（1071年）十一月二十八日",
            "description": "熙宁四年七月上旬，苏轼离京赴陈州，拜访张方平、会见苏辙。后顺颍河南下至颍州，拜望退隐的欧阳修。再顺颍河、淮河、运河南下，途经寿州、扬州、润州、常州、苏州，十一月二十八日抵达杭州任通判。",
            "place_ids": ["bianjing", "chengzhou", "yingzhou", "shouzhou", "yangzhou",
                         "runzhou", "suzhou", "hangzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route07": {
            "route_id": "route07",
            "route_name": "知密州",
            "start_date": "熙宁七年（1074年）九月下旬",
            "end_date": "熙宁九年（1076年）十二月",
            "description": "熙宁七年九月下旬，苏轼离开杭州北行知密州。途经润州、高邮、海州，十一月三日到密州任。在密州期间创作《水调歌头》《江城子·密州出猎》等名篇。熙宁九年十二月离去。",
            "place_ids": ["hangzhou", "runzhou", "gaoyou", "haizhou", "mizhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route08": {
            "route_id": "route08",
            "route_name": "知徐州",
            "start_date": "熙宁九年（1076年）十二月",
            "end_date": "元丰二年（1079年）二三月",
            "description": "熙宁九年十二月，苏轼罢密州，北上经郓州改知徐州。熙宁十年四月二十一日到徐州任。期间率民抗黄河洪水，建黄楼。创作《永遇乐》《放鹤亭记》等。元丰二年二三月，罢徐州知湖州。",
            "place_ids": ["mizhou", "yizhou", "yuncheng", "xuzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route09": {
            "route_id": "route09",
            "route_name": "知湖与乌台诗案",
            "start_date": "元丰二年（1079年）二三月",
            "end_date": "元丰二年（1079年）十二月",
            "description": "元丰二年二三月，苏轼罢徐州知湖州，南下经楚州、润州等到湖州。七月因乌台诗案被捕，押解至汴京。",
            "place_ids": ["xuzhou", "huaian", "zhenjiang", "huzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route10": {
            "route_id": "route10",
            "route_name": "贬谪黄州",
            "start_date": "元丰三年（1080年）正月",
            "end_date": "元丰七年（1084年）四月",
            "description": "元丰二年十二月，苏轼因乌台诗案被贬黄州团练副使。元丰三年正月出狱，二月至黄州。在黄州四年多，躬耕东坡，自号东坡居士，创作《念奴娇·赤壁怀古》、前后《赤壁赋》等千古名篇。",
            "place_ids": ["bianjing", "guangzhou_henan", "macheng", "huangzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route11": {
            "route_id": "route11",
            "route_name": "量移汝州与庐山之游",
            "start_date": "元丰七年（1084年）四月",
            "end_date": "元丰七年（1084年）十二月",
            "description": "元丰七年四月，苏轼量移汝州团练副使。离开黄州，经金陵访王安石，经高安访好友，游庐山。后至汝州。",
            "place_ids": ["huangzhou", "jinling", "gaoan", "lushan"],
            "source": "李常生《苏轼行踪考》"
        },
        "route12": {
            "route_id": "route12",
            "route_name": "万里来去知登州",
            "start_date": "元丰八年（1085年）六月",
            "end_date": "元丰八年（1085年）十一月",
            "description": "元丰八年六月，苏轼在南都接诰命起知登州。北上循运河经海州、密州、莱州至登州。十月十五日至登州，五日后即以礼部郎中召还。",
            "place_ids": ["nandu", "haizhou", "mizhou", "laizhou", "dengzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route13": {
            "route_id": "route13",
            "route_name": "第六次入京",
            "start_date": "元丰八年（1085年）十二月",
            "end_date": "元祐四年（1089年）四月",
            "description": "元丰八年十二月，苏轼自登州返京，任职约四年。元祐四年四月，出京赴杭州任知州。",
            "place_ids": ["bianjing"],
            "source": "李常生《苏轼行踪考》"
        },
        "route14": {
            "route_id": "route14",
            "route_name": "再知杭州",
            "start_date": "元祐四年（1089年）四月",
            "end_date": "元祐六年（1091年）",
            "description": "元祐四年四月，苏轼自汴京赴杭州任知州。疏浚西湖，修筑苏堤。",
            "place_ids": ["bianjing", "hangzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route15": {
            "route_id": "route15",
            "route_name": "知颍州与知扬州",
            "start_date": "元祐六年（1091年）",
            "end_date": "元祐七年（1092年）",
            "description": "元祐六年，苏轼自杭州移知颍州，途经高邮。元祐七年，自颍州移知扬州。",
            "place_ids": ["hangzhou", "gaoyou", "yingzhou", "yangzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route16": {
            "route_id": "route16",
            "route_name": "第七次进京",
            "start_date": "元祐七年（1092年）",
            "end_date": "元祐八年（1093年）",
            "description": "元祐七年，苏轼自扬州进京任兵部尚书、礼部尚书等职。",
            "place_ids": ["yangzhou", "chuzhou", "bianjing"],
            "source": "李常生《苏轼行踪考》"
        },
        "route17": {
            "route_id": "route17",
            "route_name": "贬谪惠州",
            "start_date": "绍圣元年（1094年）四月",
            "end_date": "绍圣四年（1097年）四月",
            "description": "绍圣元年四月，苏轼落职知英州，后贬惠州安置。从定州出发，经淮安、扬州、真州、金陵、当涂、湖口、江州、彭蠡、南康、赣州、大庾岭、南雄、韶州、英德、广州，十月二日到惠州贬所。在惠州两年多。",
            "place_ids": ["dingzhou", "huaian", "yangzhou", "zhenzhou", "changlu", 
                          "jinling", "dangtu", "hukou", "jiangzhou", "pengli", 
                          "nankang", "ganzhou", "dayuling", "nanxiongzhou", 
                          "shaozhou", "yinzhou", "guangzhou", "huizhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route18": {
            "route_id": "route18",
            "route_name": "贬谪儋州",
            "start_date": "绍圣四年（1097年）四月",
            "end_date": "元符三年（1100年）六月",
            "description": "绍圣四年四月，苏轼再贬儋州别驾，昌化军安置。从惠州出发，经广州、梧州、藤州、容州、雷州，渡海至琼州，到儋州。在儋州三年，讲学授徒。",
            "place_ids": ["huizhou", "guangzhou", "wuzhou", "tengzhou", "rongzhou", 
                          "leizhou", "xuwen", "qiongzhou", "danzhou"],
            "source": "李常生《苏轼行踪考》"
        },
        "route19": {
            "route_id": "route19",
            "route_name": "北归常州",
            "start_date": "元符三年（1100年）六月",
            "end_date": "建中靖国元年（1101年）七月",
            "description": "元符三年，苏轼遇赦北归。离儋州，经澄迈、琼州、雷州、廉州、容州、藤州、梧州、广州、英州、赣州、金陵，至常州。建中靖国元年七月卒于常州。",
            "place_ids": ["danzhou", "chengmai", "qiongzhou", "leizhou", "lianzhou", 
                          "rongzhou", "tengzhou", "wuzhou", "guangzhou", 
                          "yinzhou", "ganzhou", "jinling", "changzhou"],
            "source": "李常生《苏轼行踪考》"
        },
    }

    return {
        "version": "4.0",
        "created_at": datetime.now().isoformat(),
        "routes": routes,
        "source": "李常生《苏轼行踪考》"
    }


def main():
    """主函数"""
    # 创建地点数据
    places_data = create_places_dataset()
    places_file = Path("/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data/places-detailed-v3.json")
    with open(places_file, "w", encoding="utf-8") as f:
        json.dump(places_data, f, ensure_ascii=False, indent=2)

    # 创建路线数据
    routes_data = create_routes_dataset()
    routes_file = Path("/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data/routes-v3.json")
    with open(routes_file, "w", encoding="utf-8") as f:
        json.dump(routes_data, f, ensure_ascii=False, indent=2)

    print("✅ V4数据已生成!")
    print(f"   - 地点数据: {places_file}")
    print(f"   - 路线数据: {routes_file}")
    print(f"   - 地点数量: {len(places_data['places'])} 个")
    print(f"   - 路线数量: {len(routes_data['routes'])} 条")
    print()
    print("地点列表:")
    for pid, pdata in places_data['places'].items():
        routes = list(pdata['route_order'].keys())
        print(f"   - {pid}: {pdata['name_song']} (路线: {routes})")


if __name__ == "__main__":
    main()
