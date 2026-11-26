---
name: fac-credentials-scripts-formula-plan
overview: 在 FAC 凭证脚本计划基础上，增加全项目 README 公式规范化：所有公式改为 LaTeX 展示格式，源码未命中时使用 \underline{} 强调；随后完成 specx 凭证管理子包、CLI、启动器、文档与校验。
todos:
  - id: verify-targets
    content: 使用 [subagent:code-explorer] 复核公式注记、scripts 与文档入口
    status: pending
  - id: update-formula-rules
    content: 使用 [skill:skill-creator] 更新 LaTeX 与 \underline 规则
    status: pending
    dependencies:
      - verify-targets
  - id: normalize-formula-readmes
    content: 使用 [subagent:code-explorer] 与 [skill:lsp-code-analysis] 规范 README 公式
    status: pending
    dependencies:
      - update-formula-rules
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
      - normalize-formula-readmes
  - id: validate-all
    content: 校验公式格式、凭证闭环、脚本与文档门禁
    status: pending
    dependencies:
      - add-launchers-docs
---

## User Requirements

- 更新上一轮计划：FAC 项目 README 中所有公式必须使用 LaTeX 美观展示；若源码中未找到公式依据，必须使用 `\underline{}` 强调，不再使用 HTML `<u>` 标记。
- 在 FAC 项目的 `scripts/` 下新增凭证设置与读取脚本，面向未来超算计算、Gitee 推送、WSL 安装与计算等场景。
- 凭证保存方式仿照 FLASH：非敏感信息使用明文 JSON，敏感信息使用 Fernet 加密；存储位置通过 `Path.home()/".physimx"/"specx"` 解析，不硬编码用户目录。
- 未来需要整合 flychk 凭证，因此当前设计必须采用统一 `~/.physimx/` 根目录、命名空间隔离和可复用 API。
- 不读取、不导出、不复制任何真实凭据内容；仓库内只保留占位示例与脚本。
- 不修改 FAC 源码、Makefile、`check.py`、构建脚本、外部 FLASH 项目或已移动工作目录内容。

## Product Overview

- 形成两部分交付：一是统一的 README 公式格式与源码注记规范；二是 FAC 项目级凭证管理子包与 CLI。
- README 体系做到公式展示一致、源码依据可追溯、未命中公式使用 LaTeX 下划线强调。
- 凭证体系做到配置与密钥分离、命名空间隔离、默认脱敏输出、未来可无缝扩展到 flychk 与 flash。

## Core Features

- 全量更新 README 公式展示：完整公式使用 `$ ... $`，源码未命中公式下方使用 `\underline{\text{源码未找到该公式，需人工核查}}`。
- 同步更新 README 维护 skill 的规则与模板，确保后续维护持续采用 LaTeX 格式。
- 新建 `scripts/credentials/` 子包，支持 namespace、Fernet 加密、原子写入、脱敏展示。
- 支持 HPC SSH、Gitee Token、WSL 配置、通用 API Key 的设置与读取。
- 提供 `manage.py` 统一 CLI 与 Windows 一键启动器。
- 补充依赖说明、README 入口与最终门禁校验。

## Tech Stack Selection

