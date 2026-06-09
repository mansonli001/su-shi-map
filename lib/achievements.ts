/**
 * 成就系统核心模块 v3.0
 * 25枚成就，五大板块分类
 * v3: 新增 ACHIEVEMENT_IMAGES 映射 + getAchievementStatus 函数
 */

import { PlaceCore } from '@/types';

export interface Achievement {
  id: string;
  name: string;
  emoji: string;
  icon: string;      // 图标文件名（不含扩展名）
  color: string;     // 主色
  glow: string;      // rgba 光晕
  desc: string;      // 解锁描述
  poem: string;      // 诗词金句
  poemSrc: string;   // 出处
  category: 'grow' | 'banish' | 'jiangnan' | 'poem' | 'secret'; // 分类
  tier: 'bronze' | 'silver' | 'gold'; // 品级
  minPlaces?: number;
  requiredPlaces?: string[]; // 特殊成就需要打卡的地点ID列表
  isHidden?: boolean; // 是否为隐藏成就
  isSynthesis?: boolean; // 是否为合成成就
  synthesisFrom?: string[]; // 合成来源的成就ID
}

/**
 * 25枚成就定义
 */
export const achievements: Achievement[] = [
  // ===== 成长阶梯（11枚）=====
  // 青铜5枚
  {
    id: 'grow-001',
    name: '初踏苏途',
    emoji: '初',
    icon: '初踏苏途',
    color: '#929292',
    glow: 'rgba(146, 146, 146, 0.4)',
    desc: '累计打卡3处东坡足迹点位',
    poem: '人生到处知何似，应似飞鸿踏雪泥',
    poemSrc: '《和子由渑池怀旧》',
    category: 'grow',
    tier: 'bronze',
    minPlaces: 3,
  },
  {
    id: 'grow-002',
    name: '眉山故人',
    emoji: '山',
    icon: '眉山故人',
    color: '#929292',
    glow: 'rgba(146, 146, 146, 0.4)',
    desc: '完整打卡眉山全出生地/故居/求学点位',
    poem: '门前流水尚能西，休将白发唱黄鸡',
    poemSrc: '《浣溪沙》',
    category: 'grow',
    tier: 'bronze',
    minPlaces: 5,
  },
  {
    id: 'grow-003',
    name: '宦途起步',
    emoji: '凤',
    icon: '宦途起步',
    color: '#929292',
    glow: 'rgba(146, 146, 146, 0.4)',
    desc: '凤翔全部为官旧址完整打卡',
    poem: '凤翔千山万木秋，使君行处即风流',
    poemSrc: '《凤翔八观》',
    category: 'grow',
    tier: 'bronze',
    minPlaces: 4,
  },
  {
    id: 'grow-004',
    name: '行路起步',
    emoji: '路',
    icon: '行路起步',
    color: '#929292',
    glow: 'rgba(146, 146, 146, 0.4)',
    desc: '在3个不同省级行政区完成点位打卡',
    poem: '竹杖芒鞋轻胜马，谁怕？一蓑烟雨任平生',
    poemSrc: '《定风波》',
    category: 'grow',
    tier: 'bronze',
    minPlaces: 3,
  },
  {
    id: 'grow-005',
    name: '一城漫游',
    emoji: '城',
    icon: '一城漫游',
    color: '#929292',
    glow: 'rgba(146, 146, 146, 0.4)',
    desc: '单个城市内累计打卡5个点位',
    poem: '不识庐山真面目，只缘身在此山中',
    poemSrc: '《题西林壁》',
    category: 'grow',
    tier: 'bronze',
    minPlaces: 5,
  },
  // 白银4枚
  {
    id: 'grow-006',
    name: '宦游四方',
    emoji: '游',
    icon: '宦游四方',
    color: '#C4C4C4',
    glow: 'rgba(196, 196, 196, 0.4)',
    desc: '总打卡20点位、覆盖5个省份',
    poem: '江山如画，一时多少豪杰',
    poemSrc: '《念奴娇·赤壁怀古》',
    category: 'grow',
    tier: 'silver',
    minPlaces: 20,
  },
  {
    id: 'grow-007',
    name: '半生起落',
    emoji: '月',
    icon: '半生起落',
    color: '#C4C4C4',
    glow: 'rgba(196, 196, 196, 0.4)',
    desc: '总打卡50点位，打卡记录包含汴京点位',
    poem: '人有悲欢离合，月有阴晴圆缺',
    poemSrc: '《水调歌头》',
    category: 'grow',
    tier: 'silver',
    minPlaces: 50,
  },
  {
    id: 'grow-008',
    name: '七日同游',
    emoji: '日',
    icon: '七日同游',
    color: '#C4C4C4',
    glow: 'rgba(196, 196, 196, 0.4)',
    desc: '连续7天任意点位打卡',
    poem: '一日看尽长安花',
    poemSrc: '《登科后》',
    category: 'grow',
    tier: 'silver',
    minPlaces: 7,
  },
  {
    id: 'grow-009',
    name: '月月同游',
    emoji: '月',
    icon: '月月同游',
    color: '#C4C4C4',
    glow: 'rgba(196, 196, 196, 0.4)',
    desc: '连续30天任意点位打卡',
    poem: '三十功名尘与土，八千里路云和月',
    poemSrc: '《满江红》',
    category: 'grow',
    tier: 'silver',
    minPlaces: 30,
  },
  // 鎏金2枚
  {
    id: 'grow-010',
    name: '半生行遍',
    emoji: '卷',
    icon: '半生行遍',
    color: '#C9973A',
    glow: 'rgba(201, 151, 58, 0.4)',
    desc: '累计打卡80个全地图点位',
    poem: '大江东去，浪淘尽，千古风流人物',
    poemSrc: '《念奴娇·赤壁怀古》',
    category: 'grow',
    tier: 'gold',
    minPlaces: 80,
  },
  {
    id: 'grow-011',
    name: '集大成者',
    emoji: '鼎',
    icon: '鎏金终极',
    color: '#C9973A',
    glow: 'rgba(201, 151, 58, 0.4)',
    desc: '120个全量足迹全部打卡完毕',
    poem: '会挽雕弓如满月，西北望，射天狼',
    poemSrc: '《江城子·密州出猎》',
    category: 'grow',
    tier: 'gold',
    minPlaces: 120,
  },

  // ===== 贬谪专题（4枚）=====
  {
    id: 'banish-001',
    name: '黄州客居',
    emoji: '壁',
    icon: '黄州客居',
    color: '#C82333',
    glow: 'rgba(200, 35, 51, 0.4)',
    desc: '黄州全片区点位打卡',
    poem: '大江东去，浪淘尽，千古风流人物',
    poemSrc: '《念奴娇·赤壁怀古》',
    category: 'banish',
    tier: 'bronze',
  },
  {
    id: 'banish-002',
    name: '岭南逐客',
    emoji: '荔',
    icon: '岭南逐客',
    color: '#C82333',
    glow: 'rgba(200, 35, 51, 0.4)',
    desc: '惠州全片区点位打卡',
    poem: '日啖荔枝三百颗，不辞长作岭南人',
    poemSrc: '《惠州一绝》',
    category: 'banish',
    tier: 'bronze',
  },
  {
    id: 'banish-003',
    name: '天涯儋州',
    emoji: '海',
    icon: '天涯儋州',
    color: '#C82333',
    glow: 'rgba(200, 35, 51, 0.4)',
    desc: '海南儋州全点位打卡',
    poem: '九死南荒吾不恨，兹游奇绝冠平生',
    poemSrc: '《六月二十日夜渡海》',
    category: 'banish',
    tier: 'bronze',
  },
  {
    id: 'banish-004',
    name: '贬谪三地行者',
    emoji: '行',
    icon: '', // 合成成就，暂空，使用emoji显示
    color: '#C82333',
    glow: 'rgba(200, 35, 51, 0.4)',
    desc: '集齐黄州、惠州、儋州全部成就自动解锁',
    poem: '此心安处是吾乡',
    poemSrc: '《定风波》',
    category: 'banish',
    tier: 'gold',
    isSynthesis: true,
    synthesisFrom: ['banish-001', 'banish-002', 'banish-003'],
  },

  // ===== 江南专题（2枚）=====
  {
    id: 'jiangnan-001',
    name: '西湖闲客',
    emoji: '湖',
    icon: '西湖闲客',
    color: '#5B8C6E',
    glow: 'rgba(91, 140, 110, 0.4)',
    desc: '杭州西湖全系列点位打卡',
    poem: '欲把西湖比西子，淡妆浓抹总相宜',
    poemSrc: '《饮湖上初晴后雨》',
    category: 'jiangnan',
    tier: 'bronze',
  },
  {
    id: 'jiangnan-002',
    name: '江南行舟',
    emoji: '舟',
    icon: '江南行舟',
    color: '#5B8C6E',
    glow: 'rgba(91, 140, 110, 0.4)',
    desc: '杭州+湖州+扬州三地全点位打卡',
    poem: '春水碧于天，画船听雨眠',
    poemSrc: '《菩萨蛮》',
    category: 'jiangnan',
    tier: 'silver',
  },

  // ===== 诗词珍藏（5枚）=====
  {
    id: 'poem-001',
    name: '美食墨客',
    emoji: '碗',
    icon: '美食墨客',
    color: '#929292',
    glow: 'rgba(146, 146, 146, 0.4)',
    desc: '打卡东坡美食关联点位+收藏对应美食诗词',
    poem: '东坡肉香飘万里，人间至味是清欢',
    poemSrc: '《猪肉颂》',
    category: 'poem',
    tier: 'bronze',
    minPlaces: 8,
  },
  {
    id: 'poem-002',
    name: '中秋望月',
    emoji: '月',
    icon: '中秋望月',
    color: '#C4C4C4',
    glow: 'rgba(196, 196, 196, 0.4)',
    desc: '收藏《水调歌头·明月几时有》+任意2首中秋题材诗词',
    poem: '但愿人长久，千里共婵娟',
    poemSrc: '《水调歌头》',
    category: 'poem',
    tier: 'silver',
    minPlaces: 3,
  },
  {
    id: 'poem-003',
    name: '赤壁诗魂',
    emoji: '石',
    icon: '赤壁诗魂',
    color: '#C9973A',
    glow: 'rgba(201, 151, 58, 0.4)',
    desc: '收藏《前后赤壁赋》+《念奴娇·赤壁怀古》三首名篇',
    poem: '大江东去，浪淘尽，千古风流人物',
    poemSrc: '《念奴娇·赤壁怀古》',
    category: 'poem',
    tier: 'gold',
    minPlaces: 3,
  },
  {
    id: 'poem-004',
    name: '风雨定风波',
    emoji: '竹',
    icon: '风雨定风波',
    color: '#C9973A',
    glow: 'rgba(201, 151, 58, 0.4)',
    desc: '收藏≥5首《定风波》系列词作',
    poem: '一蓑烟雨任平生',
    poemSrc: '《定风波》',
    category: 'poem',
    tier: 'gold',
    minPlaces: 5,
  },
  {
    id: 'poem-005',
    name: '千首拾珍',
    emoji: '书',
    icon: '千首拾珍',
    color: '#C9973A',
    glow: 'rgba(201, 151, 58, 0.4)',
    desc: '累计收藏100首苏轼全品类诗词',
    poem: '腹有诗书气自华',
    poemSrc: '《和董传留别》',
    category: 'poem',
    tier: 'gold',
    minPlaces: 100,
  },

  // ===== 隐秘彩蛋（3枚）=====
  {
    id: 'secret-001',
    name: '雨夜读苏',
    emoji: '灯',
    icon: '雨夜读苏',
    color: '#6B4A8C',
    glow: 'rgba(107, 74, 140, 0.4)',
    desc: '当日20:00~24:00区间任意地点打卡',
    poem: '夜阑风静縠纹平',
    poemSrc: '《临江仙》',
    category: 'secret',
    tier: 'bronze',
    isHidden: true,
    minPlaces: 1,
  },
  {
    id: 'secret-002',
    name: '生辰同游',
    emoji: '桃',
    icon: '生辰同游',
    color: '#6B4A8C',
    glow: 'rgba(107, 74, 140, 0.4)',
    desc: '用户注册生日当天，任意点位打卡',
    poem: '人生得意须尽欢，莫使金樽空对月',
    poemSrc: '《将进酒》',
    category: 'secret',
    tier: 'bronze',
    isHidden: true,
    minPlaces: 1,
  },
  {
    id: 'secret-003',
    name: '节气同游',
    emoji: '雪',
    icon: '节气同游',
    color: '#6B4A8C',
    glow: 'rgba(107, 74, 140, 0.4)',
    desc: '二十四节气任意一个节气自然日完成打卡',
    poem: '雪沫乳花浮午盏，蓼茸蒿笋试春盘',
    poemSrc: '《浣溪沙》',
    category: 'secret',
    tier: 'bronze',
    isHidden: true,
    minPlaces: 1,
  },
];

