/**
 * data-v4 Phase 1 / Step 5
 * ----------------------------------------------------------
 * 组装最终交付物：
 *   ① data-v4/places-index.json     —— 234 节点全量索引（前端首屏拉取）
 *   ② data-v4/routes-index.json     —— 20 路线轻量索引
 *   ③ data-v4/routes/R00-R19.json   —— 20 条路线详情骨架
 *
 * P 编号分配规则：按古名 zh-Hans-CN 排序，从 P001 顺次分配
 * 路线编号已固定 R00-R19
 * ----------------------------------------------------------
 */

import * as fs from "fs";
import * as path from "path";

// ======================================================
// 类型
// ======================================================
type Layer = "main" | "sight" | "around";
type CoordSource =
  | "core_curated"
  | "inferred"
  | "approximate"
  | "chgis_pending"
  | "amap"
  | "amap_corrected"
  | "chgis";

interface CoordedNode {
  ancient_name: string;
  modern_name: string;
  routes: { route_id: string; layer: Layer; order_in_route: number }[];
  occurrences: number;
  lng: number;
  lat: number;
  coordinate_source: CoordSource;
  trustworthy: boolean;
  match_strategy: string;
  matched_key?: string;
  inferred_type?: string;
}

interface ParsedRoute {
  route_id: string;
  route_index: number;
  route_title_raw: string;
  main: string[][];
  sight: string[];
  around: string[];
}

const projectRoot = path.resolve(__dirname, "..", "..");

// ======================================================
// 路线元数据（从订正版 V1 抽取的固定属性）
// ======================================================
const ROUTE_META: Record<
  string,
  {
    name: string;
    period: string;
    start_year: number;
    end_year: number;
    description_short: string;
    description_long: string;
    color: string;
    color_dim: string;
  }
