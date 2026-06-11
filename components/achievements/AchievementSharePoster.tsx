/**
 * 成就合集海报组件 — 文人手稿风格
 * 基于 Stitch 设计稿 stitch_designs/share/screen.png
 * 5列网格25格 + 苏轼印章 + 诗词大字 + QR码
 * 供 html2canvas 截图生成分享图片
 * 布局：正常文档流，无 absolute 定位避免遮挡
 */

'use client';

import { useEffect, useRef, forwardRef } from 'react';

/* ── 类型定义 ── */
export interface AchievementSharePosterProps {
  achievements: Array<{
    id: string;
    name: string;
    tier: 'bronze' | 'silver' | 'gold' | 'special';
    imageUrl: string;
    poem: string[];
    poemSource: string;
    unlocked: boolean;
    unlockedAt?: string;
  }>;
  userStats: {
    checkinCount: number;
    achievementCount: number;
    totalAchievements: number;
    progressPercent: number;
  };
}

/* ── 中文日期 ── */
const DIGIT_CN: Record<string, string> = {
  '0': '〇', '1': '一', '2': '二', '3': '三', '4': '四',
  '5': '五', '6': '六', '7': '七', '8': '八', '9': '九',
};

function toChineseDate(date: Date): string {
  const y = String(date.getFullYear()).split('').map(d => DIGIT_CN[d]).join('');
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const mStr = m <= 10 ? (m === 10 ? '十' : DIGIT_CN[String(m)]) : `十${DIGIT_CN[String(m - 10)]}`;
  const dStr = d < 10 ? DIGIT_CN[String(d)] :
    d === 10 ? '十' :
    d < 20 ? `十${DIGIT_CN[String(d - 10)]}` :
    d === 20 ? '二十' :
    d < 30 ? `二十${DIGIT_CN[String(d - 20)]}` :
    d === 30 ? '三十' : `三十${DIGIT_CN[String(d - 30)]}`;
  return `${y}年${mStr}月${dStr}日`;
}

/* ── QR码加载器 ── */
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

