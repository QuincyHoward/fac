# FeL 核数 / MPI 数矩阵实测结果

日期：2026-11-26  
平台：NC-E，账户 `flash_ssh`，作业目录 `~/<credential_user>/fac/fac`  
场景：`FeL_single_node`  
时限：每个作业 `03:00:00`  
构建：`USE_MPI=2`，HPC Python 3.8.6

## 结果表

| 核数 | MPI | JobID | 状态 | Elapsed | fe wall(s) | spec wall(s) | total wall(s) | 产物 OK |
|---:|---:|---|---|---|---:|---:|---:|---|
| 40 | 40 | 4973989 | COMPLETED | 02:45:15 | 未记录 | 未记录 | 未记录 | True（基线复用） |
| 16 | 8 | 4974612 | COMPLETED | 02:28:47 | 7913.615 | 946.591 | 8860.207 | True |
| 24 | 16 | 4974613 | COMPLETED | 02:16:57 | 7213.612 | 937.020 | 8150.632 | True |
| 40 | 24 | 4974614 | COMPLETED | 02:26:59 | 7817.733 | 934.745 | 8752.479 | True |
| 40 | 32 | 4974615 | COMPLETED | 02:32:48 | 8160.026 | 941.713 | 9101.739 | True |

## 结论

- 所有组合均 `COMPLETED`，`fe_exit=0`、`spec_exit=0`，产物计数一致。
- 推荐组合：`(24 核, 16 MPI)`。
  - FAC 总墙钟 `8150.632 s`，约 `02:15:50`。
  - 相比基线 `(40,40)` 的 `02:45:15`，墙钟约缩短 `18%`。
  - MPI 数小于核数，避免过多 OpenMP 线程争抢 CPU。
- `(40,32)` 反而比 `(40,24)` 慢，说明该算例并非 MPI 数越多越好。
- `(16,8)` 比基线快，但受核数限制，`fe.py` 阶段耗时明显更长。
- `spec.py` 阶段各组合差异很小，加速瓶颈主要在 `fe.py`。

## 资源字段说明

该集群 `sacct` 对 `TotalCPU`、`AveCPU`、`MaxRSS`、`AveRSS` 返回空或 0；本次以 `Elapsed` 与 FAC summary 中的 wall seconds 作为主要耗时依据，并明确记录未提供字段，不做推算。

## 产物一致性

- `data_files=36`
- `data_en/tr/ce/ci/ai/rr` 各 6
- `fe08_files=210`
- `fe08_rt=42`
- `fe08_sp=42`

大产物保留在 HPC 各作业 archive/work 目录；本地只回传 summary 与日志。
