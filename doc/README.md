# `doc/` —— FAC 文档与理论资料入口

## 1. 目录定位

`doc/` 集中存放 FAC（Flexible Atomic Code）的**用户手册源码**、**构建规则**以及两组专题资料：

- `manual.tex`：FAC 官方用户手册的 LaTeX 源文件（约 5000 行），是理解输入接口、输出表格格式、FAQ 与物理近似的权威一手资料；
- `Makefile`：手册 PDF 的构建规则；
- [`misc/`](misc/README.md)：开发协作与跨程序接口工具说明（jj 耦合转 LS 耦合、Git 提交流程）；
- [`papers/`](papers/README.md)：描述 FAC 理论背景的论文源码与编译产物（structure、excitation、ionization、pirr、aidr、ebfield、mcross 等主题）。

本目录本身不含可执行计算代码，但 `manual.tex` 与 `papers/` 中的公式是整套 README 体系中物理公式与源码对应关系的主要依据。

## 2. 文件组织与逐文件说明

| 条目 | 类型 | 功能 |
|---|---|---|
| `manual.tex` | LaTeX 主文档 | FAC 手册源码，含概览、快速入门、输出文件二进制/ASCII 格式、函数参考、FAQ 五大部分；源码中的公式与注释被各 README 引用为公式出处 |
| `Makefile` | 构建脚本 | 目标 `doc` 依次执行 `pdflatex manual` → `bibtex manual` → `makeindex manual` → 两次 `pdflatex manual` 生成 `manual.pdf`；`clean` 清理 `*~` |
| [`misc/`](misc/README.md) | 子目录 | `jj2ls.md`、`gitcommit.md` 两篇开发文档 |
| [`papers/`](papers/README.md) | 子目录 | 理论论文源码 `.tex` 与产物 `.dvi`/`.ps`/`.eps`/`.pdf`、参考文献 `.bib` |

## 3. `manual.tex` 章节导览

### 3.1 Overview（概览）
- `What Is FAC`：FAC 的定位、相对论框架、连续过程采用扭曲波（DW）近似等基本说明；手册指出 VP 与 SE 采用屏蔽氢样近似。
- `Obtain and Install FAC`：源码获取与安装流程，与根目录 README 的原始安装章节对应。
- `Quick Start`：分别以 SFAC 与 PFAC 接口逐行讲解类氖铁原子结构算例，是 [`demo/structure/`](../demo/structure/README.md) 的权威注解。

### 3.2 Description of Output Files（输出文件说明）
定义所有二进制表格头结构与记录结构：`F_HEADER`、`EN_HEADER`/`EN_RECORD`、`TR_HEADER`/`TR_RECORD`/`TR_EXTRA`、`CE_*`、`RR_*`、`AI_*`、`CI_*`、`SP_*`、`RT_*`、`DR_*`、`AIM_*`、`CIM_*`、`RO_*`、`CX_*`；随后给出对应的 ASCII 表格 `DB_EN`、`DB_TR`、`DB_CE`、`DB_RR`、`DB_AI`、`DB_CI`、`DB_SP`、`DB_RT`、`DB_DR`、`DB_AIM`、`DB_CIM`、`DB_RO`、`DB_CX` 的列定义。

这些定义是解读 [`demo/*/ref/`](../demo/README.md) 参考数据文件列含义的直接依据。

### 3.3 FAC Function Reference（函数参考）
按模块列出 API：`fac`（核心模块，变量与函数）、`crm`（碰撞辐射模型）、`pol`（谱线偏振）、`util`（工具函数）、`config`（电子组态语法）、`const`（物理常数）、`table`（文本表格）、`atom`（`fac` 的应用封装）、`spm`（`crm` 的应用封装）。对应源码见 [`python/`](../python/README.md) 与 [`sfac/`](../sfac/README.md)。

### 3.4 FAQ
涵盖 General、Atomic Structure、Collisional Excitation 等主题，说明 Hamiltonian、能级、QED 修正、截面与速率等常见问题的处理方式。

## 4. 物理效应与公式索引

本目录不实现物理计算，但提供公式出处。主要效应及其理论文档位置：

| 物理效应 | 手册/论文出处 | 实现源码 | 示例 |
|---|---|---|---|
| 相对论原子结构（Dirac 方程、SCF、CI） | `papers/structure.tex`、`manual.tex` FAQ | [`faclib/structure.c`](../faclib/README.md)、`orbital.c`、`radial.c` | [`demo/structure/`](../demo/structure/README.md) |
| 电子碰撞激发 $\Omega_{ij}$、$\sigma_{ij}=\pi\Omega_{ij}/(g_i k_i^2)$ | `papers/excitation.tex` | `faclib/excitation.c` | [`demo/excitation/`](../demo/excitation/README.md) |
| 电子碰撞电离 | `papers/ionization.tex` | `faclib/ionization.c` | [`demo/ionization/`](../demo/ionization/README.md) |
| 光电离与辐射复合（Milne 关系） | `papers/pirr.tex` | `faclib/recombination.c` | [`demo/pirr/`](../demo/pirr/README.md) |
| 自电离与双电子复合 | `papers/aidr.tex` | `faclib/recombination.c`、`crm.c` | [`demo/aidr/`](../demo/aidr/README.md) |
| 外场与跃迁 | `papers/ebfield.tex`、`mcross.tex` | `faclib/excitation.c`、`faclib/polarization.c`、`faclib/transition.c` | [`demo/polariz/`](../demo/polariz/README.md) |

更完整的逐篇论文清单、文件清单与公式说明见 [`papers/README.md`](papers/README.md)。

## 5. 使用与构建

```bash
cd doc
make          # 生成 doc/manual.pdf
```

顶层 `Makefile.in` 的 `doc` 目标等价于上述命令。CircleCI 的 `.circleci/config.yml` 使用 `koppor/texlive` 镜像执行 `cd doc; make`，并在 `master` 分支把 `manual.pdf` 发布到 `release-pdf` 分支（详见 [`.circleci/README.md`](../.circleci/README.md)）。

## 6. 导航

## 7. README 维护记录（自底向上）

- **定位与职责**：`doc/` 是手册、论文与输出表格式的文档层，不参与核心构建。
- **底层依据**：`manual.tex`、`papers/*.tex`、`misc/` 实用说明；公式最终以各源码目录 README 的核查结果为准。
- **输入/输出**：输入 LaTeX 源与图表；输出 `manual.pdf`、论文 DVI/PS/PDF 与格式说明。
- **验证与回归**：`cd doc && make` 或顶层 `make doc`；CircleCI 使用 TeX Live 镜像构建手册。
- **已知限制**：文档公式可能与源码实现记号不同；出现冲突时以源码和输出文件头为准。
- **公式核查**：本目录公式为索引性转述，逐条状态见 `faclib/`、`modqed/`、`coul/`、`ionis/`、`mpfun/` 与各 `demo/` README。
- **导航**：父级 [`../README.md`](../README.md)；论文 [`papers/README.md`](papers/README.md)；开发文档 [`misc/README.md`](misc/README.md)。

- [返回上级](../README.md)
- [`misc/` 开发文档](misc/README.md)
- [`papers/` 理论论文](papers/README.md)
