# 优化计划

## 1. 目标与原则

目标：在不删除既有能力、不虚构能力的前提下，降低重复维护成本，明确每个 Skill 的职责与触发条件，恢复通用/项目边界，让 Workflow 可调用，并建立可重复的静态校验与注册表。

原则：

- 稳定性优先：不改已确认结论、不批量改写证据标签、不动已验证脚本行为。
- 单一权威：同一规则只在一处手维护，其余为生成副本或指针。
- 能力不丢失：超长内容移入 `references/`，不删除知识。
- 变更可回滚：逐仓库、逐提交，可用 `git revert` 恢复。
- 静态可测优先：能脚本判定的不靠人工记忆；客户端行为单独标注。

## 2. 现状问题

- 无注册表，`docs/README.md` 手工表已漏项。
- `workflows/*/WORKFLOW.md` 不会被 Claude Code 发现，`docs/usage.md` 却暗示可直接走 Workflow。
- 通用证据规则在约 8 个 Skill 中重复；并发 11 问在 SKILL 与 reference 重复。
- `storage-concurrency-analysis` 未被任何 Workflow 引用，`storage-feature-design` 把并发阶段错误映射给 `design-document`。
- `ci-test-case` 约九成是通用测试方法，Hans 的 `templates/test-case-design.md` 反向泄漏 NeonSAN 专有词。
- `humanizer-zh` 491 行，24 模式占约三分之二，每次触发全量加载。
- 写作技能重复同一套方法；跨仓库 `storage-debug`、博客脚本存在有意/无意分叉。
- 无静态校验，无法发现悬空引用、重名、描述缺失或生成物漂移。

## 3. 目标架构

```
Hansyangxingxiang/                 personal-notes/
├── skills/{storage,writing,testing}/   ├── skills/{neonsan-docs,ci-test-case,
├── shared/references/  ← 唯一源        │            writing-neonsan-internals}
├── workflows/          ← 编排散文      ├── CLAUDE.md
├── commands/           ← slash 入口    └── README.md
├── templates/
├── scripts/  audit + sync
└── docs/optimization/  ← 审计交付物
```

- 通用规则：`shared/references/method-and-evidence.md` 手维护，`skill_audit.py --write` 生成 10 份 `references/shared-method.md`。
- 项目技能：只保留项目输入、框架导航、分类与检查项，通用方法按技能名委托。
- Workflow：保留编排说明；`commands/<name>.md` 作为真实入口。
- 注册表：由文件系统与 frontmatter 生成，不手改。

## 4. 分阶段计划

| 阶段 | 风险 | 内容 |
|---|---|---|
| A0 | 低 | 记录三仓库基线，创建 `chore/skill-library-audit` 分支，保护未跟踪文件 |
| A1 | 低 | 新增 `skill_audit.py` + 配置：结构、描述、引用、重名、生成物、脱敏、体量 |
| A2 | 低 | 生成清单/依赖/注册表，人工编写评估、计划、迁移、回归、总结 |
| A3 | 低 | 新增 `docs/skill-conventions.md` 并回链 |
| A4 | 低 | 建立 shared 单源，生成 10 份副本，收敛各 SKILL 通用句 |
| A5 | 低 | 修正 Hans/personal 文档、手维护表，新增 `personal-notes/CLAUDE.md` |
| A6 | 低 | 回归集增加 R22–R29，区分静态与客户端 |
| A7 | 低 | 内部写作技能增加发布边界，不删内容 |
| A8 | 低 | 新增 `sync_skills.py`，默认 dry-run、删除需显式开关 |
| B1 | 中 | humanizer-zh 24 模式移入 references，SKILL 压到 140 行 |
| B2 | 中 | 新增通用 `test-case-design`，`ci-test-case` 收敛为项目补充层，清理模板专有词 |
| B3 | 中 | 新增 4 个 `commands/*.md`，更新 usage 与 workflow 开发规范 |
| B4 | 中 | 并发分析接回 feature-design 与 bug-analysis 条件分支；写作流程补内部技能 |

## 5. 具体任务与产出

