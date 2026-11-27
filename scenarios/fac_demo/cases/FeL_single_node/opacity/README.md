# FeL_opacity —— 复用 FeL 产物的不透明度谱示例

本场景位于 `FeL_single_node/opacity/`，直接复用 `../artifacts/FeL_single_node_c24m16/` 中的 FeL 仿真产物，不重跑 `fe.py`/`spec.py`。

## 1. 输入产物

- `data/Fe08a.en`、`data/Fe09a.en`、`data/Fe10a.en`：能级块偏移，用于 `(block, level)` → `bound_index` 映射。
- `data/Fe08a.rr`、`data/Fe09a.rr`、`data/Fe10a.rr`：光电离 PI 截面（每跃迁 6 个能量点）。
- `Fe08/Fe08a_t??d0i3.sp`：`TYPE=0000000` 布居块，给出各能级稳态布居。
- `plots_inputs/temperatures.csv`、`plots_inputs/abund.csv`：温度与铁离子丰度。

注意：
- `temperatures.csv` 的 `T_K` 列实为 eV，`log10T=6.5` 对应约 272 eV。
- FeL `spec.py` 的 `.sp` 文件只包含 `NELE=8` 与 `NELE=9` 布居；`Fe10`（Fe XVII）使用基态布居近似，并在 `build_metadata.json` 中记录 `fallback=ground_state`。

## 2. 执行阶段

```bash
# 查看命令
python run.py --dry-run

# 基线：build -> validate -> plot
python run.py --phase all

# 单独阶段
python run.py --phase build
python run.py --phase validate
python run.py --phase plot

# 需要密集 PI 时（PFAC 环境）
python run.py --phase all --dense-pi --cores 24 --mpi 16
```

`--artifacts-dir` 与 `--output-dir` 可覆盖默认路径；`--cores`/`--mpi` 只记录到各阶段参数与汇总，核数与 MPI 数不混用。

## 3. 计算量分级

- **基线后处理**：顺序读取约 4.5 GB ASCII，流式提取布居与 PI 通道；本地完成，不提交 HPC。
- **密集 PI（`TotalPICross`）**：需要 PFAC，优先在已构建 HPC/WSL 环境执行；为短作业量级。
- **RRTable 重算**：与 FeL `fe.py` 同量级（参考 7213.612 s），必须走 HPC；模板见 `hpc_jobs/`。

## 4. 输出

- `outputs/tables/opacity_tXX.csv`：`energy_ev`、`wavelength_a`、`kappa_cm2_per_Fe`、`kappa_inv_cm`、`transmission`、`kappa_bf`、`kappa_bb`。
- `outputs/figures/*.png`：κ(E)、κ(λ)、T(E) 与 bf/bb 分量图。
- `outputs/dense_pi/*.csv`：可选密集 PI 网格。
- `outputs/summary.json`：阶段退出码、耗时、计数与验证状态。

## 5. 验证口径

无官方 `ref/`，不做 `make check`；只做产物完整性、能量单调性、κ 非负性、布居归一、离子丰度一致、原始 6 点往返一致性，以及文献条件记录检查。详见 [`docs/literature_comparison.md`](docs/literature_comparison.md) 与 [`../refs/mds/reading_notes.md`](../refs/mds/reading_notes.md)。
