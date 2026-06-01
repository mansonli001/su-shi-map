/**
 * 配置文件 v4.1
 * 高德地图密钥读取：env-only + fail-fast，禁止任何硬编码 fallback。
 *
 * 安全原则（GOLDEN RULE）：NEVER hardcode secrets / NO defaults。
 * 旧版残留的 fallback 值已在 v4.1 移除并准备 rotate。
 */

/**
 * 获取高德 JSAPI Key（浏览器与服务端均可读取）。
 * 缺失时立即 throw，不返回任何默认值。
 */
export function getAMapKey(): string {
  // 兼容服务端独立 AMAP_KEY 与浏览器侧 NEXT_PUBLIC_AMAP_KEY
  const k = process.env.AMAP_KEY || process.env.NEXT_PUBLIC_AMAP_KEY;
  if (!k) {
    throw new Error(
      '[config] AMAP_KEY / NEXT_PUBLIC_AMAP_KEY 未配置。请在 .env.local 与 Vercel Project Env 同步配置。'
    );
  }
  return k;
}

/**
 * 获取高德 securityJsCode（仅服务端可读取）。
 * 缺失时立即 throw。
 */
export function getAMapSecurityCode(): string {
  const c = process.env.AMAP_SECURITY_JS_CODE;
  if (!c) {
    throw new Error(
      '[config] AMAP_SECURITY_JS_CODE 未配置。请在 .env.local 与 Vercel Project Env 同步配置。'
    );
  }
  return c;
}
