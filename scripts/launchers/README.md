# Windows 一键启动器

本目录的 `.bat` 文件用于 Windows 下快速调用分类后的 Python 脚本。

- `00_menu.bat`：显示入口菜单。
- `env_check.bat`：`01_env_diagnose/env_check.py`。
- `smoke_check.bat`：`03_checks/smoke_check.py`。
- `check_tables.bat`：`03_checks/check_tables.py`。
- `cred_manage.bat`：打开凭证主菜单。
- `cred_status.bat`：查看当前 namespace 凭据状态。
- `cred_setup.bat`：进入凭据设置子菜单。
- `git_push.bat`：提交并推送到 Gitee。
- `git_pull.bat`：从 Gitee 拉取。
- `git_status.bat`：查看 Git 状态。
- `package.bat`：构建 sdist/wheel。
- `backup.bat`：发布前备份。
- `deploy_wsl.bat`：将当前项目部署到 WSL 目标目录。

批处理文件在 `.gitattributes` 中设为 CRLF；其他文本默认 LF。
