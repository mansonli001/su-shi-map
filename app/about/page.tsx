'use client';

/**
 * 关于页 v5.0「行吟山河」
 * 数据来源、字体方案与免责声明（v4 数据 + 字体 v6.0 双字体方案）
 */

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-paper">
      {/* 顶部 */}
      <div className="fixed top-0 inset-x-0 z-40 bg-paper/80 backdrop-blur-sm border-b border-ink/10 safe-top">
        <div className="flex items-center gap-3 px-4 py-3">
          <button
            onClick={() => (window.location.href = '/')}
            className="p-2 -ml-2 rounded-lg hover:bg-ink/5"
          >
            ←
          </button>
          <h1 className="text-lg font-wenkai text-ink tracking-wider">关于本项目</h1>
        </div>
      </div>

      <div className="pt-16 px-4 pb-8 max-w-2xl mx-auto">
        {/* 项目介绍 */}
        <section className="mb-8">
          <h2 className="text-2xl font-wenkai text-ink mb-2 tracking-wider">行吟山河</h2>
          <p className="text-xs text-gold-m tracking-[0.2em] mb-4">
            XINGYIN SHANHE · 读苏轼游神州
          </p>
          <p className="text-ink/70 leading-relaxed">
            一个慢慢做下去的项目。展示苏轼一生走过的{' '}
            <strong className="text-ink">234 个地点</strong>，
            涵盖{' '}
            <strong className="text-ink">20 条主题路线</strong>、
            <strong className="text-ink">6 个人生阶段</strong>、
            <strong className="text-ink">68 篇代表作</strong>，
            横跨现今{' '}
            <strong className="text-ink">14 个省份</strong>。
          </p>
          <p className="text-ink/70 leading-relaxed mt-4">
            用户可以在地图上查看苏轼的足迹、阅读相关事迹与诗词、按路线追溯不同人生阶段。
            采用 PWA 技术，支持添加到手机桌面、离线使用与高德地图一键导航。
          </p>
          <p className="text-ink/70 leading-relaxed mt-4 italic">
            项目愿景不止于苏轼——未来会陆续加入李白、杜甫、白居易等更多诗人的山河足迹。
          </p>
        </section>

        {/* 数据规模 */}
        <section className="mb-8">
          <h3 className="text-lg font-wenkai text-ink mb-3 tracking-wider">数据规模 · v4</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="p-3 bg-paper-2 rounded-lg">
              <div className="text-2xl font-mono text-gold-m">234</div>
              <div className="text-xs text-ink/60 mt-1">个足迹点</div>
            </div>
            <div className="p-3 bg-paper-2 rounded-lg">
              <div className="text-2xl font-mono text-gold-m">20</div>
              <div className="text-xs text-ink/60 mt-1">条主题路线</div>
            </div>
            <div className="p-3 bg-paper-2 rounded-lg">
              <div className="text-2xl font-mono text-gold-m">68</div>
              <div className="text-xs text-ink/60 mt-1">篇代表作</div>
            </div>
            <div className="p-3 bg-paper-2 rounded-lg">
              <div className="text-2xl font-mono text-gold-m">6</div>
              <div className="text-xs text-ink/60 mt-1">个人生阶段</div>
            </div>
          </div>
        </section>

        {/* 数据来源 */}
        <section className="mb-8">
          <h3 className="text-lg font-wenkai text-ink mb-3 tracking-wider">数据来源</h3>
          <div className="space-y-3 text-sm text-ink/65">
            <div>
              <h4 className="font-medium text-ink/85">苏轼生平数据</h4>
              <p>基于《苏轼年谱》、《苏轼全集校注》、《宋史·苏轼传》等权威文献整理。</p>
            </div>
            <div>
              <h4 className="font-medium text-ink/85">诗词数据</h4>
              <p>
                来源于{' '}
                <a
                  href="https://github.com/chinese-poetry/chinese-poetry"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gold-m hover:underline"
                >
                  chinese-poetry
                </a>{' '}
                （CC0 公共领域），苏轼总作品 3186 首。
              </p>
            </div>
            <div>
              <h4 className="font-medium text-ink/85">历史地理数据</h4>
              <p>
                北宋政区数据来源于 CHGIS（哈佛大学 + 复旦大学），现代地名由 v4 数据流水线匹配。
              </p>
            </div>
            <div>
              <h4 className="font-medium text-ink/85">地图服务</h4>
              <p>使用高德地图 JSAPI 2.0，坐标系统为 GCJ-02。</p>
            </div>
          </div>
        </section>

        {/* 字体方案 v6.0 */}
        <section className="mb-8">
          <h3 className="text-lg font-wenkai text-ink mb-3 tracking-wider">字体方案 · v6.0</h3>
          <div className="space-y-3 text-sm text-ink/65">
            <p>本项目采用双字体职能分工，兼顾现代易读与文化诗意：</p>
            <div className="pl-3 border-l-2 border-gold/40 space-y-2">
              <p>
                <strong className="text-ink">UI 主力</strong>：
                <span className="font-sans"> Noto Sans SC（思源黑体）</span> —— 导航、卡片、列表、按钮。SIL OFL 开源协议，由 Google + Adobe 联合发布。
              </p>
              <p>
                <strong className="text-ink">诗意锚点</strong>：
                <span className="font-wenkai"> LXGW WenKai（霞鹜文楷）</span> —— Hero 大标题、品牌名、诗句。SIL OFL 开源协议。
              </p>
              <p>
                <strong className="text-ink">数字</strong>：
                <span className="font-mono"> JetBrains Mono</span> —— 年份、统计数字。等宽美化。
              </p>
            </div>
            <p className="pt-2">
              本项目源代码采用 MIT 协议开源，详见{' '}
              <a href="https://github.com/mansonli001/su-shi-map" className="text-gold-m hover:underline">
                LICENSE
              </a>{' '}
              文件。
            </p>
          </div>
        </section>

        {/* 免责声明 */}
        <section className="mb-8">
          <h3 className="text-lg font-wenkai text-ink mb-3 tracking-wider">免责声明</h3>
          <div className="space-y-2 text-sm text-ink/65">
            <p>1. 本项目为个人学习研究项目，不构成任何专业建议。</p>
            <p>2. 旅游信息（门票、开放时间等）会随时间变化，请以现场为准。</p>
            <p>3. 诗词今译与赏析为 AI 辅助生成，仅供参考，不代表学术观点。</p>
            <p>4. 若您发现数据错误，欢迎通过 GitHub Issues 提出修正建议。</p>
          </div>
        </section>

        {/* 联系方式 */}
        <section className="mb-8">
          <h3 className="text-lg font-wenkai text-ink mb-3 tracking-wider">联系与贡献</h3>
          <p className="text-sm text-ink/65">
            GitHub:{' '}
            <a
              href="https://github.com/mansonli001/su-shi-map"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gold-m hover:underline"
            >
              mansonli001/su-shi-map
            </a>
          </p>
          <p className="text-sm text-ink/65 mt-2">
            部署平台：Vercel · 域名：su-shi.starfluxes.com
          </p>
        </section>

        {/* 返回按钮 */}
        <div className="mt-8 flex gap-3">
          <button
            onClick={() => (window.location.href = '/')}
            className="px-4 py-2 rounded-lg border border-ink/20 text-sm text-ink hover:bg-ink/5 transition-colors"
          >
            ← 返回首页
          </button>
          <button
            onClick={() => (window.location.href = '/explore')}
            className="px-4 py-2 rounded-lg bg-ink text-gold text-sm hover:bg-ink-mid transition-colors"
          >
            进入地图 →
          </button>
        </div>
      </div>
    </div>
  );
}
