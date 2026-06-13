/**
 * 底部 Tab 导航 v3.0「Ink & Path + 贺野」
 * - 双套导航：苏轼 4 栏 + 切换入口 / 贺野 4 栏 + 切换入口
 * - 按 usePathname() 是否以 /he-ye 开头切换
 * - 苏轼：首页 / 水墨地图 / 古诗集 / 名士录 / 贺野游中国→
 * - 贺野：首页 / 足迹地图 / 文章流 / 旅人录 / ←苏轼行吟山河
 * - 浮动切换方案：苏轼 / 不动，不设独立选择页
 */

'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';

const SUSHI_NAV = [
  { path: '/',        label: '首页',     icon: 'home' },
  { path: '/explore', label: '水墨地图', icon: 'map' },
  { path: '/poems',   label: '古诗集',   icon: 'auto_stories' },
  { path: '/profile', label: '名士录',   icon: 'person' },
];

const HEYE_NAV = [
  { path: '/he-ye',           label: '首页',     icon: 'home' },
  { path: '/he-ye/explore',   label: '足迹地图', icon: 'map' },
  { path: '/he-ye/feed',      label: '文章流',   icon: 'article' },
  { path: '/he-ye/profile',   label: '旅人录',   icon: 'person' },
];

export default function BottomNav() {
  const pathname = usePathname() || '/';
  const isHeye = pathname.startsWith('/he-ye');

  const navItems = isHeye ? HEYE_NAV : SUSHI_NAV;

  const isActive = (path: string) => {
    if (!isHeye) {
      // 苏轼导航逻辑（保持原样）
      if (path === '/explore' && pathname.startsWith('/places/')) return true;
      if (path === '/') return pathname === '/';
      return pathname === path || pathname.startsWith(path + '/');
    }
    // 贺野导航逻辑
    if (path === '/he-ye') return pathname === '/he-ye';
    return pathname === path || pathname.startsWith(path + '/');
  };

  return (
    <nav className={`ip-bottomnav ${isHeye ? 'heye-bottomnav' : ''}`} aria-label="底部导航">
      {navItems.map((item) => {
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
      {/* 行者切换入口 */}
      <Link
        href={isHeye ? '/' : '/he-ye'}
        className="ip-bottomnav-link ip-bottomnav-switch"
        aria-label={isHeye ? '切换到苏轼行吟山河' : '切换到贺野游中国'}
      >
        {isHeye ? (
          <span
            className="material-symbols-outlined ip-bottomnav-icon"
            aria-hidden="true"
          >
            auto_stories
          </span>
        ) : (
          <Image
            src="/heye-logo.png"
            alt="贺野"
            width={22}
            height={22}
            className="ip-bottomnav-avatar"
            style={{ borderRadius: '50%', objectFit: 'cover' }}
          />
        )}
        <span className="ip-bottomnav-label">
          {isHeye ? '行吟山河' : '贺野游中国'}
        </span>
      </Link>
    </nav>
  );
}
