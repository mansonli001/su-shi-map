/**
 * /profile — 个人中心页 v4.0「Ink & Path」
 * 米白宣纸 + 墨黑 + 朱砂红 视觉
 * 顶部：身份卡（米白 hairline）+ 苏轼全局数据 4 卡（引导探索）
 *      ↓ 用户行为数据 4 卡（收藏/打卡/成就/笔记）+ 打卡进度条
 * Tab 切换：成就墙 / 收藏诗词 / 我的笔记
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useSuShiStore } from '@/lib/store';
import AchievementWall from '@/components/AchievementWall';
import AchievementToast from '@/components/AchievementToast';
import SharePoster from '@/components/SharePoster';
import { achievements } from '@/lib/achievements';

// ink-path tokens
const INK = {
  parchment: '#fef8f6',
  parchmentSoft: '#f7f0ec',
  parchmentDeep: '#ede4dd',
  ink: '#1a1410',
  inkSoft: '#3d342e',
  inkLite: '#6b5d54',
  cinnabar: '#ba1a1a',
  cinnabarSoft: 'rgba(186, 26, 26, 0.08)',
  goldM: '#9b7a3a',
  goldLite: '#d1c4bc',
  hairline: 'rgba(209, 196, 188, 0.5)',
  hairlineSoft: 'rgba(209, 196, 188, 0.28)',
};

// 苏轼一生全局数据（v4 数据库实测值）
const SU_SHI_GLOBAL = {
  places: 234,   // 234 处足迹
  poems: 326,    // 326 首代表作
  routes: 20,    // 20 条主题路线
  stages: 6,     // 6 大人生阶段
};

export default function ProfilePage() {
  const { favoritePoems, checkinPlaces, userNotes, places, unlockedAchievements, checkAndUnlockAchievements } = useSuShiStore();
  const [activeTab, setActiveTab] = useState<'achievements' | 'favorites' | 'notes'>('achievements');

  // 初始化时检查成就
  useEffect(() => {
    if (places.length > 0) {
      checkAndUnlockAchievements();
    }
  }, [places, checkAndUnlockAchievements]);

  const stats = {
    favorites: favoritePoems.length,
    checkins: checkinPlaces.length,
    notes: userNotes.length,
    achievements: unlockedAchievements.length,
    totalPlaces: places.length || SU_SHI_GLOBAL.places,
  };

  const checkinProgress = stats.totalPlaces > 0
    ? Math.round((stats.checkins / stats.totalPlaces) * 100)
    : 0;

  return (
    <div
      style={{
        minHeight: '100vh',
        background: INK.parchment,
        paddingBottom: 'calc(80px + env(safe-area-inset-bottom))',
      }}
      className="font-wenkai"
    >
      {/* 成就解锁Toast */}
      <AchievementToast />

      {/* ===== 顶部：身份区（米白 hairline 卡）v9.3.5 改为横排：左 logo + 右文字 ===== */}
      <div
        style={{
          padding: '40px 16px 28px',
          background: INK.parchment,
          borderBottom: `1px solid ${INK.hairlineSoft}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '16px',
        }}
      >
        {/* v9.3.2 头像替换为品牌 logo（与首页一致）；v9.3.6 logo 缩到与右侧两行文字等高 */}
        <img
          src="/brand/logo.png"
          alt="行吟山河"
          width={40}
          height={40}
          style={{
            width: '40px',
            height: '40px',
            objectFit: 'contain',
            display: 'block',
            flexShrink: 0,
          }}
        />
        <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '4px' }}>
          <h1
            style={{
              fontSize: '20px',
              fontWeight: 600,
              color: INK.ink,
              margin: 0,
              letterSpacing: '0.06em',
              lineHeight: 1.2,
            }}
          >
            行吟山河
          </h1>
          <p
            style={{
              fontSize: '12px',
              color: INK.inkLite,
              letterSpacing: '0.1em',
              lineHeight: 1.2,
              margin: 0,
            }}
          >
            追随苏轼足迹，品读千古诗词
          </p>
        </div>
      </div>

      {/* ===== 苏轼全局数据 4 卡（引导探索） ===== */}
      <div style={{ padding: '20px 16px 12px' }}>
        <div
          style={{
            fontSize: '10px',
            color: INK.inkLite,
            letterSpacing: '0.24em',
            textTransform: 'uppercase',
            marginBottom: '10px',
            paddingLeft: '4px',
            fontFamily: '"Source Sans 3", sans-serif',
          }}
        >
          SU SHI · 一生数据
        </div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '8px',
          }}
        >
          {[
            { label: '足迹', value: SU_SHI_GLOBAL.places, unit: '处', href: '/explore' },
            { label: '诗词', value: SU_SHI_GLOBAL.poems, unit: '首', href: '/poems' },
            { label: '路线', value: SU_SHI_GLOBAL.routes, unit: '条', href: '/routes' },
            { label: '阶段', value: SU_SHI_GLOBAL.stages, unit: '幕', href: '/' },
          ].map((c) => (
            <Link
              key={c.label}
              href={c.href}
              style={{
                display: 'block',
                background: INK.parchment,
                border: `1px solid ${INK.hairline}`,
                borderRadius: '10px',
                padding: '14px 8px',
                textAlign: 'center',
                textDecoration: 'none',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = INK.cinnabar;
                e.currentTarget.style.background = INK.cinnabarSoft;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = INK.hairline;
                e.currentTarget.style.background = INK.parchment;
              }}
            >
              <div
                className="font-wenkai"
                style={{
                  fontSize: '24px',
                  fontWeight: 700,
                  color: INK.ink,
                  lineHeight: 1,
                }}
              >
                {c.value}
              </div>
              <div
                style={{
                  fontSize: '10px',
                  color: INK.inkLite,
                  marginTop: '6px',
                  letterSpacing: '0.06em',
                }}
              >
                {c.label} · {c.unit}
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ===== 我的探索 4 卡（用户行为数据） ===== */}
      <div style={{ padding: '8px 16px 20px' }}>
        <div
          style={{
            fontSize: '10px',
            color: INK.inkLite,
            letterSpacing: '0.24em',
            textTransform: 'uppercase',
            marginTop: '8px',
            marginBottom: '10px',
            paddingLeft: '4px',
            fontFamily: '"Source Sans 3", sans-serif',
          }}
        >
          MY · 我的探索
        </div>
        <div
          style={{
            background: INK.parchmentSoft,
            border: `1px solid ${INK.hairlineSoft}`,
            borderRadius: '12px',
            padding: '16px 12px',
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '4px',
          }}
        >
          {[
            { label: '收藏', value: stats.favorites, color: stats.favorites > 0 ? INK.cinnabar : INK.inkLite },
            { label: '打卡', value: stats.checkins, color: stats.checkins > 0 ? INK.cinnabar : INK.inkLite },
            { label: '成就', value: stats.achievements, color: stats.achievements > 0 ? INK.cinnabar : INK.inkLite },
            { label: '笔记', value: stats.notes, color: stats.notes > 0 ? INK.cinnabar : INK.inkLite },
          ].map((c) => (
            <div key={c.label} style={{ textAlign: 'center' }}>
              <div
                className="font-wenkai"
                style={{
                  fontSize: '22px',
                  fontWeight: 600,
                  color: c.color,
                  lineHeight: 1,
                }}
              >
                {c.value}
              </div>
              <div
                style={{
                  fontSize: '11px',
                  color: INK.inkLite,
                  marginTop: '6px',
                  letterSpacing: '0.04em',
                }}
              >
                {c.label}
              </div>
            </div>
          ))}
        </div>

        {/* 打卡进度条 */}
        <div style={{ marginTop: '14px' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px',
            }}
          >
            <span style={{ fontSize: '12px', color: INK.inkSoft, letterSpacing: '0.04em' }}>打卡进度</span>
            <span style={{ fontSize: '12px', color: stats.checkins > 0 ? INK.cinnabar : INK.inkLite, fontWeight: 600 }}>
              {stats.checkins} / {stats.totalPlaces} ({checkinProgress}%)
            </span>
          </div>
          <div
            style={{
              height: '6px',
              background: INK.parchmentDeep,
              borderRadius: '3px',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                background: `linear-gradient(90deg, ${INK.cinnabar} 0%, #d44343 100%)`,
                borderRadius: '3px',
                transition: 'width 0.5s ease-out',
                width: `${checkinProgress}%`,
              }}
            />
          </div>
          {stats.checkins === 0 && (
            <p
              style={{
                fontSize: '11px',
                color: INK.inkLite,
                marginTop: '10px',
                letterSpacing: '0.04em',
                fontStyle: 'italic',
              }}
            >
              还未启程 · 去
              <Link href="/explore" style={{ color: INK.cinnabar, fontWeight: 600, margin: '0 4px', textDecoration: 'underline' }}>
                水墨地图
              </Link>
              开始第一次打卡
            </p>
          )}
        </div>
      </div>

      {/* ===== Tab 切换 ===== */}
      <div
        style={{
          display: 'flex',
          background: INK.parchment,
          borderTop: `1px solid ${INK.hairlineSoft}`,
          borderBottom: `1px solid ${INK.hairlineSoft}`,
          overflowX: 'auto',
        }}
      >
        {[
          { k: 'achievements', label: '成就墙' },
          { k: 'favorites', label: '收藏诗词' },
          { k: 'notes', label: '我的笔记' },
        ].map((t) => {
          const isActive = activeTab === t.k;
          return (
            <button
              key={t.k}
              onClick={() => setActiveTab(t.k as typeof activeTab)}
              style={{
                flex: 1,
                minWidth: '100px',
                padding: '14px 4px',
                background: 'transparent',
                border: 'none',
                borderBottom: isActive ? `2px solid ${INK.cinnabar}` : '2px solid transparent',
                color: isActive ? INK.cinnabar : INK.inkLite,
                fontWeight: isActive ? 600 : 400,
                fontSize: '13px',
                letterSpacing: '0.08em',
                cursor: 'pointer',
                marginBottom: '-1px',
                transition: 'color 0.2s',
              }}
              className="font-wenkai"
            >
              {t.label}
            </button>
          );
        })}
      </div>

      {/* ===== 内容区 ===== */}
      <div style={{ padding: '16px' }}>
        {activeTab === 'achievements' ? (
          <div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px',
              }}
            >
              <h2 style={{ fontSize: '15px', fontWeight: 600, color: INK.ink, letterSpacing: '0.06em' }}>
                成就墙
              </h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '12px', color: INK.inkLite }}>
                  {stats.achievements} / {achievements.length} 已解锁
                </span>
                <SharePoster type="collection" />
              </div>
            </div>
            <AchievementWall />
          </div>
        ) : activeTab === 'favorites' ? (
          favoritePoems.length === 0 ? (
            <EmptyHint
              icon="📚"
              title="还没有收藏诗词"
              hint="在诗词页面点击「♥」按钮，保存你喜欢的作品"
              ctaLabel="去诗词集"
              ctaHref="/poems"
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {favoritePoems.map((poem) => (
                <Link
                  key={poem.poemId}
                  href={`/poems/${poem.poemId}`}
                  style={{
                    display: 'block',
                    padding: '14px 16px',
                    background: INK.parchment,
                    border: `1px solid ${INK.hairline}`,
                    borderRadius: '12px',
                    textDecoration: 'none',
                    transition: 'border-color 0.2s, background 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = INK.cinnabar;
                    e.currentTarget.style.background = INK.cinnabarSoft;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = INK.hairline;
                    e.currentTarget.style.background = INK.parchment;
                  }}
                >
                  <h3
                    style={{
                      fontSize: '15px',
                      fontWeight: 600,
                      color: INK.ink,
                      marginBottom: '4px',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {poem.title}
                  </h3>
                  <p style={{ fontSize: '11px', color: INK.inkLite }}>
                    {new Date(poem.addedAt).toLocaleDateString('zh-CN')}
                  </p>
                </Link>
              ))}
            </div>
          )
        ) : (
          userNotes.length === 0 ? (
            <EmptyHint
              icon="📝"
              title="还没有笔记"
              hint="在地点详情页或诗词页面添加笔记"
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {userNotes.map((note) => (
                <div
                  key={note.id}
                  style={{
                    padding: '14px 16px',
                    background: INK.parchment,
                    border: `1px solid ${INK.hairline}`,
                    borderRadius: '12px',
                  }}
                >
                  <p
                    style={{
                      fontSize: '14px',
                      color: INK.inkSoft,
                      lineHeight: 1.7,
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
                        color: INK.cinnabar,
                        background: INK.cinnabarSoft,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        letterSpacing: '0.06em',
                      }}
                    >
                      {note.targetType === 'poem' ? '诗词' : '地点'}
                    </span>
                    <span style={{ fontSize: '11px', color: INK.inkLite }}>
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

// ===== 空态提示组件 =====
function EmptyHint(props: {
  icon: string;
  title: string;
  hint: string;
  ctaLabel?: string;
  ctaHref?: string;
}) {
  return (
    <div
      style={{
        textAlign: 'center',
        padding: '48px 20px',
        color: INK.inkLite,
      }}
    >
      <div style={{ fontSize: '40px', marginBottom: '16px', opacity: 0.6 }}>{props.icon}</div>
      <p style={{ fontSize: '14px', marginBottom: '8px', color: INK.inkSoft }}>
        {props.title}
      </p>
      <p style={{ fontSize: '12px' }}>
        {props.hint}
      </p>
      {props.ctaLabel && props.ctaHref && (
        <Link
          href={props.ctaHref}
          style={{
            display: 'inline-block',
            marginTop: '24px',
            padding: '12px 36px',
            background: INK.ink,
            color: INK.parchment,
            borderRadius: '8px',
            textDecoration: 'none',
            fontSize: '13px',
            letterSpacing: '0.12em',
            fontWeight: 600,
            transition: 'background 0.2s',
          }}
          className="font-wenkai"
          onMouseEnter={(e) => (e.currentTarget.style.background = INK.cinnabar)}
          onMouseLeave={(e) => (e.currentTarget.style.background = INK.ink)}
        >
          {props.ctaLabel}
        </Link>
      )}
    </div>
  );
}
