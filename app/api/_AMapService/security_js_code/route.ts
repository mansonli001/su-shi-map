/**
 * 高德密钥安全代理 - 固定路由
 * 只处理 security_js_code 请求（这是高德 JSAPI 必须的第一步）
 */

import { NextRequest, NextResponse } from 'next/server';

const AMAP_SECURITY_JS_CODE = process.env.AMAP_SECURITY_JS_CODE;

export async function GET(request: NextRequest) {
  if (!AMAP_SECURITY_JS_CODE) {
    return NextResponse.json(
      { error: 'AMAP_SECURITY_JS_CODE 未配置' },
      { status: 500 }
    );
  }

  return NextResponse.json({
    securityJsCode: AMAP_SECURITY_JS_CODE,
  });
}

export async function POST(request: NextRequest) {
  return GET(request);
}
