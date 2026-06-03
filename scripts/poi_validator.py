#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高德POI验证核对系统 v1.0
确保POI信息准确、与路线匹配
@author: 行吟山河
"""

import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class POIVerification:
    """POI验证记录"""
    place_id: str
    place_name: str
    amap_poi_id: Optional[str] = None
    amap_name: Optional[str] = None
    amap_address: Optional[str] = None
    verified: bool = False
    confidence: float = 0.0
    verification_notes: str = ""
    verification_time: Optional[str] = None


class POIValidator:
    """POI验证器"""
    
    def __init__(self, project_root: Path = None, amap_key: str = None):
        if project_root is None:
            project_root = Path.cwd()
        
        self.project_root = project_root
        self.data_v4 = project_root / "data-v4"
        self.amap_key = amap_key or os.environ.get("AMAP_KEY", "")
        
        # 验证状态目录
        self.poi_verification_dir = self.data_v4 / "meta" / "poi-verification"
        self.poi_verification_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载现有数据
        self.places_index = self._load_places_index()
        self.existing_verifications = self._load_existing_verifications()
    
    def _load_places_index(self) -> Dict[str, Any]:
        """加载地点索引"""
        index_path = self.data_v4 / "places-index.json"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"poems": []}
    
    def _load_existing_verifications(self) -> Dict[str, POIVerification]:
        """加载现有验证记录"""
        verifications = {}
        for file in self.poi_verification_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    v = POIVerification(
                        place_id=data["placeId"],
                        place_name=data["placeName"],
                        amap_poi_id=data.get("amapPoiId"),
                        amap_name=data.get("amapName"),
                        amap_address=data.get("amapAddress"),
                        verified=data.get("verified", False),
                        confidence=data.get("confidence", 0.0),
                        verification_notes=data.get("verificationNotes", ""),
                        verification_time=data.get("verificationTime")
                    )
                    verifications[v.place_id] = v
            except Exception as e:
                print(f"⚠️  加载验证记录 {file} 失败: {e}")
        return verifications
    
    def verify_place_poi(self, place: Dict[str, Any]) -> POIVerification:
        """验证单个地点的POI"""
        verification = POIVerification(
            place_id=place["id"],
            place_name=place.get("modern_name", place.get("ancient_name", ""))
        )
        
        # 如果已有高德数据，先进行一致性检查
        if "amap_address" in place:
            verification.amap_address = place["amap_address"]
            verification.confidence = 0.5
        
        # 如果有API key，进行实时验证
        if self.amap_key:
            verification = self._verify_with_amap(place, verification)
        
        verification.verification_time = datetime.now().isoformat()
        return verification
    
    def _verify_with_amap(self, place: Dict[str, Any], verification: POIVerification) -> POIVerification:
        """使用高德API验证"""
        place_name = place.get("modern_name", place.get("ancient_name", ""))
        lng = place.get("lng")
        lat = place.get("lat")
        
        # 搜索POI
        search_results = self._search_amap_poi(place_name, lng, lat)
        
        if search_results:
            # 取第一个结果作为最佳匹配
            best_poi = search_results[0]
            verification.amap_poi_id = best_poi.get("id")
            verification.amap_name = best_poi.get("name")
            verification.amap_address = best_poi.get("address")
            
            # 计算匹配度
            verification.confidence = self._calculate_match_confidence(place_name, best_poi)
            verification.verified = verification.confidence >= 0.7
        
        return verification
    
    def _search_amap_poi(self, keyword: str, lng: float = None, lat: float = None) -> List[Dict[str, Any]]:
        """调用高德API搜索POI"""
        if not self.amap_key:
            return []
        
        url = "https://restapi.amap.com/v3/place/text"
        params = {
            "key": self.amap_key,
            "keywords": keyword,
            "output": "json",
            "offset": 10
        }
        
        if lng is not None and lat is not None:
            params["location"] = f"{lng},{lat}"
            params["citylimit"] = "true"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1":
                return data.get("pois", [])
        except Exception as e:
            print(f"⚠️  API请求失败: {e}")
        
        return []
    
    def _calculate_match_confidence(self, place_name: str, poi: Dict[str, Any]) -> float:
        """计算匹配置信度"""
        confidence = 0.0
        
        poi_name = poi.get("name", "")
        
        # 精确匹配
        if place_name == poi_name:
            confidence = 1.0
        # 包含匹配
        elif place_name in poi_name or poi_name in place_name:
            confidence = 0.8
        # 部分匹配
        elif any(word in place_name and word in poi_name for word in ["山", "湖", "寺", "楼", "亭"]):
            confidence = 0.6
        
        return confidence
    
    def save_verification(self, verification: POIVerification):
        """保存验证记录"""
        file_path = self.poi_verification_dir / f"{verification.place_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "placeId": verification.place_id,
                "placeName": verification.place_name,
                "amapPoiId": verification.amap_poi_id,
                "amapName": verification.amap_name,
                "amapAddress": verification.amap_address,
                "verified": verification.verified,
                "confidence": verification.confidence,
                "verificationNotes": verification.verification_notes,
                "verificationTime": verification.verification_time
            }, f, ensure_ascii=False, indent=2)
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        places = self.places_index.get("poems", [])
        
        total = 0
        verified = 0
        high_confidence = 0
        need_review = 0
        
        for place in places:
            place_id = place["id"]
            if place_id in self.existing_verifications:
                v = self.existing_verifications[place_id]
                if v.verified:
                    verified += 1
                if v.confidence >= 0.7:
                    high_confidence += 1
                else:
                    need_review += 1
            else:
                need_review += 1
        
        report = {
            "generatedAt": datetime.now().isoformat(),
            "totalPlaces": len(places),
            "verified": verified,
            "highConfidence": high_confidence,
            "needReview": need_review
        }
        
        report_path = self.poi_verification_dir / "verification-report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def run_full_verification(self, dry_run: bool = True):
        """运行完整验证流程"""
        print("=" * 80)
        print("高德POI验证核对系统 v1.0")
        print("=" * 80)
        print()
        
        if dry_run:
            print("⚠️  DRY RUN 模式：只生成报告，不实际调用API")
            print()
        
        places = self.places_index.get("poems", [])
        
        for i, place in enumerate(places, 1):
            print(f"[{i}/{len(places)}] {place['id']}: {place.get('modern_name', place.get('ancient_name', ''))}")
            
            if not dry_run:
                verification = self.verify_place_poi(place)
                self.save_verification(verification)
        
        report = self.generate_verification_report()
        
        print()
        print("=" * 80)
        print("📊 验证报告:")
        print("=" * 80)
        print(f"  总地点数: {report['totalPlaces']}")
        print(f"  已验证: {report['verified']}")
        print(f"  高置信度: {report['highConfidence']}")
        print(f"  需审核: {report['needReview']}")
        print()
        print("📍 验证记录: data-v4/meta/poi-verification/")
        print()


if __name__ == "__main__":
    import os
    validator = POIValidator()
    validator.run_full_verification(dry_run=True)
