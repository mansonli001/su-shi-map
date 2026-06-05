#!/usr/bin/env python3
"""
综合检测脚本 - 固化专家方法论
覆盖：数据一致性、工程化规范、安全防护、性能优化、移动端适配
"""
import json
import os
import re
from pathlib import Path

# 颜色输出
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_title(title):
    print(f'\n{BLUE}=== {title} ==={RESET}')
    print('=' * 70)

def print_pass(msg):
    print(f'{GREEN}✓ {msg}{RESET}')

def print_fail(msg):
    print(f'{RED}✗ {msg}{RESET}')

def print_warn(msg):
    print(f'{YELLOW}⚠ {msg}{RESET}')

def check_data_consistency():
    """单一数据源检查：data-v4/ 与 public/data-v4/ 是否一致"""
    print_title('1. 单一数据源一致性检查')
    
    data_dir = Path('data-v4')
    public_dir = Path('public/data-v4')
    
    issues = []
    
    # 检查 poems 目录
    data_poems = set(f.name for f in (data_dir / 'poems').glob('*.json'))
    public_poems = set(f.name for f in (public_dir / 'poems').glob('*.json'))
    
    if data_poems != public_poems:
        missing_in_public = data_poems - public_poems
        extra_in_public = public_poems - data_poems
        
        if missing_in_public:
            issues.append(f'public/data-v4/poems 缺少 {len(missing_in_public)} 个文件')
        if extra_in_public:
            issues.append(f'public/data-v4/poems 多余 {len(extra_in_public)} 个文件')
    
    # 检查 places 目录
    data_places = set(f.name for f in (data_dir / 'places').glob('*.json'))
    public_places = set(f.name for f in (public_dir / 'places').glob('*.json'))
    
    if data_places != public_places:
        issues.append(f'places 目录不一致: data={len(data_places)}, public={len(public_places)}')
    
    # 检查索引文件
    index_files = ['poems-index.json', 'places-index.json', 'routes-index.json']
    for idx_file in index_files:
        data_path = data_dir / idx_file
        public_path = public_dir / idx_file
        
        if data_path.exists() != public_path.exists():
            issues.append(f'索引文件 {idx_file} 存在性不一致')
        elif data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                data_content = f.read().strip()
            with open(public_path, 'r', encoding='utf-8') as f:
                public_content = f.read().strip()
            
            if data_content != public_content:
                issues.append(f'索引文件 {idx_file} 内容不一致')
    
    if issues:
        for issue in issues:
            print_fail(issue)
        return False
    else:
        print_pass('data-v4/ 与 public/data-v4/ 完全一致')
        return True

def check_poem_consistency():
    """诗词数据一致性检查"""
    print_title('2. 诗词数据一致性检查')
    
    with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    poems_index = index_data.get('poems', [])
    poems_dir = Path('data-v4/poems')
    
    inconsistencies = []
    
    for poem in poems_index:
        pid = poem.get('id', '')
        index_title = poem.get('title', '')
        
        fpath = poems_dir / f'{pid}.json'
        if not fpath.exists():
            inconsistencies.append({'id': pid, 'issue': '文件缺失'})
            continue
        
        with open(fpath, 'r', encoding='utf-8') as f:
            detail_data = json.load(f)
        
        detail_title = detail_data.get('title', '')
        if index_title != detail_title:
            inconsistencies.append({'id': pid, 'issue': f'标题不一致: "{index_title}" vs "{detail_title}"'})
        
        paragraphs = detail_data.get('paragraphs', [])
        fullText = detail_data.get('fullText', '')
        if not paragraphs and not fullText:
            inconsistencies.append({'id': pid, 'issue': '缺少内容(paragraphs/fullText)'})
        
        index_year = poem.get('year', 0)
        detail_year = detail_data.get('year', 0)
        if index_year != 0 and detail_year != 0 and index_year != detail_year:
            inconsistencies.append({'id': pid, 'issue': f'年份不一致: {index_year} vs {detail_year}'})
    
    if inconsistencies:
        print_fail(f'发现 {len(inconsistencies)} 处不一致:')
        for issue in inconsistencies:
            print(f'  [{issue["id"]}] {issue["issue"]}')
        return False
    else:
        print_pass(f'✓ 所有 {len(poems_index)} 首诗词数据一致')
        return True

def check_security():
    """安全检查：XSS防护"""
    print_title('3. 安全检查（XSS防护）')
    
    issues = []
    dangerously_pattern = re.compile(r'<[^>]*dangerouslySetInnerHTML[^>]*>', re.IGNORECASE)
    
    for root, dirs, files in os.walk('app'):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                filepath = Path(root) / f
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if dangerously_pattern.search(content):
                        issues.append(f'{filepath}: 使用了 dangerouslySetInnerHTML')
    
    if issues:
        for issue in issues:
            print_fail(issue)
        print_warn('建议：改用纯React节点解析或DOMPurify处理')
        return False
    else:
        print_pass('未发现 dangerouslySetInnerHTML 使用')
        return True

def check_performance():
    """性能检查：事件去重、请求竞态"""
    print_title('4. 性能优化检查')
    
    issues = []
    
    # 检查 AbortController 使用（在 fetch 中使用）
    abort_pattern = re.compile(r'AbortController|signal:\s*ctrl\.signal', re.IGNORECASE)
    has_abort = False
    
    for root, dirs, files in os.walk('.'):
        # 排除 node_modules 和 .next
        if 'node_modules' in root or '.next' in root:
            continue
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                filepath = Path(root) / f
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if abort_pattern.search(content):
                        has_abort = True
                        break
    
    if not has_abort:
        issues.append('未发现 AbortController 使用（可能存在请求竞态风险）')
    
    # 检查事件去重使用 Map
    map_pattern = re.compile(r'new\s+Map\s*\(', re.IGNORECASE)
    has_map = False
    
    for root, dirs, files in os.walk('.'):
        if 'node_modules' in root or '.next' in root:
            continue
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                filepath = Path(root) / f
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if map_pattern.search(content):
                        has_map = True
                        break
    
    if not has_map:
        issues.append('未发现 Map 数据结构用于事件去重（可能存在 O(n²) 复杂度）')
    
    if issues:
        for issue in issues:
            print_warn(issue)
        return False
    else:
        print_pass('✓ AbortController 和 Map 去重均已使用')
        return True

