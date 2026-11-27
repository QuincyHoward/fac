# PhySimX FAC 变更记录

本文件记录 FAC 项目的工程化、文档体系、Agent 支持、部署与验证变更。历史上游记录保留在 [`ChangeLog`](ChangeLog)。

## 2026-11-26

### Added

- FeL 子场景新增 `plots/`、`figures/`、`artifacts/`、`hpc_jobs/` 与 `FeL仿真报告.html`，所有子场景相关文件集中在 `scenarios/fac_demo/cases/FeL_single_node/`。
- 回传 Job 4974613 全部 249 个产物，约 22 GB，并导出丰度 CSV。
- 新增 Python3 绘图脚本：光谱、丰度、速率、跃迁速率与矩阵耗时对比；科研风格，英文标注，Times New Roman，字号 >18pt。
- 新增 `export_fel_temps.py` / `fetch_fel_temps.py`：从 HPC 的 `get_tgrid(26,8)` 导出 T00–T06 的真实 Kelvin 温度。

### Changed

- FeL 谱图图例改为真实物理温度（272.5–2164.6 K），不再只写 T index。
- CE/RR/AI/CI 与跃迁速率图改为 10–18 Å 波长轴；内部能级编号图不再作为物理解释图。
- 报告明确说明：当前只计算发射谱；透过率谱需要额外光离截面、柱密度和连续谱假设，暂不计算。

- 新增 `skills/fac-hpc-parallel/`，覆盖超算并行执行、USE_MPI 检查、核数/MPI 矩阵、并行提交与资源汇总。
- 新增 FeL 参数矩阵配置 `scenarios/fac_demo/cases/FeL_single_node/matrix.json`。
- 新增 `scenarios/run/remote/batch_submit.py` 与 `matrix_report.py`。

### Changed

- 拆分 SLURM 核数与 FAC MPI 数接口：
  - `--cores N` 控制 SLURM CPU 数。
  - `--mpi M` 控制 `fac.InitializeMPI(M)` 与 `OMP_NUM_THREADS=M`。
  - `make -j` 使用核数，不与 MPI 数混用。
- `hpc.py` 新增 `matrix`、`wait-many`、`collect` 子命令。

### Validation

- 复用 `(40,40)` 基线作业 `4973989`（`02:45:15`），未重复提交。
- 并行提交并全部完成：
  - `(16,8)` Job `4974612`
  - `(24,16)` Job `4974613`
  - `(40,24)` Job `4974614`
  - `(40,32)` Job `4974615`
- 所有组合 `COMPLETED`、`fe_exit=0`、`spec_exit=0`、产物计数一致。
- 推荐组合：`(24 核, 16 MPI)`，FAC 总墙钟 `8150.632 s`，约比基线快 `18%`。
- 该集群 `sacct` 的 TotalCPU/AveCPU/MaxRSS 返回空或 0，已在结果中明确记录，不做推算。

## 2026-11-25

### Added

- 项目根新增跨 Agent 上下文协议 `AGENTS.md` 与 `CLAUDE.md`、Cursor/Copilot 薄入口。
- 项目根新增 `skills/`，包含：
  - `fac-onboarding`
  - `fac-demo-workflow`
  - `fac-demo-troubleshooting`
  - `fac-code-navigation`
  - `fac-readme-maintainer`
  - `fac-hpc-parallel`（2026-11-26 新增）
- 新增只读 MCP 风格上下文服务 `mcp_server.py`，供各类 Agent 读取 skill、README 与审计信息。
- 新增 `scripts/` 编号化工具体系：
  - `01_env_diagnose/`：环境检查
  - `02_build/`：构建辅助
  - `03_checks/`：冒烟与表比对
  - `04_audit/`：README 与公式门禁
  - `05_demo/`：原型清单
  - `06_scenarios/`：场景审计
  - `07_git_publish/`：Gitee 推送/拉取/Git 状态
  - `08_release/`：打包与 PyPI 发布
  - `09_backup/`：发布前备份
  - `10_deploy/`：WSL/HPC 部署
  - `credentials/`：namespace 化凭证管理与交互菜单
