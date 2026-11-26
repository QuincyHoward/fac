# FAC 项目 Agent 上下文协议

本文件是 `{fac/}` 项目的通用上下文入口，供 Codex、OpenCode、Cursor、Zed、Warp、Amp、Jules、VS Code、Claude Code、Workbuddy、CodeBuddy 等 Agent 读取。厂商适配文件只指向本文件，不复制规则正文。

## 1. 项目范围与工作边界

- 项目根即本文件所在目录 `{fac/}`；所有相对路径均相对该根目录。
- FAC 是相对论原子结构与原子过程计算套件：C 核心库 `faclib/`、Fortran 数值库、Python/PFAC 接口、SFAC 命令接口和 `demo/` 回归示例共同构成完整工作流。
- 原始源码树视为只读事实源。构建、运行、调试优先在**独立可写工作目录**完成，用 `<WORK_ROOT>` 表示；不要在文档中写死该目录的具体路径或名称。
- 不修改 `demo/*/ref/` 基准，除非用户明确要求重建基准；`make ref` 会覆盖基准，必须先确认物理结果正确。
- 不把“环境适配”“ABI 修补”“Python 语法兼容”误判为物理模型修改；也不得在未核实前改物理参数、阈值、积分网格或输出单位。

## 2. 读取顺序与渐进披露

1. 先读本文件，确认任务类型、路径口径、并行策略和安全边界。
2. 按触发规则只读取一个或两个相关 `SKILL.md`，不要一次加载全部 skill。
3. 只有需要命令细节、字段表、完整错误库或源码映射时，再读取对应 `references/` 文档。
4. 最后才读取具体 `README.md` 或源码文件；优先用结构化线索定位，避免整仓库全文扫描。
5. 事实冲突时优先级：实际脚本与源码 > 输出文件头与实测记录 > 项目 README > 历史笔记或旧注释。

## 3. Skill 索引与触发规则

| Skill | 何时触发 | 入口 |
|---|---|---|
| `fac-onboarding` | 首次上手、重新构建、并行编译、PFAC 导入失败、冒烟测试 | `skills/fac-onboarding/SKILL.md` |
| `fac-demo-workflow` | 选择 demo 运行路径、判断输入输出依赖、分类回归方式、估算资源消耗 | `skills/fac-demo-workflow/SKILL.md` |
| `fac-demo-troubleshooting` | 构建失败、运行崩溃、比对失败、无基准、长耗时、单位或列语义异常 | `skills/fac-demo-troubleshooting/SKILL.md` |
| `fac-code-navigation` | 查找物理功能实现、API 调用链、模块职责、PFAC/SFAC 接口映射 | `skills/fac-code-navigation/SKILL.md` |
| `fac-readme-maintainer` | 自底向上维护 README、核查公式、添加源码未命中下划线注记 | `skills/fac-readme-maintainer/SKILL.md` |
| `fac-hpc-parallel` | 超算并行执行 FAC、USE_MPI、核数/MPI 矩阵、并行提交与资源汇总 | `skills/fac-hpc-parallel/SKILL.md` |

触发多条时按“先环境/构建，再工作流，再排障，再源码定位，再文档维护”的顺序处理；不要让排障 skill 直接覆盖工作流判断。

## 4. 通用路径与命名约定

- `{fac/}` 内部路径使用仓库相对路径，例如 `demo/`、`faclib/`、`python/`、`doc/`。
- 构建与运行目录统一写作 `<WORK_ROOT>`；执行时由用户或 Agent 替换为真实可写路径。
- 输出表保留原始文件名与扩展名：`check.py` 依赖文件尾部分派，改名会导致 `TypeError`。
- 历史执行记录只写“实测记录摘要”，不硬编码易变的外部目录路径。
- 文档中不得写死某台机器的绝对路径；命令示例使用 `<WORK_ROOT>`、`<CASE_DIR>`、`<RESULT>` 等占位符。

## 5. 并行策略

- 优先并行：只读检索、多份文档读取、独立算例、独立输出目录、互不依赖的检查任务。
- 必须串行：行尾归一化、`configure`、生成或修改 `sysdef.h`、写入同一文件、对同一基准目录的写操作。
- PFAC 非线程安全：不要用 Python 多线程并发调用同一 PFAC 实例；并行只能走独立进程/独立解释器，并隔离输出目录与日志。
- OpenMP/MPI 只在脚本显式支持时启用；不能假定所有脚本识别 `openmp` 参数。
- 并行任务必须记录退出码、日志归属和输出目录；失败时保留现场，不要立即清理。

## 6. 回归与验证约定

- 有基准表时优先 `make check` 或单项 `python ../check.py <结果> <基准>`。
- 无官方基准时不得声称“自动回归通过”；改做产物完整性、正值性、能量网格、物理趋势和文献量级检查。
- 比对失败先检查：扩展名分派、`E0`/`NBlocks`、行序重排、容差、死键、版本/时间戳、单位与列语义；最后才怀疑物理实现。
- 耗时口径分离：日常 `check.py` 无计时逻辑；长任务只记录端到端墙钟与脚本内部计时，不从退出码推断速度。
- 未实测的耗时、退出码、产物规模不得编造；写“未记录”比推断更安全。

## 7. 安全边界

- 不删除或覆盖用户未明确授权的文件，尤其是基准表、历史日志、外部工作目录产物。
- 不把调试补丁写回原始源码树；若必须在工作副本中适配，说明原因、物理影响和验证方式。
- 不通过放宽容差、替换基准、改物理参数来“修好”比对；先定位根因。
- 涉及数值单位时，先确认 ASCII 与二进制单位、`TYPE` 字段和读取器键名，再做换算。
- 文档与代码注释冲突时，以实际函数调用、输出文件头和实测记录为准。

## 8. 输出风格

- 用中文回答；技术术语、命令、文件名保留原文。
- 给结论时附最小证据：文件路径、函数名、表字段或命令退出码。
- 能运行的最小验证优先于长篇推断；但不要在本协议层执行修改性操作。
- 对不确定事项明确标注“需实测”或“源码定义待核对”，不要伪装成确定结论。

## 9. 工程入口与上下文服务

- Skill 唯一事实源是项目根 `skills/`；不要再引用隐藏目录中的旧 skill 路径。
- `scripts/` 存放场景无关工具，按 `01_`–`09_` 分类：环境、构建、检查、审计、demo、场景、Gitee 推送/拉取、打包发布、备份；`scripts/credentials/` 提供 namespace 化凭证管理，默认 `specx`，CLI 默认脱敏。Gitee/PyPI 令牌不进入命令行或 remote URL。
- `scenarios/` 只负责物理场景创建；`scenarios/run/` 提供 local/wsl/hpc-remote/hpc-insitu 执行接口。场景通过 `scene.json`、`scene_manifest.json` 与 `_scene_anchors.json` 发现；HPC/WSL 用户目录来自凭证 `account.username`，不硬编码机器路径。
- `mcp_server.py` 提供只读 MCP 风格上下文服务：列出 skills、读取 skill/context/README、审计报告与场景清单；不提供写入或 shell 执行。
- 依赖边界见 `DEPENDENCIES.md`；Python 辅助依赖见 `requirements-dev.txt`；LF 与 CRLF 例外见 `.gitattributes`。
- README 体系维护必须遵循 `skills/fac-readme-maintainer/SKILL.md`：源码未溯源公式直接写成 `\underline{$...$}`，源码已溯源公式不加下划线。
