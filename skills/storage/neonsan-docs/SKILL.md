---
name: neonsan-docs
description: Use when asked to write a NeonSAN design document for a feature or
  optimization (方案设计), or an analysis/archive document for a bug, incident,
  or production issue (分析归档) — Chinese body, saved as local markdown. Not for
  Confluence publishing, blog articles, or Jira comment editing.
---

# Writing NeonSAN Design/Analysis Docs — NeonSAN 文档规范与归档专家

## Overview

本 skill 负责 **NeonSAN 项目研发文档的规范与归档**：在 NeonSAN 里怎么组织、怎么落盘。**不再定义完整设计章节结构**——章节结构归 design-document（通用研发技术设计文档专家）。

一条铁律（Iron law）：**每个 file:line 必须从当前代码重读**。MEMORY.md / plans / wiki / transcripts 只是线索——行号会漂移。

## When to Use / NOT

Use: "写个设计文档", "分析一下这个 bug 记录下来", archiving bugs found in review.

NOT: Confluence publishing (use qingcloud-atlassian), blog articles (producing-tech-blog), pure implementation tasks.

## Phase 0 — Classify & Place

- **design** (方案设计) → repo-top `docs/design/YYYY-MM-DD-<slug>.md`
- **analysis** (分析归档) → `docs/analysis/YYYY-MM-DD-<slug>.md`

`docs/` is a non-repo directory — never committed.

## Phase 1 — Verify by Reading Code (source map)

grep to locate → read → record `{conclusion, file:line, one-line note}`; every conclusion needs code evidence; log strings verbatim. git evidence (`git log -S`, `git show`) only inside qfa/qfcenter/qbd/monitor/ci subdirs — top level is not a repo.

## Phase 2 — Structure

**设计文档的章节结构由 design-document 决定**（默认 8 个一级章节）。本 skill 负责按 NeonSAN 规范组织与落盘，不重复定义章节模板。

### 分析归档规范（8 槽，推荐归档规范，非设计章节）

Bug / 事故分析归档建议按以下 8 槽组织，按序填写。空槽写"无" + 一行原因，不删除。

1. **概要** — one-sentence verdict first
2. **后果** — tiered: unreachable-by-default / silent damage / privacy…
3. **触发链** — causal chain from request to failure
4. **触发条件与暴露面** — config gates, versions, blast radius
5. **来源与定年** — git evidence: introducing commit + date + Jira
6. **发现过程** — how/when found (review? production log?)
7. **修法建议** — options + risk trade-offs
8. **处置状态** — incl. user ruling verbatim

## Phase 3 — Hard Checklist

- **Direction semantics**: any range conversion/alignment states its ceil/floor (expand/shrink) direction and argues SHRINK. Prefer "one whole object per command" protocol shapes that eliminate conversion arithmetic.
- **Resource conflicts**: grep existing users before claiming a new opcode/constant (0x88/0x89 were taken).
- **Full-path walkthrough**: enumerate every exit of a lifecycle; check adjacent command types symmetrically (error labels outside the switch).
- **Concurrency**: per path — protecting lock + TOCTOU.
- **Dating**: analysis docs carry a git evidence chain, not a guess.

## Phase 4 — Verification Plan

No-cluster: TCP/RDMA mirror-symmetry walk; explicit ninja targets (`neonsan_tcp_client` not implied by `neonstore`); grep marker counts; `git show` hunk check; then cluster scenarios + acceptance criteria.

## NeonSAN 文档规范

### NeonSAN 专属术语

- **模块名**：qfa / qfcenter / qbd / monitor / ci。
- **核心组件**：NeonStore / NeonSAN CLI / QFCenter。
- **数据对象**：Volume / Snapshot / Clone / Object / Extent / LBA。
- **请求类型**：Write / Discard / COW / Recovery / Migration。
- 无依据不创造术语。

### Markdown 规范

- 标题层级、代码块、表格、ASCII 图遵循仓库既有风格。
- 英文技术词保留原文，不翻译；首次出现可加中文注释，之后一律用英文原词。
- 代码标识符、函数名、结构体名一律用原文。

### 文档归档分类

设计文档 / 源码分析 / Bug 分析 / 性能分析 / 技术调研 / 测试报告。

### 文档落盘

- 文件命名 `YYYY-MM-DD-<slug>.md`。
- 保存目录 `docs/design|analysis|...`（non-repo 不提交）。
- 更新已有文档方式：优先编辑既有文档，避免重复创建；保留已有内容原则。

### ASCII 架构图规范

- 简洁 / 对齐 / 表达数据流与控制流。
- 不用 Mermaid 除非用户明确要求。

## Common Mistakes

- Citing file:line from memory/plan without re-reading (numbers drift)
- Direction (ceil/floor) asserted but never argued
- Conclusion without code evidence
- Treating plan-era line numbers as fact
- Analysis doc without git dating
- Dropping 发现过程/处置状态 slots "because nothing to say"
- 重复定义设计章节结构（归 design-document）
- 创造无依据的 NeonSAN 术语
