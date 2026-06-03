/**
 * /profile — 个人中心页
 * 完全按照设计稿实现
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useSuShiStore } from '@/lib/store';

export default function ProfilePage() {
  const { favoritePoems, checkinPlaces, userNotes } = useSuShiStore();
  const [activeTab, setActiveTab] = useState<'favorites' | 'notes'>('favorites');

  const stats = {
    favorites: favoritePoems.length,
    checkins: checkinPlaces.length,
    notes: userNotes.length,
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#F1EFE8',
        paddingBottom: 'calc(64px + env(safe-area-inset-bottom))',
      }}
    >
      {/* 头部信息 */}
      <div
        style={{
          background: '#1A1008',
          padding: '32px 16px 24px',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          {/* 头像 */}
          <div
            style={{
              width: '72px',
              height: '72px',
              borderRadius: '50%',
              background: '#BA7517',
              margin: '0 auto 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '28px',
              color: '#FAF6F0',
              fontWeight: '600',
            }}
          >
            行
          </div>
          <h1 style={{ fontSize: '18px', fontWeight: '600', color: '#FAF6F0', marginBottom: '4px' }}>
            行吟山河
          </h1>
          <p style={{ fontSize: '12px', color: '#888780', letterSpacing: '0.08em' }}>
            追随苏轼足迹，品读千古诗词
          </p>
        </div>

        {/* 统计卡片 */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-around',
            marginTop: '24px',
            padding: '16px',
            background: 'rgba(250, 199, 117, 0.06)',
            borderRadius: '12px',
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: '22px',
                fontWeight: '600',
                color: '#FAC775',
              }}
            >
              {stats.favorites}
            </div>
            <div
              style={{
                fontSize: '11px',
                color: '#888780',
                marginTop: '4px',
              }}
            >
              收藏诗词
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: '22px',
                fontWeight: '600',
                color: '#FAC775',
              }}
            >
              {stats.checkins}
            </div>
            <div
              style={{
                fontSize: '11px',
                color: '#888780',
                marginTop: '4px',
              }}
            >
              打卡地点
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div
              style={{
                fontSize: '22px',
                fontWeight: '600',
                color: '#FAC775',
              }}
            >
              {stats.notes}
            </div>
            <div
              style={{
                fontSize: '11px',
                color: '#888780',
                marginTop: '4px',
              }}
            >
              个人笔记
            </div>
          </div>
        </div>
      </div>

      {/* Tab切换 */}
      <div
        style={{
          display: 'flex',
          background: '#fff',
          borderBottom: '0.5px solid #E5E7EB',
        }}
      >
        <button
          onClick={() => setActiveTab('favorites')}
          style={{
            flex: 1,
            padding: '12px 4px',
            background: 'transparent',
            border: 'none',
            borderBottom:
              activeTab === 'favorites'
                ? '2px solid #BA7517'
                : '2px solid transparent',
            color: activeTab === 'favorites' ? '#BA7517' : '#9CA3AF',
            fontWeight: activeTab === 'favorites' ? '600' : 'normal',
            fontSize: '12px',
            letterSpacing: '0.03em',
            cursor: 'pointer',
            marginBottom: '-0.5px',
          }}
        >
          收藏诗词
        </button>
        <button
          onClick={() => setActiveTab('notes')}
          style={{
            flex: 1,
            padding: '12px 4px',
            background: 'transparent',
            border: 'none',
            borderBottom:
              activeTab === 'notes'
                ? '2px solid #BA7517'
                : '2px solid transparent',
            color: activeTab === 'notes' ? '#BA7517' : '#9CA3AF',
            fontWeight: activeTab === 'notes' ? '600' : 'normal',
            fontSize: '12px',
            letterSpacing: '0.03em',
            cursor: 'pointer',
            marginBottom: '-0.5px',
          }}
        >
          我的笔记
        </button>
      </div>

      {/* 内容区域 */}
      <div style={{ padding: '16px' }}>
        {activeTab === 'favorites' ? (
          favoritePoems.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#9CA3AF',
              }}
            >
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📚</div>
              <p style={{ fontSize: '14px', marginBottom: '8px' }}>
                还没有收藏诗词
              </p>
              <p style={{ fontSize: '12px' }}>
                在诗词页面点击「♥」按钮，保存你喜欢的作品
              </p>
              <Link
                href="/poems"
                style={{
                  display: 'inline-block',
                  marginTop: '20px',
                  padding: '12px 40px',
                  background: '#BA7517',
                  color: '#FAF6F0',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  fontSize: '14px',
                  letterSpacing: '0.12em',
                  fontWeight: '600',
                }}
              >
                去浏览
              </Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {favoritePoems.map((poem) => (
                <Link
                  key={poem.poemId}
                  href={`/poems/${poem.poemId}`}
                  style={{
                    display: 'block',
                    padding: '14px 16px',
                    background: '#fff',
                    border: '0.5px solid #E5E7EB',
                    borderRadius: '12px',
                    textDecoration: 'none',
                  }}
                >
                  <h3
                    style={{
                      fontSize: '15px',
                      fontWeight: '600',
                      color: '#1A1008',
                      marginBottom: '4px',
                    }}
                  >
                    {poem.title}
                  </h3>
                  <p style={{ fontSize: '11px', color: '#9CA3AF' }}>
                    {new Date(poem.addedAt).toLocaleDateString('zh-CN')}
                  </p>
                </Link>
              ))}
            </div>
          )
        ) : (
          userNotes.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#9CA3AF',
              }}
            >
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📝</div>
              <p style={{ fontSize: '14px', marginBottom: '8px' }}>还没有笔记</p>
              <p style={{ fontSize: '12px' }}>
                在地点详情页或诗词页面添加笔记
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {userNotes.map((note) => (
                <div
                  key={note.id}
                  style={{
                    padding: '14px 16px',
                    background: '#fff',
                    border: '0.5px solid #E5E7EB',
                    borderRadius: '12px',
                  }}
                >
                  <p
                    style={{
                      fontSize: '14px',
                      color: '#3D2B1F',
                      lineHeight: '1.7',
                      marginBottom: '10px',
                    }}
                  >
                    {note.content}
                  </p>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span
                      style={{
                        fontSize: '10px',
                        color: '#BA7517',
                        background: 'rgba(186, 117, 23, 0.1)',
                        padding: '2px 8px',
                        borderRadius: '4px',
                      }}
                    >
                      {note.targetType === 'poem' ? '诗词' : '地点'}
                    </span>
                    <span style={{ fontSize: '11px', color: '#9CA3AF' }}>
                      {new Date(note.createdAt).toLocaleDateString('zh-CN')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  );
}
