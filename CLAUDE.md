# CLAUDE.md — Personal AI Engineering Skills 仓库总规则

本仓库是**个人 AI Engineering Skills** 的受版本管理副本，定位为可长期用 Git 管理的个人技能库。不绑定 NeonSAN，未来扩展分布式存储 / Ceph / 云原生存储 / AI Infrastructure / KV Cache / AI Storage 等方向。

## 仓库定位

- **Skills**：单一能力单元，每个 Skill 只做一件事。
- **Workflows**：组合多个 Skill 的端到端流水线，解决完整任务。
- **Templates**：输出结构骨架，保证产出物格式一致。
- **docs/**：仓库说明、Skill / Workflow 开发指南、使用说明。

## 核心原则（8 条）

1. **Skill 单一能力**：一个 Skill 只解决一类问题，不堆叠多职责。
2. **Workflow 组合能力**：复杂任务由 Workflow 编排多个 Skill，而非把逻辑塞进单个 Skill。
3. **Template 输出结构**：产出物结构由 Template 约束，Skill 负责方法与判断。
4. **通用能力不绑定项目**：通用 Skill（如 design-document）不依赖任何项目专属术语。
5. **项目专属能力归属项目仓库**：NeonSAN 专属技能（neonsan-docs / ci-test-case / writing-neonsan-internals）由 personal-notes 仓库维护，本仓库不复制，避免污染通用 Skill。
6. **优先基于事实和源码**：结论带出处（`file:line`、命令输出、文档链接），不凭记忆。
7. **不确定必须标注**：推测 / 推断 / 观点必须明确标注，不冒充事实。
8. **分布式存储优先一致性 / 并发 / 异常恢复**：Write / Discard / Snapshot / Clone / COW / Recovery 等生命周期必须主动检查。

## 修改原则

- **避免重复规则**：同一规则只在一处定义，其余引用。
- **避免无限膨胀**：不为"完整"机械增加章节 / 规则。
- **保持单一职责**：改动不破坏 Skill / Workflow / Template 的职责边界。
- **优先复用**：能复用既有 Skill / Template 就不新建。

## 目录结构

```text
skills/       Skill 定义（storage/、writing/、testing/、planning/ 分类）
workflows/    Workflow 流水线定义（编排散文，不会被自动发现）
commands/     Claude Code slash command 入口，每个 Workflow 一个同名文件
templates/    输出结构模板
shared/       通用规则唯一手维护源，生成到各 Skill 的 references/
scripts/      静态校验、注册表生成与安装同步辅助
docs/         仓库说明与开发指南；optimization/ 为审计交付物
```

## Markdown 文档标准

正文格式、章节结构路由、ASCII 图、元数据与静态检查以 `skills/writing/markdown-document-standard/` 为唯一权威源。文档结构只在 `templates/` 维护；技能不再复制章节清单。正式技术图默认 ASCII，Mermaid 仅作显式例外。

三项长期文档习惯（详细规则见权威源，其他地方只写指针）：

- **Plan 与最终技术文档分离**：Plan 记录范围、步骤、进度、验证与回滚；最终文档记录已验证的架构、机制、流程、并发、异常与取舍。最终文档从已验证实现沉淀，不复制 Plan 清单，不把未完成计划写成已实现。
- **ASCII 图 + 结构化正文**：重要架构图后按组件职责、交互流程、关键机制、异常与边界解释；控制请求、IO 数据、元数据与异步任务分开，图文双向一致。
- **统一格式、独立章节**：所有文档共享正文格式；设计文档、源码分析、RCA、技术原理、计划台账保留各自模板结构，不强行同构。

```bash
# 模板与示例检查（在仓库根执行）
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --profile new templates/*.md
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --strict docs/markdown-standard/examples/*.md
python3 skills/writing/markdown-document-standard/scripts/tests/test_doc_lint.py
```

静态检查不能验证技术结论、图语义或渲染效果；未运行或未人工审查时不得声称通过。

## 计划驱动执行

复杂、多步骤、跨文件任务使用 `skills/planning/plan-driven-development/` 与 `workflows/plan-driven-development/WORKFLOW.md`，显式入口是 `/plan-driven-development`。计划方法、评审门槛、执行授权、验证与恢复以该技能为唯一权威源；四个领域 Workflow 只写一行指针。

- 原生 Plan Mode 负责权限与计划确认；Plan Mode 内不写项目文件，也不创建 `docs/plans/`。
- 计划确认不等于执行授权；用户明确要求执行后才落盘并修改。
- 执行台账在 `docs/plans/YYYY-MM-DD-task-name.md`，结构见 `templates/plan-driven-development.md`，状态与恢复规则见 `docs/plans/README.md`。
- 完成后按已验证实现更新最终技术文档；只写已验证内容，保留长期决策与交叉引用，不复制台账清单。
- 领域内容仍由对应 Workflow / Skill 决定；本工作流不替代设计、源码分析、排障或写作。

## 静态校验

```bash
python3 scripts/skill_audit.py --check     # 结构、引用、重复、脱敏、生成模板/ shared-method 漂移
python3 scripts/skill_audit.py --write     # 重新生成注册表/清单/依赖、shared-method 与模板副本
python3 scripts/sync_skills.py             # 安装同步预览（默认 dry-run）
```

`docs/optimization/` 中的注册表、清单与依赖报告由脚本生成，不手改；其余审计报告为人工编写。通用规则改 `shared/references/method-and-evidence.md`，再 `--write` 生成副本，不要直接改 `references/shared-method.md`。

## 与 ~/.claude/skills/ 的关系

本仓库是**受版本管理的副本**。`~/.claude/skills/` 是 Claude Code 实际加载的生效目录。改动本仓库后，需**手动同步**到 `~/.claude/skills/` 对应目录才生效。详见 `docs/usage.md`。

NeonSAN 专属技能（neonsan-docs / ci-test-case / writing-neonsan-internals）不在本仓库，从 `personal-notes` 仓库的 `skills/` 同步到 `~/.claude/skills/`。
