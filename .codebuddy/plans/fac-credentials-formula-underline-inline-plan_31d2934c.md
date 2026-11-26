---
name: fac-credentials-formula-underline-inline-plan
overview: 按用户最新示例修正公式规则：源码未溯源的公式直接写成 `\underline{$...$}`，删除此前的下划线说明文字、紧贴公式下方注记及其他 underline 相关规则；凭证脚本任务保持不变。
todos:
  - id: verify-targets
    content:
      - "#text": 使用 [subagent:code-explorer] 复核公式与脚本入口
    status: completed
  - id: update-formula-rules
    content:
      - "#text": 使用 [skill:skill-creator] 更新公式与 underline 规则
    status: completed
    dependencies:
      - verify-targets
  - id: normalize-formula-readmes
    content:
      - "#text": 使用 [subagent:code-explorer] 与 [skill:lsp-code-analysis] 规范公式
    status: completed
    dependencies:
      - update-formula-rules
  - id: create-credential-core
    content:
      - "#text": 新建 scripts/credentials 核心加密与 namespace 层
    status: completed
    dependencies:
      - verify-targets
  - id: create-service-scripts
    content:
      - "#text": 新增 HPC、Gitee、WSL、API Key 脚本
    status: completed
    dependencies:
      - create-credential-core
  - id: create-manage-cli
    content:
      - "#text": 实现 manage.py 统一 CLI 与脱敏输出
    status: completed
    dependencies:
      - create-service-scripts
  - id: add-launchers-docs
    content:
      - "#text": 补充启动器、README、依赖与协议入口
    status: completed
    dependencies:
      - create-manage-cli
      - normalize-formula-readmes
  - id: validate-all
    content:
      - "#text": 校验公式写法、凭证闭环、脚本与文档门禁
    status: completed
    dependencies:
      - add-launchers-docs
---

## User Requirements
- 将 FAC 部署到已确认的 NC-E 超算账户 `scfa2696`，目标位置按 `~/{用户名}/fac/fac` 语义解析，默认使用 NC-E 的 `remote_home` 下的 `fac/fac`，并允许执行时覆盖目标路径。
- 在 `scenarios/run/` 中建立类似 FLASH `flash_run` 的仿真运行接口，支持本地、WSL、超算远程、超算就地等执行目标；场景层只声明物理与策略，执行层统一负责 SSH、SLURM、作业目录、提交、轮询和产物回传。
- 在 `scenarios/fac_demo/cases/` 中新增 FeL 单节点满核测试场景，不修改原始 `demo/FeL/` 脚本；通过适配副本注入满核并行设置，完成一次真实 NC-E 超算单节点满核 FeL 测试。
- 新增 `PhySimX_fac_CHANGELOG.md`，记录近期工程化改造、部署与验证结果，不修改原有 `ChangeLog`。
- 全程不打印、不复制真实密码或令牌；敏感信息从 `~/.physimx/specx` 的加密凭证读取。

## Product Overview
形成一套可复用的 FAC 仿真执行层与 HPC 提交机制，并完成一次可追溯的 FeL 单节点满核超算验证；同时新增独立变更日志，便于后续 Agent 与用户查看工程化演进。

## Tech Stack Selection
- 执行层：Python 3 标准库为主，SSH/SFTP 使用 `paramiko` 作为开发依赖。
- 超算作业：SLURM，使用 `sbatch` 提交、`squeue`/`sacct` 轮询、`scancel` 取消。
- 凭证：复用 `scripts/credentials/` 与 `~/.physimx/specx/credentials.enc`，账户基础信息读取 `hpc_accounts.json` 中的 `flash_ssh`。
- 场景体系：沿用现有 `scenarios/common/`、`scenarios/core/`、`scenarios/fac_demo/cases/` 结构，新增 `scenarios/run/` 执行层。
- 文档：Markdown、相对链接、中文说明；公式沿用现有 LaTeX 规则。

## Implementation Approach
采用“接口分层 → 场景接入 → HPC 部署 → 真实提交 → 变更记录”的流程。关键决策：

1. `scenarios/run/` 只提供通用执行机制，不写 FeL 专属常量；FeL 专属配置放在 `scenarios/fac_demo/cases/FeL_single_node/`。
2. HPC 目标默认按远程 `HOME` 解析，NC-E 使用 `flash_ssh` 的 `remote_home`，同时提供 `--target` 覆盖能力，避免硬编码用户目录。
3. FeL 产物巨大，作业目录采用 home 存脚本与日志、scratch 存大数据；默认只回传状态、日志摘要、关键小表，不回传 20 GB 级 `Fe08/` 全量产物。
4. 单节点满核通过远程自动探测核心数，作业使用 `--nodes=1 --ntasks-per-node=N`，FeL 适配副本中注入 `fac.InitializeMPI(N)`。
5. SSH/SFTP 操作串行化；`sbatch` 超时必须回查队列，防止重复提交。

