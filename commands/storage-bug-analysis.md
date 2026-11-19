---
description: 存储故障分析：现象 → 分层定位 → 源码/调用链 → 根因 → 修复与测试方案
argument-hint: <故障现象或待排查问题>
---

按 storage-bug-analysis 工作流排查下面的问题：

$ARGUMENTS

执行步骤：

1. 读取 `~/.claude/workflows/storage-bug-analysis/WORKFLOW.md`；该文件不存在时，读取本命令来源仓库的 `workflows/storage-bug-analysis/WORKFLOW.md`。
2. 从现象出发建立假设与验证实验，先走 `storage-debug` 主入口；需要调用链与源码证据时用 `storage-code-analysis`。
3. 条件分支：症状为数据不一致、已删除对象重新可见或疑似竞态时，先用 `storage-concurrency-analysis` 梳理并发生命周期与交错时序，再回到 `storage-debug` 验证。普通空间未释放、IO 行为异常不强制进入该分支。
4. 根因确认后再用 `design-document` 产出修复方案与测试方案。
5. 遵守证据规则：根因是证据闭环后的结论；未确认时列候选解释、反证和下一步实验，不把单条日志当根因。
6. 交付根因分析、方案与归档路径，标注已验证 / 待验证项；不自动执行破坏性命令。
