/**
 * iOS PWA 安装引导横幅 v2.0
 * 仅在 iOS Safari 且未安装 PWA 时显示
 * 关闭后记录 localStorage，不再显示
 *
 * v2 优化：改为顶部固定提示条，不干扰底部导航和内容区域
 * 使用 transform 动画平滑出入，不引起布局偏移
 */
'use client';

import { useState, useEffect } from 'react';

const DISMISSED_KEY = 'pwa_ios_banner_dismissed';

function isIOSSafari(): boolean {
  if (typeof navigator === 'undefined') return false;
  const ua = navigator.userAgent;
  const isIOS = /iPad|iPhone|iPod/.test(ua);
  const isSafari = /Safari/.test(ua) && !/CriOS|FxiOS/.test(ua);
  return isIOS && isSafari;
}

function isStandalone(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone === true;
}

export default function PWAInstallBanner() {
  const [visible, setVisible] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!isIOSSafari()) return;
    if (isStandalone()) return;
    if (localStorage.getItem(DISMISSED_KEY) === 'true') return;
    // 延迟 2 秒显示，避免首屏加载时干扰
    const timer = setTimeout(() => setVisible(true), 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    setDismissed(true);
    localStorage.setItem(DISMISSED_KEY, 'true');
    setTimeout(() => setVisible(false), 300); // 等动画完成
  };

  // 渲染条件：visible=true 才渲染。dismissed=true 且 visible=true 时仍渲染以播放退出动画。
  if (!visible) return null;

  return (
    <div
      className={`fixed top-0 left-0 right-0 z-50 transition-transform duration-300 ease-in-out ${
        dismissed ? '-translate-y-full' : 'translate-y-0'
      }`}
    >
      <div className="bg-[#2C1810]/95 backdrop-blur-sm text-[#F5E6C8] px-4 py-2.5 flex items-center gap-3 safe-area-top">
        <div className="flex-1 text-xs leading-relaxed font-wenkai">
          <span className="font-bold">添加到主屏幕</span>
          <span className="text-[#B8A88A] ml-1">
            — 点击底部 ⬆️ 分享按钮 → 添加到主屏幕
          </span>
        </div>
        <button
          onClick={handleDismiss}
          className="text-[#B8A88A] text-base px-2 py-1 shrink-0 rounded-lg active:bg-white/10"
          aria-label="关闭"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
