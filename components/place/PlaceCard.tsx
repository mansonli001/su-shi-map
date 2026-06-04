/**
 * PlaceCard v6.0「行吟山河」
 * 设计稿 ④简介卡 风格：
 *   - 顶部 4 类色芯片（出生/任职/贬谪/游览）
 *   - 大字宋代地名（金色 m）
 *   - 时间区段（duration_summary.duration_label）
 *   - famous_line 金色引语（quote-gold）
 *   - 三按钮：详情 / 诗词数量 / 导航
 *   - 数据切到 v4 /data-v4/places/{P_id}.json
 */

'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { useSuShiStore } from '@/lib/store';
import { PlaceCore } from '@/types';
import Link from 'next/link';
import { searchNearbyFood, getSushiSpecialFoods, type AMapPOIResult, type FoodItem } from '@/lib/food-search';

interface FamousLine {
  quote: string;
  source: string;
  from: string;
}

interface DurationSummary {
  first_year: number;
  last_year: number;
  span_years: number;
  duration_label: string;
  related_route_count: number;
  stage_ids: string[];
}

interface V4PlaceFull extends PlaceCore {
  background?: string;
  famous_line?: FamousLine;
  duration_summary?: DurationSummary;
  periods?: Array<{ period: string; title: string; description: string }>;
  global_events?: any[];
  global_works?: Array<{
    id?: string;
    title: string;
    type?: string;
    note?: string;
    excerpt?: string;
    fullText?: string;
    background?: string;
    year?: number | string;
    year_estimate?: number;
    route_id?: string;
  }>;
  route_events?: Record<string, any[]>;
  memorial_sites?: any[];
  foods?: any[];
  transport?: any[];
  related_routes?: string[];
  ancient_name?: string;
  modern_name?: string;
  tags?: string[];
  _auto_generated?: boolean;
}

const TYPE_LABEL: Record<string, string> = {
  birth: '出生地',
  office: '任职地',
  exile: '贬谪地',
  tour: '游览地',
  friend: '友人交往',
  burial: '终老地',
};

const TYPE_CHIP: Record<string, { bg: string; fg: string; border: string }> = {
  birth: { bg: 'rgba(8,80,65,0.15)', fg: '#085041', border: 'rgba(93,202,165,0.5)' },
  office: { bg: 'rgba(12,68,124,0.12)', fg: '#0C447C', border: 'rgba(133,183,235,0.5)' },
  exile: { bg: 'rgba(113,43,19,0.13)', fg: '#712B13', border: 'rgba(240,153,123,0.5)' },
  tour: { bg: 'rgba(99,56,6,0.12)', fg: '#633806', border: 'rgba(201,151,90,0.5)' },
  friend: { bg: 'rgba(186,117,23,0.12)', fg: '#BA7517', border: 'rgba(250,199,117,0.5)' },
  burial: { bg: 'rgba(60,40,30,0.15)', fg: '#3D2B1F', border: 'rgba(120,90,60,0.5)' },
};

// 七阶段中文名（PlaceCore.stage 映射）
const STAGE_NAME: Record<string, string> = {
  youth: '眉山少年',
  early_career: '入京初仕',
  first_exile: '黄州四年',
  middle_career: '翰林侍从',
  second_exile: '岭南三年',
  third_exile: '儋耳三年',
  final_journey: '北归长眠',
  // v4 stage_id 兜底
  S1: '眉山·少年',
  S2: '汴京·宦游',
  S3: '黄州·东坡',
  S4: '元祐·还朝',
  S5: '惠儋·南贬',
  S6: '北归·终老',
};

interface PlaceCardProps {
  place: PlaceCore;
}

