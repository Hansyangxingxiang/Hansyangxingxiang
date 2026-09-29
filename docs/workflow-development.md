# Workflow 开发指南

## 如何创建 Workflow

1. 在 `workflows/<workflow-name>/WORKFLOW.md` 下创建。
2. 每个 WORKFLOW.md 必须含：目的、适用场景、阶段流水线（ASCII）、每阶段用到的 Skill、产出物、检查清单。
3. 阶段流水线用 ASCII 图表达端到端流程。
4. 明确每个阶段用哪个 Skill，不把逻辑塞进单个 Skill。

## 何时用 Workflow 而非 Skill

- **用 Workflow**：任务需要多个 Skill 组合、有明确阶段顺序、产出物跨多个 Skill。
- **用 Skill**：任务单一、只解决一类问题、不需要编排。

## 检查清单

- [ ] 目的清晰
- [ ] 适用场景明确
- [ ] 阶段流水线完整（ASCII）
- [ ] 每阶段 Skill 引用正确
- [ ] 产出物明确
- [ ] 检查清单可执行
