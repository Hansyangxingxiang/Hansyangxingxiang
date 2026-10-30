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

一条铁律（Iron law）：**每个 file:line 必须有当前版本的实读核验记录；相关版本、文件或条件变化后重新核验**。MEMORY.md / plans / wiki / transcripts 只是线索——行号会漂移。

## When to Use / NOT

Use: "写个设计文档", "分析一下这个 bug 记录下来", archiving bugs found in review.

NOT: Confluence publishing (use qingcloud-atlassian), blog articles (producing-tech-blog), pure implementation tasks.

## Phase 0 — 确认项目与归档位置

仅在确认目标是 NeonSAN 项目后应用专属规范。先读取项目说明，使用 `git rev-parse --show-toplevel`、`git -C <目录> rev-parse --show-toplevel` 与 `git check-ignore` 核实源码根、嵌套仓库和归档目录；不假定顶层一定不是仓库或 docs 一定不提交。

优先使用已有文档及项目约定，默认建议 `docs/design/YYYY-MM-DD-<slug>.md` 或 `docs/analysis/YYYY-MM-DD-<slug>.md`。确认实际保存路径，保留已有内容；是否纳入版本管理遵循目标项目规则。

历史工作区示例见 [项目配置参考](references/project-layout.md)，仅作定位线索。

## Phase 1 — Verify by Reading Code (source map)

grep to locate → read → record `{conclusion, file:line, one-line note}`; 实现结论需要源码证据，需求、运行现象与设计决策分别引用对应依据；日志原样引用。git evidence (`git log -S`, `git show`) 在探测到的实际仓库根中执行，不预设顶层或子目录的 Git 属性。

## Phase 2 — Structure

**设计文档的章节结构由 design-document 决定**（按规模选择轻量或完整模式）。本 skill 负责按 NeonSAN 规范组织与落盘，不重复定义章节模板。

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

- **Direction semantics**: any range conversion/alignment states its ceil/floor (expand/shrink) direction and argues SHRINK. 按已确认的协议与需求比较设计方案，不预设必须采用整对象命令。
- **Resource conflicts**: grep existing users before claiming a new opcode/constant ；具体值是否占用以当前版本为准。
- **Full-path walkthrough**: enumerate every exit of a lifecycle; check adjacent command types symmetrically (error labels outside the switch).
- **Concurrency**: per path — protecting lock + TOCTOU.
- **Dating**: analysis docs carry a git evidence chain, not a guess.

## Phase 4 — Verification Plan

无集群时，按实际改动检查适用的 TCP/RDMA 路径、错误分支与差异。构建目标从当前构建文件和项目说明确认；静态检索不能代替功能验证。给出集群场景与验收条件，明确哪些检查已执行、未执行或受阻。

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
- 保存目录 `docs/design|analysis|...`（以探测到的项目规范为准）。
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

## 输入、交付与证据复用

- 输入：已确认的 NeonSAN 项目、文档内容、证据和归档规则。
- 交付与完成条件：符合实际项目规则的本地文档路径与检查结果。只有文件实际保存并检查后才声称归档完成；外部发布不在本技能范围。
- 输入不足时先完成有依据的部分，仅询问影响结论或执行的关键缺口。
- 交接证据包含仓库、commit、文件或符号、结论与验证状态。同一版本且相关文件与运行条件未变化时复用已核验记录；版本、文件或关键条件变化时重核相关结论，不重复开展全部研究。
