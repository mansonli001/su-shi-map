/**
 * Zustand 全局状态管理 v4.0
 * currentStage / selectedPlace / isCardOpen / mapRef
 */

import { create } from 'zustand';
import { Stage, PlaceCore } from '@/types';

export type RouteId = 
  | 'route01' | 'route02' | 'route03' | 'route04' | 'route05'
  | 'route06' | 'route07' | 'route08' | 'route09' | 'route10'
  | 'route11' | 'route12' | 'route13' | 'route14' | 'route15'
  | 'route16' | 'route17' | 'route18' | 'route19'
  | 'overview'
  | null;

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

  // 当前路线（时间轴点击后高亮该路线）
  currentRoute: RouteId;
  setCurrentRoute: (routeId: RouteId) => void;
  clearRoute: () => void;
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

  // 当前路线
  currentRoute: null,
  setCurrentRoute: (routeId) => set({ currentRoute: routeId }),
  clearRoute: () => set({ currentRoute: null }),
}));
