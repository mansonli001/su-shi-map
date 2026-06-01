/**
 * 苏轼行踪路线 · 19条独立路线配置 + 路线构建函数
 * + 1条一生总览
 *
 * 说明：路线基于史料考据，按苏轼生平 journey 拆分
 */

export interface Route19Config {
  id: string;
  name: string;
  time: string;
  mainColor: string;
  desc: string;
  startPlace: string;  // 起点（宋代地名）
  endPlace: string;    // 终点（宋代地名）
  distance?: number;    // 估算里程（km）
}

/**
 * 路线轨迹点（从 places 动态构建）
 */
export interface Route19TrackPoint {
  id: string;      // 地点ID (SSxxx)
  name: string;    // 宋代地名
  lat: number;
  lng: number;
  order: number;     // 在该路线中的顺序
  routeId: string;
  tag: string;       // 标签：故里/途经/任职/被捕/贬谪/病逝...
}

/**
 * 路线配置容器（v4.1: 改为可变，运行时由 v4-adapter 注入）
 *
 * 注意：默认值仍保留旧 v3 写死配置作为 SSR/构建期兜底，
 * 客户端首屏拉到 v4 数据后调用 installRouteConfigs() 进行替换。
 */
export const ROUTE19_CONFIG_DEFAULT: Record<string, Route19Config> = {
  // ── 第1条：第一次出蜀赴京（1056）────────────────────
  route01: {
    id: 'route01',
    name: '第一次出蜀赴京',
    time: '1056',
    mainColor: '#8B4513',
    desc: '嘉祐元年（1056），21岁苏轼与父苏洵、弟苏辙离眉山，沿剑门古道向北翻越秦岭，经凤翔、长安、洛阳，千里跋涉赴汴京应试。一举进士及第，名动京师。',
    startPlace: '眉山',
    endPlace: '汴京',
    distance: 1500,
  },

  // ── 第2条：母丧返乡守制（1057-1059）────────────────
  route02: {
    id: 'route02',
    name: '母丧返乡守制',
    time: '1057-1059',
    mainColor: '#2F4F4F',
    desc: '进士及第后母程夫人病逝，苏轼、苏辙兄弟随父急归眉山守制。丁忧三年（实际约26个月），在故里眉山度过平静的读书时光。',
    startPlace: '汴京',
    endPlace: '眉山',
  },

  // ── 第3条：第二次出蜀赴京（1059-1060）─────────────
  route03: {
    id: 'route03',
    name: '第二次出蜀赴京',
    time: '1059-1060',
    mainColor: '#4682B4',
    desc: '守制结束，苏轼携父、弟沿长江水路出蜀，经戎州、泸州、忠州、夔州，出三峡至江陵，再陆路北上汴京。这是苏轼最后一次经过家乡眉山。',
    startPlace: '眉山',
    endPlace: '汴京',
    distance: 1800,
  },

  // ── 第4条：赴凤翔任职签判（1061-1064）──────────
  route04: {
    id: 'route04',
    name: '赴凤翔任职',
    time: '1061-1064',
    mainColor: '#B8860B',
    desc: '嘉祐六年（1061）苏轼赴凤翔府任签书判官。凤翔是苏轼第一个任职地，期间写下大量诗作，开始形成自己的文学风格。与知府宋选合作良好。',
    startPlace: '汴京',
    endPlace: '凤翔',
  },

  // ── 第5条：凤翔返京·父丧返乡（1065-1068）───────
  // 合并：凤翔任满返京 + 父丧返乡守制
  route05: {
    id: 'route05',
    name: '凤翔返京·父丧返乡',
    time: '1065-1068',
    mainColor: '#CD853F',
    desc: '凤翔签判任满，苏轼返回汴京。归途刚至汴京，发妻王弗病逝，年仅27岁。治平三年（1066）父苏洵病逝，苏轼兄弟护柩归蜀守制。这是苏轼人生中最后一次回到故乡眉山。',
    startPlace: '凤翔',
    endPlace: '眉山',
  },

  // ── 第6条：第三次进京任职（1069）─────────────────
  route06: {
    id: 'route06',
    name: '第三次进京任职',
    time: '1069',
    mainColor: '#6B8E23',
    desc: '守制结束，苏轼兄弟重返汴京。此时王安石变法开始，苏轼因政见不合，主动请求外放，为日后地方官生涯埋下伏笔。',
    startPlace: '眉山',
    endPlace: '汴京',
  },

  // ── 第7条：赴杭州任通判（1071-1074）─────────────
  route07: {
    id: 'route07',
    name: '赴杭州任通判',
    time: '1071-1074',
    mainColor: '#2E8B57',
    desc: '因反对王安石新法，苏轼自请外放，通判杭州。在杭州三年，留下大量吟咏西湖的诗作，"欲把西湖比西子"即成于此期。与诗僧参寥子结交。',
    startPlace: '汴京',
    endPlace: '杭州',
  },

  // ── 第8条：移知密州（1074-1076）─────────────────
  route08: {
    id: 'route08',
    name: '移知密州',
    time: '1074-1076',
    mainColor: '#556B2F',
    desc: '杭州通判任满，改知密州（今山东诸城）。在密州写下《水调歌头·明月几时有》等名篇。蝗灾旱灾接连，苏轼全力救灾，深受百姓爱戴。',
    startPlace: '杭州',
    endPlace: '密州',
  },

  // ── 第9条：移知徐州（1077-1079）─────────────────
  route09: {
    id: 'route09',
    name: '移知徐州',
    time: '1077-1079',
    mainColor: '#8FBC8F',
    desc: '知密州满，移知徐州。在徐州遭遇特大洪水，苏轼亲率军民抗洪，保一城百姓平安。在徐州结识醉道士等奇人，写下《放鹤亭记》。',
    startPlace: '密州',
    endPlace: '徐州',
  },

  // ── 第10条：赴湖州与乌台诗案（1079）──────────────
  route10: {
    id: 'route10',
    name: '乌台诗案·湖州被捕',
    time: '1079',
    mainColor: '#B22222',
    desc: '知徐州满，移知湖州。到任仅三个月，御史台据其诗作弹劾，苏轼在湖州被捕，押解回京受审。这就是著名的"乌台诗案"，苏轼几死，最终贬黄州。',
    startPlace: '徐州',
    endPlace: '黄州',
  },

  // ── 第11条：贬谪黄州（1080-1084）────────────────
  route11: {
    id: 'route11',
    name: '贬谪黄州',
    time: '1080-1084',
    mainColor: '#4682B4',
    desc: '乌台诗案结案，苏轼贬检校水部员外郎黄州团练副使。从汴京出发，经陈州、光州，押赴黄州。在黄州四年，自号"东坡居士"，写下前后《赤壁赋》等巅峰之作。',
    startPlace: '汴京',
    endPlace: '黄州',
  },

  // ── 第12条：量移汝州途中（1084-1085）─────────────
  route12: {
    id: 'route12',
    name: '量移汝州途中',
    time: '1084-1085',
    mainColor: '#DAA520',
    desc: '元丰七年（1084），苏轼量移汝州团练副使。离开黄州北上，途中游庐山、访好友于高安、至金陵见王安石，最终抵常州买田定居。这是苏轼人生中最自由的一段旅程。',
    startPlace: '黄州',
    endPlace: '常州',
  },

  // ── 第13条：赴登州任职（1085）───────────────────
  route13: {
    id: 'route13',
    name: '赴登州任职',
    time: '1085',
    mainColor: '#1E90FF',
    desc: '元丰八年（1085）神宗崩，哲宗立，高太后听政，旧党复起。苏轼被起用为登州知州。在登州仅五日即被召回京城，留下《登州海市》等诗。',
    startPlace: '常州',
    endPlace: '登州',
  },

  // ── 第14条：再知杭州（1089-1091）─────────────────
  route14: {
    id: 'route14',
    name: '再知杭州',
    time: '1089-1091',
    mainColor: '#228B22',
    desc: '元祐四年（1089）苏轼以龙图阁学士知杭州。这是他第二次在杭州任职，主持疏浚西湖、修筑苏堤，深得百姓爱戴。离杭时百姓沿路相送。',
    startPlace: '汴京',
    endPlace: '杭州',
  },

  // ── 第15条：移知颍州（1091-1092）────────────────
  route15: {
    id: 'route15',
    name: '移知颍州',
    time: '1091-1092',
    mainColor: '#3CB371',
    desc: '知杭州不满两年，被召还朝。途中改知颍州（今安徽阜阳）。在颍州疏浚沟渠，兴修水利。欧阳修曾守颍州，苏轼在此追怀恩师。',
    startPlace: '杭州',
    endPlace: '颍州',
  },

  // ── 第16条：移知扬州（1092）─────────────────────
  route16: {
    id: 'route16',
    name: '移知扬州',
    time: '1092',
    mainColor: '#DAA520',
    desc: '知颍州仅半年，移知扬州。在扬州废除苛捐杂税，减免债务，百姓欢腾。在扬州仅半年即被召回京师，任礼部侍郎。',
    startPlace: '颍州',
    endPlace: '扬州',
  },

  // ── 第17条：移知定州（1093-1094）────────────────
  route17: {
    id: 'route17',
    name: '移知定州',
    time: '1093-1094',
    mainColor: '#CD853F',
    desc: '元祐八年（1093）高太后崩，哲宗亲政，新党复起。苏轼被逐出朝，以端明殿学士知定州（今河北定州）。在定州整顿军纪，修缮营房。这是苏轼最后一个北方任职地。',
    startPlace: '汴京',
    endPlace: '定州',
  },

  // ── 第18条：贬谪惠州（1094-1097）────────────────
  route18: {
    id: 'route18',
    name: '贬谪惠州',
    time: '1094-1097',
    mainColor: '#FF8C00',
    desc: '绍圣元年（1094）新党再度执政，苏轼被贬宁远军节度副使惠州安置。从定州出发，经赣州、越大庾岭，抵达惠州。在惠州三年，修桥铺路，与当地百姓和睦相处。',
    startPlace: '定州',
    endPlace: '惠州',
    distance: 2400,
  },

  // ── 第19条：贬谪儋州·北归常州（1097-1101）────────
  // 合并：贬谪儋州 + 北归常州
  route19: {
    id: 'route19',
    name: '贬谪儋州·北归常州',
    time: '1097-1101',
    mainColor: '#8B008B',
    desc: '绍圣四年（1097）章惇等人继续迫害，苏轼再贬琼州别驾昌化军安置，即在海南儋州。从惠州出发，经广州、渡琼州海峡至儋州。在海南三年，讲学授徒。元符三年（1100）赦还，经雷州、广州、赣州、南昌、金陵等地，历时一年，最终抵常州。建中靖国元年（1101）七月二十八日，在常州孙氏馆病逝，享年66岁。',
    startPlace: '惠州',
    endPlace: '常州',
    distance: 5000,
  },

  // ── 总览 ────────────────────────────────────────────
  overview: {
    id: 'overview',
    name: '一生总览',
    time: '1037-1101',
    mainColor: '#8B6914',
    desc: '苏轼一生行迹总览，涵盖所有19条路线。从眉山出发，遍历大半个中国，足迹遍及十余省，行程约五万里。',
    startPlace: '眉山',
    endPlace: '常州',
    distance: 50000,
  },
};

