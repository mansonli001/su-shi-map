/**
 * 成就卡弹窗组件 — 文人手稿风格
 * 基于 Stitch 设计稿 stitch_designs/single/code.html
 * 羊皮纸底纹 + 双线描边 + LXGW WenKai Mono TC 字体
 * 响应式：max-h-[90dvh]，内容区滚动，header/footer 固定
 */

'use client';

import { useEffect, useRef, useState } from 'react';

/* ── 类型定义 ── */
export interface AchievementModalProps {
  achievement: {
    id: string;
    name: string;
    description: string;
    tier: 'bronze' | 'silver' | 'gold' | 'special';
    imageUrl: string;
    poem: string[];
    poemSource: string;
    unlockedAt?: string;
  };
  userStats: {
    checkinCount: number;
    achievementCount: number;
    totalAchievements: number;
    progressPercent: number;
  };
  onClose: () => void;
  /** 可选：保留兼容旧调用，按钮已改为直接下载当前成就卡，不再触发跳转 */
  onShare?: () => void;
}

/* ── tier 映射 ── */
const TIER_MAP: Record<string, string> = {
  bronze: '铜级成就',
  silver: '银级成就',
  gold: '金级成就',
  special: '特别成就',
};

/* ── QR码加载器（动态CDN） ── */
function loadQRCodeLib(): Promise<void> {
  return new Promise((resolve) => {
    if ((window as unknown as Record<string, unknown>).QRCode) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';
    script.onload = () => resolve();
    script.onerror = () => resolve();
    document.head.appendChild(script);
  });
}

