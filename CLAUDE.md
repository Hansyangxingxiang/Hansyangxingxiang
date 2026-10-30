# CLAUDE.md — Personal AI Engineering Skills 仓库总规则

本仓库是**个人 AI Engineering Skills** 的受版本管理副本，定位为可长期用 Git 管理的个人技能库。不绑定 NeonSAN，未来扩展分布式存储 / Ceph / 云原生存储 / AI Infrastructure / KV Cache / AI Storage 等方向。

## 仓库定位

- **Skills**：单一能力单元，每个 Skill 只做一件事。
- **Workflows**：组合多个 Skill 的端到端流水线，解决完整任务。
- **Templates**：输出结构骨架，保证产出物格式一致。
- **docs/**：仓库说明、Skill / Workflow 开发指南、使用说明。

## 核心原则（8 条）

1. **Skill 单一能力**：一个 Skill 只解决一类问题，不堆叠多职责。
2. **Workflow 组合能力**：复杂任务由 Workflow 编排多个 Skill，而非把逻辑塞进单个 Skill。
3. **Template 输出结构**：产出物结构由 Template 约束，Skill 负责方法与判断。
4. **通用能力不绑定项目**：通用 Skill（如 design-document）不依赖任何项目专属术语。
5. **项目专属能力归属项目仓库**：NeonSAN 专属技能（neonsan-docs / ci-test-case / writing-neonsan-internals）由 personal-notes 仓库维护，本仓库不复制，避免污染通用 Skill。
6. **优先基于事实和源码**：结论带出处（`file:line`、命令输出、文档链接），不凭记忆。
7. **不确定必须标注**：推测 / 推断 / 观点必须明确标注，不冒充事实。
8. **分布式存储优先一致性 / 并发 / 异常恢复**：Write / Discard / Snapshot / Clone / COW / Recovery 等生命周期必须主动检查。

## 修改原则

- **避免重复规则**：同一规则只在一处定义，其余引用。
- **避免无限膨胀**：不为"完整"机械增加章节 / 规则。
- **保持单一职责**：改动不破坏 Skill / Workflow / Template 的职责边界。
- **优先复用**：能复用既有 Skill / Template 就不新建。

## 目录结构

```
skills/       Skill 定义（storage/ 与 writing/ 分类）
workflows/    Workflow 流水线定义
templates/    输出结构模板
docs/         仓库说明与开发指南
```

## 与 ~/.claude/skills/ 的关系

本仓库是**受版本管理的副本**。`~/.claude/skills/` 是 Claude Code 实际加载的生效目录。改动本仓库后，需**手动同步**到 `~/.claude/skills/` 对应目录才生效。详见 `docs/usage.md`。

NeonSAN 专属技能（neonsan-docs / ci-test-case / writing-neonsan-internals）不在本仓库，从 `personal-notes` 仓库的 `skills/` 同步到 `~/.claude/skills/`。
