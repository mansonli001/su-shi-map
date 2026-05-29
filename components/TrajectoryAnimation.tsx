/**
 * TrajectoryAnimation v4.0
 * 按时间顺序连线播放苏轼一生行迹
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore, Stage } from '@/types';

// 阶段颜色
const STAGE_COLORS: Record<Stage, string> = {
  youth: '#4CAF50',
  early_career: '#37474F',
  first_exile: '#C62828',
  middle_career: '#6D4C41',
  second_exile: '#F9A825',
  third_exile: '#424242',
  final_journey: '#8B6914',
};

export default function TrajectoryAnimation() {
  const { isTrajectoryPlaying, setTrajectoryPlaying } = useSuShiStore();
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [playing, setPlaying] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // ★ v4.0 修复：从 store 获取 places，不再依赖 props
  const { places } = useSuShiStore();

  // 按阶段+时间排序地点
  const sortedPlaces = [...(places || [])].sort((a, b) => {
    const stageOrder = ['youth', 'early_career', 'first_exile', 'middle_career', 'second_exile', 'third_exile', 'final_journey'];
    const aIdx = stageOrder.indexOf(a.stage);
    const bIdx = stageOrder.indexOf(b.stage);
    return aIdx - bIdx;
  });

  // 开始播放
  const startPlay = () => {
    setCurrentIndex(0);
    setPlaying(true);
  };

  // 暂停
  const pausePlay = () => {
    setPlaying(false);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  // 重置
  const resetPlay = () => {
    pausePlay();
    setCurrentIndex(-1);
  };

  // 自动播放逻辑
  useEffect(() => {
    if (!playing || currentIndex < 0) return;

    if (currentIndex >= sortedPlaces.length) {
      setPlaying(false);
      return;
    }

    timerRef.current = setInterval(() => {
      setCurrentIndex(prev => prev + 1);
    }, 1500); // 每1.5秒移动到下一个地点

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [playing, currentIndex, sortedPlaces.length]);

  // 关闭
  const handleClose = () => {
    resetPlay();
    setTrajectoryPlaying(false);
  };

  if (!isTrajectoryPlaying) return null;

  const currentPlace = currentIndex >= 0 && currentIndex < sortedPlaces.length 
    ? sortedPlaces[currentIndex] 
    : null;

  return (
    <div className="fixed inset-0 z-50 framer-overlay flex items-end justify-center">
      <div className="bg-paper rounded-t-2xl w-full max-w-lg p-6 shadow-2xl">
        {/* 标题 */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-serif text-ink">苏轼行迹动画</h3>
          <button onClick={handleClose} className="text-ink/40 hover:text-ink">
            ✕
          </button>
        </div>

        {/* 进度条 */}
        <div className="mb-4">
          <div className="w-full h-1.5 bg-ink/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-ink transition-all duration-500"
              style={{
                width: `${currentIndex >= 0 ? (currentIndex / sortedPlaces.length) * 100 : 0}%`,
              }}
            />
          </div>
          <p className="text-xs text-ink/40 mt-1">
            {currentIndex + 1} / {sortedPlaces.length}
          </p>
        </div>

        {/* 当前地点 */}
        {currentPlace && (
          <div className="mb-4 p-3 border border-ink/10 rounded-lg">
            <p className="text-sm font-serif text-ink">{currentPlace.songName}</p>
            <p className="text-xs text-ink/50">{currentPlace.modernName}</p>
          </div>
        )}

        {/* 控制按钮 */}
        <div className="flex gap-3">
          {!playing ? (
            <button
              onClick={startPlay}
              className="flex-1 py-2 rounded-lg bg-ink text-paper text-sm font-medium"
            >
              {currentIndex < 0 ? '开始播放' : '继续播放'}
            </button>
          ) : (
            <button
              onClick={pausePlay}
              className="flex-1 py-2 rounded-lg border border-ink/20 text-ink text-sm font-medium"
            >
              暂停
            </button>
          )}
          <button
            onClick={resetPlay}
            className="px-4 py-2 rounded-lg border border-ink/20 text-ink/60 text-sm"
          >
            重置
          </button>
        </div>
      </div>
    </div>
  );
}
