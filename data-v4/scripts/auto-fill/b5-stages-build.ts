/**
 * B5 六阶段归组构建器
 *
 * 输入：
 *   public/data-v4/routes-index.json
 *
 * 输出：
 *   public/data-v4/stages-index.json   六阶段定义
 *   public/data-v4/routes-index.json   注入 stage_id
 *
 * 决策：用户拍板六阶段（2026-06-01）
 */

import * as fs from "fs";
import * as path from "path";

type StageDef = {
  id: string;
  index: number;
  name: string;
  alias: string;
  route_ids: string[];
  start_year: number;
  end_year: number;
  duration_years: number;
  theme: string;
  color: string; // 阶段主色（设计稿"墨黑+金"基础上加阶段色）
  age_range: string;
};

const STAGES: StageDef[] = [
  {
    id: "S1",
    index: 1,
    name: "眉山·少年",
    alias: "蜀中读书",
    route_ids: ["R00"],
    start_year: 1037,
    end_year: 1056,
    duration_years: 19,
    theme: "蜀中故里、少年读书、家学渊源",
    color: "#085041", // birth 青绿
    age_range: "0-19岁",
  },
  {
    id: "S2",
    index: 2,
    name: "汴京·宦游",
    alias: "中举入仕",
    route_ids: ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09"],
    start_year: 1056,
    end_year: 1079,
    duration_years: 23,
    theme: "进京中举、外放杭密徐、乌台诗案",
    color: "#0C447C", // office 蓝
    age_range: "19-42岁",
  },
  {
    id: "S3",
    index: 3,
    name: "黄州·东坡",
    alias: "贬谪悟道",
    route_ids: ["R10", "R11"],
    start_year: 1080,
    end_year: 1085,
    duration_years: 5,
    theme: "黄州贬谪、东坡悟道、赤壁文学",
    color: "#712B13", // exile 赤红
    age_range: "43-48岁",
  },
  {
    id: "S4",
    index: 4,
    name: "元祐·还朝",
    alias: "宦海再起",
    route_ids: ["R12", "R13", "R14", "R15", "R16", "R17"],
    start_year: 1085,
    end_year: 1094,
    duration_years: 9,
    theme: "登州还朝→再知杭州→颍州扬州→外放定州",
    color: "#BA7517", // gold-m 金
    age_range: "48-57岁",
  },
  {
    id: "S5",
    index: 5,
    name: "惠儋·南贬",
    alias: "万里南迁",
    route_ids: ["R18"],
    start_year: 1094,
    end_year: 1100,
    duration_years: 6,
    theme: "定州→惠州→儋州，跨海远贬创办书院",
    color: "#7B3F2E", // 南迁赭褐
    age_range: "57-63岁",
  },
  {
    id: "S6",
    index: 6,
    name: "北归·终老",
    alias: "遇赦归常",
    route_ids: ["R19"],
    start_year: 1100,
    end_year: 1101,
    duration_years: 1,
    theme: "遇赦北归、儋州→常州、人生收官",
    color: "#8B7355", // 暮云沉金
    age_range: "63-64岁",
  },
];

// 反查 route → stage
const ROUTE_TO_STAGE = new Map<string, string>();
for (const stage of STAGES) {
  for (const rid of stage.route_ids) {
    ROUTE_TO_STAGE.set(rid, stage.id);
  }
}

const PUB = path.resolve(__dirname, "..", "..", "..", "public", "data-v4");
const INTERNAL = path.resolve(__dirname, "..", "..");

function writeBoth(rel: string, json: any) {
  const data = JSON.stringify(json, null, 2);
  fs.writeFileSync(path.join(PUB, rel), data, "utf-8");
  fs.writeFileSync(path.join(INTERNAL, rel), data, "utf-8");
}

function main() {
  // 1) 写 stages-index.json
  writeBoth("stages-index.json", {
    schema_version: "v4.1",
    generated_at: new Date().toISOString(),
    total: STAGES.length,
    stages: STAGES,
  });
  console.log(`✅ stages-index.json 写出 ${STAGES.length} 个阶段`);

  // 2) 给 routes-index 注入 stage_id
  const routesPath = path.join(PUB, "routes-index.json");
  const routesData = JSON.parse(fs.readFileSync(routesPath, "utf-8"));
  let stageInjected = 0;
  for (const r of routesData.routes || []) {
    const sid = ROUTE_TO_STAGE.get(r.id);
    if (sid) {
      r.stage_id = sid;
      stageInjected++;
    }
  }
  routesData.schema_version = "v4.1";
  writeBoth("routes-index.json", routesData);
  console.log(`✅ routes-index.json 注入 stage_id: ${stageInjected}/${routesData.routes.length}`);

  // 3) 同步给每个 route detail 注入 stage_id
  let routeDetailInjected = 0;
  for (const r of routesData.routes || []) {
    const detailPath = path.join(PUB, "routes", `${r.id}.json`);
    if (!fs.existsSync(detailPath)) continue;
    try {
      const detail = JSON.parse(fs.readFileSync(detailPath, "utf-8"));
      detail.stage_id = r.stage_id;
      const data = JSON.stringify(detail, null, 2);
      fs.writeFileSync(detailPath, data, "utf-8");
      const internalDetailPath = path.join(INTERNAL, "routes", `${r.id}.json`);
      if (fs.existsSync(internalDetailPath)) {
        fs.writeFileSync(internalDetailPath, data, "utf-8");
      }
      routeDetailInjected++;
    } catch (e: any) {
      console.warn(`  ⚠️ ${r.id} detail 写入失败: ${e?.message}`);
    }
  }
  console.log(`✅ routes/${routesData.routes.length} detail 注入 stage_id: ${routeDetailInjected}`);

  console.log("\n📊 六阶段归组：");
  for (const s of STAGES) {
    console.log(`  ${s.id} ${s.name}（${s.age_range}）${s.route_ids.join("+")}`);
  }
}

main();
