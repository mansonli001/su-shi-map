/**
 * IndexedDB 封装 v4.0
 * 匿名打卡 CRUD
 */

import { LocalCheckin } from '@/types';

const DB_NAME = 'su-shi-map';
const DB_VERSION = 1;
const STORE_NAME = 'checkins';

/**
 * 打开 IndexedDB
 */
function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'placeId' });
        store.createIndex('checkedAt', 'checkedAt', { unique: false });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

/**
 * 打卡（创建或更新）
 */
export async function checkin(placeId: string, note?: string): Promise<void> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const data: LocalCheckin = {
      placeId,
      checkedAt: Date.now(),
      note,
    };
    const request = store.put(data);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

/**
 * 取消打卡
 */
export async function uncheckin(placeId: string): Promise<void> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const request = store.delete(placeId);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

/**
 * 获取所有打卡记录
 */
export async function getAllCheckins(): Promise<LocalCheckin[]> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => reject(request.error);
  });
}

/**
 * 检查某地点是否已打卡
 */
export async function isCheckedin(placeId: string): Promise<boolean> {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const request = store.get(placeId);
    request.onsuccess = () => resolve(!!request.result);
    request.onerror = () => reject(request.error);
  });
}

/**
 * 获取打卡进度（已打卡数量 / 总数量）
 */
export async function getCheckinProgress(total: number): Promise<{ checked: number; total: number; percent: number }> {
  const checkins = await getAllCheckins();
  const checked = checkins.length;
  const percent = total > 0 ? Math.round((checked / total) * 100) : 0;
  return { checked, total, percent };
}
