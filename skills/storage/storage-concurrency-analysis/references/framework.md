# 通用分析框架：11 维引导

本文件把 SKILL.md 里的 11 问展开成可执行的分析引导。适用于 14 个内置场景，也适用于**任意未在列表中的新并发场景**（套用 §末尾的"扩展法"）。

---

## 0. 前置：锁定目标系统的并发模型

在答任何一维前，先填好"前置事实表"（见 SKILL.md §前置）。没有它，11 维分析会变成泛泛而谈。至少明确：

- 地址映射：LBA → 物理区段 在哪一层、是否原子更新、是否持久化。
- thin provisioning 下，"逻辑分配（alloc）" 与 "数据写入（write）" 是否两个独立步骤。
- discard/TRIM 的语义：是"建议"（可延迟、可忽略）还是"命令"（必须释放且清零）。
- 快照/克隆/COW 的实现流派：COW（写时复制）还是 ROW（重定向写）/ clone-on-write。
- 副本/EC/重建 的版本来源：谁给数据打 version/generation，恢复时以谁为准。

---

## 1. 操作发生顺序（Operation Ordering）

**目标**：列出 OpA 与 OpB 的**关键子步骤**，再枚举交错。

做法：

1. 把每个操作拆成不可逆的子步骤（不是"开始/结束"两个黑盒）。例如 Write 拆为：
   `W1 分配/定位 extent` → `W2 更新映射表(LBA→phys)` → `W3 数据写入缓冲/落盘` → `W4 提交(ack)`。
2. Discard 拆为：
   `D1 标记逻辑区间为空闲(映射置空)` → `D2 释放物理 extent(引用计数 dec / 回收队列)` → `D3 可选清零`。
3. 枚举交错：至少要列 **3 种**——(a) A 全程先于 B；(b) B 全程先于 A；(c) A 与 B 子步骤交错（这是危险来源）。
4. 若两操作都带子步骤交错，标注哪一步到哪一步构成**危险交错**。

**反模式**：只画"OpA 和 OpB 同时发生"两个方块——这没有定位到窗口。

---

## 2. 数据生命周期（Data Lifecycle）

**目标**：跨两个操作追踪"被波及的数据对象"的生命周期。

标准生命周期轴（thin/COW 系统常见）：

```
分配(alloc) → 写入(buffer/journal) → 落盘(committed) → 被引用(snapshot/clone/share)
            → 被 discard/delete 标记空闲 → 物理回收(reclaim) → 可选清零(zero) → 可被重新分配(reuse)
```

对每个场景，回答：

- 数据对象在 OpA 与 OpB 中分别处于生命周期哪一段？
- 是否存在"OpA 认为数据已落盘、OpB 已将其标记为空闲并可能清零/复用"的对冲？
- 跨租户时：被回收的 extent 是否被清零后才分配给新租户？

---

## 3. 状态变化（State Changes）

**目标**：把"生命周期"落到可调用的**状态机**与**计数**。

常见状态（按需取用）：

- extent 状态：`FREE → ALLOCATED → WRITTEN → SHARED(被快照/克隆共享) → RECLAIMING → FREE`
- 引用计数：`refcnt`：卷自身 1 + 每个快照/克隆 +1；discard 仅当 `refcnt==0` 或"仅本卷引用"时才真正释放物理。
- 卷/快照/克隆状态：`CREATING → ACTIVE → FROZEN(快照瞬间) → DELETING → GONE`
- recovery/migration/rebuild 状态：`IDLE → SCANNING → COPYING → VERIFYING → DONE / ABORTED`

对每个场景，给出：

- 哪些状态会被 OpA / OpB 改变？
- 内存态与持久化态是否一致（崩溃后能否恢复同一状态）？

---

## 4. 并发窗口（Concurrency Window）

**目标**：精确到"哪一步 → 哪一步"的重叠区间。

- 窗口 = OpA 的某关键子步骤 与 OpB 的某关键子步骤 **同时处于未完成** 的区间。
- 例（Write/Discard 危险窗口）：`W2(更新映射)` 完成但 `W3(数据落盘)` 未完成 时，D2(释放物理 extent) 发生 → 写落到已回收 extent。窗口 = `[W2 完成, W3 完成)` 与 `[D1, D2]` 的重叠。
- 若两个操作各自持有互斥锁覆盖整个关键区间，则**窗口被关闭**（无竞态）。分析时必须说清"窗口是否已被某机制关闭"。

