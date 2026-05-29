/**
 * 高德 URI 导航 v4.0
 * appUri + 网页兜底
 */

import { PlaceCore } from '@/types';

/**
 * 生成高德 App URI（调起高德地图 APP）
 */
function buildAppUri(place: PlaceCore, travelMode: 'drive' | 'transit' | 'walk' | 'ride' = 'drive'): string {
  const params = new URLSearchParams({
    sourceApplication: 'su-shi-map',
    poiname: place.modernName || place.songName,
    lat: String(place.lat),
    lon: String(place.lng),
    dev: '0', // GCJ-02 坐标
    style: travelMode === 'drive' ? '0' : travelMode === 'walk' ? '2' : travelMode === 'ride' ? '3' : '1',
  });
  return `androidamap://navi?${params.toString()}`;
}

/**
 * 生成高德网页版导航 URL（兜底）
 */
function buildWebUrl(place: PlaceCore): string {
  const params = new URLSearchParams({
    key: process.env.NEXT_PUBLIC_AMAP_KEY || '',
    location: `${place.lng},${place.lat}`,
    name: place.modernName || place.songName,
    src: 'su-shi-map',
  });
  return `https://uri.amap.com/marker?${params.toString()}`;
}

/**
 * 执行导航
 * 优先尝试调起高德 App，失败则打开网页版
 */
export async function navigateTo(place: PlaceCore): Promise<NavigateResult> {
  if (typeof window === 'undefined') {
    return { success: false, message: '仅在浏览器环境可用' };
  }

  try {
    const appUri = buildAppUri(place);
    const webUrl = buildWebUrl(place);

    // 尝试调起 App（给 <a href="androidamap://..."> 使用）
    return {
      success: true,
      message: '请点击按钮选择导航方式',
      appUri,
      webUrl,
    };
  } catch (err) {
    return {
      success: false,
      message: `导航失败: ${err instanceof Error ? err.message : '未知错误'}`,
    };
  }
}

/**
 * 直接调起高德 App 导航（客户端点击时使用）
 */
export function openNavigation(place: PlaceCore): void {
  if (typeof window === 'undefined') return;

  const appUri = buildAppUri(place);
  const webUrl = buildWebUrl(place);

  // 先尝试调 App
  const iframe = document.createElement('iframe');
  iframe.style.display = 'none';
  iframe.src = appUri;
  document.body.appendChild(iframe);

  // 500ms 后兜底打开网页版
  const timer = setTimeout(() => {
    window.open(webUrl, '_blank');
    document.body.removeChild(iframe);
  }, 500);

  // 如果 App 调起成功，清除定时器
  window.addEventListener('pagehide', () => clearTimeout(timer));
}

export interface NavigateResult {
  success: boolean;
  message: string;
  appUri?: string;
  webUrl?: string;
}
