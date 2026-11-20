# Markdown 文档标准实施报告

| 项 | 值 |
|---|---|
| 文档类型 | 实施报告 |
| 状态 | 静态实施完成，客户端回归未运行 |
| 适用版本 | `Hansyangxingxiang@8b94123` 之后的工作树 |
| 证据基线 | 本轮命令输出与仓库文件实读；未运行项单列 |
| 最后核验 | 2026-11-20 |

## 结论

标准技能、9 个模板、20 条静态规则、16 个单元测试和 3 个完整示例已落地；模板与示例静态检查为 0 error，`skill_audit.py --check` 为 0 error。真实 Claude Code 客户端的触发与产出质量回归（R30–R32）尚未运行，不能声称客户端行为已验证。

## 改造前后

| 问题 | 改造前 | 改造后 |
|---|---|---|
| 格式规则位置 | 分散在根 `CLAUDE.md`、项目技能与各写作技能，互相重复 | `markdown-document-standard/references/` 单一权威；其他技能写一行指针 |
| 图示默认 | `writing-project-principles` / `writing-neonsan-internals` 默认 Mermaid，`design-document` / `neonsan-docs` 默认 ASCII | 全部改为 ASCII 优先；Mermaid 仅显式要求或平台需要 |
| 章节结构 | 技能内复制 8 章 / 8 槽 / 十项清单，改一处要改多处 | 结构只在 `templates/`；技能保留方法与判断 |
| 模板数量 | 5 个（设计、Bug、性能、文章、测试用例） | 9 个（新增源码分析、通用 RCA、技术原理、实施计划） |
| 文档类型边界 | 通用 RCA 与项目 8 槽归档混用，无映射 | `incident-rca.md` 与 `bug-analysis.md` 并存，模板内给 8 槽 → RCA 映射 |
| 静态检查 | 只有技能结构审计与博客样式检查 | `doc_lint.py` 覆盖标题、围栏、表格、链接、ASCII、元数据，共 20 条 |
| 示例 | 无完整样例 | 架构设计、源码分析、实施计划 3 篇，带合成/计划说明 |
| 安装一致性 | 模板无法随技能安装 | `assets/templates/` 生成副本 + `Generated` 头 + 漂移检查 |

## 交付物

### 标准技能

`skills/writing/markdown-document-standard/`：

- `SKILL.md`：四层流程、文档路由、ASCII 默认、修改分级、检查器用法与 Not for 边界。
- 6 个 references：Markdown 格式、ASCII 图、技术写作、文档类型路由、人工审查清单、已有文档修改。
- `scripts/doc_lint.py`：MD001–MD020，`new` / `legacy` profile，`--json`、`--strict`、`--doctype`、`--ascii-max-width`、`--ignore`、`--list-checks`。
- `scripts/tests/`：16 个单元测试；3 个干净夹具、8 个坏夹具。
- `assets/templates/`：9 个生成副本。

### 模板

`templates/` 新增 `source-analysis.md`、`incident-rca.md`、`technical-principles.md`、`implementation-plan.md`；重写 `design-document.md`、`performance-analysis.md`、`technical-article.md`、`bug-analysis.md`；`test-case-design.md` 只补标准指针。

### 集成

- 去重：`design-document`、`storage-code-analysis`、`writing-project-principles`、`wechat-tech-article` 删除重复章节清单，改为模板指针。
- ASCII 默认：`writing-project-principles` 的 SKILL、`diagram-guidelines.md`、`article-template.md`、`series-plan-template.md`；项目侧 `writing-neonsan-internals` 的 SKILL 与 `figures.md`。
- 指针：`storage-debug`、`storage-concurrency-analysis`、`test-case-design`、`producing-tech-blog`、`humanizer-zh` 增加格式/ASCII/检查指针。
- Workflow：4 个 `WORKFLOW.md` 增加同一条横向约束，不新增阶段。
- 项目仓库：`neonsan-docs` 的 8 槽清单改为模板指针，新增 `references/ascii-diagram-rules.md`；`writing-neonsan-internals` 改为 ASCII 默认；`CLAUDE.md` / `README.md` 补充同步顺序。
- 生成与校验：`skill_audit.py` 增加 `generated_templates` 检查；配置加入新技能、共享方法副本与名称前缀。

### 文档与示例

