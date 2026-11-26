# 参数矩阵与资源记录协议

## 1. 参数命名

每个组合记为 `(N,M)`：

- `N`：SLURM CPU 核数，`#SBATCH --ntasks-per-node=N`。
- `M`：FAC MPI/线程数，`fac.InitializeMPI(M)`、`FAC_MPI_THREADS=M`、`OMP_NUM_THREADS=M`。

作业名：

```text
fac_<scene>_<N>c_<M>m
```

run_id：

```text
<scene>_c<N>m<M>
```

## 2. 作业隔离

每个组合必须拥有独立：

- job name
- run_id
- `work/fac_build`
- `work/run`
- `archive`

不得复用或覆盖其他组合目录。

## 3. 提交协议

1. 本地 dry-run 渲染所有作业脚本。
2. 检查每个脚本的 `--time`、`--ntasks-per-node`、`FAC_MPI_THREADS`、`OMP_NUM_THREADS`、场景参数。
3. 打开一个 SSH 会话。
4. 在该会话内依次执行多条 `sbatch`。
5. 保存 job_id 清单。
6. 统一轮询所有 job_id。
7. 统一回传/summarize。

## 4. 记录字段

SLURM：

- JobID
- JobName
- State
- ExitCode
- Elapsed
- TotalCPU
- AveCPU
- MaxRSS
- AveRSS
- NodeList

FAC：

- fe_exit
- spec_exit
- ok
- fe_wall_seconds
- spec_wall_seconds
- total_wall_seconds
- data_files
- data_en/tr/ce/ci/ai/rr
- fe08_files
- fe08_rt/sp

产物一致性：

- 与基线计数一致。
- 无 Traceback。
- 非致命警告单独记录，不直接判失败。

## 5. 汇总文件

- `matrix_jobs.json`：作业清单。
- `matrix_summary.json`：机器可读合并结果。
- `matrix_summary.md`：人类可读表格与推荐组合。
