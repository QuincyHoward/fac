---
name: fac-readme-formula-verification
overview: 对全部 38 份中文 README 逐份核查公式：先分类是否应含公式，再用仓库论文/手册与联网文献核对标准形式，再以 FAC 源码实现为最终依据逐条验证，发现错误直接修正 README（不出报告、不改源码）。
todos:
  - id: inventory-readmes
    content: Use [subagent:code-explorer] 盘点38份README公式与出处
    status: completed
  - id: verify-literature
    content: Use [subagent:code-explorer] 核对仓库论文手册并使用 [skill:agent-browser] 联网查证
    status: completed
    dependencies:
      - inventory-readmes
  - id: verify-core-source
    content: Use [subagent:code-explorer] 核对核心物理库公式与源码实现
    status: completed
    dependencies:
      - verify-literature
  - id: verify-other-source
    content: Use [subagent:code-explorer] 核对接口、demo、数据与文档README公式
    status: completed
    dependencies:
      - verify-literature
  - id: apply-corrections
    content: 直接修正有问题的README正文与出处
    status: completed
    dependencies:
      - verify-core-source
      - verify-other-source
  - id: final-check
    content: 验证38份覆盖且仅README发生变更
    status: completed
    dependencies:
      - apply-corrections
---

## 用户需求

对 FAC 源码树中已建立的 38 份中文 `README.md` 进行公式核查，确保物理公式、数值拟合式与源码实现一致、可追溯、可直接用于理解代码。

## 产品概述

本次工作不新增独立核查报告，只直接修正有问题的 `README.md` 正文。核查范围覆盖全部 38 份 README：含公式的逐条验证，当前不含公式的逐份确认是否确实无需公式。

## 核心功能

- 逐份检查 38 个目录的 `README.md`，建立公式与物理/数值主题清单。
- 先用仓库内 `doc/manual.tex`、`doc/papers/*.tex` 核对理论来源，再联网检索权威论文或教材核对标准形式。
- 阅读 FAC 源码中的真实函数、子程序、系数、单位换算和实现近似，逐条验证 README 公式。
- 当文献标准形式与源码实现不一致时，以源码实现为准，并在 README 中说明差异。
- 只修改 `README.md`；不修改源码、手册、论文、构建脚本、数据文件，也不创建报告文档。
- 保持原有中文文档结构、相对链接、逐文件说明与源码对应表，只做必要的公式、系数、单位、条件和出处修正。

## Tech Stack Selection

- 文档对象：Markdown 格式的中文 `README.md`，数学公式使用 LaTeX 行内 `$... 与独立 `$...。
- 理论资料：仓库内 `doc/manual.tex`、`doc/papers/*.tex`，以及联网可访问的 FAC 相关论文、权威原子物理教材和公开标准公式。
- 源码对象：FAC 核心 C 库、Fortran 数值库、Python/SFAC 接口脚本、demo 示例脚本。
- 工作约束：上一阶段已将 478 个非 README 原始文件设为只读；源码仍可读取，但不解除只读、不修改内容。`demo/README` 旧英文文件保持不动。

## Implementation Approach

采用「清单化核查 → 文献核对 → 源码核对 → 就地修正 → 最终验证」的流程。先用只读探索汇总每份 README 的公式数量、公式主题、声称出处与源码对应；随后按主题并行核对仓库文献和联网资料；最后以源码实现作为最高优先级，直接修改错误公式。

关键决策：

- **源码优先**：README 描述必须与 FAC 实际实现一致。文献公式只用于确认标准物理含义和发现可能错误；若源码采用近似、特殊单位或不同归一化，以源码为准并说明。
- **不落盘报告**：核查清单只作为执行过程中的临时工作记忆，不新增 Markdown 文档，避免污染 38 份 README 体系。
- **全覆盖但不强行加公式**：数值库、CI 配置、纯数据目录逐份确认是否需要公式；无明确物理公式需求时保持原样。
- **小范围修改**：仅修正错误公式、错误系数、错误单位、错误近似条件、错误出处和不一致描述，不重写整篇 README。

性能与可靠性：公式-rich 文件集中在 `faclib/`、`modqed/`、`coul/`、`ionis/`、`doc/papers/` 和 demo 示例，按主题分组并行核查；其余 README 做快速确认。源码核对以函数名和关键语句为准，避免依赖可能变化的行号。

## Implementation Notes

- 只写入 `README.md` 文件，任何源码、`.tex`、`.f`、`.c`、`.h`、`.py`、构建脚本、数据文件和 `demo/README` 均不得修改。
- 不改文件只读属性；若工具因源码只读失败，应停止写入源码方向的操作，只修改 README。
- 对每个公式执行三向核对：README 当前写法、仓库文献或联网标准形式、源码实际实现。
- 重点核对以下源码位置：`faclib/structure.c`、`radial.c`、`excitation.c`、`ionization.c`、`recombination.c`、`transition.c`、`polarization.c`、`crm.c`、`rmatrix.c`、`rates.c`、`interpolation.c`；`modqed/dirac.f`、`se_pot.f`、`fse_dat.f`、`uehling.f`、`wk.f`；`ionis/rrfit.f`、`drfit.f`、`nrrfit.f`、`ndrfit.f`、`phfit2.f`；`coul/coulcc.f`、`cmultip.f`、`dcoul.f`、`mohrfin.f`。
- 对 README 中已标注「源码未给出显式公式」的位置，必须完成源码核对后更新为准确表述，说明源码中实际采用的拟合、插值、近似或量纲约定。
- 联网资料只作为标准形式参考，不覆盖源码事实；若联网资料与源码不同，在 README 中写明差异原因。
- 修改后验证：38 份 README 全部覆盖；`git status` 仅显示 README 变更；源码仍为只读；英文旧 `demo/README` 未变。