export default function PlaceCard({ place }: PlaceCardProps) {
  const { isCardOpen, closeCard, addCheckin, removeCheckin, isPlaceCheckedIn } = useSuShiStore();
  const [expanded, setExpanded] = useState(false);
  const [showDetail, setShowDetail] = useState<string | false>(false);
  const [detail, setDetail] = useState<V4PlaceFull | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showCheckinSuccess, setShowCheckinSuccess] = useState(false);

  // 卡片打开时加载详情（v4 路径）
  // 修复 v6.1: 加 AbortController 防快速切换地点的请求竞态；去掉 ?t= 让浏览器/Vercel CDN 正常缓存
  useEffect(() => {
    if (!place || !isCardOpen) return;
    setDetailLoading(true);
    setShowDetail(false);
    setDetail(null); // 切换地点时清掉旧详情，避免短暂错位
    const ctrl = new AbortController();
    fetch(`/data-v4/places/${place.id}.json`, { signal: ctrl.signal })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) setDetail(data as V4PlaceFull);
      })
      .catch((err) => {
        if (err?.name !== 'AbortError') {
          // 真正的网络/解析错误才打印，AbortError 是正常切换信号
          console.warn('[PlaceCard] 详情加载失败', place.id, err);
        }
      })
      .finally(() => setDetailLoading(false));
    return () => ctrl.abort();
  }, [place, isCardOpen]);

  const handleDragEnd = (_event: any, info: PanInfo) => {
    if (info.offset.y > 100) closeCard();
  };

  const chip = TYPE_CHIP[place.type] || TYPE_CHIP.tour;
  const typeLabel = TYPE_LABEL[place.type] || '途经';

  // 字段优先用 detail（v4），兜底 place（v3 PlaceCore）
  const ancient = (detail?.ancient_name as any) || place.songName;
  const modern = (detail?.modern_name as any) || place.modernName;
  const duration = detail?.duration_summary?.duration_label || '';
  const famous = detail?.famous_line;
  const summary = detail?.background || (place as any).summary || '';
  const works = detail?.global_works || [];
  const memorialSites = detail?.memorial_sites || [];
  const foods = detail?.foods || [];

  return (
    <AnimatePresence>
      {isCardOpen && place && (
        <>
          {/* 遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="framer-overlay"
            onClick={closeCard}
          />

          {/* 半屏卡片 — BUG-NAV-002 v2 真修复：固定高度 + flex 让浏览器自己算可滚动空间
              v1 失效根因：
                外层 maxHeight 按全屏算（≈92vh），但 collapsed 状态 translateY=38% 把卡片往下推 35vh，
                实际可见只剩 ≈57vh；内层滚动容器仍按全屏 maxHeight 渲染 → 浏览器判定"未溢出"→ 滑不动。
              v2 改造：
                1) 外层固定 height:92dvh（不是 maxHeight）+ flex flex-col，translateY 不再影响 layout；
                2) 内层用 flex-1 min-h-0 overflow-y-auto，浏览器自动 = 92dvh - 拖拽手柄；
                3) 100dvh 解决 iOS Safari 地址栏弹收时高度跳变；
                4) .sheet-scroll = -webkit-overflow-scrolling:touch + overscroll-behavior:contain 防穿透。 */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: expanded ? '8%' : '38%' }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 280 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            onDragEnd={handleDragEnd}
            className="fixed left-0 right-0 bottom-0 z-50 md:max-w-2xl md:mx-auto flex flex-col"
            style={{
              background: 'var(--card)',
              borderRadius: '18px 18px 0 0',
              boxShadow: '0 -10px 40px rgba(26,16,8,0.18)',
              // 固定高度（不是 maxHeight）：dvh 适配移动端动态视口，扣掉顶部安全区 + 底部安全区
              height: 'calc(92dvh - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px))',
              maxHeight: 'calc(100dvh - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px))',
            }}
          >
            {/* 拖拽手柄（固定高度，不参与滚动） */}
            <div
              onPointerDown={() => setExpanded((v) => !v)}
              className="cursor-grab active:cursor-grabbing pt-3 pb-2 shrink-0"
            >
              <div className="w-10 h-1 rounded-full mx-auto" style={{ background: 'rgba(186,117,23,0.4)' }} />
            </div>

            {/* 内容区：flex-1 撑满 + min-h-0 让 overflow 生效 + sheet-scroll iOS 顺滑滚动 */}
            <div
              className="px-5 pb-6 flex-1 min-h-0 overflow-y-auto sheet-scroll"
              style={{ WebkitOverflowScrolling: 'touch' }}
            >
              {/* ====== 详情视图 ====== */}
              {showDetail ? (
                <DetailView
                  detail={detail}
                  works={works}
                  memorialSites={memorialSites}
                  foods={foods}
                  initialTab={showDetail as 'story' | 'works' | 'travel'}
                  onBack={() => setShowDetail(false)}
                  place={place}
                />
              ) : (
                <>
                  {/* 头部：类型芯片 + 时间标签 */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className="text-[10px] tracking-[0.18em] font-wenkai px-2.5 py-1 rounded-full font-medium"
                        style={{
                          background: chip.bg,
                          color: chip.fg,
                          border: `0.5px solid ${chip.border}`,
                        }}
                      >
                        {typeLabel}
                      </span>
                      {duration && (
                        <span className="text-[10px] tracking-[0.08em] text-gold-m font-wenkai">
                          {duration}
                        </span>
                      )}
                    </div>
                    {detailLoading && (
                      <span className="text-[10px] text-ink-lt/50">加载中…</span>
                    )}
                  </div>

                  {/* 标题区 */}
                  <h2 className="font-wenkai text-[28px] font-semibold text-ink leading-none tracking-[0.04em] mb-1">
                    {ancient}
                  </h2>
                  <p className="font-wenkai text-[12px] text-ink-lt mb-3 tracking-[0.06em]">
                    {modern}
                  </p>

                  {/* 简介 */}
                  {summary ? (
                    <p className="font-wenkai text-[13px] text-ink/75 leading-[1.95] mb-4">
                      {summary.length > 120 ? summary.slice(0, 118) + '…' : summary}
                    </p>
                  ) : (
                    <p className="font-wenkai text-[12.5px] text-ink-lt/70 leading-[1.9] mb-4 italic">
                      {place.tag ? `「${place.tag}」` : '途经地'}
                      ·
                      苏轼曾经此地，详细事迹待补充。
                    </p>
                  )}

                  {/* 名句金色引语（设计稿 .quote-gold） */}
                  {famous && famous.quote && (
                    <div className="quote-gold mb-4">
                      <div className="text-[10px] text-gold-m tracking-[0.16em] mb-1">
                        名句
                      </div>
                      <div className="font-wenkai text-[14px] tracking-[0.04em]">
                        {famous.quote}
                      </div>
                      {famous.source && (
                        <div className="font-wenkai text-[11px] text-ink-mid mt-1.5">
                          ——《{famous.source}》
                        </div>
                      )}
                    </div>
                  )}

                  {/* 基础信息块（任何 place 都有，避免空白卡）*/}
                  <div
                    className="rounded-lg p-3 mb-4 grid grid-cols-2 gap-2 text-[11px]"
                    style={{
                      background: 'rgba(186,117,23,0.05)',
                      border: '0.5px solid rgba(186,117,23,0.15)',
                    }}
                  >
                    <div>
                      <div className="text-ink-lt/60 tracking-wider mb-0.5">所属阶段</div>
                      <div className="font-wenkai text-ink/85">
                        {STAGE_NAME[place.stage] || place.stage || '—'}
                      </div>
                    </div>
                    <div>
                      <div className="text-ink-lt/60 tracking-wider mb-0.5">主路线</div>
                      <div className="font-wenkai text-ink/85">
                        {place.routeId || '—'}
                        {place.routeOrder ? ` · 第 ${place.routeOrder} 站` : ''}
                      </div>
                    </div>
                    <div>
                      <div className="text-ink-lt/60 tracking-wider mb-0.5">坐标</div>
                      <div className="font-mono text-[10px] text-ink/75">
                        {place.lat?.toFixed(3)}, {place.lng?.toFixed(3)}
                      </div>
                    </div>
                    <div>
                      <div className="text-ink-lt/60 tracking-wider mb-0.5">数据</div>
                      <div className="font-wenkai text-ink/75">
                        {detail?._auto_generated
                          ? '骨架（待充实）'
                          : works.length > 0
                            ? `${works.length} 部作品`
                            : detail
                              ? '已收录'
                              : '加载中…'}
                      </div>
                    </div>
                  </div>

                  {/* 打卡按钮 */}
                  <div className="mb-3">
                    <button
                      onClick={() => {
                        if (isPlaceCheckedIn(place.id)) {
                          removeCheckin(place.id);
                        } else {
                          addCheckin({
                            placeId: place.id,
                            placeName: ancient || place.songName || '未知地点',
                            checkinAt: new Date().toISOString(),
                          });
                          setShowCheckinSuccess(true);
                          setTimeout(() => setShowCheckinSuccess(false), 2000);
                        }
                      }}
                      className="w-full font-wenkai py-2.5 rounded-lg text-[12px] transition-colors flex items-center justify-center gap-2"
                      style={{
                        background: isPlaceCheckedIn(place.id) ? 'rgba(186,117,23,0.1)' : 'var(--gold-m)',
                        color: isPlaceCheckedIn(place.id) ? '#8B6914' : '#fff',
                        border: isPlaceCheckedIn(place.id) ? '1px solid rgba(186,117,23,0.3)' : 'none',
                      }}
                    >
                      {isPlaceCheckedIn(place.id) ? (
                        <>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M20 6L9 17l-5-5" />
                          </svg>
                          已打卡
                        </>
                      ) : (
                        <>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="10" r="3" />
                            <path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 7 8 11.7z" />
                          </svg>
                          打卡此地
                        </>
                      )}
                    </button>
                    {showCheckinSuccess && (
                      <div className="text-center mt-2 text-[11px] text-gold-m font-wenkai">
                        ✅ 打卡成功！可在"打卡"页查看
                      </div>
                    )}
                  </div>

                  {/* 三按钮 */}
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    <button
                      onClick={() => setShowDetail('story')}
                      className="font-wenkai py-3 rounded-lg text-[12px] text-ink border transition-colors hover:bg-paper-2"
                      style={{ borderColor: 'rgba(186,117,23,0.3)' }}
                    >
                      查看详情
                    </button>
                    <button
                      onClick={() => setShowDetail('works')}
                      className="font-wenkai py-3 rounded-lg text-[12px] text-ink border transition-colors hover:bg-paper-2"
                      style={{ borderColor: 'rgba(186,117,23,0.3)' }}
                    >
                      {works.length > 0 ? `${works.length} 部作品` : '相关作品'}
                    </button>
                    <button
                      onClick={() => {
                        const url = `https://uri.amap.com/marker?position=${place.lng},${place.lat}&name=${encodeURIComponent(ancient)}`;
                        window.open(url, '_blank');
                      }}
                      className="font-wenkai py-3 rounded-lg text-[12px] text-gold-light"
                      style={{ background: 'var(--gold-m)' }}
                    >
                      导航去这
                    </button>
                  </div>
                </>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// ═════ 详情视图（事迹 / 作品 / 文旅 三 Tab） ═════
function DetailView(props: {
  detail: V4PlaceFull | null;
  works: any[];
  memorialSites: any[];
  foods: any[];
  initialTab: 'story' | 'works' | 'travel';
  onBack: () => void;
  place: PlaceCore;
}) {
  const { detail, works, memorialSites, foods, initialTab, onBack, place } = props;
  const [tab, setTab] = useState<'story' | 'works' | 'travel'>(initialTab);

  const events = detail?.global_events || [];
  const routeEvents = detail?.route_events || {};
  // 把 route_events 拍平：兼容两种结构
  //   ① 旧结构 routeEvents[rid] = Event[]    （直接迭代）
  //   ② 新结构 routeEvents[rid] = { duration, essence, su_shi_story, historical_context, ... }
  //                                                              （一条整合事件）
  const flatRouteEvents: any[] = [];
  for (const rid of Object.keys(routeEvents)) {
    const v = (routeEvents as any)[rid];
    if (Array.isArray(v)) {
      for (const ev of v) flatRouteEvents.push({ ...ev, route_id: rid });
    } else if (v && typeof v === 'object') {
      // 把整个对象包成一条事件
      const yrList = Array.isArray(v.duration_years) ? v.duration_years : [];
      const yr = yrList.length > 0 ? `${yrList[0]}${yrList.length > 1 ? `–${yrList[yrList.length - 1]}` : ''}` : (v.duration || '');
      flatRouteEvents.push({
        route_id: rid,
        year: yr,
        period: v.duration || '',
        title: v.essence || `路线 ${rid}`,
        content: v.su_shi_story || v.historical_context || '',
        description: v.historical_context || '',
      });
    }
  }
  
  // 合并事件并去重（根据标题和年份判断重复）
  // 修复 v6.1: 用 Map 把 O(n²) 降到 O(n)，避免事件数大时卡顿
  const _eventKey = (ev: any): string => {
    const y = typeof ev.year === 'number'
      ? ev.year
      : parseInt(String(ev.year || ev.year_estimate || ev.date || 0).match(/\d+/)?.[0] || '0', 10);
    const t = (ev.title || ev.event || '').trim();
    return `${y}|${t}`;
  };
  const _seen = new Map<string, any>();
  for (const ev of [...events, ...flatRouteEvents]) {
    const k = _eventKey(ev);
    if (!_seen.has(k)) _seen.set(k, ev);
  }
  const allEventsWithDedup = Array.from(_seen.values());
  
  // 按年份排序
  const allEvents = allEventsWithDedup.sort((a, b) => {
    const getYear = (item: any) => {
      if (typeof item.year === 'number') return item.year;
      const yearStr = String(item.year || item.year_estimate || item.date || '0');
      const match = yearStr.match(/\d{4}/);
      return match ? parseInt(match[0], 10) : 0;
    };
    return getYear(a) - getYear(b);
  });

  return (
    <div>
      {/* 返回 */}
      <button
        onClick={onBack}
        className="font-wenkai text-[12px] text-gold-m hover:text-ink mb-3 tracking-wider"
      >
        ← 返回简介
      </button>

      {/* 标题简版 */}
      <h3 className="font-wenkai text-[18px] font-semibold text-ink mb-1">
        {detail?.ancient_name || ''}
      </h3>
      <p className="font-wenkai text-[10px] text-ink-lt mb-3 tracking-[0.06em]">
        {detail?.modern_name || ''} · 详细资料
      </p>

      {/* Tab 栏 */}
      <div className="flex border-b mb-4" style={{ borderColor: 'rgba(186,117,23,0.2)' }}>
        {(['story', 'works', 'travel'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`font-wenkai flex-1 text-center py-2 text-[12px] tracking-[0.08em] transition-colors ${
              tab === t ? 'text-gold-m font-semibold' : 'text-ink-lt/60'
            }`}
            style={{
              borderBottom: tab === t ? '2px solid var(--gold-m)' : 'none',
              marginBottom: tab === t ? '-1px' : 0,
            }}
          >
            {t === 'story' ? '事迹' : t === 'works' ? '作品' : '文旅'}
          </button>
        ))}
      </div>

      {/* === Tab 内容 === */}
      {tab === 'story' && (
        <div>
          <div className="text-[10px] text-ink-lt/60 tracking-[0.16em] mb-3">主要事迹</div>
          {detail?.background && (
            <p className="font-wenkai text-[13px] text-ink/80 leading-[1.9] mb-4">
              {detail.background}
            </p>
          )}
          {allEvents.length > 0 ? (
            <div className="space-y-3">
              {allEvents.slice(0, 12).map((ev, i) => (
                <div key={i} className="flex">
                  <div className="flex flex-col items-center mr-3">
                    <div className="w-2 h-2 rounded-full mt-1.5" style={{ background: 'var(--gold-m)' }} />
                    {i < allEvents.length - 1 && (
                      <div className="w-px flex-1 mt-1" style={{ background: 'rgba(186,117,23,0.2)' }} />
                    )}
                  </div>
                  <div className="flex-1 pb-3">
                    <div className="text-[10px] text-gold-m tracking-[0.05em] mb-1 font-mono">
                      {ev.year || ev.year_estimate || ev.period || ev.date || ''}
                    </div>
                    <div className="font-wenkai text-[13px] font-medium text-ink mb-1">
                      {ev.title || ev.event || ''}
                    </div>
                    <div className="font-wenkai text-[12px] text-ink/70 leading-[1.85]">
                      {ev.content || ev.description || ev.note || ''}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : !detail?.background ? (
            <div className="text-center py-8">
              <p className="text-[12px] text-ink-lt/60 italic mb-2">
                此地暂无事迹细节记录
              </p>
              <p className="text-[11px] text-ink-lt/50 leading-relaxed">
                苏轼一生踪迹 234 地，史料完整度因人地而异<br />
                此地或为路过留宿，未留下详细记述
              </p>
            </div>
          ) : null}
        </div>
      )}

      {tab === 'works' && (
        <div>
          <div className="text-[10px] text-ink-lt/60 tracking-[0.16em] mb-3">
            相关作品 · {works.length} 部
          </div>
          {works.length > 0 ? (
            <div className="space-y-3">
              {works.map((w, i) => (
                <WorkCard key={`${w.id || w.title}-${i}`} work={w} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-[12px] text-ink-lt/60 italic mb-2">
                此地暂未收录代表作
              </p>
              <p className="text-[11px] text-ink-lt/50 leading-relaxed">
                苏轼一生作品逾 3000 首，本系统收录 326 首代表作（全部含全文与赏析）<br />
                此地或为途经停留，未留下传世名篇
              </p>
            </div>
          )}
        </div>
      )}

      {tab === 'travel' && (
        <TravelTab 
          memorialSites={memorialSites} 
          localFoods={foods}
          routeId={detail?.routeId || ''}
          placeLat={detail?.lat || place.lat}
          placeLng={detail?.lng || place.lng}
        />
      )}
    </div>
  );
}

// ═════ Travel Tab 组件（美食模块：全部/苏轼特供/附近推荐） ═════
function TravelTab({ 
  memorialSites, 
  localFoods, 
  routeId,
  placeLat,
  placeLng 
}: { 
  memorialSites: any[];
  localFoods: any[];
  routeId: string;
  placeLat: number | undefined;
  placeLng: number | undefined;
}) {
  const [foodTab, setFoodTab] = useState<'all' | 'sushi' | 'nearby'>('all');
  const [sushiFoods, setSushiFoods] = useState<FoodItem[]>([]);
  const [nearbyFoods, setNearbyFoods] = useState<AMapPOIResult[]>([]);
  const [nearbyLoading, setNearbyLoading] = useState(false);

  // 加载苏轼特供美食
  useEffect(() => {
    getSushiSpecialFoods(routeId).then(setSushiFoods);
  }, [routeId]);

  // 加载附近美食
  useEffect(() => {
    if (foodTab === 'nearby' && placeLat && placeLng) {
      setNearbyLoading(true);
      searchNearbyFood(placeLat, placeLng, 2000)
        .then(setNearbyFoods)
        .finally(() => setNearbyLoading(false));
    }
  }, [foodTab, placeLat, placeLng]);

  // 获取当前显示的美食列表
  const getDisplayFoods = () => {
    if (foodTab === 'sushi') {
      return sushiFoods;
    }
    if (foodTab === 'nearby') {
      return nearbyFoods;
    }
    // all: 合并本地美食和苏轼特供
    const localItems = localFoods.map((f, i) => ({ ...f, source: 'local', uniqueId: `local-${i}` }));
    const sushiItems = sushiFoods.map((f) => ({ ...f, source: 'sushi', uniqueId: `sushi-${f.id}` }));
    return [...localItems, ...sushiItems];
  };

  const displayFoods = getDisplayFoods();

  return (
    <div>
      {/* 推荐景点 */}
      {memorialSites.length > 0 && (
        <div className="mb-4">
          <div className="text-[10px] text-ink-lt/60 tracking-[0.16em] mb-3">推荐景点</div>
          <div className="space-y-2">
            {memorialSites.map((s, i) => (
              <div
                key={i}
                className="border rounded-lg p-3"
                style={{ borderColor: 'rgba(186,117,23,0.18)' }}
              >
                <div className="font-wenkai text-[13px] font-medium text-ink mb-1">
                  {s.name || ''}
                </div>
                <div className="font-wenkai text-[11.5px] text-ink/70 leading-[1.85]">
                  {s.description || s.note || ''}
                </div>
                {s.address && (
                  <div className="text-[10px] text-ink-lt/60 mt-1.5">📍 {s.address}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 美食模块 */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <div className="text-[10px] text-ink-lt/60 tracking-[0.16em]">特色美食</div>
          {/* 美食 sub-tab */}
          <div className="flex bg-paper-2 rounded-lg p-0.5">
            {(['all', 'sushi', 'nearby'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setFoodTab(t)}
                className={`font-wenkai text-[10px] px-2 py-1 rounded-md transition-colors ${
                  foodTab === t 
                    ? 'bg-white text-gold-m' 
                    : 'text-ink-lt/60 hover:text-ink'
                }`}
              >
                {t === 'all' ? '全部' : t === 'sushi' ? '苏轼特供' : '附近推荐'}
              </button>
            ))}
          </div>
        </div>

        {/* 加载状态 */}
        {nearbyLoading && (
          <div className="text-center py-4">
            <div className="text-[11px] text-ink-lt/60">加载附近美食中...</div>
          </div>
        )}

        {/* 美食列表 */}
        {!nearbyLoading && displayFoods.length > 0 && (
          <div className="space-y-2">
            {displayFoods.map((f) => (
              <div
                key={(f as any).uniqueId || (f as any).id || Math.random()}
                className="border rounded-lg p-3"
                style={{ 
                  borderColor: (f as any).source === 'sushi' 
                    ? 'rgba(186,117,23,0.35)' 
                    : 'rgba(186,117,23,0.18)',
                  background: (f as any).source === 'sushi' 
                    ? 'rgba(186,117,23,0.05)' 
                    : 'transparent'
                }}
              >
                <div className="flex justify-between items-start mb-1">
                  <div className="font-wenkai text-[13px] font-medium text-ink">
                    {((f as any).name || (f as FoodItem).name) || ''}
                    {((f as FoodItem).alias) && (
                      <span className="text-ink-lt/50 ml-1">({(f as FoodItem).alias})</span>
                    )}
                  </div>
                  {(f as any).source === 'sushi' && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded text-white bg-gold-m">
                      苏轼特供
                    </span>
                  )}
                  {(f as AMapPOIResult).rating && (
                    <span className="text-[10px] text-amber-500">★ {(f as AMapPOIResult).rating}</span>
                  )}
                </div>
                <div className="font-wenkai text-[11.5px] text-ink/70 leading-[1.85] mb-2">
                  {(f as any).description || (f as FoodItem).desc || (f as AMapPOIResult).address || ''}
                </div>
                {(f as FoodItem).relatedPoem && (
                  <div className="text-[10px] text-gold-m/80 italic font-wenkai border-l-2 border-gold-m/30 pl-2">
                    「{(f as FoodItem).relatedPoem}」
                  </div>
                )}
                {(f as AMapPOIResult).distance && (
                  <div className="text-[10px] text-ink-lt/60 mt-1">
                    📍 距离 {(f as AMapPOIResult).distance}m
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* 空状态 */}
        {!nearbyLoading && displayFoods.length === 0 && (
          <div className="text-center py-6">
            <div className="text-[32px] mb-2">🍽️</div>
            <p className="text-[12px] text-ink-lt/60 italic">
              {foodTab === 'sushi' ? '暂无苏轼特供美食' : '暂无美食信息'}
            </p>
          </div>
        )}
      </div>

      {/* 空状态（无景点无美食） */}
      {memorialSites.length === 0 && !nearbyLoading && displayFoods.length === 0 && (
        <div className="text-center py-8">
          <p className="text-[12px] text-ink-lt/60 italic mb-2">
            此地文旅信息待补充
          </p>
          <p className="text-[11px] text-ink-lt/50 leading-relaxed">
            推荐景点 / 特色美食 / 交通信息<br />
            正在分批整理中
          </p>
        </div>
      )}
    </div>
  );
}

// ═════ 单部作品卡片（支持展开全文与跳转） ═════
// 诗词：保留"展开全文"模式，同时支持跳转
// 文章：只支持跳转
function WorkCard({ work }: { work: any }) {
  const [open, setOpen] = useState(false);
  const hasFull = !!work.fullText && work.fullText.length > 0;
  const hasPoemId = !!work.poem_id;
  
  // 判断是否为诗词类型（诗、词）还是文章类型（文、赋、策等）
  const poemTypes = ['诗', '词'];
  const isPoem = poemTypes.includes(work.type || '');

  return (
    <div
      className="border rounded-lg p-3"
      style={{ borderColor: 'rgba(186,117,23,0.18)' }}
    >
      <div className="flex justify-between items-start mb-1 gap-2">
        {/* 标题：文章类型直接跳转，诗词类型只有有poem_id时才跳转 */}
        {(isPoem && hasPoemId) || (!isPoem && hasPoemId) ? (
          <Link 
            href={`/poems/${work.poem_id}`}
            className="font-wenkai text-[13px] font-semibold text-gold-m hover:text-gold-d flex-1"
          >
            {work.title}
          </Link>
        ) : (
          <div className="font-wenkai text-[13px] font-semibold text-ink flex-1">
            {work.title}
          </div>
        )}
        {work.type && (
          <span className="text-[9px] px-2 py-0.5 rounded text-gold-m bg-gold-light tracking-[0.08em] whitespace-nowrap">
            {work.type}
          </span>
        )}
      </div>
      {(work.year || work.year_estimate) && (
        <div className="text-[10px] text-ink-lt/60 mb-1.5 font-mono">
          {work.year || work.year_estimate}{typeof (work.year || work.year_estimate) === 'number' ? ' 年' : ''}
        </div>
      )}
      {work.excerpt && (
        <div className="quote-left mb-2 font-wenkai">{work.excerpt}</div>
      )}
      {work.note && (
        <div className="font-wenkai text-[11.5px] text-ink/70 leading-[1.85] mb-2">
          {work.note}
        </div>
      )}
      
      {/* 诗词类型：保留展开全文按钮 */}
      {isPoem && hasFull && (
        <>
          {open ? (
            <div
              className="mt-2 p-2.5 rounded font-wenkai text-[12.5px] leading-[2] text-ink/85 whitespace-pre-line"
              style={{ background: 'rgba(186,117,23,0.06)' }}
            >
              {work.fullText}
              {work.background && (
                <div className="mt-3 pt-2 border-t border-gold-m/20 text-[11px] text-ink/65">
                  <div className="text-[10px] text-gold-m tracking-wider mb-0.5">创作背景</div>
                  {work.background}
                </div>
              )}
            </div>
          ) : null}
          <button
            onClick={() => setOpen((v) => !v)}
            className="font-wenkai text-[11px] text-gold-m hover:text-gold-d tracking-wider mt-1"
          >
            {open ? '收起 ↑' : '展开全文 ↓'}
          </button>
        </>
      )}
      
      {/* 诗词类型：有poem_id但无fullText时显示查看全文链接 */}
      {isPoem && hasPoemId && !hasFull && (
        <Link 
          href={`/poems/${work.poem_id}`}
          className="font-wenkai text-[11px] text-gold-m hover:text-gold-d tracking-wider mt-1 block"
        >
          查看全文与赏析 →
        </Link>
      )}
      
      {/* 文章类型：只支持跳转，不显示展开全文 */}
      {!isPoem && hasPoemId && (
        <Link 
          href={`/poems/${work.poem_id}`}
          className="font-wenkai text-[11px] text-gold-m hover:text-gold-d tracking-wider mt-1 block"
        >
          查看全文 →
        </Link>
      )}
    </div>
  );
}