/**
 * 所有路线ID（v4.1: 改为可变 let，运行时由 v4-adapter 注入）
 */
const ROUTE19_IDS_DEFAULT = [
  'route01', 'route02', 'route03', 'route04', 'route05',
  'route06', 'route07', 'route08', 'route09', 'route10',
  'route11', 'route12', 'route13', 'route14', 'route15',
  'route16', 'route17', 'route18', 'route19',
  'overview',
] as const;

export type Route19Id = string;

// 可变全局容器（默认指向 v3 兜底）
export let ROUTE19_CONFIG: Record<string, Route19Config> = ROUTE19_CONFIG_DEFAULT;
export let ROUTE19_IDS: readonly string[] = ROUTE19_IDS_DEFAULT;
export let ROUTE19_ONLY_IDS: readonly string[] = ROUTE19_IDS_DEFAULT.filter((id) => id !== 'overview');

/**
 * 客户端 v4 加载完成后调用，把 ROUTE19_CONFIG/ROUTE19_IDS 替换为 v4 真实数据
 */
export function installRouteConfigs(
  cfgs: Record<string, Route19Config>,
  ids?: readonly string[],
): void {
  ROUTE19_CONFIG = cfgs;
  const finalIds = ids ?? Object.keys(cfgs);
  ROUTE19_IDS = [...finalIds, 'overview'] as readonly string[];
  ROUTE19_ONLY_IDS = finalIds as readonly string[];
}

