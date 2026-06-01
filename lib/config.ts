/**
 * 配置文件
 * 存储高德地图API密钥等配置项
 */

// 高德地图 Web服务 API Key（用于导航API）
export const AMAP_KEY = process.env.AMAP_KEY || process.env.NEXT_PUBLIC_AMAP_KEY || '58b83b5ce989b73370141e4c61e5ef41';

// 高德地图安全JS代码
export const AMAP_SECURITY_JS_CODE = process.env.AMAP_SECURITY_JS_CODE || 'e2b0432c83a60cb97a4f66842dfd4169';