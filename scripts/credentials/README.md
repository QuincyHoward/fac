# FAC 凭证管理子包

本目录提供 FAC 的凭证设置、读取与脱敏展示工具，面向超算、Gitee、WSL 与通用 API Key 场景。

## 1. 存储边界

- 根目录：`Path.home()/".physimx"`
- 当前 namespace：`specx`，目录 `~/.physimx/specx/`
- 敏感数据：`credentials.enc`，Fernet 加密
- 密钥：`.secret_key`
- 非敏感配置：`hpc_accounts.json`、`wsl_config.json`

不硬编码用户目录；不在仓库保存任何真实凭据。

## 2. Namespace 设计

所有脚本支持 `--namespace`，默认 `specx`。预留 `flychk`、`flash` 作为同级命名空间，便于后续整合。凭据键使用服务前缀：`gitee.token`、`gitee.repo_url`、`account.username`、`account.password`、`hpc.<账户>.password`、`wsl.default_distro`、`api.deepseek.api_key`、`pypi`、`testpypi`。

## 3. 使用入口

```bash
python scripts/credentials/manage.py              # 交互式主菜单
python scripts/credentials/manage.py setup        # 凭据设置子菜单
python scripts/credentials/manage.py --help
python scripts/credentials/manage.py status
python scripts/credentials/manage.py list
python scripts/credentials/manage.py show gitee.token
python scripts/credentials/manage.py set demo.key
```

交互式主菜单仿照 FLASH 凭证管理方式：显示 namespace、存储目录与已保存条目，提供状态、列表、脱敏查看、键值设置、删除、常用凭据设置与 namespace 切换。敏感值在输入时可见一次，之后不再明文显示；`status/list/show` 默认脱敏。

`3) HPC 账户基础信息与密码` 采用 FLASH 式流程：启动时自动读取当前 namespace 的 `hpc_accounts.json`，列出已有账户供选择；账户标题、SSH 用户名、专属用户名、线路标识与线路列表来自该 JSON，用户手动输入的 SSH 密码写入加密库键 `hpc.<账户名>.password`。若检测到账户尚未设置密码，会立即提示补录；已设置密码时默认跳过，只有明确选择“是”才替换。

`5) PyPI / TestPyPI 令牌` 写入 `pypi`、`testpypi` 条目，`scripts/08_release/publish_pypi.py` 通过环境变量传给 twine，不进入命令行。

`6) 用户名与密码` 用于手动设置通用 `account.username` 与 `account.password`，代码中不预设 `hello/123` 等固定值；再次进入时会显示已有用户名作为默认值。HPC 账户另有独立 `username` 字段保存在 `hpc_accounts.json`，与 `ssh_username` 分开。

## 4. 安全约定

- 非敏感基础信息放 JSON；密码、令牌、API Key 放加密库。
- 加密写入采用临时文件加原子替换。
- POSIX 系统收紧目录与文件权限；Windows 给出提醒但不阻断。
- 解密失败不猜测、不覆盖已有密文。
- 测试仅使用临时 namespace，不触碰真实 `specx` 凭据。

## 5. 导航

父级 [`../README.md`](../README.md)；上下文 [`../../AGENTS.md`](../../AGENTS.md)。
