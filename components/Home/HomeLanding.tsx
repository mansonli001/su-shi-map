/**
 * 行吟山河 · 首页 Landing v3.0「Ink & Path」（2026-06-05）
 *
 * 严格对齐 references/stitch-pc/ink_path/DESIGN.md：
 *   - 主底统一暖米白 #fef8f6（不再黑底反白）
 *   - 主按钮墨黑 #000 + 米白字（不再朱砂红 / 暗金）
 *   - 卡片 1px hairline #d1c4bc/40（不再玻璃质感 + 印章金边）
 *   - 字体：Noto Serif SC 标题 / Source Sans 3 正文 / Material Symbols 图标
 *   - 朱砂红 #ba1a1a：仅时间轴关键节点（黄州/儋州）+ 印章感
 *   - 暗金 #7b5800/#fdc34d：次按钮描边 + 时间轴节点
 *   - PC 端：左侧 256px 内嵌竖排导航（仅 lg+ 显示，与 explore/profile 自身布局零冲突）
 *   - PWA：顶部无额外 header（保持简洁），底部走全站 BottomNav
 *
 * 数字（来自 v4 真实数据，文案 100% 不动）：
 *   234 个足迹 · 64 年人生 · 3000+ 首诗词 · 14 个省份
 *
 * 全部 class 命名空间：.ip-* （ink-path），样式定义在 app/ink-path.css
 */

'use client';

import Link from 'next/link';

const SIDENAV_ITEMS = [
  { href: '/', label: '首页', icon: 'home' },
  { href: '/explore', label: '水墨地图', icon: 'map' },
  { href: '/poems', label: '古诗集', icon: 'auto_stories' },
  { href: '/routes', label: '文化路径', icon: 'route' },
  { href: '/profile', label: '名士录', icon: 'person' },
];

