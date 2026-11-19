# 验证方法目录

每个场景的"第 11 维：如何验证"都从这里取手段。**关键纪律：验证实验必须能证伪你的结论**——既要设计"应失败"的对照组，也要设计"应通过"的正常组，并明确预期观测。

分 **动态（运行时）** 与 **静态（代码/设计）** 两类。

---

## 一、动态验证

### 1.1 并发压测 + 模式校验（通用首选）
- 用 `fio` 对目标 LBA 区间并发两类操作，写入**唯一可校验模式**（如每块填 `LBA 序号 + 写序号 + 随机盐`），读回逐字节比对。
- 组合：
  - W/D 并发：`fio --rw=trimwrite` 或 `randwrite` + `trim`（`--trim_percentage`）。
  - R/D 并发：`randread` + `trim`。
  - Clone/Snap 并发写：建克隆/快照后并发写父/子卷，校验各视图。
- **预期（通过）**：无校验错，各视图自洽。
- **预期（失败）**：校验错、读回旧数据（复活）、已 ack 写不可见（丢失）。

### 1.2 注入延迟放大并发窗口（定位竞态最有效）
- 在目标系统的关键子步骤之间插入人为延迟，强制危险交错稳定复现：
  - 内核态：用 `bpftrace`/`kprobe` 在"映射更新"与"数据提交"间 `msleep`；或在 discard 的 D1/D2 间延迟。
  - 用户态：在 alloc/write/commit、COW 读/写、recovery 读源/写目标 之间插入 sleep/断点。
- **预期（通过，保护有效）**：即使放大窗口仍无丢数据/复活（证明锁/版本真关闭了窗口）。
- **预期（失败）**：延迟一插入就复现丢数据/复活（证明窗口未被保护）。

### 1.3 崩溃 / 掉电注入（崩溃一致性）
- 在并发窗口内触发：VM/节点 reset、断电、`kill -9`、拔盘、网络分区（跨节点场景）。
- 重启后运行：文件系统 `fsck`、卷 `scrub`、EC/副本 `check`、checksum 校验。
- **预期（通过）**：恢复后无悬空引用、无孤儿 extent、无 refcnt 负值、用户数据自洽。
- **预期（失败）**：refcnt 负值、extent 既 FREE 又被引用、已 ack 写丢失、复活数据出现。

### 1.4 断言断点（运行时不变式）
- 在非法状态迁移处下断点/触发 panic-on-bug：
  - `WRITTEN → FREE` 但 `rc > 0`（共享 extent 误释放）。
  - discard 释放时 `rc` 已为 0 或负（double-free）。
  - COW 读到的 extent 已被标记为 RECLAIMING（use-after-free / 复活）。
  - recovery/migration 提交时 version 低于当前（stale overwrite）。
- 配合 1.2 的延迟注入，让断点在危险交错时命中。

### 1.5 跨租户泄露专项（针对"数据复活"）
- 在卷 A 写已知 pattern → discard（不 secure）→ 将同一物理 extent 分配给卷 B/新文件 → 读卷 B 检查是否含卷 A 旧数据。
- **预期（安全）**：卷 B 读到零或新写数据，无旧数据。
- **预期（泄露）**：卷 B 读到卷 A 旧 pattern（跨租户复活，合规硬伤）。

---

## 二、静态验证（代码 / 设计审查）

### 2.1 锁序与持锁范围审查
- 两个并发操作是否对冲突 LBA 区间加**同一把锁**？
- 持锁范围是否覆盖整个危险窗口（alloc→write→commit / COW 读→写→切映射 / discard rc--→释放）？
- 是否有锁序反转导致死锁风险（顺带记录，但本技能聚焦正确性）。

### 2.2 引用计数不变式
- `rc(extent) >= 被引用者数量（卷 + 每个快照/克隆 + COW/Recovery 引用）`。
- discard/释放 是否用 `atomic dec_and_test(rc)==0` 才回收？是否存在"读 rc 后再判断"的非原子 TOCTOU？
- 是否有路径绕过 `rc` 直接物理释放（最危险的实现缺陷）？

### 2.3 持久化顺序审查（崩溃一致性）
- 映射更新 vs 数据释放 vs 清零 的 journal/WAL 顺序是否满足：崩溃后重放能得出确定且正确的终态？
- 快照/克隆元数据提交是否为**单原子事务**（不会"半计入"）？
- recovery/migration/rebuild 的"确定权威版本"是否在提交前 re-check version（防过期覆盖）？

### 2.4 代码审查清单（逐场景）
- [ ] Write/Discard：discard 是否持与 write 同区间锁？基于最新映射？
- [ ] Read/Discard：分配器交付 extent 前是否清零（或 secure discard）？
- [ ] Snapshot/Write：快照提交是否原子？COW 是否在切换前完成旧值拷贝？
- [ ] Snapshot/Discard：discard 是否走 `rc--` 而非直接释放？快照是否 pin？
- [ ] Clone/Write、COW/Write：COW 是否对区间加锁 / 基于固定版本读旧值？
- [ ] Clone/Discard：并发 discard 的 `rc` 操作是否原子 dec_and_test？
- [ ] COW/Discard：COW 是否 pin 住 extent 防止 discard 释放？
- [ ] Recovery/Write、Rebuild/IO：是否以 max(version) 仲裁？提交前 re-check？
- [ ] Recovery/Discard、Migration/IO：恢复/迁移是否 pin extent / 避让 discard？路由切换是否原子？

---

## 三、验证报告格式

每个场景验证后给出：

```
## 验证结论
- 动态：实验X（描述）→ 观测（通过/失败）+ 证据
- 静态：审查点Y → 发现（保护到位/存在缺陷）+ 文件:行号
- 最终判定：丢数据=是/否；复活=是/否；保护机制=有效/缺失
- 未验证：[推测] 级项 + 待补证据
```

> 任何"保护有效"的结论，必须有"放大窗口后仍通过"或"代码审查确认锁/版本覆盖窗口"的支撑；仅"正常跑没报错"不足以证明无竞态。