def check_mobile_adaptation():
    """移动端适配检查"""
    print_title('5. 移动端适配检查')
    
    issues = []
    
    # 检查 100dvh 使用
    dvh_pattern = re.compile(r'100dvh', re.IGNORECASE)
    has_dvh = False
    
    # 检查 safe-area-inset 使用
    safe_pattern = re.compile(r'safe-area-inset', re.IGNORECASE)
    has_safe = False
    
    # 检查 overscroll-behavior 使用
    overscroll_pattern = re.compile(r'overscroll-behavior', re.IGNORECASE)
    has_overscroll = False
    
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts') or f.endswith('.css'):
                filepath = Path(root) / f
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if dvh_pattern.search(content):
                            has_dvh = True
                        if safe_pattern.search(content):
                            has_safe = True
                        if overscroll_pattern.search(content):
                            has_overscroll = True
                except:
                    pass
    
    if not has_dvh:
        issues.append('未使用 100dvh（iOS Safari 地址栏弹收可能导致高度跳变）')
    if not has_safe:
        issues.append('未使用 safe-area-inset（全面屏设备可能遮挡内容）')
    if not has_overscroll:
        issues.append('未使用 overscroll-behavior（滚动穿透可能影响体验）')
    
    if issues:
        for issue in issues:
            print_warn(issue)
        return False
    else:
        print_pass('✓ 100dvh、safe-area-inset、overscroll-behavior 均已配置')
        return True

def check_defensive_coding():
    """防御性编程检查"""
    print_title('6. 防御性编程检查')
    
    issues = []
    
    # 检查 error instanceof Error 处理
    error_pattern = re.compile(r'error:\s*any', re.IGNORECASE)
    bad_error = []
    
    for root, dirs, files in os.walk('app'):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                filepath = Path(root) / f
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if error_pattern.search(content):
                        bad_error.append(f'{filepath}')
    
    if bad_error:
        issues.append(f'发现 {len(bad_error)} 处 error: any 用法')
        for item in bad_error:
            print(f'  {item}')
    
    # 检查 SSR 防护
    ssr_pattern = re.compile(r'typeof\s+window\s*===', re.IGNORECASE)
    has_ssr_protection = False
    
    for root, dirs, files in os.walk('lib'):
        for f in files:
            if f.endswith('.ts'):
                filepath = Path(root) / f
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if ssr_pattern.search(content):
                        has_ssr_protection = True
                        break
    
    if not has_ssr_protection:
        issues.append('未发现 typeof window 检查（SSR 环境可能出错）')
    
    if issues:
        print_warn('建议：使用 error instanceof Error 或 typeof error === "string"')
        return False
    else:
        print_pass('✓ 防御性编程规范已遵循')
        return True

def check_atomic_write():
    """原子写入检查"""
    print_title('7. 原子写入检查')
    
    issues = []
    
    # 检查 Python 脚本中的原子写入模式
    for f in Path('scripts').glob('*.py'):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            # 检查是否使用 os.replace 或临时文件模式
            if 'os.replace' not in content and '.tmp' not in content.lower():
                if 'open(' in content and ('w' in content or 'write' in content):
                    issues.append(f'{f}: 未使用原子写入模式（建议使用 *.tmp + os.replace）')
    
    if issues:
        for issue in issues:
            print_warn(issue)
        return False
    else:
        print_pass('✓ 所有脚本已使用原子写入模式')
        return True

def check_single_source():
    """单一数据源检查"""
    print_title('8. 单一数据源验证')
    
    issues = []
    
    # 检查 store.ts 是否有重复的成就数据
    store_path = Path('lib/store.ts')
    if store_path.exists():
        with open(store_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 检查是否有硬编码的成就数据
            if 'bronze' in content and 'silver' in content and 'gold' in content:
                if 'import.*achievements' not in content:
                    issues.append('lib/store.ts: 可能存在重复的成就数据硬编码')
    
    # 检查是否存在唯一数据源
    achievements_path = Path('lib/achievements.ts')
    if not achievements_path.exists():
        issues.append('lib/achievements.ts: 成就数据源文件不存在')
    
    if issues:
        for issue in issues:
            print_fail(issue)
        return False
    else:
        print_pass('✓ 单一数据源规范已遵循')
        return True

def main():
    """主入口"""
    print(f'{BLUE}🚀 苏轼地图项目综合检测脚本{RESET}')
    print(f'{BLUE}基于专家方法论固化的检测方案{RESET}')
    print('=' * 70)
    
    checks = [
        check_data_consistency,
        check_poem_consistency,
        check_security,
        check_performance,
        check_mobile_adaptation,
        check_defensive_coding,
        check_atomic_write,
        check_single_source,
    ]
    
    results = [check() for check in checks]
    
    print('\n' + '=' * 70)
    if all(results):
        print(f'{GREEN}🎉 所有检查通过！项目状态良好。{RESET}')
    else:
        failed = len([r for r in results if not r])
        print(f'{YELLOW}⚠ 检测完成，{failed} 项检查存在问题需要修复。{RESET}')

if __name__ == '__main__':
    main()
