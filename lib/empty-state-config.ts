/**
 * 空状态文案配置系统
 * 
 * 原则：
 * - 第一人称视角，像苏轼自己在说话
 * - 不用「暂无数据」「内容整理中」这类冷冰冰的系统语言
 * - 每条带一句真实诗文或化用，有出处感
 * - 结尾留悬念或引导动作
 */

export interface EmptyStateConfig {
  title: string; // 标题行（一句话，苏轼视角，10字内）
  body: string[]; // 正文（1-3行，解释原因，语气轻盈不沮丧）
  quote?: string; // 引用（可选，真实诗句，斜体金色）
  source?: string; // 出处（可选）
  action?: {
    text: string; // 行动引导文字
    href?: string; // 跳转链接
    onClick?: string; // 点击事件名称
  };
}

/**
 * 事迹 Tab 空状态
 */
export const STORY_EMPTY: EmptyStateConfig = {
  title: '此处山河，我曾路过',
  body: [
    '脚步太快，笔墨未及落下。',
    '这一段的故事，还在寻访之中。',
  ],
  quote: '人生到处知何似，应似飞鸿踏雪泥',
  source: '苏轼《和子由渑池怀旧》',
  action: {
    text: '史料整理中 · 欢迎提供线索',
  },
};

/**
 * 作品 Tab 空状态
 */
export const WORKS_EMPTY: EmptyStateConfig = {
  title: '我在此地，沉默过',
  body: [
    '不是每一处山水都值得落笔。',
    '有时候，只是静静地看着，',
    '把它藏在心里，不写。',
  ],
  quote: '此心安处是吾乡',
  source: '苏轼《定风波》',
};

/**
 * 作品 Tab 空状态（待录入）
 */
export const WORKS_PENDING: EmptyStateConfig = {
  title: '诗在路上，尚未抵达',
  body: [
    '三千余首，仍在一首一首整理。',
    '这里的篇章，稍后见。',
  ],
  quote: '腹有诗书气自华',
  source: '苏轼《和董传留别》',
};

/**
 * 文旅 Tab 空状态（推荐景点为空）
 */
export const TRAVEL_EMPTY: EmptyStateConfig = {
  title: '此地风物，我记得',
  body: [
    '只是文字还没追上脚步。',
    '景点信息正在逐批整理，',
    '若你已到访，倒不如你来告诉我。',
  ],
  quote: '江山如此多娇，我曾一一走过',
  source: '化用毛泽东《沁园春·雪》',
};

/**
 * 文旅 Tab 空状态（交通信息为空）
 */
export const TRAVEL_TRANSPORT_EMPTY: EmptyStateConfig = {
  title: '我当年靠的是一匹马',
  body: [
    '现在你有更好的办法。',
    '交通信息暂未录入，',
    '建议直接导航前往。',
  ],
};

/**
 * 美食 Tab 空状态（东坡特供为空）
 */
export const FOOD_SUSHI_EMPTY: EmptyStateConfig = {
  title: '此味甚好，只是忘了记下',
  body: [
    '老夫平生好吃，吃过的何止万千？',
    '此处风味，待你替我尝尝看。',
  ],
  quote: '人间至味是清欢',
  source: '苏轼《浣溪沙》',
  action: {
    text: '去「附近推荐」找找看 →',
    onClick: 'switchToNearby',
  },
};

/**
 * 美食 Tab 空状态（附近推荐加载中）
 */
export const FOOD_NEARBY_LOADING: EmptyStateConfig = {
  title: '正在寻访附近食肆……',
  body: [],
};

/**
 * 美食 Tab 空状态（附近推荐为空）
 */
export const FOOD_NEARBY_EMPTY: EmptyStateConfig = {
  title: '此地人迹罕至，连高德也沉默了',
  body: [
    '或许这正是它的珍贵之处。',
    '建议问问当地人，',
    '他们知道最好的那家在哪里。',
  ],
};

/**
 * 美食 Tab 空状态（全部为空）
 */
export const FOOD_ALL_EMPTY: EmptyStateConfig = {
  title: '美食这件事，我从不将就',
  body: [
    '但此处记录尚缺，',
    '无论东坡特供还是附近推荐，',
    '都还在路上。',
    '',
    '稍后再来，或者——',
    '你先去别处看看？',
  ],
};

/**
 * 收藏诗词为空
 */
export const COLLECTION_EMPTY: EmptyStateConfig = {
  title: '你还没有收藏任何诗词',
  body: [
    '三千余首，总有一首是为你写的。',
    '去找找看。',
  ],
  quote: '腹有诗书气自华',
  source: '苏轼《和董传留别》',
  action: {
    text: '→ 去诗词页',
    href: '/poems',
  },
};

/**
 * 打卡记录为空
 */
export const CHECKIN_EMPTY: EmptyStateConfig = {
  title: '你还没有踏上这段旅程',
  body: [
    '一千年前，苏轼从眉山出发。',
    '你从哪里开始？',
  ],
  action: {
    text: '→ 打开地图，找到第一个地点',
    href: '/explore',
  },
};

/**
 * 成就墙全未解锁
 */
export const ACHIEVEMENT_EMPTY: EmptyStateConfig = {
  title: '六枚徽章，等你来取',
  body: [
    '东坡走了六十四年，你才刚刚开始。',
    '不急。',
  ],
};

/**
 * 笔记为空
 */
export const NOTE_EMPTY: EmptyStateConfig = {
  title: '你还没有留下任何文字',
  body: [
    '苏轼说：「书到用时方恨少。」',
    '我说：读过之后，不妨写两句。',
  ],
  action: {
    text: '→ 去诗词页，读完添笔记',
    href: '/poems',
  },
};

/**
 * 搜索结果为空
 */
export const SEARCH_EMPTY: EmptyStateConfig = {
  title: '没有找到',
  body: [
    '也许换个说法？',
    '苏轼的世界很大，',
    '但有些角落还没被整理进来。',
  ],
};

/**
 * 路线页内容为空
 */
export const ROUTE_EMPTY: EmptyStateConfig = {
  title: '二十条路线，正在铺开',
  body: [
    '每条路线都是一段独立故事，',
    '正在逐条整理史料与地点。',
    '地图上的足迹已在，',
    '路线叙事稍后见。',
  ],
};

/**
 * 空状态组件渲染函数
 */
export function renderEmptyState(config: EmptyStateConfig): {
  title: string;
  bodyLines: string[];
  quote?: string;
  source?: string;
  actionText?: string;
  actionHref?: string;
  actionOnClick?: string;
} {
  return {
    title: config.title,
    bodyLines: config.body.filter(line => line !== ''),
    quote: config.quote,
    source: config.source,
    actionText: config.action?.text,
    actionHref: config.action?.href,
    actionOnClick: config.action?.onClick,
  };
}