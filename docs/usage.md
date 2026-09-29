# 使用指南

## 在 Claude Code 中使用这些 Skill

本仓库的 Skill 是**受版本管理的副本**。Claude Code 实际加载的是 `~/.claude/skills/` 下的目录。

### 生效目录

- 生效目录：`~/.claude/skills/`
- 本仓库：`skills/`（受版本管理）

### 同步说明

改动本仓库后，需**手动同步**到 `~/.claude/skills/` 对应目录才生效。例如：

```bash
# 同步 design-document
cp -r skills/storage/design-document ~/.claude/skills/design-document

# 同步 neonsan-docs（注意：生效目录名与仓库内目录名一致）
cp -r skills/storage/neonsan-docs ~/.claude/skills/neonsan-docs
```

> 注意：`~/.claude/skills/` 中既有目录名（如 `writing-neonsan-design-docs`）与本仓库内目录名（`neonsan-docs`）可能不同。同步时以生效目录为准，或统一改名后同步。

### 触发方式

Skill 通过 description 自动触发。也可在对话中直接描述任务，Claude Code 会匹配对应 Skill。

## 按任务选择 Workflow

| 任务 | 用哪个 Workflow |
|---|---|
| 设计一个存储功能 | `storage-feature-design` |
| 排查一个存储 bug | `storage-bug-analysis` |
| 分析一个性能问题 | `storage-performance-analysis` |
| 写一篇技术文章 | `technical-writing` |

## 使用示例

以「设计分布式块存储 Trim/Discard 功能」为例：

1. 用 `storage-code-analysis` 分析现有 Discard 处理路径（源码事实）。
2. 用 `design-document` 产出 8 章节设计文档（含并发 / 一致性 / 兼容 / 测试）。
3. 用 `neonsan-docs` 按 NeonSAN 规范归档落盘。
4. 或直接走 `storage-feature-design` Workflow 端到端完成。
