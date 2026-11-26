# 依赖说明

本文档只描述依赖边界，不替代构建与使用说明。FAC 核心构建依赖与 Python 辅助工具依赖相互独立。

## 1. FAC 核心构建依赖

| 依赖 | 用途 | 必需性 |
|---|---|---|
| C 编译器 `gcc` 或等价工具 | 编译 `faclib/`、`python/`、`sfac/` | 必需 |
| Fortran 编译器 `gfortran` 或等价工具 | 编译数值库与特殊函数 | 必需 |
| GNU `make` | 执行顶层与各目录构建目标 | 必需 |
| Python 3 | 构建 PFAC 扩展并运行辅助脚本 | 必需 |
| Linux/WSL | 推荐构建环境 | 强烈建议 |

Windows 原生环境通常缺少 Fortran 工具链，且不能直接加载 Linux/WSL 编译出的扩展模块；优先在 WSL 中构建与运行。

## 2. Python 辅助依赖

`scripts/`、`scenarios/` 与 `mcp_server.py` 优先使用 Python 标准库。可选依赖集中在 `requirements-dev.txt`：

- 绘图：`matplotlib`、`numpy`
- 开发测试：`pytest`
- 凭证管理：`cryptography`（Fernet 加密；仅 `scripts/credentials/` 使用）
- 打包发布：`build`、`twine`（仅 `scripts/08_release/` 使用）
- 提交门禁：`pre-commit`（配合 `.pre-commit-config.yaml`）
- HPC 远程执行：`paramiko`（仅 `scenarios/run/remote` 使用；密码来自加密凭证）

这些依赖**不影响 FAC 核心库构建**；缺失时相关脚本应给出清晰安装提示，而不是在导入阶段阻断其他功能。

凭证管理使用 `Path.home()/".physimx"` 作为根目录，当前 namespace 为 `specx`；敏感信息写入 `~/.physimx/specx/credentials.enc`，密钥为 `.secret_key`，非敏感配置写入同目录 JSON。该 API 支持 `flychk`、`flash` 等平行 namespace，未来整合时无需改脚本结构。

## 3. MCP 服务

根目录 `mcp_server.py` 提供只读 Agent 上下文服务：

- 暴露 skill 列表、skill 内容、上下文协议、README 与审计报告。
- 不提供文件写入、shell 执行或任意路径读取。
- 默认仅使用标准库，可本地启动；不需要额外 MCP Python SDK。

如后续需要 stdio/SSE 正式 MCP 传输或工具调用权限，应单独设计权限模型后再扩展，不要在只读服务中直接加入命令执行能力。

## 4. 路径与工作目录

构建、运行、调试优先放在独立可写工作目录，文档中统一写作 `<WORK_ROOT>`。不要写死任何机器绝对路径；场景与脚本使用相对清单和锚点发现资源。

## 5. Skill 与上下文资产

所有 skill 的唯一事实源是项目根 `skills/`。`AGENTS.md` 及各 Agent 适配入口只负责发现与加载，不复制 skill 正文。
