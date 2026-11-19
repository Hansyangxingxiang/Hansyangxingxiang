# Skill 统一规范

本文件定义本仓库 Skill / Workflow / Template 的统一约定。新增或修改技能时以此为准，并用 `scripts/skill_audit.py --check` 做静态校验。

## Frontmatter

必填：

| 字段 | 要求 |
|---|---|
| `name` | kebab-case，且与技能目录名完全一致 |
| `description` | 非空；写清"什么时候用"与"什么时候不用"（至少一个 `Not for` / `不用于` / `不负责` / `不适用` 子句） |

允许的可选字段：`allowed-tools`、`metadata`、`license`。其他字段会被告警。

`description` 是技能是否被触发的唯一依据，应写触发语义，不写功能摘要。长度建议不超过 1024 字符，硬上限 1536。

## 主文件结构

推荐顺序（缺失会告警，不强制全部出现）：

1. `Overview`：这个技能解决什么问题。
2. `When to Use / NOT`：触发与不适用场景，指名相邻技能。
3. `核心方法` / `执行流程`：可执行的步骤与判断标准。
4. `与其他技能协作`：上下游与交接点。
5. 输入、交付与完成条件：只写本技能特有内容，通用规则引用 `references/shared-method.md`。
6. `参考资源`：references / scripts / templates 的加载时机。
7. 可选 `来源与维护`。

体量预算：主 `SKILL.md` 建议 ≤ 300 行；单个 reference 建议 ≤ 400 行。超长时优先拆分到 `references/` 按需加载，而不是删除内容。

## References / Scripts / Assets

- `references/`：方法、清单、案例、项目配置；主文件说明"何时读哪一份"。
- `scripts/`：可执行辅助；只依赖标准库时在文件中注明 Python 版本；不得硬编码机器路径或密钥。
- `assets/`：模板与示例文件。
- 相对路径必须能从所属文件解析；跨仓库引用不得写文件路径，按**技能名**交接。

## 证据分级

统一四级：**事实 / 推断 / 建议 / 待验证**。既有 `分析` 映射为 `推断`，`推测` 映射为 `待验证`；仅统一语义，不批量改写既有文本。

通用规则（证据分级、`file:line` 本轮实读、输入不足、交付与证据复用、稳定性优先级）只在 `shared/references/method-and-evidence.md` 维护，生成到各技能的 `references/shared-method.md`。**不要在 SKILL.md 重复这些段落。**

## 一条规则一处定义

同一规则只在唯一权威位置定义，其他位置引用：

- 通用方法与证据规则 → `shared/references/method-and-evidence.md`。
- 项目专属术语与流程 → 项目仓库（如 `personal-notes`），通用技能不得写入。
- 输出结构 → `templates/`，技能只负责方法与判断。
- 编排顺序 → `workflows/`，命令只负责入口与阶段委托。

## Workflow 与命令

- `workflows/<name>/WORKFLOW.md` 是编排说明，Claude Code **不会自动发现**。
- 每个 Workflow 必须配 `commands/<name>.md` 作为显式入口；命令 frontmatter 只使用 `description` 与可选 `argument-hint`，正文用 `$ARGUMENTS` 并委托 WORKFLOW.md 的阶段。
- 命令不得复制整份 Workflow 正文。

## 命名与改名

- 目录名 = `name` = kebab-case。
- 改名必须同步所有引用（Workflow、commands、docs、其他技能的协作说明），并单独成一个 commit。

## 校验

```bash
python3 scripts/skill_audit.py --check
python3 scripts/skill_audit.py --write   # 重新生成 registry / inventory / dependencies / shared-method 副本
```

静态检查通过不等于客户端触发与产出已验证；真实触发与组合回归见 `docs/skill-regression.md`。