/* ── 组件 ── */
const AchievementSharePoster = forwardRef<HTMLDivElement, AchievementSharePosterProps>(
  function AchievementSharePoster({ achievements, userStats }, ref) {
    const qrcodeRef = useRef<HTMLDivElement>(null);

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
            width: 72,
            height: 72,
            colorDark: '#765538',
            colorLight: '#ffffff',
            correctLevel: 1,
          });
        }
      });
      return () => { cancelled = true; };
    }, []);

    // 找最高级已解锁成就的诗词
    const tierOrder = { gold: 3, special: 3, silver: 2, bronze: 1 };
    const topAchievement = achievements
      .filter(a => a.unlocked)
      .sort((a, b) => (tierOrder[b.tier] || 0) - (tierOrder[a.tier] || 0))[0];

    const today = new Date();
    const chineseDate = toChineseDate(today);

    return (
      <div
        ref={ref}
        className="ach-parchment-bg ach-double-border font-wenkai relative overflow-hidden flex flex-col"
        style={{
          width: 750,
          height: 1080,
          padding: 0,
          color: '#201b16',
        }}
      >
        {/* ── 1. 顶部标题区 ── */}
        <div className="text-center pt-12 pb-6 shrink-0">
          <h1 className="text-5xl font-bold tracking-tight" style={{ color: '#765538' }}>
            行吟山河
          </h1>
          <div className="flex items-center justify-center gap-4 mt-3">
            <div className="h-px flex-1 max-w-[80px]" style={{ background: 'linear-gradient(90deg, transparent, #b08968)' }} />
            <span className="text-lg tracking-[0.2em]" style={{ color: '#7f5539' }}>我的成就合集</span>
            <div className="h-px flex-1 max-w-[80px]" style={{ background: 'linear-gradient(270deg, transparent, #b08968)' }} />
          </div>
        </div>

        {/* ── 2. 数据栏 ── */}
        <div className="flex items-center justify-center py-4 mx-8 shrink-0"
          style={{ borderTop: '1px solid rgba(211,196,185,0.4)', borderBottom: '1px solid rgba(211,196,185,0.4)' }}
        >
          <div className="flex-1 text-center">
            <p className="text-xs tracking-wider mb-1" style={{ color: '#81756b' }}>足迹地</p>
            <p className="text-2xl font-bold" style={{ color: '#7f5539' }}>{userStats.checkinCount}</p>
          </div>
          <div className="h-10 w-px" style={{ background: 'rgba(211,196,185,0.4)' }} />
          <div className="flex-1 text-center">
            <p className="text-xs tracking-wider mb-1" style={{ color: '#81756b' }}>已达成</p>
            <p className="text-2xl font-bold" style={{ color: '#7f5539' }}>{userStats.achievementCount}/{userStats.totalAchievements}</p>
          </div>
          <div className="h-10 w-px" style={{ background: 'rgba(211,196,185,0.4)' }} />
          <div className="flex-1 text-center">
            <p className="text-xs tracking-wider mb-1" style={{ color: '#81756b' }}>完成度</p>
            <p className="text-2xl font-bold" style={{ color: '#7f5539' }}>{userStats.progressPercent}%</p>
          </div>
        </div>

        {/* ── 3. 成就格子 5×5 ── */}
        <div className="grid grid-cols-5 gap-2.5 mx-8 mt-6 shrink-0">
          {achievements.map((ach) => (
            <div
              key={ach.id}
              className="aspect-square flex items-center justify-center relative"
              style={{
                background: ach.unlocked ? '#fef1ea' : '#ece0d9',
                border: ach.unlocked ? '1.5px solid #b08968' : '1px solid #d3c4b9',
              }}
            >
              {ach.unlocked ? (
                <img
                  src={ach.imageUrl}
                  alt={ach.name}
                  className="w-full h-full object-cover"
                  crossOrigin="anonymous"
                />
              ) : (
                <span className="material-symbols-outlined text-2xl" style={{ color: '#b0a890' }}>
                  lock
                </span>
              )}
            </div>
          ))}
        </div>

        {/* ── 4. 苏轼印章 + 诗词大字 ── */}
        <div className="mx-8 mt-8 flex items-start justify-between shrink-0">
          <div className="flex-1 text-center pr-4">
            {topAchievement && topAchievement.poem.length > 0 && (
              <>
                <p className="text-3xl font-bold leading-[1.8]" style={{ color: '#765538' }}>
                  {topAchievement.poem[0]}
                </p>
                {topAchievement.poem.length > 1 && (
                  <p className="text-xl mt-1" style={{ color: '#4f453d' }}>
                    {topAchievement.poem.slice(1).join('，')}
                  </p>
                )}
                <p className="text-sm mt-2 tracking-wider" style={{ color: '#81756b' }}>
                  {topAchievement.poemSource}
                </p>
              </>
            )}
          </div>
          {/* 苏轼印章 */}
          <div className="shrink-0 w-16 h-16 flex items-center justify-center border-2"
            style={{
              borderColor: '#ba1a1a',
              color: '#ba1a1a',
              writingMode: 'vertical-rl',
              fontSize: '18px',
              fontWeight: 700,
              letterSpacing: '0.15em',
              lineHeight: 1.2,
              background: 'rgba(186,26,26,0.04)',
            }}
          >
            苏轼
          </div>
        </div>

        {/* ── 5. 底部 — 正常文档流，不再 absolute ── */}
        <div className="mt-auto px-8 py-6 flex items-center justify-between shrink-0"
          style={{ background: 'rgba(236,224,217,0.4)', borderTop: '1px solid rgba(211,196,185,0.3)' }}
        >
          {/* 左侧：记录时间 + 访问典藉 */}
          <div className="flex items-center gap-4">
            <div>
              <p className="text-[10px] tracking-widest uppercase" style={{ color: '#81756b' }}>记录时间</p>
              <p className="text-sm font-medium" style={{ color: '#4f453d' }}>{chineseDate}</p>
            </div>
            <div className="h-8 w-px" style={{ background: 'rgba(211,196,185,0.4)' }} />
            <div>
              <p className="text-[10px] tracking-widest uppercase" style={{ color: '#81756b' }}>访问典藉</p>
              <a className="text-sm font-bold hover:underline" style={{ color: '#7f5539' }}
                href="https://su-shi.starfluxes.com"
                target="_blank"
                rel="noopener noreferrer"
              >
                su-shi.starfluxes.com
              </a>
            </div>
          </div>
          {/* 右侧：QR码 */}
          <div className="flex flex-col items-center gap-1 shrink-0">
            <div className="p-2 bg-white border shadow-sm" style={{ borderColor: '#d3c4b9' }}>
              <div ref={qrcodeRef} />
            </div>
            <span className="text-[10px] font-bold tracking-tighter" style={{ color: '#d3c4b9' }}>扫码同游</span>
          </div>
        </div>

        {/* 装饰性「詩」水印 */}
        <div className="absolute top-1/2 -right-8 opacity-[0.03] pointer-events-none rotate-12 select-none">
          <span className="text-[200px]" style={{ color: '#765538' }}>詩</span>
        </div>
      </div>
    );
  }
);

export default AchievementSharePoster;
