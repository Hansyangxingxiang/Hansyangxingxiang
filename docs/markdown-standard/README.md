# Markdown 文档标准

面向分布式存储、云原生存储与 AI Storage 研发文档的统一格式基线。目标不是增加写作规矩，而是让设计、分析、排障、性能、原理与实施计划在同一套结构下可读、可评审、可检查。

## 四层结构

| 层 | 解决的问题 | 权威位置 |
|---|---|---|
| 1 基础格式 | 标题、段落、列表、表格、代码块、链接、元数据 | `skills/writing/markdown-document-standard/references/markdown-style-guide.md` |
| 2 内容组织 | 问题、证据、架构、机制、流程、取舍、验证的顺序与深度 | `.../references/technical-writing-guide.md` |
| 3 文档类型 | 每类文档的章节骨架与规模选择 | 仓库 `templates/`；路由见 `.../references/document-types.md` |
| 4 检查 | 可自动判定的格式错误与人工审查项 | `.../scripts/doc_lint.py`、`.../references/document-review-checklist.md` |

技能入口：[SKILL.md](../../skills/writing/markdown-document-standard/SKILL.md)。ASCII 图规范见 [ascii-diagram-guide.md](../../skills/writing/markdown-document-standard/references/ascii-diagram-guide.md)；已有文档修改分级见 [existing-document-editing.md](../../skills/writing/markdown-document-standard/references/existing-document-editing.md)。

## 核心约定

1. **单一权威**：格式规则只在 `markdown-document-standard/references/` 维护；章节结构只在 `templates/` 维护；其他技能写指针，不复制清单。
2. **ASCII 优先**：架构、控制/数据路径、时序、状态、恢复、迁移图默认 ASCII；仅当用户明确要求或目标平台明确需要时用 Mermaid。
3. **结论先于形式**：格式规范化不改变已确认章节、技术结论、设计决策与证据限定。缺失元数据写 `待补充` / `未核验`，不推断日期、版本、作者或 commit。
4. **静态检查不证明正确**：`doc_lint.py` 不验证技术结论、组件职责、控制/数据语义、图形对称性或渲染效果；通过后仍需人工审查。

## 文档类型与模板

| 文档类型 | canonical 模板 | 主要技能 |
|---|---|---|
| 架构 / 技术设计 | [design-document.md](../../templates/design-document.md) | `design-document` |
| 源码分析 | [source-analysis.md](../../templates/source-analysis.md) | `storage-code-analysis` |
| 通用故障 RCA | [incident-rca.md](../../templates/incident-rca.md) | `storage-debug` |
| 项目 Bug/事故归档 | [bug-analysis.md](../../templates/bug-analysis.md) | 项目归档技能（项目仓库） |
| 性能分析 | [performance-analysis.md](../../templates/performance-analysis.md) | `storage-debug` + `design-document` |
| 技术原理 | [technical-principles.md](../../templates/technical-principles.md) | `writing-project-principles` |
| 技术文章 | [technical-article.md](../../templates/technical-article.md) | `wechat-tech-article` + `producing-tech-blog` |
| 实施计划 | [implementation-plan.md](../../templates/implementation-plan.md) | `design-document` / 项目技能 |
| 测试用例设计 | [test-case-design.md](../../templates/test-case-design.md) | `test-case-design` |

`skills/writing/markdown-document-standard/assets/templates/` 是随技能安装的生成副本，带 `Generated` 头，不手工编辑；漂移由 `skill_audit.py --check` 拦截。

## 检查器用法

```bash
# 新文档
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --profile new doc.md

# 旧文档：H1、标题跳级、表格列数与 ASCII 宽度降级为 warning
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --profile legacy old.md

# 指定文档类型时检查必需元数据键
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --doctype design doc.md

# JSON 报告；--strict 让 warning 也导致退出码 1
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --json report.json --strict doc.md
```

退出码：`0` 无 error；`1` 存在 error（或 `--strict` 下的 warning）；`2` 参数或路径错误。`--list-checks` 列出 MD001–MD020；`--ignore MD006,MD017` 可临时忽略指定规则。

### 规则范围

| 范围 | 规则 |
|---|---|
| 标题 | 单 H1、层级不跳级、slug 不重复、编号连续 |
| 代码块 | 围栏闭合、语言标识、Mermaid 提示 |
| 表格 | 分隔行合法、列数一致 |
| 空白 | 行尾空格、代码外 Tab、连续空行 |
| 链接 | 相对目标存在、Markdown 锚点可匹配 |
| ASCII 图 | 显示宽度（CJK 宽 2）、Tab、框线混用、图注 |
| 元数据 | 指定文档类型时必需键、占位符提醒 |

## 示例

三个完整示例均标注为合成或计划示例，不可当作真实项目事实：

- [分布式块存储架构设计](examples/architecture-design.md)
- [Discard 校验路径源码分析](examples/source-analysis.md)（引用合成 fixture [mini_discard.c](examples/fixtures/mini_discard.c)）
- [Markdown 标准接入实施计划](examples/implementation-plan.md)

```bash
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --strict docs/markdown-standard/examples/*.md
```

## 与已有技能、模板、Workflow 的关系

- 内容技能保留方法、判断与失败模式；章节清单与格式细节移入本技能和 `templates/`。
- 4 个 Workflow 增加同一条横向约束：格式/ASCII/检查，但不新增流水线阶段。
- 项目仓库只增加 NeonSAN 角色与图示语义（`neonsan-docs/references/ascii-diagram-rules.md`），不复制通用规则。
- 修改本仓库后需同步 `~/.claude/skills/markdown-document-standard/` 才在客户端生效；同步默认 dry-run，不自动 `--apply`。

## 已知限制

- 只解析 CommonMark 子集；复杂嵌套表格、HTML 块、脚注不在检查范围。
- 锚点为近似 GitHub slug，不覆盖自定义锚点与重复标题的 `-1` 后缀。
- ASCII 宽度按东亚宽度计算，不模拟终端字体、换行与渲染器差异。
- 无法判断图的技术正确性、组件职责是否准确、控制/数据路径语义是否成立。

## 验证状态

静态项与单元测试见 [REPORT.md](REPORT.md)。真实客户端触发与产出质量回归（R30–R32）标为未运行，需在 Claude Code 客户端执行。
