#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代旅游信息自动补全工具 - 优化版
使用高德地图API自动补全景点的POI信息（地址、描述、图片等）
优化搜索策略，提高匹配成功率
"""

import json
import os
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

class AmapAutoFiller:
    """高德地图自动补全器"""
    
    def __init__(self, project_root: str = None, amap_key: str = None):
        if project_root is None:
            project_root = self._find_project_root()
        
        self.project_root = Path(project_root)
        self.data_v4 = self.project_root / "data-v4"
        self.places_dir = self.data_v4 / "places"
        
        # 加载配置
        self.amap_key = amap_key or self._load_amap_key()
        
        # 统计信息
        self.stats = {
            "total_places": 0,
            "with_poi": 0,
            "without_poi": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }
        
        # 缓存
        self._cache = {}
        self.cache_file = self.project_root / "data-v4-source" / "amap-poi-cache.json"
        self._load_cache()
    
    def _find_project_root(self) -> Path:
        """寻找项目根目录"""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / "README.md").exists() or (parent / "data-v4").exists():
                return parent
        return current
    
    def _load_amap_key(self) -> Optional[str]:
        """加载高德地图API Key"""
        possible_locations = [
            self.project_root / ".env.local",
            self.project_root / ".env",
            os.environ.get("AMAP_KEY"),
            os.environ.get("AMAP_WEB_SERVICE_KEY"),
        ]
        
        for loc in possible_locations:
            if loc and Path(loc).exists():
                try:
                    with open(loc, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'AMAP_WEB_SERVICE_KEY=' in line:
                                return line.strip().split('=')[1]
                            if 'AMAP_KEY=' in line and 'NEXT_PUBLIC' not in line:
                                return line.strip().split('=')[1]
                except:
                    pass
            elif loc:
                return loc
        
        print("⚠️  未找到高德地图API Key")
        return None
    
    def _load_cache(self):
        """加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                print(f"✅ 加载了 {len(self._cache)} 条缓存记录")
            except Exception as e:
                print(f"⚠️  加载缓存失败: {e}")
    
    def _save_cache(self):
        """保存缓存"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)
    
    def load_places_index(self) -> Dict[str, Any]:
        """加载places索引"""
        index_path = self.data_v4 / "places-index.json"
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_place_detail(self, place_id: str) -> Optional[Dict[str, Any]]:
        """加载地点详情"""
        file_path = self.places_dir / f"{place_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_place_detail(self, place_id: str, data: Dict[str, Any]):
        """保存地点详情"""
        file_path = self.places_dir / f"{place_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def search_poi(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """在高德地图搜索POI"""
        ancient_name = place.get("ancient_name", "")
        modern_name = place.get("modern_name", "")
        
        # 提取现代名称中的核心地点
        core_names = []
        if modern_name:
            # 去掉括号内容
            clean_name = modern_name.replace("（", "(").replace("）", ")")
            clean_name = ''.join(clean_name.split('(')[:1]).strip()
            clean_name = ''.join(clean_name.split('（')[:1]).strip()
            core_names.append(clean_name)
            # 添加古地名
            if ancient_name and ancient_name != modern_name and ancient_name not in modern_name:
                core_names.append(ancient_name)
        
        # 生成搜索关键词（优化策略）
        keywords = []
        for name in core_names:
            if not name:
                continue
            # 直接搜索地名
            keywords.append(name)
            # 尝试添加常用后缀
            for suffix in ["景区", "景点", "旅游区", "公园", "纪念馆", "故居"]:
                if suffix not in name:
                    keywords.append(f"{name} {suffix}")
            # 尝试添加苏轼相关
            if "苏轼" not in name and "东坡" not in name:
                keywords.append(f"{name} 苏轼")
                keywords.append(f"{name} 苏东坡")
        
        # 去重
        keywords = list(dict.fromkeys(keywords))
        
        # 尝试各种关键词组合
        for keyword in keywords:
            if not keyword:
                continue
            
            # 检查缓存
            if keyword in self._cache:
                cached = self._cache[keyword]
                if cached and cached.get("pois"):
                    return cached
            
            if not self.amap_key:
                continue
            
            # 先不限制城市，扩大搜索范围
            result = self._call_amap_search(keyword, None, None)
            if result:
                self._cache[keyword] = result
                return result
            
            # 如果没有结果，再用坐标缩小范围
            lng, lat = place.get("lng"), place.get("lat")
            if lng and lat:
                result_with_loc = self._call_amap_search(keyword, lng, lat)
                if result_with_loc:
                    self._cache[keyword + "_loc"] = result_with_loc
                    return result_with_loc
        
        return None
    
    def _call_amap_search(self, keyword: str, lng: float = None, lat: float = None) -> Optional[Dict[str, Any]]:
        """调用高德地图搜索API"""
        url = "https://restapi.amap.com/v3/place/text"
        params = {
            "key": self.amap_key,
            "keywords": keyword,
            "output": "json",
            "offset": 10,
            "extensions": "all",
        }
        
        # 如果有坐标，设置搜索中心
        if lng is not None and lat is not None:
            params["location"] = f"{lng},{lat}"
            params["radius"] = 30000  # 30公里范围
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1" and int(data.get("count", 0)) > 0:
                pois = data.get("pois", [])
                if pois:
                    return {
                        "keyword": keyword,
                        "pois": pois,
                        "timestamp": time.time(),
                    }
            
        except Exception as e:
            print(f"   ⚠️  搜索 '{keyword}' 失败: {e}")
            pass
        
        return None
    
    def _is_place_missing_poi(self, place: Dict[str, Any], detail: Optional[Dict[str, Any]] = None) -> bool:
        """判断地点是否缺少POI信息"""
        if detail and "modern_visit" in detail and detail["modern_visit"]:
            return False
        return True
    
    def fill_places(self, max_places: int = None, place_ids: List[str] = None):
        """批量补全POI信息"""
        print("=" * 80)
        print("行吟山河 - 现代旅游信息自动补全工具（优化版）")
        print("=" * 80)
        
        index = self.load_places_index()
        places = index["places"]
        
        self.stats["total_places"] = len(places)
        
        # 过滤需要补全的地点
        places_to_fill = []
        for place in places:
            detail = self.load_place_detail(place["id"])
            if self._is_place_missing_poi(place, detail):
                self.stats["without_poi"] += 1
                places_to_fill.append((place, detail))
            else:
                self.stats["with_poi"] += 1
        
        print(f"\n📊 统计: {self.stats['total_places']} 个地点")
        print(f"   - 已有POI: {self.stats['with_poi']}")
        print(f"   - 待补全: {self.stats['without_poi']}\n")
        
        # 如果指定了place_ids，只处理这些
        if place_ids:
            places_to_fill = [p for p in places_to_fill if p[0]["id"] in place_ids]
        
        if max_places:
            places_to_fill = places_to_fill[:max_places]
        
        # 开始处理
        for i, (place, detail) in enumerate(places_to_fill, 1):
            place_id = place["id"]
            ancient_name = place.get("ancient_name", "")
            modern_name = place.get("modern_name", "")
            
            print(f"[{i}/{len(places_to_fill)}] {place_id}: {ancient_name} / {modern_name}")
            
            if not detail:
                print(f"   ⏭️  没有详情文件，跳过")
                self.stats["skipped"] += 1
                continue
            
            # 搜索POI
            poi_data = self.search_poi(place)
            if poi_data and poi_data.get("pois"):
                best_poi = self._select_best_poi(place, poi_data["pois"])
                if best_poi:
                    self._update_place_with_poi(place_id, detail, best_poi)
                    self.stats["success"] += 1
                else:
                    print(f"   ⚠️  找到POI但无法匹配")
                    self.stats["failed"] += 1
            else:
                print(f"   ❌ 未找到POI信息")
                self.stats["failed"] += 1
            
            # 防止频率限制
            if i < len(places_to_fill):
                time.sleep(0.3)
        
        # 保存缓存
        self._save_cache()
        
        # 打印统计
        self._print_stats()
    
    def _select_best_poi(self, place: Dict[str, Any], pois: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """选择最佳POI"""
        if not pois:
            return None
        
        ancient_name = place.get("ancient_name", "")
        modern_name = place.get("modern_name", "")
        
        # 优先匹配包含古地名或苏轼相关的POI
        for poi in pois:
            poi_name = poi.get("name", "")
            if ancient_name and ancient_name in poi_name:
                return poi
            if "苏轼" in poi_name or "东坡" in poi_name:
                return poi
        
        # 其次匹配类型为景点/景区的
        for poi in pois:
            poi_type = poi.get("type", "")
            if any(t in poi_type for t in ["风景名胜", "旅游景点", "公园"]):
                return poi
        
        # 返回第一个
        return pois[0]
    
    def _update_place_with_poi(self, place_id: str, detail: Dict[str, Any], poi: Dict[str, Any]):
        """用POI更新地点详情"""
        modern_visit = {
            "amap_poi_id": poi.get("id"),
            "amap_name": poi.get("name"),
            "address": poi.get("address"),
            "location": poi.get("location"),
            "cityname": poi.get("cityname"),
            "adname": poi.get("adname"),
            "type": poi.get("type"),
            "typecode": poi.get("typecode"),
            "tel": poi.get("tel"),
            "rating": poi.get("rating"),
            "cost": poi.get("cost"),
            "open_time": poi.get("opentime") or poi.get("opentime_tod"),
            "photos": [],
            "recommendation": "",
            "best_time_to_visit": "",
            "transportation": "",
        }
        
        # 提取照片（如果有）
        if poi.get("photos"):
            for photo in poi["photos"][:5]:
                modern_visit["photos"].append({
                    "title": photo.get("title"),
                    "url": photo.get("url"),
                })
        
        detail["modern_visit"] = modern_visit
        detail["amap_updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        
        self.save_place_detail(place_id, detail)
        
        print(f"   ✅ 已更新POI信息: {modern_visit['amap_name']}")
    
    def _print_stats(self):
        """打印统计"""
        print("\n" + "=" * 80)
        print("处理完成！")
        print("=" * 80)
        print(f"📁 总地点数: {self.stats['total_places']}")
        print(f"✅ 已补全: {self.stats['success']}")
        print(f"❌ 失败: {self.stats['failed']}")
        print(f"⏭️  跳过: {self.stats['skipped']}")
        print(f"📦 缓存条目: {len(self._cache)}")


if __name__ == "__main__":
    import sys
    
    filler = AmapAutoFiller()
    
    max_places = None
    place_ids = None
    
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            max_places = int(sys.argv[1])
        else:
            place_ids = sys.argv[1:]
    
    filler.fill_places(max_places=max_places, place_ids=place_ids)