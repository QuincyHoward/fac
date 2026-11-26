# FeL 单节点满核场景

把 `demo/FeL` 抽象为可提交超算的单节点满核测试场景；不修改 demo 原始脚本。

- 场景名：`FeL_single_node`
- 入口：`run.py`
- 核心：`fe.py` → `spec.py`
- 资源：1 节点全部核心，核心数由 `nproc` 或 SLURM 自动检测
- 基准：无官方 `ref/`，只做产物完整性与物理合理性检查
- 产物：
  - `data/`：36 个文件，Fe08/Fe09/Fe10 六类表
  - `Fe08/`：210 个文件，`.rt/.sp/.d0`–`.d5`
  - `summary.json`：退出码、文件计数、验证状态

## 一键提交

```bash
python -m scenarios.run.hpc submit --scene FeL_single_node --cores auto -n
python -m scenarios.run.hpc submit --scene FeL_single_node --cores auto
python -m scenarios.run.hpc status --job <ID>
python -m scenarios.run.hpc wait --job <ID>
python -m scenarios.run.hpc download --remote <archive_dir> --local <local_dir>
```

## 2026-11-25 HPC 实测结果

- 作业号：`4973989`
- 核心数：`40`，`USE_MPI=2`，确认启用 FAC 内部并行仿真
- 状态：`COMPLETED`
- `fe_exit=0`、`spec_exit=0`
- `data/` 36 个文件，`Fe08/` 210 个文件
- `summary.json.ok=true`
- 回传摘要：`scenarios/fac_demo/outputs/FeL_single_node_HPC/`

## 已知事项

- 原 `spec.py` 只有 `neles = range(8,9)`，本轮只生成 Fe08 谱表。
- 历史 8 线程实测中 `Fe07b.en` 缺失警告非致命；本次仍按非致命处理。
- 大产物留在 HPC scratch/home，不回传 20 GB 级 `Fe08/`。

父级 [`../../README.md`](../../README.md)。
