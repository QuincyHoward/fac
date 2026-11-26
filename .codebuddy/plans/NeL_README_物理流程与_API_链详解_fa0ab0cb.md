---
name: NeL README 物理流程与 API 链详解
overview: 以中文重构 demo/NeL/README.md：新增多张带输入输出与物理含义标注的 Mermaid 图、逐 API 详解“关键 API 链”，并系统核查/修正 NeL 及直接相关文档中的事实性错误。
todos:
  - id: redesign-nel-mermaid
    content: 用 [subagent:code-explorer] 核查源码，重构 NeL/README.md 第 5 节新增 5 张 Mermaid 图
    status: completed
  - id: detail-api-chain
    content: 详解 ne.py 与 spec.py 关键 API 链的参数、C 层动作与物理含义
    status: completed
    dependencies:
      - redesign-nel-mermaid
  - id: fix-nel-facts
    content: 修正 NeL/README.md 中公式、单位、列语义、温度、MPI 等事实错误
    status: completed
    dependencies:
      - redesign-nel-mermaid
  - id: sync-ref-doc
    content: 修正 ref/README.md 的 A/gf 公式、r.energy 单位与 SP 列语义
    status: completed
    dependencies:
      - fix-nel-facts
  - id: sync-related-docs
    content: 统一 demo/README.md、根 README.md、demo/tests/README.md 的 NeL 口径与交叉引用
    status: completed
    dependencies:
      - fix-nel-facts
---

## 产品概述

将 `demo/NeL` 打造成便于物理研究员理解的 FAC 入门示例文档。通过多张 Mermaid 图，清晰展示 `ne.py` 与 `spec.py` 每个处理环节的输入、输出及物理含义（处理了什么物理效应、采用什么物理公式、得到什么物理量），并详细解释“关键 API 链”的具体作用。

## 核心功能

- 新增多张 Mermaid 图：FAC 使用流程、数据流、物理过程链、ne.py 与 spec.py 各自的 API 调用链，节点需标注输入/输出/物理效应/公式/物理量。
- 详解“关键 API 链”：逐个说明每个 API 的参数含义、C 层实际动作、物理计算内容；覆盖 `SetAtom`/`Config`/`ConfigEnergy`/`OptimizeRadial`/`Structure`/`MemENTable`/`PrintTable`/`TRTable`/`CETable`/`InitializeMPI` 及 CRM 侧 `AddIon`/`SetBlocks`/`SetEleDist`/`SetTRRates`/`SetCERates`/`SetAbund`/`SetEleDensity`/`InitBlocks`/`SetIteration`/`LevelPopulation`/`SpecTable`/`RateTable`/`DumpRates`/`spm.get_complexes`。
- 仔细核查并修正事实性错误：A/gf 公式口径、`r.energy` 单位、SP 表列语义、API 链文本错误、温度标度含义、`SetBlocks(-1)` 语义、密度单位出处、`InitializeMPI` 术语、NLEV 数量等。
- 同步核查并修正直接相关文档：`demo/NeL/ref/README.md`、`demo/README.md`、根 `README.md`、`demo/tests/README.md`，保持 photons/s 与能量发射率口径一致，必要时增加交叉引用。

## 技术栈

