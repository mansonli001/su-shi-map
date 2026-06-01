/**
 * 条件 logger v4.1
 * - 开发模式打印 debug/info；生产仅 error。
 * - 严禁打印 key / 完整坐标 / 用户 IP 等敏感信息。
 */

const isDev =
  typeof process !== 'undefined' && process.env.NODE_ENV !== 'production';

export const logger = {
  debug: (...args: unknown[]) => {
    if (isDev) console.log('[debug]', ...args);
  },
  info: (...args: unknown[]) => {
    if (isDev) console.log('[info]', ...args);
  },
  warn: (...args: unknown[]) => {
    if (isDev) console.warn('[warn]', ...args);
  },
  error: (...args: unknown[]) => {
    // 错误生产环境也打印（用于服务端日志），但调用方自行确保不泄露敏感信息
    console.error('[error]', ...args);
  },
};
