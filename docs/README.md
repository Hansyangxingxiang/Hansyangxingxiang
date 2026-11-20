# Personal AI Engineering Skills

个人 AI Engineering Skills 仓库：一套可长期用 Git 管理的 Claude Code Skills / Workflows / Templates，用于存储研发与技术写作。不绑定 NeonSAN，未来扩展分布式存储 / Ceph / 云原生存储 / AI Infrastructure / KV Cache / AI Storage 等方向。

## 项目简介

本仓库把分散在 `~/.claude/skills/` 的 10 个通用 Skill 整理为受版本管理的副本，并补充 Workflow（组合流水线）、Command（原生入口）与 Template（输出结构），形成「Skills → Workflows → Templates → Claude Code 研发助手」的完整体系。NeonSAN 专属技能由 `personal-notes` 仓库维护。

## 目录结构

```
.
├── README.md                 个人主页（保留，不动）
├── CLAUDE.md                 仓库总规则
├── LICENSE                   MIT
├── .gitignore
├── skills/                   Skill 定义
│   ├── storage/              存储研发类
│   ├── writing/              技术写作类
│   └── testing/              测试设计类
├── workflows/                端到端流水线（编排散文）
├── commands/                 Claude Code slash command 入口
├── templates/                输出结构模板
├── shared/references/        通用规则唯一源（生成到各 Skill）
├── scripts/                  静态校验、注册表生成与同步辅助
└── docs/                     仓库说明与开发指南（optimization/ 为审计交付物）
```

## Skill 分类

### storage/（存储研发）

| Skill | 职责 |
|---|---|
| `storage-code-analysis` | 深入读 Ceph/存储源码，区分"源码事实"与"推测" |
| `storage-debug` | 存储/IO 问题排障，从现象反推根因 |
| `design-document` | 通用研发技术设计文档（轻量 / 完整模式，不依赖 NeonSAN） |
| `storage-concurrency-analysis` | 存储并发、竞态与一致性分析（14 类场景、11 维框架） |

### writing/（技术写作）

| Skill | 职责 |
|---|---|
| `writing-project-principles` | 项目原理写作 / 系列规划 / 技术评审与一致性检查 |
| `wechat-tech-article` | 公众号选题 / 标题 / 读者表达 |
| `producing-tech-blog` | 排版成微信 HTML（`.md` + 内联 CSS）；可选 md2wx / blog_lint 脚本 |
| `humanizer-zh` | 去除文本 AI 生成痕迹；可选 check_style 脚本 |
| `markdown-document-standard` | Markdown 格式 / 章节结构路由 / ASCII 图 / 文档类型模板 / `doc_lint.py` 静态检查 |

### testing/（测试设计）

| Skill | 职责 |
|---|---|
| `test-case-design` | 通用测试用例设计：逐步操作/预期/验证、覆盖映射、有界等待、验收映射；不绑定项目 |

### NeonSAN 专属技能（personal-notes 仓库）

以下技能绑定 NeonSAN 项目，由 `personal-notes` 仓库的 `skills/` 维护，本仓库不复制：

| Skill | 职责 |
|---|---|
| `neonsan-docs` | NeonSAN 文档规范与归档（原 writing-neonsan-design-docs） |
| `ci-test-case` | NeonSAN CI 项目补充层：ci/ 框架导航、CI-1/CI-2/M 分类；通用方法由 `test-case-design` 负责 |
| `writing-neonsan-internals` | NeonSAN 技术原理系列写作 |

## Workflow 分类

| Workflow | 用途 | 组合的 Skill |
|---|---|---|
| `storage-feature-design` | 功能设计端到端 | storage-code-analysis + storage-concurrency-analysis + design-document +（NeonSAN 归档）neonsan-docs |
| `storage-bug-analysis` | 故障排障端到端 | storage-debug（主入口）+ 条件分支 storage-concurrency-analysis + storage-code-analysis + design-document |
| `storage-performance-analysis` | 性能分析端到端 | storage-debug + storage-code-analysis + design-document |
| `technical-writing` | 技术写作端到端 | 按任务选择 writing-project-principles / wechat-tech-article / writing-neonsan-internals；润色与 HTML 按需 |

`WORKFLOW.md` 只是编排说明，Claude Code 不会自动发现。实际入口是 `commands/` 下同名 slash command；同步到 `~/.claude/{commands,workflows}/` 后可用。

## Template 分类

| Template | 对应产出物 |
|---|---|
| `design-document.md` | 设计文档（13 个候选章节 → 默认 8 章 + 轻量模式） |
| `source-analysis.md` | 源码分析（完整 11 章 / 卡片模式） |
| `incident-rca.md` | 通用故障 RCA（11 章） |
| `bug-analysis.md` | 项目 Bug/事故分析归档（8 槽 + RCA 映射） |
| `performance-analysis.md` | 性能分析报告（10 章） |
| `technical-principles.md` | 技术原理文章（10 章 / compact-5） |
| `technical-article.md` | 技术文章（10 节候选 + 微信叠加说明） |
| `implementation-plan.md` | 实施计划（11 章 + 执行前/中/后清单） |
| `test-case-design.md` | 测试用例设计（项目中性骨架，配合 `test-case-design`） |

模板 canonical 在 `templates/`；`markdown-document-standard/assets/templates/` 是供安装后自包含的生成副本，带 `Generated` 头，不手工编辑。文档格式、ASCII 图与检查规则以该技能为唯一权威源。

## 如何使用

1. 阅读 `docs/usage.md` 了解在 Claude Code 中的使用方式。
2. 按任务类型选择对应 Workflow（见上表），或直接调用 `commands/<name>.md` 对应的 slash command。
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
