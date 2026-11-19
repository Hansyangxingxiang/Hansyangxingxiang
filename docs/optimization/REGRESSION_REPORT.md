# 回归报告

本报告区分四类结果：

- **通过（静态）**：由脚本或文件检查得到，可复现。
- **通过（脚本冒烟）**：脚本在临时目录执行，未向仓库写入夹具。
- **未运行 — 需真实客户端**：依赖 Claude Code 的触发、路由或生成质量，本次未执行。
- **未涉及**：超出本次只读范围。

静态通过不代表客户端路由或产出通过；未运行项不得记为通过。

## 一、静态校验

| 项 | 命令 / 方法 | 结果 |
|---|---|---|
| 结构与引用校验 | `python3 scripts/skill_audit.py --check` | 通过：退出码 0，0 error，107 warning（warning 为脱敏提示与项目词提示） |
| 生成物确定性 | `--write` 后再 `--check` | 通过：0 error |
| 脚本语法 | `python3 -m py_compile scripts/skill_audit.py scripts/sync_skills.py` | 通过 |
| 通用规则副本一致性 | 对 10 份 `references/shared-method.md` 计算 SHA-256 | 通过：均为 `935c70e8…70c66a`，与 `shared/references/method-and-evidence.md` 一致 |
| humanizer 体量与模式数 | 行数 + 模式编号计数 | 通过：`SKILL.md` 140 行（≤180）；`references/patterns-catalog.md` 含 24 个模式 |
| 通用资产项目词 | Hans 通用技能与 `templates/test-case-design.md` grep `NeonSAN\|neonsan\|ci/\|CI-1\|CI-2` | 通过：仅剩按技能名路由的允许提及（`design-document`、`test-case-design` 的 Not for、commands 说明） |
| Workflow/Command 对应 | 审计器检查 `commands/<x>.md` ↔ `workflows/<x>/WORKFLOW.md`，技能名可解析 | 通过：4 对全部匹配，无悬空技能引用 |
| 未跟踪文件保护 | `git -C personal-notes status --short` | 通过：`work/neonsan/analysis/2026-11-19-csi-neonsan-clone.md` 仍为 `??`，未 stage、未修改 |
| workbuddy 静态校验 | `validate_v21.py` | 未涉及：workbuddy 未改，本次不运行 |

## 二、脚本冒烟（临时目录）

| 脚本 | 夹具 | 断言 | 结果 |
|---|---|---|---|
| `producing-tech-blog/scripts/md2wx.py` | 含 `<x>`、表格、中文的 Markdown | 退出码 0；`<x>` 被转义；表格保留；生成 `report.json` | 通过 |
| `producing-tech-blog/scripts/blog_lint.py` | 干净夹具 | 退出码 0 | 通过 |
| `blog_lint.py` | 含 deny 词夹具 | 退出码非零且报告命中 | 通过 |
| `blog_lint.py --json` | 报告输出到文件 | JSON 可解析，含 `counts/file/issues/stats/verdict` | 通过 |
| `humanizer-zh/scripts/check_style.py` | 含硬禁令夹具 | 退出码 1 | 通过 |
| `check_style.py` | 干净夹具 / stdin `-` | 退出码 0；stdin 可用 | 通过 |

## 三、逐技能触发用例（已设计，未运行）

每个技能设计 3 个应触发、3 个不应触发、2 个易混淆输入；以下仅为用例设计，**全部未在客户端执行**。