/**
 * 二十四节气日期（公历）
 */
export const solarTerms: Record<string, { month: number; day: number }> = {
  '立春': { month: 2, day: 4 },
  '雨水': { month: 2, day: 19 },
  '惊蛰': { month: 3, day: 6 },
  '春分': { month: 3, day: 21 },
  '清明': { month: 4, day: 5 },
  '谷雨': { month: 4, day: 20 },
  '立夏': { month: 5, day: 6 },
  '小满': { month: 5, day: 21 },
  '芒种': { month: 6, day: 6 },
  '夏至': { month: 6, day: 21 },
  '小暑': { month: 7, day: 7 },
  '大暑': { month: 7, day: 23 },
  '立秋': { month: 8, day: 8 },
  '处暑': { month: 8, day: 23 },
  '白露': { month: 9, day: 8 },
  '秋分': { month: 9, day: 23 },
  '寒露': { month: 10, day: 8 },
  '霜降': { month: 10, day: 23 },
  '立冬': { month: 11, day: 7 },
  '小雪': { month: 11, day: 22 },
  '大雪': { month: 12, day: 7 },
  '冬至': { month: 12, day: 22 },
  '小寒': { month: 1, day: 6 },
  '大寒': { month: 1, day: 20 },
};

/**
 * 中国省级行政区前缀列表（用于 modernName 匹配）
 */
