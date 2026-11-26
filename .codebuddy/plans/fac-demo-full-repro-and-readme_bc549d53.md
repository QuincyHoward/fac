---
name: fac-demo-full-repro-and-readme
overview: 全量复核 38 份 README 公式；在 WSL 的 temp_test 副本中逐个跑完 10 个 demo 示例（含调试 FeL 与 rmatrix），并把每个示例 README 深度改写为含物理场景、公式、执行记录、FAC 使用流程图与数据流图的中文文档；副本构建/运行改动必须在相关 README 中说明物理意义。
todos:
  - id: inventory-formulas
    content: 使用 [subagent:code-explorer] 全量盘点38份README公式与出处
    status: completed
  - id: literature-source-check
    content: 使用 [skill:agent-browser] 与 [skill:lsp-code-analysis] 核对文献源码
    status: completed
    dependencies:
      - inventory-formulas
  - id: run-all-demos
    content: 在WSL副本中逐个跑完10个demo并记录结果
    status: completed
    dependencies:
      - literature-source-check
  - id: apply-formula-fixes
    content: 就地修正38份README中的公式出处与单位
    status: completed
    dependencies:
      - run-all-demos
  - id: rewrite-demo-readmes
    content: 重写10个示例README并加入Mermaid流程图数据流图
    status: completed
    dependencies:
      - apply-formula-fixes
  - id: final-verification
    content: 验证执行覆盖、文档结构、只读保护与英文附录
    status: completed
    dependencies:
      - rewrite-demo-readmes
---

## User Requirements

继续核查公式，并在逐示例真实执行的基础上深度更新 `demo/` 下每个示例的 README.md。

## Product Overview

形成一套可验证、可复现、便于人类与 Agent 利用的示例文档体系：每个示例都说明物理场景、物理效应、物理公式、源码与 API 对应、运行流程、输入输出、数据流、回归比对结果，以及执行中暴露的限制。

## Core Features

- 全量复核全部 38 份 README.md 中的公式、单位、系数、指数、索引、出处和源码对应关系。
- 逐个实际执行 `demo/` 下 10 个示例，不设时间上限，必须跑到结束。
- 深度更新 10 个示例 README.md，补充物理背景、LaTeX 公式、完整执行流程、FAC 使用流程图和数据流图。
- 在 `temp_test/` 副本中调试 FeL 与 rmatrix 的执行问题；所有副本改动必须写入 README.md，并说明物理或数值意义。
- 保持原始源码只读不变；只修改 README.md 以及 `temp_test/` 内副本、脚本和日志。
- 不新增独立核查报告，核查结论直接体现在 README.md 正文中。

## Tech Stack Selection

- 文档对象：FAC 源码树中 38 份中文 README.md，公式使用标准 LaTeX，流程图使用 Mermaid 代码块。
- 执行环境：复用 WSL Ubuntu-22.04，gcc 9.5、gfortran 11.4、GNU make、Python 3.10。
- 构建位置：仅在 `temp_test/fac_src/` 副本中 configure、make、make pfac；原树仅读取且保持只读。
- 回归工具：使用 `demo/check.py` 对示例输出表与 `demo/*/ref/` 参考表逐项比对。
- 文献来源：仓库 `doc/manual.tex`、`doc/papers/*.tex`，并用联网工具与权威论文、教材交叉核对标准公式。
- 源码分析：结合 `code-explorer`、`lsp-code-analysis` 和文本检索定位函数、宏、调用链、单位换算和数值实现。

## Implementation Approach

采用“全量公式复核 到 WSL 逐示例执行 到 README 深度重写 到最终验证”的流程。

关键决策：

- 文献只用于确认物理意义和标准形式，最终 README 写法以 FAC 源码实现为准。
- 每个示例必须真实执行，不能只依据脚本静态推断；执行结果、日志、比对结论写入对应 README。
- FeL 不设时间上限；rmatrix 需继续诊断段错误，优先在副本中调整构建桥接、线程或运行参数，并记录任何修改的物理意义。
- 公式复核和示例重写同步推进：示例 README 中的公式必须再次与该示例脚本、调用到的 faclib 函数、论文手册出处三方核对。
- 小范围修正全库其余 README，只改错误公式、单位、出处、源码行号和必要说明，不重写无关内容。

性能与可靠性：

- 全库公式约百级条目，先统一清单再复用，避免重复扫描。
- WSL 构建只做一次，复用同一份 `temp_test/fac_src/` 产物运行全部示例。
- FeL 为主要时间瓶颈，单独运行并记录起止时间与输出；rmatrix 为主要稳定性瓶颈，单独调试并记录崩溃点与解决过程。
- 回归比对优先使用已有 `check.py`；没有参考表的示例只记录实际输出与物理合理性检查。

## Implementation Notes

- 只写入 README.md 与 `temp_test/` 内文件，不修改原树源码、论文、构建脚本或数据文件。
- 原树 478 个非 README 文件继续保持只读；不得解除只读属性。
- 根 README 末尾英文原文附录必须逐字保留。
- 副本已有改动包括脚本 CRLF 转 LF、`sysdef.h` 中定义 `f2cFortran`；后续任何新增改动都要写入相关 README，说明改动原因、物理数值意义以及对结果的影响。
- 每个示例 README 至少应包含：
- 物理场景与科学问题；
- 涉及的物理效应和 LaTeX 公式；
- 脚本、Makefile、ref 数据逐文件说明；
- pfac 或 sfac API 调用链；
- Mermaid FAC 使用流程图；
- Mermaid 数据流图；
- 实际运行命令、环境、参数、耗时或日志路径；
- 输出文件清单与物理量含义；
- 与 ref 的比对结果；
- 已知限制和副本改动说明。
- 发现公式错误时直接就地修正，不单独产出报告文档。
- 最终检查相对链接、代码围栏、Mermaid 代码块闭合和 README 数量。

