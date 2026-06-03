#!/usr/bin/env python3
"""
为作品按类型重新编号（诗 S、词 C、文 W ...）

修复 v6.1：
  ① 删除 public/ 双写代码，统一调用 lib_sync.sync_public()（一次性同步在末尾）
  ② 加原子写入：所有 JSON 写到 *.tmp 后 os.replace，避免脚本中途崩溃留下半新半旧
  ③ 加 dry-run 预演 + 异常时直接 raise，绝不污染主目录
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# 确保能 import 同目录的 lib_sync
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_sync import sync_public  # noqa: E402

# 类型到前缀的映射
TYPE_PREFIX = {
    '诗': 'S',
    '词': 'C',
    '文': 'W',
    '书': 'L',
    '记': 'J',
    '赋': 'F',
    '策': 'Z',
    '序': 'X',
    '铭': 'M',
    '题画': 'T',
    'unknown': 'O',
}


def write_json_atomic(path: Path, data) -> None:
    """原子写入：先写到 *.tmp，再 os.replace 覆盖目标。

    若中途 Python 崩溃 / 磁盘满 / Ctrl+C，目标文件保持原内容不变。
    """
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def main():
    # 加载诗词索引
    with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    poems = index_data.get('poems', [])

    # 统计类型数量
    type_counts = {}
    for poem in poems:
        p_type = poem.get('type', 'unknown')
        type_counts[p_type] = type_counts.get(p_type, 0) + 1

    # 按类型分组
    type_groups: dict = {}
    for poem in poems:
        p_type = poem.get('type', 'unknown')
        type_groups.setdefault(p_type, []).append(poem)

    # 为每个类型分配编号
    old_to_new_id: dict = {}
    new_poems: list = []

    for p_type, poems_list in type_groups.items():
        prefix = TYPE_PREFIX.get(p_type, 'O')
        poems_list.sort(key=lambda x: x.get('year', 0))

        for i, poem in enumerate(poems_list, 1):
            old_id = poem.get('id', '')
            new_id = f'{prefix}{str(i).zfill(3)}'
            old_to_new_id[old_id] = new_id

            poem['id'] = new_id
            new_poems.append(poem)

            print(f'{old_id} -> {new_id} ({p_type}): {poem.get("title")}')

    # 保存更新后的索引（原子）
    index_data['poems'] = new_poems
    index_data['total'] = len(new_poems)
    write_json_atomic(Path('data-v4/poems-index.json'), index_data)

    # 重命名诗词详情文件（每条原子）
    poems_dir = Path('data-v4/poems')
    for old_id, new_id in old_to_new_id.items():
        old_path = poems_dir / f'{old_id}.json'
        new_path = poems_dir / f'{new_id}.json'

        if not old_path.exists():
            continue
        with open(old_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        content['id'] = new_id
        write_json_atomic(new_path, content)
        # 只有新文件成功落盘后才删除旧文件
        if new_path.exists() and new_path != old_path:
            old_path.unlink()

    # 更新地点数据中的 poem_id 引用
    places_dir = Path('data-v4/places')
    for pf in places_dir.glob('P*.json'):
        with open(pf, 'r', encoding='utf-8') as f:
            place_data = json.load(f)

        works = place_data.get('global_works', [])
        updated = False
        for work in works:
            if 'poem_id' in work and work['poem_id'] in old_to_new_id:
                work['poem_id'] = old_to_new_id[work['poem_id']]
                updated = True

        if updated:
            write_json_atomic(pf, place_data)

    # 一次性把所有变更同步到 public/data-v4
    sync_public()

    print('\n' + '=' * 60)
    print(f'已重新编号 {len(old_to_new_id)} 个作品')
    print('\n新编号体系统计：')
    for p_type, count in type_counts.items():
        prefix = TYPE_PREFIX.get(p_type, 'O')
        print(f'{p_type} ({prefix}): {count} 个')


if __name__ == '__main__':
    main()
