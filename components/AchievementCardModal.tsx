/**
 * 成就卡预览弹窗组件
 * 展示生成的Canvas成就卡，并支持下载
 */

import { useEffect, useState } from 'react';
import type { Achievement } from '@/lib/achievements';

interface AchievementCardModalProps {
  achievement: Achievement;
  cardDataUrl: string;
  onClose: () => void;
}

export default function AchievementCardModal({
  achievement,
  cardDataUrl,
  onClose,
}: AchievementCardModalProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  const handleDownload = async () => {
    setIsDownloading(true);
    
    try {
      const response = await fetch(cardDataUrl);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `成就卡_${achievement.name}_${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('下载失败:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 弹窗内容 */}
      <div className="relative bg-stone-900 rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-stone-700">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{achievement.emoji}</span>
            <h2 className="text-lg font-semibold text-white">{achievement.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-stone-400 hover:text-white transition-colors p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 成就卡预览 */}
        <div className="p-4 bg-stone-800/50">
          <div className="flex justify-center">
            <img
              src={cardDataUrl}
              alt={achievement.name}
              className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-lg"
            />
          </div>
        </div>

        {/* 底部操作 */}
        <div className="p-4 border-t border-stone-700 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 bg-stone-700 hover:bg-stone-600 text-white rounded-lg transition-colors"
          >
            关闭
          </button>
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="flex-1 px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-stone-900 font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isDownloading ? '下载中...' : '下载成就卡'}
          </button>
        </div>
      </div>
    </div>
  );
}