/**
 * 高德密钥安全代理 v4.0
 * 服务端注入 securityJsCode，不暴露前端
 *
 * 所有高德 JSAPI 的后端请求都走此代理：
 * window._AMapSecurityConfig = { serviceHost: '/api/_AMapService' }
 */

import { NextRequest, NextResponse } from 'next/server';

const AMAP_SECURITY_JS_CODE = process.env.AMAP_SECURITY_JS_CODE;

/**
 * 拦截高德 JSAPI 的密钥验证请求
 * 高德会请求 /_AMapService/... 路径，由此外层代理转发并注入密钥
 */
export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  if (!AMAP_SECURITY_JS_CODE) {
    return NextResponse.json({ error: 'AMAP_SECURITY_JS_CODE 未配置' }, { status: 500 });
  }

  const path = params.path.join('/');
  
  // 高德密钥验证接口：返回 securityJsCode
  if (path.includes('security_js_code') || path.endsWith('key')) {
    return NextResponse.json({
      securityJsCode: AMAP_SECURITY_JS_CODE,
    });
  }

  // 其他高德 API 请求：代理转发
  const amapUrl = `https://webapi.amap.com/${path}${request.nextUrl.search}`;
  
  try {
    const response = await fetch(amapUrl, {
      headers: {
        'Referer': 'https://webapi.amap.com',
        'User-Agent': request.headers.get('user-agent') || '',
      },
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { error: `代理请求失败: ${err instanceof Error ? err.message : '未知错误'}` },
      { status: 502 }
    );
  }
}

export async function POST(request: NextRequest, { params }: { params: { path: string[] } }) {
  return GET(request, { params });
}