/**
 * 获取某条路线的配置
 */
export function getRoute19Config(routeId: string): Route19Config | undefined {
  return ROUTE19_CONFIG[routeId];
}

// ────────────────────────────────────────────────────────
// 路线轨迹构建函数（从 places 动态构建）
// ────────────────────────────────────────────────────────

import { PlaceCore } from '@/types';

/**
 * 从120个PlaceCore动态构建19条路线轨迹点
 * 规则：按 routeId + routeOrder 排序
 */
export function buildRoutes19FromPlaces(places: PlaceCore[]): Route19TrackPoint[] {
  const points: Route19TrackPoint[] = [];

  // 遍历19条路线（不含overview）
  ROUTE19_ONLY_IDS.forEach(routeId => {
    const config = ROUTE19_CONFIG[routeId];
    if (!config) return;

    // 找出属于该路线的所有地点，按 routeOrder 排序
    const routePlaces = places
      .filter(p => p.routeId === routeId)
      .sort((a, b) => (a.routeOrder || 0) - (b.routeOrder || 0));

    routePlaces.forEach((p, idx) => {
      points.push({
        id: p.id,
        name: p.songName,
        lat: p.lat,
        lng: p.lng,
        order: p.routeOrder || idx + 1,
        routeId: routeId,
        tag: p.type === 'birth' ? '故里'
          : p.type === 'office' ? '任职'
          : p.type === 'exile' ? '贬谪'
          : p.type === 'burial' ? '终老'
          : '途经',
      });
    });
  });

  return points;
}

/**
 * 获取某条路线的轨迹点（从预构建的缓存读取）
 * 调用方应在 places 加载后调用 buildRoutes19FromPlaces() 并缓存结果
 */
let _cachedRoute19Points: Route19TrackPoint[] | null = null;

export function setRoute19PointsCache(points: Route19TrackPoint[]) {
  _cachedRoute19Points = points;
}

export function getRoute19Points(routeId: string): Route19TrackPoint[] {
  if (!_cachedRoute19Points) return [];
  return _cachedRoute19Points
    .filter(p => p.routeId === routeId)
    .sort((a, b) => a.order - b.order);
}

/**
 * 获取所有路线的轨迹点（用于总览模式）
 */
export function getAllRoute19Points(): Route19TrackPoint[] {
  return _cachedRoute19Points || [];
}

/**
 * 获取某条路线的统计信息
 */
export function getRoute19Stats(routeId: string) {
  const points = getRoute19Points(routeId);
  return {
    count: points.length,
    start: points[0]?.name || '',
    end: points[points.length - 1]?.name || '',
  };
}
