#!/usr/bin/env python3
"""
问题预防手册查阅工具
用于快速对照检查，避免重复踩坑
"""
import json
from pathlib import Path

PREVENTION_GUIDE = Path(__file__).parent / "PREVENTION_GUIDE.md"

def show_section(title):
    """显示指定章节内容"""
    content = PREVENTION_GUIDE.read_text(encoding='utf-8')
    
    # 找到章节开始和结束
    start_marker = f"## {title}"
    end_marker = "\n## "
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"❌ 未找到章节: {title}")
        return
    
    next_section_idx = content.find(end_marker, start_idx + len(start_marker))
    if next_section_idx == -1:
        section_content = content[start_idx:]
    else:
        section_content = content[start_idx:next_section_idx]
    
    print("\n" + "="*60)
    print(section_content.strip())
    print("="*60 + "\n")

def show_checklist():
    """显示检查清单"""
    content = PREVENTION_GUIDE.read_text(encoding='utf-8')
    
    # 找到检查清单部分
    start_marker = "## 六、检查清单"
    end_marker = "## 七、问题案例库"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ 未找到检查清单")
        return
    
    checklist_content = content[start_idx:end_idx]
    print("\n" + "="*60)
    print(checklist_content.strip())
    print("="*60 + "\n")

def show_case(case_num):
    """显示指定案例"""
    content = PREVENTION_GUIDE.read_text(encoding='utf-8')
    
    # 找到案例库部分
    start_marker = "## 七、问题案例库"
    start_idx = content.find(start_marker)
    
    if start_idx == -1:
        print("❌ 未找到案例库")
        return
    
    # 查找指定案例
    case_marker = f"### 案例 {case_num}："
    case_start = content.find(case_marker, start_idx)
    
    if case_start == -1:
        print(f"❌ 未找到案例 {case_num}")
        return
    
    # 找到下一个案例或文档结尾
    next_case_marker = f"### 案例 {case_num + 1}："
    next_case_start = content.find(next_case_marker, case_start)
    
    if next_case_start == -1:
        # 找到文档结尾或其他章节
        next_section = content.find("\n## ", case_start)
        if next_section == -1:
            case_content = content[case_start:]
        else:
            case_content = content[case_start:next_section]
    else:
        case_content = content[case_start:next_case_start]
    
    print("\n" + "="*60)
    print(case_content.strip())
    print("="*60 + "\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="问题预防手册查阅工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python check-prevention.py --list          # 列出所有章节
  python check-prevention.py --section "一、数据一致性保障"
  python check-prevention.py --checklist     # 显示检查清单
  python check-prevention.py --case 1        # 显示案例1
        """
    )
    
    parser.add_argument('--list', action='store_true', help='列出所有章节')
    parser.add_argument('--section', type=str, help='显示指定章节')
    parser.add_argument('--checklist', action='store_true', help='显示检查清单')
    parser.add_argument('--case', type=int, help='显示指定案例')
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📚 预防手册章节列表：")
        print("-" * 40)
        sections = [
            "一、数据一致性保障",
            "二、安全防护",
            "三、代码质量保障",
            "四、前端最佳实践",
            "五、工程化流程",
            "六、检查清单",
            "七、问题案例库"
        ]
        for i, section in enumerate(sections, 1):
            print(f"{i}. {section}")
        print("\n使用 --section 参数查看具体章节")
        
    elif args.section:
        show_section(args.section)
        
    elif args.checklist:
        show_checklist()
        
    elif args.case:
        show_case(args.case)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()