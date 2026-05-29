/**
 * 坐标转换脚本 v4.0 修正版
 * WGS84 → GCJ-02（中国国测局加密算法）
 * 支持 Point / MultiPoint / LineString / MultiLineString / Polygon / MultiPolygon
 *
 * 用法: npx tsx scripts/convert-geojson.ts
 */

import * as fs from 'fs';
import * as path from 'path';

/** GCJ-02 加偏量 */
const PI = Math.PI;
const A = 6378245.0;
const EE = 0.00669342162296594323;

/**
 * WGS84 经度 → GCJ-02 经度
 */
function transformLat(lng: number, lat: number): number {
  const ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat +
    0.1 * lng * lat + 0.2 * Math.sqrt(Math.abs(lng));
  const ret2 = (20.0 * Math.sin(6.0 * lng * PI) * Math.sin(2.0 * lat * PI))
    - (20.0 * Math.sin(2.0 * lng * PI) * Math.sin(4.0 * lat * PI))
    - (16.0 * Math.sin(lng * PI) * Math.sin(6.0 * lat * PI))
    - (16.0 * Math.sin(4.0 * lng * PI) * Math.sin(lat * PI));
  return ret + ret2;
}

/**
 * WGS84 纬度 → GCJ-02 纬度
 */
function transformLng(lng: number, lat: number): number {
  const ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng +
    0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng));
  const ret2 = (20.0 * Math.sin(6.0 * lng * PI) * Math.sin(2.0 * lat * PI))
    + (20.0 * Math.sin(2.0 * lng * PI) * Math.sin(4.0 * lat * PI))
    + (16.0 * Math.sin(lng * PI) * Math.sin(6.0 * lat * PI))
    + (16.0 * Math.sin(4.0 * lng * PI) * Math.sin(lat * PI));
  return ret + ret2;
}

/**
 * 将单个坐标点从 WGS84 转换为 GCJ-02
 */
function convertPoint(wgsLng: number, wgsLat: number): [number, number] {
  const gcjLng = transformLng(wgsLng, wgsLat);
  const gcjLat = transformLat(wgsLng, wgsLat);
  return [gcjLng, gcjLat];
}

/**
 * 递归转换坐标数组
 */
function convertCoordinates(coords: number[] | number[][] | number[][][] | number[][][][] | number[][][][][], depth: number): number[] | number[][] | number[][][] | number[][][][] | number[][][][][] {
  if (depth === 0) {
    // Point: [lng, lat]
    const [lng, lat] = coords as [number, number];
    return convertPoint(lng, lat);
  }

  if (depth === 1) {
    // MultiPoint / LineString: [[lng, lat], ...]
    return (coords as number[][]).map(point => convertPoint(point[0], point[1]));
  }

  if (depth === 2) {
    // Polygon / MultiLineString: [[[lng, lat], ...], ...]
    return (coords as number[][][]).map(ring =>
      ring.map(point => convertPoint(point[0], point[1]))
    );
  }

  if (depth === 3) {
    // MultiPolygon: [[[[lng, lat], ...], ...], ...]
    return (coords as number[][][][]).map(polygon =>
      polygon.map(ring =>
        ring.map(point => convertPoint(point[0], point[1]))
      )
    );
  }

  // depth === 4: MultiPolygon with extra array layer
  return (coords as number[][][][][]).map(mp =>
    mp.map(polygon =>
      polygon.map(ring =>
        ring.map(point => convertPoint(point[0], point[1]))
      )
    )
  );
}

/**
 * 获取 GeoJSON 几何对象的坐标深度
 */
function getCoordDepth(geom: unknown): number {
  if (Array.isArray(geom)) {
    const first = geom[0];
    if (Array.isArray(first)) return 1 + getCoordDepth(first);
    if (typeof first === 'number') return 0;
  }
  return -1;
}

/**
 * 转换单个 GeoJSON Feature
 */
function convertFeature(feature: GeoJSON.Feature<GeoJSON.GeometryObject>): GeoJSON.Feature<GeoJSON.GeometryObject> {
  const geom = feature.geometry;
  if (!geom || geom === null) return feature;

  const depth = getCoordDepth(geom.coordinates);
  const newCoords = convertCoordinates(geom.coordinates, depth);

  return {
    ...feature,
    geometry: {
      ...geom,
      coordinates: newCoords,
    },
  };
}

/**
 * 转换整个 GeoJSON 文件
 */
function convertGeoJSON(inputPath: string, outputPath: string): void {
  console.log(`📖 读取: ${inputPath}`);
  const data = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));

  let features: GeoJSON.Feature[];
  if (data.type === 'FeatureCollection') {
    features = data.features;
  } else if (data.type === 'Feature') {
    features = [data];
  } else {
    throw new Error(`不支持的 GeoJSON 类型: ${data.type}`);
  }

  console.log(`📍 转换 ${features.length} 个要素...`);

  const converted = features.map(convertFeature);

  const output: GeoJSON.FeatureCollection = {
    type: 'FeatureCollection',
    features: converted,
  };

  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2), 'utf-8');
  console.log(`✅ 已写入: ${outputPath}`);
}

/**
 * 主函数
 */
function main(): void {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log('用法: npx tsx scripts/convert-geojson.ts <input.geojson> <output.geojson>');
    console.log('示例: npx tsx scripts/convert-geojson.ts data/song-wgs84.geojson data/song-gcj02.geojson');
    process.exit(1);
  }

  const inputPath = path.resolve(args[0]);
  const outputPath = path.resolve(args[1]);

  if (!fs.existsSync(inputPath)) {
    console.error(`❌ 文件不存在: ${inputPath}`);
    process.exit(1);
  }

  convertGeoJSON(inputPath, outputPath);
}

main();
