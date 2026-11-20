# Markdown 文档标准接入技能库 实施计划

| 项 | 值 |
|---|---|
| 文档类型 | 实施计划 |
| 状态 | 计划中 |
| 适用版本 | 技能库当前基线 |
| 证据基线 | `Hansyangxingxiang@8b94123` |
| 计划范围 | 通用技能库的格式规范、模板与静态检查 |
| 最后核验 | 2026-11-20 |

> 示例说明：本示例取材于本次 Markdown 标准建设任务，用于演示实施计划的结构与粒度；它只描述计划，不代表工作已完成。实际执行结果以 `docs/markdown-standard/REPORT.md` 为准。

## 1. 任务背景

技能库已有 12 个技能和 9 个模板，但正文格式规则分散在根 `CLAUDE.md`、项目技能与各写作技能中，存在三类问题：

1. 图示默认策略冲突：有的技能默认 Mermaid，有的默认 ASCII。
2. 模板与技能章节清单互相复制，改一处需要改多处。
3. 缺少单 H1、标题跳级、围栏闭合、表格列数、链接目标、ASCII 宽度等静态检查。

后果是同一类文档在不同技能下产出格式不一致，评审需要反复指出同类问题。本次任务把格式规则收敛到单一权威源，并提供可执行的检查器。

## 2. 目标与范围

目标：

- 新增 `markdown-document-standard` 技能，作为格式、结构路由与检查的唯一权威源。
- 九个文档模板统一元数据、章节编号与 ASCII 图默认。
- `doc_lint.py` 覆盖 20 条静态规则，模板与示例零 error。
- 已有技能只保留方法与判断，章节清单改为模板指针。

非目标：

- 不批量重排已有文章、设计文档或分析报告。
- 不修改任何已确认的技术事实、实验数据或结论。
- 不实现 Mermaid 渲染、HTML 排版或微信客户端验证。
- 不向 `workbuddy-agents` 复制内容。

范围：`skills/writing/`、`templates/`、`workflows/`、`docs/` 与 `scripts/skill_audit.py`。项目仓库只增加 ASCII 图示覆盖层，不改通用技能。

## 3. 现状分析

- 格式规则现状：根 `CLAUDE.md` 只给原则，项目技能含项目级 Markdown 与 ASCII 规则，写作技能各自描述输出结构。
- 模板现状：设计文档 8 章、性能报告 10 章、Bug 分析 8 槽，但缺少源码分析、通用 RCA、技术原理与实施计划模板。
- 检查现状：`skill_audit.py` 校验技能结构与引用；`blog_lint.py` 校验博客样式；没有通用正文检查器。
- 约束：模板必须能随技能安装；不能引入第三方依赖；旧文档不能被新规则批量判失败。

已确认事实以上述文件当前内容为准；未验证项包括各技能在真实客户端中的触发率与产出质量。

## 4. 技术方案

采用四层结构：

1. Markdown 基础格式：标题、段落、表格、代码块、链接、元数据。
2. 技术内容组织：问题 → 架构 → 机制 → 流程 → 取舍 → 验证。
3. 文档类型模板：结构只在 `templates/` 维护。
4. 检查工具：`doc_lint.py` 做静态约束，人工审查负责技术正确性。

关键决策：

- 单一权威：格式规则只写在 `markdown-document-standard/references/`；技能用一行指针引用。
- ASCII 优先：控制/数据路径、时序、状态图默认 ASCII；仅显式要求时用 Mermaid。
- 模板归属：canonical 在仓库 `templates/`，技能内 `assets/templates/` 为生成副本，带生成头并由 `skill_audit.py --check` 校验漂移。
- RCA 不合并：通用 `incident-rca.md` 与项目 `bug-analysis.md` 的 8 槽归档并存，用映射表衔接。

备选方案：把所有规则写进每个 `SKILL.md`。该方案会造成多处漂移，且技能 token 成本高，不采用。

## 5. 影响文件与兼容性

| 文件/模块 | 变更类型 | 影响 | 验证方式 |
|---|---|---|---|
| `skills/writing/markdown-document-standard/` | 新增 | 格式权威源与检查器 | 单元测试、模板 lint |
| `templates/*.md` | 修改/新增 | 九类文档结构 | `doc_lint --profile new` |
| `design-document`、`storage-code-analysis`、`writing-project-principles`、`wechat-tech-article` | 修改 | 删除重复章节清单，改指针 | 人工比对章节职责未丢失 |
| 项目归档技能 | 修改（项目仓库） | 8 槽清单改指针，新增 ASCII 覆盖层 | 项目仓库 lint 与人工审查 |
| `scripts/skill_audit.py` | 修改 | 生成模板副本与漂移检查 | `--write` 后 `--check` |

兼容性：技能名与触发描述不变；模板章节语义保留，旧文档不被强制迁移；`doc_lint --profile legacy` 对旧文档降级 H1、跳级、表格列数与 ASCII 宽度规则。

## 6. 实施步骤

