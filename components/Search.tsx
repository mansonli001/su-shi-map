/**
 * Search v4.0
 * fuse.js 本地模糊搜索，AnimatePresence 弹出层
 */

'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Fuse from 'fuse.js';
import { useSuShiStore } from '@/lib/store';
import { PlaceIndex } from '@/types';

export default function Search() {
  const { isSearchOpen, closeSearch, setSelectedPlace } = useSuShiStore();
  const [query, setQuery] = useState('');
  const [places, setPlaces] = useState<PlaceIndex[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  // 加载地点索引数据
  useEffect(() => {
    if (!isSearchOpen) return;
    fetch('/data/places-index.json')
      .then(res => res.json())
      .then(data => setPlaces(data))
      .catch(err => console.error('加载搜索索引失败', err));
  }, [isSearchOpen]);

  // fuse.js 搜索
  const results = useMemo(() => {
    if (!query.trim() || places.length === 0) return [];
    const fuse = new Fuse(places, {
      keys: [
        { name: 'songName', weight: 0.4 },
        { name: 'modernName', weight: 0.4 },
        { name: 'summary', weight: 0.2 },
      ],
      threshold: 0.4,
      includeScore: true,
    });
    return fuse.search(query).slice(0, 10);
  }, [query, places]);

  // 选中地点
  const handleSelect = (place: PlaceIndex) => {
    // 获取完整 PlaceCore 并选中
    fetch(`/data/places-core.json`)
      .then(res => res.json())
      .then((cores: PlaceIndex[]) => {
        const core = cores.find(p => p.id === place.id);
        if (core) {
          setSelectedPlace(core as any);
        }
      });
    setQuery('');
    closeSearch();
  };

  // 关闭时清空
  const handleClose = () => {
    setQuery('');
    closeSearch();
  };

  return (
    <AnimatePresence>
      {isSearchOpen && (
        <>
          {/* 遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="framer-overlay z-50"
            onClick={handleClose}
          />

          {/* 搜索面板 */}
          <motion.div
            initial={{ y: '-100%' }}
            animate={{ y: 0 }}
            exit={{ y: '-100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed inset-x-0 top-0 z-50 bg-paper shadow-lg max-h-[80vh] overflow-y-auto"
          >
            <div className="p-4 safe-top">
              {/* 搜索框 */}
              <div className="flex items-center gap-3 mb-4">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    placeholder="搜索地点、诗词..."
                    className="w-full px-4 py-2.5 border border-ink/20 rounded-lg text-sm focus:outline-none focus:border-ink/50 font-sans"
                    autoFocus
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/30 text-sm">
                    {query ? '✕' : '🔍'}
                  </span>
                </div>
                <button
                  onClick={handleClose}
                  className="text-sm text-ink/50 hover:text-ink px-2 py-1"
                >
                  取消
                </button>
              </div>

              {/* 搜索结果 */}
              {query.trim() && (
                <div className="space-y-1">
                  {results.length === 0 && (
                    <p className="text-sm text-ink/40 text-center py-8">未找到相关地点</p>
                  )}
                  {results.map(({ item, score }) => (
                    <button
                      key={item.id}
                      onClick={() => handleSelect(item)}
                      className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-ink/5 transition-colors flex items-center gap-3"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-ink truncate">
                          {item.songName}
                        </p>
                        <p className="text-xs text-ink/40 truncate">
                          {item.modernName}
                          {item.famousLine && ` · ${item.famousLine}`}
                        </p>
                      </div>
                      {score && score < 0.3 && (
                        <span className="text-xs text-ink/30 shrink-0">精确</span>
                      )}
                    </button>
                  ))}
                </div>
              )}

              {/* 未输入时的提示 */}
              {!query.trim() && (
                <div className="py-8 text-center">
                  <p className="text-sm text-ink/40 mb-2">输入地名、诗词关键词搜索</p>
                  <p className="text-xs text-ink/30">
                    支持：宋代地名 / 现代地名 / 诗词名句
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