## Performance and Reliability
- 远程大文件传输只做一次目录上传，避免逐文件往返。
- 产物回传使用白名单策略，避免拉取 `data/` 与 `Fe08/` 大目录。
- 作业轮询间隔固定且可配置，失败状态立即终止。
- 完整产物校验在 HPC 本地完成，本地只保留可验证摘要。

## Architecture Design
```text
scenarios/
├── fac_demo/cases/FeL_single_node   # 场景声明、FeL 适配、验证
├── run/                             # 执行契约与 CLI
│   ├── execution.py                 # 目标解析与 run_scene
│   ├── hpc.py                       # HPC 统一入口
│   ├── remote/                      # SSH、SLURM、作业渲染、回传
│   └── env/                         # 路径、资源、目标路径解析
└── core/                            # 场景发现、清单、锚点

scripts/credentials/                 # 只读凭证与账户解析
scripts/10_deploy/                   # WSL 与 HPC 部署经验
```

## Directory Structure
- `scenarios/run/README.md`：新增，说明四目标模型、分层铁律、HPC 流程和经验。
- `scenarios/run/__init__.py`：新增，惰性导出核心 API。
- `scenarios/run/execution.py`：新增，统一执行契约、目标解析、策略校验。
- `scenarios/run/hpc.py`：新增，提交、状态、等待、取消、下载、节点探测 CLI。
- `scenarios/run/remote/session.py`：新增，唯一 SSH/SFTP 入口，从凭证读取密码。
- `scenarios/run/remote/slurm.py`：新增，唯一 SLURM 操作封装。
- `scenarios/run/remote/job.py`：新增，stage/build/run/verify/archive 作业脚本渲染与提交。
- `scenarios/run/remote/layout.py`：新增，home 与 scratch 目录布局、资源规格。
- `scenarios/run/remote/fetch.py`：新增，产物白名单回传与摘要生成。
- `scenarios/run/env/paths.py`：新增，解析远程 HOME、用户名和目标路径。
- `scenarios/run/env/resources.py`：新增，单节点满核探测与资源策略。
- `scenarios/fac_demo/cases/FeL_single_node/README.md`：新增，FeL 场景说明与运行方式。
- `scenarios/fac_demo/cases/FeL_single_node/scene.json`：新增，场景元数据与执行策略。
- `scenarios/fac_demo/cases/FeL_single_node/run.py`：新增，场景入口，调用 `scenarios/run`。
- `scenarios/fac_demo/cases/FeL_single_node/prepare_fel.py`：新增，从 `demo/FeL/` 生成适配副本并注入核心数。
- `scenarios/fac_demo/cases/FeL_single_node/verify_fel.py`：新增，检查退出码、关键文件、产物数量与物理合理性摘要。
- `scenarios/fac_demo/scene_manifest.json`：修改，注册 FeL 单节点场景。
- `scenarios/_scene_anchors.json`：修改，增加 HPC 运行目录、FeL 场景与脚本锚点。
- `scripts/10_deploy/README.md`：修改，补充 NC-E 部署经验与事故规避。
- `requirements-dev.txt`：修改，新增 `paramiko`。
- `PhySimX_fac_CHANGELOG.md`：新增，记录工程化、部署与 FeL 测试结果。
- `scripts/README.md`、`scenarios/README.md`、`AGENTS.md`：修改，补充新入口与分层约定。

## Key Code Structures
- `ExecutionTarget`：字符串枚举，包含 `local`、`wsl`、`hpc-remote`、`hpc-insitu`。
- `ExecutionPolicy`：声明允许目标、核数约束、失败原因。
- `JobRequest`：包含场景名、远程目录、scratch 目录、核数、命令模板、回传白名单。
- `RemoteSession`：提供 `run`、`upload`、`download`、`exists`、`mkdir_p`。

## Agent Extensions
### SubAgent
- **code-explorer**
  - Purpose: 复核 FLASH `flash_run`、FAC `scenarios/` 与 `demo/FeL/` 的落点和现有约定。
  - Expected outcome: 输出精确文件清单、接口边界和 FeL 场景适配点。

### Skill
- **lsp-code-analysis**
  - Purpose: 分析现有 `scenarios/core/` 与新增执行层的 API 依赖关系，确认无反向依赖。
  - Expected outcome: 得到场景层与执行层的符号引用清单，避免把 HPC 机制错误塞入场景层。
