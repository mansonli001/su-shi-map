/**
 * 匿名 UUID 生成器
 * 首次访问时生成 crypto.randomUUID，存储在 localStorage 的 xys_uid key 中
 */

const UID_KEY = 'xys_uid';

/**
 * 获取或生成匿名用户 ID
 * @returns 匿名 UUID
 */
export function getUID(): string {
  let uid = localStorage.getItem(UID_KEY);
  
  if (!uid) {
    // 生成新的 UUID
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
  const uid = crypto.randomUUID();
  localStorage.setItem(UID_KEY, uid);
  return uid;
}

/**
 * 检查是否已有用户 ID
 * @returns 是否存在 uid
 */
export function hasUID(): boolean {
  return localStorage.getItem(UID_KEY) !== null;
}