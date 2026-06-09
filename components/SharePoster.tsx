/**
 * 分享海报组件 v2.0
 * 按规格：750×1080px 竖版，宣纸色背景
 * 支持：成就分享、打卡分享、合集分享
 * 技术：html2canvas 截图 → 预览 → 保存/分享
 */

'use client';

import { useState, useCallback } from 'react';
import { useSuShiStore } from '@/lib/store';
import { achievements } from '@/lib/achievements';
import { achievementIconsHD } from '@/lib/icons';
import {
  generateShareImage,
  saveImageToAlbum,
  nativeShare,
  generateShareText,
  copyToClipboard,
} from '@/lib/sharePoster';
import type { Achievement } from '@/lib/achievements';

export type ShareType = 'achievement' | 'checkin' | 'collection';

interface SharePosterProps {
  type: ShareType;
  achievement?: Achievement;
  placeName?: string;
  subtitle?: string;   // 如 "东坡居士 · 1080–1084"
  poem?: string;       // 代表诗句
  poemSrc?: string;    // 诗句出处
  onClose?: () => void;
}

export default function SharePoster({
  type,
  achievement,
  placeName,
  subtitle,
  poem,
  poemSrc,
  onClose,
}: SharePosterProps) {
  const { checkinPlaces, unlockedAchievements } = useSuShiStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);

  const checkinCount = checkinPlaces.length;
  const achievementCount = unlockedAchievements.length;
  const totalAchievements = achievements.length;

  // 当前打卡日期
  const today = new Date();
  const dateStr = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

  const getShareData = useCallback(() => {
    switch (type) {
      case 'achievement':
        return {
          title: achievement?.name || '成就解锁',
          text: generateShareText('achievement', { name: achievement?.name }),
          posterId: 'share-poster-achievement',
        };
      case 'checkin':
        return {
          title: `打卡${placeName}`,
          text: generateShareText('checkin', { name: placeName }),
          posterId: 'share-poster-checkin',
        };
      case 'collection':
        return {
          title: '我的成就合集',
          text: generateShareText('collection', {
            checkinCount,
            achievementCount,
            totalAchievements,
          }),
          posterId: 'share-poster-collection',
        };
      default:
        return { title: '行吟山河', text: '行吟山河 · 读苏轼 游神州', posterId: 'share-poster' };
    }
  }, [type, achievement, placeName, checkinCount, achievementCount, totalAchievements]);

  // 生成海报并显示预览
  const handleGenerate = useCallback(async () => {
    const shareData = getShareData();
    setIsGenerating(true);

    try {
      const base64 = await generateShareImage(shareData.posterId);
      if (!base64) {
        alert('生成海报失败，请重试');
        return;
      }
      setPreviewUrl(base64);
    } catch (error) {
      console.error('生成海报失败:', error);
      alert('生成海报失败，请重试');
    } finally {
      setIsGenerating(false);
    }
  }, [getShareData]);

  // 保存图片
  const handleSave = useCallback(async () => {
    if (!previewUrl) return;
    try {
      await saveImageToAlbum(previewUrl);
      await copyToClipboard(getShareData().text);
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        setPreviewUrl(null);
        onClose?.();
      }, 2000);
    } catch (error) {
      console.error('保存失败:', error);
      alert('保存失败，请长按图片保存');
    }
  }, [previewUrl, getShareData, onClose]);

  // 系统分享
  const handleNativeShare = useCallback(async () => {
    if (!previewUrl) return;
    try {
      const shareData = getShareData();
      await nativeShare(shareData.title, shareData.text, previewUrl);
    } catch {
      // 不支持系统分享，忽略
    }
  }, [previewUrl, getShareData]);

  // ===== 海报 DOM 模板（750×1080px，html2canvas 截图用） =====

  // 通用底部
  const PosterFooter = () => (
    <div style={{ position: 'absolute', bottom: 40, left: 0, right: 0, textAlign: 'center' }}>
      <div style={{
        width: 80, height: 80, margin: '0 auto 12px',
        background: '#E8E0D4', borderRadius: 8,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 12, color: '#999',
      }}>
        二维码
      </div>
      <p style={{ fontSize: 18, color: '#8B7355', letterSpacing: '0.1em' }}>
        扫码追随苏轼足迹
      </p>
      <p style={{ fontSize: 14, color: '#B8A88A', marginTop: 4 }}>
        su-shi.starfluxes.com
      </p>
    </div>
  );

  // 成就分享海报
  const renderAchievementPoster = () => {
    if (!achievement) return null;
    return (
      <div id="share-poster-achievement" style={{ width: 750, height: 1080, position: 'absolute', left: -9999, top: 0 }}>
        <div style={{
          width: 750, height: 1080, background: '#F5F0E8',
          padding: '60px 50px', display: 'flex', flexDirection: 'column', alignItems: 'center',
          fontFamily: '"Noto Serif SC", serif',
        }}>
          {/* 顶部 logo */}
          <p style={{ fontSize: 22, color: '#C9973A', letterSpacing: '0.15em', marginBottom: 40 }}>
            行吟山河 · 读苏轼 游神州
          </p>

          {/* 成就卡主体 */}
          <div style={{
            width: 600, borderRadius: 20, padding: '50px 40px',
            border: `2px solid ${achievement.color}80`,
            background: '#fff',
            boxShadow: `0 8px 30px ${achievement.glow}`,
            textAlign: 'center',
          }}>
            <div style={{ width: 120, height: 120, margin: '0 auto 24px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {achievement.icon && achievementIconsHD[achievement.icon] ? (
                <img src={achievementIconsHD[achievement.icon]} alt={achievement.name} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              ) : (
                <span style={{ fontSize: 80, color: achievement.color }}>{achievement.emoji}</span>
              )}
            </div>
            <h3 style={{ fontSize: 36, fontWeight: 700, color: achievement.color, marginBottom: 12 }}>
              {achievement.name}
            </h3>
            <p style={{ fontSize: 20, color: '#666', lineHeight: 1.6, marginBottom: 24 }}>
              {achievement.desc}
            </p>
            <div style={{ borderTop: '1px solid #f0ebe3', paddingTop: 20 }}>
              <p style={{ fontSize: 22, color: '#555', fontStyle: 'italic' }}>
                「{achievement.poem}」
              </p>
              <p style={{ fontSize: 16, color: '#999', marginTop: 8 }}>
                ——{achievement.poemSrc}
              </p>
            </div>
          </div>

          {/* 用户数据 */}
          <div style={{ textAlign: 'center', marginTop: 30, fontSize: 20, color: '#666' }}>
            <p>已打卡 {checkinCount} 处 · 已解锁 {achievementCount}/{totalAchievements} 项成就</p>
          </div>

          <PosterFooter />
        </div>
      </div>
    );
  };

  // 打卡分享海报
  const renderCheckinPoster = () => (
    <div id="share-poster-checkin" style={{ width: 750, height: 1080, position: 'absolute', left: -9999, top: 0 }}>
      <div style={{
        width: 750, height: 1080, background: '#F5F0E8',
        padding: '60px 50px', display: 'flex', flexDirection: 'column', alignItems: 'center',
        fontFamily: '"Noto Serif SC", serif',
      }}>
        {/* 顶部 logo */}
        <p style={{ fontSize: 22, color: '#C9973A', letterSpacing: '0.15em', marginBottom: 50 }}>
          行吟山河 · 读苏轼 游神州
        </p>

        {/* 地点大字 */}
        <h2 style={{
          fontSize: 64, fontWeight: 700, color: '#1A1410',
          letterSpacing: '0.08em', marginBottom: 16,
          textShadow: '0 2px 4px rgba(0,0,0,0.08)',
        }}>
          {placeName || '打卡成功'}
        </h2>

        {/* 副标题 */}
        {subtitle && (
          <p style={{ fontSize: 22, color: '#8B7355', letterSpacing: '0.06em', marginBottom: 40 }}>
            {subtitle}
          </p>
        )}

        {/* 诗句（竖排效果用大字横排模拟） */}
        {poem && (
          <div style={{
            padding: '30px 40px', marginBottom: 40,
            borderLeft: '3px solid #C9973A',
            background: 'rgba(201, 151, 58, 0.06)',
          }}>
            <p style={{ fontSize: 28, color: '#3D342E', lineHeight: 1.8, letterSpacing: '0.06em' }}>
              {poem}
            </p>
            {poemSrc && (
              <p style={{ fontSize: 16, color: '#999', marginTop: 12 }}>
                ——{poemSrc}
              </p>
            )}
          </div>
        )}

        {/* 打卡标签 */}
        <div style={{
          display: 'flex', gap: 12, marginBottom: 30,
        }}>
          <span style={{
            fontSize: 16, padding: '6px 20px', borderRadius: 20,
            background: '#EAF3DE', color: '#1E4A2A',
          }}>
            到此一游
          </span>
          <span style={{
            fontSize: 16, padding: '6px 20px', borderRadius: 20,
            background: 'rgba(201, 151, 58, 0.12)', color: '#8B6914',
          }}>
            第 {checkinCount} 处
          </span>
        </div>

        {/* 日期 */}
        <p style={{ fontSize: 18, color: '#B8A88A', letterSpacing: '0.08em' }}>
          {dateStr}
        </p>

        <PosterFooter />
      </div>
    </div>
  );

  // 成就合集海报
  const renderCollectionPoster = () => {
    const unlockedItems = achievements.filter(a => unlockedAchievements.includes(a.id));
    return (
      <div id="share-poster-collection" style={{ width: 750, height: 1080, position: 'absolute', left: -9999, top: 0 }}>
        <div style={{
          width: 750, height: 1080, background: '#F5F0E8',
          padding: '60px 50px', display: 'flex', flexDirection: 'column',
          fontFamily: '"Noto Serif SC", serif',
        }}>
          {/* 顶部 */}
          <p style={{ fontSize: 22, color: '#C9973A', letterSpacing: '0.15em', textAlign: 'center', marginBottom: 30 }}>
            行吟山河 · 读苏轼 游神州
          </p>

          <div style={{ textAlign: 'center', marginBottom: 30 }}>
            <h3 style={{ fontSize: 32, fontWeight: 700, color: '#1A1410', marginBottom: 8 }}>我的成就合集</h3>
            <p style={{ fontSize: 18, color: '#8B7355' }}>累计解锁 {achievementCount}/{totalAchievements} 项成就</p>
          </div>

          {/* 成就网格 */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12,
            marginBottom: 30,
          }}>
            {unlockedItems.slice(0, 10).map((ach) => (
              <div key={ach.id} style={{
                aspectRatio: '1', borderRadius: 12,
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                background: ach.color + '20', border: `1px solid ${ach.color}40`,
                padding: 8,
              }}>
                {ach.icon && achievementIconsHD[ach.icon] ? (
                  <img src={achievementIconsHD[ach.icon]} alt={ach.name} style={{ width: 40, height: 40, objectFit: 'contain' }} />
                ) : (
                  <span style={{ fontSize: 32 }}>{ach.emoji}</span>
                )}
                <p style={{ fontSize: 10, color: '#666', marginTop: 4, textAlign: 'center' }}>{ach.name}</p>
              </div>
            ))}
            {Array.from({ length: Math.max(0, 10 - unlockedItems.length) }).map((_, i) => (
              <div key={`empty-${i}`} style={{
                aspectRatio: '1', borderRadius: 12,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: '#E8E0D4',
              }}>
                <span style={{ fontSize: 28, color: '#C0B8A8' }}>🔒</span>
              </div>
            ))}
          </div>

          {/* 统计 */}
          <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 60 }}>
              <div>
                <p style={{ fontSize: 40, fontWeight: 700, color: '#C9973A' }}>{checkinCount}</p>
                <p style={{ fontSize: 14, color: '#8B7355' }}>打卡地点</p>
              </div>
              <div style={{ width: 1, background: '#D4C8B8' }} />
              <div>
                <p style={{ fontSize: 40, fontWeight: 700, color: '#C9973A' }}>{achievementCount}</p>
                <p style={{ fontSize: 14, color: '#8B7355' }}>解锁成就</p>
              </div>
            </div>
          </div>

          <PosterFooter />
        </div>
      </div>
    );
  };

  return (
    <>
      {/* 隐藏的海报容器（html2canvas 截图用） */}
      {type === 'achievement' && renderAchievementPoster()}
      {type === 'checkin' && renderCheckinPoster()}
      {type === 'collection' && renderCollectionPoster()}

      {/* 触发按钮 */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating}
        className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-wenkai transition-all duration-300"
        style={{
          backgroundColor: isGenerating ? '#9CA3AF' : '#C9973A',
          color: '#fff',
          fontSize: '12px',
        }}
      >
        {isGenerating ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            生成中...
          </>
        ) : (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            生成分享海报
          </>
        )}
      </button>

      {/* 预览 Modal */}
      {previewUrl && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          style={{ background: 'rgba(0,0,0,0.7)' }}
          onClick={() => setPreviewUrl(null)}
        >
          <div
            className="relative max-w-[90vw] max-h-[80vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={previewUrl}
              alt="分享海报预览"
              style={{ maxWidth: '100%', maxHeight: '70vh', borderRadius: 12 }}
            />
            <div className="flex gap-3 justify-center mt-4">
              <button
                onClick={handleSave}
                className="px-6 py-3 rounded-xl font-wenkai text-white text-sm"
                style={{ background: '#C9973A' }}
              >
                保存图片
              </button>
              {typeof navigator !== 'undefined' && 'share' in navigator && (
                <button
                  onClick={handleNativeShare}
                  className="px-6 py-3 rounded-xl font-wenkai text-sm border"
                  style={{ borderColor: '#C9973A', color: '#C9973A', background: 'transparent' }}
                >
                  分享
                </button>
              )}
              <button
                onClick={() => setPreviewUrl(null)}
                className="px-6 py-3 rounded-xl font-wenkai text-sm"
                style={{ background: '#666', color: '#fff' }}
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 成功提示 */}
      {showSuccess && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
          <div className="bg-white rounded-2xl p-6 text-center max-w-sm mx-4">
            <div className="text-4xl mb-3">🎉</div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">分享成功</h3>
            <p className="text-sm text-gray-500">海报已保存到相册，文案已复制</p>
          </div>
        </div>
      )}
    </>
  );
}