## Directory Structure

本次不新增文件；38 份 README 全部为核查对象，按下表处理。

```text
fac/
├── README.md                         # [核查，按需修改] 总览中的行内公式、物理索引与出处一致性
├── .circleci/README.md               # [确认] 确认无需公式，保持原样
├── blas/README.md                    # [确认] 数值库接口说明，确认无需物理公式
├── ci/README.md                      # [确认] 环境配置说明，确认无需公式
├── coul/README.md                    # [重点核查，按需修改] 库仑波函数、连续态、特殊函数公式与源码对应
├── faclib/README.md                  # [重点核查，按需修改] 原子结构、碰撞、复合、跃迁、CRM、R 矩阵等公式
├── ionis/README.md                   # [重点核查，按需修改] 电离平衡、Maxwell 速率、Verner 等拟合式
├── lapack/README.md                  # [确认] 线性代数库说明，确认无需物理公式
├── minpack/README.md                 # [确认] 优化库说明，确认无需物理公式
├── modqed/README.md                  # [重点核查，按需修改] Dirac 方程、自能、Uehling、WK 势公式
├── mpfun/README.md                   # [核查，按需修改] 高精度与缔合 Legendre 函数方程及源码对应
├── ode/README.md                     # [确认] ODE 求解器说明，确认无需物理公式
├── python/README.md                  # [重点核查，按需修改] PFAC 接口说明中的偏振、CRM、速率公式
├── quadpack/README.md                # [确认] 积分库说明，确认无需物理公式
├── sfac/README.md                    # [核查，按需修改] 命令行接口中 CRM、偏振等物理公式
├── toms/README.md                    # [确认] TOMS 数值例程说明，确认无需物理公式
├── demo/
│   ├── README.md                     # [重点核查，按需修改] 示例总览中的物理效应索引公式
│   ├── aidr/
│   │   ├── README.md                 # [核查，按需修改] 自电离与双电子复合公式
│   │   └── ref/README.md             # [核查，按需修改] 参考数据对应物理量与公式
│   ├── excitation/
│   │   ├── README.md                 # [核查，按需修改] 碰撞强度、截面、速率系数公式
│   │   └── ref/README.md             # [核查，按需修改] CE 表格物理量公式
│   ├── FeL/README.md                 # [核查，按需修改] Fe-L 壳谱形成与 CRM 公式
│   ├── ionization/
│   │   ├── README.md                 # [核查，按需修改] 碰撞电离截面与速率公式
│   │   └── ref/README.md             # [核查，按需修改] CI 表格物理量公式
│   ├── NeL/
│   │   ├── README.md                 # [核查，按需修改] Ne VIII CRM 与谱合成公式
│   │   └── ref/README.md             # [核查，按需修改] CRM 与谱数据公式
│   ├── pirr/
│   │   ├── README.md                 # [核查，按需修改] 光电离与辐射复合公式
│   │   └── ref/README.md             # [核查，按需修改] PI/RR 参考数据公式
│   ├── polariz/
│   │   ├── README.md                 # [核查，按需修改] 谱线偏振公式
│   │   └── ref/README.md             # [核查，按需修改] 偏振与布居数据公式
│   ├── rmatrix/README.md             # [核查，按需修改] Dirac R 矩阵与碰撞强度公式
│   ├── structure/
│   │   ├── README.md                 # [核查，按需修改] 原子结构、跃迁率公式
│   │   └── ref/README.md             # [核查，按需修改] 能级与跃迁表公式
│   └── tests/
│       ├── README.md                 # [核查，按需修改] 哈密顿量、Maxwell、CRM 诊断公式
│       └── ref/README.md             # [核查，按需修改] 诊断数据对应公式
└── doc/
    ├── README.md                     # [核查，按需修改] 文档索引中的公式与出处
    ├── misc/README.md                # [确认] 开发工具说明，确认无需公式
    └── papers/README.md              # [重点核查，按需修改] 论文主题、理论公式与源码对应
```

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 批量读取 38 份 README、仓库论文、手册和源码，提取公式清单、出处、源码函数与实现细节。
- Expected outcome: 形成完整且可执行的逐条核查依据，明确指出哪些 README 公式需要修正及修正内容。

### Skill

- **agent-browser**
- Purpose: 在需要联网核对时浏览权威论文、教材或公开资料页面，提取标准公式与物理定义。
- Expected outcome: 为仓库内无法完全确认的公式提供外部标准形式参考，最终仍由源码实现决定 README 写法。