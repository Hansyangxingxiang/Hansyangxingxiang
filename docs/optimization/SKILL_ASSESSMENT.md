# Skill 质量评估

评估对象为 `Hansyangxingxiang` 的 9 个通用技能与 `personal-notes` 的 3 个项目技能。分数为 0–10，加权总分按下列 8 维权重计算。"改前"指出厂基线 `Hansyangxingxiang@02dd60b` / `personal-notes@a2b7834`，"改后"指本次 `chore/skill-library-audit` 工作树。

## 评估维度与权重

| 维度 | 权重 | 判定要点 |
|---|---:|---|
| 结构与命名 | 15% | 目录名 = frontmatter `name`，kebab-case，单一 SKILL.md，references 布局 |
| 触发描述 | 15% | description 写清何时用 / 何时不用，边界可区分 |
| 职责边界 | 15% | 技能单一职责；通用方法不绑定项目；Workflow 只编排 |
| 证据规范 | 15% | 事实可追溯，区分推断，不编造；规则只有一处定义 |
| 复用与去重 | 10% | 通用规则集中，项目差异隔离，无复制漂移 |
| 上下文体量 | 10% | SKILL.md 按需加载，超长目录移入 references |
| 文档与验证 | 10% | 注册表/清单可生成，静态校验可重复，Workflow 可调用 |
| 安全与发布边界 | 10% | 敏感信息有审计，内部资产有发布边界 |

## 维度证据（改后）

| 维度 | 证据 | 结论 |
|---|---|---|
| 结构与命名 | 12 个技能均通过 `scripts/skill_audit.py --check`；目录名与 `name` 一致；新增 `skills/testing/test-case-design/` | 9.0 |
| 触发描述 | 12 个技能的 description 均含 Not for / 不用于 / 不负责类边界（逐文件 grep 通过）；`test-case-design` 明确与 `ci-test-case` 分工 | 9.0 |
| 职责边界 | `ci-test-case/SKILL.md:13-21` 收敛为项目补充层；`storage-feature-design/WORKFLOW.md:35` 并发结论输入方案而非替代；`storage-bug-analysis/WORKFLOW.md:33-37` 为条件分支 | 8.5 |
| 证据规范 | `shared/references/method-and-evidence.md` 统一四级证据与 `file:line` 规则；10 个技能副本 SHA-256 一致；各 SKILL 只保留特有输入与指针 | 9.0 |
| 复用与去重 | 通用规则单源 + 生成副本；`humanizer-zh` 24 模式移入 `references/patterns-catalog.md`；`storage-concurrency-analysis/SKILL.md:79-81` 11 问改为索引 + 指向 `references/framework.md` | 8.0 |
| 上下文体量 | `humanizer-zh/SKILL.md` 491 → 140 行，模式目录按需加载；全库 SKILL.md 从 8 个 1018 行变为 9 个 1130 行（新增技能 174 行） | 8.5 |
| 文档与验证 | `docs/optimization/` 注册表/清单/依赖由脚本生成；`skill_audit.py --check` 0 error；4 个 `commands/*.md` 对应 4 个 Workflow；`docs/skill-regression.md` R22–R29 | 9.0 |
| 安全与发布边界 | 审计脚本对私网 IP、内部域名、路径、密钥与项目标识做 block/warn；`templates/test-case-design.md` 已去项目专有词；`writing-neonsan-internals/SKILL.md:64` 增加发布边界 | 8.5 |

## 加权结果

| 维度 | 改前 | 改后 |
|---|---:|---:|
| 结构与命名 | 8.5 | 9.0 |
| 触发描述 | 8.5 | 9.0 |
| 职责边界 | 6.5 | 8.5 |
| 证据规范 | 7.5 | 9.0 |
| 复用与去重 | 5.0 | 8.0 |
| 上下文体量 | 5.5 | 8.5 |
| 文档与验证 | 5.0 | 9.0 |
| 安全与发布边界 | 6.5 | 8.5 |
| **加权总分** | **6.8** | **8.8** |

改前主要失分：通用规则多份复制、humanizer 超长、Workflow 不可调用、并发技能未接线、通用测试与 NeonSAN 耦合、无注册表/静态校验。

## 逐技能评分（改后）

| 技能 | 仓库 | 结构与命名 | 触发 | 职责 | 证据 | 复用 | 体量 | 文档验证 | 安全 | 加权 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `design-document` | Hans | 9 | 9 | 9 | 9 | 8 | 9 | 9 | 8 | 8.8 |
| `storage-code-analysis` | Hans | 9 | 9 | 9 | 9 | 8 | 9 | 9 | 8 | 8.8 |
| `storage-concurrency-analysis` | Hans | 9 | 9 | 9 | 9 | 8 | 8 | 9 | 8 | 8.7 |
| `storage-debug` | Hans | 9 | 9 | 9 | 9 | 8 | 9 | 9 | 8 | 8.8 |
| `test-case-design` | Hans | 9 | 9 | 9 | 8 | 9 | 9 | 9 | 8 | 8.8 |
| `humanizer-zh` | Hans | 9 | 9 | 8 | 9 | 9 | 10 | 9 | 9 | 9.0 |
| `producing-tech-blog` | Hans | 9 | 9 | 9 | 9 | 8 | 9 | 8 | 9 | 8.8 |
| `wechat-tech-article` | Hans | 9 | 9 | 9 | 8 | 8 | 9 | 9 | 8 | 8.7 |
| `writing-project-principles` | Hans | 9 | 9 | 8 | 9 | 8 | 9 | 9 | 8 | 8.7 |
| `ci-test-case` | personal | 9 | 8 | 9 | 9 | 9 | 10 | 8 | 8 | 8.9 |
| `neonsan-docs` | personal | 9 | 8 | 9 | 8 | 7 | 9 | 7 | 8 | 8.4 |
| `writing-neonsan-internals` | personal | 9 | 8 | 9 | 8 | 7 | 9 | 7 | 9 | 8.3 |

## 主要薄弱项（改后仍在）

- `neonsan-docs` 未接入统一证据指针，仍自带一套证据表述；本次不重写其正文，留作后续小步改造。
- `producing-tech-blog` 的三个脚本在 Hans 与 workbuddy 存在分叉副本，本次只验证 Hans 版本，未统一。
- Workflow 的客户端触发与产出质量未运行，文档验证得分只覆盖静态可测部分。