---

## 5. 是否存在竞态（Race?）

**输出格式**：`是 / 否 / 条件性（当 X 机制缺失时）` + **竞态类型**。

竞态类型词表（精确使用，不要泛称"有并发问题"）：

- **丢失更新（lost update）**：两写并发，后提交者覆盖先提交者未持久的部分。
- **撕裂写/读（torn write/read）**：写未原子完成，读看到半新半旧。
- **TOCTOU（time-of-check-to-time-of-use）**：先检查状态（如 extent 空闲），再用时状态已被另一操作改变。
- **use-after-free / 读到已释放**：discard 释放后，COW/快照/读仍引用该物理 extent。
- **double-free / 双释放**：Clone/Discard 共用引用计数，并发 dec 导致 extent 被回收两次或计数变负。
- **读未提交（dirty read）**：读到其他操作尚未 ack 的数据。
- **双写覆盖（stale overwrite）**：恢复/重建基于旧版本数据覆盖了客户端新写。
- **幻读（phantom）**：discard 后重新分配，新分配者读到旧数据（跨租户泄露）。

---

## 6. 谁负责保护（Responsibility）

**输出格式**：`层名 + 该层具体职责`，跨层时要指明协调者。

责任层候选：

- **block layer / 设备**：保证 sector 级原子写、discard 语义（如 NVMe DSM）。
- **文件系统 / 卷管理层**：保证 extent 分配与映射更新的原子性、引用计数、快照/克隆语义。
- **副本 / EC 层**：保证多副本/EC 的写一致、恢复版本仲裁。
- **应用 / 上层**：保证更高层语义（如数据库 WAL）。

**禁止**出现"系统保证""内核会处理"这类模糊归属。必须落到某一层的具体动作。

---

## 7. 锁 / 版本 / 状态机制（Protection Primitive）

**目标**：说明具体用什么原语、如何**关闭并发窗口**（对应第 4 维）。

原语清单（选实际使用的，说明粒度与锁序）：

- **区间锁（range/extent lock）**：对冲突 LBA 区间加互斥锁，覆盖 alloc→write→commit 全区间 → 关闭 Write/Discard、Write/Write 窗口。
- **引用计数原子操作（atomic refcount）**：extent 被快照/克隆共享时 `refcnt++`；discard 时 `refcnt--`，仅 `==0` 才回收 → 关闭 Clone/Discard 双释放、Snapshot/Discard 误回收。
- **generation / epoch 版本号**：每次元数据提交递增 generation；恢复/重建以最大 generation 为准 → 关闭 Recovery/Write、Rebuild/IO 的旧数据复活。
- **seqlock / 版本化映射**：读映射用 seqlock 重试，避免读到半更新的映射表。
- **journal / WAL 顺序**：映射更新先于数据释放持久化（严格顺序写），崩溃后重放决定最终状态。
- **租约 / 冻结（freeze）**：建快照瞬间冻结写（短暂加全局/卷级锁或暂停 IO），快照提交后再放行 → 关闭 Snapshot/Write 一致性窗口。
- **COW 顺序约束**：COW 必须在任何可能 discard 旧数据之前，先完成"读旧值并写出新 extent" → 关闭 COW/Discard 复活窗口。

---

## 8. 异常情况下的结果（Abnormal Outcome）

**目标**：在**并发窗口内**注入崩溃/掉电/进程杀/网络分区，推演最终状态。

推演方法：

1. 取第 1 维的危险交错。
2. 在窗口的若干切点（如 W2 后、D2 后、commit 前）插入崩溃。
3. 依据第 3 维的状态机与第 7 维的持久化顺序，推演崩溃恢复后的状态：
   - journal 重放决定映射表最终指向哪块物理 extent；
   - 引用计数是否出现负值 / 孤儿 extent / 双回收；
   - 是否有 extent 既被标记为 FREE 又被某快照引用（悬空引用）。
4. 标注结果属于 `[事实]`（可由恢复逻辑推演）还是 `[推测]`（依赖具体实现未核实）。

---

## 9. 是否可能数据丢失（Data Loss?）—— 必答

**输出格式**：`是 / 否` + **条件**（何种交错 + 何种故障）+ **丢失什么**。

