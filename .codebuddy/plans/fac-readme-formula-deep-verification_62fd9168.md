---
name: fac-readme-formula-deep-verification
overview: 对全部 38 份中文 README 进行第二轮深度公式核查：逐公式追踪源码具体语句/系数/单位/张量指标，结合仓库与联网文献交叉验证，并在根目录新建的 temp_test/ 中构建源码副本、调用脚本做数值复现；原始源码只读可执行不可修改，发现问题仅就地修正 README，标准式保留并标注源码差异。
todos:
  - id: inventory-all
    content: 使用 [subagent:code-explorer] 盘点 38 份 README 全部公式
    status: completed
  - id: literature-check
    content: 使用 [subagent:code-explorer] 与 [skill:agent-browser] 核对仓库及联网文献
    status: completed
    dependencies:
      - inventory-all
  - id: source-core
    content: 使用 [skill:lsp-code-analysis] 追踪核心库公式源码实现
    status: completed
    dependencies:
      - inventory-all
  - id: source-other
    content: 使用 [subagent:code-explorer] 核对接口、demo、数据和文档源码
    status: completed
    dependencies:
      - inventory-all
  - id: numeric-repro
    content: 在 temp_test/ 构建副本并执行数值复现
    status: completed
    dependencies:
      - literature-check
      - source-core
      - source-other
  - id: apply-and-verify
    content: 就地修正 README 并完成最终一致性验证
    status: completed
    dependencies:
      - numeric-repro
---

## 用户需求

对全部 38 份中文 README 进行第二轮深度公式核查：继续搜索相关文献核对公式，并阅读源码核对公式；范围是全量复核，不限上一轮已修正或带不确定标注的文件。

## 产品概述

逐份检查公式、拟合式、单位换算、系数、索引、出处与源码对应关系。核查深度为 A+B：逐公式追踪源码语句，并在根目录新建 temp_test/ 中构建源码副本、调用脚本做数值复现。

## 核心要点

- 原始源码只允许读取和执行，不可修改；不在原树生成构建产物。
- 每份 README 都需形成核查结论；无公式文档确认无需公式。
- 发现错误仅就地修正 README，不新增核查报告文档。
- 源码无字面公式但物理上有效的标准式继续保留，并明确标注源码差异、近似与归一化约定。

## 技术栈与约束

- 文档对象：38 份 Markdown 中文 README，公式使用 LaTeX 行内 `$... 与独立 `$...。
- 文献来源：`doc/manual.tex`、`doc/papers/*.tex`，以及通过工具层 `web_search`、`web_fetch` 获取的权威论文和教材；动态页面必要时使用 `agent-browser`。
- 源码对象：FAC 的 C 核心库、Fortran 数值库、Python 与 SFAC 接口、demo 脚本和参考数据。
- 只读约束：478 个非 README 原始文件当前为只读；不得解除、覆盖或修改。只写 README.md 和 temp_test/ 内新文件。
- 数值复现约束：原树无 `libfac.a` 与 `.o`，且顶层 `Makefile.in` 使用 `cd blas; make` 等原地构建，`demo/Make.common` 也在当前目录写结果，因此不能直接原树构建。按用户指定，在根目录建立 `temp_test/`，复制源码到 `temp_test/fac_src/` 后构建与执行。

## 实施策略

采用“全量清单 → 文献交叉核对 → 源码逐行核对 → temp_test 数值复现 → 就地修正 → 最终验证”的流程。

- 源码优先：文献标准式只用于确认物理含义和发现错误，最终 README 写法以源码实现为准。
- 标准式保留：R 矩阵、MBPT、二次 Stark 等保留公式，但补充源码实际算法、近似、单位与归一化差异。
- 小范围修改：只改错误公式、系数、单位、出处和必要说明，不重写整篇 README。
- 数值复现控制成本：只做一次构建，复用同一副本运行 structure、excitation、ionization、pirr、aidr、tests 等小算例；FeL 等高耗时示例不作为默认复现对象。
- 构建失败兜底：若编译器、Python 版本或依赖导致构建失败，在 temp_test/scripts/ 中用独立 Python 数值计算并读取 ref 数据验证；不得伪造结果。

## temp_test 目录结构

```text
temp_test/
├── fac_src/                  # 原源码树完整副本，副本可写用于 configure/make
│   └── ...                   # 保持与原树一致的目录结构
├── runs/                     # 数值复现工作目录
│   ├── structure/
│   ├── excitation/
│   ├── ionization/
│   ├── pirr/
│   ├── aidr/
│   ├── tests/
│   ├── ref_compare/          # 参考数据与数值对比输出
│   └── standalone/           # 独立公式数值验证输出
├── scripts/                  # 临时校验脚本，不写入 README 文档体系
└── logs/                     # configure、make、demo 与复现日志
```

执行约定：

- 从原树复制到 `temp_test/fac_src/`，不软链原树；构建产物只留在副本。
- 各 demo 算例复制到 `temp_test/runs/<case>/` 后运行，必要时设置 `PYTHONPATH` 指向 `temp_test/fac_src/` 的 PFAC 构建产物。
- 参考结果从副本的 `demo/*/ref/` 读取，输出留在 `temp_test/runs/<case>/`。
- `temp_test/` 是用户要求保留的测试区；最终 git 状态除该目录外只允许 README.md 变更。

## Implementation Notes

- 只修改 README.md；源码、`.tex`、`.f`、`.c`、`.h`、构建脚本、数据文件及旧 `demo/README` 一律不改。
- 根 README 末尾英文原文附录已与 `git HEAD` 逐字一致，修正时不得破坏。
- 核查证据只作为执行上下文，不落盘为新的核查报告。
- 源码定位以函数名和关键语句为主，行号作为辅助证据，避免因环境差异误判。
- 最终验证包括：38 份 README 全覆盖、错误公式无残留、原树源文件仍只读且未修改、英文附录逐字一致、除 `temp_test/` 外仅 README.md 变更。

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 批量读取 38 份 README、仓库文献、源码与参考数据，建立逐公式清单并提取实现证据。
- Expected outcome: 得到每条公式的 README 写法、文献依据、源码位置、系数单位差异和可执行的修正建议。

### Skill

- **lsp-code-analysis**
- Purpose: 定位 C 与 Python 核心符号定义、引用和调用关系，辅助逐行核对公式对应实现。
- Expected outcome: 明确关键函数、结构体、宏与调用路径，减少纯文本检索造成的误判。

- **agent-browser**
- Purpose: 在静态抓取不足时访问权威论文或教材页面，提取标准公式和物理定义。
- Expected outcome: 为仓库内无法完全确认的公式提供外部交叉验证依据，最终仍以源码实现为准。