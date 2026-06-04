/**
 * 底部Tab导航栏
 * 4栏设计：首页 / 地图 / 诗词 / 我的
 * 完全按照设计稿实现：白色背景 + Tabler Icons
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  {
    path: '/',
    label: '首页',
    icon: 'home',
  },
  {
    path: '/explore',
    label: '地图',
    icon: 'map',
  },
  {
    path: '/poems',
    label: '诗词',
    icon: 'book',
  },
  {
    path: '/profile',
    label: '我的',
    icon: 'user',
  },
];

export default function BottomNav() {
  const pathname = usePathname() || '/';

  const isActive = (path: string) => {
    // 特殊处理：/places/* 也高亮「地图」Tab
    if (path === '/explore' && pathname.startsWith('/places/')) {
      return true;
    }
    return pathname === path || pathname.startsWith(path + '/');
  };

  return (
    <nav
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: '#fff',
        borderTop: '0.5px solid #E5E7EB',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        padding: '8px 0 16px',
        zIndex: 1000,
      }}
    >
      {NAV_ITEMS.map((item) => {
        const active = isActive(item.path);

        return (
          <Link
            key={item.path}
            href={item.path}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '3px',
              textDecoration: 'none',
            }}
          >
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke={active ? '#BA7517' : '#9CA3AF'}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {/* home */}
              {item.icon === 'home' && (
                <>
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                  <polyline points="9 22 9 12 15 12 15 22" />
                </>
              )}
              {/* map */}
              {item.icon === 'map' && (
                <>
                  <polygon points="1 6 1 22 8 18 16 22 21 18 21 2 16 6 8 2 1 6" />
                  <line x1="8" y1="2" x2="8" y2="18" />
                  <line x1="16" y1="6" x2="16" y2="22" />
                </>
              )}
              {/* book */}
              {item.icon === 'book' && (
                <>
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                </>
              )}
              {/* user */}
              {item.icon === 'user' && (
                <>
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </>
              )}
            </svg>
            <span
              style={{
                fontSize: '10px',
                letterSpacing: '0.03em',
                color: active ? '#BA7517' : '#9CA3AF',
              }}
            >
              {item.label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
