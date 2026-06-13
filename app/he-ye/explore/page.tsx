/**
 * 贺野游中国 · 地图页
 */
'use client';

import dynamic from 'next/dynamic';

const HeyeMap = dynamic(() => import('@/components/map/HeyeMapContainer'), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center" style={{ background: 'var(--he-bg)' }}>
      <div className="text-center">
        <div className="text-4xl mb-4">🗺️</div>
        <p className="font-serif tracking-wider" style={{ color: 'var(--he-muted)' }}>地图加载中…</p>
      </div>
    </div>
  ),
});

export default function HeyeExplorePage() {
  return (
    <main className="relative h-screen overflow-hidden" style={{ background: 'var(--he-bg)' }}>
      <HeyeMap />
    </main>
  );
}
