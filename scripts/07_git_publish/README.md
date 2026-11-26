# 07 Gitee 发布与同步

仿 FLASH `03_git_publish` 的常用流程，令牌从 `scripts/credentials` 读取，不进入命令行，不落盘到 remote URL。

## 文件

- `_git_auth.py`：Git 执行、repo_url、令牌注入。
- `gitee_push.py`：一键提交并推送；支持删除护栏、dry-run、pull-first、status。
- `gitee_pull.py`：一键拉取；支持 ff-only、rebase、stash。
- `gitee_pull_github.py`：从 GitHub 官方仓库拉取源码，以官方内容覆盖本地冲突文件；保护名单硬编码为根目录 `.gitignore` 与 `README.md`。
- `git_status.py`：查看分支、远端和状态。

## 常用命令

```bash
python scripts/07_git_publish/git_status.py
python scripts/07_git_publish/gitee_push.py --status
python scripts/07_git_publish/gitee_push.py -m "feat: update"
python scripts/07_git_publish/gitee_push.py -n
python scripts/07_git_publish/gitee_pull.py --ff-only
python scripts/07_git_publish/gitee_pull_github.py --dry-run
python scripts/07_git_publish/gitee_pull_github.py
python scripts/07_git_publish/gitee_pull_github.py --ref ced21df --dry-run
```

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
