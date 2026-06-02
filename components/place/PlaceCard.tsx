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
  const { isCardOpen, closeCard } = useSuShiStore();
  const [expanded, setExpanded] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [detail, setDetail] = useState<V4PlaceFull | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // 卡片打开时加载详情（v4 路径）
  useEffect(() => {
    if (!place || !isCardOpen) return;
    setDetailLoading(true);
    setShowDetail(false);
    fetch(`/data-v4/places/${place.id}.json?t=${Date.now()}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) setDetail(data as V4PlaceFull);
      })
      .catch(() => {})
      .finally(() => setDetailLoading(false));
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

          {/* 半屏卡片 */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: expanded ? '8%' : '38%' }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 280 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            onDragEnd={handleDragEnd}
            className="fixed inset-x-0 bottom-0 z-50 max-h-[88vh] overflow-y-auto md:max-w-2xl md:mx-auto"
            style={{
              background: 'var(--card)',
              borderRadius: '18px 18px 0 0',
              boxShadow: '0 -10px 40px rgba(26,16,8,0.18)',
            }}
          >
            {/* 拖拽手柄 */}
            <div
              onPointerDown={() => setExpanded((v) => !v)}
              className="cursor-grab active:cursor-grabbing pt-3 pb-2"
            >
              <div className="w-10 h-1 rounded-full mx-auto" style={{ background: 'rgba(186,117,23,0.4)' }} />
            </div>

            <div className="px-5 pb-32" style={{ paddingBottom: 'calc(env(safe-area-inset-bottom, 0px) + 9rem)' }}>
              {/* ====== 详情视图 ====== */}
              {showDetail ? (
                <DetailView
                  detail={detail}
                  works={works}
                  memorialSites={memorialSites}
                  foods={foods}
                  onBack={() => setShowDetail(false)}
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

                  {/* 三按钮 */}
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    <button
                      onClick={() => setShowDetail(true)}
                      className="font-wenkai py-3 rounded-lg text-[12px] text-ink border transition-colors hover:bg-paper-2"
                      style={{ borderColor: 'rgba(186,117,23,0.3)' }}
                    >
                      查看详情
                    </button>
                    <button
                      onClick={() => setShowDetail(true)}
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
  onBack: () => void;
}) {
  const { detail, works, memorialSites, foods, onBack } = props;
  const [tab, setTab] = useState<'story' | 'works' | 'travel'>('story');

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
  const allEvents = [...events, ...flatRouteEvents].sort((a, b) => {
    const numA = typeof a.year === 'number' ? a.year : parseInt(String(a.year || a.year_estimate || 0).match(/\d+/)?.[0] || '0', 10);
    const numB = typeof b.year === 'number' ? b.year : parseInt(String(b.year || b.year_estimate || 0).match(/\d+/)?.[0] || '0', 10);
    return numA - numB;
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
                苏轼一生作品逾 3000 首，本系统收录 68 首代表作（已注入 39 首全文）<br />
                此地或为途经停留，未留下传世名篇
              </p>
            </div>
          )}
        </div>
      )}

      {tab === 'travel' && (
        <div>
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
          {foods.length > 0 && (
            <div className="mb-4">
              <div className="text-[10px] text-ink-lt/60 tracking-[0.16em] mb-3">特色美食</div>
              <div className="space-y-2">
                {foods.map((f, i) => (
                  <div
                    key={i}
                    className="border rounded-lg p-3"
                    style={{ borderColor: 'rgba(186,117,23,0.18)' }}
                  >
                    <div className="font-wenkai text-[13px] font-medium text-ink mb-1">
                      {f.name || ''}
                    </div>
                    <div className="font-wenkai text-[11.5px] text-ink/70 leading-[1.85]">
                      {f.description || ''}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {memorialSites.length === 0 && foods.length === 0 && (
            <div className="text-center py-8">
              <p className="text-[12px] text-ink-lt/60 italic mb-2">
                此地文旅信息待补充
              </p>
              <p className="text-[11px] text-ink-lt/50 leading-relaxed">
                推荐景点 / 特色美食 / 交通信息<br />
                正在分批整理中（外部专家任务 A5）
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ═════ 单部作品卡片（支持展开全文） ═════
function WorkCard({ work }: { work: any }) {
  const [open, setOpen] = useState(false);
  const hasFull = !!work.fullText && work.fullText.length > 0;

  return (
    <div
      className="border rounded-lg p-3"
      style={{ borderColor: 'rgba(186,117,23,0.18)' }}
    >
      <div className="flex justify-between items-start mb-1 gap-2">
        <div className="font-wenkai text-[13px] font-semibold text-ink flex-1">
          {work.title}
        </div>
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
      {hasFull && (
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
    </div>
  );
}
