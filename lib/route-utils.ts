/**
 * 路线手绘化工具
 * 把直线路径变成弯曲的、有手绘感的曲线
 * 模拟宋代官道/古道的不规则走向
 */

/**
 * Catmull-Rom 样条插值
 * 在 p1→p2 之间生成平滑插值点
 */
function catmullRom(
  p0: { lng: number; lat: number },
  p1: { lng: number; lat: number },
  p2: { lng: number; lat: number },
  p3: { lng: number; lat: number },
  t: number
): { lng: number; lat: number } {
  const t2 = t * t;
  const t3 = t2 * t;
  return {
    lng:
      0.5 *
      (2 * p1.lng +
        (-p0.lng + p2.lng) * t +
        (2 * p0.lng - 5 * p1.lng + 4 * p2.lng - p3.lng) * t2 +
        (-p0.lng + 3 * p1.lng - 3 * p2.lng + p3.lng) * t3),
    lat:
      0.5 *
      (2 * p1.lat +
        (-p0.lat + p2.lat) * t +
        (2 * p0.lat - 5 * p1.lat + 4 * p2.lat - p3.lat) * t2 +
        (-p0.lat + 3 * p1.lat - 3 * p2.lat + p3.lat) * t3),
  };
}

/**
 * 把路径点数组扩展（首尾各补一个虚拟点）
 */
function expandPoints(points: { lng: number; lat: number }[]) {
  if (points.length < 2) return points;
  const first = points[0];
  const last = points[points.length - 1];
  // 向前延伸一个点（镜像）
  const expanded = [
    { lng: 2 * first.lng - points[1].lng, lat: 2 * first.lat - points[1].lat },
    ...points,
    {
      lng: 2 * last.lng - points[points.length - 2].lng,
      lat: 2 * last.lat - points[points.length - 2].lat,
    },
  ];
  return expanded;
}

/**
 * 在相邻点之间加入垂直方向的随机扰动，模拟手绘感
 * @param points - 平滑后的路径点
 * @param maxJitterDeg - 最大扰动（度），默认 0.015° ≈ 1.5km
 */
function addHandDrawJitter(
  points: { lng: number; lat: number }[],
  maxJitterDeg: number = 0.015
): { lng: number; lat: number }[] {
  if (points.length < 2) return points;

  return points.map((p, i) => {
    if (i === 0 || i === points.length - 1) return p; // 端点不动

    // 计算前后段的方向角
    const prev = points[i - 1];
    const next = points[i + 1];
    const dx = next.lng - prev.lng;
    const dy = next.lat - prev.lat;
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len < 1e-10) return p;

    // 垂直单位向量（逆时针转90度）
    const nx = -dy / len;
    const ny = dx / len;

    // 随机扰动（高斯分布质感，用 Box-Muller 近似）
    const u1 = Math.random();
    const u2 = Math.random();
    const gauss = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    const jitter = gauss * maxJitterDeg * 0.5;

    return {
      lng: p.lng + nx * jitter,
      lat: p.lat + ny * jitter,
    };
  });
}

export interface SmoothPathOptions {
  /** 每条边插值段数，越大越平滑，默认 8 */
  segmentsPerEdge?: number;
  /** 手绘扰动幅度（度），默认 0.012 ≈ 1.3km */
  jitterDeg?: number;
  /** 是否启用 Catmull-Rom 平滑，默认 true */
  smooth?: boolean;
}

/**
 * 将直线路径转换为手绘风格弯曲路径
 * @param points - 原始路径点 [{lng, lat}]
 * @param options - 配置项
 * @returns 平滑后的路径坐标数组 [[lng, lat], ...]
 */
export function smoothPath(
  points: { lng: number; lat: number }[],
  options: SmoothPathOptions = {}
): [number, number][] {
  const {
    segmentsPerEdge = 8,
    jitterDeg = 0.012,
    smooth = true,
  } = options;

  if (points.length < 2) return points.map((p) => [p.lng, p.lat] as [number, number]);

  // 如果只有两个点且不启用平滑，只加扰动
  if (points.length === 2 || !smooth) {
    const jittered = addHandDrawJitter(
      points.map((p) => ({ ...p })),
      jitterDeg
    );
    return jittered.map((p) => [p.lng, p.lat] as [number, number]);
  }

  // Catmull-Rom 插值
  const expanded = expandPoints(points);
  const smoothed: { lng: number; lat: number }[] = [];

  for (let i = 1; i < expanded.length - 2; i++) {
    const p0 = expanded[i - 1];
    const p1 = expanded[i];
    const p2 = expanded[i + 1];
    const p3 = expanded[i + 2];

    // 第一段保持起点
    if (i === 1) smoothed.push(p1);

    for (let s = 1; s <= segmentsPerEdge; s++) {
      const t = s / segmentsPerEdge;
      const interp = catmullRom(p0, p1, p2, p3, t);
      // 最后一段的点去重（避免 p2 被加两次）
      if (i < expanded.length - 3 || s < segmentsPerEdge) {
        smoothed.push(interp);
      }
    }
  }

  // 确保最后一个点
  const last = points[points.length - 1];
  const lastSmoothed = smoothed[smoothed.length - 1];
  if (!lastSmoothed || Math.abs(lastSmoothed.lng - last.lng) > 1e-8) {
    smoothed.push(last);
  }

  // 加入手绘扰动
  const jittered = addHandDrawJitter(smoothed, jitterDeg);

  return jittered.map((p) => [p.lng, p.lat] as [number, number]);
}

/**
 * 为整条路线生成"手绘感"路径（对外主函数）
 * 在 route-config 定义的直连路径基础上，加入弯曲和扰动
 */
export function makeHandDrawnPath(
  points: { lng: number; lat: number }[],
  style: 'light' | 'medium' | 'heavy' = 'medium'
): [number, number][] {
  const config = {
    light: { segmentsPerEdge: 6, jitterDeg: 0.008 },
    medium: { segmentsPerEdge: 8, jitterDeg: 0.012 },
    heavy: { segmentsPerEdge: 10, jitterDeg: 0.018 },
  }[style];

  return smoothPath(points, {
    segmentsPerEdge: config.segmentsPerEdge,
    jitterDeg: config.jitterDeg,
    smooth: true,
  });
}
