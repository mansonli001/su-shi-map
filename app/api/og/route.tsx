/**
 * OG 分享长图 v4.0
 * @vercel/og Edge Runtime 动态生成
 */

import { NextRequest } from 'next/server';
import { ImageResponse } from '@vercel/og';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  // 加载地点数据
  let placeName = '读苏轼·游神州';
  let modernName = '';
  let famousLine = '';

  if (id) {
    try {
      const res = await fetch(new URL(`/data/places-core.json`, request.url));
      const places = await res.json();
      const place = places.find((p: any) => p.id === id);
      if (place) {
        placeName = place.songName;
        modernName = place.modernName;
      }

      // 尝试加载详情获取诗句
      const detailRes = await fetch(new URL(`/data/places/${id}.json`, request.url));
      if (detailRes.ok) {
        const detail = await detailRes.json();
        if (detail.poems && detail.poems.length > 0) {
          famousLine = detail.poems[0].content.slice(0, 20) + '...';
        }
      }
    } catch (err) {
      console.error('加载 OG 数据失败', err);
    }
  }

  // 生成 OG 图片
  return new ImageResponse(
    (
      <div
        style={{
          width: '1200px',
          height: '630px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#F5E6C8',
          fontFamily: 'Noto Serif SC',
          padding: '60px',
        }}
      >
        {/* 标题 */}
        <div style={{ fontSize: '48px', color: '#8B6914', marginBottom: '24px', fontWeight: 'bold' }}>
          读苏轼·游神州
        </div>

        {/* 地点名 */}
        <div style={{ fontSize: '72px', color: '#1A1405', marginBottom: '16px', fontWeight: 'bold' }}>
          {placeName}
        </div>

        {/* 现代地名 */}
        {modernName && (
          <div style={{ fontSize: '32px', color: '#1A1405', opacity: 0.6, marginBottom: '32px' }}>
            {modernName}
          </div>
        )}

        {/* 诗句 */}
        {famousLine && (
          <div
            style={{
              fontSize: '28px',
              color: '#1A1405',
              opacity: 0.8,
              maxWidth: '800px',
              textAlign: 'center',
              lineHeight: '1.6',
            }}
          >
            {famousLine}
          </div>
        )}

        {/* 底部 */}
        <div style={{ position: 'absolute', bottom: '40px', fontSize: '24px', color: '#8B6914', opacity: 0.8 }}>
          扫码探索苏轼一生足迹 →
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
