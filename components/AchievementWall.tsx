/**
 * 成就墙组件 v3.0 — 亮色高级质感
 * 四种状态：unlocked / near / inprogress / locked
 * 插画 PNG 作为 background-image + 渐变遮罩
 * 解锁动效 + 分享卡片生成
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
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareImageUrl, setShareImageUrl] = useState<string>('');
  const [flippingId, setFlippingId] = useState<string | null>(null);
  const shareCardRef = useRef<HTMLDivElement>(null);

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

  // 生成分享海报
  const handleGenerateShare = useCallback(async (ach: Achievement) => {
    setSelectedAchievement(ach);
    setShowShareModal(true);
    setShareImageUrl('');

    // 等待 DOM 渲染后截图（双重 rAF 确保渲染完成）
    requestAnimationFrame(() => {
      requestAnimationFrame(async () => {
        const node = shareCardRef.current;
        if (!node) return;
        try {
          const html2canvas = (await import('html2canvas')).default;
          const canvas = await html2canvas(node, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff',
          });
          setShareImageUrl(canvas.toDataURL('image/png'));
        } catch (err) {
          console.error('生成分享图失败:', err);
        }
      });
    });
  }, []);

  const handleDownload = useCallback(() => {
    if (!shareImageUrl) return;
    const a = document.createElement('a');
    a.href = shareImageUrl;
    a.download = `行吟山河成就_${selectedAchievement?.name || ''}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [shareImageUrl, selectedAchievement]);

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

      {/* 分享卡片 Modal */}
      {showShareModal && selectedAchievement && (
        <ShareModal
          achievement={selectedAchievement}
          imageUrl={shareImageUrl}
          shareCardRef={shareCardRef}
          checkinPlaces={checkinPlaces}
          unlockedCount={unlockedAchievements.length}
          totalPlaces={places.length}
          onClose={() => { setShowShareModal(false); setShareImageUrl(''); setSelectedAchievement(null); }}
          onDownload={handleDownload}
        />
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

// ===== 分享卡片 Modal =====
interface ShareModalProps {
  achievement: Achievement;
  imageUrl: string;
  shareCardRef: React.RefObject<HTMLDivElement>;
  checkinPlaces: { placeId: string; placeName: string }[];
  unlockedCount: number;
  totalPlaces: number;
  onClose: () => void;
  onDownload: () => void;
}

function ShareModal({
  achievement,
  imageUrl,
  shareCardRef,
  checkinPlaces,
  unlockedCount,
  totalPlaces,
  onClose,
  onDownload,
}: ShareModalProps) {
  const tierLabel = achievement.tier === 'gold' ? '金级成就解锁' : achievement.tier === 'silver' ? '银级成就解锁' : '铜级成就解锁';
  const imagePath = ACHIEVEMENT_IMAGES[achievement.icon];
  const progressPct = totalPlaces > 0 ? ((checkinPlaces.length / totalPlaces) * 100).toFixed(1) : '0';
  const placeNames = checkinPlaces.slice(0, 5).map(c => c.placeName);
  const today = new Date();
  const dateStr = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`;

  // 诗句分行 — 按标点自然断句
  const poemLines = achievement.poem.split(/[，。！？；]/).filter(Boolean);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />

      <div className="relative bg-stone-900 rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-stone-700">
          <h2 className="text-lg font-semibold text-white font-wenkai">{achievement.name}</h2>
          <button onClick={onClose} className="text-stone-400 hover:text-white p-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 预览图 */}
        <div className="p-4 bg-stone-800/50 flex justify-center">
          {imageUrl ? (
            <img src={imageUrl} alt={achievement.name} className="max-w-full max-h-[60vh] object-contain rounded-lg shadow-lg" />
          ) : (
            <div className="text-stone-400 text-sm py-8">生成中...</div>
          )}
        </div>

        {/* 底部操作 */}
        <div className="p-4 border-t border-stone-700 flex gap-3">
          <button onClick={onClose} className="flex-1 px-4 py-2.5 bg-stone-700 hover:bg-stone-600 text-white rounded-lg transition-colors text-sm">
            关闭
          </button>
          <button
            onClick={onDownload}
            disabled={!imageUrl}
            className="flex-1 px-4 py-2.5 bg-[#2a6e3a] hover:bg-[#2a6e3a]/90 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 text-sm"
          >
            保存图片
          </button>
        </div>
      </div>

      {/* 隐藏的分享卡片 DOM（供 html2canvas 截图） */}
      <div
        ref={shareCardRef}
        id="share-card-node"
        style={{ position: 'absolute', left: -9999, top: 0, width: 375, height: 667 }}
      >
        <div style={{ width: 375, height: 667, background: '#fff', borderRadius: 14, border: '1px solid #e8e0d4', overflow: 'hidden', fontFamily: "'STSong','SimSun','Noto Serif SC',serif" }}>
          {/* 黑色头部 */}
          <div style={{ background: '#1a1612', padding: '16px 18px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 13, fontWeight: 500, color: '#c8a060', letterSpacing: '0.12em' }}>行 吟 山 河</span>
            <span style={{ fontSize: 10, color: '#8a6a40', letterSpacing: '0.05em', border: '1px solid #3a2e18', padding: '2px 7px', borderRadius: 3 }}>{tierLabel}</span>
          </div>

          {/* 主体 */}
          <div style={{ padding: '20px 18px' }}>
            {/* 徽章 + 名称 */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 18 }}>
              <div
                style={{
                  width: 64, height: 64, borderRadius: '50%', border: '2px solid #2a6e3a',
                  backgroundImage: `url(${imagePath})`, backgroundSize: 'cover', backgroundPosition: 'center top',
                  flexShrink: 0, backgroundColor: '#f0f8f2',
                }}
              />
              <div>
                <div style={{ fontSize: 20, fontWeight: 500, color: '#1a1612', letterSpacing: '0.06em', marginBottom: 4, fontFamily: "'STSong','SimSun','Noto Serif SC',serif" }}>{achievement.name}</div>
                <div style={{ fontSize: 12, color: '#8a8070' }}>{achievement.desc}</div>
              </div>
            </div>

            {/* 分割线 */}
            <div style={{ height: 1, background: '#f0ece4', marginBottom: 16 }} />

            {/* 诗句 */}
            <div style={{ textAlign: 'center', padding: '0 8px', marginBottom: 18 }}>
              {poemLines.map((line, i) => (
                <div key={i} style={{ fontSize: 16, color: '#2a2018', lineHeight: 2.2, letterSpacing: '0.15em' }}>{line}</div>
              ))}
              <div style={{ fontSize: 11, color: '#b0a890', marginTop: 4, letterSpacing: '0.06em' }}>{achievement.poemSrc}</div>
            </div>

            {/* 统计 */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', border: '1px solid #eee8de', borderRadius: 8, overflow: 'hidden', marginBottom: 14 }}>
              <div style={{ padding: '10px 0', textAlign: 'center', borderRight: '1px solid #eee8de' }}>
                <div style={{ fontSize: 18, fontWeight: 500, color: '#1a1612' }}>{checkinPlaces.length}</div>
                <div style={{ fontSize: 9, color: '#b0a890', marginTop: 2, letterSpacing: '0.04em' }}>打卡地点</div>
              </div>
              <div style={{ padding: '10px 0', textAlign: 'center', borderRight: '1px solid #eee8de' }}>
                <div style={{ fontSize: 18, fontWeight: 500, color: '#1a1612' }}>{unlockedCount}</div>
                <div style={{ fontSize: 9, color: '#b0a890', marginTop: 2, letterSpacing: '0.04em' }}>解锁成就</div>
              </div>
              <div style={{ padding: '10px 0', textAlign: 'center' }}>
                <div style={{ fontSize: 18, fontWeight: 500, color: '#1a1612' }}>{progressPct}%</div>
                <div style={{ fontSize: 9, color: '#b0a890', marginTop: 2, letterSpacing: '0.04em' }}>苏途进度</div>
              </div>
            </div>

            {/* 地点标签 */}
            <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginBottom: 14 }}>
              {placeNames.map(name => (
                <span key={name} style={{ background: '#f4f0ea', border: '1px solid #e8e0d4', borderRadius: 3, padding: '3px 8px', fontSize: 10, color: '#6a6050' }}>{name}</span>
              ))}
            </div>

            {/* 底部 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              <div>
                <div style={{ fontSize: 10, color: '#c0b8a8', lineHeight: 1.7 }}>{dateStr}</div>
                <div style={{ fontSize: 9, color: '#d0c8b8' }}>su-shi.starfluxes.com</div>
              </div>
              <div style={{ width: 40, height: 40, background: '#f4f0ea', borderRadius: 4, display: 'grid', gridTemplateColumns: 'repeat(5, 6px)', gridTemplateRows: 'repeat(5, 6px)', gap: 1, padding: 4 }}>
                {[1,1,1,0,1, 1,0,1,1,0, 1,1,0,1,1, 0,1,1,0,1, 1,0,1,1,0].map((v, i) => (
                  <div key={i} style={{ width: 6, height: 6, borderRadius: 1, background: v ? '#2a2018' : 'transparent' }} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
