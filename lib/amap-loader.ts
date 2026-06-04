/**
 * lib/amap-loader.ts v4.1
 * 高德 JSAPI 2.0 模块级单例加载器。
 *
 * 设计要点：
 * - 全模块共用一个 Promise，避免重复加载 SDK
 * - 浏览器侧调用，env 缺失立刻 throw（fail-fast）
 * - securityJsCode 通过 window._AMapSecurityConfig 注入，与 AMapLoader.load 传入双保险
 * - 不污染 window.suShiMapInstance 等全局变量
 */

'use client';

import { logger } from './logger';

declare global {
  interface Window {
    AMap: any;
    AMapLoader: any;
    _AMapSecurityConfig?: { securityJsCode?: string; serviceHost?: string };
    __amapLoaded?: boolean;
  }
}

let _loaderPromise: Promise<any> | null = null;

/**
 * 加载并返回高德 AMap 全局对象。
 * 多次调用返回同一个 Promise（单例）。
 */
export function loadAMap(): Promise<any> {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('loadAMap 只能在浏览器侧调用'));
  }
  if (_loaderPromise) return _loaderPromise;

  _loaderPromise = (async () => {
    // 已加载则复用
    if (window.AMap && window.AMap.Map) {
      window.__amapLoaded = true;
      window.dispatchEvent(new Event('amap-ready'));
      return window.AMap;
    }

    // env 校验（浏览器侧只能读 NEXT_PUBLIC_*）
    const amapKey = process.env.NEXT_PUBLIC_AMAP_KEY;
    if (!amapKey) {
      const err = new Error(
        '[amap-loader] NEXT_PUBLIC_AMAP_KEY 未配置（请在 .env.local 与 Vercel Project Env 设置）'
      );
      logger.error(err.message);
      throw err;
    }

    // securityJsCode 来源：① NEXT_PUBLIC_AMAP_SECURITY_JS_CODE（最快，build-time inline）
    // ② 服务端 /api/_AMapService/security_js_code 取（兜底，不需要把 secret 暴露给前端 build）
    let securityJsCode = process.env.NEXT_PUBLIC_AMAP_SECURITY_JS_CODE;
    if (!securityJsCode) {
      try {
        const resp = await fetch('/api/amap-security', {
          cache: 'no-store',
        });
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        if (!data?.securityJsCode) throw new Error('响应缺少 securityJsCode');
        securityJsCode = data.securityJsCode;
      } catch (e: any) {
        const err = new Error(
          '[amap-loader] 无法获取 securityJsCode：请配置 AMAP_SECURITY_JS_CODE（服务端）或 NEXT_PUBLIC_AMAP_SECURITY_JS_CODE（前端）。详情：' +
            (e?.message || e)
        );
        logger.error(err.message);
        throw err;
      }
    }

    window._AMapSecurityConfig = { securityJsCode };

    // 动态加载 AMapLoader 脚本
    return await new Promise<any>((resolve, reject) => {
      const loaderScript = document.createElement('script');
      loaderScript.src = 'https://webapi.amap.com/loader.js';
      loaderScript.async = true;
      loaderScript.onload = () => {
        if (!window.AMapLoader) {
          const err = new Error('[amap-loader] AMapLoader 脚本加载完成但未挂载到 window');
          logger.error(err.message);
          return reject(err);
        }
        window.AMapLoader.load({
          key: amapKey,
          version: '2.0',
          plugins: ['AMap.Map', 'AMap.Marker', 'AMap.Polyline', 'AMap.PlaceSearch'],
          SecurityJsCode: securityJsCode,
        })
          .then((AMap: any) => {
            window.AMap = AMap;
            window.__amapLoaded = true;
            logger.info('AMap JSAPI 2.0 ready');
            window.dispatchEvent(new Event('amap-ready'));
            resolve(AMap);
          })
          .catch((err: any) => {
            logger.error('AMapLoader.load 失败', err?.message || err);
            reject(err);
          });
      };
      loaderScript.onerror = (e) => {
        logger.error('AMapLoader 脚本加载失败', e);
        reject(new Error('AMapLoader script failed'));
      };
      document.head.appendChild(loaderScript);
    });
  })();

  return _loaderPromise;
}
