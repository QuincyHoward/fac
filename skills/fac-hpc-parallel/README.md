# fac-hpc-parallel

在超算上并行执行 FAC/PFAC 的项目级 skill。

## 触发场景

- 用户要求部署、构建或运行 HPC 上的 FAC。
- 用户要求启用 `USE_MPI` 或比较核数/MPI 数。
- 用户要求并行提交多个独立场景或参数组合。
- 用户要求汇总 SLURM 资源消耗、FAC 耗时和产物一致性。

## 核心规则

- 核数与 MPI 数是两个独立参数。
- `USE_MPI=2` 必须验证。
- 每个提交使用独立 job name、run_id 和工作目录。
- 通过一个 SSH 会话依次提交多个作业，SLURM 侧并行运行。
- 结果必须同时验证状态、退出码和产物完整性。

## 资源

- [`SKILL.md`](SKILL.md)
- [`references/matrix-protocol.md`](references/matrix-protocol.md)
- [`references/fel-matrix-results.md`](references/fel-matrix-results.md)
- [`references/error-library.md`](references/error-library.md)
- [`assets/matrix-summary-template.md`](assets/matrix-summary-template.md)

父级 [`../README.md`](../README.md)。
