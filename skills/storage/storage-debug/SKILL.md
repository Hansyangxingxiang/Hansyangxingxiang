---
name: storage-debug
description: Use when investigating a storage/IO problem — 空间未释放、性能异常、IO 行为不符预期、崩溃或卡死，需要从现象反推根因并设计验证实验时。Not for 纯源码理解（用 storage-code-analysis）或方案设计（用 design-document）。
---

# Storage Debug — 假设驱动，先分层再下钻

## Overview

排障不是乱试，而是**假设驱动**：先分层定位问题在哪一层，再对每个候选根因写可证伪假设，用工具收集证据，最小复现验证。核心产出是**排障记录单**，每条结论带证据。

## When to Use

- 空间未释放（删除/覆盖后空间没回来）
- 性能异常（延迟、吞吐、IO 卡顿）
- IO 行为不符预期（DISCARD 没下发、写放大、顺序变随机）
- 崩溃、卡死、数据不一致
- 需要从现象反推根因并设计验证实验

## 核心方法

### 1. 分层定位法

按层切割问题域，确定问题在哪一层：

```
应用层      → 应用行为、系统调用（strace）
文件系统层  → ext4/xfs 行为、DISCARD 策略（dmesg、mount 选项）
Block Layer → 请求合并/调度、discard 处理（blktrace、iostat）
存储栈      → RBD/QBD/Store 处理（ceph daemon、日志）
驱动/硬件   → NVMe/SSD 行为（nvme-cli、smartctl、dmesg）
```

每层问：这一层的行为与预期是否一致？不一致 → 问题在这一层或更下层。

### 2. 证据收集工具对照表

| 层 | 工具 | 看什么 |
|---|---|---|
| 应用 | `strace -f -e trace=file,ioctl` | 系统调用序列、参数 |
| 文件系统 | `dmesg`、`mount`、`df`、`stat` | 挂载选项、空间统计、错误 |
| Block Layer | `iostat -x`、`blktrace`、`blkdiscard` | 队列深度、IO 大小、discard 请求 |
| 存储栈 | `ceph daemon <osd> dump_ops_in_flight`、`ceph osd tree`、日志 | 请求处理、空间统计 |
| 驱动/硬件 | `nvme list`、`smartctl -a`、`nvme id-ns` | 命名空间、discard 支持、磨损 |

### 3. 假设表法

对每个候选根因写假设表：

| 假设 | 预测的可观察结果 | 验证方法 | 结果 |
|---|---|---|---|
| 假设 A：ext4 没发 DISCARD | mount 选项无 discard，且 blktrace 无 discard 请求 | `mount` 查看选项 + `blktrace` 抓取 | 证实/推翻 |
| 假设 B：RBD 不支持 discard | 下发后空间未释放，Store 无 trim 日志 | `ceph daemon` 查空间 + 日志 | 证实/推翻 |

每个假设必须**可证伪**——能设计实验推翻它。

### 4. 最小复现

- 最小化变量：最小环境、最小操作序列，一次只改一个
- 先复现，再定位；复现不了先缩小范围
- 记录：环境、命令、原始输出

## 排障记录单模板

```
## 现象
- 一句话：<什么操作、什么环境、什么表现、何时开始>

## 分层定位
- 应用层：<证据>
- 文件系统层：<证据>
- Block Layer：<证据>
- 存储栈：<证据>
- 驱动/硬件：<证据>
- 结论：问题在 <层>

## 假设表
| 假设 | 预测 | 验证方法 | 结果 |

## 根因
- 结论：<一句话>
- 证据链：<每步带出处>

## 证据附录
- 命令、日志、源码位置

## 下一步
- 根因确认？→ 交接 storage-design 出方案
- 未确认？→ 交接 storage-architect 研究 / 继续缩小范围
```

## Common Mistakes

- **跳过分层直接猜** — 不定位层就下结论，容易修错地方
- **假设不可证伪** — "可能是缓存问题"没有预测，无法验证
- **一次改多个变量** — 无法归因
- **不记录原始输出** — 证据丢失，无法复核
- **把现象当根因** — "空间没释放"是现象，根因在某一层
