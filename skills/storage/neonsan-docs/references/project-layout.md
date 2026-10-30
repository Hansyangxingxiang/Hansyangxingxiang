# 历史项目布局参考

部分 NeonSAN 工作区以 qfa / qfcenter / qbd / monitor / ci 子目录分别作为 Git 仓库，顶层 docs 用于本地归档。这只是历史布局，不是当前项目事实。

使用前核实各目录的 Git 根、版本及归档规则。构建目标（如 neonstore、neonsan_tcp_client）必须在当前版本中确认存在及依赖关系，不依据名称推定一个目标覆盖另一个。目标不存在时记录差异，不修改构建配置来迎合示例。