> = {
  R00: { name: "眉山故里·少年成长", period: "1037–1056", start_year: 1037, end_year: 1056,
    description_short: "未出蜀的二十年，眉山-青神-成都之间游学。",
    description_long: "苏轼出生于眉山，二十岁前在故里度过少年成长期。父亲苏洵游学，母亲程夫人启蒙；与弟苏辙同就学于青神中岩寺。期间随父短赴成都，拜谒益州知州张方平，张氏以国士相待，奠定一生人脉。",
    color: "#8B4513", color_dim: "#C8B294" },
  R01: { name: "首次进京赶考·母丧返蜀", period: "1056–1057", start_year: 1056, end_year: 1057,
    description_short: "父子三人首次出蜀进京，应礼部考试一鸣惊人；母程氏卒于眉山，原路返蜀守孝。",
    description_long: "嘉祐元年三月，苏洵携苏轼苏辙首次出蜀进京。穿越蜀道、过潼关、抵汴京，应礼部试苏轼以《刑赏忠厚之至论》得欧阳修激赏。次年闻母丧，仓皇返蜀守制三年。",
    color: "#C41E24", color_dim: "#E0A09F" },
  R02: { name: "三苏父子·岷江长江出蜀南行", period: "1059", start_year: 1059, end_year: 1060,
    description_short: "守制毕，父子三人沿岷江入长江，三峡水路第二次出蜀。",
    description_long: "嘉祐四年十月，苏洵守制毕，再携二子顺岷江、犍为、戎州、入长江、过三峡、出夔门，至江陵。途中所作诗合编为《南行集》，是苏轼早期诗歌的重要标志。",
    color: "#4A6670", color_dim: "#A6BDC4" },
  R03: { name: "二次进京·赴凤翔签判", period: "1060–1064", start_year: 1060, end_year: 1064,
    description_short: "由荆州陆行赴汴京，授官凤翔府签判，初入仕途。",
    description_long: "庚子年由江陵北上，经襄阳、邓州、汴京，再西行至长安、凤翔。任凤翔签判三年，与太守陈希亮共事；游访东湖、太白山、五丈原，写下《喜雨亭记》《凌虚台记》等名篇。",
    color: "#8B6914", color_dim: "#D5C6A3" },
  R04: { name: "三次进京·父丧扶柩归蜀", period: "1065–1068", start_year: 1065, end_year: 1068,
    description_short: "凤翔任满还朝判官诰院；父苏洵卒于汴京，扶柩水路归葬眉山。",
    description_long: "凤翔三年任满归京，授殿中丞判登闻鼓院。次年父亲苏洵病逝京师，苏轼苏辙扶柩沿汴河、淮河、长江、三峡水路归葬眉山。途经扬州瓜州渡，第一次见识江南繁华。",
    color: "#7B9E89", color_dim: "#C8D5CC" },
  R05: { name: "四次进京·重返朝堂卷入党争", period: "1069", start_year: 1069, end_year: 1069,
    description_short: "守父丧毕，再赴汴京任职，正值王安石变法，旋陷党争。",
    description_long: "熙宁二年由眉山经成都、剑门、汉中、长安、洛阳进京。任直史馆兼判官告院。因反对新法激进派被王安石派系攻击，主动请外。",
    color: "#A0826D", color_dim: "#D8C8BC" },
  R06: { name: "外放杭州通判·南下江南", period: "1071–1074", start_year: 1071, end_year: 1074,
    description_short: "请外得杭州通判，沿运河南下，初识西湖。",
    description_long: "由汴京经陈州、颍州、寿州、滁州、扬州、镇江、苏州抵杭。任通判三年，遍游西湖、灵隐、孤山、凤凰山，写下《饮湖上初晴后雨》等大量西湖诗篇，奠定与杭州的一生缘分。",
    color: "#5B7A8C", color_dim: "#B8C5CC" },
  R07: { name: "自杭州调任密州知州", period: "1074–1076", start_year: 1074, end_year: 1076,
    description_short: "杭州任满改知密州，跨越江浙鲁三省北上。",
    description_long: "熙宁七年由杭州出发，经湖州、苏州、无锡、扬州、楚州、海州抵山东密州。在密州两年，于超然台北望抒怀，写下《江城子·乙卯正月二十日夜记梦》《水调歌头·明月几时有》等千古名作。",
    color: "#9C5F30", color_dim: "#D8C0AC" },
  R08: { name: "自密州调任徐州知州", period: "1077–1078", start_year: 1077, end_year: 1078,
    description_short: "密州任满改知徐州，黄河决口任内组织抗洪。",
    description_long: "由密州经沂州、海州、楚州、泗州抵徐州。任职期间正逢黄河决口，苏轼亲临前线督修城防百日不归家，事后筑黄楼记功，写下《放鹤亭记》《百步洪》等名篇。",
    color: "#6B8E5A", color_dim: "#C2CCB8" },
  R09: { name: "自湖州上任·乌台诗案押解进京", period: "1078–1079", start_year: 1078, end_year: 1079,
    description_short: "徐州移知湖州，到任三月即被御史李定等罗织罪名，押京下狱百三十日。",
    description_long: "元丰二年三月由徐州赴湖州，七月即被御史台缇骑逮捕，沿运河押解进京下御史台狱。这是北宋第一起著名的文字狱，史称\"乌台诗案\"。出狱后贬黄州团练副使。",
    color: "#B8485E", color_dim: "#E4B5BE" },
  R10: { name: "贬谪黄州·安置闲居", period: "1080–1084", start_year: 1080, end_year: 1084,
    description_short: "由汴京沿淮河南岸古道抵黄州团练副使任，开荒东坡，自号东坡居士。",
    description_long: "元丰三年二月抵黄州。最初寓居定惠院，后迁临皋亭。两年后开垦城东坡地，筑雪堂，自号\"东坡居士\"。期间游赤壁三次，作前后《赤壁赋》《念奴娇·赤壁怀古》，文学生涯达至高峰。",
    color: "#3F5C6E", color_dim: "#A8B8C2" },
  R11: { name: "黄州量移·漫游庐山筠州金陵常州", period: "1084", start_year: 1084, end_year: 1085,
    description_short: "量移汝州团练副使途中辗转游历庐山金陵，请居常州得允。",
    description_long: "元丰七年三月奉命量移汝州，先东行经九江登庐山，访石钟山，至筠州探视弟苏辙，再赴金陵谒王安石；最终上书请居常州，神宗允之。",
    color: "#A88539", color_dim: "#D8C490" },
  R12: { name: "自宜兴赴任登州·五日太守", period: "1085", start_year: 1085, end_year: 1085,
    description_short: "神宗崩、哲宗立，起复登州知州，自宜兴北上，到任仅五日复召还朝。",
    description_long: "元丰八年神宗崩，哲宗立，起复苏轼为登州知州。沿苏北沿海北上，经楚州、海州、密州抵登州蓬莱，到任五日即被召还朝任礼部郎中。",
    color: "#7C9885", color_dim: "#C8D2C8" },
  R13: { name: "登州还朝·第六次进京·元祐入阁", period: "1085–1086", start_year: 1085, end_year: 1086,
    description_short: "由登州经齐鲁古道还朝，元祐元年入阁任翰林学士知制诰。",
    description_long: "由登州经莱州、青州、淄州、济南、郓州、曹州一线还朝。元祐元年任翰林学士知制诰，掌内制；与司马光主导废除王安石新法，是仕途最高峰。",
    color: "#925E4A", color_dim: "#D4BFB2" },
  R14: { name: "再知杭州·疏浚西湖筑苏堤", period: "1089–1091", start_year: 1089, end_year: 1091,
    description_short: "请外再知杭州，疏浚西湖筑长堤，杭人立祠以祀。",
    description_long: "元祐四年请外得杭州知州。任内组织疏浚西湖，筑\"苏堤\"，立\"三潭印月\"，疏浚六井，赈灾防疫。今西湖苏堤春晓即由此而来，杭人立\"苏文忠公祠\"祀之。",
    color: "#4D7178", color_dim: "#B0C0C2" },
  R15: { name: "杭州罢任·第七次短暂回京", period: "1091", start_year: 1091, end_year: 1091,
    description_short: "杭州任满还朝任翰林学士承旨。",
    description_long: "元祐六年由杭州沿江南运河北上，经苏州、常州、扬州、楚州、泗州抵汴京，任翰林学士承旨。在京数月即出。",
    color: "#9E6B3F", color_dim: "#D6C0A4" },
  R16: { name: "出京知颍州·再迁扬州", period: "1091–1093", start_year: 1091, end_year: 1093,
    description_short: "出知颍州，半年后改知扬州，江淮辗转。",
    description_long: "元祐六年八月由汴京经陈州、颍州、洪泽湖、楚州、扬州。知颍州时疏浚颍州西湖；知扬州时减赋税、撤万花会，深得民心。",
    color: "#7A8C5B", color_dim: "#C2C8B2" },
  R17: { name: "第八次进京·外放河北定州", period: "1093–1094", start_year: 1093, end_year: 1094,
    description_short: "高太后崩，新党再起，苏轼外放定州抵御契丹。",
    description_long: "元祐八年高太后崩，哲宗亲政重用新党。苏轼由扬州还朝旋出知定州。沿黄河北上经相州、磁州、邢州、真定抵定州。任内整顿边防、训练士兵、巡阅边关，但仅半年即遭再贬。",
    color: "#B85F4A", color_dim: "#E4BCB0" },
  R18: { name: "南迁远贬·定州→惠州→儋州", period: "1094–1100", start_year: 1094, end_year: 1100,
    description_short: "新党执政清算元祐党人，苏轼一贬再贬至岭南、海南。",
    description_long: "绍圣元年贬英州、惠州，三年再贬儋州。由定州南下，过大庾岭至惠州合江楼、白鹤峰；再渡琼州海峡至儋州中和镇，建桄榔庵、办载酒堂、教化生徒，这是苏轼一生最艰难的六年。",
    color: "#5E7A8C", color_dim: "#B8C8D0" },
  R19: { name: "遇赦北归·儋州终老常州", period: "1100–1101", start_year: 1100, end_year: 1101,
    description_short: "徽宗赦还，自儋州北归常州孙氏馆，旋卒。",
    description_long: "元符三年徽宗即位大赦元祐党人。苏轼自儋州渡海北归，沿岭南西江、赣江、长江一路东行，途中遍访旧友。建中靖国元年七月二十八日卒于常州，葬郏县小峨眉山。",
    color: "#8C5A3F", color_dim: "#D0BFAD" },
};