const PROVINCE_PREFIXES = [
  '四川','陕西','河南','江苏','浙江','湖北','湖南','江西','安徽',
  '山东','河北','广东','海南','福建','甘肃','北京','天津','上海',
  '重庆','广西','云南','贵州','辽宁','山西','宁夏','西藏','内蒙古','新疆','青海','吉林','黑龙江',
];

/**
 * 从 modernName 提取省份前缀
 */
function extractProvince(modernName: string): string {
  for (const prov of PROVINCE_PREFIXES) {
    if (modernName.startsWith(prov)) return prov;
  }
  return '';
}

/**
 * 从 modernName 提取城市名（省份后2-3字）
 */
function extractCity(modernName: string): string {
  const prov = extractProvince(modernName);
  if (!prov) return modernName;
  const rest = modernName.slice(prov.length);
  // 取前2-3字作为城市名
  return rest.slice(0, Math.min(3, rest.length));
}

/**
 * 解析特殊成就所需的地点ID列表
 * v2: 基于 modernName 精确匹配省份/城市
 */
export function resolveSpecialPlaces(allPlaces: PlaceCore[]): {
  meishan: string[];    // 眉山相关
  fengxiang: string[];  // 凤翔相关
  huangzhou: string[];  // 黄州相关
  huizhou: string[];    // 惠州相关
  danzhou: string[];    // 儋州/海南相关
  jiangnan: string[];   // 杭州/西湖/江南系列
  bianjing: string[];   // 汴京/开封
  banish: string[];     // 黄州+惠州+儋州 合集
} {
  const result = {
    meishan: [] as string[],
    fengxiang: [] as string[],
    huangzhou: [] as string[],
    huizhou: [] as string[],
    danzhou: [] as string[],
    jiangnan: [] as string[],
    bianjing: [] as string[],
    banish: [] as string[],
  };

  for (const place of allPlaces) {
    const name = place.songName || '';
    const modernName = place.modernName || '';

    // 眉山
    if (modernName.includes('眉山') || name.includes('眉山')) {
      result.meishan.push(place.id);
    }
    // 凤翔
    if (modernName.includes('凤翔') || name.includes('凤翔')) {
      result.fengxiang.push(place.id);
    }
    // 黄州
    if (modernName.includes('黄州') || name.includes('黄州')) {
      result.huangzhou.push(place.id);
      result.banish.push(place.id);
    }
    // 惠州
    if (modernName.includes('惠州') || name.includes('惠州')) {
      result.huizhou.push(place.id);
      result.banish.push(place.id);
    }
    // 儋州/海南
    if (modernName.includes('儋州') || name.includes('儋州') ||
        modernName.includes('海南') || name.includes('海南')) {
      result.danzhou.push(place.id);
      result.banish.push(place.id);
    }
    // 杭州/西湖/江南
    if (modernName.includes('杭州') || name.includes('杭州') ||
        modernName.includes('西湖') || name.includes('西湖') ||
        modernName.includes('苏堤') || name.includes('苏堤') ||
        modernName.includes('湖州') || name.includes('湖州') ||
        modernName.includes('扬州') || name.includes('扬州')) {
      result.jiangnan.push(place.id);
    }
    // 汴京/开封
    if (modernName.includes('开封') || name.includes('汴京') || name.includes('汴梁')) {
      result.bianjing.push(place.id);
    }
  }

  return result;
}

