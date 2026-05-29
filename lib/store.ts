/**
 * Zustand 全局状态管理 v4.0
 * currentStage / selectedPlace / isCardOpen / mapRef
 */

import { create } from 'zustand';
import { Stage, PlaceCore } from '@/types';

interface SuShiStore {
  // 地点数据（首屏加载后写入）
  places: PlaceCore[];
  setPlaces: (places: PlaceCore[]) => void;

  // 时间轴
  currentStage: Stage | null;
  setCurrentStage: (stage: Stage | null) => void;

  // 选中地点
  selectedPlace: PlaceCore | null;
  setSelectedPlace: (place: PlaceCore | null) => void;

  // 半屏卡片
  isCardOpen: boolean;
  openCard: () => void;
  closeCard: () => void;

  // 地图引用（注入给 Zustand，跨组件共享）
  mapRef: any | null;
  setMapRef: (ref: any | null) => void;

  // 轨迹动画
  isTrajectoryPlaying: boolean;
  setTrajectoryPlaying: (playing: boolean) => void;

  // 搜索面板
  isSearchOpen: boolean;
  openSearch: () => void;
  closeSearch: () => void;
}

export const useSuShiStore = create<SuShiStore>((set) => ({
  // 地点数据
  places: [],
  setPlaces: (places) => set({ places }),

  // 时间轴
  currentStage: null,
  setCurrentStage: (stage) => set({ currentStage: stage }),

  // 选中地点
  selectedPlace: null,
  setSelectedPlace: (place) => set({ selectedPlace: place, isCardOpen: !!place }),

  // 半屏卡片
  isCardOpen: false,
  openCard: () => set({ isCardOpen: true }),
  closeCard: () => set({ isCardOpen: false, selectedPlace: null }),

  // 地图引用
  mapRef: null,
  setMapRef: (ref) => set({ mapRef: ref }),

  // 轨迹动画
  isTrajectoryPlaying: false,
  setTrajectoryPlaying: (playing) => set({ isTrajectoryPlaying: playing }),

  // 搜索面板
  isSearchOpen: false,
  openSearch: () => set({ isSearchOpen: true }),
  closeSearch: () => set({ isSearchOpen: false }),
}));
