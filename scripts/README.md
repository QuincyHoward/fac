# FAC 常用脚本

本目录存放与物理场景无关的 FAC 辅助脚本，按 FLASH 风格使用编号目录分类。凭证管理子包保留在 `credentials/`，Windows 一键入口集中在 `launchers/`。

## 1. 设计原则

- Python 3 标准库优先；构建、发布与加密依赖作为辅助依赖，不参与 FAC 核心构建。
- 所有路径默认相对项目根；外部工作目录写作 `<WORK_ROOT>`。
- 每个脚本提供 `--help`、明确退出码。
- Gitee/PyPI 令牌通过凭证模块读取，不进入命令行、不写入 remote URL。

## 2. 目录结构

```text
scripts/
├── 01_env_diagnose/   # 环境诊断
├── 02_build/          # 构建辅助
├── 03_checks/         # 冒烟检查与表比对
├── 04_audit/          # README 与公式门禁
├── 05_demo/           # demo 原型清单
├── 06_scenarios/      # 场景审计
├── 07_git_publish/    # Gitee 推送/拉取、Git 状态、GitHub 官方源码覆盖
├── 08_release/        # 打包与 PyPI 发布
├── 09_backup/         # 发布前备份
├── 10_deploy/         # WSL / 超算部署经验与工具
├── credentials/       # FAC 凭证管理与交互式菜单
└── launchers/         # Windows .bat 一键入口
```

## 3. 功能索引

| 分类 | 脚本 | 用途 |
|---|---|---|
| `01_env_diagnose` | `env_check.py` | 检查编译器、make、Python 与 PFAC 模块可见性 |
| `02_build` | `build_parallel.py` | 生成并执行安全的并行构建命令 |
| `03_checks` | `smoke_check.py` | PFAC 导入与 demo 冒烟检查 |
| `03_checks` | `check_tables.py` | 调用 `demo/check.py` 做单项表比对 |
| `04_audit` | `audit_readmes.py` | 审计 README 覆盖与相对链接 |
| `04_audit` | `audit_formula_underlines.py` | 审计公式下划线写法与 `<u>` 残留 |
| `05_demo` | `list_archetypes.py` | 列出 demo 通用原型 |
| `06_scenarios` | `audit_scenarios.py` | 审计场景清单、scene.json 与锚点 |
| `07_git_publish` | `gitee_push.py` / `gitee_pull.py` / `git_status.py` | Gitee 一键推送、拉取与状态 |
| `07_git_publish` | `gitee_pull_github.py` | 拉取 GitHub 官方源码并覆盖本地冲突文件；保护根目录 `.gitignore` 与 `README.md` |
| `08_release` | `package.py` / `publish_pypi.py` | 打包、检查与 PyPI/TestPyPI 发布 |
| `09_backup` | `backup.py` | 发布前备份 |
| `10_deploy` | `deploy_wsl.py` | 将项目部署到 WSL 目标目录，并记录部署经验 |
| `credentials` | `manage.py` | namespace 化凭证 CLI 与交互式菜单 |

## 4. 常用命令

```bash
python scripts/credentials/manage.py              # 凭证主菜单
python scripts/07_git_publish/git_status.py
python scripts/07_git_publish/gitee_push.py -m "feat: update"
python scripts/07_git_publish/gitee_push.py -n
python scripts/07_git_publish/gitee_pull.py --ff-only
python scripts/07_git_publish/gitee_pull_github.py --dry-run
python scripts/07_git_publish/gitee_pull_github.py
python scripts/08_release/package.py --check
python scripts/09_backup/backup.py --mode gitee -n
```

## 5. Windows 一键入口

`launchers/` 提供环境、冒烟、表比对、凭证、Git 推送/拉取/状态、打包与备份的 `.bat` 入口。

## 6. 导航

父级 [`../README.md`](../README.md)；上下文协议 [`../AGENTS.md`](../AGENTS.md)；场景 [`../scenarios/README.md`](../scenarios/README.md)。
