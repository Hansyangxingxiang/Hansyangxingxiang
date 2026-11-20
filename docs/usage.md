# 使用指南

## 在 Claude Code 中使用这些 Skill

本仓库的 Skill 是**受版本管理的副本**。Claude Code 实际加载的是 `~/.claude/skills/` 下的目录。

### 生效目录

- 生效目录：`~/.claude/skills/`
- 本仓库：`skills/`（受版本管理）

### 同步说明

改动本仓库后，需**手动同步**到 `~/.claude/skills/` 对应目录才生效。例如：

```bash
# 同步 design-document
rsync -a -c --delete-delay --omit-dir-times skills/storage/design-document/ ~/.claude/skills/design-document/
```

`scripts/sync_skills.py` 提供带差异预览的同步方式，默认 dry-run，`--apply` 才写入：

```bash
python3 scripts/sync_skills.py                          # 预览全部 Hans 技能
python3 scripts/sync_skills.py --skills design-document --apply
python3 scripts/sync_skills.py --commands --workflows --apply
```

删除目标目录中多余文件必须显式加 `--delete`；同步 personal-notes 技能须显式 `--repo personal-notes`。

### Command 与 Workflow 的同步

Claude Code **不会自动发现** `workflows/`。`WORKFLOW.md` 是编排说明，实际入口是 `commands/<name>.md`：

```bash
rsync -a -c --delete-delay --omit-dir-times commands/ ~/.claude/commands/
rsync -a -c --delete-delay --omit-dir-times workflows/ ~/.claude/workflows/
```

同步后可用 `/storage-feature-design`、`/storage-bug-analysis`、`/storage-performance-analysis`、`/technical-writing`、`/plan-driven-development`。未同步时，可在对话中直接说明任务，由技能自动触发。

### 计划驱动执行

复杂、多步骤、跨文件任务使用 `plan-driven-development`。在 Plan Mode 中它只输出计划、不写项目文件；原生计划批准不等于执行授权，需用户明确要求开始执行。执行台账写在项目 `docs/plans/YYYY-MM-DD-task-name.md`，结构见 `templates/plan-driven-development.md`，恢复与状态规则见 `docs/plans/README.md`。领域内容仍由对应 Workflow 与技能负责。

### NeonSAN 专属技能

`neonsan-docs`、`ci-test-case`、`writing-neonsan-internals` 绑定 NeonSAN 项目，**不在本仓库**，由 `personal-notes` 仓库的 `skills/` 维护。这些技能同样需要同步到 `~/.claude/skills/`：

```bash
# 在 personal-notes 仓库根目录执行
for n in neonsan-docs ci-test-case writing-neonsan-internals; do
  rsync -a -c --delete-delay --omit-dir-times "skills/$n/" "$HOME/.claude/skills/$n/"
done
```

目录名与 `SKILL.md` frontmatter 的 `name` 一致，运行时技能名不变。

### 触发方式

Skill 通过 description 自动触发。也可在对话中直接描述任务，Claude Code 会匹配对应 Skill。

## Markdown 文档标准与检查

格式、章节结构路由、ASCII 图与文档类型模板以 `markdown-document-standard` 为唯一权威源。写设计文档、源码分析、RCA、性能报告、技术原理、公众号文章或实施计划时，先按该技能的 `references/document-types.md` 选模板，再用对应内容技能写正文。

```bash
# 新文档：0 error 才可交付（warning 仍需人工判断）
python3 ~/.claude/skills/markdown-document-standard/scripts/doc_lint.py --profile new doc.md

# 旧文档：降级 H1、标题跳级、表格列数与 ASCII 宽度规则
python3 ~/.claude/skills/markdown-document-standard/scripts/doc_lint.py --profile legacy old.md

# 完整仓库模板与示例（在仓库根执行）
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --profile new templates/*.md
python3 skills/writing/markdown-document-standard/scripts/doc_lint.py --strict docs/markdown-standard/examples/*.md
python3 skills/writing/markdown-document-standard/scripts/tests/test_doc_lint.py
```

`doc_lint.py` 只做静态格式检查，不能验证技术结论、图语义或渲染效果；静态通过后仍需人工审查。技术图默认 ASCII；仅当用户明确要求或目标平台明确需要时使用 Mermaid。

## 存储分析入口

- 并发 / 竞态 / 数据安全（是否丢数据、是否数据复活、谁负责保护、如何验证）：`storage-concurrency-analysis`。
- 只需读懂源码或调用链：`storage-code-analysis`。
- 已有具体故障现象要反推根因：`storage-debug`。
- 要为并发保护机制写正式设计文档：`design-document` 主导，并发结论由 `storage-concurrency-analysis` 提供。

```bash
# 同步 storage-concurrency-analysis
rsync -a -c --delete-delay --omit-dir-times skills/storage/storage-concurrency-analysis/ ~/.claude/skills/storage-concurrency-analysis/
```

## 博客工具（可选）

三个脚本只用 Python 3.8+ 标准库，脚本不可用不阻塞手工排版与人工润色。

```bash
cd skills/writing/producing-tech-blog
python3 scripts/md2wx.py article.md -o article.html --accent "#1677FF" --font-size 16
python3 scripts/blog_lint.py article.md --deny deny-words.txt

cd ../humanizer-zh
python3 scripts/check_style.py draft.md
```

- `md2wx.py` 只做排版转换，并在输出旁写 `article.report.json`；不修改源 Markdown。
- `blog_lint.py` 做编码、敏感词、结构与发布前体检；退出码 0 仅表示「可发布」。
- `check_style.py` 只报告硬禁令与风险位置，不自动改写；WARN 需人工判断。
- 脚本是辅助证据，不等于微信客户端预览，预览仍需单独记录。

```bash
# 同步博客工具相关技能
rsync -a -c --delete-delay --omit-dir-times skills/writing/producing-tech-blog/ ~/.claude/skills/producing-tech-blog/
rsync -a -c --delete-delay --omit-dir-times skills/writing/humanizer-zh/ ~/.claude/skills/humanizer-zh/
```

## 按任务选择 Workflow

| 任务 | 用哪个 Workflow |
|---|---|
| 设计一个存储功能 | `storage-feature-design` |
| 排查一个存储 bug | `storage-bug-analysis` |
| 分析一个性能问题 | `storage-performance-analysis` |
| 写一篇技术文章 | `technical-writing` |

上表的 Workflow 需先按上文同步 `commands/` 与 `workflows/`，再以 slash command 调用；直接说任务时由 Skill 自动匹配，但不会自动加载整条流水线。

## 写作任务入口

- 项目原理、源码证据、系列规划、技术评审或系列一致性：`writing-project-principles`。
- 公众号选题、标题或已有正文的读者表达调整：`wechat-tech-article`。
- 只润色已有文本：`humanizer-zh`；只生成微信 HTML：`producing-tech-blog`。
- 公众号原理文章先完成机制论证，再按需处理表达和排版；博客或系列规划不自动生成 HTML。

## 使用示例

以「设计分布式块存储 Trim/Discard 功能」为例：

1. 用 `storage-code-analysis` 分析现有 Discard 处理路径（源码事实）。
2. 用 `design-document` 产出 8 章节设计文档（含并发 / 一致性 / 兼容 / 测试）。
3. 用 `neonsan-docs`（personal-notes 仓库维护）按 NeonSAN 规范归档落盘。
4. 或调用 `/storage-feature-design` 端到端完成（需先同步 `commands/` 与 `workflows/`）。