- [ ] 1. 记录基线 commit 与受保护未跟踪文件 — 完成条件：`git status --short` 与基线哈希已记录。
- [ ] 2. 新建标准技能与六个 references — 完成条件：frontmatter 合法，引用路径存在。
- [ ] 3. 新建/更新九个模板 — 完成条件：模板全部通过 `doc_lint --profile new`。
- [ ] 4. 实现 `doc_lint.py` 与 16 个单元测试 — 完成条件：测试全通过，覆盖全部 error 规则。
- [ ] 5. 编写三个示例与 README、REPORT — 完成条件：示例通过 `--strict`。
- [ ] 6. 修改通用技能、Workflow 与仓库文档 — 完成条件：重复章节清单已移除，指针可达。
- [ ] 7. 修改项目覆盖层 — 完成条件：项目技能仍可独立阅读，未复制通用规则全文。
- [ ] 8. 扩展 `skill_audit.py` 并生成副本 — 完成条件：`--write` 后 `--check` 为 0 error。

### 执行前

- [ ] 确认 Git 状态，无未提交的用户改动被覆盖。
- [ ] 记录基线 commit 与关键文件哈希。
- [ ] 确认 `doc_lint.py` 与测试可在 Python 3.9 运行。

### 执行中

- [ ] 只修改计划内路径，不顺手重排旧文档。
- [ ] 结构改动后运行 `doc_lint` 与 `skill_audit.py --check`。
- [ ] 记录实际偏差与新增风险。

### 执行后

- [ ] 运行验证计划全部可执行项。
- [ ] 汇总变更文件、通过项与未运行项。
- [ ] 按显式路径分别提交，不 push。

## 7. 依赖与执行顺序

- 前置依赖：Python 3.9+、Git、现有技能目录结构。
- 顺序约束：先建标准技能与模板，再实现检查器；先改权威源，再 `--write` 生成副本。
- 可并行：references 撰写与模板改写可并行；示例必须等检查器可用后再最终校验。
- 外部依赖：真实 Claude Code 客户端回归不可在静态阶段执行，标记为未运行。

## 8. 风险分析

| 风险 | 影响 | 概率 | 缓解 | 触发信号 |
|---|---|---|---|---|
| 生成副本漂移 | 技能内模板与 canonical 不一致 | 中 | 生成头 + `--check` 漂移校验 | `skill_audit.py --check` 报模板差异 |
| 删除章节清单导致能力丢失 | 技能少了判断依据 | 中 | 先把职责要点迁入模板，再删清单 | 人工比对模板与技能 |
| 旧文档 lint 失败 | 无法采用新规则 | 中 | `--profile legacy` 降级 | 旧文档出现 error |
| ASCII 宽度误报 | CJK 图被误判 | 低 | 按东亚宽度计算，可配置阈值 | 合法图报 MD014 |
| 示例被误当事实 | 读者引用虚构内容 | 中 | 每篇加示例说明，组件名带 Example | 评审抽查 |

高风险操作：删除技能章节清单与批量生成副本。前者先迁移职责要点；后者统一生成后再校验，均可通过 revert 回滚。

## 9. 验证计划

| 项 | 命令/方法 | 期望结果 | 状态 |
|---|---|---|---|
| 单元测试 | `python3 skills/writing/markdown-document-standard/scripts/tests/test_doc_lint.py` | 全通过 | 未运行 |
| 语法 | `python3 -m py_compile skill/scripts/doc_lint.py` | 0 error | 未运行 |
| 模板 | `doc_lint --profile new templates/*.md` | 0 error | 未运行 |
| 示例 | `doc_lint --strict docs/markdown-standard/examples/*.md` | 0 error，0 warning | 未运行 |
| 坏夹具 | 逐个运行 `bad/*.md` | 退出 1，命中预期规则 | 未运行 |
| 生成物 | `skill_audit.py --write` 后 `--check` | 0 error，无漂移 | 未运行 |
| 客户端回归 | R30–R32 | 技能路由正确 | 未运行，需真实客户端 |

静态通过不代表技术内容正确；示例与已有文档的技术结论仍需人工评审。

## 10. 回滚方案

- 回滚单位：按 commit 回滚，不手工修复生成物。
- 模板与技能修改：`git revert` 对应 commit；随后重新运行 `skill_audit.py --write`。
- 生成副本：删除技能内 `assets/templates/` 后 revert，再由权威模板重新生成。
- 数据与元数据：本次不改运行时代码或数据，无数据迁移回滚。
- 回滚后验证：`doc_lint --profile new`、`skill_audit.py --check`、示例 `--strict` 均需重新通过。

## 11. 执行记录与最终结果

### 执行记录

| 时间 | 步骤 | 结果 | 偏差/备注 |
|---|---|---|---|
| 2026-11-20 | 计划编写 | 完成 | 本示例只记录计划，无执行结果 |

### 最终结果

- 实际完成：无；本文件为结构示例。
- 验证结果：全部未运行。
- 与原计划差异：不适用。
- 剩余风险：见 §8；执行状态以 REPORT 为准。

## 附录

- 参考：`skills/writing/markdown-document-standard/SKILL.md`、`templates/implementation-plan.md`。