// ======================================================
// 主流程
// ======================================================
function main() {
  // 读取上游产物
  const coorded: { _meta: unknown; nodes: CoordedNode[] } = JSON.parse(
    fs.readFileSync(path.join(projectRoot, "data-v4", "meta", "places-with-coords.json"), "utf-8")
  );
  const routesRaw: { _meta: unknown; routes: ParsedRoute[] } = JSON.parse(
    fs.readFileSync(path.join(projectRoot, "data-v4", "meta", "routes-parsed-raw.json"), "utf-8")
  );

  const nodes = coorded.nodes;

  // ① 分配 P 编号
  const idMap = new Map<string, string>(); // ancient_name → "P001"
  nodes.forEach((n, i) => {
    const id = `P${String(i + 1).padStart(3, "0")}`;
    idMap.set(n.ancient_name, id);
  });

  // ② 推断主类型
  function inferType(n: CoordedNode): string {
    if (n.inferred_type) return n.inferred_type;
    const layers = new Set(n.routes.map((r) => r.layer));
    if (layers.has("main")) return "main";
    if (layers.has("sight")) return "sight";
    return "around";
  }

  // ③ 生成 places-index.json
  const places = nodes.map((n) => {
    const id = idMap.get(n.ancient_name)!;
    const type = inferType(n);
    const layers = new Set(n.routes.map((r) => r.layer));
    const primaryLayer: "main" | "sight" | "around" | "special" = layers.has("main")
      ? "main"
      : layers.has("sight")
      ? "sight"
      : layers.has("around")
      ? "around"
      : "special";

    const importance: 1 | 2 | 3 = n.routes.length >= 4 ? 1 : n.routes.length >= 2 ? 2 : 3;
    const tags: string[] = [];
    if (n.coordinate_source === "approximate") tags.push("坐标待考");
    if (n.coordinate_source === "inferred") tags.push("坐标推断");
    if (importance === 1) tags.push("核心节点");
    if (n.routes.length >= 4) tags.push(`跨${new Set(n.routes.map(r => r.route_id)).size}路线`);

    return {
      id,
      ancient_name: n.ancient_name,
      modern_name: n.modern_name || "",
      type,
      layer: primaryLayer,
      lat: n.lat,
      lng: n.lng,
      coordinate_source: n.coordinate_source,
      trustworthy: n.trustworthy,
      importance,
      tags,
      summary: "", // Phase 2 详情迁移时回填
      related_routes: Array.from(new Set(n.routes.map((r) => r.route_id))).sort(),
      route_layers: n.routes.map((r) => ({
        route_id: r.route_id,
        layer: r.layer,
        order: r.order_in_route,
      })),
      occurrences: n.occurrences,
      has_detail: false, // Phase 2 起 true
      verified: n.coordinate_source === "core_curated",
      legacy: {} as { ss_id?: string; pinyin_id?: string },
    };
  });

  const placesIndex = {
    _meta: {
      schema_version: "v4.0",
      data_source: "网络公开资料整理",
      disclaimer:
        "本项目所用苏轼路线、地点、诗词等数据，整理自互联网公开资料，仅供个人学习与文化爱好者交流之用，不作为学术引用依据。坐标与路线为示意性还原，如有错漏欢迎指正。",
      version: "v4.0.0-phase1",
      generated_at: new Date().toISOString(),
      total_places: places.length,
      coordinate_source_dist: places.reduce<Record<string, number>>((a, p) => {
        a[p.coordinate_source] = (a[p.coordinate_source] || 0) + 1;
        return a;
      }, {}),
      type_dist: places.reduce<Record<string, number>>((a, p) => {
        a[p.type] = (a[p.type] || 0) + 1;
        return a;
      }, {}),
    },
    places,
  };

  fs.writeFileSync(
    path.join(projectRoot, "data-v4", "places-index.json"),
    JSON.stringify(placesIndex, null, 2),
    "utf-8"
  );
  console.log(`[write] data-v4/places-index.json (${places.length} 节点)`);

  // ④ 生成 routes/R*.json
  const routesDir = path.join(projectRoot, "data-v4", "routes");
  fs.mkdirSync(routesDir, { recursive: true });

  const routesIndex: any[] = [];

  for (const r of routesRaw.routes) {
    const meta = ROUTE_META[r.route_id];
    if (!meta) {
      console.warn(`  ⚠️  ${r.route_id} 缺少 ROUTE_META 元数据，跳过`);
      continue;
    }

    // 主线 segments
    const segments = r.main.map((chain, i) => {
      const place_ids = chain
        .map((token) => {
          const ancient = token.replace(/[（(].*$/, "").trim();
          return idMap.get(ancient) || null;
        })
        .filter(Boolean) as string[];
      return {
        segment_id: `${r.route_id}-S${String(i + 1).padStart(2, "0")}`,
        label: r.main.length > 1 ? `第${i + 1}段` : "全程",
        place_ids,
        transport_mode: "mixed" as const, // Phase 2 标注
      };
    });

    const sightIds = r.sight
      .map((t) => idMap.get(t.replace(/[（(].*$/, "").trim()) || null)
      .filter(Boolean) as string[];
    const aroundIds = r.around
      .map((t) => idMap.get(t.replace(/[（(].*$/, "").trim()) || null)
      .filter(Boolean) as string[];

    const allIds = Array.from(
      new Set([...segments.flatMap((s) => s.place_ids), ...sightIds, ...aroundIds])
    );

    const routeDetail = {
      id: r.route_id,
      index: r.route_index,
      name: meta.name,
      title_raw: r.route_title_raw,
      period: meta.period,
      start_year: meta.start_year,
      end_year: meta.end_year,
      unique_color: meta.color,
      unique_color_dim: meta.color_dim,
      description_short: meta.description_short,
      description_long: meta.description_long,
      track_segments: segments,
      sight_place_ids: sightIds,
      around_place_ids: aroundIds,
      related_place_ids: allIds,
      source: ["网络公开资料整理", "李常生《苏轼行踪考》订正"],
      schema_version: "v4.0",
    };

    fs.writeFileSync(
      path.join(routesDir, `${r.route_id}.json`),
      JSON.stringify(routeDetail, null, 2),
      "utf-8"
    );

    routesIndex.push({
      id: r.route_id,
      index: r.route_index,
      name: meta.name,
      period: meta.period,
      start_year: meta.start_year,
      end_year: meta.end_year,
      unique_color: meta.color,
      description_short: meta.description_short,
      place_count: allIds.length,
      main_count: segments.reduce((s, x) => s + x.place_ids.length, 0),
      sight_count: sightIds.length,
      around_count: aroundIds.length,
    });
  }

  fs.writeFileSync(
    path.join(projectRoot, "data-v4", "routes-index.json"),
    JSON.stringify(
      {
        _meta: {
          schema_version: "v4.0",
          version: "v4.0.0-phase1",
          generated_at: new Date().toISOString(),
          total_routes: routesIndex.length,
        },
        routes: routesIndex,
      },
      null,
      2
    ),
    "utf-8"
  );
  console.log(`[write] data-v4/routes-index.json (${routesIndex.length} 路线)`);
  console.log(`[write] data-v4/routes/R00.json ~ R${String(routesIndex.length - 1).padStart(2, "0")}.json`);

  // ⑤ 总结
  console.log(`\n=== Phase 1 完成 ===`);
  console.log(`  节点：${places.length}`);
  console.log(`  路线：${routesIndex.length}`);
  console.log(`  坐标分布：`, placesIndex._meta.coordinate_source_dist);
  console.log(`  类型分布：`, placesIndex._meta.type_dist);
  console.log(`\n下一步：Phase 2 详情迁移 + CHGIS 政区底图`);
}

main();
