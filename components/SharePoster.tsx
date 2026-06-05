/**
 * 分享海报组件
 * 用于生成国风分享海报，支持成就分享、打卡分享、合集分享
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
  copyToClipboard 
} from '@/lib/sharePoster';
import type { Achievement } from '@/lib/achievements';

export type ShareType = 'achievement' | 'checkin' | 'collection';

interface SharePosterProps {
  type: ShareType;
  achievement?: Achievement;
  placeName?: string;
  onClose?: () => void;
}

export default function SharePoster({ type, achievement, placeName, onClose }: SharePosterProps) {
  const { checkinPlaces, unlockedAchievements } = useSuShiStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [copied, setCopied] = useState(false);

  const checkinCount = checkinPlaces.length;
  const achievementCount = unlockedAchievements.length;
  const totalAchievements = achievements.length;

  // 获取分享数据
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
            totalAchievements 
          }),
          posterId: 'share-poster-collection',
        };
      default:
        return { title: '行吟山河', text: '行吟山河 · 读苏轼 游神州', posterId: 'share-poster' };
    }
  }, [type, achievement, placeName, checkinCount, achievementCount, totalAchievements]);

  // 处理分享
  const handleShare = useCallback(async () => {
    const shareData = getShareData();
    setIsGenerating(true);

    try {
      const base64 = await generateShareImage(shareData.posterId);
      if (!base64) {
        alert('生成海报失败，请重试');
        return;
      }

      // 保存到相册
      await saveImageToAlbum(base64);

      // 复制文案到剪贴板
      await copyToClipboard(shareData.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);

      // 显示成功提示
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        onClose?.();
      }, 2500);

      // 尝试调用系统分享（可选）
      try {
        await nativeShare(shareData.title, shareData.text, base64);
      } catch {
        // 系统分享不支持时跳过
      }
    } catch (error) {
      console.error('分享失败:', error);
      alert('分享失败，请重试');
    } finally {
      setIsGenerating(false);
    }
  }, [getShareData, onClose]);

  // 渲染成就分享海报
  const renderAchievementPoster = () => {
    if (!achievement) return null;

    return (
      <div id="share-poster-achievement" className="w-[375px] h-[667px] relative hidden">
        <div className="w-full h-full bg-[#FAF6F0] p-6 flex flex-col items-center" style={{ fontFamily: 'Noto Serif SC, serif' }}>
          {/* 顶部标题 */}
          <h2 className="text-[#C9973A] text-xl font-bold mb-6" style={{ textShadow: '0 1px 2px rgba(0,0,0,0.1)' }}>
            行吟山河 · 读苏轼 游神州
          </h2>

          {/* 成就卡主体 */}
          <div 
            className="w-[300px] rounded-xl p-6 border-2 bg-white mb-6"
            style={{ 
              borderColor: achievement.color + '80',
              boxShadow: `0 4px 15px ${achievement.glow}`
            }}
          >
            <div className="w-20 h-20 mx-auto mb-4 flex items-center justify-center">
              {achievement.icon && achievementIconsHD[achievement.icon] ? (
                <img
                  src={achievementIconsHD[achievement.icon]}
                  alt={achievement.name}
                  className="w-full h-full object-contain"
                />
              ) : (
                <span className="text-6xl" style={{ color: achievement.color }}>
                  {achievement.emoji}
                </span>
              )}
            </div>
            <h3 className="text-center text-xl font-bold mb-2" style={{ color: achievement.color }}>
              {achievement.name}
            </h3>
            <p className="text-center text-sm text-gray-500 line-clamp-2">
              {achievement.desc}
            </p>
            {/* 金句 */}
            <div className="mt-4 pt-4 border-t border-gray-100">
              <p className="text-center text-sm italic text-gray-600">
                「{achievement.poem}」
              </p>
              <p className="text-center text-xs text-gray-400 mt-1">
                ——《{achievement.poemSrc}》
              </p>
            </div>
          </div>

          {/* 用户数据 */}
          <div className="text-center mb-8">
            <p className="text-gray-600">已打卡：{checkinCount} 处</p>
            <p className="text-gray-600">已解锁成就：{achievementCount}/{totalAchievements} 项</p>
          </div>

          {/* 底部 */}
          <div className="absolute bottom-8 left-0 right-0 text-center">
            {/* 占位二维码区域 */}
            <div className="w-20 h-20 mx-auto mb-3 bg-gray-200 rounded-lg flex items-center justify-center">
              <span className="text-xs text-gray-400">二维码</span>
            </div>
            <p className="text-xs text-gray-500">扫码追随苏轼足迹</p>
          </div>
        </div>
      </div>
    );
  };

  // 渲染打卡分享海报
  const renderCheckinPoster = () => {
    return (
      <div id="share-poster-checkin" className="w-[375px] h-[667px] relative hidden">
        <div className="w-full h-full bg-[#FAF6F0] p-6 flex flex-col items-center" style={{ fontFamily: 'Noto Serif SC, serif' }}>
          {/* 顶部标题 */}
          <h2 className="text-[#C9973A] text-xl font-bold mb-6" style={{ textShadow: '0 1px 2px rgba(0,0,0,0.1)' }}>
            行吟山河 · 读苏轼 游神州
          </h2>

          {/* 打卡卡片 */}
          <div className="w-[300px] rounded-xl p-6 border-2 border-[#4A7C62] bg-white mb-6">
            <div className="text-5xl text-center mb-4" style={{ color: '#4A7C62' }}>
              ✨
            </div>
            <h3 className="text-center text-xl font-bold mb-2" style={{ color: '#4A7C62' }}>
              {placeName || '打卡成功'}
            </h3>
            <p className="text-center text-sm text-gray-500">
              与苏轼隔空相逢
            </p>
            <div className="mt-4 flex justify-center gap-2">
              <span className="text-xs px-3 py-1 rounded-full" style={{ backgroundColor: '#EAF3DE', color: '#1E4A2A' }}>
                到此一游
              </span>
            </div>
          </div>

          {/* 用户数据 */}
          <div className="text-center mb-8">
            <p className="text-gray-600">累计打卡：{checkinCount} 处</p>
            <p className="text-gray-600">已解锁成就：{achievementCount}/{totalAchievements} 项</p>
          </div>

          {/* 底部 */}
          <div className="absolute bottom-8 left-0 right-0 text-center">
            <div className="w-20 h-20 mx-auto mb-3 bg-gray-200 rounded-lg flex items-center justify-center">
              <span className="text-xs text-gray-400">二维码</span>
            </div>
            <p className="text-xs text-gray-500">扫码追随苏轼足迹</p>
          </div>
        </div>
      </div>
    );
  };

  // 渲染成就合集海报
  const renderCollectionPoster = () => {
    // 获取已解锁的成就
    const unlockedItems = achievements.filter(a => unlockedAchievements.includes(a.id));
    
    return (
      <div id="share-poster-collection" className="w-[375px] h-[667px] relative hidden">
        <div className="w-full h-full bg-[#FAF6F0] p-6 flex flex-col" style={{ fontFamily: 'Noto Serif SC, serif' }}>
          {/* 顶部标题 */}
          <h2 className="text-[#C9973A] text-xl font-bold text-center mb-4" style={{ textShadow: '0 1px 2px rgba(0,0,0,0.1)' }}>
            行吟山河 · 读苏轼 游神州
          </h2>

          {/* 成就合集标题 */}
          <div className="text-center mb-4">
            <h3 className="text-lg font-bold text-gray-800">我的成就合集</h3>
            <p className="text-sm text-gray-500">累计解锁 {achievementCount}/{totalAchievements} 项成就</p>
          </div>

          {/* 成就网格 */}
          <div className="flex-1 grid grid-cols-3 gap-2 mb-4">
            {unlockedItems.slice(0, 9).map((ach) => (
              <div 
                key={ach.id} 
                className="aspect-square rounded-lg flex flex-col items-center justify-center p-2"
                style={{ 
                  backgroundColor: ach.color + '20',
                  border: `1px solid ${ach.color}40`
                }}
              >
                {ach.icon && achievementIconsHD[ach.icon] ? (
                  <img
                    src={achievementIconsHD[ach.icon]}
                    alt={ach.name}
                    className="w-8 h-8 object-contain"
                  />
                ) : (
                  <span className="text-2xl">{ach.emoji}</span>
                )}
              </div>
            ))}
            {/* 未解锁的显示锁图标 */}
            {Array.from({ length: Math.max(0, 9 - unlockedItems.length) }).map((_, i) => (
              <div 
                key={`empty-${i}`} 
                className="aspect-square rounded-lg flex items-center justify-center bg-gray-200"
              >
                <span className="text-xl text-gray-400">🔒</span>
              </div>
            ))}
          </div>

          {/* 统计数据 */}
          <div className="text-center mb-4">
            <div className="flex justify-center gap-6">
              <div>
                <p className="text-2xl font-bold" style={{ color: '#C9973A' }}>{checkinCount}</p>
                <p className="text-xs text-gray-500">打卡地点</p>
              </div>
              <div className="w-px bg-gray-300"></div>
              <div>
                <p className="text-2xl font-bold" style={{ color: '#C9973A' }}>{achievementCount}</p>
                <p className="text-xs text-gray-500">解锁成就</p>
              </div>
            </div>
          </div>

          {/* 底部 */}
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-2 bg-gray-200 rounded-lg flex items-center justify-center">
              <span className="text-xs text-gray-400">二维码</span>
            </div>
            <p className="text-xs text-gray-500">扫码追随苏轼足迹</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* 隐藏的海报容器 */}
      {type === 'achievement' && renderAchievementPoster()}
      {type === 'checkin' && renderCheckinPoster()}
      {type === 'collection' && renderCollectionPoster()}

      {/* 分享按钮 */}
      <button
        onClick={handleShare}
        disabled={isGenerating}
        className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-wenkai transition-all duration-300"
        style={{
          backgroundColor: isGenerating ? '#9CA3AF' : '#C9973A',
          color: '#fff',
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

      {/* 成功提示 */}
      {showSuccess && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
          <div className="bg-white rounded-2xl p-6 text-center max-w-sm mx-4 animate-bounce-in">
            <div className="text-4xl mb-3">🎉</div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">分享成功</h3>
            <p className="text-sm text-gray-500">海报已保存到相册，文案已复制</p>
          </div>
        </div>
      )}

      {/* 复制提示 */}
      {copied && !showSuccess && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-black/70 text-white px-4 py-2 rounded-lg text-sm">
          文案已复制
        </div>
      )}
    </>
  );
}
