/**
 * Zustand 全局状态管理 v4.0
 * currentStage / selectedPlace / isCardOpen / mapRef
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Stage, PlaceCore } from '@/types';

// v4.1: RouteId 弱类型化，兼容 R00-R19 与历史 route01-route19
export type RouteId = string | null;

// 用户收藏
export interface FavoritePoem {
  poemId: string;
  title: string;
  addedAt: string;
}

// 用户打卡
export interface CheckinPlace {
  placeId: string;
  placeName: string;
  checkinAt: string;
  note?: string;
  photos?: string[];
}

// 用户笔记
export interface UserNote {
  id: string;
  targetId: string; // poemId or placeId
  targetType: 'poem' | 'place';
  content: string;
  createdAt: string;
  updatedAt: string;
}

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

  // ===== 用户数据（持久化到localStorage） =====
  // 收藏诗词
  favoritePoems: FavoritePoem[];
  addFavoritePoem: (poem: FavoritePoem) => void;
  removeFavoritePoem: (poemId: string) => void;
  isPoemFavorited: (poemId: string) => boolean;

  // 打卡地点
  checkinPlaces: CheckinPlace[];
  addCheckin: (checkin: CheckinPlace) => void;
  removeCheckin: (placeId: string) => void;
  isPlaceCheckedIn: (placeId: string) => boolean;
  updateCheckinNote: (placeId: string, note: string) => void;

  // 用户笔记
  userNotes: UserNote[];
  addNote: (note: UserNote) => void;
  updateNote: (noteId: string, content: string) => void;
  deleteNote: (noteId: string) => void;
  getNotesByTarget: (targetId: string) => UserNote[];
}

export const useSuShiStore = create<SuShiStore>()(
  persist(
    (set, get) => ({
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

      // ===== 用户数据 =====
      // 收藏诗词
      favoritePoems: [],
      addFavoritePoem: (poem) =>
        set((state) => ({
          favoritePoems: [...state.favoritePoems, poem],
        })),
      removeFavoritePoem: (poemId) =>
        set((state) => ({
          favoritePoems: state.favoritePoems.filter((p) => p.poemId !== poemId),
        })),
      isPoemFavorited: (poemId) =>
        get().favoritePoems.some((p) => p.poemId === poemId),

      // 打卡地点
      checkinPlaces: [],
      addCheckin: (checkin) =>
        set((state) => ({
          checkinPlaces: [...state.checkinPlaces, checkin],
        })),
      removeCheckin: (placeId) =>
        set((state) => ({
          checkinPlaces: state.checkinPlaces.filter((c) => c.placeId !== placeId),
        })),
      isPlaceCheckedIn: (placeId) =>
        get().checkinPlaces.some((c) => c.placeId === placeId),
      updateCheckinNote: (placeId, note) =>
        set((state) => ({
          checkinPlaces: state.checkinPlaces.map((c) =>
            c.placeId === placeId ? { ...c, note } : c
          ),
        })),

      // 用户笔记
      userNotes: [],
      addNote: (note) =>
        set((state) => ({
          userNotes: [...state.userNotes, note],
        })),
      updateNote: (noteId, content) =>
        set((state) => ({
          userNotes: state.userNotes.map((n) =>
            n.id === noteId
              ? { ...n, content, updatedAt: new Date().toISOString() }
              : n
          ),
        })),
      deleteNote: (noteId) =>
        set((state) => ({
          userNotes: state.userNotes.filter((n) => n.id !== noteId),
        })),
      getNotesByTarget: (targetId) =>
        get().userNotes.filter((n) => n.targetId === targetId),
    }),
    {
      name: 'su-shi-user-data',
      partialize: (state) => ({
        favoritePoems: state.favoritePoems,
        checkinPlaces: state.checkinPlaces,
        userNotes: state.userNotes,
      }),
    }
  )
);
