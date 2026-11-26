# <场景> 核数 / MPI 数矩阵结果

基线 `(N0,M0)`：`<job_id>`，`<source>`。

## 参数矩阵

| 核数 | MPI | JobID | 状态 | Elapsed | TotalCPU | AveCPU | MaxRSS | fe wall(s) | spec wall(s) | total wall(s) | 产物 OK |
|---:|---:|---|---|---|---|---|---|---:|---:|---:|---|

## 产物一致性

| 组合 | data_files | Fe 文件数 | 其他关键计数 | 警告 | 结论 |
|---|---:|---:|---|---|---|

## 推荐组合

按 FAC 总墙钟时间最短：`(N,M)`。

理由：

- 产物一致性通过。
- 总墙钟最短。
- 核数与 MPI 数比例合理。
- 未出现异常节点或资源统计。

## 备注

- 该集群是否提供 TotalCPU/AveCPU/MaxRSS：
- 大产物保留位置：
- 后续复现命令：
