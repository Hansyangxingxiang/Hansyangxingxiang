---
name: markdown-document-standard
description: Use when 需要统一技术文档的 Markdown 排版、章节结构、ASCII 架构图或发布前静态检查 — 设计文档、源码分析、RCA、性能报告、技术原理、技术博客、实施计划。Not for 技术内容研究与结论（分别用 design-document、storage-code-analysis、storage-debug、writing-project-principles）；不负责微信 HTML 排版（用 producing-tech-blog）、内容选题（用 wechat-tech-article）或纯语言润色（用 humanizer-zh）。
---

# Markdown Document Standard — 技术文档格式与结构规范

## Overview

本技能是技术文档**格式、结构与静态检查**的唯一权威源。它不研究方法、不做技术判断、不生成内容结论；内容由对应领域技能负责。

四层结构：

1. 基础排版 → `references/markdown-style-guide.md`
2. 内容组织 → `references/technical-writing-guide.md`
3. 文档类型与模板 → `references/document-types.md` + `templates/`
4. 检查与审查 → `scripts/doc_lint.py` + `references/document-review-checklist.md`

## When to Use / NOT

适用：

- 新建或规范化设计文档、源码分析、RCA、性能报告、技术原理、技术博客、实施计划。
- 需要 ASCII 架构图、控制/数据路径图、时序图、状态图或恢复图。
- 发布前做 Markdown 静态检查，或按统一结构评审文档。
- 需要判断“格式优化 / 表达优化 / 结构调整 / 技术内容变更”的边界。

不适用：

- 技术研究、源码结论、故障根因、方案取舍 → `design-document`、`storage-code-analysis`、`storage-debug`。
- 原理文章的机制论证 → `writing-project-principles`；项目内部规范 → 对应项目技能。
- 微信 HTML 生成 → `producing-tech-blog`；选题与读者表达 → `wechat-tech-article`；去 AI 味 → `humanizer-zh`。

## 单一权威与协作

- 正文格式规则只在本技能维护；其他技能写指针，不复述整套规则。
- 章节结构只在 `templates/` 维护；技能只保留方法、判断与失败模式。
- 项目专属术语、角色准确性与归档规则由项目仓库的技能维护，本技能不写项目词。
- 证据分级、输入不足与交付复用遵循 `references/shared-method.md`。

## 文档路由

按任务选择模板与领域技能：

| 任务 | 模板 | 内容技能 |
|---|---|---|
| 软件/存储架构设计 | `templates/design-document.md` | `design-document` |
| 源码调用链与机制分析 | `templates/source-analysis.md` | `storage-code-analysis` |
| 故障 RCA | `templates/incident-rca.md` | `storage-debug` |
| 项目分析归档（8 槽） | `templates/bug-analysis.md` | 项目归档技能 |
| 性能分析与优化 | `templates/performance-analysis.md` | `storage-debug` + `design-document` |
| 技术原理讲解 | `templates/technical-principles.md` | `writing-project-principles` |
| 技术博客 / 公众号草稿 | `templates/technical-article.md` | `wechat-tech-article` |
| 实施计划（正式交付物） | `templates/implementation-plan.md` | `plan-driven-development` / 用户 |
| 计划与执行台账 | `templates/plan-driven-development.md` | `plan-driven-development` |
| 测试用例设计 | `templates/test-case-design.md` | `test-case-design` |

模板是完整骨架；规模、合并与裁剪由内容技能判断，不机械填满。详细路由与元数据要求见 `references/document-types.md`。

## 核心原则

1. **一个 H1**；章节编号连续，层级不跳级，原则上不超过四级。
2. **先结论后依据**；复杂机制按“问题 → 为什么 → 如何实现 → 正常 → 异常 → 取舍”展开。
3. **事实 / 推断 / 建议 / 待验证** 分离；事实给出处，不编造路径、行号、日志或实验数据。
4. **ASCII 优先**：正式技术文档的架构、控制/数据路径、时序、状态、恢复、迁移图默认 ASCII；仅当用户明确要求或目标平台明确需要时用 Mermaid。
5. **一图一问题**；控制路径、数据路径、元数据操作与异步任务分开；图后按组件职责、交互流程、关键机制、异常与边界解释，图注说明条件与箭头语义。
6. **表格承载结构化对照，正文承载论证**；不把完整论述塞进单元格。
7. **统一格式不统一章节**：所有文档共享正文格式；设计、源码分析、RCA、技术原理、计划台账保留各自模板结构。
8. **计划台账不是终态文档**：最终技术文档从已验证实现沉淀，不复制实施清单，不把未完成计划写成已实现。
9. **保留已确认内容**：编辑既有文档时，不借格式统一改写技术结论或设计决策。

## ASCII 图最低要求

- 使用等宽字符与 `text` 围栏；显示宽度建议不超过 100 列（公众号等窄屏场景不超过 78）。
- 组件方框对齐，箭头方向一致；避免连线交叉与超宽图；一张图回答一个问题。
- 控制消息、数据搬运、元数据查询用不同箭头或标签；同步/异步明确。
- 图注格式：`**图 N：<一句话结论>（<条件/图例>）**`；正文引用“如图 N 所示”。
- 无法在一张图内表达时拆图，不混层。
- 完整规则见 `references/ascii-diagram-guide.md`；项目角色准确性由项目技能补充。

## 已有文档修改分级

| 类别 | 示例 | 权限 |
|---|---|---|
| 格式优化 | 空行、标题层级、表格转义、围栏语言、链接语法、元数据形式 | 可直接做，渲染含义不变 |
| 表达优化 | 措辞、句序、术语统一 | 保留事实、数字、单位、限定词与作者声音；大改先确认 |
| 结构调整 | 章节顺序、合并拆分、编号、模板迁移 | 需用户确认；保留已确认章节与结论，给出旧→新映射 |
| 技术内容变更 | 事实、结论、设计决策、范围 | 必须给依据并由用户决定，不与格式修改混在一起 |

完整规则见 `references/existing-document-editing.md`。

## 静态检查

运行：

```bash
python3 scripts/doc_lint.py --profile new <file-or-dir>
python3 scripts/doc_lint.py --profile legacy <old-doc.md>
python3 scripts/doc_lint.py --strict --json report.json <files>
```

检查单 H1、标题跳级、编号连续性、围栏闭合与语言标识、表格分隔与列数、相对链接与锚点、行尾空格、连续空行、ASCII 显示宽度/Tab/框线风格/图注、指定文档类型的元数据键。退出码 0/1/2。

脚本不能验证：图的技术正确性、组件职责、控制/数据语义、交叉与对称美观、项目角色准确性、证据真实性与渲染结果。静态通过不等于人工审查通过。

## 输入、交付与完成条件

输入：目标文档类型、正文或提纲、读者与发布渠道、可用的模板路径、是否需要检查旧文档。

交付：符合本规范的 Markdown；必要的图注与元数据；静态检查结果；未验证项清单；结构或技术内容变更说明。

完成条件：格式规则满足；结构与模板一致或已说明差异；ASCII 图可读且图文一致；静态检查无未解释的 error；无法自动验证的内容已列入人工审查。

## 参考资源

- `references/markdown-style-guide.md`
- `references/technical-writing-guide.md`
- `references/ascii-diagram-guide.md`
- `references/document-types.md`
- `references/document-review-checklist.md`
- `references/existing-document-editing.md`
- `references/shared-method.md`（生成副本，证据与交付通用规则）
- `scripts/doc_lint.py`、`scripts/tests/`
