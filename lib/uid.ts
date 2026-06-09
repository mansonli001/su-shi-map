/**
 * 匿名 UUID 生成器
 * 首次访问时生成 crypto.randomUUID，存储在 localStorage 的 xys_uid key 中
 * SSR 安全：所有 localStorage 操作均在 typeof window 判断内
 */

const UID_KEY = 'xys_uid';

/**
 * 获取或生成匿名用户 ID
 * SSR 安全：服务端返回空字符串
 * @returns 匿名 UUID
 */
export function getUID(): string {
  if (typeof window === 'undefined') return '';
  let uid = localStorage.getItem(UID_KEY);

  if (!uid) {
    uid = crypto.randomUUID();
    localStorage.setItem(UID_KEY, uid);
  }

  return uid;
}

/**
 * 重置匿名用户 ID（用于测试或隐私重置）
 * @returns 新的 UUID
 */
export function resetUID(): string {
  if (typeof window === 'undefined') return '';
  const uid = crypto.randomUUID();
  localStorage.setItem(UID_KEY, uid);
  return uid;
}

/**
 * 检查是否已有用户 ID
 * @returns 是否存在 uid
 */
export function hasUID(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(UID_KEY) !== null;
}