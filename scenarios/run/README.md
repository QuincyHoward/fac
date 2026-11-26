# FAC 仿真运行接口

仿 FLASH `flash_run` 的分层设计，提供 FAC 场景在 local / wsl / hpc-remote / hpc-insitu 四种目标上的统一执行契约。

## 分层铁律

```text
scenarios/  ->  scenarios/run/  ->  scripts/credentials/
```

- 场景只声明物理与资源策略，不内联 SSH/SLURM/wsl 逻辑。
- 本目录不 import `fac_demo`，运行层不包含场景名常量。
- 用户名统一来自凭证 `account.username`，HPC/WSL 路径均写作 `~/<用户名>/fac/fac`。

## 子模块

- `execution.py`：唯一目标解析与执行入口；核数与 FAC MPI 数为两个独立参数。
- `remote/batch_submit.py`：并行提交独立参数矩阵。
- `remote/matrix_report.py`：合并 SLURM 资源、FAC 内部耗时与产物一致性。
- `modes/`：local / wsl / hpc-insitu 执行体。
- `remote/`：SSH、SLURM、作业渲染、提交、回传。
- `env/`：装置默认值与资源配置。

## 常用入口

```bash
python -m scenarios.run.hpc status
python -m scenarios.run.hpc nodes
python -m scenarios.run.hpc submit --scene FeL_single_node --cores auto
python -m scenarios.run.hpc wait --job <ID>
python -m scenarios.run.hpc download --remote <dir> --local <dir>
```

父级 [`../README.md`](../README.md)。
