# 10 WSL 与超算部署经验

本目录记录 FAC 从 Windows 工作区部署到 WSL，再迁移到超算的通用流程与踩坑经验。场景脚本只关注物理场景，本目录只关注部署。

## 1. 当前实测环境

| 项目 | 实测值 |
|---|---|
| WSL 发行版 | `Ubuntu-22.04` |
| WSL 主机名 | `Quincy` |
| Windows 源文件 | 当前 `{fac/}` 项目根 |
| WSL 目标 | `/root/QC/fac/fac` |
| Python | `3.10.12` |
| gcc | `/usr/bin/gcc` |
| gfortran | `/usr/local/bin/gfortran` |
| make | `/usr/bin/make` |

部署前 `env_check.py` 会显示 `pfac.fac/crm/pol/util` 为“不可见”，这是正常的：PFAC 扩展尚未在 WSL 中构建。

## 2. 推荐流程

1. 在 Windows 运行 `deploy_wsl.py`，通过 `wslpath` 自动转换源路径。
2. 在 WSL 目标目录中执行环境检查与构建：优先在 WSL 本地 ext4 路径构建，不要在 `/mnt/e` 直接构建。
3. 构建前完成串行兼容处理：CRLF→LF、`configure`、必要时修正 `sysdef.h` 的 `f2cFortran` ABI 开关。
4. 使用 `make -j<N>` 做受控并行编译；PFAC 非线程安全，Python 层并行必须多进程且输出隔离。
5. 导入检查通过后运行 `demo/make check`。
6. WSL 验证完成后，再将已验证目录同步到超算。
7. HPC/WSL 用户目录统一来自凭证 `account.username`，所有目标路径写作 `~/<用户名>/fac/fac`。

## 3. 关键经验

- `mkdir fac/fac` 失败是因为父目录 `fac` 不存在；应先 `mkdir -p /root/QC/fac/fac`。
- WSL 中 `/root/QC/fac/fac` 对应 root 用户的 `~/QC/fac/fac`，与凭证中填写的 `~/QC/fac/fac` 一致。
- Windows 路径不要硬编码；用 `wslpath` 或脚本的 `--source/--target` 参数。
- 复制用 `cp -a` 保留权限与时间戳；默认 LF，`.bat` 例外 CRLF。
- 不要把 Gitee/PyPI Token 写入远程 URL 或脚本参数；通过 `scripts/credentials` 读取并以环境变量传给工具。
- 构建产物、日志与基准表分离；`make ref` 会覆盖基准，未经物理确认不要使用。

## 4. 常用命令

```bash
python scripts/10_deploy/deploy_wsl.py
python scripts/10_deploy/deploy_wsl.py -n
python scripts/10_deploy/deploy_hpc.py --namespace specx --credential flash_ssh
wsl -d Ubuntu-22.04 -- python3 /root/QC/fac/fac/scripts/01_env_diagnose/env_check.py
```

## 5. HPC 实测经验

- HPC 目标路径为 `<remote_home>/<account.username>/fac/fac`；本次解析为 `/publicfs01/fs1-e/home/scfa2696/QC/fac/fac`。
- SSH 用户名必须使用完整值 `scfa2696@NC-E`，不要拆成 `scfa2696`。
- `configure` 必须具备执行权限；压缩包复制后需 `chmod +x configure config.guess config.sub install.sh mkinsdir.sh`。
- `--with-mpi=omp` 会设置编译链接参数，但当前 `configure` 的模板替换未写入 `sysdef.h`，必须手动将 `#undef USE_MPI` 改为 `#define USE_MPI 2`。
- 必须同时修正 `f2cFortran` ABI 宏，否则 `cfortran.h` 报环境未识别。
- PFAC 扩展应用 `make pfac` 构建，直接 `python setup.py build` 会缺少 `init.h` include 路径。
- HPC 系统 `python3` 为 3.6.8 且无 numpy；FAC 构建与 FeL 场景使用 `/public1/soft/python/3.8.6/bin/python3.8`。

## 6. 并行参数矩阵经验

- SLURM 核数与 FAC MPI 数必须拆开：`--cores N` 控制 CPU 申请，`--mpi M` 控制 `fac.InitializeMPI(M)`。
- FeL 实测推荐 `(24,16)`；更多 MPI 数不一定更快，`(40,32)` 比 `(40,24)` 更慢。
- 多个矩阵作业可以使用独立 job name/run_id/work/archive，通过一个 SSH 会话依次提交，SLURM 侧并行运行。
- 详细结果见 `skills/fac-hpc-parallel/references/fel-matrix-results.md`。

父级 [`../README.md`](../README.md)。
