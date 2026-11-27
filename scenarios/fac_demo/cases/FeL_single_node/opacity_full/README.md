# FeL_opacity_full —— full-physics 不透明度谱场景

在保留 `opacity/` 基线的前提下，新增 full-physics 不透明度场景。目标是让谱从平滑的 bound-free 背景升级为包含可见谱线、真实线宽、密集 PI 和 AI/DR 共振贡献的 Fe-L 谱。

## 1. 分阶段执行

```bash
python run.py --dry-run
python run.py --phase smoke          # 本地快速验证，可无 PFAC
python run.py --phase all            # 本地可用数据下的完整合成
python run.py --phase crm-pop        # HPC/WSL：Fe08/09/10 完整 CRM 布居
python run.py --phase pi-dense       # HPC/WSL：TotalPICross 密集 PI
python run.py --phase ai-dr          # HPC/WSL：AI/DR 共振贡献
python run.py --phase build
python run.py --phase validate
python run.py --phase plot
```

`--allow-fallback` 允许在 PFAC 或 HPC 产物缺失时用基线 ASCII/现有 `.sp` 降级，并在 metadata 中记录。默认开启。

## 2. 物理层级

- **bound-free**：`data/*.rr` 直接 PI；有 PFAC 时用 `TotalPICross` 生成密集网格。
- **bound-bound**：`data/*.tr` 的 gf + `.sp` 下能级布居；Voigt 线型 = Doppler + Stark/impact（若 `.sp` 提供 `wimp/wstk`）+ 自然宽度。
- **共振**：优先从 AI/DR 表构造示例级共振 PI；不可用时为零并记录。
- **绝对量纲**：主输出为 `cm^2 per Fe ion`；`kappa_inv_cm` 使用配置中的 Fe 丰度和路径长度，不与文献实验的 `cm^2/g` 直接比较。

## 3. HPC

推荐 24 核 / 16 MPI；`crm-pop` 与 `ai-dr` 使用 03:00:00，`pi-dense` 视规模使用 00:30:00 或 03:00:00。提交模板见 `hpc_jobs/`。

## 4. 验证与边界

不做 `make check`，无官方机器可读基准。验证项包括：bb 非零、谱线数、线宽正值、布居覆盖、能量单调、κ 非负、AI/DR 非负、阶段退出码。详见 `docs/physics_notes.md`。
