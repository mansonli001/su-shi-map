/**
 * 底部 Tab 导航 v2.0「Ink & Path」（2026-06-05）
 * - 米白 frosted parchment 底（rgba 0.92 + blur 14px）
 * - active 状态：朱砂红圆点 dot 上浮 + 墨黑文字（不再金色）
 * - icon 切换为 Material Symbols Outlined（与 stitch 设计稿统一）
 * - 4 栏：首页 / 水墨地图 / 古诗集 / 名士录
 * - 完全对齐 references/stitch-pc/ink_path/DESIGN.md「Bottom Navigation」规范：
 *     "A frosted Warm Parchment bar with Deep Ink Black icons.
 *      The active state is indicated by a Cinnabar Red dot above the icon."
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { path: '/',        label: '首页',     icon: 'home' },
  { path: '/explore', label: '水墨地图', icon: 'map' },
  { path: '/poems',   label: '古诗集',   icon: 'auto_stories' },
  { path: '/profile', label: '名士录',   icon: 'person' },
];

export default function BottomNav() {
  const pathname = usePathname() || '/';

  const isActive = (path: string) => {
    // /places/* → 高亮「水墨地图」
    if (path === '/explore' && pathname.startsWith('/places/')) return true;
    if (path === '/') return pathname === '/';
    return pathname === path || pathname.startsWith(path + '/');
  };

  return (
    <nav className="ip-bottomnav" aria-label="底部导航">
      {NAV_ITEMS.map((item) => {
        const active = isActive(item.path);
        return (
          <Link
            key={item.path}
            href={item.path}
            className="ip-bottomnav-link"
            aria-current={active ? 'page' : undefined}
          >
            <span
              className="material-symbols-outlined ip-bottomnav-icon"
              style={{
                fontVariationSettings: active ? "'FILL' 1" : "'FILL' 0",
              }}
              aria-hidden="true"
            >
              {item.icon}
            </span>
            <span className="ip-bottomnav-label">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
