/**
 * 贺野游中国 · 旅人录
 * 纯SVG冰箱贴地图 + 3D翻牌成就卡片 + 打卡记录 + 统计
 */
'use client';

import { useEffect, useState, useMemo } from 'react';
import { useHeyeStore } from '@/lib/heye-store';
import { getHeyeLocations, getHeyeProvinceStats } from '@/lib/heye-loader';
import dynamic from 'next/dynamic';
import type { HeyeLocation, HeyeProvinceStatsMap } from '@/types/heye';

const ChinaMapMask = dynamic(() => import('@/components/map/ChinaMapMask'), { ssr: false });

const ProvinceAchievementGrid = dynamic(
  () => import('@/components/map/ChinaMapMask').then(m => ({ default: m.ProvinceAchievementGrid })),
  { ssr: false }
);

const LIT_THRESHOLD = 3;

export default function HeyeProfilePage() {
  const { heyeCheckins } = useHeyeStore();
  const [locations, setLocations] = useState<HeyeLocation[]>([]);
  const [provinceStats, setProvinceStats] = useState<HeyeProvinceStatsMap>({});

  useEffect(() => {
    getHeyeLocations().then(setLocations);
    getHeyeProvinceStats().then(setProvinceStats);
  }, []);

  // 每省打卡数量（直辖市合并到对应省）
  const provincePlaceCount = useMemo(() => {
    const count: Record<string, number> = {};
    for (const [province, stats] of Object.entries(provinceStats)) {
      count[province] = stats.placeCount;
    }
    // 直辖市合并到对应省
    const MERGE_MAP: Record<string, string> = {
      '北京': '河北', '天津': '河北',
      '上海': '江苏',
      '重庆': '四川',
    };
    for (const [city, target] of Object.entries(MERGE_MAP)) {
      if (count[city]) {
        count[target] = (count[target] ?? 0) + count[city];
        delete count[city];
      }
    }
    return count;
  }, [provinceStats]);

  // 已点亮的省份
  const litProvinces = useMemo(() => {
    const set = new Set<string>();
    for (const [province, count] of Object.entries(provincePlaceCount)) {
      if (count >= LIT_THRESHOLD) {
        set.add(province);
      }
    }
    return set;
  }, [provincePlaceCount]);

  const totalPlaces = useMemo(() => {
    return Object.values(provincePlaceCount).reduce((a, b) => a + b, 0);
  }, [provincePlaceCount]);

  const checkedSnacks = useMemo(() => {
    return new Set(locations.flatMap((l) => l.snacks));
  }, [locations]);

  const handleProvinceClick = (name: string) => {
    console.log('点击省份:', name, '打卡数:', provincePlaceCount[name] ?? 0);
  };

  return (
    <div className="he-profile">
      {/* 顶栏 */}
      <div className="he-profile-topbar">
        <h1 className="he-profile-title">旅人录</h1>
      </div>

      <div className="he-profile-content">
        {/* 统计概览 */}
        <div className="he-profile-stats">
          <div className="he-profile-stat-card">
            <div className="he-profile-stat-n">{totalPlaces}</div>
            <div className="he-profile-stat-l">打卡地点</div>
          </div>
          <div className="he-profile-stat-card">
            <div className="he-profile-stat-n">{litProvinces.size}</div>
            <div className="he-profile-stat-l">点亮省份</div>
          </div>
          <div className="he-profile-stat-card">
            <div className="he-profile-stat-n">{checkedSnacks.size}</div>
            <div className="he-profile-stat-l">尝过小吃</div>
          </div>
        </div>

        {/* 冰箱贴地图（纯SVG，不依赖PNG） */}
        <div className="he-china-map">
          <div className="he-china-map-header">
            <div className="he-china-map-title">足迹地图</div>
            <div className="he-china-map-stats">
              {litProvinces.size}/27 省份已点亮
            </div>
          </div>
          <div className="he-china-map-body">
            <ChinaMapMask
              litProvinces={litProvinces}
              onProvinceClick={handleProvinceClick}
            />
          </div>
          <div className="he-china-map-hint">
            每省打卡 {LIT_THRESHOLD} 个地点即可点亮该省
          </div>
        </div>

        {/* 省份成就卡（SVG缩略图 + 3D翻牌） */}
        <div className="he-province-section">
          <div className="he-province-section-title">省份成就</div>
          <div className="he-province-section-subtitle">
            {litProvinces.size > 0
              ? `已解锁 ${litProvinces.size} 张冰箱贴`
              : `打卡 ${LIT_THRESHOLD} 个地点解锁省份冰箱贴`}
          </div>
          <ProvinceAchievementGrid
            litProvinces={litProvinces}
            checkinCounts={provincePlaceCount}
            threshold={LIT_THRESHOLD}
            onCardClick={handleProvinceClick}
          />
        </div>

        {/* 打卡记录 */}
        <div className="he-checkin-list">
          <div className="he-checkin-list-title">打卡记录</div>
          {heyeCheckins.length === 0 ? (
            <div className="he-empty-state">
              还没有打卡记录，去地图上打卡吧！
            </div>
          ) : (
            heyeCheckins.map((c) => (
              <div key={c.placeId + c.checkinAt} className="he-checkin-item">
                <span className="he-checkin-item-name">{c.placeName}</span>
                <span className="he-checkin-item-date">
                  {new Date(c.checkinAt).toLocaleDateString('zh-CN')}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
