# Mermaid 并发表达模板

用于表达并发场景的**危险交错**与**保护机制**。只在"图能比文字更清楚地说明窗口"时才画。通用约定：

- `sequenceDiagram`：表达两个操作的子步骤交错；用 `Note over` 标注**并发窗口**与**危险点**；用 `rect` 包裹**持锁区间**。
- `stateDiagram-v2`：表达 extent / 卷 / 恢复状态机。
- 颜色仅用 Mermaid 原生（如 `rect rgb(...)`），不要依赖外部样式。

---

## 模板 A：Write / Discard（危险窗口标注）

```mermaid
sequenceDiagram
    participant W as Write(客户端)
    participant D as Discard(回收)
    participant M as 映射表/分配器

    W->>M: W2 更新映射 LBA→phys_p
    Note over W,M: 写未落盘，phys_p 仍被本卷引用
    rect rgb(255,240,240)
        Note over W,D: ⚠️ 并发窗口：[W2完成, W3完成) ∩ [D1,D2]
        D->>M: D1 标记逻辑区间空闲
        D->>M: D2 释放 phys_p (rc-- → 0)
        W->>M: W3 写数据到 phys_p（已被回收/复用！）
    end
    Note over W,M: 结果：写落到已回收 extent → 写丢失 / 写他人空间
```

**保护后**（区间锁关闭窗口）：

```mermaid
sequenceDiagram
    participant W as Write
    participant D as Discard
    W->>W: 加 L(LBA) [覆盖 alloc→write→commit]
    W->>W: 写完成并 ack
    W->>W: 释放 L(LBA)
    D->>D: 请求 L(LBA) → 阻塞直到 W 释放
    Note over D: 写完成后才释放/回收 → 窗口关闭
```

---

## 模板 B：Snapshot / Write（快照点一致性）

```mermaid
sequenceDiagram
    participant C as 客户端写
    participant S as Snapshot 提交
    participant V as 版本指针/元数据

    C->>V: W 更新映射(基于 gen=N)
    rect rgb(255,250,230)
        Note over S,V: 快照提交临界区（应原子）
        S->>V: 原子切换 当前版本指针 → 新快照(gen=N+1)
    end
    Note over C,S: 危险：若切换非原子，某写可能半计入快照
    S->>V: 快照固定引用 gen≤N 的旧值（COW 流派先拷贝）
```

---

## 模板 C：COW / Discard（数据复活高发区）

```mermaid
sequenceDiagram
    participant COW as COW(读旧值→写新extent)
    participant D as Discard
    participant E as 物理 extent

    COW->>E: 读旧值(准备拷贝到快照)
    rect rgb(255,235,235)
        Note over COW,D: ⚠️ 复活窗口：COW 读 vs D 释放
        D->>E: 释放 extent(rc-- 误判为0)
        D->>E: 清零/复用 extent
        COW->>E: 读到 零/他人数据（旧值已消失）
    end
    COW->>COW: 把脏值固化进快照/克隆
    Note over COW: 结果：已释放数据以错误形式"复活"进快照
```

**保护后**（COW pin 住 extent）：

```mermaid
sequenceDiagram
    participant COW as COW
    participant D as Discard
    COW->>COW: pin(extent) / 加 L(range)
    COW->>COW: 读旧值 → 写新 extent → 切映射
    COW->>COW: unpin
    D->>D: 请求释放 → 见 pin/rc>0 → 避让
```

---

## 模板 D：Migration / IO（路由不一致）

```mermaid
sequenceDiagram
    participant IO as 客户端 IO
    participant R as 路由表
    participant S as 源端
    participant T as 目标端

    IO->>R: 提交写 W
    R->>S: 写源端（迁移中：双写或重定向）
    rect rgb(255,240,240)
        Note over IO,R: ⚠️ 危险：写落到旧端 且 路由已切到目标端
        IO->>S: W 写源端（未同步目标端）
        R->>R: 切换路由 → 指向目标端
        IO->>T: 后续读 → 目标端无 W → 读到旧值（复活）/ W 丢失
    end
```

---

## 模板 E：extent 状态机（通用）

```mermaid
stateDiagram-v2
    [*] --> FREE
    FREE --> ALLOCATED: 分配(alloc)
    ALLOCATED --> WRITTEN: 数据提交
    WRITTEN --> SHARED: 被快照/克隆引用(rc++)
    SHARED --> WRITTEN: 断共享(COW/rc--)
    WRITTEN --> RECLAIMING: discard(rc==0)
    SHARED --> RECLAIMING: discard(rc 降至0)
    RECLAIMING --> FREE: 回收(可选清零)
    RECLAIMING --> WRITTEN: 取消回收(并发撤销)
    note right of RECLAIMING
        危险：仍被引用(含COW/Recovery)时
        不得进入 FREE，否则 use-after-free / 复活
    end note
```

---

## 使用纪律

- 每个时序图必须标出**并发窗口**（哪个子步骤区间重叠）与**危险点**（哪一步导致丢数据/复活）。
- 配一张"保护后"图说明窗口如何被锁/版本/引用关闭。
- 状态机图只画与目标场景相关的状态与迁移，避免堆砌。
- 图中角色名要对应目标系统的真实组件（block / FS / 卷管 / 副本层），不要停留在抽象 W/D。