- 新增 `scenarios/run/` 仿真运行接口：
  - local / wsl / hpc-remote / hpc-insitu 四目标执行契约
  - SSH/SFTP、SLURM 作业渲染、提交、轮询与产物回传
  - 用户名统一来自凭证 `account.username`，路径写作 `~/<用户名>/fac/fac`
- 新增 `scenarios/fac_demo/cases/FeL_single_node/`，用于 FeL 单节点满核 HPC 验证。
- 新增 `.pre-commit-config.yaml`、`pyproject.toml`、`.gitattributes`、`.editorconfig`、`DEPENDENCIES.md`、`requirements-dev.txt`。

### Changed

- README 体系按章节化方式重构，覆盖 80 份 README；公式统一使用 LaTeX 展示，源码未溯源公式使用 `\underline{$...$}`。
- `.gitignore` 按章节重构：仅 `demo/` 与场景清单中的产物/基准可入库，其余输出表、日志、缓存、报告、大文件默认忽略。
- 凭证体系仿 FLASH：非敏感配置 JSON + Fernet 加密敏感信息；支持 HPC、Gitee、WSL、API Key、PyPI、通用用户名/密码。
- 凭证交互输入改为可见一次，避免隐藏输入导致误操作；`Ctrl+C` 会安全退出而非抛栈。
- HPC 用户名与 WSL 用户名均由凭证 `account.username = QC` 推导，不再硬编码。
- HPC 作业构建流程修正：
  - `chmod +x configure config.guess config.sub install.sh mkinsdir.sh`
  - shell 脚本保持 LF
  - `sysdef.h` 手动修正 `f2cFortran` 与 `USE_MPI=2`
  - 使用 `make pfac` 而不是裸 `python setup.py build`
  - 使用 HPC Python 3.8.6（自带 numpy 1.22.4）替代 Python 3.6

### Fixed

- 修正 `env_check.py` 在未构建 PFAC 时崩溃的问题。
- 修正 HPC SSH 登录用户名问题：必须使用完整 `scfa2696@NC-E`，不能拆掉 `@NC-E`。
- 修正 `sbatch` 拒绝 CRLF 脚本的问题：作业脚本以二进制 LF 写入。
- 修正 `configure` 因压缩包丢失执行权限导致的 `Permission denied`。
- 修正 `cfortran.h` ABI 报错：启用 `f2cFortran`。
- 修正 `pfac.fac` 编译时找不到 `init.h`：改用 `make pfac` 传递正确的 include/link 参数。
- 修正 FeL 场景脚本在 Python 3.6 下的语法兼容问题与场景根目录定位问题。

### Validation

- WSL：`Ubuntu-22.04`、主机名 `Quincy`；部署到 `/root/QC/fac/fac`；`env_check.py` 显示核心工具链可用。
- HPC：NC-E 凭据 `flash_ssh`；部署到 `/publicfs01/fs1-e/home/scfa2696/QC/fac/fac`。
- FeL 单节点满核 HPC 测试：
  - 作业号：`4973989`
  - 核心数：`40`
  - 构建宏：`USE_MPI=2`，确认支持 FAC 内部并行仿真
  - 结束状态：`COMPLETED`
  - `fe_exit=0`、`spec_exit=0`
  - `data/` 文件数：36
  - `Fe08/` 文件数：210
  - `summary.json.ok=true`
  - 小摘要与日志回传至 `scenarios/fac_demo/outputs/FeL_single_node_HPC/`

### Deployment Notes

- WSL 目标目录未发现已构建但串行的情况（`NO_SYSDEF`）。
- HPC 上曾出现未定义 `USE_MPI` 导致 fe.py 段错误；已通过 `configure --with-mpi=omp` 与 `sysdef.h` 手动补丁修复。
- 大产物保留在 HPC 作业目录，仓库只回传摘要、状态和小日志。
