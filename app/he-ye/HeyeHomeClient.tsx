/**
 * 贺野首页 · 客户端交互组件
 * 精选轮播（水平滚动 + snap）
 */
'use client';

import { useRef, useCallback } from 'react';
import Link from 'next/link';
import type { HeyeLocation } from '@/types/heye';

// 精选地点图片映射（本地下载的高质量风景图）
const FEATURED_IMAGES: Record<string, string> = {
  HY150: '/heye-map/featured/HY150.jpg',
  HY211: '/heye-map/featured/HY211.jpg',
  HY059: '/heye-map/featured/HY059.jpg',
  HY202: '/heye-map/featured/HY202.jpg',
  HY298: '/heye-map/featured/HY298.jpg',
  HY133: '/heye-map/featured/HY133.jpg',
  HY038: '/heye-map/featured/HY038.jpg',
  HY117: '/heye-map/featured/HY117.jpg',
  HY275: '/heye-map/featured/HY275.jpg',
  HY213: '/heye-map/featured/HY213.jpg',
  HY220: '/heye-map/featured/HY220.jpg',
  HY057: '/heye-map/featured/HY057.jpg',
  HY207: '/heye-map/featured/HY207.jpg',
  HY093: '/heye-map/featured/HY093.jpg',
  HY161: '/heye-map/featured/HY161.jpg',
  HY229: '/heye-map/featured/HY229.jpg',
  HY273: '/heye-map/featured/HY273.jpg',
  HY297: '/heye-map/featured/HY297.jpg',
  HY040: '/heye-map/featured/HY040.jpg',
  HY063: '/heye-map/featured/HY063.jpg',
  HY260: '/heye-map/featured/HY260.jpg',
  HY276: '/heye-map/featured/HY276.jpg',
  HY006: '/heye-map/featured/HY006.jpg',
  HY020: '/heye-map/featured/HY020.jpg',
  HY191: '/heye-map/featured/HY191.jpg',
  HY209: '/heye-map/featured/HY209.jpg',
};

export default function HeyeHomeClient({ featured }: { featured: HeyeLocation[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);
  const startX = useRef(0);
  const scrollLeft = useRef(0);
  const hasMoved = useRef(false);

  // 鼠标拖拽（桌面端）
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    const el = scrollRef.current;
    if (!el) return;
    isDragging.current = true;
    hasMoved.current = false;
    startX.current = e.pageX - el.offsetLeft;
    scrollLeft.current = el.scrollLeft;
  }, []);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging.current) return;
    e.preventDefault();
    const el = scrollRef.current;
    if (!el) return;
    const x = e.pageX - el.offsetLeft;
    const walk = x - startX.current;
    if (Math.abs(walk) > 3) hasMoved.current = true;
    el.scrollLeft = scrollLeft.current - walk;
  }, []);

  const onMouseUp = useCallback(() => {
    isDragging.current = false;
  }, []);

  // 触摸拖拽（Android/iOS）
  const onTouchStart = useCallback((e: React.TouchEvent) => {
    const el = scrollRef.current;
    if (!el) return;
    startX.current = e.touches[0].pageX - el.offsetLeft;
    scrollLeft.current = el.scrollLeft;
  }, []);

  const onTouchMove = useCallback((e: React.TouchEvent) => {
    const el = scrollRef.current;
    if (!el) return;
    const x = e.touches[0].pageX - el.offsetLeft;
    el.scrollLeft = scrollLeft.current - (x - startX.current);
  }, []);

  if (featured.length === 0) return null;

  return (
    <div className="he-featured">
      <div className="he-featured-scroll" ref={scrollRef}
        onMouseDown={onMouseDown} onMouseMove={onMouseMove} onMouseUp={onMouseUp} onMouseLeave={onMouseUp}
        onTouchStart={onTouchStart} onTouchMove={onTouchMove}
      >
        {featured.map((loc) => {
          const imgSrc = FEATURED_IMAGES[loc.id] || loc.imageUrl;
          return (
            <div key={loc.id} className="he-featured-card">
              <div className="he-featured-img">
                {imgSrc ? (
                  <img src={imgSrc} alt={loc.placeName} loading="lazy" />
                ) : (
                  <div className="he-featured-placeholder" />
                )}
              </div>
              <div className="he-featured-body">
                <div className="he-featured-province">{loc.city} · {loc.province}</div>
                <div className="he-featured-name">{loc.placeName}</div>
                <div className="he-featured-visits">到访 {loc.visitCount} 次</div>
                <div className="he-featured-excerpt">{loc.excerpt}</div>
                {loc.snacks.length > 0 && (
                  <div className="he-featured-snacks">
                    {loc.snacks.slice(0, 3).map((s) => (
                      <span key={s} className="he-snack-tag">{s}</span>
                    ))}
                  </div>
                )}
                <Link href={`/he-ye/explore?focus=${loc.id}`} className="he-featured-link">
                  查看详情 →
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
