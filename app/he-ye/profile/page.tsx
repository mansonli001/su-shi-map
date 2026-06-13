/**
 * 贺野游中国 · 旅人录
 * PNG 足迹地图（纯展示）+ 3D 翻牌省份成就卡 + 打卡记录 + 统计概览
 */
'use client';

import { useEffect, useState, useMemo } from 'react';
import { useHeyeStore } from '@/lib/heye-store';
import { getHeyeLocations } from '@/lib/heye-loader';
import dynamic from 'next/dynamic';
import type { HeyeLocation } from '@/types/heye';

const ChinaMapMask = dynamic(() => import('@/components/map/ChinaMapMask'), { ssr: false });

const ProvinceAchievementGrid = dynamic(
  () => import('@/components/map/ChinaMapMask').then(m => ({ default: m.ProvinceAchievementGrid })),
  { ssr: false }
);

const LIT_THRESHOLD = 3;

export default function HeyeProfilePage() {
  const { heyeCheckins } = useHeyeStore();
  const [locations, setLocations] = useState<HeyeLocation[]>([]);

  useEffect(() => {
    getHeyeLocations().then(setLocations);
  }, []);

  // placeId -> location 映射，用于把打卡记录反查到省份
  const locationById = useMemo(() => {
    const map = new Map<string, HeyeLocation>();
    for (const l of locations) map.set(l.id, l);
    return map;
  }, [locations]);

  // 我实际打卡过的地点（按 placeId 去重，过滤掉查不到的脏数据）
  const checkedLocations = useMemo(() => {
    const seen = new Set<string>();
    const result: HeyeLocation[] = [];
    for (const c of heyeCheckins) {
      if (seen.has(c.placeId)) continue;
      seen.add(c.placeId);
      const loc = locationById.get(c.placeId);
      if (loc) result.push(loc);
    }
    return result;
  }, [heyeCheckins, locationById]);

  // 每省「实际打卡」数量（直辖市合并到对应省）
  const provincePlaceCount = useMemo(() => {
    const count: Record<string, number> = {};
    for (const loc of checkedLocations) {
      if (!loc.province) continue;
      count[loc.province] = (count[loc.province] ?? 0) + 1;
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
  }, [checkedLocations]);

  // 已点亮的省份（实际打卡满阈值）
  const litProvinces = useMemo(() => {
    const set = new Set<string>();
    for (const [province, count] of Object.entries(provincePlaceCount)) {
      if (count >= LIT_THRESHOLD) {
        set.add(province);
      }
    }
    return set;
  }, [provincePlaceCount]);

  // 实际打卡地点总数
  const totalPlaces = checkedLocations.length;

  // 实际打卡地点里尝过的小吃（去重）
  const checkedSnacks = useMemo(() => {
    return new Set(checkedLocations.flatMap((l) => l.snacks));
  }, [checkedLocations]);

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

        {/* 足迹地图（PNG 设计图，纯展示） */}
        <div className="he-china-map">
          <div className="he-china-map-header">
            <div className="he-china-map-title">足迹地图</div>
            <div className="he-china-map-stats">
              {litProvinces.size}/27 省份已点亮
            </div>
          </div>
          <div className="he-china-map-body">
            <ChinaMapMask litProvinces={litProvinces} />
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
