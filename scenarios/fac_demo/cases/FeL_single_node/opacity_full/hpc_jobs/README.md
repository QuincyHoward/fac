# HPC 分级执行说明

重计算统一通过顶层 wrapper 场景 `FeL_opacity_full` 提交：

```bash
python -m scenarios.run.hpc submit --scene FeL_opacity_full --cores 24 --mpi 16 --walltime 03:00:00 \
  --run-id opacity_full_crm --stage crm-pop -- --phase crm-pop
python -m scenarios.run.hpc submit --scene FeL_opacity_full --cores 24 --mpi 16 --walltime 00:30:00 \
  --run-id opacity_full_pidense --stage pi-dense -- --phase pi-dense
python -m scenarios.run.hpc submit --scene FeL_opacity_full --cores 24 --mpi 16 --walltime 03:00:00 \
  --run-id opacity_full_aidr --stage ai-dr -- --phase ai-dr
```

要点：
- 必须使用唯一 `--run-id`，否则同秒提交会复用同一作业目录。
- 24 核 / 16 MPI 沿用 FeL 实测推荐组合；核数与 MPI 数不要混用。
- `crm-pop` 生成 Fe08/09/10 完整布居；`pi-dense` 用 `TotalPICross` 生成密集 PI；`ai-dr` 生成示例级共振贡献。
- 回传仅取 CSV/JSON/PNG/summary，不回传 GB 级原始表。

实际提交脚本由 `scenarios/run/remote/job_scripts.py` 自动生成到本目录，以下 `.sbatch` 仅作阶段模板说明。
