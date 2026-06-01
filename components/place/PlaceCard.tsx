/**
 * PlaceCard v4.2
 * Framer Motion 半屏卡片，手势拖拽上滑展开/下滑关闭
 * 修复：原地展开详情，不跳转新页面
 */

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore, PlaceDetail } from '@/types';

/** stage → 中文人生阶段 */
const STAGE_LABELS: Record<string, string> = {
  youth: '眉山少年（1037-1056）',
  early_career: '初入仕途（1056-1071）',
  first_exile: '乌台诗案·黄州（1079-1084）',
  middle_career: '元祐重返（1085-1094）',
  second_exile: '贬惠州（1094-1097）',
  third_exile: '贬儋州（1097-1100）',
  final_journey: '北归途中（1100-1101）',
};

interface PlaceCardProps {
  place: PlaceCore;
}

export default function PlaceCard({ place }: PlaceCardProps) {
  const { isCardOpen, closeCard } = useSuShiStore();
  const [expanded, setExpanded] = useState(false);
  const [checkedIn, setCheckedIn] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [detail, setDetail] = useState<PlaceDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // 打开卡片时：检查打卡状态
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

  // 打卡
  const handleCheckin = async () => {
    try {
      await import('@/lib/idb').then(m => m.checkin(place.id));
      setCheckedIn(true);
    } catch (err) {
      console.error('打卡失败', err);
    }
  };

  // 查看详情：加载详情数据并展开
  const handleShowDetail = async () => {
    setDetailLoading(true);
    try {
      const res = await fetch(`/data/places/${place.id}.json`);
      if (res.ok) {
        const data = await res.json();
        setDetail(data);
        setShowDetail(true);
      }
    } catch (err) {
      console.error('加载详情失败', err);
    } finally {
      setDetailLoading(false);
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
            animate={{ y: expanded ? '10%' : '35%' }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            onDragEnd={handleDragEnd}
            className="fixed inset-x-0 bottom-0 z-50 bg-paper rounded-t-2xl shadow-2xl max-h-[80vh] overflow-y-auto md:max-w-2xl md:mx-auto md:rounded-2xl"
          >
            {/* 拖拽手柄 */}
            <div className="drag-handle cursor-grab active:cursor-grabbing">
              <div className="w-12 h-1.5 bg-ink/20 rounded-full mx-auto" />
            </div>

            <div className="px-6 pb-6">
              {/* ===== 详情视图 ===== */}
              {showDetail && detail ? (
                <>
                  {/* 详情头部 */}
                  <div className="flex items-center gap-2 mb-4">
                    <button
                      onClick={() => setShowDetail(false)}
                      className="p-1.5 rounded-lg hover:bg-ink/5 text-ink/60"
                    >
                      ← 返回
                    </button>
                    <span className="text-xs text-ink/40">详细故事</span>
                  </div>

                  {/* 详情内容 */}
                  <div className="overflow-y-auto max-h-[60vh] pr-2">
                    {/* 事迹概述 */}
                    {detail.summary && (
                      <p className="text-sm text-ink/70 leading-relaxed mb-4">
                        {detail.summary}
                      </p>
                    )}

                    {/* 详细故事 */}
                    {detail.story && (
                      <div className="mb-6">
                        <h3 className="text-base font-serif text-ink/80 mb-2">详细故事</h3>
                        <div className="text-sm text-ink/80 whitespace-pre-wrap font-serif leading-relaxed">
                          {detail.story}
                        </div>
                      </div>
                    )}

                    {/* 相关诗词 */}
                    {detail.poems && detail.poems.length > 0 && (
                      <div className="mb-6">
                        <h3 className="text-base font-serif text-ink/80 mb-2">相关诗词</h3>
                        <div className="space-y-3">
                          {detail.poems.map((poem: any) => (
                            <div key={poem.id} className="border-l-2 border-ink/20 pl-3">
                              <p className="font-serif text-ink/90 text-sm">{poem.title}</p>
                              <pre className="text-xs text-ink/70 mt-1 whitespace-pre-wrap font-serif">
                                {poem.content}
                              </pre>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 现代景点 */}
                    {detail.attractions && detail.attractions.length > 0 && (
                      <div className="mb-6">
                        <h3 className="text-base font-serif text-ink/80 mb-2">现代景点</h3>
                        <div className="space-y-2">
                          {detail.attractions.map((attr: any) => (
                            <div key={attr.id} className="border border-ink/10 rounded-lg p-3">
                              <h4 className="text-sm font-medium text-ink">{attr.name}</h4>
                              <p className="text-xs text-ink/60 mt-1">{attr.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  {/* ===== 卡片视图（默认） ===== */}
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-serif ${
                      place.type === 'birth' ? 'bg-green-100 text-green-800' :
                      place.type === 'office' ? 'bg-blue-100 text-blue-800' :
                      place.type === 'exile' ? 'bg-red-100 text-red-800' :
                      place.type === 'tour' ? 'bg-amber-100 text-amber-800' :
                      place.type === 'friend' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {place.type === 'birth' ? '出生地' :
                       place.type === 'office' ? '任职地' :
                       place.type === 'exile' ? '贬谪地' :
                       place.type === 'tour' ? '游览地' :
                       place.type === 'friend' ? '友人' : '长眠地'}
                    </span>
                    <span className="text-xs text-ink/50">{STAGE_LABELS[place.stage] || place.stage}</span>
                  </div>

                  {/* 标题：宋朝地名 + 现代地名 */}
                  <h2 className="text-2xl font-serif text-ink mb-1">
                    {place.songName}
                  </h2>
                  <p className="text-sm text-ink/60 mb-3">{place.modernName}</p>

                  {/* 简介 */}
                  {place.summary ? (
                    <p className="text-sm text-ink/70 leading-relaxed mb-4 line-clamp-3">
                      {place.summary}
                    </p>
                  ) : (
                    <p className="text-sm text-ink/40 leading-relaxed mb-4 italic">
                      暂无简介
                    </p>
                  )}

                  {/* 操作按钮：打卡 + 查看详情 */}
                  <div className="flex gap-3 mt-4">
                    <button
                      onClick={handleCheckin}
                      className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        checkedIn ? 'bg-ink/10 text-ink/50' : 'bg-ink text-paper hover:bg-ink/90'
                      }`}
                    >
                      {checkedIn ? '已打卡' : '打卡'}
                    </button>
                    <button
                      onClick={handleShowDetail}
                      disabled={detailLoading}
                      className="flex-1 py-2.5 rounded-lg text-sm font-medium border border-ink/20 text-ink hover:bg-ink/5 transition-colors disabled:opacity-50"
                    >
                      {detailLoading ? '加载中...' : '查看详情'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
