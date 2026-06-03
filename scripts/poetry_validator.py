#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏轼诗词验证系统 v1.0
严谨的三步式验证流程：候选→审核→入库
确保诗词完整性、真实性、准确性
@author: 行吟山河
"""

import json
import re
import hashlib
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PoetryCandidate:
    """诗词候选数据结构"""
    id: str
    title: str
    author: str
    type: str
    rhythmic: str
    paragraphs: List[str]
    core_verse: str
    source: str
    confidence: float = 0.0
    verification_status: str = "pending"
    route_id: Optional[str] = None
    related_route_ids: List[str] = field(default_factory=list)
    year: Optional[int] = None
    notes: str = ""
    verification_log: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "type": self.type,
            "rhythmic": self.rhythmic,
            "paragraphs": self.paragraphs,
            "coreVerse": self.core_verse,
            "source": self.source,
            "confidence": self.confidence,
            "verificationStatus": self.verification_status,
            "routeId": self.route_id,
            "relatedRouteIds": self.related_route_ids,
            "year": self.year,
            "notes": self.notes,
            "verificationLog": self.verification_log
        }


class PoetryValidator:
    """诗词验证器"""
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path.cwd()
        
        self.project_root = project_root
        self.data_v4 = project_root / "data-v4"
        self.data_v4_source = project_root / "data-v4-source"
        
        # 验证状态目录
        self.candidates_dir = self.data_v4_source / "诗词验证" / "候选"
        self.review_dir = self.data_v4_source / "诗词验证" / "审核"
        self.approved_dir = self.data_v4_source / "诗词验证" / "已通过"
        
        # 创建目录结构
        for dir_path in [self.candidates_dir, self.review_dir, self.approved_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 加载现有数据
        self.existing_poems = self._load_existing_poems()
        self.existing_titles = {p["title"]: p for p in self.existing_poems}
        
        # 验证规则
        self._init_validation_rules()
    
    def _load_existing_poems(self) -> List[Dict[str, Any]]:
        """加载现有诗词数据"""
        index_path = self.data_v4 / "poems-index.json"
        if not index_path.exists():
            return []
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("poems", [])
    
    def _init_validation_rules(self):
        """初始化验证规则"""
        # 常见错字检查
        self.common_errors = {
            "祇": "只",
            "祗": "只",
            "菴": "庵",
            "翦": "剪",
            "繋": "系",
            "髪": "发",
            "巻": "卷",
            "昇": "升",
            "歩": "步"
        }
        
        # 苏轼各时期地点关键词
        self.route_keywords = {
            "R00": ["眉山", "故乡", "中岩", "蟆颐", "老翁泉"],
            "R01": ["嘉祐", "汴京", "开封", "京师", "礼部"],
            "R02": ["嘉州", "犍为", "戎州", "泸州", "渝州", "三峡", "江陵"],
            "R03": ["凤翔", "签判", "石鼓", "东湖", "真兴寺"],
            "R04": ["治平", "父丧", "返蜀", "丁忧", "居丧"],
            "R05": ["熙宁", "变法", "安石", "神宗", "进京"],
            "R06": ["杭州", "西湖", "通判", "望湖楼", "孤山", "灵隐"],
            "R07": ["密州", "超然", "太守", "江城子", "水调歌头"],
            "R08": ["徐州", "黄楼", "百步洪", "吕梁洪", "抗洪"],
            "R09": ["湖州", "乌台", "诗案", "御史", "押解"],
            "R10": ["黄州", "东坡", "赤壁", "定风波", "念奴娇", "雪堂", "东坡居"],
            "R11": ["筠州", "金陵", "中山", "荆公", "王安石"],
            "R12": ["登州", "海市", "五日太守", "蓬莱阁"],
            "R13": ["汴京", "元祐", "玉堂", "翰林", "学士", "中书"],
            "R14": ["杭州", "苏堤", "再知", "太守", "六桥", "西湖"],
            "R15": ["颍州", "扬州", "平山堂", "欧阳修"],
            "R16": ["汴京", "南迁", "定州"],
            "R17": ["定州", "雪浪石", "中山松醪"],
            "R18": ["惠州", "儋州", "贬谪", "荔枝", "朝云", "白鹤峰", "桄榔庵"],
            "R19": ["常州", "遇赦", "渡海", "北归", "孙氏馆"]
        }
        
        # 苏轼生平年份对照
        self.year_ranges = {
            "R00": (1036, 1056),
            "R01": (1056, 1057),
            "R02": (1059, 1061),
            "R03": (1061, 1064),
            "R04": (1064, 1068),
            "R05": (1068, 1071),
            "R06": (1071, 1074),
            "R07": (1074, 1076),
            "R08": (1076, 1079),
            "R09": (1079, 1079),
            "R10": (1080, 1084),
            "R11": (1084, 1085),
            "R12": (1085, 1085),
            "R13": (1085, 1089),
            "R14": (1089, 1091),
            "R15": (1091, 1093),
            "R16": (1093, 1094),
            "R17": (1094, 1094),
            "R18": (1094, 1100),
            "R19": (1100, 1101)
        }
    
    def validate_integrity(self, candidate: PoetryCandidate) -> Tuple[bool, List[str]]:
        """验证完整性"""
        issues = []
        
        # 检查标题
        if not candidate.title or len(candidate.title.strip()) == 0:
            issues.append("标题为空")
        
        # 检查段落
        if not candidate.paragraphs or len(candidate.paragraphs) == 0:
            issues.append("内容段落为空")
        else:
            total_chars = sum(len(p) for p in candidate.paragraphs)
            if total_chars < 10:
                issues.append("内容过短")
        
        # 检查coreVerse
        if not candidate.core_verse:
            candidate.core_verse = candidate.paragraphs[0] if candidate.paragraphs else ""
        
        return len(issues) == 0, issues
    
    def validate_authenticity(self, candidate: PoetryCandidate) -> Tuple[bool, List[str]]:
        """验证真实性"""
        issues = []
        
        # 验证作者
        if candidate.author not in ["苏轼", "苏东坡", "东坡居士"]:
            issues.append("作者不是苏轼")
        
        # 基本格式检查
        text = " ".join(candidate.paragraphs)
        
        # 检查常见错字（可选警告）
        for wrong, correct in self.common_errors.items():
            if wrong in text:
                issues.append(f"发现异体字/旧字形 '{wrong}'（建议 '{correct}'）")
        
        return len(issues) == 0, issues
    
    def match_route(self, candidate: PoetryCandidate) -> Optional[str]:
        """智能匹配路线"""
        best_match = None
        max_score = 0
        
        combined_text = candidate.title + " " + " ".join(candidate.paragraphs)
        
        for route_id, keywords in self.route_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in combined_text:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_match = route_id
        
        # 只有匹配度足够高才返回
        if max_score >= 2:
            return best_match
        
        return None
    
    def calculate_confidence(self, candidate: PoetryCandidate) -> float:
        """计算置信度"""
        score = 0.0
        
        # 完整性
        if candidate.title:
            score += 0.2
        if candidate.paragraphs and len(candidate.paragraphs) > 0:
            score += 0.3
        
        # 真实性
        if candidate.author in ["苏轼", "苏东坡", "东坡居士"]:
            score += 0.2
        
        # 匹配度
        if candidate.route_id:
            score += 0.2
        
        # 来源可信度
        source_scores = {
            "chinese-poetry": 0.9,
            "全宋词": 0.95,
            "苏轼词集": 0.95,
            "行踪考提取": 0.85
        }
        score += source_scores.get(candidate.source, 0.5) * 0.1
        
        return min(score, 1.0)
    
    def create_candidate(self, data: Dict[str, Any], source: str) -> PoetryCandidate:
        """创建诗词候选"""
        candidate_id = f"C{len(list(self.candidates_dir.glob('*.json'))) + 1:04d}"
        
        candidate = PoetryCandidate(
            id=candidate_id,
            title=data.get("title", ""),
            author=data.get("author", "苏轼"),
            type="词" if "rhythmic" in data else "诗",
            rhythmic=data.get("rhythmic", ""),
            paragraphs=data.get("paragraphs", []),
            core_verse=data.get("paragraphs", [""])[0] if data.get("paragraphs") else "",
            source=source
        )
        
        # 验证
        is_integrity, integrity_issues = self.validate_integrity(candidate)
        is_authentic, authenticity_issues = self.validate_authenticity(candidate)
        
        candidate.verification_log.extend(integrity_issues)
        candidate.verification_log.extend(authenticity_issues)
        
        # 匹配路线
        candidate.route_id = self.match_route(candidate)
        if candidate.route_id:
            candidate.related_route_ids = [candidate.route_id]
        
        # 计算置信度
        candidate.confidence = self.calculate_confidence(candidate)
        
        # 设置状态
        if candidate.confidence >= 0.8 and is_integrity and is_authentic:
            candidate.verification_status = "ready_for_review"
        else:
            candidate.verification_status = "needs_manual_check"
        
        return candidate
    
    def save_candidate(self, candidate: PoetryCandidate):
        """保存候选到审核队列"""
        file_path = self.candidates_dir / f"{candidate.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(candidate.to_dict(), f, ensure_ascii=False, indent=2)
    
    def generate_review_report(self) -> Dict[str, Any]:
        """生成审核报告"""
        candidates = list(self.candidates_dir.glob("*.json"))
        
        stats = {
            "total": len(candidates),
            "ready_for_review": 0,
            "needs_manual_check": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "by_route": {}
        }
        
        for candidate_file in candidates:
            with open(candidate_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            status = data.get("verificationStatus", "pending")
            if status == "ready_for_review":
                stats["ready_for_review"] += 1
            else:
                stats["needs_manual_check"] += 1
            
            confidence = data.get("confidence", 0)
            if confidence >= 0.8:
                stats["high_confidence"] += 1
            elif confidence >= 0.6:
                stats["medium_confidence"] += 1
            else:
                stats["low_confidence"] += 1
            
            route_id = data.get("routeId")
            if route_id:
                stats["by_route"][route_id] = stats["by_route"].get(route_id, 0) + 1
        
        report_path = self.candidates_dir.parent / "审核报告.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "generatedAt": datetime.now().isoformat(),
                "statistics": stats
            }, f, ensure_ascii=False, indent=2)
        
        return stats
    
    def run_full_verification_pipeline(self) -> Dict[str, Any]:
        """运行完整验证流程"""
        print("=" * 80)
        print("苏轼诗词验证系统 v1.0")
        print("=" * 80)
        print()
        print("📋 验证流程:")
        print("  1️⃣ 完整性检查")
        print("  2️⃣ 真实性验证")
        print("  3️⃣ 路线智能匹配")
        print("  4️⃣ 置信度评估")
        print("  5️⃣ 生成审核报告")
        print()
        
        stats = self.generate_review_report()
        
        print("📊 当前状态:")
        print(f"  总候选数: {stats['total']}")
        print(f"  高置信度(≥0.8): {stats['high_confidence']}")
        print(f"  中置信度(0.6-0.8): {stats['medium_confidence']}")
        print(f"  低置信度(<0.6): {stats['low_confidence']}")
        print(f"  可直接审核: {stats['ready_for_review']}")
        print(f"  需人工检查: {stats['needs_manual_check']}")
        print()
        print("=" * 80)
        
        return stats


if __name__ == "__main__":
    validator = PoetryValidator()
    validator.run_full_verification_pipeline()
