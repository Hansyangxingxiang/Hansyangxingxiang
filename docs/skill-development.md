# Skill 开发指南

## 如何新增 Skill

1. 在 `skills/<category>/<skill-name>/` 下创建 `SKILL.md`。
2. frontmatter 必须含 `name`（唯一标识）与 `description`（触发条件 + 不适用场景）。
3. 遵循仓库核心原则：单一能力、不绑定项目、基于事实、不确定标注。项目专属能力不放本仓库，应放到对应项目仓库（如 `personal-notes`），`name` 与目录名仍须一致。
4. 若产出物有固定结构，在 `templates/` 提供对应 Template。
5. 若被 Workflow 使用，更新对应 `workflows/*/WORKFLOW.md` 的 Skill 引用。

## 如何修改 Skill

- 保持单一职责，不堆叠多职责。
- 避免重复规则：同一规则只在一处定义。
- 修改后同步到 `~/.claude/skills/` 对应目录才生效（见 `docs/usage.md`）。

## 如何测试 Skill

- 用真实任务触发，验证 description 能正确触发。
- 验证产出物结构符合对应 Template。
- 验证与其他 Skill 无冲突、无重复规则。
- 验证 frontmatter `name` 唯一且引用一致。

## 回归评估

按 [Skill 任务回归集](skill-regression.md) 对比修改前后表现。静态名称与引用检查不能替代客户端中的实际触发和产出评估。

## 命名约定

- 目录名 = Skill 名（kebab-case）。
- `name` 与目录名一致。
- 改名需同步更新所有引用（Workflow / docs / 其他 Skill 的协作说明）。
