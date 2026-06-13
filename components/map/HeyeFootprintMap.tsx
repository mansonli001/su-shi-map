/**
 * 贺野游中国 · 足迹地图（高德地图版）
 * 显示中国地图 + 已点亮省份边界高亮 + 省份点击交互
 */
'use client';

import { useEffect, useRef, useState } from 'react';
import { loadAMap } from '@/lib/amap-loader';
import { logger } from '@/lib/logger';

// 省份名称到高德行政区查询名的映射
const PROVINCE_ADMAP: Record<string, string> = {
  '北京': '北京市', '天津': '天津市', '上海': '上海市', '重庆': '重庆市',
  '河北': '河北省', '山西': '山西省', '辽宁': '辽宁省', '吉林': '吉林省',
  '黑龙江': '黑龙江省', '江苏': '江苏省', '浙江': '浙江省', '安徽': '安徽省',
  '福建': '福建省', '江西': '江西省', '山东': '山东省', '河南': '河南省',
  '湖北': '湖北省', '湖南': '湖南省', '广东': '广东省', '海南': '海南省',
  '四川': '四川省', '贵州': '贵州省', '云南': '云南省', '陕西': '陕西省',
  '甘肃': '甘肃省', '青海': '青海省', '台湾': '台湾省',
  '内蒙古': '内蒙古自治区', '广西': '广西壮族自治区', '西藏': '西藏自治区',
  '宁夏': '宁夏回族自治区', '新疆': '新疆维吾尔自治区',
  '香港': '香港特别行政区', '澳门': '澳门特别行政区',
};

// 省份中心坐标
const PROVINCE_CENTER: Record<string, [number, number]> = {
  '北京': [116.4, 39.9], '天津': [117.2, 39.1], '上海': [121.47, 31.23], '重庆': [106.55, 29.56],
  '河北': [114.5, 38.0], '山西': [112.5, 37.5], '辽宁': [123.4, 41.8], '吉林': [126.5, 43.5],
  '黑龙江': [126.6, 45.7], '江苏': [118.8, 32.0], '浙江': [120.1, 30.2], '安徽': [117.3, 31.8],
  '福建': [119.3, 26.0], '江西': [115.9, 28.6], '山东': [117.0, 36.6], '河南': [113.6, 34.7],
  '湖北': [114.3, 30.5], '湖南': [112.9, 28.2], '广东': [113.2, 23.1], '海南': [110.3, 20.0],
  '四川': [104.0, 30.5], '贵州': [106.7, 26.6], '云南': [102.7, 25.0], '陕西': [108.9, 34.2],
  '甘肃': [103.8, 36.0], '青海': [101.7, 36.6], '台湾': [121.0, 23.7],
  '内蒙古': [111.7, 40.8], '广西': [108.3, 22.8], '西藏': [91.1, 29.6],
  '宁夏': [106.2, 38.5], '新疆': [87.6, 43.8],
  '香港': [114.1, 22.3], '澳门': [113.5, 22.2],
};

interface HeyeFootprintMapProps {
  litProvinces: Set<string>;
  onProvinceClick?: (name: string) => void;
}

export default function HeyeFootprintMap({ litProvinces, onProvinceClick }: HeyeFootprintMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const overlaysRef = useRef<any[]>([]);
  const [isMapReady, setIsMapReady] = useState(false);

  // 初始化地图
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    let destroyed = false;

    loadAMap()
      .then((AMap: any) => {
        if (destroyed || mapRef.current || !AMap?.Map) return;
        const map = new AMap.Map(containerRef.current, {
          zoom: 4.5,
          center: [104.5, 35.5],
          viewMode: '2D',
          zoomControl: false,
          scaleControl: false,
          toolBarControl: false,
          dragEnable: false,
          zoomEnable: false,
          doubleClickZoom: false,
          keyboardEnable: false,
          scrollWheel: false,
          touchZoom: false,
          mapStyle: 'amap://styles/5bcb375541c22ed25703103920a7d5e8',
        });
        mapRef.current = map;
        setIsMapReady(true);
      })
      .catch((err: any) => {
        logger.error('足迹地图初始化失败', err?.message || err);
      });

    return () => {
      destroyed = true;
      if (mapRef.current) {
        mapRef.current.destroy();
        mapRef.current = null;
      }
    };
  }, []);

  // 绘制省份边界高亮
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isMapReady) return;
    const AMapLocal = (window as any).AMap;
    if (!AMapLocal?.DistrictSearch) return;

    // 清除旧覆盖物
    overlaysRef.current.forEach((o) => map.remove(o));
    overlaysRef.current = [];

    const districtSearch = new AMapLocal.DistrictSearch({
      subdistrict: 0,
      extensions: 'all',
      level: 'province',
    });

    // 为已点亮省份绘制高亮边界
    const litArray = Array.from(litProvinces);
    litArray.forEach((province) => {
      const adName = PROVINCE_ADMAP[province];
      if (!adName) return;

      districtSearch.search(adName, (status: string, result: any) => {
        if (status === 'complete' && result?.districtList?.[0]) {
          const bounds = result.districtList[0].boundaries;
          if (bounds && bounds.length > 0) {
            const polygons = bounds.map((bound: any) => new AMapLocal.Polygon({
              path: bound,
              strokeColor: '#C4612A',
              strokeWeight: 2,
              strokeOpacity: 0.9,
              fillColor: '#C4612A',
              fillOpacity: 0.25,
              zIndex: 10,
              bubble: true,
            }));
            map.add(polygons);
            overlaysRef.current.push(...polygons);
          }
        }
      });
    });
  }, [litProvinces, isMapReady]);

  // 点击省份
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isMapReady) return;

    const handleClick = (e: any) => {
      const AMapLocal = (window as any).AMap;
      if (!AMapLocal?.DistrictSearch) return;

      const districtSearch = new AMapLocal.DistrictSearch({
        subdistrict: 0,
        extensions: 'all',
        level: 'province',
      });

      // 通过点击位置反查省份
      const lnglat = e.lnglat;
      // 遍历省份中心点，找最近的
      let closestProvince = '';
      let minDist = Infinity;
      for (const [name, center] of Object.entries(PROVINCE_CENTER)) {
        const dist = Math.sqrt(
          Math.pow(lnglat.getLng() - center[0], 2) +
          Math.pow(lnglat.getLat() - center[1], 2)
        );
        if (dist < minDist) {
          minDist = dist;
          closestProvince = name;
        }
      }
      if (closestProvince && minDist < 5) {
        onProvinceClick?.(closestProvince);
      }
    };

    map.on('click', handleClick);
    return () => {
      map.off('click', handleClick);
    };
  }, [isMapReady, onProvinceClick]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '320px',
        borderRadius: '8px',
        overflow: 'hidden',
      }}
    />
  );
}