| 任务 | 产出 | 状态 |
|---|---|---|
| 校验器与配置 | `scripts/skill_audit.py`, `scripts/skill_audit.config.json` | 完成 |
| 注册表生成 | `docs/optimization/{SKILL_INVENTORY,SKILL_DEPENDENCIES,SKILL_REGISTRY}.md`, `skill_registry.json` | 完成 |
| 统一规范 | `docs/skill-conventions.md` | 完成 |
| 通用规则单源 | `shared/references/method-and-evidence.md` + 10 份副本 | 完成 |
| 通用测试设计 | `skills/testing/test-case-design/`（SKILL + 3 references） | 完成 |
| 项目测试补充层 | `personal-notes/skills/ci-test-case/` 重写与两张 references 收敛 | 完成 |
| Workflow 入口 | `commands/{4 个}.md` | 完成 |
| 并发接线 | `workflows/storage-feature-design/WORKFLOW.md`, `storage-bug-analysis/WORKFLOW.md` | 完成 |
| 同步辅助 | `scripts/sync_skills.py` | 完成 |
| 文档修正 | Hans `CLAUDE.md`, `docs/{README,usage,workflow-development,skill-regression}.md`; personal `CLAUDE.md`, `README.md` | 完成 |
| 发布边界 | `writing-neonsan-internals/SKILL.md` | 完成 |

## 6. 职责边界调整

- 通用测试方法 → `test-case-design`；NeonSAN 的 `ci/` 导航与 CI 分类 → `ci-test-case`，按技能名委托，不写跨仓库文件路径。
- 并发/一致性 → `storage-concurrency-analysis`；方案、异常、兼容、测试设计 → `design-document`。
- 排障主入口仍是 `storage-debug`；只有数据不一致、数据复活或疑似竞态才进入并发分支。
- 原理写作 → `writing-project-principles`；NeonSAN 内部规范 → `writing-neonsan-internals`；公众号表达与排版不前置。
- 项目技能不得复制通用技能；内部 references 不进入发布仓库。

## 7. 依赖与实施顺序

1. 先固定基线、分支与未跟踪文件保护。
2. 先建校验器与配置，再用它检查后续改动。
3. 通用规则单源必须先于各 SKILL 收敛，避免中间态引用断链。
4. `test-case-design` 必须先于 `ci-test-case` 重写。
5. `commands/` 必须先于 `docs/usage.md` 的调用说明。
6. 每次结构调整后运行 `--write`，再用 `--check` 确认确定性。
7. 最后按仓库分别提交，不跨仓库混合提交。

## 8. 验收标准

- `python3 scripts/skill_audit.py --check` 退出码 0、0 error。
- 新增脚本 `py_compile` 通过。
- 10 份 `shared-method.md` 与单源 SHA-256 一致。
- `humanizer-zh` 模式 24 个、SKILL ≤180 行。
- 4 个 command 均有同名 Workflow，引用技能名可解析。
- Hans 通用技能与 `templates/test-case-design.md` 无项目专有词（按技能名路由的提及除外）。
- `personal-notes` 未跟踪 CSI 分析文件仍在且未被 stage。
- 客户端触发、组合回归与微信预览未运行时标为未运行。

## 9. 风险与回滚

| 风险 | 缓解 | 回滚 |
|---|---|---|
| 引用断链 | 校验器覆盖路径与技能名；改后 `--check` | `git revert` 对应提交 |
| 通用/项目边界再次混淆 | 技能名委托；发布边界说明；脱敏审计 | 恢复 `ci-test-case` 原文件 |
| 生成物漂移 | 单源 + SHA-256；不手改副本 | 回滚后重新 `--write` |
| 误删用户内容 | 不 `git add -A`；不动未跟踪文件；`--delete` 显式 | 从 Git 恢复 |
| Workflow 仍不可调用 | command 入口 + 同步说明 | 删除 commands 并 revert 文档 |

## 10. 未纳入本次范围

- 不改根目录 `CLAUDE.md`（三仓库事实仍待更新）。
- 不改 `workbuddy-agents` 的技能、计数、marketplace 或脚本分叉。
- 不新增 Hans 性能分析 Skill；性能方法仍由 `storage-debug` / `design-document` 承担。
- 不统一既有证据标签用词，只做映射说明。
- 不同步 `~/.claude/`，不 push，不建 PR。
- 未运行客户端触发、组合回归与微信客户端预览。
