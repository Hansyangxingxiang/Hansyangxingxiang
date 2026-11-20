# 技能库审计与优化交付物

基线：`Hansyangxingxiang@02dd60b`、`personal-notes@a2b7834`、`workbuddy-agents@05356b5`（只读）。
改动范围：`Hansyangxingxiang/` 与 `personal-notes/`；`workbuddy-agents/` 与 `~/.claude/` 未改。
验证边界：静态检查已执行；客户端触发、路由与产出质量未运行。

## 交付物

| 文件 | 生成方式 | 内容 |
|---|---|---|
| `SKILL_INVENTORY.md` | 脚本生成 | 12 个技能的路径、行数、references、描述摘要 |
| `SKILL_ASSESSMENT.md` | 人工 | 8 维加权评分（改前 6.8 → 改后 8.8）、逐技能评分与证据 |
| `SKILL_DEPENDENCIES.md` | 脚本生成 | 技能 ↔ Workflow ↔ Command 引用关系与悬空检查 |
| `OPTIMIZATION_PLAN.md` | 人工 | 目标、现状问题、目标架构、A/B 阶段、验收、风险与回滚 |
| `SKILL_REGISTRY.md` | 脚本生成 | 机器注册表的人读版本 |
| `MIGRATION_MAP.md` | 人工 | 职责映射、文件级新增/修改、未改动项、提交与回滚 |
| `REGRESSION_REPORT.md` | 人工 | 静态与脚本结果、逐技能触发用例（未运行）、R01–R29 状态 |
| `OPTIMIZATION_SUMMARY.md` | 人工 | 14 个问题回答、前后对比、修改清单、剩余事项 |
| `skill_registry.json` | 脚本生成 | 机器可读注册表：技能、workflow、command、模板、生成物哈希 |

## 重新生成与校验

```bash
cd Hansyangxingxiang
python3 scripts/skill_audit.py --write   # 重新生成 4 份生成物与 shared-method 副本
python3 scripts/skill_audit.py --check   # 校验结构、引用、重复、脱敏、生成物漂移
```

生成物不手改；通用规则改 `shared/references/method-and-evidence.md` 后重新 `--write`。

## 阅读顺序

1. `OPTIMIZATION_SUMMARY.md`：先看结论与待确认项。
2. `SKILL_ASSESSMENT.md`：看质量依据与薄弱项。
3. `MIGRATION_MAP.md`：看具体改了什么、如何回滚。
4. `REGRESSION_REPORT.md`：看哪些验证已做、哪些未做。
5. `OPTIMIZATION_PLAN.md`：看方案与验收标准。
6. 生成物（INVENTORY / DEPENDENCIES / REGISTRY）：按需查明细。