- 文档格式：Markdown（简体中文正文），Mermaid 流程图/数据流图（```mermaid 代码块）。
- 核查依据：FAC 源码（`python/fac.c`、`python/pcrm.c`、`faclib/*.c`、`python/rfac.py`、`demo/check.py`）与手册 `doc/manual.tex`。

## 实现方案

以现有 `demo/NeL/README.md` 的九节结构为骨架进行增强，不改动任何源码、脚本或参考数据文件。核心策略：

1. **Mermaid 图设计**（插入/替换第 5 节）：

- 5.1 FAC 使用总览流程图：从 `ne.py` 到 `spec.py` 到 `make check`，节点标注输入（如 `z=10, nele=3, nmax=5`、`Te=125 eV`、`ne=1e10 cm^-3`）与输出（`Ne03a.en/.tr/.ce/.sp/.rt`、`Ne03b.ham`）。
- 5.2 ne.py API 链与数据流图：`SetAtom → Config → ConfigEnergy/OptimizeRadial → Structure → MemENTable/PrintTable → TRTable → CETable`，每个节点注明物理效应（自洽场径向势、CI 对角化、辐射跃迁、碰撞激发）与输出物理量（能级/混合系数、A 与 gf、碰撞强度 Ω 与截面）。
- 5.3 spec.py API 链与数据流图：`AddIon → SetBlocks → SetEleDist → SetTRRates → SetCERates → SetAbund → SetEleDensity → InitBlocks → SetIteration → LevelPopulation → SpecTable/PrintTable → spm.get_complexes → RateTable → DumpRates`，节点注明输入（二进制表、125 eV Maxwell、密度）与输出（稳态布居、谱线发射率 photons/s、速率矩阵）。
- 5.4 CRM 物理过程网络图：展示 TR/CE/RR/AI/CI 各过程在稳态方程 $\sum_j n_j R_{j\to i} - n_i\sum_j R_{i\to j}=0$ 中的角色，及 `Ne03a.rt` 中各列贡献。
- 5.5 从属文档与比对流图：展示脚本输出 → ASCII 表 → `check.py`/`rfac.read_*` → `ref/` 基准 → `Tests passed!`，标注 `Ne03b.ham` 二进制需 `read_ham()` 解析。

2. **API 链详解**（新增第 4 节内容，替换现有简略链）：
采用表格+文字说明，逐 API 给出：函数签名与 demo 实参、Python/C 实现位置、参数物理含义、C 层实际动作、输出物理量。重点澄清易混淆点：

- `SetEleDist(0,125,-1,-1)`：0=Maxwell，125 eV，-1 触发表内默认 `Emin=1.25e-18 eV`、`Emax=1.25e4 eV`。
- `SetBlocks(-1)`：负丰度开关，仅保留同离子内过程，非块数。
- `SetTRRates(0)`：仅正向辐射率；`SetCERates(1)`：含碰撞退激发逆过程。
- `SpecTable(fn,0)`：rrc=0 输出布居+线发射率，不含复合连续谱。
- `DumpRates(fn,-1,m,-1,1)`：k=-1 所有离子，m=0/1/3 分别为能级信息/辐射率/碰撞激发率，imax=-1 全部能级，a=1 ASCII。

3. **事实核查与修正清单**（基于已确认事实）：

- A/gf 公式：改用 `manual.tex:601-620` 口径 $gA=2\alpha^3\omega^2 gf$，$gf=(2L+1)^{-1}\omega(\alpha\omega)^{2L-2}|M|^2$；或明确标注原公式为通用多极形式并补充 FAC 实际口径。
- `r.energy` 单位：`crm.c:4488` 中 `r.energy=e` 为 Hartree，ASCII 的 eV 来自 `dbase.c:6955-6956` verbose 打印时乘 `HARTREE_EV`；修正“e 已乘 HARTREE_EV”的错误说法。
- SP 表列语义：说明 `PrintSPTable`（`dbase.c:6963-6964`）实际输出 8 列（upper, lower, energy, strength, rrate, trate, wimp, wstk；utr=1 时 9 列），而 `rfac.read_sp` 按 6 列解析为比较字段；文档需明确“文件实际列”与“check.py 比较口径”双口径。
- 修正 API 链文本 `Config('g%d'%n,'1s2 2*1 %d*1'%(n))` → 实际 `ne.py:30` 为 `1s2 2*0 %d*1`（nele-3=0），g2 才是 `1s2 2*1`。
- 温度公式注明 $q=1+z-nele=8$ 电荷态经验标度，FAC 内部只收到 125 eV Maxwell 分布。
- 密度单位出处改为 `manual.tex:4352-4354`（`SetEleDensity`），非 `:4516-4519`（pol 模块 `SetDensity`）。
- `InitializeMPI(2)` 注明是 MPI 初始化（脚本注释“openmp”不准确）。
- `ref/Ne03a.en` 的 NBlocks=3、三块 NLEV=8/7/9（共 24 能级），修正“NLEV=8”不完整表述。
- `ref` 文件头为 FAC 1.1.5 而 `demo/README` 称基准 1.1.4，保留矛盾说明。

4. **相关文档同步**：

- `demo/NeL/ref/README.md`：修正 A/gf 公式、`r.energy` 单位、SP 列语义、NLEV 数量，与 NeL README 保持一致。
- `demo/README.md:124,128`：统一 photons/s 与能量发射率口径（`SpecTable` 输出 photons/s，能量谱需另乘 $h\nu$）。
- `README.md`（根）：检查 NeL 引用（第 98、118、137 行）是否需要补充交叉链接或口径说明。
- `demo/tests/README.md:181`：确认 photons/s 口径与 NeL 一致，必要时加交叉引用。

## 实现注意事项

- **不改动源码/脚本/数据**：仅修改 Markdown 文档；`README.md` 中“副本改动说明”保留原样。
- **Mermaid 语法**：节点 label 中避免未转义的特殊字符；公式使用 `$... 行内 LaTeX 放在节点外文字中；代码块统一使用 ```mermaid。
- **引用路径**：保持相对链接正确（如 `../README.md`、`../../doc/manual.tex`、`python/rfac.py:1085`）。
- **验证方式**：修改后逐条对照源码行号与 ref 文件头部；检查所有 Mermaid 代码块可被 Mermaid 渲染（节点无语法错误）；确认相关文档口径一致。

## 目录结构

```
R/
├── README.md                         # [MODIFY] 根 README，检查/补充 NeL 交叉引用与口径说明（第 98/118/137 行附近）
├── demo/
│   ├── README.md                     # [MODIFY] 统一 photons/s vs 能量谱口径（第 124/128 行），补充 NeL 链接
│   ├── NeL/
│   │   ├── README.md                 # [MODIFY] 主文档：重构第 4/5 节，新增 5 张 Mermaid 图与 API 链详解，修正事实错误
│   │   └── ref/
│   │       └── README.md             # [MODIFY] 修正 A/gf 公式、r.energy 单位、SP 列语义、NLEV 数量
│   └── tests/
│       └── README.md                 # [MODIFY] 确认 photons/s 口径一致，必要时加交叉引用
```

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 在实施阶段对关键 API 的 C 层实现、物理公式口径、ref 文件头部字段进行二次核查，确保文档修正与源码一致。
- Expected outcome: 产出精确的源码行号与字段语义映射，支撑文档中所有“源码依据”声明的准确性。