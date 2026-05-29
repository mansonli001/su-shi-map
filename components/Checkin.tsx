/**
 * Checkin v4.0
 * 个人足迹页，IndexedDB 读取，进度条
 */

'use client';

import { useState, useEffect } from 'react';
import { useSuShiStore } from '@/lib/store';
import { getCheckinProgress, getAllCheckins, uncheckin } from '@/lib/idb';
import { PlaceCore, LocalCheckin } from '@/types';

export default function Checkin() {
  const [progress, setProgress] = useState({ checked: 0, total: 0, percent: 0 });
  const [checkins, setCheckins] = useState<LocalCheckin[]>([]);
  const [placesMap, setPlacesMap] = useState<Record<string, PlaceCore>>({});

  // 加载数据
  useEffect(() => {
    // 加载打卡记录
    getAllCheckins().then(setCheckins).catch(console.error);

    // 加载地点数据
    fetch('/data/places-core.json')
      .then(res => res.json())
      .then((places: PlaceCore[]) => {
        const map: Record<string, PlaceCore> = {};
        places.forEach(p => { map[p.id] = p; });
        setPlacesMap(map);
        setProgress({
          checked: checkins.length,
          total: places.length,
          percent: places.length > 0 ? Math.round((checkins.length / places.length) * 100) : 0,
        });
      })
      .catch(console.error);
  }, []);

  // 取消打卡
  const handleUncheckin = async (placeId: string) => {
    try {
      await uncheckin(placeId);
      const updated = await getAllCheckins();
      setCheckins(updated);
      setProgress(await getCheckinProgress(await fetch('/data/places-core.json').then(r => r.json()).then((p: PlaceCore[]) => p.length)));
    } catch (err) {
      console.error('取消打卡失败', err);
    }
  };

  return (
    <div className="min-h-screen bg-paper">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* 标题 */}
        <h1 className="text-2xl font-serif text-ink mb-6">我的足迹</h1>

        {/* 进度条 */}
        <div className="mb-8 p-4 border border-ink/10 rounded-xl">
          <div className="flex items-end justify-between mb-2">
            <span className="text-2xl font-serif text-ink">{progress.percent}%</span>
            <span className="text-sm text-ink/40">
              {progress.checked} / {progress.total}
            </span>
          </div>
          <div className="w-full h-2 bg-ink/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-ink transition-all duration-700"
              style={{ width: `${progress.percent}%` }}
            />
          </div>
          <p className="text-xs text-ink/40 mt-2">
            {progress.percent < 30 && '才开始，继续探索吧！'}
            {progress.percent >= 30 && progress.percent < 60 && '不错，渐入佳境！'}
            {progress.percent >= 60 && progress.percent < 90 && '厉害，已经过半了！'}
            {progress.percent >= 90 && progress.percent < 100 && '快要集齐了！'}
            {progress.percent === 100 && '🎉 全部打卡完成！'}
          </p>
        </div>

        {/* 打卡列表 */}
        <div className="space-y-3">
          <h2 className="text-lg font-serif text-ink/80 mb-3">已打卡地点</h2>
          {checkins.length === 0 && (
            <p className="text-sm text-ink/40 text-center py-8">暂无打卡记录，去地图上探索吧！</p>
          )}
          {checkins
            .sort((a, b) => b.checkedAt - a.checkedAt)
            .map(checkin => {
              const place = placesMap[checkin.placeId];
              return (
                <div
                  key={checkin.placeId}
                  className="flex items-center gap-3 p-3 border border-ink/10 rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-ink truncate">
                      {place?.songName || checkin.placeId}
                    </p>
                    <p className="text-xs text-ink/40">
                      {place?.modernName || ''}
                      {' · '}
                      {new Date(checkin.checkedAt).toLocaleDateString('zh-CN')}
                    </p>
                  </div>
                  <button
                    onClick={() => handleUncheckin(checkin.placeId)}
                    className="text-xs text-ink/30 hover:text-red-500 transition-colors"
                  >
                    取消
                  </button>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
