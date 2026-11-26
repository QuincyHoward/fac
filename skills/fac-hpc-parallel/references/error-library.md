# HPC FAC 并行错误库

## SSH

- `AuthenticationException`：确认使用完整 SSH 用户名，例如 `<user>@NC-E`，不要拆成 `<user>`。
- `gaierror`：IPv6 线路不可达，换用 IPv4 线路。
- `TimeoutError`：线路超时，继续尝试下一条。

## sbatch

- `Batch script contains DOS line breaks`：作业脚本必须以 LF 写入。
- `Invalid account or account/partition combination`：SLURM 计费账户不是凭据名；账户取装置默认值。
- `job name/run_id 冲突`：每个组合必须使用唯一 job name 和 run_id。

## 构建

- `./configure: Permission denied`：执行 `chmod +x configure config.guess config.sub install.sh mkinsdir.sh`。
- `cfortran.h: Can't find your environment`：把 `sysdef.h` 中 `#undef f2cFortran` 改为 `#define f2cFortran 1`。
- `USE_MPI` 仍为 `#undef`：`configure --with-mpi=omp` 后必须手动把 `sysdef.h` 改为 `#define USE_MPI 2`。
- `python/fac.c: fatal error: init.h`：使用 `make pfac`，不要裸运行 `python setup.py build`。
- `No module named numpy`：系统 Python 3.6 无 numpy；改用 HPC Python 3.8.6 或已带 numpy 的解释器。
- `make -j` 只加速构建，不代表运行时并行；必须检查 `USE_MPI=2` 与 `InitializeMPI(M)`。

## 运行

- `fe.py` 段错误且 `USE_MPI` 未定义：禁止继续，重建。
- 总墙钟异常长：检查是否误把核数与 MPI 数混用，或 `OMP_NUM_THREADS` 未设置。
- `TotalCPU/AveCPU/MaxRSS` 为空或 0：记录为该集群未提供，不自行推算。
- 部分产物存在但 `fe_exit != 0`：不得判成功。
- `Fe07b.en does not exist`：FeL 历史非致命警告；单独记录，不直接判失败。

## 产物回传

- 默认只回传 summary、exit、日志、小日志。
- 不回传 GB 级 `Fe08/`、`data/*.tr`。
- 大产物保留在 HPC archive/work 目录，供后续物理分析。
