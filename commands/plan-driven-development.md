---
description: 复杂任务计划驱动研发：Plan → Review → Execute → Verify → Report，计划确认与执行授权分离
argument-hint: <任务目标、范围或已有计划路径>
---

按 plan-driven-development 工作流处理下面的任务：

$ARGUMENTS

执行步骤：

1. 读取 `~/.claude/workflows/plan-driven-development/WORKFLOW.md`；该文件不存在时，读取本命令来源仓库的 `workflows/plan-driven-development/WORKFLOW.md`。
2. 判断是否属于复杂任务：跨文件/模块/技能、存在设计取舍、数据或兼容风险、需要回滚或跨会话恢复。简单任务直接完成，不套流程。
3. 处于 Plan Mode 时：只做调研、影响面分析、方案对比，输出计划（背景、目标、非目标、现状、方案、影响文件、步骤、风险、验证、回滚）；不写项目文件，不创建 `docs/plans/`，等待原生计划确认。
4. 计划确认后检查执行授权：批准消息明确要求执行才写文件；只说“计划可以”时，询问一次是否开始执行。Plan Mode 批准不等于执行授权。
5. 获得执行授权后：先写 `docs/plans/YYYY-MM-DD-task-name.md`（模板 `templates/plan-driven-development.md`），状态置 `执行中`；再按步骤实施，更新清单与执行记录，不扩范围、不覆盖用户未提交改动。
6. 执行后检查实际 diff，运行适用的构建/测试/静态检查；未运行项标 `未运行`/`受阻`。更新计划状态与最终报告。
7. 文档沉淀：按已验证实现更新最终技术文档（`docs/design/`、`docs/internals/`、`docs/troubleshooting/` 或项目既有目录）；只写已验证内容，保留长期决策与交叉引用，不复制执行清单。
8. 中断恢复：读计划状态与清单、`git status`/`git diff`、已有验证记录，从首个未完成步骤继续；无法确认的项重跑，不凭记忆标完成。
9. 领域内容交给对应技能与 Workflow：设计用 `design-document`，源码用 `storage-code-analysis`，排障用 `storage-debug`；本工作流只治理执行过程。

不要实现审批 UI、状态数据库或原生计划文件读写；不自动提交、不 push、不发布。