- 文档：Markdown + LaTeX；沿用现有中文 README、相对链接、代码围栏与自底向上维护规范。
- 公式格式：
- 完整公式使用独立展示块 `$ ... $`。
- 简短变量可用 `$...，但完整物理公式、积分、求和、系数关系必须独立成块。
- 源码未命中的公式使用 `\underline{\text{源码未找到该公式，需人工核查}}`。
- 仅有手册或论文依据时使用 `\underline{\text{源码未找到该公式；仅见手册/论文，需人工核查}}`。
- 禁止继续使用 HTML `<u>...</u>` 作为公式注记。
- 脚本：Python 3 标准库优先；凭证加密使用 `cryptography.fernet`，作为辅助依赖写入 `requirements-dev.txt`。
- 凭证存储：
- 根目录：`Path.home()/".physimx"`。
- 当前 namespace：`specx`。
- 当前目录：`~/.physimx/specx/`。
- 敏感数据：`~/.physimx/specx/credentials.enc`。
- 密钥：`~/.physimx/specx/.secret_key`。
- 非敏感配置：`~/.physimx/specx/hpc_accounts.json`、`~/.physimx/specx/wsl_config.json`。
- Windows 一键入口：`scripts/launchers/*.bat`，按 `.gitattributes` 使用 CRLF。

## Implementation Approach

采用“复核目标 → 更新公式规则 → 规范化 README 公式 → 实现凭据核心层 → 实现服务脚本与 CLI → 补文档入口 → 统一校验”的流程。

关键决策：

1. 先更新 `fac-readme-maintainer` 的规则文件，再批量规范 README，避免后续维护规则漂移。
2. 公式核查事实优先级为：源码实现/输出器 > 生成文件头与实测记录 > 项目 README > 历史注释。
3. 凭证脚本集中在 `scripts/credentials/`，不散落在 `scripts/` 根目录。
4. 所有凭证 API 接受 `--namespace`，默认 `specx`，未来可直接使用 `flychk` 或 `flash` 命名空间。
5. 凭据键使用服务前缀：`gitee.token`、`hpc.flash_ssh.password`、`wsl.default_distro`、`api.deepseek.api_key`，避免跨项目重名。
6. CLI 默认只输出脱敏信息；自动化需要明文时必须通过 Python API 或显式受控输出，不在普通展示中泄露密钥。
7. HPC 基础信息单独 JSON 管理，密码和令牌只进入加密库。

## Implementation Notes

- 公式规范化范围包括 `faclib/`、`modqed/`、`coul/`、`ionis/`、`mpfun/`、`python/`、`sfac/`、6 个数值库 README，以及根 README 与 `doc/` 中的公式摘要。
- 需要同步修改 `skills/fac-readme-maintainer/references/formula-check-rules.md` 与 `readme-template.md`。
- 最终校验中搜索 `<u>` 应无残留；搜索 `\underline{\text{` 应与源码未命中公式清单一致。
- 凭据脚本所有写入采用临时文件加原子替换，避免中断导致密文损坏。
- POSIX 系统收紧目录与文件权限；Windows 下给出权限提醒但不阻断使用。
- 解密失败时返回空或明确错误，不猜测、不覆盖已有密文。
- 所有新增脚本必须支持 `--help`、明确退出码，并且不得在 stdout 输出明文密钥。
- 不修改真实 `specx` 凭据；测试只使用临时 namespace，结束后仅删除临时 namespace。

## Architecture Design

- 公式维护链路：
- README 维护 skill 规则 → 自底向上源码核查 → LaTeX 公式展示 → `\underline{}` 注记 → README 门禁校验。
- 凭证调用链路：
- `.bat` 启动器 / CLI → `scripts/credentials/manage.py` → namespace resolver → `MinimalCredentialManager` → `~/.physimx/<namespace>/credentials.enc` 与 `.secret_key` → 服务 JSON → 脱敏输出或 Python API 返回值。
- 组件职责：
- `manage.py`：统一 CLI 与菜单。
- `_minimal.py`：Fernet 密钥、加解密、原子写入、权限控制。
- `_core.py`：namespace 解析、凭据读写封装、脱敏、统一错误处理。
- `_config.py`：服务键、默认字段与 namespace 常量。
- `hpc_accounts.py`：HPC 账户、线路、SSH 用户名等非敏感配置。
- `gitee.py`：Gitee Token 设置、读取、脱敏展示。
- `wsl.py`：WSL 发行版、用户名、路径和计算环境配置。
- `api_keys.py`：通用 API Key 条目管理。

## Directory Structure

- `skills/fac-readme-maintainer/references/formula-check-rules.md`：[MODIFY] 将 `<u>` 规则改为 LaTeX `\underline{}` 规则，并规定公式必须用 `$ ... $` 展示。
- `skills/fac-readme-maintainer/references/readme-template.md`：[MODIFY] README 模板中增加 LaTeX 公式展示与下划线注记要求。
- `faclib/README.md`、`modqed/README.md`、`coul/README.md`、`ionis/README.md`、`mpfun/README.md`、`python/README.md`、`sfac/README.md`：[MODIFY] 将已核查公式改为 LaTeX 展示，源码未命中项改用 `\underline{}`。
- `blas/README.md`、`lapack/README.md`、`minpack/README.md`、`quadpack/README.md`、`toms/README.md`、`ode/README.md`：[MODIFY] 将通用算法注记改为 LaTeX `\underline{}` 展示。
- `doc/README.md`、`doc/papers/README.md`、`doc/misc/README.md`、`README.md`、`demo/README.md`：[MODIFY] 公式摘要统一为 LaTeX 展示，并链接到底层核查结论。
- `scripts/README.md`：[MODIFY] 新增 credentials 子包说明、使用场景与依赖提示。
- `scripts/credentials/README.md`：[NEW] 凭证管理子包总说明、安全边界、namespace 设计、存储位置。
- `scripts/credentials/__init__.py`：[NEW] 导出公共 API 与 namespace 辅助。
- `scripts/credentials/_config.py`：[NEW] 服务键命名、默认字段与 namespace 常量。
- `scripts/credentials/_minimal.py`：[NEW] Fernet 加密最小实现、密钥生成、原子写入。
- `scripts/credentials/_core.py`：[NEW] namespace 解析、凭据读写封装、脱敏、错误处理。
- `scripts/credentials/hpc_accounts.py`：[NEW] HPC 账户与线路 JSON 读写。
- `scripts/credentials/gitee.py`：[NEW] Gitee Token 设置、读取与脱敏展示。
- `scripts/credentials/wsl.py`：[NEW] WSL 配置管理。
- `scripts/credentials/api_keys.py`：[NEW] 通用 API Key 管理。
- `scripts/credentials/manage.py`：[NEW] 统一 CLI：status/setup/set/get/delete/list/show，支持 `--namespace`。
- `scripts/launchers/cred_manage.bat`、`cred_status.bat`、`cred_setup.bat`：[NEW] Windows 一键入口。
- `requirements-dev.txt`：[MODIFY] 增加 `cryptography>=41.0.0` 并注明仅辅助脚本使用。
- `DEPENDENCIES.md`：[MODIFY] 增加凭证管理依赖、存储位置、安全边界与 flychk 扩展方式。
- `AGENTS.md`、`CLAUDE.md`、`.cursor/rules/fac-context.mdc`、`.github/copilot-instructions.md`：[MODIFY] 增加凭证脚本入口与安全约定。
- `README.md`：[MODIFY] 根 README 导航补充凭证脚本入口。

## Validation

- `python scripts/credentials/manage.py --help` 正常运行。
- `status`、`list`、`show` 默认不输出任何明文密钥。
- 使用临时 namespace 完成 set/get/delete 闭环测试，测试后仅删除临时 namespace。
- `hpc_accounts.json` 可生成示例结构，但不写入真实主机或账号。
- 所有新增脚本通过 `--help` 检查。
- `python scripts/audit_readmes.py` 无缺失 README、无断链。
- 全项目搜索不得出现 `<u>` 残留、真实令牌、密码、真实主机地址或已移动工作目录具体名称。

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 复核 FAC 当前 `scripts/`、README、依赖文件、公式注记位置与凭证目标结构。
- Expected outcome: 得到精确修改路径、当前 `<u>` 残留清单、README 更新入口与潜在冲突点。

### Skill

- **skill-creator**
- Purpose: 更新 README 维护 skill 的公式规范，并保证 `fac-readme-maintainer` 结构合法。
- Expected outcome: skill 规则明确要求 LaTeX 公式与 `\underline{}` 注记，且通过 quick_validate。
- **lsp-code-analysis**
- Purpose: 在公式规范化阶段辅助确认源码符号、函数与实现位置。
- Expected outcome: 为公式是否存在源码实现提供可追溯证据，减少误标或漏标。