export default function HomeLanding() {
  return (
    <div className="ip-shell ip-shell-with-sidenav">
      {/* ============ PC 左侧竖排导航（仅 lg+，移动端走 BottomNav） ============ */}
      <nav className="ip-sidenav" aria-label="主导航">
        <div className="ip-sidenav-header">
          <div className="ip-sidenav-seal" aria-hidden="true">
            {/* v9.3 真 logo（替换 material icon account_balance） */}
            <img
              src="/brand/logo.png"
              alt=""
              width={56}
              height={56}
              style={{ width: 56, height: 56, objectFit: 'contain', display: 'block' }}
            />
          </div>
          <h1 className="ip-sidenav-title">行吟山河</h1>
          <p className="ip-sidenav-en">Xingyin Shanhe</p>
        </div>

        <ul className="ip-sidenav-list">
          {SIDENAV_ITEMS.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className="ip-sidenav-link"
                aria-current={item.href === '/' ? 'page' : undefined}
              >
                <span className="material-symbols-outlined" aria-hidden="true">
                  {item.icon}
                </span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="ip-sidenav-cta">
          <Link href="/explore" className="ip-btn-primary">
            地图探索
            <span className="material-symbols-outlined" style={{ fontSize: 18 }} aria-hidden="true">
              arrow_forward
            </span>
          </Link>
        </div>
      </nav>

      {/* ============ Hero ============ */}
      <section className="ip-hero">
        <div className="ip-hero-vertical" aria-hidden="true">
          行吟山河
        </div>

        <div className="ip-hero-inner">
          <p className="ip-hero-eyebrow">XINGYIN SHANHE</p>
          <h1 className="ip-hero-title">行吟山河</h1>
          <p className="ip-hero-tag">追随千古诗人步履　行走华夏山河之间</p>

          <p className="ip-hero-body">
            一千年前，苏轼从眉山出发，走过了这片土地上的两百三十四个地方。他栖身的黄州，风骨依旧；他疏浚的西湖，清丽如初；他挥毫作赋的赤壁石，风华未改。
          </p>

          <p className="ip-hero-em">跟着苏轼，走遍神州</p>

          <div className="ip-hero-actions">
            <Link href="/explore" className="ip-btn-primary">
              开始探索
              <span className="material-symbols-outlined" style={{ fontSize: 18 }} aria-hidden="true">
                arrow_forward
              </span>
            </Link>
            <a href="#trajectory" className="ip-btn-secondary">
              了解一生
            </a>
          </div>
        </div>
      </section>

      {/* ============ Bento 数字看板 ============ */}
      <section className="ip-section" aria-label="数字一瞥">
        <div className="ip-bento-grid">
          {[
            { n: '234', l: '个足迹点' },
            { n: '20', l: '条主题路线' },
            { n: '3000+', l: '首诗词' },
            { n: '14', l: '个省份' },
          ].map((s) => (
            <div key={s.l} className="ip-bento">
              <span className="ip-bento-num">{s.n}</span>
              <span className="ip-bento-label">{s.l}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ============ 苏轼一生轨迹（5 阶段时间轴） ============ */}
      <section id="trajectory" className="ip-section">
        <div className="ip-section-head">
          <span className="ip-section-eyebrow">LIFE TRAJECTORY</span>
          <h2 className="ip-section-title">苏轼一生轨迹</h2>
          <p className="ip-section-sub">从四川眉山到海南儋州，走过半个中国</p>
          <div className="ip-section-bar" />
        </div>

        <div className="ip-timeline">
          <div className="ip-timeline-stages">
            {[
              { name: '眉山少年', sub: '求学初出' },
              { name: '仕途初期', sub: '开封·凤翔' },
              { name: '东坡居士', sub: '黄州四年' },
              { name: '南贬岁月', sub: '惠州·儋州' },
              { name: '晚年北归', sub: '常州长眠' },
            ].map((s) => (
              <div key={s.name} className="ip-timeline-stage">
                <span className="ip-timeline-stage-name">{s.name}</span>
                <span className="ip-timeline-stage-sub">{s.sub}</span>
              </div>
            ))}
          </div>

          <div className="ip-timeline-track">
            <div className="ip-timeline-fill" />
          </div>

          <div className="ip-timeline-dots">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={
                  i === 2 || i === 3
                    ? 'ip-timeline-dot ip-timeline-dot--cinnabar'
                    : 'ip-timeline-dot'
                }
              />
            ))}
          </div>

          <div className="ip-timeline-years">
            {['1037', '1057', '1080', '1094', '1101'].map((y) => (
              <span key={y} className="ip-timeline-year">
                {y}
              </span>
            ))}
          </div>
        </div>

        {/* 路线浏览入口 */}
        <div style={{ maxWidth: 720, margin: '40px auto 0', padding: '0 8px' }}>
          <Link
            href="/routes"
            className="ip-card"
            style={{
              display: 'block',
              textAlign: 'center',
              textDecoration: 'none',
            }}
          >
            <p className="ip-section-eyebrow" style={{ marginBottom: 6 }}>
              VIEW ALL ROUTES
            </p>
            <p
              className="font-wenkai"
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: 'var(--ip-on-surface)',
                marginBottom: 6,
                letterSpacing: '0.06em',
              }}
            >
              查看 20 条路线 →
            </p>
            <p
              className="ip-body-md"
              style={{ fontSize: 13, lineHeight: '20px', margin: 0 }}
            >
              每条路线都是一段独立故事 · 含史诗叙事 / 关键事件 / 文学创作
            </p>
          </Link>
        </div>
      </section>

      {/* ============ 代表性足迹 ============ */}
      <section className="ip-section" style={{ background: 'var(--ip-surface-container-low)' }}>
        <div className="ip-section-head">
          <span className="ip-section-eyebrow">FEATURED PLACES</span>
          <h2 className="ip-section-title">代表性足迹</h2>
          <p className="ip-section-sub">点击地点，查看苏轼在那里发生的一切</p>
          <div className="ip-section-bar" />
        </div>

        <div className="ip-grid-4">
          {[
            {
              pid: 'P072',
              name: '黄州',
              chip: '贬谪',
              chipKind: 'cinnabar' as const,
              year: '1080.2 — 1084.4',
              loc: '湖北黄冈',
              desc: '因乌台诗案被贬，自号"东坡居士"。人生最低谷，写下最伟大的作品群。',
              line: '大江东去，浪淘尽，千古风流人物。',
            },
            {
              pid: 'P024',
              name: '赤壁',
              chip: '游历',
              chipKind: 'bronze' as const,
              year: '1082.7 / 1082.10',
              loc: '两游赤壁',
              desc: '两个秋夜，成就了前后《赤壁赋》与《念奴娇》，改变了中国文学的走向。',
              line: '寄蜉蝣于天地，渺沧海之一粟。',
            },
            {
              pid: 'P058',
              name: '杭州',
              chip: '为官',
              chipKind: 'bronze' as const,
              year: '1071 / 1089',
              loc: '两知杭州',
              desc: '两次主政杭州，疏浚西湖、筑成苏堤。山水间的政治家与诗人合二为一。',
              line: '欲把西湖比西子，淡妆浓抹总相宜。',
            },
            {
              pid: 'P034',
              name: '儋州',
              chip: '贬谪',
              chipKind: 'cinnabar' as const,
              year: '1097.5 — 1100.6',
              loc: '海南儋州',
              desc: '62 岁再贬海南，办学堂传文化，留下海南历史上最早的文脉。',
              line: '他年谁作舆地志，海南万里真吾乡。',
            },
          ].map((p) => (
            <Link
              key={p.name}
              href={`/explore?focus=${p.pid}`}
              className="ip-place-card"
            >
              <div className="ip-place-card-meta">
                <span
                  className={
                    p.chipKind === 'cinnabar'
                      ? 'ip-chip ip-chip-cinnabar'
                      : 'ip-chip ip-chip-bronze'
                  }
                >
                  {p.chip}
                </span>
                <span className="ip-label-caps" style={{ fontSize: 10 }}>
                  {p.year}
                </span>
              </div>

              <h3 className="ip-place-card-title">{p.name}</h3>

              <div className="ip-place-card-loc">
                <span className="material-symbols-outlined" aria-hidden="true">
                  location_on
                </span>
                <span>{p.loc}</span>
              </div>

              <p className="ip-place-card-quote">{p.line}</p>
              <p className="ip-place-card-desc">{p.desc}</p>

              <span className="ip-place-card-cta">
                查看详情
                <span className="material-symbols-outlined" style={{ fontSize: 16 }} aria-hidden="true">
                  arrow_forward
                </span>
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* ============ 此心安处是吾乡 ============ */}
      <section className="ip-quote">
        <div className="ip-quote-bar" />
        <p className="ip-quote-main">此心安处是吾乡</p>
        <p className="ip-quote-src">苏轼《定风波》</p>
        <p className="ip-quote-note">
          每一个他停留过的地方，都是他的家乡。
          <br />
          那些地方，今天还在。
        </p>
        <div className="ip-quote-bar" style={{ marginTop: 24 }} />
      </section>

      {/* ============ COMING SOON ============ */}
      <section className="ip-section">
        <div className="ip-section-head">
          <span className="ip-section-eyebrow">COMING SOON</span>
          <h2 className="ip-section-title">行吟山河不止于苏轼</h2>
          <p className="ip-section-sub">他们都走过这片土地，只是时代不同</p>
          <div className="ip-section-bar" />
        </div>

        <div className="ip-grid-4">
          <div className="ip-card" style={{ textAlign: 'center' }}>
            <h3
              className="font-wenkai"
              style={{
                fontSize: 22,
                fontWeight: 700,
                color: 'var(--ip-on-surface)',
                margin: '0 0 6px',
                letterSpacing: '0.1em',
              }}
            >
              苏轼
            </h3>
            <p className="ip-label-caps" style={{ fontSize: 10, marginBottom: 12 }}>
              1037 — 1101
            </p>
            <p className="ip-label-caps" style={{ fontSize: 10, opacity: 0.7 }}>
              64 年人生
            </p>
            <span className="ip-chip ip-chip-bronze">已上线 · 234 地</span>
          </div>
          {[
            { n: '李白', y: '701 — 762' },
            { n: '杜甫', y: '712 — 770' },
            { n: '白居易', y: '772 — 846' },
          ].map((f) => (
            <div key={f.n} className="ip-card" style={{ textAlign: 'center' }}>
              <h3
                style={{
                  fontFamily: 'Noto Serif SC, serif',
                  fontSize: 22,
                  fontWeight: 700,
                  color: 'var(--ip-on-surface)',
                  margin: '0 0 6px',
                  letterSpacing: '0.1em',
                }}
              >
                {f.n}
              </h3>
              <p className="ip-label-caps" style={{ fontSize: 10, marginBottom: 12 }}>
                {f.y}
              </p>
              <span className="ip-chip ip-chip-neutral">规划中</span>
            </div>
          ))}
        </div>
      </section>

      {/* ============ ABOUT ============ */}
      <section className="ip-section" style={{ background: 'var(--ip-surface-container-low)' }}>
        <div className="ip-section-head">
          <span className="ip-section-eyebrow">ABOUT</span>
          <h2 className="ip-section-title">中国的山河从来不只是地理</h2>
          <div className="ip-section-bar" />
        </div>

        <div className="ip-grid-3">
          {[
            {
              poet: '苏轼在黄州',
              t: '一个人如何在人生最低谷写出最伟大的作品',
              p: '被贬、种地、酿酒、作诗。他没有对抗命运，而是在每一寸他站立的土地上，让自己扎根下去。',
            },
            {
              poet: '我们做一件简单的事',
              t: '不是旅游攻略，不是语文课本',
              p: '是一千年前的某个人，曾经站在你现在站的地方，抬头看了同一片天。',
            },
            {
              poet: '移动端优先',
              t: '在路上随时查，到了地方就能用',
              p: '添加到手机桌面即用，高德地图一键导航，离线可用，完全免费。',
            },
          ].map((a) => (
            <div key={a.poet} className="ip-card">
              <p
                className="font-wenkai ip-vertical-header"
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  letterSpacing: '0.18em',
                  color: 'var(--ip-on-surface-variant)',
                  marginBottom: 12,
                  textTransform: 'none',
                }}
              >
                {a.poet}
              </p>
              <h3
                className="font-wenkai"
                style={{
                  fontSize: 17,
                  lineHeight: '26px',
                  fontWeight: 600,
                  color: 'var(--ip-on-surface)',
                  margin: '0 0 10px',
                }}
              >
                {a.t}
              </h3>
              <p className="ip-body-md" style={{ margin: 0 }}>
                {a.p}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ============ Final CTA ============ */}
      <section className="ip-cta">
        <h2 className="ip-cta-title">在地图上，跟他走一遍</h2>
        <p className="ip-cta-sub">234 处足迹 · 20 条路线 · 328 篇诗词 · 14 省山河</p>
        <div className="ip-cta-btns">
          <Link href="/explore" className="ip-btn-primary">
            进入地图
            <span className="material-symbols-outlined" style={{ fontSize: 18 }} aria-hidden="true">
              arrow_forward
            </span>
          </Link>
          <Link href="/routes" className="ip-btn-secondary">
            浏览 20 条路线
          </Link>
          <Link href="/explore?focus=P072" className="ip-btn-secondary">
            从黄州开始
          </Link>
        </div>
      </section>

      {/* ============ Footer ============ */}
      <footer className="ip-footer">
        <div className="ip-footer-brand">行吟山河</div>
        <div className="ip-footer-en">XINGYIN SHANHE</div>
        <p className="ip-footer-note">追随千古诗人步履　行走华夏山河之间</p>
        <p className="ip-footer-copy">
          © 2026 · 一个慢慢做下去的项目 · 数据 v4 · 234 地点 · 328 篇诗词
        </p>
      </footer>
    </div>
  );
}
