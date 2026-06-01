/**
 * AMapScript - 使用官方 AMapLoader 加载高德地图 JSAPI 2.0
 */
'use client';

import { useEffect } from 'react';

declare global {
  interface Window {
    AMap: any;
    AMapLoader: any;
    _AMapSecurityConfig?: { securityJsCode?: string };
    __amapLoaded?: boolean;
  }
}

export default function AMapScript() {
  useEffect(() => {
    const amapKey = process.env.NEXT_PUBLIC_AMAP_KEY || '58b83b5ce989b73370141e4c61e5ef41';
    const securityJsCode = process.env.AMAP_SECURITY_JS_CODE || 'e2b0432c83a60cb97a4f66842dfd4169';
    
    // 设置安全配置
    window._AMapSecurityConfig = {
      securityJsCode: securityJsCode
    };
    console.log('[AMapScript] 安全配置已设置');

    // 检查是否已加载
    if (window.AMap && window.AMap.Map) {
      console.log('[AMapScript] AMap 已存在');
      window.dispatchEvent(new Event('amap-ready'));
      return;
    }

    // 创建 script 标签动态加载 AMapLoader
    const loaderScript = document.createElement('script');
    loaderScript.src = 'https://webapi.amap.com/loader.js';
    loaderScript.async = true;
    loaderScript.onload = () => {
      console.log('[AMapScript] AMapLoader 加载完成');
      
      // 使用 AMapLoader 加载地图
      window.AMapLoader.load({
        key: amapKey,
        version: '2.0',
        plugins: ['AMap.Map', 'AMap.Marker', 'AMap.Polyline'],
        SecurityJsCode: securityJsCode,
      }).then((AMap: any) => {
        window.AMap = AMap;
        window.__amapLoaded = true;
        console.log('[AMapScript] ✅ 高德地图 JSAPI 2.0 初始化完成');
        window.dispatchEvent(new Event('amap-ready'));
      }).catch((err: any) => {
        console.error('[AMapScript] ❌ 高德地图初始化失败:', err);
      });
    };
    
    loaderScript.onerror = (e) => {
      console.error('[AMapScript] ❌ AMapLoader 加载失败:', e);
    };

    document.head.appendChild(loaderScript);

    return () => {
      document.head.removeChild(loaderScript);
    };
  }, []);

  return (<div style={{ display: 'none' }} data-amap-script="loaded"/>);
}