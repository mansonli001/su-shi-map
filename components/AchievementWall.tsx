/**
 * 成就墙组件 v4.0 — 文人手稿风格
 * 四种状态：unlocked / near / inprogress / locked
 * 插画 PNG 作为 background-image + 渐变遮罩
 * 解锁动效 + AchievementModal 弹窗 + AchievementSharePoster 海报
 */

'use client';

import { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import {
  achievements,
  evaluateAchievements,
  ACHIEVEMENT_IMAGES,
  getAchievementStatus,
  type Achievement,
  type AchievementStatus,
} from '@/lib/achievements';
import { useSuShiStore } from '@/lib/store';
import AchievementModal from '@/components/achievements/AchievementModal';
import AchievementSharePoster from '@/components/achievements/AchievementSharePoster';

// 分类配置 — 用中文符号替代 emoji
const CATEGORIES = [
  { id: 'grow', name: '成长阶梯', symbol: '拾' },
  { id: 'banish', name: '贬谪专题', symbol: '谪' },
  { id: 'jiangnan', name: '江南专题', symbol: '舟' },
  { id: 'poem', name: '诗词珍藏', symbol: '诗' },
  { id: 'secret', name: '隐秘彩蛋', symbol: '隐' },
];

// 品级标签样式
const TIER_STYLES: Record<string, { label: string; className: string }> = {
  bronze: { label: '铜', className: 'tier-cu' },
  silver: { label: '银', className: 'tier-ag' },
  gold: { label: '金', className: 'tier-gold' },
};

// 进度条颜色
const PROGRESS_COLORS: Record<AchievementStatus, string> = {
  unlocked: '#2a6e3a',
  near: '#c8820a',
  inprogress: '#b8b0a0',
  locked: '#ccc8c0',
};

export default function AchievementWall() {
  const { unlockedAchievements, checkinPlaces, places, favoritePoems, lastUnlockedAchievement, setLastUnlockedAchievement } = useSuShiStore();
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null);
  const [showAchievementModal, setShowAchievementModal] = useState(false);
  const [showSharePoster, setShowSharePoster] = useState(false);
  const [flippingId, setFlippingId] = useState<string | null>(null);
  const posterRef = useRef<HTMLDivElement>(null);

  // 海报缩放：根据视口宽度动态计算 --poster-scale
  useEffect(() => {
    if (!showSharePoster) return;
    const updateScale = () => {
      const vw = window.innerWidth;
      // 海报固定 750px 宽，小屏缩放
      const scale = Math.min(1, (vw - 24) / 750); // 24px = p-3 两侧
      document.documentElement.style.setProperty('--poster-scale', String(scale));
    };
    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, [showSharePoster]);

  // 计算所有成就进度
  const achievementProgress = useMemo(() => {
    const checkedIds = new Set(checkinPlaces.map(c => c.placeId));
    const favoritePoemIds = new Set(favoritePoems.map(p => p.poemId));
    const checkinDates = checkinPlaces.map(c => new Date(c.checkinAt));
    const { progress } = evaluateAchievements(checkedIds, places, favoritePoemIds, checkinDates);
    return progress;
  }, [checkinPlaces, places, favoritePoems]);

  // 按分类分组成就
  const achievementsByCategory = useMemo(() => {
    const grouped: Record<string, Achievement[]> = {};
    CATEGORIES.forEach(cat => {
      grouped[cat.id] = achievements.filter(ach => ach.category === cat.id);
    });
    return grouped;
  }, []);

  // 解锁动效触发
  useEffect(() => {
    if (!lastUnlockedAchievement) return;
    const ach = lastUnlockedAchievement;
    setFlippingId(ach.id);

    const timer = setTimeout(() => {
      setFlippingId(null);
      setLastUnlockedAchievement(null);
    }, ach.tier === 'gold' ? 2500 : ach.tier === 'silver' ? 2800 : 700);
    return () => clearTimeout(timer);
  }, [lastUnlockedAchievement, setLastUnlockedAchievement]);

  // 打开成就卡弹窗
  const handleGenerateShare = useCallback((ach: Achievement) => {
    setSelectedAchievement(ach);
    setShowAchievementModal(true);
  }, []);

  // 保存分享海报
  const handleSavePoster = useCallback(async () => {
    if (!posterRef.current) return;
    try {
      const html2canvas = (await import('html2canvas')).default;
      const canvas = await html2canvas(posterRef.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#fff8f5',
      });
      const link = document.createElement('a');
      link.download = '行吟山河-成就合集.png';
      link.href = canvas.toDataURL();
      link.click();
    } catch (err) {
      console.error('生成分享海报失败:', err);
    }
  }, []);

  const handleCardClick = (ach: Achievement, status: AchievementStatus) => {
    if (ach.isHidden && status === 'locked') return;
    if (status === 'unlocked') {
      handleGenerateShare(ach);
    }
  };

  return (
    <>
      {/* 银级 Toast */}
      {lastUnlockedAchievement && lastUnlockedAchievement.tier === 'silver' && (
        <SilverToast achievement={lastUnlockedAchievement} />
      )}

      {/* 金级全屏揭幕 */}
      {lastUnlockedAchievement && lastUnlockedAchievement.tier === 'gold' && (
        <GoldReveal achievement={lastUnlockedAchievement} />
      )}

      <div className="bg-[#f0ece4] rounded-2xl p-4">
      {/* 分享海报入口 */}
      <div className="flex justify-end mb-4">
        <button
          onClick={() => setShowSharePoster(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-wenkai transition-colors"
          style={{ background: 'linear-gradient(135deg, #75593a 0%, #b08968 100%)', color: '#ffffff' }}
        >
          <span className="material-symbols-outlined text-base"
            style={{ fontVariationSettings: "'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24" }}
          >
            photo_library
          </span>
          生成分享海报
        </button>
      </div>

      {CATEGORIES.map((category) => {
        const categoryAchievements = achievementsByCategory[category.id];
        if (!categoryAchievements || categoryAchievements.length === 0) return null;

        const catUnlocked = categoryAchievements.filter(a => unlockedAchievements.includes(a.id)).length;

        return (
          <div key={category.id} className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-6 h-6 rounded bg-[#e8e0d4] flex items-center justify-center text-[11px] font-medium text-[#7a7060] font-wenkai shrink-0">
                {category.symbol}
              </span>
              <h2 className="text-sm font-medium font-wenkai text-[#9a9080] tracking-wider">
                {category.name}
              </h2>
              <span className="text-xs text-[#b0a890]">
                {catUnlocked}/{categoryAchievements.length}
              </span>
            </div>

            <div className={`grid gap-2.5 ${
              categoryAchievements.length === 1 ? 'grid-cols-1' : 'grid-cols-2'
            }`}>
              {categoryAchievements.map((ach) => {
                const isUnlocked = unlockedAchievements.includes(ach.id);
                const p = achievementProgress[ach.id];
                const current = p?.current || 0;
                const target = p?.target || 0;
                const status = isUnlocked ? 'unlocked' : getAchievementStatus(current, target);
                const progress = target > 0 ? Math.min((current / target) * 100, 100) : 0;
                const isHiddenAndLocked = ach.isHidden && !isUnlocked;
                const isFlipping = flippingId === ach.id;
                const tierStyle = TIER_STYLES[ach.tier] || TIER_STYLES.bronze;
                const imagePath = ACHIEVEMENT_IMAGES[ach.icon];
                const isSingle = categoryAchievements.length === 1;

                return (
                  <div
                    key={ach.id}
                    onClick={() => handleCardClick(ach, status)}
                    className={`
                      relative rounded-xl overflow-hidden cursor-pointer
                      transition-transform duration-150 active:scale-[0.97]
                      ${isFlipping ? 'ac-flipping' : ''}
                      ${status === 'unlocked' ? 'bg-white border-[1.5px] border-[#d4e8d8]' : ''}
                      ${status === 'near' ? 'bg-[#fdf5e6] border-[1.5px] border-[#e8c060]' : ''}
                      ${status === 'inprogress' ? 'bg-[#f4f0ea] border border-[#ddd8ce]' : ''}
                      ${status === 'locked' ? 'bg-[#f0ece4] border border-[#ddd8ce]' : ''}
                    `}
                    style={{ aspectRatio: isSingle ? '1.2' : '0.78' }}
                  >
                    {/* 插画背景层 */}
                    {imagePath && !isHiddenAndLocked && (
                      <div
                        className="absolute inset-0"
                        style={{
                          backgroundImage: `url(${imagePath})`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center top',
                          filter: status === 'unlocked' ? 'none' : 'grayscale(1) brightness(0.5) contrast(0.8)',
                        }}
                      />
                    )}

                    {/* 无插画兜底：显示成就名首字 */}
                    {!imagePath && !isHiddenAndLocked && (
                      <div className="absolute inset-0 bg-[#f4f0ea] flex items-center justify-center">
                        <span className={`font-wenkai text-[#c8c0b0] ${isSingle ? 'text-6xl' : 'text-5xl'}`}>
                          {ach.name[0]}
                        </span>
                      </div>
                    )}

                    {/* 隐藏成就：问号背景 */}
                    {isHiddenAndLocked && (
                      <div className="absolute inset-0 bg-[#f0ece4] flex items-center justify-center">
                        <span className="text-4xl font-wenkai opacity-20 text-[#7a7060]">隐</span>
                      </div>
                    )}

                    {/* 渐变遮罩层 */}
                    <div
                      className="absolute inset-0"
                      style={{
                        background: status === 'unlocked'
                          ? 'linear-gradient(to top, rgba(255,255,255,0.97) 0%, rgba(255,255,255,0.6) 45%, transparent 100%)'
                          : status === 'near'
                            ? 'linear-gradient(to top, rgba(253,245,230,0.97) 0%, rgba(253,245,230,0.7) 50%, transparent 100%)'
                            : 'linear-gradient(to top, rgba(240,235,226,0.97) 0%, rgba(240,235,226,0.7) 50%, transparent 100%)',
                      }}
                    />

                    {/* 右上角等级标签 */}
                    <span
                      className={`absolute top-2 right-2 z-10 rounded font-medium tracking-wider border ${tierStyle.className} ${
                        isSingle ? 'text-[11px] px-2 py-1' : 'text-[9px] px-1.5 py-0.5'
                      }`}
                    >
                      {tierStyle.label}
                    </span>

                    {/* 左上角已解锁勾标 */}
                    {status === 'unlocked' && (
                      <div className={`absolute top-2 left-2 z-10 rounded-full bg-[#2a6e3a] flex items-center justify-center ${
                        isSingle ? 'w-6 h-6' : 'w-5 h-5'
                      }`}>
                        <div
                          className={`border-r-2 border-b-2 border-white ${
                            isSingle ? 'w-3 h-3' : 'w-2.5 h-2.5'
                          }`}
                          style={{ transform: 'rotate(45deg) translate(-1px,-1px)' }}
                        />
                      </div>
                    )}

                    {/* 底部信息层 */}
                    <div className={`absolute inset-x-0 bottom-0 z-10 ${isSingle ? 'p-4' : 'p-2.5'}`}>
                      {/* 成就名 */}
                      <p
                        className={`font-medium mb-0.5 truncate font-wenkai ${
                          isSingle ? 'text-[16px]' : 'text-[13px]'
                        } ${status === 'unlocked' ? 'text-[#1a1612]' : 'text-[#7a7060]'}`}
                      >
                        {ach.name}
                      </p>

                      {/* 解锁条件 */}
                      <p
                        className={`mb-1.5 truncate ${
                          isSingle ? 'text-[12px]' : 'text-[10px]'
                        } ${status === 'unlocked' ? 'text-[#8a6a40]' : 'text-[#aaa098]'}`}
                      >
                        {status === 'unlocked'
                          ? `${current}处足迹 · 已解锁`
                          : ach.desc}
                      </p>

                      {/* 进度行 */}
                      {status !== 'unlocked' && !isHiddenAndLocked && (
                        <div className="flex justify-between items-center mb-1">
                          <span
                            className={`font-medium ${
                              isSingle ? 'text-[11px]' : 'text-[9px]'
                            } ${status === 'near' ? 'text-[#b07820]' : 'text-[#aaa098]'}`}
                          >
                            {current} / {target}
                          </span>
                          {status === 'near' && (
                            <span className={`text-[#b07820] font-medium ${isSingle ? 'text-[11px]' : 'text-[9px]'}`}>差一步!</span>
                          )}
                        </div>
                      )}

                      {/* 进度条 */}
                      <div className="h-1 bg-black/[0.06] rounded-sm overflow-hidden">
                        <div
                          className="h-full rounded-sm transition-all duration-400"
                          style={{
                            width: `${progress}%`,
                            backgroundColor: PROGRESS_COLORS[status],
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      </div>

      {/* 成就卡弹窗 — 文人手稿风格 */}
      {showAchievementModal && selectedAchievement && (
        <AchievementModal
          achievement={{
            id: selectedAchievement.id,
            name: selectedAchievement.name,
            description: selectedAchievement.desc,
            tier: selectedAchievement.tier,
            imageUrl: ACHIEVEMENT_IMAGES[selectedAchievement.icon] || '/achievements/default.jpg',
            poem: selectedAchievement.poem.split(/[，。！？；]/).filter(Boolean),
            poemSource: selectedAchievement.poemSrc,
          }}
          userStats={{
            checkinCount: checkinPlaces.length,
            achievementCount: unlockedAchievements.length,
            totalAchievements: achievements.length,
            progressPercent: places.length > 0 ? Math.round((checkinPlaces.length / places.length) * 100) : 0,
          }}
          onClose={() => { setShowAchievementModal(false); setSelectedAchievement(null); }}
          onShare={() => { setShowAchievementModal(false); setShowSharePoster(true); }}
        />
      )}

      {/* 成就合集海报弹窗 — 响应式 */}
      {showSharePoster && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-end sm:justify-center p-3 sm:p-4">
          <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setShowSharePoster(false)} />
          {/* 海报容器 — 缩放适配小屏 */}
          <div className="relative z-10 flex flex-col items-center w-full max-w-[750px] max-h-[85dvh] sm:max-h-[90dvh]">
            <div className="overflow-auto overscroll-contain flex-1 w-full flex justify-center"
              style={{ scrollbarWidth: 'thin' }}
            >
              <div style={{ transform: 'scale(var(--poster-scale, 1))', transformOrigin: 'top center' }}>
                <AchievementSharePoster
                  ref={posterRef}
                  achievements={achievements.map(ach => ({
                    id: ach.id,
                    name: ach.name,
                    tier: ach.tier,
                    imageUrl: ACHIEVEMENT_IMAGES[ach.icon] || '/achievements/default.jpg',
                    poem: ach.poem.split(/[，。！？；]/).filter(Boolean),
                    poemSource: ach.poemSrc,
                    unlocked: unlockedAchievements.includes(ach.id),
                  }))}
                  userStats={{
                    checkinCount: checkinPlaces.length,
                    achievementCount: unlockedAchievements.length,
                    totalAchievements: achievements.length,
                    progressPercent: places.length > 0 ? Math.round((checkinPlaces.length / places.length) * 100) : 0,
                  }}
                />
              </div>
            </div>
            {/* 操作按钮 — 固定底部 */}
            <div className="shrink-0 flex gap-3 py-4 z-20">
              <button
                onClick={() => setShowSharePoster(false)}
                className="px-6 py-2.5 rounded-lg text-sm font-wenkai transition-colors"
                style={{ background: 'rgba(255,255,255,0.15)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)' }}
              >
                关闭
              </button>
              <button
                onClick={handleSavePoster}
                className="px-6 py-2.5 rounded-lg text-sm font-wenkai transition-colors"
                style={{ background: 'linear-gradient(135deg, #75593a 0%, #b08968 100%)', color: '#ffffff' }}
              >
                保存图片
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ===== 银级 Toast 组件 =====
function SilverToast({ achievement }: { achievement: Achievement }) {
  const [exiting, setExiting] = useState(false);
  const imagePath = ACHIEVEMENT_IMAGES[achievement.icon];

  useEffect(() => {
    const t1 = setTimeout(() => setExiting(true), 2200);
    return () => clearTimeout(t1);
  }, []);

  return (
    <div className={`fixed top-0 left-0 right-0 z-[60] ${exiting ? 'toast-out' : 'toast-in'}`}>
      <div className="bg-[#2C1810]/95 backdrop-blur-sm mx-3 mt-3 rounded-xl h-[72px] flex items-center gap-3 px-4 shadow-lg">
        <div
          className="w-10 h-10 rounded-lg shrink-0"
          style={{
            backgroundImage: `url(${imagePath})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center top',
          }}
        />
        <div className="flex-1 min-w-0">
          <p className="text-[#F5E6C8] text-sm font-medium font-wenkai truncate">{achievement.name}</p>
          <p className="text-[#B8A88A] text-xs truncate">成就解锁！{achievement.desc}</p>
        </div>
      </div>
    </div>
  );
}

// ===== 金级全屏揭幕组件 =====
function GoldReveal({ achievement }: { achievement: Achievement }) {
  const [visible, setVisible] = useState(true);
  const imagePath = ACHIEVEMENT_IMAGES[achievement.icon];
  const poemChars = achievement.poem.replace(/[，。、！？；：""''《》（）\s]/g, '').split('');

  useEffect(() => {
    const t = setTimeout(() => setVisible(false), 2500);
    return () => clearTimeout(t);
  }, []);

  if (!visible) return null;

  return (
    <div
      className="fixed inset-0 z-[70] flex items-center justify-center"
      onClick={() => setVisible(false)}
    >
      {/* 遮罩 */}
      <div
        className="absolute inset-0 bg-black"
        style={{ animation: 'reveal-fade-in 300ms ease-out forwards' }}
      />
      {/* 卡片 */}
      <div
        className="relative bg-white rounded-2xl w-[280px] overflow-hidden shadow-2xl"
        style={{ animation: 'reveal-card-pop 400ms cubic-bezier(0.34,1.56,0.64,1) forwards' }}
      >
        <div
          className="h-[200px] w-full"
          style={{
            backgroundImage: `url(${imagePath})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center top',
          }}
        />
        <div className="p-5 text-center">
          <h3 className="text-lg font-medium font-wenkai text-[#1a1612] mb-2">{achievement.name}</h3>
          <div className="text-sm font-wenkai text-[#2a2018] leading-[2.2] tracking-widest">
            {poemChars.map((char, i) => (
              <span
                key={i}
                style={{
                  animation: `char-fade-in 300ms ease-out ${i * 50}ms both`,
                }}
              >
                {char}
              </span>
            ))}
          </div>
          <p className="text-[11px] text-[#b0a890] mt-2 tracking-wider">{achievement.poemSrc}</p>
        </div>
      </div>
    </div>
  );
}


