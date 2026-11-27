# HPC 提交说明

本目录只用于可选高精度路径。基线不透明度后处理不需要 HPC。

## 何时提交

| 路径 | 计算量 | 是否提交 HPC |
|---|---|---|
| `build` + `validate` + `plot` | 顺序读取约 4.5 GB ASCII，分钟级 | 否 |
| `dense-pi`（`TotalPICross`） | 读二进制 RR + 少量能级，需 PFAC | 建议 HPC/WSL 短作业 |
| `RRTable` 重算 | 与 FeL `fe.py` 同量级，参考 7213.612 s | 必须 HPC |

## 推荐组合

沿用 FeL 实测推荐组合：`24 核 / 16 MPI`，`USE_MPI=2`，短作业模板时限 `00:30:00`；若改为 `RRTable` 重算，时限改为 `03:00:00`。

核数 `N` 与 MPI 数 `M` 分属不同参数：SLURM 申请 `--ntasks-per-node=N`，FAC 内部 `fac.InitializeMPI(M)`。不要混淆。

## 提交命令

```bash
python -m scenarios.run.hpc submit --scene FeL_opacity --cores 24 --mpi 16 -n
python -m scenarios.run.hpc submit --scene FeL_opacity --cores 24 --mpi 16
python -m scenarios.run.hpc status --job <JOB_ID>
python -m scenarios.run.hpc wait --job <JOB_ID>
```

场景目录由 `scene.json` 自动发现，无需在 Python 中硬编码绝对路径。

## 归档规则

只回传 `outputs/tables/*.csv`、`outputs/figures/*.png`、`outputs/*metadata.json`、`outputs/validation.json` 和 `outputs/summary.json`。不回传 GB 级 FeL 原始产物，也不覆盖已有成功摘要。
