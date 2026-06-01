/**
 * 行吟山河 · 首页 Landing v1.0
 * 设计稿对应：v3.html 第①首页
 * 结构：Hero → 一生轨迹 → 代表性足迹 → 此心安处是吾乡 → COMING SOON → ABOUT → Footer
 *
 * 已删除：苏东坡人生路线图（用户决策：太复杂，后面"一生轨迹"已覆盖）
 *
 * 数字（来自 v4 真实数据）：
 *   - 234 个足迹（v4 places-index 总数）
 *   - 64 年人生（1101 - 1037）
 *   - 3000+ 首诗词（chinese-poetry 苏轼总作品 3186）
 *   - 14 个省份（精确算自 places.modern_name）
 */

'use client';

import Link from 'next/link';

export default function HomeLanding() {
  return (
    <div className="ho-root">
      {/* ============ Hero ============ */}
      <section className="ho-hero">
        <div className="ho-en">XINGYIN SHANHE</div>
        <h1 className="logo-brand logo-brand-lg ho-brand">行吟山河</h1>
        <div className="ho-tag">追随千古诗人步履　行走华夏山河之间</div>

        <svg
          width="160"
          height="50"
          viewBox="0 0 160 50"
          className="ho-trace"
          aria-hidden="true"
        >
          <polyline
            points="12,42 38,30 68,18 100,30 132,12 152,36"
            fill="none"
            stroke="#FAC775"
            strokeWidth="1"
            opacity="0.35"
          />
          <polyline
            points="12,42 38,30 68,18"
            fill="none"
            stroke="#FAC775"
            strokeWidth="1.5"
            opacity="0.9"
          />
          <circle cx="12" cy="42" r="3" fill="#FAC775" opacity="0.9" />
          <circle cx="38" cy="30" r="2.5" fill="#FAC775" opacity="0.7" />
          <circle cx="68" cy="18" r="4" fill="#FAC775" />
          <circle cx="100" cy="30" r="3" fill="#FAC775" opacity="0.75" />
          <circle cx="132" cy="12" r="2.5" fill="#FAC775" opacity="0.6" />
          <circle cx="152" cy="36" r="3.5" fill="#FAC775" opacity="0.85" />
        </svg>

        <p className="ho-body">
          一千年前，苏轼从眉山出发，走过了这片土地上的两百三十四个地方。
          <br />
          他栖身的黄州，风骨依旧；他疏浚的西湖，清丽如初。
          <br />
          他挥毫作赋的赤壁石，风华未改。
        </p>

        <div className="ho-em">在地图上，跟他走一遍。</div>

        <div className="ho-btns">
          <Link href="/explore" className="ho-btn-p">
            开始探索 →
          </Link>
          <a href="#trajectory" className="ho-btn-s">
            了解一生
          </a>
        </div>

        <div className="ho-scroll">↓ 向下滚动</div>
      </section>

      {/* ============ 一生轨迹 ============ */}
      <section id="trajectory" className="ho-sec ho-sec--cream">
        <div className="ho-sec-lbl">LIFE TRAJECTORY</div>
        <h2 className="ho-sec-title">苏轼一生轨迹</h2>
        <div className="ho-sec-sub">从四川眉山到海南儋州，走过半个中国</div>
        <div className="ho-gold-bar" />

        <div className="ho-tl">
          <div className="ho-tl-stages">
            {[
              { name: '眉山少年', sub: '求学初出' },
              { name: '仕途初期', sub: '开封·凤翔' },
              { name: '东坡居士', sub: '黄州四年' },
              { name: '南贬岁月', sub: '惠州·儋州' },
              { name: '晚年北归', sub: '常州长眠' },
            ].map((s) => (
              <div key={s.name} className="ho-tl-s">
                <span className="ho-tl-sname">{s.name}</span>
                <span className="ho-tl-ssub">{s.sub}</span>
              </div>
            ))}
          </div>
          <div className="ho-tl-track">
            <div className="ho-tl-fill" />
          </div>
          <div className="ho-tl-dots">
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} className="ho-tl-dot" />
            ))}
          </div>
          <div className="ho-tl-years">
            {['1037', '1057', '1080', '1094', '1101'].map((y) => (
              <span key={y} className="ho-tl-yr">
                {y}
              </span>
            ))}
          </div>
        </div>

        <div className="ho-tl-stats">
          <div>
            <div className="ho-stat-n">64</div>
            <div className="ho-stat-l">年人生</div>
          </div>
          <div>
            <div className="ho-stat-n">234</div>
            <div className="ho-stat-l">个足迹点</div>
          </div>
          <div>
            <div className="ho-stat-n">3000+</div>
            <div className="ho-stat-l">首诗词</div>
          </div>
          <div>
            <div className="ho-stat-n">14</div>
            <div className="ho-stat-l">个省份</div>
          </div>
        </div>

        {/* 路线浏览入口（设计稿 ③ 路线介绍链接） */}
        <div className="ho-routes-entry">
          <Link href="/routes" className="ho-routes-card">
            <div className="ho-routes-en">VIEW ALL ROUTES</div>
            <div className="ho-routes-title">查看 20 条路线 →</div>
            <div className="ho-routes-sub">
              每条路线都是一段独立故事 · 含史诗叙事 / 关键事件 / 文学创作
            </div>
          </Link>
        </div>
      </section>

      {/* ============ 代表性足迹 ============ */}
      <section className="ho-sec ho-sec--ivory">
        <div className="ho-sec-lbl">FEATURED PLACES</div>
        <h2 className="ho-sec-title">代表性足迹</h2>
        <div className="ho-sec-sub">点击地点，查看苏轼在那里发生的一切</div>

        <div className="ho-pg-grid">
          {[
            {
              pid: 'P072',
              name: '黄州',
              year: '1080.2 — 1084.4 · 湖北黄冈',
              accent: '#BA7517',
              desc: '因乌台诗案被贬，自号"东坡居士"。人生最低谷，写下最伟大的作品群。',
              line: '大江东去，浪淘尽，千古风流人物。',
            },
            {
              pid: 'P024',
              name: '赤壁',
              year: '1082.7 / 1082.10 · 两游赤壁',
              accent: '#085041',
              desc: '两个秋夜，成就了前后《赤壁赋》与《念奴娇》，改变了中国文学的走向。',
              line: '寄蜉蝣于天地，渺沧海之一粟。',
            },
            {
              pid: 'P058',
              name: '杭州',
              year: '1071 / 1089 · 两知杭州',
              accent: '#0C447C',
              desc: '两次主政杭州，疏浚西湖、筑成苏堤。山水间的政治家与诗人合二为一。',
              line: '欲把西湖比西子，淡妆浓抹总相宜。',
            },
            {
              pid: 'P034',
              name: '儋州',
              year: '1097.5 — 1100.6 · 海南儋州',
              accent: '#712B13',
              desc: '62 岁再贬海南，办学堂传文化，留下海南历史上最早的文脉。',
              line: '他年谁作舆地志，海南万里真吾乡。',
            },
          ].map((p) => (
            <div key={p.name} className="ho-pgcard">
              <div className="ho-pgcard-acc" style={{ background: p.accent }} />
              <div className="ho-pgcard-body">
                <div className="ho-pname">{p.name}</div>
                <div className="ho-pyear">{p.year}</div>
                <div className="ho-pdesc">{p.desc}</div>
                <div className="ho-pl">{p.line}</div>
                <Link href={`/explore?focus=${p.pid}`} className="ho-plink">
                  查看详情 →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ============ 此心安处是吾乡 ============ */}
      <section className="ho-qt">
        <div className="ho-qt-bar" />
        <div className="ho-qt-main">此心安处是吾乡</div>
        <div className="ho-qt-src">
          苏轼《定风波·南海归赠王定国侍人寓娘》
        </div>
        <div className="ho-qt-note">
          每一个他停留过的地方，都是他的家乡。
          <br />
          那些地方，今天还在。
        </div>
        <div className="ho-qt-bar" style={{ marginTop: '1.5rem' }} />
      </section>

      {/* ============ COMING SOON ============ */}
      <section className="ho-sec ho-sec--cream">
        <div className="ho-sec-lbl">COMING SOON</div>
        <h2 className="ho-sec-title">行吟山河不止于苏轼</h2>
        <div className="ho-sec-sub">他们都走过这片土地，只是时代不同</div>

        <div className="ho-ft-grid">
          <div className="ho-ft-card">
            <div className="ho-ft-name">苏轼</div>
            <div className="ho-ft-yrs">1037 — 1101</div>
            <span className="ho-tag-live">已上线 · 234 地</span>
          </div>
          {[
            { n: '李白', y: '701 — 762' },
            { n: '杜甫', y: '712 — 770' },
            { n: '白居易', y: '772 — 846' },
          ].map((f) => (
            <div key={f.n} className="ho-ft-card">
              <div className="ho-ft-name">{f.n}</div>
              <div className="ho-ft-yrs">{f.y}</div>
              <span className="ho-tag-soon">规划中</span>
            </div>
          ))}
        </div>
      </section>

      {/* ============ ABOUT ============ */}
      <section className="ho-sec ho-sec--ivory">
        <div className="ho-sec-lbl">ABOUT</div>
        <h2 className="ho-sec-title">中国的山河从来不只是地理</h2>

        <div className="ho-ab-grid">
          <div>
            <div className="ho-ab-poet">苏轼在黄州</div>
            <div className="ho-ab-t">
              一个人如何在人生最低谷写出最伟大的作品
            </div>
            <div className="ho-ab-p">
              被贬、种地、酿酒、作诗。他没有对抗命运，而是在每一寸他站立的土地上，让自己扎根下去。
            </div>
          </div>
          <div>
            <div className="ho-ab-poet">我们做一件简单的事</div>
            <div className="ho-ab-t">不是旅游攻略，不是语文课本</div>
            <div className="ho-ab-p">
              是一千年前的某个人，曾经站在你现在站的地方，抬头看了同一片天。
            </div>
          </div>
          <div>
            <div className="ho-ab-poet">移动端优先</div>
            <div className="ho-ab-t">在路上随时查，到了地方就能用</div>
            <div className="ho-ab-p">
              添加到手机桌面即用，高德地图一键导航，离线可用，完全免费。
            </div>
          </div>
        </div>
      </section>

      {/* ============ Final CTA ============ */}
      <section className="ho-cta">
        <div className="ho-cta-bar" />
        <h2 className="ho-cta-title">在地图上，跟他走一遍</h2>
        <div className="ho-cta-sub">
          234 个足迹 · 20 条路线 · 68 篇代表作 · 14 省山河
        </div>
        <div className="ho-cta-btns">
          <Link href="/explore" className="ho-btn-p">
            进入地图 →
          </Link>
          <Link href="/routes" className="ho-btn-s">
            浏览 20 条路线
          </Link>
          <Link href="/explore?focus=P072" className="ho-btn-s">
            从黄州开始
          </Link>
        </div>
      </section>

      {/* ============ Footer ============ */}
      <footer className="ho-footer">
        <div className="logo-brand logo-brand-md ho-hf-brand">行吟山河</div>
        <div className="ho-hf-en">XINGYIN SHANHE</div>
        <div className="ho-hf-note">
          追随千古诗人步履　行走华夏山河之间
        </div>
        <div className="ho-hf-copy">
          © 2026 · 一个慢慢做下去的项目 · 数据 v4 · 234 地点 · 68 篇代表作
        </div>
      </footer>
    </div>
  );
}