| 技能 | 应触发（3） | 不应触发（3） | 易混淆（2） |
|---|---|---|---|
| `design-document` | 为参数校验改动写设计；写通用 Ceph 功能设计；评审设计方案 | 只排障不写方案；把已有正文排成微信 HTML；纯源码调用链研究 | 与 `writing-neonsan-internals` 的归档边界；与 `storage-concurrency-analysis` 的并发结论归属 |
| `storage-code-analysis` | 读 Ceph 源码解释调用链；核对结构体字段语义；验证提交版本行为 | 只有现象无源码的排障；写方案；写公众号文章 | 与 `storage-debug` 的源码定位；与 `storage-architect` 角色的研究决策 |
| `storage-concurrency-analysis` | Write/Discard 并发是否丢数据；Clone 与 Recovery 竞态；快照与覆盖顺序 | 无并发嫌疑的单点性能问题；纯接口设计；文档归档 | 与 `design-document` 的方案主入口；与 `storage-debug` 的数据不一致初筛 |
| `storage-debug` | 删除后容量不降；IO 延迟异常；空间未释放验证假设 | 只做技术调研；写设计文档；排版文章 | 与 `storage-concurrency-analysis` 的竞态分支；与 `storage-code-analysis` 的源码定位 |
| `test-case-design` | 通用项目三条测试用例；无 CI 源码的验收设计；故障注入用例编排 | NeonSAN `ci/` 框架映射；源码调用链研究；写方案 | 与 `ci-test-case` 的项目补充层；与 `design-document` 的测试设计章节 |
| `humanizer-zh` | 润色保留限定词的段落；去宣传语；检查终稿 AI 味 | 重写技术结论；排版 HTML；从零写文章 | 与 `wechat-tech-article` 的表达优化；与 `producing-tech-blog` 的排版 |
| `producing-tech-blog` | Markdown 转微信 HTML；保留表格与代码的排版；生成双输出 | 文章选题与结构；改写正文；源码分析 | 与 `wechat-tech-article` 的内容边界；与 `humanizer-zh` 的润色 |
| `wechat-tech-article` | 公众号技术文章内容草稿；标题与开头优化；面向读者重组 | 微信 HTML 排版；完整源码研究；设计文档归档 | 与 `writing-project-principles` 的原理主导；与 `producing-tech-blog` 的排版交接 |
| `writing-project-principles` | 项目原理短文；系列规划；原理文章评审 | 公众号排版；单点排障；通用方案设计 | 与 `wechat-tech-article` 的表达分工；与 `writing-neonsan-internals` 的项目规范 |
| `ci-test-case` | NeonSAN `ci/` 用例与 CI-1/CI-2/M 映射；项目框架导航 | 通用项目测试设计；源码研究；方案设计 | 与 `test-case-design` 的通用方法；与 `neonsan-docs` 的文档规范 |
| `neonsan-docs` | NeonSAN 设计/分析文档归档；术语与落盘规范 | 通用技术写作；测试设计；排障 | 与 `design-document` 的方案内容；与 `writing-neonsan-internals` 的写作规范 |
| `writing-neonsan-internals` | NeonSAN 技术原理系列；内部写作规范；图表模板 | 对外公众号发布；通用原理写作；设计文档归档 | 与 `writing-project-principles` 的方法重合；与 `neonsan-docs` 的归档边界 |

组合回归（R19、R23、R24、R25）同样未运行；R23 的静态前置条件（feature-design 含并发节点、bug-analysis 含条件分支）已由文件检查确认。

## 四、回归集执行状态

`docs/skill-regression.md` 中 R01–R29 的状态：

| 范围 | 状态 | 依据 |
|---|---|---|
| R01–R21 | 未运行 — 需真实客户端 | 需要真实路由、源码夹具或脚本运行环境；本次未在客户端执行 |
| R22–R25 | 未运行 — 需真实客户端 | slash command 调用、并发路由、通用/项目测试技能分流 |
| R26 | 通过（静态） | 模式目录 24 个；SKILL 140 行 |
| R27 | 通过（静态） | 10 份副本 SHA-256 一致 |
| R28 | 通过（静态） | `--check` 退出码 0、0 error |
| R29 | 通过（静态） | command ↔ workflow 4 对匹配，技能引用可解析 |

微信客户端预览：未验证。workbuddy 的 `validate_v21.py`：未涉及（workbuddy 未改）。

## 五、未运行项与限制

- 所有依赖 Claude Code 客户端触发、路由与产出质量的用例均未运行，不能据此宣称技能发现或回答质量通过。
- 脚本冒烟只验证接口行为与转义，不验证排版视觉效果与微信客户端兼容性。
- 静态脱敏为模式匹配，107 条 warning 需人工复核；0 error 不等于绝对无敏感信息。
- 本次未同步 `~/.claude/`，客户端实际加载内容仍是修改前版本。
