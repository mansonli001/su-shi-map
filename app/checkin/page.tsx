/**
 * /checkin — 打卡足迹页
 * 完全按照设计稿实现
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useSuShiStore } from '@/lib/store';

export default function CheckinPage() {
  const { checkinPlaces, removeCheckin, updateCheckinNote } = useSuShiStore();
  const [editingNote, setEditingNote] = useState<string | null>(null);
  const [noteText, setNoteText] = useState('');

  const handleEditNote = (placeId: string, currentNote: string = '') => {
    setEditingNote(placeId);
    setNoteText(currentNote);
  };

  const handleSaveNote = (placeId: string) => {
    updateCheckinNote(placeId, noteText);
    setEditingNote(null);
    setNoteText('');
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#F1EFE8',
        paddingBottom: 'calc(64px + env(safe-area-inset-bottom))',
      }}
    >
      {/* 头部 */}
      <div
        style={{
          background: '#1A1008',
          padding: '24px 16px 20px',
        }}
      >
        <h1
          style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#FAC775',
            letterSpacing: '0.15em',
          }}
        >
          我的足迹
        </h1>
        <p style={{ fontSize: '12px', color: '#888780', marginTop: '4px' }}>
          已打卡 {checkinPlaces.length} 个地点
        </p>
      </div>

      {/* 打卡列表 */}
      <div style={{ padding: '16px' }}>
        {checkinPlaces.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '40px 20px',
              color: '#9CA3AF',
            }}
          >
            <div
              style={{
                fontSize: '48px',
                marginBottom: '16px',
              }}
            >
              📍
            </div>
            <p style={{ fontSize: '14px', marginBottom: '8px' }}>
              还没有打卡记录
            </p>
            <p style={{ fontSize: '12px' }}>
              在地图页面点击地点卡片上的「打卡」按钮，记录你的足迹
            </p>
            <Link
              href="/explore"
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
              去探索
            </Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {checkinPlaces.map((checkin) => (
              <div
                key={checkin.placeId}
                style={{
                  background: '#fff',
                  border: '0.5px solid #E5E7EB',
                  borderRadius: '12px',
                  padding: '16px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '12px',
                  }}
                >
                  <div>
                    <h3
                      style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#1A1008',
                        marginBottom: '4px',
                      }}
                    >
                      {checkin.placeName}
                    </h3>
                    <p style={{ fontSize: '11px', color: '#9CA3AF' }}>
                      {new Date(checkin.checkinAt).toLocaleDateString('zh-CN')}
                    </p>
                  </div>
                  <button
                    onClick={() => removeCheckin(checkin.placeId)}
                    style={{
                      padding: '6px 12px',
                      background: 'transparent',
                      border: '0.5px solid #E5E7EB',
                      borderRadius: '6px',
                      fontSize: '11px',
                      color: '#9CA3AF',
                      cursor: 'pointer',
                    }}
                  >
                    取消
                  </button>
                </div>

                {/* 笔记区域 */}
                {editingNote === checkin.placeId ? (
                  <div>
                    <textarea
                      value={noteText}
                      onChange={(e) => setNoteText(e.target.value)}
                      placeholder="写下你的感想..."
                      style={{
                        width: '100%',
                        padding: '12px',
                        border: '0.5px solid #E5E7EB',
                        borderRadius: '8px',
                        fontSize: '14px',
                        minHeight: '80px',
                        resize: 'vertical',
                        marginBottom: '10px',
                        fontFamily: "'LXGW WenKai','Songti SC','STSong','SimSun',serif",
                      }}
                    />
                    <div
                      style={{
                        display: 'flex',
                        gap: '10px',
                        justifyContent: 'flex-end',
                      }}
                    >
                      <button
                        onClick={() => setEditingNote(null)}
                        style={{
                          padding: '8px 20px',
                          background: '#F1EFE8',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '13px',
                          color: '#5F5E5A',
                          cursor: 'pointer',
                        }}
                      >
                        取消
                      </button>
                      <button
                        onClick={() => handleSaveNote(checkin.placeId)}
                        style={{
                          padding: '8px 20px',
                          background: '#BA7517',
                          color: '#FAF6F0',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '13px',
                          cursor: 'pointer',
                        }}
                      >
                        保存
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    {checkin.note ? (
                      <p
                        style={{
                          fontSize: '13px',
                          color: '#3D2B1F',
                          lineHeight: '1.8',
                          marginBottom: '10px',
                        }}
                      >
                        {checkin.note}
                      </p>
                    ) : null}
                    <button
                      onClick={() => handleEditNote(checkin.placeId, checkin.note)}
                      style={{
                        padding: '6px 12px',
                        background: 'transparent',
                        border: '0.5px solid #BA7517',
                        borderRadius: '6px',
                        fontSize: '11px',
                        color: '#BA7517',
                        cursor: 'pointer',
                      }}
                    >
                      {checkin.note ? '编辑笔记' : '添加笔记'}
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