- `docs/markdown-standard/README.md`、`REPORT.md`。
- `docs/markdown-standard/examples/`：架构设计、源码分析、实施计划，均标注合成或计划属性。
- `docs/markdown-standard/examples/fixtures/mini_discard.c`：源码示例引用的合成 fixture，`file:line` 指向 fixture 已核实行号。

## 验证结果

| 项 | 命令 | 结果 |
|---|---|---|
| 单元测试 | `python3 .../scripts/tests/test_doc_lint.py` | 16 tests，OK |
| 语法 | `python3 -m py_compile doc_lint.py test_doc_lint.py skill_audit.py` | 退出 0 |
| 9 个模板 | `doc_lint.py --profile new templates/*.md` | 0 error，0 warning，9 files |
| 3 个示例 | `doc_lint.py --strict docs/markdown-standard/examples/*.md` | 0 error，0 warning，3 files |
| 标准 README | `doc_lint.py --strict docs/markdown-standard/README.md` | 0 error，0 warning |
| 坏夹具 H1 | `bad/h1.md` | 退出 1，MD001 |
| 坏夹具跳级 | `bad/jump.md` | 退出 1，MD002 |
| 坏夹具围栏 | `bad/fence.md` | 退出 1，MD005 |
| 坏夹具表格 | `bad/table-separator.md` / `bad/table-columns.md` | 退出 1，MD007 / MD008 |
| 坏夹具链接 | `bad/link.md` | 退出 1，MD012 |
| 坏夹具 ASCII | `bad/ascii.md` | 退出 1，MD014、MD015、MD017 |
| 坏夹具元数据 | `bad/metadata.md --doctype design` | 仅 MD018 warning；未指定 `--doctype` 时退出 0（元数据检查按设计跳过） |
| 旧文档 profile | `doc_lint.py --profile legacy templates/*.md` | 0 error，0 warning |
| 项目 ASCII 规则 | `doc_lint.py ../personal-notes/skills/neonsan-docs/references/ascii-diagram-rules.md` | 0 error，0 warning |
| 审计生成 | `python3 scripts/skill_audit.py --write` | 退出 0 |
| 审计校验 | `python3 scripts/skill_audit.py --check` | 0 error，127 warning，13 skills |
| Mermaid 默认残留 | grep `默认 Mermaid` | 无命中 |
| 项目词扫描 | grep 新通用技能/模板中的项目名 | 业务文件无命中；项目名只出现在项目仓库 |

审计的 127 个 warning 来自 NeonSAN 术语命中（含新增项目 ASCII 规则文件）、个人仓库技能描述缺 near-miss 等项，均非 error。模板生成副本与 shared-method 副本均通过漂移检查。

## 未运行与受阻

1. **客户端回归 R30–R32 未运行**：需要真实 Claude Code 客户端、夹具与人工评估，本环境只完成静态检查。
2. **安装同步未执行**：未运行 `sync_skills.py --apply`，未写入 `~/.claude/skills/`。
3. **未 push / 未建 PR**：按任务边界保留本地提交。
4. **未修改 `workbuddy-agents`**：该仓库只读。
5. **未批量迁移旧文档**：只提供 `legacy` profile 与一个示例性流程，不改写已有文章结论。
6. **未验证渲染**：未检查 GitHub、微信或 IDE 的实际 Markdown/ASCII 渲染效果。

## 风险与限制

- `doc_lint.py` 只解析 CommonMark 子集；锚点为近似 GitHub slug，复杂表格与 HTML 块不检查。
- ASCII 宽度按东亚宽度计算，不等同实际终端或阅读器换行；CJK 图可能仍需人工调宽。
- 静态规则不能验证技术正确性、组件职责、控制/数据语义、图形对称性或版本准确性。
- 示例为合成或计划内容；读者若引用其中的组件名、数字或结论，属于误用。
- 模板生成副本可能因手工编辑而漂移；必须通过 `skill_audit.py --check` 拦截。

## 文件与提交边界

Hans 仓库改动按边界分为：标准技能与测试、模板与示例、技能/Workflow 整合、生成物与仓库文档；personal-notes 为独立项目覆盖层。改动按显式路径分别提交到本地仓库，未 push、未同步安装目录。父目录 `CLAUDE.md` 与用户级 `CLAUDE.md` 已更新，但不在 Git 管理范围，需单独同步或备份。

未触碰 `personal-notes` 的受保护未跟踪文件 `work/neonsan/analysis/2026-11-19-csi-neonsan-clone.md`。
