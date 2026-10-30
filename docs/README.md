# Personal AI Engineering Skills

个人 AI Engineering Skills 仓库：一套可长期用 Git 管理的 Claude Code Skills / Workflows / Templates，用于存储研发与技术写作。不绑定 NeonSAN，未来扩展分布式存储 / Ceph / 云原生存储 / AI Infrastructure / KV Cache / AI Storage 等方向。

## 项目简介

本仓库把分散在 `~/.claude/skills/` 的 8 个 Skill 整理为受版本管理的副本，并补充 Workflow（组合流水线）与 Template（输出结构），形成「Skills → Workflows → Templates → Claude Code 研发助手」的完整体系。

## 目录结构

```
.
├── README.md                 个人主页（保留，不动）
├── CLAUDE.md                 仓库总规则
├── LICENSE                   MIT
├── .gitignore
├── skills/                   Skill 定义
│   ├── storage/              存储研发类
│   └── writing/              技术写作类
├── workflows/                端到端流水线
├── templates/                输出结构模板
└── docs/                     仓库说明与开发指南
```

## Skill 分类

### storage/（存储研发）

| Skill | 职责 |
|---|---|
| `ci-test-case` | 基于 NeonSAN CI 框架产出可评审的测试用例设计 |
| `storage-code-analysis` | 深入读 Ceph/存储源码，区分"源码事实"与"推测" |
| `storage-debug` | 存储/IO 问题排障，从现象反推根因 |
| `design-document` | 通用研发技术设计文档（默认 8 章节，不依赖 NeonSAN） |
| `neonsan-docs` | NeonSAN 文档规范与归档（原 writing-neonsan-design-docs） |

### writing/（技术写作）

| Skill | 职责 |
|---|---|
| `wechat-tech-article` | 公众号技术文章选题 / 结构 / 草稿 |
| `producing-tech-blog` | 排版成微信 HTML（`.md` + 内联 CSS） |
| `humanizer-zh` | 去除文本 AI 生成痕迹 |

## Workflow 分类

| Workflow | 用途 | 组合的 Skill |
|---|---|---|
| `storage-feature-design` | 功能设计端到端 | storage-code-analysis + design-document + neonsan-docs |
| `storage-bug-analysis` | 故障排障端到端 | storage-debug + storage-code-analysis + design-document |
| `storage-performance-analysis` | 性能分析端到端 | storage-debug + storage-code-analysis + design-document |
| `technical-writing` | 技术写作端到端 | wechat-tech-article + humanizer-zh + producing-tech-blog |

## Template 分类

| Template | 对应产出物 |
|---|---|
| `design-document.md` | 设计文档（8 章节骨架） |
| `bug-analysis.md` | Bug/事故分析归档（8 槽） |
| `performance-analysis.md` | 性能分析报告 |
| `technical-article.md` | 技术文章（10 节结构） |

## 如何使用

1. 阅读 `docs/usage.md` 了解在 Claude Code 中的使用方式。
2. 按任务类型选择对应 Workflow（见上表）。
3. 用对应 Template 约束产出物结构。

## 如何新增 Skill / Workflow / Template

- 新增 Skill：见 `docs/skill-development.md`
- 新增 Workflow：见 `docs/workflow-development.md`
- 新增 Template：参照 `templates/` 既有结构，保持单一职责

## Git 管理

- 本仓库是受版本管理的副本，`~/.claude/skills/` 原样保留。
- 改动后需手动同步到 `~/.claude/skills/` 才生效（见 `docs/usage.md`）。
- 提交遵循仓库既有 commit 风格。

## 版本管理

- 用 Git 历史管理 Skill / Workflow / Template 的演进。
- 每个 Skill 的 frontmatter `name` 是唯一标识，改名需同步更新引用。

## 架构图

```
Skills（单一能力）
   │  组合
   ▼
Workflows（端到端流水线）
   │  约束
   ▼
Templates（输出结构）
   │
   ▼
Claude Code 研发助手
```
