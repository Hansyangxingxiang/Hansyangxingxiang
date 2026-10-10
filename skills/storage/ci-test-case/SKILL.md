---
name: ci-test-case
description: Use when writing NeonSAN 自动化测试用例设计文档 — 基于 ci/ pytest 框架，把功能/场景落成带详细步骤与每步预期结果的用例设计。产出中文用例设计文档（本地 md / wiki）。Not for 直接写 pytest 代码（本 skill 只产出设计文档）或排障（用 storage-debug）。
---

# CI Test Case — 基于 ci/ pytest 框架的自动化测试用例设计

## Overview

本 skill 解决"一个功能 / 场景如何形成一份完整、可执行、可评审的自动化测试用例设计文档"。核心产出是**带详细步骤与每步预期结果的用例设计文档**（8 章结构），每条步骤与断言基于 ci/ pytest 框架的真实原语（`file:line` 实读复核），不凭空写。

用例设计文档是**可执行契约**：步骤具体到 API / 命令 / 故障注入，预期结果可判定（退出码 / allocated 变化 / 日志串 / MD5），并给出 CI 框架映射（可自动化 vs manual）。

**边界**：本 skill 只产出用例设计文档，不直接写 pytest 代码。实现轮（把设计落成 `ci/test_case/tests/functional/...` 下的 pytest 文件）是另一任务。

## When to Use

- 为存储功能 / 优化设计自动化测试用例
- 把抽象场景表（如 wiki 设计页 §8）落成带步骤与断言的用例
- 给出 CI 框架映射：哪些可自动化（CI-1 / CI-2）、哪些需 manual runbook（M）
- 需要一份可评审、可交给实现轮执行的用例设计

Not for 直接写 pytest 代码（本 skill 只产出设计文档）或排障（用 storage-debug）。

## 核心方法（5 步）

### 1. 先摸清框架原语（复用清单）

- 用 Grep / Read 实读 ci 框架，建立「复用清单」：框架已有什么、需新增什么封装。
- 区分「框架已有」与「需新增封装」——新增封装随用例文件提供，不改框架文件。
- **不信任记忆中的行号**：每个 `file:line` 必须重新 Grep 验证（行号会漂移）。

### 2. 建立覆盖对照

- 需求 / 场景 ↔ 用例 ID ↔ 级别（CI-1 / CI-2 / M）三列对照表。
- 保证无遗漏：源场景表每一行、每个场景号都有落点；缺行显式补上并标注。
- 级别定义：
  - **CI-1**：纯 API + 客户端命令可自动化的 pytest 用例（第一批实现）
  - **CI-2**：需要 FaultStore 故障注入的 pytest 用例（第二批实现）
  - **M**：manual runbook，按第 5 章原始命令手工执行

### 3. 逐用例写「目的 / 前置 / 步骤 / 断言」

- 每条用例独立成节，格式见下「用例格式」。
- 步骤可执行：具体到 API 方法 / 命令 / 故障注入，不写"验证一下"这类空动作。
- 断言可判定：退出码 / allocated 变化 / 日志串 / MD5，不写"应该正常"这类空断言。

### 4. 标注级别与实现注

- 每条用例标注级别（CI-1 / CI-2 / M）。
- 实现注记录：依赖的框架原语、易错点、为何该断言成立、与既有用例的衔接。

### 5. 补 runbook 与验收矩阵

- Manual runbook：store 日志 grep 清单、直调库工具接口、迁移 / failover / 混布 / 注入的手工编排步骤。
- 验收矩阵：源验收标准 ↔ 覆盖用例，标注缺口。

## 用例设计文档结构（8 章）

```
1. 概述与范围        — 解决什么问题 / 交付边界 / 覆盖对照表（场景↔用例↔级别）
2. 测试环境与前置条件 — 集群与 bundle / 客户端节点要求 / 命名与 teardown 约定
3. 框架原语映射与新增封装 — 复用清单（file:line）/ 需新增的封装（代码片段）
4. 用例详单          — 按功能域分节，每条用例「目的/前置/步骤/断言/级别/实现注」
5. Manual runbook   — store 日志 grep 清单 / 直调库工具接口 / 迁移 / failover / 混布 / 注入
6. 验收矩阵          — 源验收标准 ↔ 覆盖用例，标注缺口
7. 差异与修正建议    — 源场景表与实现的差异、覆盖缺口、回填执行约定
8. （可选）覆盖缺口   — 源场景表缺行、需补的用例
```

