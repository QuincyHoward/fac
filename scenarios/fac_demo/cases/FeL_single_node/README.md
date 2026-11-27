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

## 绘图与报告

- [`plots/`](plots/)：Python3 绘图脚本与 HPC 产物/温度回传脚本；温度由 `get_tgrid(26,8)` 导出。
- [`figures/`](figures/)：全套图像，英文标注、Times New Roman、字号 >18pt。
- [`artifacts/`](artifacts/)：Job 4974613 的全量产物，本地保留。
- [`hpc_jobs/`](hpc_jobs/)：矩阵作业清单与汇总。
- - [`FeL仿真报告.html`](FeL仿真报告.html)：自包含 HTML 报告。
- [`fac与文献对比图分析报告.html`](fac与文献对比图分析报告.html)：文献截取图与 FAC 不透明度/PI 图的并列与叠加对照报告。

## 不透明度谱子场景

[`opacity/`](opacity/README.md) 直接复用本目录的 `artifacts/FeL_single_node_c24m16/` 产物，合成 10–18 Å 不透明度谱与透过率；基线本地后处理，不做 `make check`。文献 PDF 已统一重命名并转换为 Markdown，通读笔记见 [`refs/mds/reading_notes.md`](refs/mds/reading_notes.md)。

[`opacity_full/`](opacity_full/README.md) 为 full-physics 升级场景：打开 bound-bound、Voigt 线型、密集 PI 与示例级 AI/DR 共振，重计算阶段通过顶层 [`FeL_opacity_full`](../FeL_opacity_full/) HPC wrapper 提交。

复现：

```bash
python plots/fetch_fel_artifacts.py --job 4974613 --skip-existing
python plots/fetch_fel_abund.py --remote-run <remote_run> --remote-build <remote_build>
python plots/fetch_fel_temps.py --remote-run <remote_run> --remote-build <remote_build>
python plots/plot_all.py
```

## 参数矩阵（2026-11-26）

四组独立作业已并行提交并全部完成；基线 `(40,40)` 复用未重跑。详细结果见 [`../../outputs/FeL_single_node_HPC/matrix_summary.md`](../../outputs/FeL_single_node_HPC/matrix_summary.md)。

推荐组合：`(24 核, 16 MPI)`，FAC 总墙钟 `8150.632 s`，约比 `(40,40)` 基线快 `18%`。

## 已知事项

- 原 `spec.py` 只有 `neles = range(8,9)`，本轮只生成 Fe08 谱表。
- 历史 8 线程实测中 `Fe07b.en` 缺失警告非致命；本次仍按非致命处理。
- 大产物留在 HPC scratch/home，不回传 20 GB 级 `Fe08/`。

父级 [`../../README.md`](../../README.md)。
