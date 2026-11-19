# 迁移映射

本次不删除、不移动、不重命名任何技能目录；迁移以"新增文件 + 内容收敛 + 引用改线"实现。基线：`Hansyangxingxiang@02dd60b`、`personal-notes@a2b7834`、`workbuddy-agents@05356b5`（只读）。

## 技能与职责映射

| 原位置 / 原职责 | 新位置 / 新职责 | 迁移方式 |
|---|---|---|
| `ci-test-case` 通用测试方法（约九成内容） | `Hansyangxingxiang/skills/testing/test-case-design/` | 新增通用技能；原技能按技能名委托 |
| `ci-test-case` 的 `ci/` 导航、CI-1/CI-2/M | 保留在 `personal-notes/skills/ci-test-case/` | 收敛为项目补充层，`references/ci-navigation.md` 不动 |
| `templates/test-case-design.md`（含 NeonSAN 词） | 同路径，项目中性骨架 | 重写模板，去掉 `ci/`、CI 分类、专有接口与占位符 |
| `humanizer-zh/SKILL.md` 24 模式目录 | `humanizer-zh/references/patterns-catalog.md` | 内容移入 references，SKILL 保留规则与指针 |
| 各 SKILL 内重复的通用证据规则 | `shared/references/method-and-evidence.md` | 单源手维护，生成 10 份 `references/shared-method.md` |
| `storage-feature-design` 并发段映射给 `design-document` | `storage-concurrency-analysis` + `design-document` 分工 | 修改 WORKFLOW 映射与流水线顺序 |
| `storage-bug-analysis` 无并发分支 | 保留 `storage-debug` 主入口，增加条件分支 | 修改 WORKFLOW 映射 |
| `workflows/*`（仅文档） | `commands/*.md` 作为入口 | 新增 4 个同名 command，不复制 workflow 正文 |

## 文件级清单

### Hansyangxingxiang 新增

| 路径 | 用途 |
|---|---|
| `shared/references/method-and-evidence.md` | 通用规则唯一源 |
| `scripts/skill_audit.py`, `scripts/skill_audit.config.json` | 静态校验与注册表生成 |
| `scripts/sync_skills.py` | 安装同步辅助（默认 dry-run） |
| `skills/testing/test-case-design/{SKILL.md,references/*}` | 通用测试用例设计 |
| `commands/{storage-feature-design,storage-bug-analysis,storage-performance-analysis,technical-writing}.md` | slash command 入口 |
| `docs/skill-conventions.md` | 统一规范 |
| `docs/optimization/*` | 本目录交付物 |
| 10 × `skills/*/*/references/shared-method.md` | 生成副本 |

### Hansyangxingxiang 修改

| 路径 | 变更 |
|---|---|
| 8 个既有 `SKILL.md` | 删除重复通用句，改为 `references/shared-method.md` 指针；`humanizer-zh` 拆分 |
| `workflows/storage-feature-design/WORKFLOW.md` | 并发节点前置并改映射 |
| `workflows/storage-bug-analysis/WORKFLOW.md` | 增加并发条件分支 |
| `workflows/technical-writing/WORKFLOW.md` | 补 `## 适用场景`、内部写作技能入口 |
| `templates/test-case-design.md` | 项目中性化 |
| `CLAUDE.md` | 补目录、校验命令、生成/人工边界 |
| `docs/README.md` | 9 技能、testing 分类、模板与 workflow 组合、command 说明 |
| `docs/usage.md` | 同步脚本、command/workflow 同步与调用 |
| `docs/workflow-development.md` | 每个 Workflow 必须配 command |
| `docs/skill-regression.md` | 增加 R22–R29 |

### personal-notes 新增 / 修改

| 路径 | 变更 |
|---|---|
| `CLAUDE.md` | 新增：仓库角色、技能归属、同步、证据、发布边界、Git 规则 |
| `README.md` | 通用技能列表补 `storage-concurrency-analysis`、`test-case-design`；同步说明 |
| `skills/ci-test-case/SKILL.md` | 241 → 72 行，项目补充层 |
| `skills/ci-test-case/references/scenario-checklist.md` | 收敛为项目补充项 |
| `skills/ci-test-case/references/case-template.md` | 注明项目副本，CI 分类 |
| `skills/ci-test-case/references/shared-method.md` | 生成副本 |
| `skills/writing-neonsan-internals/SKILL.md` | 新增发布边界 |

### 未改动

- `personal-notes/skills/ci-test-case/references/ci-navigation.md`：保持原样。
- `personal-notes/skills/neonsan-docs/`：保持原样。
- `personal-notes/work/neonsan/analysis/2026-11-19-csi-neonsan-clone.md`：未跟踪用户文件，未 stage、未修改。
- `workbuddy-agents/` 全部文件：只读审计，未改。
- `~/.claude/`：未同步。

## 提交与回滚

- 所有改动位于两仓库的 `chore/skill-library-audit` 分支，分别提交，只显式 add 具体路径。
- 建议提交顺序（Hans）：① 脚本与 shared 单源；② 技能收敛与新增测试技能；③ commands 与 workflow 改线；④ docs/模板/回归；⑤ 优化报告。
- 建议提交顺序（personal）：① CLAUDE.md 与 README；② `ci-test-case` 与模板收敛；③ 发布边界。
- 回滚：对目标提交执行 `git revert <commit>`；或切回原分支。不使用 `git reset --hard` 或强制清理。
- 生成物不手工修复：回滚后运行 `python3 scripts/skill_audit.py --write` 重新生成。
