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
rsync -a -c --delete-delay --omit-dir-times skills/storage/design-document/ ~/.claude/skills/design-document/
```

### NeonSAN 专属技能

`neonsan-docs`、`ci-test-case`、`writing-neonsan-internals` 绑定 NeonSAN 项目，**不在本仓库**，由 `personal-notes` 仓库的 `skills/` 维护。这些技能同样需要同步到 `~/.claude/skills/`：

```bash
# 在 personal-notes 仓库根目录执行
for n in neonsan-docs ci-test-case writing-neonsan-internals; do
  rsync -a -c --delete-delay --omit-dir-times "skills/$n/" "$HOME/.claude/skills/$n/"
done
```

目录名与 `SKILL.md` frontmatter 的 `name` 一致，运行时技能名不变。

### 触发方式

Skill 通过 description 自动触发。也可在对话中直接描述任务，Claude Code 会匹配对应 Skill。

## 按任务选择 Workflow

| 任务 | 用哪个 Workflow |
|---|---|
| 设计一个存储功能 | `storage-feature-design` |
| 排查一个存储 bug | `storage-bug-analysis` |
| 分析一个性能问题 | `storage-performance-analysis` |
| 写一篇技术文章 | `technical-writing` |

## 写作任务入口

- 项目原理、源码证据、系列规划、技术评审或系列一致性：`writing-project-principles`。
- 公众号选题、标题或已有正文的读者表达调整：`wechat-tech-article`。
- 只润色已有文本：`humanizer-zh`；只生成微信 HTML：`producing-tech-blog`。
- 公众号原理文章先完成机制论证，再按需处理表达和排版；博客或系列规划不自动生成 HTML。

## 使用示例

以「设计分布式块存储 Trim/Discard 功能」为例：

1. 用 `storage-code-analysis` 分析现有 Discard 处理路径（源码事实）。
2. 用 `design-document` 产出 8 章节设计文档（含并发 / 一致性 / 兼容 / 测试）。
3. 用 `neonsan-docs`（personal-notes 仓库维护）按 NeonSAN 规范归档落盘。
4. 或直接走 `storage-feature-design` Workflow 端到端完成。
