/**
 * 打卡 API v4.0
 * POST: 打卡 / DELETE: 取消打卡
 */

import { NextRequest, NextResponse } from 'next/server';
import { checkin, uncheckin, getAllCheckins } from '@/lib/idb';

/**
 * POST - 打卡
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { placeId, note } = body;

    if (!placeId) {
      return NextResponse.json({ error: 'placeId 不能为空' }, { status: 400 });
    }

    // 注意：IndexedDB 操作需要在浏览器环境执行
    // 此 API 返回操作指引，实际存储由前端调用 lib/idb.ts 完成
    return NextResponse.json({
      success: true,
      message: '请在前端调用 lib/idb.ts 的 checkin() 函数',
      placeId,
    });
  } catch (err) {
    return NextResponse.json(
      { error: `打卡失败: ${err instanceof Error ? err.message : '未知错误'}` },
      { status: 500 }
    );
  }
}

/**
 * DELETE - 取消打卡
 */
export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const placeId = searchParams.get('placeId');

  if (!placeId) {
    return NextResponse.json({ error: 'placeId 不能为空' }, { status: 400 });
  }

  return NextResponse.json({
    success: true,
    message: '请在前端调用 lib/idb.ts 的 uncheckin() 函数',
    placeId,
  });
}

/**
 * GET - 获取打卡列表
 */
export async function GET() {
  return NextResponse.json({
    success: true,
    message: '请在前端调用 lib/idb.ts 的 getAllCheckins() 函数',
  });
}