常见丢失形态：

- **写丢失**：Write 在窗口内被 Discard 释放或覆盖，ack 后数据不存在。
- **拷贝错（silent corruption）**：COW/Clone/Snapshot 拷贝了错误/未提交/已释放的旧值，新写入"看似成功"但内容错误（比直接丢失更隐蔽）。
- **覆盖新写**：Recovery/Rebuild/Migration 用旧版本数据覆盖了客户端已确认的新写。

> 注意区分"用户视角的数据丢失"（ack 后读不到）与"内部冗余暂时下降"（如重建中副本数 < N，但数据可读）。后者是可用性风险，前者是正确性灾难。

---

## 10. 是否可能数据复活（Data Resurrection?）—— 必答

**定义**：已逻辑删除 / 释放 / 覆盖的数据，在后续某时刻**重新变得可见 / 可读**，违反"删除即不可恢复"语义。

**输出格式**：`是 / 否` + **复活路径**（哪一步让旧数据重新可见）+ **危害**（跨租户泄露 / 快照固化脏数据 / 旧副本复活）。

典型复活路径：

- **未清零复用**：Discard 释放 extent 后未清零即分配给新租户/新 LBA → 新分配者读到旧数据（幻读 / 跨租户泄露）。`[分析]` 多数 SSD/薄卷默认 discard 不保证清零，依赖上层 zero-fill 或 `secure discard`。
- **COW 固化旧值**：COW/Clone 在 Discard 之后读取"旧数据"做拷贝，把已被释放的旧块内容固化进快照/克隆 → 快照内容变成不确定的旧数据。
- **快照/克隆共享区间复活**：Snapshot/Discard 并发，discard 误释放了仍被快照共享的 extent，快照后续读返回零/旧值。
- **旧副本/旧条带复活**：Recovery/Rebuild 用旧 generation 数据覆盖新写，或重建基于过期条带。

> "数据复活"往往是安全合规（如 GDPR 删除权、跨租户隔离）的硬伤，优先级等同甚至高于"数据丢失"。

---

## 11. 如何验证（Verification）

分**动态**与**静态**两类，且验证实验要能**证伪**你的结论（见 `references/verification.md` 详细目录）。

动态（运行时）：

- 并发压测：两操作并发跑，注入人为延迟放大窗口（如在内核/用户态关键步骤间 `msleep`、用 `bpftrace` 在 D1 与 D2 间插入延迟）。
- 故障注入：在并发窗口内触发崩溃（电源/VM reset）、kill -9、网络分区。
- fio 组合：`fio` 同时跑 `rw=randwrite` 与 `trim`（`trimwrite` 模式），或 `rw=randread` 与 `trim` 并发，检查数据校验（verify）。
- 崩溃一致性：窗口内掉电 → 重启 → `fsck`/scrub/checksum 校验，检查是否丢数据 / 复活。
- 断言断点：在 extent 状态机非法迁移（如 `WRITTEN → FREE` 仍有引用）处下断点。

静态（代码/设计）：

- 锁序审查：两个操作是否对冲突区间加同一把锁，持锁范围是否覆盖整个窗口。
- 引用计数不变式：`refcnt >= 被引用者数量`；`refcnt` 仅 atomic dec 到 0 才回收。
- 持久化顺序审查：映射更新 vs 数据释放 vs 清零 的 journal 顺序是否满足崩溃一致性。
- 代码 review 清单（见 verification.md）。

**必交代预期观测结果**：验证通过时应看到什么（如无 extent 悬空引用、scrub 无校验错、并发 24h 无数据偏差）；验证失败时应看到什么（如读取校验失败、refcnt 负值、旧数据复现）。

---

## 扩展法：套用到列表外的新场景

若用户给出一个不在 14 列表里的并发对（如 `EncryptionKeyRotate / Write`、`Dedupe / Write`、`Compression / Discard`、`QuotaEnforce / Write`），照做：

1. 把新操作拆成关键子步骤（如同第 1 维）。
2. 套用第 2–11 维逐一回答。
3. 重点补两件事：新操作的**状态变化**（第 3 维）与**它引入的新并发窗口**（第 4 维）。
4. 复用 `references/mermaid-templates.md` 的时序图模板表达危险交错。
5. 始终落到目标系统的真实分层与锁（第 6、7 维），不泛泛而谈。
