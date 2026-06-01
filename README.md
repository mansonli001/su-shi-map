# 读苏轼·游神州 v4.1

苏轼一生交互式数字地图（19 路线 / 水墨风格）。

## 功能特性

- 🗺️ **高德地图集成** - GCJ-02 坐标，水墨自定义样式
- 📍 **苏轼一生地点** - 分级标记（出生/任职/贬谪/游览/友人/长眠）
- 🛣️ **19 条路线** - 从一生总览到单条路线切换
- 📱 **半屏交互卡片** - Framer Motion 手势拖拽，三档 snap
- 📄 **SSG 详情页** - 每地点静态生成，事迹+诗词+景点+美食
- 🔍 **模糊搜索** - fuse.js 本地搜索地点/诗词
- 🎬 **轨迹动画** - 按时间顺序连线播放苏轼一生行迹
- ✅ **匿名打卡** - IndexedDB 本地存储

> v4.1 暂未启用 Service Worker / PWA（next-pwa 保持 disable），等核心体验稳定后再开启。

## 技术栈

- **框架**: Next.js 14 (App Router, TypeScript)
- **样式**: Tailwind CSS + @tailwindcss/typography + shadcn/ui
- **地图**: 高德 JSAPI 2.0 (@amap/amap-jsapi-loader)
- **状态管理**: Zustand
- **动画**: Framer Motion
- **搜索**: fuse.js
- **OG 图片**: @vercel/og
- **部署**: Vercel + Cloudflare

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/mansonli001/su-shi-map.git
cd su-shi-map
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env.local` 并填写：

```bash
cp .env.example .env.local
```

必须配置：
- `NEXT_PUBLIC_AMAP_KEY` - 高德地图 JS API Key
- `AMAP_SECURITY_JS_CODE` - 高德 securityJsCode（保密）

### 4. 准备数据

将120个地点数据放入 `data/` 目录：

- `data/places-core.json` - 地点核心数据（id/lat/lng/type/stage/importance）
- `data/places-index.json` - 地点索引（搜索用）
- `data/places/*.json` - 地点详情（120个）

示例数据格式见 `data/README.md`。

### 5. 运行开发服务器

```bash
npm run dev
```

打开 http://localhost:3000 查看。

## 数据来源

- **苏轼生平数据**: 基于《苏轼年谱》、《苏轼全集校注》
- **诗词数据**: [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) (CC0)
- **历史地理数据**: CHGIS（哈佛大学+复旦大学）
- **地图服务**: 高德地图 JSAPI 2.0

## 脚本命令

```bash
# 开发
npm run dev

# 构建
npm run build

# 启动生产服务器
npm run start

# 校验数据
npm run validate

# 转换坐标（WGS84 → GCJ-02）
npm run convert -- input.geojson output.geojson

# 提取苏轼诗词
npm run poems
```

## 部署

### Vercel 部署

```bash
vercel deploy
```

### Cloudflare DNS 配置

1. 在 Cloudflare 添加域名
2. 设置 CNAME 记录指向 `cname.vercel-dns.com`
3. 开启 CDN 缓存

## 项目结构

详见 [目录结构](#) （待补充链接）

## 开源协议

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**Loading in Progress...** 🌸
# Last deploy: 2026-06-01 22:59:05
