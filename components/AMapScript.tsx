/**
 * AMapScript v4.1
 * 仅作为客户端入口触发 lib/amap-loader 单例加载。
 * 不再持有任何硬编码 key / securityCode；env 缺失由 loader 统一 fail-fast。
 */
'use client';

import { useEffect } from 'react';
import { loadAMap } from '@/lib/amap-loader';
import { logger } from '@/lib/logger';

export default function AMapScript() {
  useEffect(() => {
    loadAMap().catch((err) => {
      logger.error('AMapScript: 高德地图加载失败', err?.message || err);
    });
  }, []);

  return <div style={{ display: 'none' }} data-amap-script="loaded" />;
}
