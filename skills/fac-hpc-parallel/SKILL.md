---
name: fac-hpc-parallel
description: This skill should be used when running FAC/PFAC on an HPC cluster, enabling USE_MPI=2, choosing independent SLURM core and FAC MPI counts, submitting isolated parameter matrices in parallel, collecting sacct/FAC timing and artifact checks, and troubleshooting parallel FAC builds or runs.
---

# FAC HPC 并行执行

## 1. 适用范围

用于以下任务：

- 在超算上部署、构建并运行 FAC/PFAC。
- 启用并验证 FAC 内部并行仿真，而不是只启用 `make -j` 并行构建。
- 探索“SLURM 核数”和“FAC MPI 数”的不同组合。
- 并行提交多个彼此独立的物理子场景或参数作业。
- 汇总 SLURM 资源消耗、FAC 内部耗时和产物一致性。
- 排查 `USE_MPI`、`f2cFortran`、`InitializeMPI`、Python 依赖和 sbatch 行尾问题。

## 2. 分层与边界

```text
scenarios/  ->  scenarios/run/  ->  scripts/credentials/
```

- 场景只声明物理任务；`scenarios/run/` 负责执行机制。
- 不在场景或文档中硬编码用户名。通过凭证 `account.username` 解析 `~/<用户名>/fac/fac`。
- HPC SSH 用户名来自 `hpc_accounts.json` 的 `ssh_username`，必须使用完整值，例如 `<user>@NC-E`。
- 不打印密码、令牌或其他敏感信息。

## 3. 两个独立参数

必须严格区分：

| 参数 | 作用 | 入口 |
|---|---|---|
| 核数 `N` | SLURM `--ntasks-per-node=N` 申请的 CPU 数 | `hpc.py --cores N` 或矩阵配置 `cores` |
| MPI 数 `M` | `fac.InitializeMPI(M)` 与 `OMP_NUM_THREADS=M` | `hpc.py --mpi M` 或矩阵配置 `mpi` |

- `M <= N` 通常更合理；`M > N` 只会让线程争抢 CPU。
- `make -j` 使用核数 `N`，不要与 MPI 数 `M` 混用。
- `USE_MPI=2` 必须写入 `sysdef.h`；否则 `InitializeMPI(M)` 可能导致段错误或退化为串行。

## 4. 标准流程

### 4.1 部署

```bash
python scripts/10_deploy/deploy_hpc.py --namespace specx --credential flash_ssh
```

确认目标为 `<remote_home>/<account.username>/fac/fac`。

### 4.2 检查构建并行开关

在每个新构建目录中确认：

```text
sysdef.h: #define f2cFortran 1
sysdef.h: #define USE_MPI 2
```

若缺失，按 `references/error-library.md` 处理。

### 4.3 单作业 dry-run

```bash
python -m scenarios.run.hpc submit --scene <scene> --cores N --mpi M --walltime 03:00:00 -n
```

检查 sbatch 头、job name、`FAC_SLURM_CORES`、`FAC_MPI_THREADS`、场景 `--cores/--mpi` 参数。

### 4.4 并行提交独立矩阵

```bash
python -m scenarios.run.hpc matrix -n
python -m scenarios.run.hpc matrix
```

- 每个组合必须使用唯一 run_id、job name、work/fac_build、work/run、archive 目录。
- 通过一个 SSH 会话依次发送 `sbatch`，避免 SSH 并发；SLURM 侧四个作业并行排队运行。
- 不等待单个作业完成再提交下一个。

### 4.5 统一等待

```bash
python -m scenarios.run.hpc wait-many <JOB1> <JOB2> <JOB3> <JOB4> --timeout 14400
```

### 4.6 汇总资源与产物

```bash
python -m scenarios.run.hpc collect
```

输出：

- `matrix_summary.json`
- `matrix_summary.md`

汇总字段见 `references/matrix-protocol.md`。

## 5. 结果判据

一个组合只有同时满足以下条件才算成功：

- SLURM State 为 `COMPLETED`。
- `fac.exit` 为 `0`。
- `summary.json` 中 `fe_exit=0`、`spec_exit=0`、`ok=true`。
- 产物计数与基线一致或满足场景声明的阈值。
- 对不同组合，产物计数一致；只允许数值差异和非致命警告差异。

## 6. 推荐组合选择

优先按以下顺序判断：

1. 产物一致性全部通过。
2. FAC `total_wall_seconds` 最短。
3. SLURM `Elapsed` 与 FAC wall 接近，排除排队或节点异常。
4. 核数不浪费：比较 `MPI 数 / 核数`，优先选择接近 1 但总墙钟更短的组合。
5. 如果 `TotalCPU`、`AveCPU`、`MaxRSS` 在集群上为空或 0，明确记录为“该集群未提供”，不要自行推算。

本项目当前 FeL 结果见 `references/fel-matrix-results.md`。

## 7. 禁止事项

- 禁止把 `InitializeMPI(M)` 与 SLURM 核数 `N` 混为一谈。
- 禁止在 `USE_MPI` 未定义时运行 FeL 大算例。
- 禁止覆盖已有成功基线的 summary。
- 禁止回传 GB 级产物。
- 禁止在 shell 脚本中使用 CRLF。
- 禁止把密码或 Token 放进命令行、remote URL 或日志。
- 禁止用 `make ref` 覆盖基准表，除非用户明确要求。

## 8. 参考资源

- `references/matrix-protocol.md`：参数矩阵、资源字段与汇总格式。
- `references/fel-matrix-results.md`：本项目 FeL 实测结果与推荐组合。
- `references/error-library.md`：HPC/FAC 并行常见错误与修复。
- `assets/matrix-summary-template.md`：新场景矩阵总结模板。
