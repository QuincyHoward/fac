---
name: fac-credentials-scripts-structure-plan
overview: 参考 FLASH scripts 与 credentials 结构，为 FAC 制定凭证管理脚本方案：在 scripts/ 下新增 specx 凭证设置/读取工具，使用 ~/.physimx/specx/ 的 Fernet 加密存储，并为未来 flychk 凭证整合预留命名空间。
todos:
  - id: verify-targets
    content: 使用 [subagent:code-explorer] 复核 scripts 与文档入口
    status: pending
  - id: create-credential-core
    content: 新建 scripts/credentials 核心加密与 namespace 层
    status: pending
    dependencies:
      - verify-targets
  - id: create-service-scripts
    content: 新增 HPC、Gitee、WSL、API Key 脚本
    status: pending
    dependencies:
      - create-credential-core
  - id: create-manage-cli
    content: 实现 manage.py 统一 CLI 与脱敏输出
    status: pending
    dependencies:
      - create-service-scripts
  - id: add-launchers-docs
    content: 补充启动器、README、依赖与协议入口
    status: pending
    dependencies:
      - create-manage-cli
  - id: validate-credentials
    content: 验证脚本帮助、临时 namespace 闭环与文档门禁
    status: pending
    dependencies:
      - add-launchers-docs
---

## 用户要求

- 已回答“哪些公式经核查后添加了下划线”：涉及 `faclib/`、`modqed/`、`coul/`、`ionis/`、`mpfun/`、`python/`、`sfac/` 以及 6 个数值库 README 的通用算法注记。
- 已只读整理 FLASH 项目 `scripts/` 结构：按 `01_env_diagnose/` 到 `08_docs/` 功能编号分层，另有 `utils/`、`git-hooks/` 与根级工具；每个一级目录有 README，凭据统一由 credentials 模块读取。
- 在 FAC 项目的 `scripts/` 下新增凭证设置与读取脚本，面向未来超算计算、Gitee 推送、WSL 安装与计算等场景。
- 凭证保存方式仿照 FLASH：非敏感信息明文 JSON，敏感信息 Fernet 加密；存储位置使用 `Path.home()/".physimx"/"specx"` 解析，不硬编码 `C:\Users\Administrator`。
- 未来会整合 flychk 相关凭证，因此当前设计必须采用统一 `~/.physimx/` 根目录、命名空间隔离与可复用 API。
- 不读取、不导出、不复制任何真实凭据内容；仓库内只保留占位示例与脚本。

## 交付结果

形成一套可复用的 FAC 凭证管理子包与 CLI：支持 namespace、HPC SSH 配置、Gitee Token、WSL 配置、通用 API Key、脱敏展示、Windows 一键入口，并同步更新 README 与依赖说明。

## 技术栈与约束

- 文档：Markdown，沿用项目现有中文 README、相对链接与自底向上维护规范。
- 脚本：Python 3 标准库优先；凭据加密使用 `cryptography.fernet`，作为辅助依赖写入 `requirements-dev.txt`，不影响 FAC 核心构建。
- 存储根：`Path.home()/".physimx"`；当前 namespace 为 `specx`，未来可平行扩展 `flychk`、`flash`。
- 当前 namespace 目录：`~/.physimx/specx/`。
- 敏感数据：`~/.physimx/specx/credentials.enc`。
- 密钥：`~/.physimx/specx/.secret_key`。
- 非敏感基础信息：`~/.physimx/specx/hpc_accounts.json`、`~/.physimx/specx/wsl_config.json`。
- Windows 一键入口：放在 `scripts/launchers/`，`.bat` 文件按 `.gitattributes` 使用 CRLF。
- 所有新脚本必须提供 `--help`、明确退出码、脱敏输出；默认禁止在 stdout 打印明文密钥。
- 不修改 FAC 源码、Makefile、`check.py`、构建脚本或外部 FLASH 项目。

## 实施方案

采用“复核现状到设计统一凭据层到实现服务脚本到接入一键入口到文档与校验”的流程。

关键决策：

1. 凭证脚本不散落在 `scripts/` 根目录，而是新建 `scripts/credentials/` 子包，便于维护与未来迁移。
2. 采用 FLASH 的“配置和密码分离”模式：主机、端口、线路、WSL 发行版等非敏感信息放 JSON；密码、Token、API Key 放 Fernet 加密库。
3. 采用 namespace 机制支持 flychk 整合：所有脚本支持 `--namespace specx|flychk|flash`，默认 `specx`；同一份 API 通过 namespace 切换目录。
4. 凭据键采用服务前缀：`gitee.token`、`hpc.flash_ssh.password`、`wsl.default_distro`、`api.deepseek.api_key`，避免跨项目重名冲突。
5. CLI 默认只展示脱敏信息；需要给自动化脚本使用时，通过 Python API 读取，或显式使用受控参数输出到受限文件，不在普通展示中泄露明文。
6. HPC 连接基础信息单独 JSON 管理，避免主机和线路信息进入加密库，保持与 FLASH 一致的可手工编辑特性。