/**
 * 检查是否为节气日
 */
export function isSolarTermDay(date: Date): boolean {
  const month = date.getMonth() + 1;
  const day = date.getDate();

  for (const term of Object.values(solarTerms)) {
    if (term.month === month && term.day === day) {
      return true;
    }
  }

  return false;
}

/**
 * 检查是否为雨夜（20:00-24:00）
 */
export function isRainyNight(date: Date): boolean {
  const hour = date.getHours();
  return hour >= 20 && hour < 24;
}

/**
 * 评估成就解锁状态 v2
 * 修复：省份覆盖、城市多点、特定地点成就的精确判断
 */
export function evaluateAchievements(
  checkedIds: Set<string>,
  allPlaces: PlaceCore[],
  favoritePoemIds: Set<string> = new Set(),
  checkinDates: Date[] = [],
): {
  unlocked: string[];
  progress: Record<string, { current: number; target: number }>;
} {
  const unlocked: string[] = [];
  const progress: Record<string, { current: number; target: number }> = {};

  const specialPlaces = resolveSpecialPlaces(allPlaces);
  const totalChecked = checkedIds.size;

  // 计算覆盖的省份数
  const checkedProvinces = new Set<string>();
  // 计算同城市打卡数
  const cityCheckinCount: Record<string, number> = {};

  for (const place of allPlaces) {
    if (!checkedIds.has(place.id)) continue;
    const prov = extractProvince(place.modernName || '');
    if (prov) checkedProvinces.add(prov);

    const city = extractCity(place.modernName || '');
    if (city) cityCheckinCount[city] = (cityCheckinCount[city] || 0) + 1;
  }

  const provinceCount = checkedProvinces.size;
  const maxCityCheckins = Math.max(0, ...Object.values(cityCheckinCount));

  // 计算连续打卡天数
  const consecutiveDays = calculateConsecutiveDays(checkinDates);

  // 检查是否包含汴京点位
  const hasBianjing = specialPlaces.bianjing.some(id => checkedIds.has(id));

  for (const ach of achievements) {
    let current = 0;
    let target = 1;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    let isUnlocked = false;

    // 隐藏成就：未解锁时返回模糊状态
    if (ach.isHidden && !unlocked.includes(ach.id)) {
      progress[ach.id] = { current: 0, target: 1 };
      continue;
    }

    // 合成成就：检查子成就是否全部解锁
    if (ach.isSynthesis && ach.synthesisFrom) {
      const allChildrenUnlocked = ach.synthesisFrom.every(childId => unlocked.includes(childId));
      if (allChildrenUnlocked) {
        isUnlocked = true;
        unlocked.push(ach.id);
      }
      progress[ach.id] = { current: allChildrenUnlocked ? 1 : 0, target: 1 };
      continue;
    }

    switch (ach.id) {
      // ===== 成长阶梯 =====
      case 'grow-001': // 初踏苏途：累计打卡 >= 3
        current = totalChecked;
        target = 3;
        if (totalChecked >= 3) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-002': // 眉山故人：眉山全点位打卡
        current = specialPlaces.meishan.filter(id => checkedIds.has(id)).length;
        target = Math.max(specialPlaces.meishan.length, 1);
        if (current >= target) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-003': // 宦途起步：凤翔全点位打卡
        current = specialPlaces.fengxiang.filter(id => checkedIds.has(id)).length;
        target = Math.max(specialPlaces.fengxiang.length, 1);
        if (current >= target) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-004': // 行路起步：覆盖 >= 3 个不同省份
        current = provinceCount;
        target = 3;
        if (provinceCount >= 3) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-005': // 一城漫游：同一城市内打卡 >= 5 个点位
        current = maxCityCheckins;
        target = 5;
        if (maxCityCheckins >= 5) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-006': // 宦游四方：打卡 >= 20 且覆盖 >= 5 省
        current = provinceCount; // 以省份数为进度
        target = 5;
        if (totalChecked >= 20 && provinceCount >= 5) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-007': // 半生起落：打卡 >= 50 且包含汴京
        current = totalChecked;
        target = 50;
        if (totalChecked >= 50 && hasBianjing) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-008': // 七日同游：连续7天打卡
        current = consecutiveDays;
        target = 7;
        if (consecutiveDays >= 7) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-009': // 月月同游：连续30天打卡
        current = consecutiveDays;
        target = 30;
        if (consecutiveDays >= 30) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-010': // 半生行遍：累计打卡 >= 80
        current = totalChecked;
        target = 80;
        if (totalChecked >= 80) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'grow-011': // 集大成者：累计打卡 >= 120
        current = totalChecked;
        target = 120;
        if (totalChecked >= 120) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      // ===== 贬谪专题 =====
      case 'banish-001': // 黄州客居
        current = specialPlaces.huangzhou.filter(id => checkedIds.has(id)).length;
        target = Math.max(specialPlaces.huangzhou.length, 1);
        if (current >= target) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'banish-002': // 岭南逐客
        current = specialPlaces.huizhou.filter(id => checkedIds.has(id)).length;
        target = Math.max(specialPlaces.huizhou.length, 1);
        if (current >= target) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'banish-003': // 天涯儋州
        current = specialPlaces.danzhou.filter(id => checkedIds.has(id)).length;
        target = Math.max(specialPlaces.danzhou.length, 1);
        if (current >= target) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      // ===== 江南专题 =====
      case 'jiangnan-001': // 西湖闲客：杭州西湖全系列
        current = specialPlaces.jiangnan.filter(id => checkedIds.has(id)).length;
        target = Math.max(specialPlaces.jiangnan.length, 1);
        if (current >= target) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'jiangnan-002': // 江南行舟：杭州+湖州+扬州
        current = specialPlaces.jiangnan.filter(id => checkedIds.has(id)).length;
        target = Math.max(specialPlaces.jiangnan.length, 1);
        if (current >= target) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      // ===== 诗词珍藏 =====
      case 'poem-001': // 美食墨客
        current = favoritePoemIds.size;
        target = 8;
        if (favoritePoemIds.size >= 8) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'poem-002': // 中秋望月
        current = favoritePoemIds.size;
        target = 3;
        if (favoritePoemIds.size >= 3) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'poem-003': // 赤壁诗魂
        current = favoritePoemIds.size;
        target = 3;
        if (favoritePoemIds.size >= 3) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'poem-004': // 风雨定风波
        current = favoritePoemIds.size;
        target = 5;
        if (favoritePoemIds.size >= 5) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      case 'poem-005': // 千首拾珍
        current = favoritePoemIds.size;
        target = 100;
        if (favoritePoemIds.size >= 100) { isUnlocked = true; unlocked.push(ach.id); }
        break;

      // ===== 隐秘彩蛋 =====
      case 'secret-001': // 雨夜读苏
        {
          const hasRainyNight = checkinDates.some(d => isRainyNight(d));
          current = hasRainyNight ? 1 : 0;
          target = 1;
          if (hasRainyNight) { isUnlocked = true; unlocked.push(ach.id); }
        }
        break;

      case 'secret-002': // 生辰同游（暂不实现）
        current = 0;
        target = 1;
        break;

      case 'secret-003': // 节气同游
        {
          const hasSolarTerm = checkinDates.some(d => isSolarTermDay(d));
          current = hasSolarTerm ? 1 : 0;
          target = 1;
          if (hasSolarTerm) { isUnlocked = true; unlocked.push(ach.id); }
        }
        break;

      default:
        // 兜底：minPlaces 数量型
        if (ach.minPlaces) {
          current = totalChecked;
          target = ach.minPlaces;
          if (totalChecked >= ach.minPlaces) { isUnlocked = true; unlocked.push(ach.id); }
        }
        break;
    }

    progress[ach.id] = { current, target };
  }

  return { unlocked, progress };
}

