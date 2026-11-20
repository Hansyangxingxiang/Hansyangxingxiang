# 文档类型路由

本文件只负责“任务 → 模板 → 内容技能 → 元数据要求”的路由，不复制模板章节清单。章节结构以 `templates/` 为唯一权威；已安装技能使用 `assets/templates/` 的生成副本。

## 一、共同格式与独立章节结构

所有文档类型共享正文格式规则：标题层级、编号、空行、列表、表格、代码围栏、链接与引用、术语、元数据、事实/推断分离。这些规则以 `references/markdown-style-guide.md` 为唯一权威源。

章节结构不共享：

- 设计文档、源码分析、RCA、技术原理、性能分析、计划台账各自保留模板定义的专属结构。
- 统一 Markdown 格式不等于统一章节顺序；不得为了“格式一致”把一种文档类型改写成另一种结构。
- 计划台账与最终技术文档是不同文档类型：台账记录范围、步骤、进度、验证与回滚；最终文档记录已验证的架构、机制、流程、并发、异常与取舍。二者不共用同一章节骨架，最终文档不复制台账清单。

## 二、路由表

| 文档类型 | canonical 模板 | 已安装副本 | 内容/方法技能 | 元数据 |
|---|---|---|---|---|
| 软件架构设计 | `templates/design-document.md` | `assets/templates/design-document.md` | `design-document` | 必需 |
| 源码分析 | `templates/source-analysis.md` | `assets/templates/source-analysis.md` | `storage-code-analysis` | 建议 |
| 故障 RCA | `templates/incident-rca.md` | `assets/templates/incident-rca.md` | `storage-debug` | 必需 |
| 项目分析归档（8 槽） | `templates/bug-analysis.md` | `assets/templates/bug-analysis.md` | `neonsan-docs` | 必需 |
| 性能分析 | `templates/performance-analysis.md` | `assets/templates/performance-analysis.md` | `storage-debug` + `design-document` | 必需 |
| 技术原理 | `templates/technical-principles.md` | `assets/templates/technical-principles.md` | `writing-project-principles` | 建议 |
| 技术博客 / 公众号草稿 | `templates/technical-article.md` | `assets/templates/technical-article.md` | `wechat-tech-article` | 可选 |
| 实施计划（正式交付物） | `templates/implementation-plan.md` | `assets/templates/implementation-plan.md` | `plan-driven-development` / 用户 | 必需 |
| 计划与执行台账 | `templates/plan-driven-development.md` | `assets/templates/plan-driven-development.md` | `plan-driven-development` | 必需 |
| 测试用例设计 | `templates/test-case-design.md` | `assets/templates/test-case-design.md` | `test-case-design` | 必需 |

`assets/templates/` 由 `scripts/skill_audit.py --write` 从 canonical 生成，带固定“Generated; do not edit”头；`--check` 校验字节一致。不要手工编辑副本。

## 三、规模选择

- 完整模式：用于跨模块改造、对外评审、需要长期维护的文档。
- 轻量模式：用于局部参数校验、单模块小改动；只保留问题、方案、影响、验收与风险。
- 不因“模板有这一章”而填写无关内容；合并章节时在元数据或开头说明。

## 四、元数据要求

必需键：`文档类型`、`状态`、`适用版本`、`证据基线`、`最后核验`。

按类型追加：

| 类型 | 追加键 |
|---|---|
| 实施计划 / 计划与执行台账 | `计划范围` |
| RCA / 项目归档 | `事件日期`、`处置状态` |
| 评审材料 | `评审对象`、`评审结论` |
| 技术原理 | 可选 `系列`、`前置阅读`、`本文范围` |
| 技术博客 | 可选 `读者`、`发布渠道` |

未知值写 `待补充` 或 `未核验`。不根据文件时间推断日期，不编造作者、版本、commit 或审批状态。

## 五、编号与结构例外

- 默认：H2 使用 `1.`、`2.` 连续编号；H3 使用 `1.1`、`1.2`。
- `bug-analysis.md` 保持 8 个无序归档槽位，不强制编号。
- 附录、参考、实现参考、术语表、修订记录、检查清单可以不编号，放在正文之后。
- 既有文档已形成稳定编号体系时优先保留；迁移模板需给出旧→新章节映射。

## 六、路由判断

- 先判断任务属于“设计 / 分析 / 排障 / 性能 / 原理 / 博客 / 计划 / 测试”。
- 再选择内容技能；格式与结构遵循本技能。
- 项目归档同时受项目技能约束；项目专有角色、术语与落盘规则不在本文件。
- 需要正式 RCA 时用 `incident-rca.md`；需要项目 8 槽归档时用 `bug-analysis.md`。两者不互相替代。
- 不确定时先问用户目标读者与用途，再选模板。
