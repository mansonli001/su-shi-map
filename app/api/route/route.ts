import { NextRequest, NextResponse } from 'next/server';
import { AMAP_KEY } from '@/lib/config';

/**
 * 高德导航API - 获取真实行车路径
 * 
 * 输入：起点、终点坐标
 * 输出：真实导航路径坐标数组
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const origin = searchParams.get('origin');    // 格式：lng,l at
  const destination = searchParams.get('destination'); // 格式：lng,l at
  
  if (!origin || !destination) {
    return NextResponse.json(
      { error: '缺少参数：origin 和 destination 必填' },
      { status: 400 }
    );
  }
  
  try {
    // 调用高德驾车路径规划API
    const url = `https://restapi.amap.com/v3/direction/driving?key=${AMAP_KEY}&origin=${origin}&destination=${destination}&extensions=all&output=json`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.status === '1' && data.info === 'OK') {
      // 解析路径坐标
      const routes = data.route.paths.map((path: any) => {
        // 解析 polyline（格式：lng,lat;lng,lat;...）
        const polyline = path.polyline;
        const points = polyline.split(';').map((coord: string) => {
          const [lng, lat] = coord.split(',').map(Number);
          return [lng, lat];
        });
        
        return {
          distance: path.distance,  // 距离（米）
          duration: path.duration,  // 时间（秒）
          polyline: points,
          steps: path.steps.map((step: any) => ({
            instruction: step.instruction,
            road: step.road,
            distance: step.distance,
            polyline: step.polyline.split(';').map((coord: string) => {
              const [lng, lat] = coord.split(',').map(Number);
              return [lng, lat];
            })
          }))
        };
      });
      
      return NextResponse.json({
        success: true,
        origin,
        destination,
        routes
      });
    } else {
      return NextResponse.json(
        { error: '高德API调用失败', detail: data },
        { status: 500 }
      );
    }
  } catch (error: any) {
    return NextResponse.json(
      { error: '服务器错误', detail: error.message },
      { status: 500 }
    );
  }
}

/**
 * 批量获取路径（用于路线绘制）
 * 
 * 输入：途经点数组 [{lng, lat}, ...]
 * 输出：真实路径坐标数组（合并所有路段）
 */
export async function POST(request: NextRequest) {
  const body = await request.json();
  const { waypoints } = body;  // [{lng, lat}, ...]
  
  if (!waypoints || waypoints.length < 2) {
    return NextResponse.json(
      { error: '途经点至少需要2个' },
      { status: 400 }
    );
  }
  
  try {
    const allPolylines: [number, number][][] = [];
    
    // 分段获取路径（每两个相邻点之间）
    for (let i = 0; i < waypoints.length - 1; i++) {
      const origin = `${waypoints[i].lng},${waypoints[i].lat}`;
      const destination = `${waypoints[i + 1].lng},${waypoints[i + 1].lat}`;
      
      const url = `https://restapi.amap.com/v3/direction/driving?key=${AMAP_KEY}&origin=${origin}&destination=${destination}&extensions=all&output=json`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === '1' && data.info === 'OK') {
        // 取第一条路径
        const path = data.route.paths[0];
        const polyline = path.polyline;
        const points = polyline.split(';').map((coord: string) => {
          const [lng, lat] = coord.split(',').map(Number);
          return [lng, lat] as [number, number];
        });
        
        allPolylines.push(points);
      } else {
        console.error(`路段 ${i}→${i+1} 获取失败:`, data.info);
        // 失败时使用直线连接
        allPolylines.push([
          [waypoints[i].lng, waypoints[i].lat],
          [waypoints[i + 1].lng, waypoints[i + 1].lat]
        ]);
      }
    }
    
    // 合并所有路径（去重相邻点）
    const merged: [number, number][] = [];
    allPolylines.forEach((polyline, idx) => {
      polyline.forEach((point, pidx) => {
        if (idx > 0 && pidx === 0) {
          // 跳过后续路段的首个点（与前一路段尾点重复）
          return;
        }
        merged.push(point);
      });
    });
    
    return NextResponse.json({
      success: true,
      waypoints,
      polyline: merged,  // 合并后的真实路径坐标
      segments: allPolylines.length
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: '服务器错误', detail: error.message },
      { status: 500 }
    );
  }
}