/* ── 日期格式化 ── */
function formatDate(isoStr?: string): string {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}.${m}.${day}`;
}

export default function AchievementModal({
  achievement,
  userStats,
  onClose,
}: AchievementModalProps) {
  const qrcodeRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLElement>(null);
  const [downloading, setDownloading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  // 右上角按钮：直接把当前成就卡截成高清图片下载，无跳转
  const handleDownload = async () => {
    const card = cardRef.current;
    if (!card || downloading) return;
    setDownloading(true);

    // 找到内部可滚动内容区，截图前临时展开，保证排版完整（不被滚动裁切）
    const scrollArea = card.querySelector<HTMLElement>('[data-capture-scroll]');
    const saved = {
      cardMaxH: card.style.maxHeight,
      cardOverflow: card.style.overflow,
      areaOverflow: scrollArea?.style.overflow ?? '',
    };

    try {
      // 临时移除高度限制 + 滚动，让卡片完整展开
      card.style.maxHeight = 'none';
      card.style.overflow = 'visible';
      if (scrollArea) scrollArea.style.overflow = 'visible';
      // 等一帧让布局刷新
      await new Promise((r) => requestAnimationFrame(() => r(null)));

      const html2canvas = (await import('html2canvas')).default;
      const canvas = await html2canvas(card, {
        scale: 3,            // 高清：3 倍像素密度
        useCORS: true,       // 允许跨域图片入画
        backgroundColor: '#fff8f5',
        logging: false,
        windowWidth: card.scrollWidth,
        windowHeight: card.scrollHeight,
        // 截图时忽略顶部操作按钮，保证排版干净
        ignoreElements: (el) => el.getAttribute('data-skip-capture') === 'true',
      });
      const dataUrl = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      const safeName = (achievement.name || '成就').replace(/[\\/:*?"<>|]/g, '');
      link.download = `行吟山河-${safeName}.png`;
      link.href = dataUrl;
      link.click();
      setToast('图片已保存到本地');
    } catch (err) {
      console.error('生成成就卡图片失败:', err);
      setToast('生成失败，请重试');
    } finally {
      // 恢复原样式
      card.style.maxHeight = saved.cardMaxH;
      card.style.overflow = saved.cardOverflow;
      if (scrollArea) scrollArea.style.overflow = saved.areaOverflow;
      setDownloading(false);
      setTimeout(() => setToast(null), 2000);
    }
  };

  // 初始化 QR 码
  useEffect(() => {
    let cancelled = false;
    loadQRCodeLib().then(() => {
      if (cancelled || !qrcodeRef.current) return;
      const QRCodeCtor = (window as unknown as Record<string, unknown>).QRCode as
        | (new (el: HTMLElement, opts: Record<string, unknown>) => unknown)
        | undefined;
      if (QRCodeCtor && qrcodeRef.current) {
        qrcodeRef.current.innerHTML = '';
        new QRCodeCtor(qrcodeRef.current, {
          text: 'https://su-shi.starfluxes.com',
          width: 64,
          height: 64,
          colorDark: '#765538',
          colorLight: '#ffffff',
          correctLevel: 1,
        });
      }
    });
    return () => { cancelled = true; };
  }, []);

  // ESC 关闭
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  const tierLabel = TIER_MAP[achievement.tier] || '铜级成就';
  const dateStr = formatDate(achievement.unlockedAt);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4">
      {/* 背景遮罩 */}
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />

      {/* 主卡片 — 响应式：max-h 90dvh，内容区滚动 */}
      <main
        ref={cardRef}
        className="relative w-full max-w-[400px] max-h-[90dvh] ach-parchment-bg ach-double-border shadow-2xl overflow-hidden flex flex-col font-wenkai"
        style={{ animation: 'ach-modal-in 300ms cubic-bezier(0.34,1.56,0.64,1) forwards' }}
      >
        {/* 顶部栏 — 固定（截图时忽略，保证导出图片排版干净） */}
        <header data-skip-capture="true" className="shrink-0 w-full flex justify-between items-center px-6 py-4 z-20"
          style={{ background: 'rgba(255,248,245,0.85)', backdropFilter: 'blur(12px)' }}
        >
          <button onClick={onClose} aria-label="关闭" className="material-symbols-outlined cursor-pointer hover:opacity-70 transition-opacity"
            style={{ color: '#765538', fontVariationSettings: "'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24" }}
          >
            close
          </button>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#765538' }}>行吟山河</h1>
          <button
            onClick={handleDownload}
            disabled={downloading}
            aria-label="保存成就卡图片"
            className="material-symbols-outlined cursor-pointer hover:opacity-70 transition-opacity disabled:opacity-50"
            style={{ color: '#765538', fontVariationSettings: "'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24" }}
          >
            {downloading ? 'hourglass_empty' : 'download'}
          </button>
        </header>

        {/* 可滚动内容区 */}
        <div data-capture-scroll className="flex-1 overflow-y-auto overscroll-contain">
          {/* 插画区 — 响应式高度 */}
          <section className="w-full px-6 pt-4 relative">
            <div className="w-full aspect-[4/3] sm:aspect-auto sm:h-[280px] md:h-[340px] relative group">
              <div className="absolute -inset-2" style={{ background: 'rgba(127,85,57,0.05)', filter: 'blur(24px)' }} />
              <div className="w-full h-full overflow-hidden rounded-sm border shadow-lg relative"
                style={{ borderWidth: '1px', borderColor: '#d3c4b9' }}
              >
                <img
                  alt={achievement.name}
                  className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105"
                  src={achievement.imageUrl}
                  crossOrigin="anonymous"
                />
                <div className="absolute inset-0 pointer-events-none"
                  style={{ boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>
            {/* 等级徽章 — 独立居中显示于画作下方，不遮挡画面 */}
            <div className="flex justify-center mt-6">
              <div className="ach-gold-badge px-6 py-2 text-xs border rounded-full flex items-center justify-center gap-2 whitespace-nowrap"
                style={{ color: '#ffffff', borderColor: 'rgba(118,85,56,0.3)' }}
              >
                <span className="material-symbols-outlined text-base leading-none"
                  style={{ fontVariationSettings: "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24" }}
                >
                  workspace_premium
                </span>
                {/* tracking 末尾空白用左侧 paddingLeft 补偿，使图标+文字整体视觉居中 */}
                <span className="leading-none" style={{ letterSpacing: '0.2em', paddingLeft: '0.2em' }}>{tierLabel}</span>
              </div>
            </div>
          </section>

          {/* 成就内容 */}
          <section className="w-full px-8 mt-6 text-center">
            <h2 className="text-2xl sm:text-[36px] font-bold mb-4 leading-tight" style={{ color: '#765538' }}>
              {achievement.name}
            </h2>
            <div className="ach-lattice-divider w-1/2 mx-auto mb-6" />
            {/* 诗词块 */}
            <div className="mb-6 text-lg sm:text-xl leading-[1.9]" style={{ color: '#4f453d' }}>
              {achievement.poem.map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
            <div className="ach-lattice-divider w-1/2 mx-auto" />
          </section>

          {/* 数据栏 */}
          <section className="w-full px-8 py-6">
            <div className="grid grid-cols-3 py-4"
              style={{ borderTop: '1px solid rgba(211,196,185,0.3)', borderBottom: '1px solid rgba(211,196,185,0.3)' }}
            >
              <div className="flex flex-col items-center" style={{ borderRight: '1px solid rgba(211,196,185,0.3)' }}>
                <span className="text-xs uppercase tracking-wider mb-1" style={{ color: '#81756b' }}>打卡足迹</span>
                <span className="text-lg sm:text-xl font-bold" style={{ color: '#7f5539' }}>{userStats.checkinCount}</span>
              </div>
              <div className="flex flex-col items-center" style={{ borderRight: '1px solid rgba(211,196,185,0.3)' }}>
                <span className="text-xs uppercase tracking-wider mb-1" style={{ color: '#81756b' }}>解锁成就</span>
                <span className="text-lg sm:text-xl font-bold" style={{ color: '#7f5539' }}>{userStats.achievementCount}/{userStats.totalAchievements}</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-xs uppercase tracking-wider mb-1" style={{ color: '#81756b' }}>苏途进度</span>
                <span className="text-lg sm:text-xl font-bold" style={{ color: '#7f5539' }}>{userStats.progressPercent}%</span>
              </div>
            </div>
          </section>

          {/* 底部信息 + QR码 */}
          <footer className="w-full pt-6 pb-8 px-8 flex items-stretch justify-between gap-5"
            style={{ background: 'rgba(236,224,217,0.4)', borderTop: '1px solid rgba(211,196,185,0.3)' }}
          >
            <div className="flex flex-col gap-1.5 min-w-0 flex-1">
              <p className="text-base sm:text-lg font-bold leading-snug" style={{ color: '#765538' }}>{achievement.name}</p>
              <p className="text-[13px] leading-relaxed" style={{ color: 'rgba(79,69,61,0.85)' }}>{achievement.description}</p>
              <div className="mt-auto pt-3" style={{ borderTop: '1px solid rgba(211,196,185,0.2)' }}>
                {dateStr && (
                  <p className="text-[10px] tracking-widest uppercase mb-1" style={{ color: '#81756b' }}>
                    入卷时间 {dateStr}
                  </p>
                )}
                <a className="text-[11px] font-bold block hover:underline break-all"
                  href="https://su-shi.starfluxes.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#7f5539' }}
                >
                  su-shi.starfluxes.com
                </a>
              </div>
            </div>
            <div className="flex flex-col items-center justify-center gap-2 shrink-0">
              <div className="p-2 bg-white border shadow-sm rounded-sm" style={{ borderColor: '#d3c4b9' }}>
                <div ref={qrcodeRef} />
              </div>
              <span className="text-[11px] font-bold tracking-tight" style={{ color: '#a8968a' }}>扫码同游</span>
            </div>
          </footer>
        </div>

        {/* 装饰性「詩」水印 */}
        <div data-skip-capture="true" className="absolute bottom-40 -left-10 opacity-5 pointer-events-none -rotate-12 select-none">
          <span className="text-[120px]" style={{ color: '#765538' }}>詩</span>
        </div>

        {/* 下载结果 Toast — 截图时忽略 */}
        {toast && (
          <div
            data-skip-capture="true"
            className="absolute left-1/2 bottom-6 -translate-x-1/2 z-30 px-4 py-2 rounded-lg text-sm font-wenkai shadow-lg whitespace-nowrap"
            style={{ background: 'rgba(118,85,56,0.92)', color: '#fff' }}
          >
            {toast}
          </div>
        )}
      </main>

      {/* 内联关键样式 */}
      <style jsx global>{`
        @keyframes ach-modal-in {
          from { transform: scale(0.9); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