性能与可靠性：

- 凭据读写规模很小，主要瓶颈是安全与正确性，不涉及大规模计算。
- 所有加密写入采用临时文件加原子替换，避免中断导致密文损坏。
- POSIX 系统收紧目录与文件权限；Windows 下给出权限提醒但不阻断使用。
- 解密失败时返回空或明确错误，不猜测、不覆盖已有密文。

## 架构设计

调用链：

```text
CLI / .bat launcher
  -> scripts/credentials/manage.py
  -> namespace resolver
  -> MinimalCredentialManager
  -> ~/.physimx/<namespace>/credentials.enc + .secret_key
  -> service JSON files
  -> masked output or Python API result
```

组件职责：

- `manage.py`：统一入口与菜单。
- `_minimal.py`：Fernet 加密、解密、原子写入。
- `_core.py`：namespace 解析、凭据读写封装、脱敏、通用辅助。
- `_config.py`：凭据条目模板与默认字段。
- `hpc_accounts.py`：HPC 账户、线路、SSH 用户名等非敏感配置。
- `gitee.py`：Gitee Token 设置与读取。
- `wsl.py`：WSL 发行版、用户名、项目路径等非敏感配置与必要凭据入口。
- `api_keys.py`：通用 API Key 管理。

## 目录结构

```text
fac/
├── scripts/
│   ├── README.md
│   │   # [MODIFY] 新增 credentials 子包说明、使用场景与依赖提示
│   ├── credentials/
│   │   ├── README.md
│   │   # [NEW] 凭证管理子包总说明、安全边界、namespace 设计、存储位置
│   │   ├── __init__.py
│   │   # [NEW] 导出公共 API：get/set/delete/list/mask/namespace 辅助
│   │   ├── _config.py
│   │   # [NEW] 凭据条目模板、服务键命名、默认字段与 namespace 常量
│   │   ├── _minimal.py
│   │   # [NEW] Fernet 最小实现：密钥生成、加密、解密、原子写入、权限收紧
│   │   ├── _core.py
│   │   # [NEW] 凭据管理器封装、脱敏、namespace 解析、统一错误处理
│   │   ├── hpc_accounts.py
│   │   # [NEW] HPC 账户 JSON 读写、线路与用户名管理
│   │   ├── gitee.py
│   │   # [NEW] Gitee Token 设置、读取、脱敏展示
│   │   ├── wsl.py
│   │   # [NEW] WSL 发行版、用户名、路径与计算环境配置管理
│   │   ├── api_keys.py
│   │   # [NEW] 通用 API Key 条目管理，为 flychk 与外部服务扩展预留
│   │   └── manage.py
│   │       # [NEW] CLI：status/setup/set/get/delete/list/show，支持 --namespace
│   └── launchers/
│       ├── README.md
│       # [MODIFY] 增加凭据管理启动器说明
│       ├── cred_manage.bat
│       # [NEW] 打开凭据管理菜单
│       ├── cred_status.bat
│       # [NEW] 查看当前 namespace 凭据状态
│       └── cred_setup.bat
│           # [NEW] 进入交互式常用凭据设置
├── requirements-dev.txt
│   # [MODIFY] 增加 cryptography 依赖并说明仅辅助脚本使用
├── DEPENDENCIES.md
│   # [MODIFY] 增加凭证管理依赖、存储位置、安全边界与 flychk 扩展方式
├── AGENTS.md
│   # [MODIFY] 增加 scripts/credentials 入口与安全约定
└── README.md
    # [MODIFY] 根 README 导航补充凭证脚本入口
```

## 验证标准

- `python scripts/credentials/manage.py --help` 正常运行。
- `status`、`list`、`show` 默认不输出任何明文密钥。
- 使用临时 namespace 完成 set/get/delete 闭环测试，测试后仅删除临时 namespace，不触碰真实 `specx` 凭据。
- `hpc_accounts.json` 可生成示例结构，但不写入真实主机或账号。
- 所有新增脚本通过 `--help` 检查。
- `python scripts/audit_readmes.py` 无缺失 README、无断链。
- 全项目搜索不得出现真实令牌、密码、主机地址，也不得引用已移动工作目录的具体名称。

## SubAgent

- **code-explorer**
- Purpose: 复核 FAC 当前 `scripts/`、README、依赖文件与新增目录结构，确认所有修改目标和文档入口。
- Expected outcome: 给出精确文件路径、现有脚本约定、需更新的 README 清单与潜在冲突点。