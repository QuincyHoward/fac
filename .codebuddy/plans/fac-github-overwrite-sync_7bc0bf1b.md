---
name: fac-github-overwrite-sync
overview: 核实 GitHub 官方 fac 版本并新增 scripts/07_git_publish/gitee_pull_github.py，以官方源码为准覆盖本地冲突文件并验证一致性。
todos:
  - id: implement-github-fetch
    content: 新增 gitee_pull_github.py，实现 ref 解析、归档下载与安全解压
    status: completed
  - id: implement-overwrite-verify
    content: 实现冲突扫描、备份、串行覆盖、哈希复核与退出码
    status: completed
    dependencies:
      - implement-github-fetch
  - id: update-script-docs
    content: 更新 07 与 scripts README，记录版本结论和命令示例
    status: completed
    dependencies:
      - implement-github-fetch
  - id: verify-sync-result
    content: 运行 dry-run 与覆盖验证，确认官方路径无冲突
    status: completed
    dependencies:
      - implement-overwrite-verify
      - update-script-docs
---

## 用户需求

- 核实 `https://github.com/flexible-atomic-code/fac.git` 官方版本状态，给出具体版本，并确认是否为 `ced21df`。
- 获取官方源码，以官方源码为唯一事实源覆盖当前 FAC 项目：官方内容保持不变，本地同名文件若冲突则改为官方内容，直到官方路径下无冲突；**唯一例外：仓库根目录的 `.gitignore` 与 `README.md` 指定不覆盖，该保护规则直接写在脚本中**。
- 在 `scripts/07_git_publish/gitee_pull_github.py` 新增脚本，直接完成拉取 GitHub、覆盖本地并验证结果。

## 已确认结论

- 官方 `master` HEAD 为 `9ab6defb6af62e1bc8251a35ff995809abef717c`，提交时间 `2026-10-27`，标题 `safeguard in ce interpolation (#854)`；本地 HEAD 与之相同。
- `ced21df0bc58783bcbee0714b3daffa152b4a3ff` 是有效提交，但对应旧标签 `v1.1.4`，提交时间 `2016-11-09`，不是当前官方版本。
- 当前已跟踪文件中仅 `.gitignore` 与 `README.md` 被本地修改；另有 239 个本地独有文件，不与官方 479 个路径冲突。这两个被修改文件正是本次指定的保护对象。

## 核心功能

- 支持默认拉取 `master`，也支持通过 `--ref` 指定分支、标签或提交 SHA，例如 `ced21df`。
- 展示官方完整 SHA、提交信息、冲突文件清单（含被保护跳过的文件）、被覆盖文件数量与备份位置。
- **保护名单硬编码在脚本中**：脚本顶部常量 `PROTECTED_PATHS = {".gitignore", "README.md"}`，仅限仓库根目录；这两个路径不备份、不覆盖、不参与一致性复核，报告中明确标为 `protected/skipped`。
- 覆盖前备份除保护名单外将被替换的本地文件；覆盖后对除保护名单外的全部官方路径逐文件哈希复核，确保除保护名单外无冲突。
- 默认保留本地独有文件，不删除、不改写 `demo/*/ref/` 基准。

## 技术栈选择

- 复用现有 Python 3 脚本体系：Python 3.14.6 可用，脚本目录已有 `argparse`、中文输出、`--dry-run`、明确退出码等约定。
- 仅使用标准库：`urllib.request`、`json`、`tarfile`、`hashlib`、`pathlib`、`shutil`、`subprocess`、`tempfile`、`concurrent.futures`。
- 复用 `scripts/07_git_publish/_git_auth.py` 的 `repo_root()` 定位仓库根，但不调用需要 Gitee 令牌的 `auth_env()`。
- 不新增第三方依赖；Git 仅用于读取仓库根和本地独有文件清单，不用于访问 GitHub。

## 实现思路

采用“GitHub API 解析版本 + codeload 下载源码归档 + 本地逐文件哈希覆盖”的策略。原因是实测 `git ls-remote https://github.com/flexible-atomic-code/fac.git` 在本机因 443 连接失败而不可用，但 `api.github.com` 与 `codeload.github.com` 的 HTTPS 访问返回 200。脚本不执行 `git fetch` 或 `git pull`，避免依赖不可达的 git 协议。

关键决策：

