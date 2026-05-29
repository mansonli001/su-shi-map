/**
 * PlaceCard v4.0
 * Framer Motion 半屏卡片，手势拖拽上滑展开/下滑关闭
 */

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore, PlaceDetail } from '@/types';
import { getCheckinProgress } from '@/lib/idb';

interface PlaceCardProps {
  place: PlaceCore;
  detail?: PlaceDetail;
}

export default function PlaceCard({ place, detail }: PlaceCardProps) {
  const { isCardOpen, closeCard } = useSuShiStore();
  const [expanded, setExpanded] = useState(false);
  const [checkedIn, setCheckedIn] = useState(false);

  // ★ v4.0 修复：打开卡片时检查本地是否已打卡
  useEffect(() => {
    if (!place) return;
    import('@/lib/idb').then(m => {
      m.isCheckedin(place.id).then(setCheckedIn);
    });
  }, [place]);

  /**
   * 拖拽处理：下滑关闭
   */
  const handleDragEnd = (_event: any, info: PanInfo) => {
    if (info.offsetY > 100) {
      closeCard();
    }
  };

  // ★ v4.0 修复：改用 idb 本地打卡，不再调 /api/checkin
  const handleCheckin = async () => {
    try {
      await import('@/lib/idb').then(m => m.checkin(place.id));
      setCheckedIn(true);
    } catch (err) {
      console.error('打卡失败', err);
    }
  };

  return (
    <AnimatePresence>
      {isCardOpen && place && (
        <>
          {/* 遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="framer-overlay"
            onClick={closeCard}
          />

          {/* 半屏卡片 */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: expanded ? '20%' : '50%' }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            onDragEnd={handleDragEnd}
            className="fixed inset-x-0 bottom-0 z-50 bg-paper rounded-t-2xl shadow-2xl max-h-[80vh] overflow-y-auto"
          >
            {/* 拖拽手柄 */}
            <div className="drag-handle cursor-grab active:cursor-grabbing">
              <div className="w-12 h-1.5 bg-ink/20 rounded-full mx-auto" />
            </div>

            {/* 卡片内容 */}
            <div className="px-6 pb-6">
              {/* 地点类型标签 */}
              <div className="flex items-center gap-2 mb-3">
                <span className={`px-2 py-0.5 rounded text-xs font-serif ${place.type === 'birth' ? 'bg-green-100 text-green-800' : place.type === 'office' ? 'bg-blue-100 text-blue-800' : place.type === 'exile' ? 'bg-red-100 text-red-800' : place.type === 'tour' ? 'bg-amber-100 text-amber-800' : place.type === 'friend' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'}`}>
                  {place.type === 'birth' ? '出生地' : place.type === 'office' ? '任职地' : place.type === 'exile' ? '贬谪地' : place.type === 'tour' ? '游览地' : place.type === 'friend' ? '友人' : '长眠地'}
                </span>
                <span className="text-xs text-ink/50">{place.stage}</span>
              </div>

              {/* 标题 */}
              <h2 className="text-2xl font-serif text-ink mb-1">
                {place.songName}
              </h2>
              <p className="text-sm text-ink/60 mb-4">{place.modernName}</p>

              {/* 详情内容 */}
              {detail && (
                <div className="prose-ancient text-sm">
                  <p className="text-ink/80 leading-relaxed">{detail.summary}</p>

                  {/* 诗词 */}
                  {detail.poems && detail.poems.length > 0 && (
                    <div className="mt-4 space-y-3">
                      <h3 className="text-base font-serif text-ink">相关诗词</h3>
                      {detail.poems.map((poem) => (
                        <div key={poem.id} className="border-l-2 border-ink/20 pl-3">
                          <p className="font-serif text-ink/90">{poem.title}</p>
                          <pre className="prose-poem text-xs mt-1">{poem.content}</pre>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 景点 */}
                  {detail.attractions && detail.attractions.length > 0 && (
                    <div className="mt-4">
                      <h3 className="text-base font-serif text-ink">现代景点</h3>
                      <ul className="space-y-2 mt-2">
                        {detail.attractions.map((attr) => (
                          <li key={attr.id} className="text-sm text-ink/70">
                            <span className="font-medium">{attr.name}</span>
                            {attr.ticket && <span className="text-xs ml-2 text-ink/50">{attr.ticket}</span>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* 操作按钮 */}
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleCheckin}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${checkedIn ? 'bg-ink/10 text-ink/50' : 'bg-ink text-paper hover:bg-ink/90'}`}
                >
                  {checkedIn ? '已打卡' : '打卡'}
                </button>
                <button
                  onClick={() => window.open(`https://uri.amap.com/marker?position=${place.lng},${place.lat}&name=${place.modernName}`, '_blank')}
                  className="flex-1 py-2.5 rounded-lg text-sm font-medium border border-ink/20 text-ink hover:bg-ink/5 transition-colors"
                >
                  导航
                </button>
                <button
                  onClick={() => window.open(`/place/${place.id}`, '_blank')}
                  className="flex-1 py-2.5 rounded-lg text-sm font-medium border border-ink/20 text-ink hover:bg-ink/5 transition-colors"
                >
                  详情
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