## 用例格式

每条用例固定字段：

- **目的**：一句话，验证什么（带源场景引用，如 wiki 8.2-1 / §10.2 #1）。
- **前置**：环境 / bundle / 参数前提（如对象大小已查、`qbd_trim=1`）。
- **步骤**：编号列表，每步一个具体动作（API 方法 / 命令 / 故障注入）。
- **断言**：编号列表，每步预期结果，可验证判定（退出码 / allocated 变化 / 日志串 / MD5）。
- **级别**：CI-1 / CI-2 / M。
- **实现注**：依赖原语、易错点、断言成立前提、与既有用例衔接。

## ci 框架原语映射表

> 行号需实读复核（本表为导航锚点，不替代 Grep 验证）。

| 能力 | 复用 | 出处 |
|---|---|---|
| 卷管理 | `create_volume` / `list_volume` / `delete_volume` | `test_case/services/neonsan_api/api/client/center.py:1502` / `:1534` / `:1584` |
| 快照管理 | `create_snapshot` / `delete_snapshot` / `list_snapshot` | center.py:1228 / :1255 / :1311 |
| 克隆管理 | `clone_volume` / `detach_clone_relationship` | center.py:1843 / :1877 |
| 池管理 | `create_pool` / `list_pool` | center.py:656 / :681 |
| 对象大小 | `get_volume_objsize` | center.py:1756 |
| 数据写读校验 | `write_files_to_block` / `read_file_from_block_device` / `check_file_md5_block` | `test_case/services/data_verification/data_set_manage.py:475` / `:922` / `:1056` |
| 块设备 | `QBDDevice.map/unmap/mkfs/mount/umount/remap` | `test_case/services/qbd/qbd_device.py:149` / `:172` / `:55` / `:64` / `:100` / `:184` |
| 故障注入 | `FaultStore.stop_store/start_store/disconnect_port/disconnect_rep_port/network_delay/insert_disk/inject_ssd_io_err/inject_ssd_io_timeout/inject_dispatcher_hang/disconnect_peer` | `test_case/services/fault_injection/fault_injection.py:567` / `:580` / `:54` / `:81` / `:135` / `:345` / `:606` / `:619` / `:632` / `:657` |
| 远程执行 | `SSHExecutor.connect/execute` | `test_case/services/excutor/executor.py:100` / `:151` |
| CLI | `NeonSANCLI.neonsan_cli` | `test_case/tools/neonsan_cli.py:9` |
| fio | `NEONFIO.neonfio` | `test_case/tools/neonfio.py:13` |
| 协议常量 | `QBD_PROTOCOL_TYPE_TCP` / `QBD_PROTOCOL_TYPE_RDMA` | `test_case/services/neonsan_api/const/qbd.py:1-2` |

## 步骤与预期结果方法论

- **步骤可执行**：具体到 API 方法 / 命令 / 故障注入，不写空动作。
- **预期结果可判定**：退出码 / allocated 变化 / 日志串 / MD5，不写空断言。
- **空间断言统一走 volume_allocated**：`list_volume(name, pool_name, stat_rep=True)["volumes"][0]["volume_allocated"]`；`stat_rep=True` 强制 center 先做 StatReplica 收实时值，绕开最长 5 分钟的 replica_usage 缓存。
- **短轮询容忍 statLock 竞态**：并发 StatReplica 会使 statLock.TryLock 跳过返回旧值 → 断言处用短轮询重试而非单次调用。
- **区分硬断言与软断言**：硬断言（退出码 / 数据 MD5 / allocated 变化）必须成立；软断言（日志串 / 池级 used 下降）标注"软断言"，允许噪声与延迟。

## Common Mistakes

- **凭记忆写行号** — 行号会漂移，必须重新 Grep / Read 验证。
- **步骤不可执行** — 写"验证一下"而非具体 API / 命令 / 故障注入。
- **预期结果不可判定** — 写"应该正常"而非退出码 / allocated 变化 / 日志串 / MD5。
- **不建覆盖对照** — 源场景表有行无落点，或漏了缺行。
- **把实现当设计** — 本 skill 只产出用例设计文档，不写 pytest 代码。
- **不区分级别** — 未标注 CI-1 / CI-2 / M，实现轮无法排批次。
