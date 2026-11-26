# 07 Gitee 发布与同步

仿 FLASH `03_git_publish` 的常用流程，令牌从 `scripts/credentials` 读取，不进入命令行，不落盘到 remote URL。

## 文件

- `_git_auth.py`：认证统一入口；强制 `origin` 为无凭据 Gitee URL，原 GitHub origin 保留为 `upstream`。
- `_git_credential_helper.py`：只服务 `gitee.com` 的 credential helper，凭据经管道传递，不写配置、不进命令行。
- `gitee_push.py`：一键提交并推送到 Gitee；支持删除护栏、dry-run、pull-first、status、force。
- `gitee_pull.py`：一键从 Gitee 拉取并以 Gitee 内容覆盖本地冲突文件；保护根目录 `.gitignore` 与 `README.md`。
- `gitee_pull_github.py`：从 GitHub 官方仓库拉取源码，以官方内容覆盖本地冲突文件；同样保护根目录 `.gitignore` 与 `README.md`。
- `git_status.py`：查看分支、远端和状态。

## 常用命令

```bash
python scripts/07_git_publish/git_status.py
python scripts/07_git_publish/gitee_push.py --status
python scripts/07_git_publish/gitee_push.py -m "feat: update"
python scripts/07_git_publish/gitee_push.py -n
python scripts/07_git_publish/gitee_push.py
python scripts/07_git_publish/gitee_pull.py -n
python scripts/07_git_publish/gitee_pull.py
python scripts/07_git_publish/gitee_pull_github.py --dry-run
python scripts/07_git_publish/gitee_pull_github.py
python scripts/07_git_publish/gitee_pull_github.py --ref ced21df --dry-run
```

## Gitee 一键推送 / 覆盖拉取

- 旧版 `ensure_origin()` 只判断 `origin` 是否存在；本仓 `origin` 原本指向 GitHub，因此推送时实际访问 GitHub 并要求 GitHub 凭据。现已改为：`origin` 强制设为 `gitee.repo_url`，原 GitHub URL 自动转为 `upstream`。
- 认证按 FLASH `03_git_publish` 的方式改为 credential helper：git 调用 helper，helper 从 `scripts/credentials` 读取 `gitee.token`，经 stdin/stdout 管道回传；token 不写入 `.git/config`、不进入 argv。`core.askPass` 与已有 helper 均被清空，避免弹窗。
- `gitee_pull.py` 不再做 `git pull --ff-only`，而是克隆 Gitee 分支到临时目录，按文件哈希覆盖本地同名文件；根目录 `.gitignore`、`README.md` 受保护，本地独有文件保留。它只同步工作区文件，不改写 Git 历史。

## GitHub 官方源码覆盖

- 官方版本：`https://github.com/flexible-atomic-code/fac.git` 的 `master` HEAD 为 `9ab6defb6af62e1bc8251a35ff995809abef717c`（2026-10-27，`safeguard in ce interpolation (#854)`）。`ced21df0bc58783bcbee0714b3daffa152b4a3ff` 是旧标签 `v1.1.4`（2016-11-09），不是当前版本。
- 实现：通过 `api.github.com` 解析 ref，通过 `codeload.github.com` 按 SHA 下载归档；不依赖 `git ls-remote`（本机 github.com:443 不可达），也不需要 Gitee 令牌。
- 保护名单：脚本中硬编码 `PROTECTED_PATHS = {".gitignore", "README.md"}`，根目录这两个文件不覆盖、不备份、不参与复核，报告中标记为 `protected/skipped`。
- 覆盖口径：文本按 Git index 口径比较（CRLF 归一为 LF），二进制按原始字节；只有非保护且内容确实不同的文件才会覆盖，覆盖前按原相对路径备份到 `backups/{timestamp}/`。
- 本地独有文件默认保留；不改写 `demo/*/ref/` 基准。

## 凭据

- `gitee.token`：Gitee 私人访问令牌。
- `gitee.repo_url`：仓库地址，例如 `https://gitee.com/quincyhoward/fac.git`。

父级 [`../README.md`](../README.md)。
