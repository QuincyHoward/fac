# FeL 核数 / MPI 数矩阵结果

基线 `(40,40)` 直接复用，不重跑。计时口径：
- SLURM：`sacct` Elapsed / TotalCPU / AveCPU / MaxRSS / AveRSS / ExitCode / NodeList / State
- FAC：`summary.json` 中 fe/spec/total wall seconds
- 产物一致性：`data_files=36`、`fe08_files=210`、`fe_exit=0`、`spec_exit=0`

| 核数 | MPI | JobID | 状态 | Elapsed | TotalCPU | AveCPU | MaxRSS | fe wall(s) | spec wall(s) | total wall(s) | 产物 OK |
|---:|---:|---|---|---|---|---|---|---:|---:|---:|---|
| 40 | 40 | 4973989 | COMPLETED | 02:45:15 | 00:00:00 |  |  |  |  |  | True（复用） |
| 16 | 8 | 4974612 | COMPLETED | 02:28:47 | 00:00:00 |  |  | 7913.615 | 946.591 | 8860.207 | True |
| 24 | 16 | 4974613 | COMPLETED | 02:16:57 | 00:00:00 |  |  | 7213.612 | 937.02 | 8150.632 | True |
| 40 | 24 | 4974614 | COMPLETED | 02:26:59 | 00:00:00 |  |  | 7817.733 | 934.745 | 8752.479 | True |
| 40 | 32 | 4974615 | COMPLETED | 02:32:48 | 00:00:00 |  |  | 8160.026 | 941.713 | 9101.739 | True |

基线摘要：`scenarios/fac_demo/outputs/FeL_single_node_HPC/summary.json`
基线 JobID：`4973989`

## 推荐组合

按 FAC 总墙钟时间最短：核数 `24`，MPI 数 `16`，JobID `4974613`。

