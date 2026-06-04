# 苏轼地图 · 问题预防手册

> **目标**：记录常见问题及其预防措施，建立长期记忆，避免重复踩坑
> **版本**：v1.0
> **更新日期**：2026-06-03

---

## 📚 目录

1. [数据一致性保障](#一数据一致性保障)
2. [安全防护](#二安全防护)
3. [代码质量保障](#三代码质量保障)
4. [前端最佳实践](#四前端最佳实践)
5. [工程化流程](#五工程化流程)
6. [检查清单](#六检查清单)
7. [问题案例库](#七问题案例库)

---

## 一、数据一致性保障

### 1.1 双写模式问题
**问题描述**：`data-v4/` 和 `public/data-v4/` 双目录手动同步导致数据漂移
**历史案例**：CHANGELOG #9 - 前端只显示68首诗词（public目录缺文件）

**预防方案**：
```bash
# 使用 symlink 替代双写
rm -rf public/data-v4 && ln -s ../data-v4 public/data-v4
```

**执行时机**：项目初始化时执行一次，后续脚本只写 `data-v4/`

---

### 1.2 批量操作原子性
**问题描述**：批量重命名/修改时崩溃导致数据半新半旧，无法回滚
**历史案例**：`renumber-by-type.py` 执行中断

**预防方案**（三步法）：
```python
# 1. 先备份
import shutil, datetime
backup = Path(f'data-v4-backups/{datetime.datetime.now():%Y%m%d_%H%M%S}')
shutil.copytree('data-v4', backup)

# 2. 原子写入
def atomic_write_json(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)  # POSIX原子操作

# 3. 最后批量删除旧文件
```

**执行时机**：所有批量数据修改操作

---

### 1.3 数据迁移可回溯
**问题描述**：破坏性操作无记录，无法追踪变更历史

**预防方案**：每次迁移输出 `migration_log.json`
```json
{
  "migration_id": "20260603_renumber_by_type",
  "executed_at": "2026-06-03T14:23:00+08:00",
  "mapping": { "W001": "S001", "W002": "C001" },
  "affected_files": ["data-v4/places/P001.json"],
  "reversible": true,
  "backup_path": "data-v4-backups/20260603_142300"
}
```

**执行时机**：所有ID变更、字段重命名等破坏性操作

---

## 二、安全防护

### 2.1 XSS 攻击防护
**问题描述**：`dangerouslySetInnerHTML` 直接渲染外部数据
**历史案例**：`app/routes/[id]/page.tsx` 直接渲染路线描述

**预防方案**：
```tsx
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';

<ReactMarkdown rehypePlugins={[rehypeSanitize]}>
  {userContent}
</ReactMarkdown>
```

**适用场景**：所有用户输入、外部数据源渲染

---

### 2.2 输入验证规范
| 验证项 | 规则 | 示例 |
|--------|------|------|
| HTML转义 | 所有输出前进行转义 | `html.escape(content)` |
| 长度限制 | 字符串最大长度限制 | 标题≤200字符 |
| 内容白名单 | 仅允许特定HTML标签 | `<strong>`, `<em>` |

---

## 三、代码质量保障

### 3.1 类型系统统一
**问题描述**：V3/V4 双字段混用（camelCase vs snake_case）
**历史案例**：`types/index.ts` 与 `PlaceCard.tsx` 字段不统一

**预防方案**：
1. 新建 `types/v4.ts` 完全 mirror Python 数据 schema（全 snake_case）
2. 写 `lib/v3-to-v4-adapter.ts` 做版本过渡
3. `tsconfig.json` 开启 `"strict": true`

**执行时机**：类型定义时

---

### 3.2 脚本骨架统一
**问题描述**：46个脚本重复实现路径、IO等基础功能

**预防方案**：抽 `scripts/lib_data.py`
```python
from pathlib import Path
import json, os, shutil, datetime

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data-v4"

def atomic_write_json(path: Path, data: dict | list):
    tmp = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def backup_data(prefix: str = "auto"):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = PROJECT_ROOT / "data-v4-backups" / f"{prefix}_{ts}"
    shutil.copytree(DATA_DIR, backup)
    return backup

def load_index(name: str) -> dict:
    return json.loads((DATA_DIR / f"{name}-index.json").read_text("utf-8"))

def save_index(name: str, data: dict):
    atomic_write_json(DATA_DIR / f"{name}-index.json", data)
```

**执行时机**：所有新脚本必须引用，现有脚本逐步迁移

---

### 3.3 性能优化规范
**问题描述**：O(n²) 算法在大数据量时性能下降
**历史案例**：`PlaceCard.tsx` 事件去重使用 `some()`

**预防方案**：
```tsx
// 优化前（O(n²)）
const exists = acc.some(existing => existing.title === ev.title);

// 优化后（O(n)）
const seen = new Set<string>();
const uniqueEvents = events.filter(ev => {
  const key = `${ev.title}|${ev.year}`;
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});
```

**检查要点**：
- 避免嵌套循环
- 使用 Set/Map 替代数组查找
- 大数据量时考虑分页/懒加载

---

## 四、前端最佳实践

### 4.1 内存泄漏预防
**问题描述**：异步操作未取消导致状态错乱、内存泄漏
**历史案例**：`PlaceCard.tsx` fetch 未带 AbortController

**预防方案**：
```tsx
useEffect(() => {
  const ac = new AbortController();
  fetch(url, { signal: ac.signal })
    .then(r => r.ok ? r.json() : null)
    .then(data => { if (data) setDetail(data); })
    .catch(err => { if (err.name !== 'AbortError') console.error(err); })
    .finally(() => setDetailLoading(false));
  return () => ac.abort();  // 组件卸载时取消
}, [url]);
```

**执行时机**：所有 useEffect 中的异步操作

---

### 4.2 状态持久化版本化
**问题描述**：localStorage schema 变更导致反序列化失败

**预防方案**：
```ts
import { persist } from 'zustand/middleware';

const useStore = create(
  persist(
    (set, get) => ({ /* state */ }),
    {
      name: 'su-shi-user-data',
      version: 1,
      migrate: (persisted: any, version: number) => {
        if (version < 1) {
          // v0 → v1 迁移逻辑
        }
        return persisted;
      },
    }
  )
);
```

**执行时机**：状态持久化配置时

---

### 4.3 存储限额控制
**问题描述**：localStorage 无限增长撑爆（5MB限制）

**预防方案**：
```ts
const MAX_CHECKINS = 1000;
const MAX_NOTES = 500;
const MAX_FAVORITES = 200;

addCheckin: (checkin) => set(state => ({
  checkinPlaces: [...state.checkinPlaces, checkin].slice(-MAX_CHECKINS),
}))
```

**执行时机**：用户数据添加操作

---

## 五、工程化流程

### 5.1 测试覆盖要求
| 优先级 | 测试对象 | 重点 case | 框架 |
|--------|----------|-----------|------|
| P0 | 数据提取脚本 | 模糊匹配误伤、书目识别 | pytest |
| P0 | ID重映射脚本 | 双向唯一性、引用更新 | pytest |
| P1 | UI组件分支 | 不同类型的渲染逻辑 | vitest + RTL |
| P1 | 状态管理 | CRUD与持久化行为 | vitest |

---

### 5.2 CI/CD 守卫配置
```yaml
# .github/workflows/validate.yml
name: Validate
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install dependencies
        run: pip install pytest
      - name: Validate data consistency
        run: |
          python scripts/check-poem-consistency.py
          python scripts/verify-routes.py
      - name: Build Next.js
        run: pnpm build
```

---

### 5.3 代码规范配置
**Python** (`pyproject.toml`)：
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "B"]

[tool.mypy]
strict = true
```

**TypeScript** (`tsconfig.json`)：
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

---

## 六、检查清单

### 6.1 数据变更前检查
| ✅ | 脚本使用 `lib_data.py` | 统一路径和IO |
|---|------------------------|--------------|
| ✅ | 原子写入 | 使用 `atomic_write_json` |
| ✅ | 先备份 | 重要操作前执行 `backup_data()` |
| ✅ | 无 `public/data-v4/` 直写 | 通过symlink自动同步 |
| ✅ | 输出迁移日志 | 记录 mapping 便于回滚 |

### 6.2 前端开发前检查
| ✅ | 异步操作带 AbortController | 防止内存泄漏 |
| ✅ | 状态持久化版本化 | 支持schema迁移 |
| ✅ | 存储操作有限额 | 防止localStorage溢出 |
| ✅ | 渲染外部数据用 react-markdown | 防止XSS |

### 6.3 PR 提交前检查
| ✅ | CI 验证通过 | 数据一致性 + 构建 |
| ✅ | 代码规范检查 | ruff/mypy/tsc |
| ✅ | 测试覆盖 | 核心逻辑有测试 |
| ✅ | CHANGELOG 更新 | 记录变更内容 |

---

## 七、问题案例库

### 案例 1：诗词列表只显示68首
- **时间**：2026-06-02
- **原因**：`public/data-v4/poems/` 目录缺少文件
- **根因**：脚本忘记同步 public 目录
- **预防**：symlink 替代双写

### 案例 2：UI 文案过期
- **时间**：2026-06-03
- **原因**：`PlaceCard.tsx` 硬编码"68首"，数据已升级到321首
- **根因**：静态文案未动态化
- **预防**：使用动态数据或建立文案管理机制

### 案例 3：XSS 隐患
- **时间**：2026-06-03
- **原因**：`dangerouslySetInnerHTML` 直接渲染数据字段
- **根因**：未考虑未来外部数据源风险
- **预防**：使用 `react-markdown` + `rehype-sanitize`

---

## 📝 修订记录

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-06-03 | 初始版本，基于专家评审报告整理 | System |

---

## 🔗 相关文档

- [CHANGELOG.md](CHANGELOG.md) - 变更日志
- [data-v4/SCHEMA.md]() - 数据 Schema 文档（待创建）
- [CONTRIBUTING.md]() - 贡献指南（待创建）