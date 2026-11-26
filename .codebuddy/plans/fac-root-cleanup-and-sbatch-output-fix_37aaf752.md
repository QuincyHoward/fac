---
name: fac-root-cleanup-and-sbatch-output-fix
overview: 核查 FAC 根目录文件功能，确认无可移动的运行产物；修正 HPC 作业脚本生成位置，使 sbatch 落到发起场景目录的子文件夹。
todos:
  - id: verify-callchain
    content: 使用 [subagent:code-explorer] 核查 HPC 提交调用链与产物
    status: completed
  - id: change-sbatch-output
    content: 修改 job_submit.py，按场景目录生成 hpc_jobs
    status: completed
    dependencies:
      - verify-callchain
  - id: verify-hpc-dry-run
    content: 运行 submit 和 matrix dry-run，确认根目录无 sbatch
    status: completed
    dependencies:
      - change-sbatch-output
  - id: report-root-audit
    content: 输出根目录文件功能结论与未移动原因
    status: completed
    dependencies:
      - verify-hpc-dry-run
---

## 用户需求

- 核查 FAC 项目根目录中的代码、配置与疑似产物，确认各文件功能。
- 对确实无用且可安全移走的运行产物，移动到项目根目录 `temp_delete/`；当前核查未发现 `fac_FeL*.sbatch` 文件或根目录 `config.log`、`config.status` 等产物，因此不创建空目录、不移动官方源码。
- 修正会在项目根目录生成 `fac_FeL*.sbatch` 的脚本，使本地 sbatch 保存到发起场景脚本所在目录下的子文件夹。
- 保持物理子场景执行链路、远端提交链路和已有基准不受影响。

## 核心功能

- 明确根目录 `config.guess`、`config.sub`、`configure`、`configure.ac` 的来源与用途：属于官方 Autoconf 构建体系，且 HPC 作业脚本会复制并使用，不能移动到 `temp_delete/`。
- 将本地 sbatch 输出从当前工作目录改为场景目录下的 `hpc_jobs/` 子目录，例如 `scenarios/fac_demo/cases/FeL_single_node/hpc_jobs/`。
- 验证 `submit --dry-run` 与 `matrix --dry-run` 均不再向项目根目录写出 sbatch，且返回路径仍可被远端上传流程使用。
- 输出根目录文件功能结论和未移动原因。

## 技术栈选择

- Python 3 标准库，沿用现有 `scenarios/run` 的 `SceneSpec`、`ExecOptions`、`JobLayout`、`write_job_file` 架构。
- 使用现有 CLI dry-run 流程验证，不新增第三方依赖。

## 实现思路

- 采用“由场景元数据决定本地作业脚本目录”的策略：`SceneSpec.path` 已由 `hpc.py:24-29` 和 `batch_submit.py:22-32` 指向对应 case 目录，可直接作为 sbatch 输出根目录，无需新增命令行参数。
- 在 `scenarios/run/remote/job_submit.py` 中新增私有辅助函数，将 `prepare_submission()` 的 `write_job_file(Path.cwd(), ...)` 改为写入 `scene.path / "hpc_jobs"`。
- `session.upload(info["local_job"], info["remote_job"])` 继续使用返回的本地路径，因此远端提交行为不变。
- 不修改 `hpc.py:100-103` 的 `matrix_jobs.json` 路径，因为它已位于场景输出区且不是用户本次指出的根目录产物。
- 若进一步核查发现真实存在的根目录运行产物，则仅移动这些产物到 `temp_delete/` 并保持相对路径；当前事实为零产物，因此实际不移动。

## 关键决策与权衡

- 不移动根目录 `config*`：它们是 Git 已跟踪的上游构建源，`job_scripts.py:46-52` 明确复制并使用 `configure`、`config.guess`、`config.sub`、`install.sh`、`mkinsdir.sh` 进行远端构建；移动会破坏 HPC 作业与常规构建。
- 不使用 `Path.cwd()`：该写法使输出依赖于调用位置，从项目根调用会污染根目录；改为 `SceneSpec.path` 后输出与发起场景稳定绑定。
- 不新增 `--job-dir` 参数：所有调用方已具备场景路径，新增参数会增加接口复杂度且不符合用户“按发起场景保存”的要求。

## 实现说明

- 修改点位于 `scenarios/run/remote/job_submit.py:24-45`，重点是第 37 行。
- 仅改变本地 sbatch 文件落点；不改变 `job_name`、文件名、`body`、远端作业目录和上传逻辑。
- `.gitignore:90` 已忽略 `*.sbatch`，新目录中的 sbatch 不会误入版本库。
- 不触碰 `README.md`、`.gitignore`、`demo/*/ref/`、物理源码和根目录 config 构建文件。
- 复杂度为 O(1) 路径计算和一次目录创建，无额外遍历或性能开销。

## 架构设计

- 调用链：`hpc.py` 或 `execution.py` 构造 `SceneSpec` → `submit_scene()` → `prepare_submission()` → 场景目录派生 → `write_job_file()` → `session.upload()`。
- 本地 sbatch 输出目录成为场景级产物目录；远端作业路径仍由 `JobLayout` 统一管理。

## 目录结构

```text
e:/PhySimX/PhySimX/diagnosis/SpecX_test/SpecX-diag/specx/_solvers/fac/src/fac/
├── scenarios/
│   └── run/
│       └── remote/
│           └── job_submit.py  # [MODIFY] 新增场景作业目录派生逻辑，替换 Path.cwd() 输出位置，保持返回结果和远端上传不变。
└── temp_delete/               # [NOT CREATE] 当前未发现可移动产物；仅在后续核查发现真实产物时按相对路径移入。
```

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 复核 HPC 提交调用链、根目录疑似产物和所有基于 `Path.cwd()` 的本地作业写入点，确保修改范围完整。
- Expected outcome: 给出唯一需修改入口、无 `fac_FeL*.sbatch` 可移动文件、根目录 `config*` 为必需构建源的证据。