## Architecture Design

文档与复现体系分为四层：

- 文献层：`doc/manual.tex`、`doc/papers/*.tex` 与联网权威资料，用于确认物理公式和标准定义。
- 源码层：`faclib/`、`modqed/`、`coul/`、`ionis/`、`mpfun/`、`python/`、`sfac/` 与示例脚本，用于确认实际实现、单位、系数、索引和 API。
- 执行层：`temp_test/fac_src/` 构建副本，`temp_test/runs/` 各示例独立运行目录，`temp_test/logs/` 日志，`temp_test/scripts/` 批量执行与诊断脚本。
- 文档层：38 份 README.md；其中 10 份示例 README 深度重写，其余 README 按公式核查结果小范围修正。

数据链路：

输入脚本与组态 到 pfac 或 sfac 调用 到 中间二进制表 到 文本输出表 到 ref 回归比对 到 README 中的执行记录与物理说明。

## Directory Structure

本次不新增正式文档文件；修改范围如下。

```text
fac/
├── README.md
│   # [核查并按需修正] 总公式索引、示例入口、复现状态、副本改动总说明
├── faclib/README.md
│   # [核查并按需修正] 核心物理公式、单位换算、桥接说明
├── coul/README.md
│   # [核查并按需修正] 库仑函数、连续态、特殊函数公式
├── modqed/README.md
│   # [核查并按需修正] QED 公式、前因子、出处
├── ionis/README.md
│   # [核查并按需修正] 电离平衡和拟合公式
├── mpfun/README.md
│   # [核查并按需修正] 高精度与 Legendre 递推公式
├── python/README.md
│   # [核查并按需修正] PFAC 接口物理公式与 API
├── sfac/README.md
│   # [核查并按需修正] SFAC 命令接口与物理公式
├── doc/README.md
│   # [核查并按需修正] 文档索引与实现归属
├── doc/papers/README.md
│   # [核查并按需修正] 论文公式索引与链接检查
├── demo/README.md
│   # [重写] 示例总览、10 个示例索引、执行状态、公共流程与数据流
├── demo/structure/README.md
│   # [重写] 原子结构示例：物理场景、公式、流程图、数据流图、执行记录
├── demo/structure/ref/README.md
│   # [核查并按需修正] 能级与跃迁表单位、列含义、比对结果
├── demo/excitation/README.md
│   # [重写] 电子碰撞激发示例：碰撞强度、截面、速率、流程图、数据流图
├── demo/excitation/ref/README.md
│   # [核查并按需修正] CE 表单位与比对结果
├── demo/ionization/README.md
│   # [重写] 碰撞电离示例：截面、速率、流程图、数据流图
├── demo/ionization/ref/README.md
│   # [核查并按需修正] CI 表单位与比对结果
├── demo/pirr/README.md
│   # [重写] 光电离与辐射复合示例：Milne 关系、流程图、数据流图
├── demo/pirr/ref/README.md
│   # [核查并按需修正] PI/RR 表单位与比对结果
├── demo/aidr/README.md
│   # [重写] 自电离与双电子复合示例：AI、DC、DR、流程图、数据流图
├── demo/aidr/ref/README.md
│   # [核查并按需修正] AI 表单位、比对容差、比对结果
├── demo/NeL/README.md
│   # [重写] Ne VIII 碰撞辐射模型示例：CRM、谱合成、流程图、数据流图
├── demo/NeL/ref/README.md
│   # [核查并按需修正] CRM 与谱表公式、单位、比对结果
├── demo/FeL/README.md
│   # [重写] Fe-L 壳谱示例：完整流程、长耗时执行记录、物理与数据流
├── demo/polariz/README.md
│   # [重写] 谱线偏振示例：偏振度、取向参数、流程图、数据流图
├── demo/polariz/ref/README.md
│   # [核查并按需修正] 偏振与布居数据公式
├── demo/rmatrix/README.md
│   # [重写] Dirac R 矩阵示例：匹配理论、调试改动、物理意义、流程图、数据流图
├── demo/tests/README.md
│   # [重写] 哈密顿量、Maxwell、CRM 诊断示例：公式、流程、数据流、执行记录
├── demo/tests/ref/README.md
│   # [核查并按需修正] 诊断数据公式与单位
├── temp_test/fac_src/
│   # [可修改副本] 仅此处允许构建和调试改动，原树不动
├── temp_test/runs/
│   # [NEW 或更新] 10 个示例独立运行目录与输出
├── temp_test/scripts/
│   # [NEW 或更新] 批量执行、诊断、检查脚本
└── temp_test/logs/
    # [NEW 或更新] 构建、运行、比对、调试日志
```

## SubAgent

- **code-explorer**
- Purpose: 批量读取 38 份 README、论文手册、源码和示例脚本，建立公式清单并提取实现证据。
- Expected outcome: 形成逐条公式的 README 写法、文献依据、源码位置、单位系数差异、示例流程和数据流依据。

## Skill

- **agent-browser**
- Purpose: 在静态抓取不足时访问权威论文、教材或函数文档页面，提取标准公式和物理定义。
- Expected outcome: 为仓库内无法完全确认的公式提供外部交叉验证依据，最终仍以源码实现为准。
- **lsp-code-analysis**
- Purpose: 对 C 与 Python 核心符号进行定义、引用和调用链分析，辅助确认示例 API 与公式实现路径。
- Expected outcome: 明确关键函数、宏、结构体和调用路径，减少纯文本检索造成的误判。