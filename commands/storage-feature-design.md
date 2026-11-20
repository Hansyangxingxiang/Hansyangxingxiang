---
description: 存储功能设计：需求 → 现状/源码 → 并发 → 方案 → 归档，产出可评审设计文档
argument-hint: <功能需求或设计主题>
---

按 storage-feature-design 工作流处理下面的需求：

$ARGUMENTS

执行步骤：

1. 读取 `~/.claude/workflows/storage-feature-design/WORKFLOW.md`；该文件不存在时，读取本命令来源仓库的 `workflows/storage-feature-design/WORKFLOW.md`。
2. 按工作流规定确定范围与阶段：现状分析、源码分析、约束分析、并发/一致性分析、方案设计、异常、兼容升级、测试设计、归档。已有产物满足条件时从对应阶段继续，不静默跳阶段。
3. 按阶段委托对应技能：
   - 现状 / 源码：`storage-code-analysis`
   - 并发 / 一致性：`storage-concurrency-analysis`（结论作为方案输入，不替代 `design-document`）
   - 方案 / 异常 / 兼容 / 测试设计：`design-document`
   - NeonSAN 项目归档：`neonsan-docs`（personal-notes 仓库维护）
4. 遵守工作流的证据与交接规则：`file:line` 本轮实读，事实 / 推断 / 建议 / 待验证分开，未运行实验不得标为通过。
5. 交付设计文档路径、证据基线与待确认项；不自动发布或执行远端变更。
