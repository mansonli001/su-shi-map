/**
 * 高德 securityJsCode 服务端代理（v4.1）
 *
 * 路径变更：原 /api/_AMapService/security_js_code 因 Next.js App Router 把
 * 下划线开头的目录视为 private folder（不生成路由）会 404，已迁移到
 * /api/amap-security。lib/amap-loader.ts fetch 同步更新。
 */

import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  const code = process.env.AMAP_SECURITY_JS_CODE;
  if (!code) {
    return NextResponse.json(
      { error: 'AMAP_SECURITY_JS_CODE not configured' },
      { status: 500 }
    );
  }
  // 注意：仅用于 dev/preview/prod 同源请求，securityJsCode 本身按高德设计
  // 必须配合域名白名单使用。这里不主动加 CORS（默认同源）。
  return NextResponse.json(
    { securityJsCode: code },
    {
      headers: {
        'Cache-Control': 'private, max-age=60',
      },
    }
  );
}
