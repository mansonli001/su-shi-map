/**
 * SWUpdateGuard —— 跨部署缓存自愈守卫 v1.0（2026-06-12）
 *
 * 背景：PWA（next-pwa / workbox）在新部署后存在一个窗口期——设备上残留的「陈旧
 * Service Worker」可能返回引用了「已被 Vercel 清理的旧 hash 静态资源」的 stale 页面，
 * 导致 /_next/static/*.css 等资源 404 → 整页裸样式（JS 仍执行，故数据照常渲染）。
 *
 * 本守卫只在「静态资源真的加载失败」时才动作，正常路径零开销：
 *   1. 捕获阶段监听 window 'error' 事件；
 *   2. 命中条件：target 为 <link>/<script> 且其 href/src 指向 /_next/static/；
 *   3. 动作：sessionStorage 去重 → 更新所有 SW 注册 → 清理 workbox 静态/预缓存 → 单次 reload。
 *
 * 防循环：用 sessionStorage 标记，确保单次会话只自动 reload 一次，避免死刷。
 * 安全：不打印敏感信息，不引入新依赖，无 SW 支持时完全 no-op。
 */
'use client';

import { useEffect } from 'react';

const RECOVER_FLAG = 'sw_asset_recovered';

export default function SWUpdateGuard() {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    let triggered = false;

    const isStaticAssetTarget = (target: EventTarget | null): string | null => {
      if (!target) return null;
      if (target instanceof HTMLLinkElement && target.rel === 'stylesheet') {
        return target.href || null;
      }
      if (target instanceof HTMLScriptElement) {
        return target.src || null;
      }
      return null;
    };

    const recover = async () => {
      // 单次会话只自愈一次，防止失败资源持续触发死循环刷新
      if (triggered) return;
      if (sessionStorage.getItem(RECOVER_FLAG)) return;
      triggered = true;
      sessionStorage.setItem(RECOVER_FLAG, String(Date.now()));

      try {
        // 1. 更新所有 Service Worker 注册，促使新 SW 尽快接管
        if ('serviceWorker' in navigator) {
          const regs = await navigator.serviceWorker.getRegistrations();
          await Promise.all(regs.map((reg) => reg.update().catch(() => undefined)));
        }
        // 2. 清理 workbox 静态/预缓存（仅清与 next 静态资源相关的 cache，保留数据缓存）
        if ('caches' in window) {
          const keys = await caches.keys();
          await Promise.all(
            keys
              .filter((k) => /static|precache|workbox|next/i.test(k))
              .map((k) => caches.delete(k).catch(() => false))
          );
        }
      } catch {
        // 自愈尽力而为，任何异常都不阻断后续 reload
      } finally {
        // 3. 单次硬刷新，从新部署重新拉取自洽的页面 + 资源
        window.location.reload();
      }
    };

    const onError = (event: Event) => {
      const url = isStaticAssetTarget(event.target);
      if (url && url.includes('/_next/static/')) {
        void recover();
      }
    };

    // 资源加载错误不冒泡，必须用捕获阶段监听
    window.addEventListener('error', onError, true);
    return () => window.removeEventListener('error', onError, true);
  }, []);

  return null;
}
