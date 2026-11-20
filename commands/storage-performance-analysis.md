---
description: 存储性能分析：指标确认 → 调用链 → 瓶颈 → 优化方案 → 验证
argument-hint: <性能现象或指标异常描述>
---

按 storage-performance-analysis 工作流分析下面的性能问题：

$ARGUMENTS

执行步骤：

1. 读取 `~/.claude/workflows/storage-performance-analysis/WORKFLOW.md`；该文件不存在时，读取本命令来源仓库的 `workflows/storage-performance-analysis/WORKFLOW.md`。
2. 先确认指标与观测方法（延迟 / 吞吐 / 队列深度 / 时延分布），再沿调用链定位瓶颈；主入口为 `storage-debug`，调用链与源码用 `storage-code-analysis`。
3. 优化方案与设计文档用 `design-document`，必须给出对比、取舍与适用条件。
4. 验证阶段区分已实测与验证方案：未运行的实验、未采集的指标标为未验证，不填实测数字。
5. 交付性能分析报告路径、前后对比方法、证据基线与待确认项；不自动部署或改动集群。
