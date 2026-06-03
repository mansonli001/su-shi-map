"""
lib_sync.py — data-v4 → public/data-v4 单向同步工具

设计原则：
  ① 唯一权威源是仓库根 data-v4/，public/data-v4 只是它的部署副本
  ② 任何脚本写完 data-v4/ 后必须调用 sync_public()，避免再写 public/
  ③ 用 rsync --delete 保证完全一致（处理重命名、删除）
  ④ 失败立即抛错，不允许"半同步"状态进入 git
  ⑤ 排除 scripts/ 和 icons/ —— 这些不是浏览器消费的资源，
     而且 scripts/ 里的 .ts 会被 Next.js type-check 误扫描

用法（在脚本结尾）：
    from lib_sync import sync_public
    sync_public()
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# 不应该出现在 public/data-v4 的子目录（构建脚本/源资源）
EXCLUDE_DIRS = ("scripts", "icons")

# 脚本通常在 scripts/ 下运行，但也可能从仓库根运行
_REPO_ROOT_CANDIDATES = [
    Path(__file__).resolve().parent.parent,  # scripts/.. → repo root
    Path.cwd(),
]


def _find_repo_root() -> Path:
    """定位仓库根目录（必须同时存在 data-v4/ 和 public/）。"""
    for cand in _REPO_ROOT_CANDIDATES:
        if (cand / "data-v4").is_dir() and (cand / "public").is_dir():
            return cand
    raise RuntimeError(
        "lib_sync: 找不到包含 data-v4/ 和 public/ 的仓库根目录"
    )


def sync_public(verbose: bool = True) -> None:
    """单向同步 data-v4/ → public/data-v4/，使两份完全一致。

    用 rsync 优先（速度快、支持 --delete + --exclude）；fallback 到 shutil.copytree。
    """
    root = _find_repo_root()
    src = root / "data-v4"
    dst = root / "public" / "data-v4"
    dst.parent.mkdir(parents=True, exist_ok=True)

    # 优先 rsync
    if shutil.which("rsync"):
        # 注意源末尾必须有 / 表示同步内容而非目录本身
        cmd = ["rsync", "-a", "--delete"]
        for ex in EXCLUDE_DIRS:
            cmd.extend(["--exclude", f"/{ex}"])
        cmd.extend([f"{src}/", f"{dst}/"])
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"rsync 同步失败: {result.stderr.strip() or result.stdout.strip()}"
            )
        if verbose:
            print(f"[lib_sync] rsync OK: {src} → {dst} (exclude: {EXCLUDE_DIRS})")
        return

    # Windows / 无 rsync 兜底
    if dst.exists():
        shutil.rmtree(dst)

    def _ignore(_dir, names):
        # 仅在顶层排除指定目录
        if Path(_dir).resolve() == src.resolve():
            return [n for n in names if n in EXCLUDE_DIRS]
        return []

    shutil.copytree(src, dst, ignore=_ignore)
    if verbose:
        print(f"[lib_sync] copytree OK: {src} → {dst} (exclude: {EXCLUDE_DIRS})")


if __name__ == "__main__":
    sync_public()
