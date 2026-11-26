# PhySimX FAC 变更记录

本文件记录 FAC 项目的工程化、文档体系、Agent 支持、部署与验证变更。历史上游记录保留在 [`ChangeLog`](ChangeLog)。

## 2026-11-25

### Added

- 项目根新增跨 Agent 上下文协议 `AGENTS.md` 与 `CLAUDE.md`、Cursor/Copilot 薄入口。
- 项目根新增 `skills/`，包含：
  - `fac-onboarding`
  - `fac-demo-workflow`
  - `fac-demo-troubleshooting`
  - `fac-code-navigation`
  - `fac-readme-maintainer`
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
