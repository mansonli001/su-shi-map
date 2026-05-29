'use client';

/**
 * 关于页 v4.0
 * 数据来源与免责声明
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
          <h1 className="text-lg font-serif text-ink">关于本项目</h1>
        </div>
      </div>

      <div className="pt-16 px-4 pb-8 max-w-2xl mx-auto prose-ancient">
        {/* 项目介绍 */}
        <section className="mb-8">
          <h2 className="text-xl font-serif text-ink mb-4">读苏轼·游神州</h2>
          <p className="text-ink/70 leading-relaxed">
            本项目是一个交互式数字地图应用，展示苏轼一生走过的120个地点。
            用户可以在地图上查看苏轼的足迹、阅读相关事迹与诗词、打卡签到、生成分享长图。
          </p>
          <p className="text-ink/70 leading-relaxed mt-4">
            项目采用 PWA（Progressive Web App）技术，支持离线使用和移动端安装。
          </p>
        </section>

        {/* 数据来源 */}
        <section className="mb-8">
          <h3 className="text-lg font-serif text-ink mb-3">数据来源</h3>
          <div className="space-y-3 text-sm text-ink/60">
            <div>
              <h4 className="font-medium text-ink/80">苏轼生平数据</h4>
              <p>基于《苏轼年谱》、《苏轼全集校注》等权威文献整理。</p>
            </div>
            <div>
              <h4 className="font-medium text-ink/80">诗词数据</h4>
              <p>
                来源于{' '}
                <a
                  href="https://github.com/chinese-poetry/chinese-poetry"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-ink hover:underline"
                >
                  chinese-poetry
                </a>{' '}
                （CC0 公共领域）。
              </p>
            </div>
            <div>
              <h4 className="font-medium text-ink/80">历史地理数据</h4>
              <p>
                北宋政区数据来源于 CHGIS（哈佛大学 + 复旦大学），转载请注明出处。
              </p>
            </div>
            <div>
              <h4 className="font-medium text-ink/80">地图服务</h4>
              <p>使用高德地图 JSAPI 2.0，坐标系统为 GCJ-02。</p>
            </div>
          </div>
        </section>

        {/* 字体与开源协议 */}
        <section className="mb-8">
          <h3 className="text-lg font-serif text-ink mb-3">字体与开源协议</h3>
          <div className="space-y-2 text-sm text-ink/60">
            <p>
              <strong>Noto Serif SC</strong>（思源宋体）- SIL OFL 开源协议，无版权风险。
            </p>
            <p>
              本项目源代码采用 MIT 协议开源，详见{' '}
              <a href="/LICENSE" className="text-ink hover:underline">
                LICENSE
              </a>{' '}
              文件。
            </p>
          </div>
        </section>

        {/* 免责声明 */}
        <section className="mb-8">
          <h3 className="text-lg font-serif text-ink mb-3">免责声明</h3>
          <div className="space-y-2 text-sm text-ink/60">
            <p>
              1. 本项目为个人学习研究项目，不构成任何专业建议。
            </p>
            <p>
              2. 旅游信息（门票、开放时间等）会随时间变化，请以南现场为准。
            </p>
            <p>
              3. 诗词今译与赏析为 AI 辅助生成，仅供参考，不代表学术观点。
            </p>
            <p>
              4. 若您发现数据错误，欢迎通过 GitHub Issues 提出修正建议。
            </p>
          </div>
        </section>

        {/* 联系方式 */}
        <section className="mb-8">
          <h3 className="text-lg font-serif text-ink mb-3">联系与贡献</h3>
          <p className="text-sm text-ink/60">
            GitHub:{' '}
            <a
              href="https://github.com/mansonli001/su-shi-map"
              target="_blank"
              rel="noopener noreferrer"
              className="text-ink hover:underline"
            >
              mansonli001/su-shi-map
            </a>
          </p>
        </section>

        {/* 返回按钮 */}
        <div className="mt-8">
          <button
            onClick={() => (window.location.href = '/')}
            className="px-4 py-2 rounded-lg border border-ink/20 text-sm text-ink hover:bg-ink/5 transition-colors"
          >
            ← 返回地图
          </button>
        </div>
      </div>
    </div>
  );
}
