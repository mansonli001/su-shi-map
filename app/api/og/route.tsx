/**
 * OG 分享图 v5.0 - 支持v4数据
 * 使用Vercel OG生成动态分享图片
 */

import { NextRequest } from 'next/server';
import { ImageResponse } from '@vercel/og';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const id = searchParams.get('id');

  // 默认值
  let placeName = '读苏轼·游神州';
  let modernName = '苏轼一生足迹交互式地图';
  let ancientName = '';
  let summary = '';
  let famousLine = '';
  let author = '';

  if (id) {
    try {
      // 加载v4 places-index
      const indexRes = await fetch(new URL(`/data-v4/places-index.json`, request.url));
      if (indexRes.ok) {
        const indexData = await indexRes.json();
        const place = indexData.places?.find((p: any) => p.id === id);
        if (place) {
          ancientName = place.ancient_name || place.songName || '';
          modernName = place.modern_name || '';
          summary = place.summary || '';

          // 如果有诗词，提取名句
          if (place.poems && place.poems.length > 0) {
            const poem = place.poems[0];
            famousLine = poem.content?.slice(0, 25) || '';
            famousLine = poem.famousLine || poem.coreVerse || famousLine;
            author = poem.author || '苏轼';
          } else if (place.related_poems && place.related_poems.length > 0) {
            // 尝试从相关诗词获取
            const poemId = place.related_poems[0];
            const poemRes = await fetch(new URL(`/data-v4/poems/${poemId}.json`, request.url));
            if (poemRes.ok) {
              const poem = await poemRes.json();
              famousLine = poem.famousQuotes?.[0] || poem.paragraphs?.[0]?.slice(0, 25) || '';
              author = poem.author || '苏轼';
            }
          }
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
          background: 'linear-gradient(180deg, #F5E6C8 0%, #EBD9B8 100%)',
          padding: '60px',
          position: 'relative',
        }}
      >
        {/* 顶部装饰线 */}
        <div style={{
          position: 'absolute',
          top: '0',
          left: '0',
          right: '0',
          height: '8px',
          background: 'linear-gradient(90deg, #BA7517, #FAC775, #BA7517)',
        }} />

        {/* 主标题 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '40px',
        }}>
          <div style={{
            fontSize: '36px',
            color: '#8B6914',
            fontWeight: 'bold',
            letterSpacing: '0.1em',
          }}>
            行吟山河
          </div>
          <div style={{
            width: '2px',
            height: '24px',
            background: '#8B6914',
            margin: '0 20px',
            opacity: 0.5,
          }} />
          <div style={{
            fontSize: '24px',
            color: '#8B6914',
            opacity: 0.8,
          }}>
            苏轼足迹地图
          </div>
        </div>

        {/* 地点名 - 核心展示 */}
        <div style={{
          fontSize: id ? '72px' : '64px',
          color: '#1A1405',
          fontWeight: 'bold',
          marginBottom: '16px',
          fontFamily: 'serif',
        }}>
          {id ? ancientName : '苏轼一生'}
        </div>

        {/* 现代地名 */}
        {modernName && (
          <div style={{
            fontSize: '28px',
            color: '#1A1405',
            opacity: 0.6,
            marginBottom: '24px',
          }}>
            {modernName}
          </div>
        )}

        {/* 诗句展示 */}
        {famousLine && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginTop: '20px',
          }}>
            <div style={{
              width: '4px',
              height: '48px',
              background: '#BA7517',
              marginRight: '20px',
            }} />
            <div style={{
              fontSize: '26px',
              color: '#1A1405',
              opacity: 0.85,
              maxWidth: '900px',
              lineHeight: '1.5',
            }}>
              {famousLine}
              {author && (
                <span style={{
                  fontSize: '20px',
                  color: '#8B6914',
                  marginLeft: '20px',
                  opacity: 0.8,
                }}>
                  —— {author}
                </span>
              )}
            </div>
          </div>
        )}

        {/* 底部信息 */}
        <div style={{
          position: 'absolute',
          bottom: '40px',
          left: '60px',
          right: '60px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div style={{
            fontSize: '20px',
            color: '#8B6914',
          }}>
            su-shi.starfluxes.com
          </div>
          <div style={{
            fontSize: '22px',
            color: '#8B6914',
            display: 'flex',
            alignItems: 'center',
          }}>
            扫码探索 →
          </div>
        </div>

        {/* 右下角装饰 */}
        <div style={{
          position: 'absolute',
          bottom: '40px',
          right: '60px',
          fontSize: '14px',
          color: '#8B6914',
          opacity: 0.5,
        }}>
          {id ? `地点: ${id}` : '交互式数字地图'}
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}