/**
 * 计算连续打卡天数
 */
function calculateConsecutiveDays(dates: Date[]): number {
  if (dates.length === 0) return 0;

  const sortedDates = [...dates].sort((a, b) => b.getTime() - a.getTime());
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let consecutive = 0;
  let currentDate = today;

  for (const date of sortedDates) {
    const checkDate = new Date(date);
    checkDate.setHours(0, 0, 0, 0);

    const diffDays = Math.floor((currentDate.getTime() - checkDate.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0 || diffDays === 1) {
      consecutive++;
      currentDate = checkDate;
    } else {
      break;
    }
  }

  return consecutive;
}

/**
 * 获取单个成就详情
 */
export function getAchievement(id: string): Achievement | undefined {
  return achievements.find(a => a.id === id);
}

/**
 * 获取成就进度百分比
 */
export function getAchievementProgress(
  id: string,
  checkedIds: Set<string>,
  allPlaces: PlaceCore[],
): number {
  const { progress } = evaluateAchievements(checkedIds, allPlaces);
  const p = progress[id];
  if (!p || p.target === 0) return 0;
  return Math.min((p.current / p.target) * 100, 100);
}

/**
 * 成就图片路径映射表
 * 文件名对应 public/achievements/ 目录下的 JPG 文件
 */
export const ACHIEVEMENT_IMAGES: Record<string, string> = {
  '初踏苏途': '/achievements/初踏苏途.jpg',
  '眉山故人': '/achievements/眉山故人.jpg',
  '宦途起步': '/achievements/宦途起步.jpg',
  '行路起步': '/achievements/行路起步.jpg',
  '一城漫游': '/achievements/一城漫游.jpg',
  '宦游四方': '/achievements/宦游四方.jpg',
  '半生起落': '/achievements/半生起落.jpg',
  '七日同游': '/achievements/七日同游.jpg',
  '月月同游': '/achievements/月月同游.jpg',
  '半生行遍': '/achievements/半生行遍.jpg',
  '鎏金终极': '/achievements/鎏金终极.jpg',
  '黄州客居': '/achievements/黄州客居.jpg',
  '岭南逐客': '/achievements/岭南逐客.jpg',
  '天涯儋州': '/achievements/天涯儋州.jpg',
  '西湖闲客': '/achievements/西湖闲客.jpg',
  '江南行舟': '/achievements/江南行舟.jpg',
  '美食墨客': '/achievements/美食墨客.jpg',
  '中秋望月': '/achievements/中秋望月.jpg',
  '赤壁诗魂': '/achievements/赤壁诗魂.jpg',
  '风雨定风波': '/achievements/风雨定风波.jpg',
  '千首拾珍': '/achievements/千首拾珍.jpg',
  '雨夜读苏': '/achievements/雨夜读苏.jpg',
  '生辰同游': '/achievements/生辰同游.jpg',
  '节气同游': '/achievements/节气同游.jpg',
};

/**
 * 成就卡片状态类型
 */
export type AchievementStatus = 'unlocked' | 'near' | 'inprogress' | 'locked';

/**
 * 根据进度计算成就状态
 * progress = 已完成条件数 / 总条件数
 * progress === 1     → unlocked
 * progress >= 0.8    → near
 * progress > 0       → inprogress
 * progress === 0     → locked
 */
export function getAchievementStatus(current: number, target: number): AchievementStatus {
  if (target === 0) return 'locked';
  const progress = current / target;
  if (progress >= 1) return 'unlocked';
  if (progress >= 0.8) return 'near';
  if (progress > 0) return 'inprogress';
  return 'locked';
}