- 版本解析：`GET https://api.github.com/repos/flexible-atomic-code/fac/commits/{ref}` 得到完整 SHA；若用户直接传 40 位 SHA，则跳过 API 解析以减少一次网络请求和速率限制消耗。
- 源码获取：`https://codeload.github.com/flexible-atomic-code/fac/tar.gz/{sha}`，只下载一次并流式写入临时文件；以 SHA 固定归档内容，保证可复现。
- **保护名单**：`PROTECTED_PATHS = {".gitignore", "README.md"}` 写在脚本源码中，无需命令行开关；命中时打印跳过原因，不修改文件内容。
- 覆盖语义：只对官方归档中存在的相对路径强制一致，根目录 `.gitignore`、`README.md` 例外；本地独有文件默认保留并在报告中列出，不默认删除。
- 安全解压：自行校验 tar 成员名称，拒绝绝对路径、`..`、符号链接、设备文件，再写文件到临时目录，兼容 Python 3.10 且不依赖 `extractall(filter=...)`。
- 备份：仅备份会被覆盖的非保护冲突文件。当前唯一两处冲突均被保护，因此本次真实运行预期不产生任何备份与文件写入；若未来其他官方路径出现冲突，才按原相对路径备份到 `scripts/07_git_publish/backups/{timestamp}/`。

## 性能与可靠性

- 设官方文件数为 `F`、总字节数为 `B`；哈希、扫描、覆盖均为 `O(F + B)`，空间开销为一份临时归档和解压树。
- 网络是主要瓶颈：仅 1 次 API 请求和 1 次归档下载；下载使用超时与有限重试，失败时保留临时文件并报告路径。
- 哈希比对可用线程池并行，线程数上限 8；文件写入必须串行，遵循项目“同一文件写入串行”的并行约定。
- 日志只打印冲突文件列表摘要、保护跳过项与失败项，避免刷屏；不打印任何令牌，脚本不需要 Gitee 凭据。

## 架构设计

- `resolve_ref()`：把 `--ref` 解析为官方完整 SHA、日期、标题。
- `download_archive()`：下载并校验 gzip 归档，写入 `tempfile.TemporaryDirectory()`。
- `extract_official()`：安全解压，返回“相对路径到 SHA-256”的官方文件映射。
- `scan_local()`：对官方路径计算本地 SHA；命中 `PROTECTED_PATHS` 的路径标记为 protected/skipped，不计入冲突；并用 `git ls-files --others --exclude-standard` 统计本地独有文件。
- `backup_and_overwrite()`：串行备份并覆盖非保护冲突文件；遇到保护路径直接跳过并计数。
- `verify()`：重新计算除保护名单外的全部官方路径哈希，不一致则退出码 1 并保留备份现场；保护路径单独报告为 skipped，不影响成功判定。

退出码约定：`0` 成功或 dry-run 正常结束，`1` 网络、解压、覆盖或复核失败，`2` 参数或前置条件错误，例如当前目录不是 Git 仓库。

## 目录结构

```text
scripts/
├── 07_git_publish/
│   ├── gitee_pull_github.py   # [NEW] 主脚本：解析 ref、下载官方归档、安全解压、冲突扫描、保护名单跳过、备份、覆盖、哈希复核与摘要输出；沿用 argparse 中文 CLI 风格。
│   ├── README.md              # [MODIFY] 增加新脚本说明、版本结论、运行示例、保护名单、备份位置、本地独有文件保留策略与网络限制说明。
│   └── backups/{timestamp}/   # [RUNTIME NEW] 仅在出现非保护冲突时生成；当前保护名单覆盖了两处已知冲突，故本次运行不生成备份。
└── README.md                  # [MODIFY] 功能索引中补充 gitee_pull_github.py，常用命令中加入 dry-run 与指定版本示例。

.gitignore                    # [PROTECTED] 由脚本硬编码保护，保持本地现状，不覆盖、不备份。
README.md                     # [PROTECTED] 由脚本硬编码保护，保持本地中文工程文档，不覆盖、不备份。
```

## 验证方式

- 先执行 `python scripts/07_git_publish/gitee_pull_github.py --dry-run`，确认报告官方 SHA、冲突文件（应显示 `.gitignore`、`README.md` 为 protected/skipped）、本地独有文件数量。
- 再执行真实覆盖，预期：除 `.gitignore`、`README.md` 外的 477 个官方路径哈希全部一致，2 个保护路径被跳过且内容不变；`git status` 中这两个文件仍显示本地修改，属于预期行为。
- 可用 `python scripts/07_git_publish/gitee_pull_github.py --ref ced21df --dry-run` 验证旧标签解析路径；保护名单同样生效，且不应把 `ced21df` 写成默认官方版本。