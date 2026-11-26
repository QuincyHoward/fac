# FAC（Flexible Atomic Code）源码与文档体系

**版本核查（2026-11-24 复核更正）**

- 官方仓库：<https://github.com/flexible-atomic-code/fac>
- 当前**代码基线**（code baseline，即工作树所基于的提交，亦称基准提交/base commit）：`9ab6defb6af62e1bc8251a35ff995809abef717c`（提交日期 2026-10-27，说明 `safeguard in ce interpolation (#854)`）。本地 `HEAD` 与 `origin/master` 均为此提交，且与 GitHub 官方 `master` 一致。

```bash
git clone https://github.com/flexible-atomic-code/fac.git
```

本文件是 `fac/` 源码树的**中文总入口**。它给出项目定位、架构分层、目录导航、物理效应与公式索引，以及整套中文 README 体系的组织约定。原始英文 README 全文逐字保留在文末「原始文档」章节，未作翻译或删减。

## 1. 项目概述

FAC（Flexible Atomic Code）是一套用于计算各类原子过程的相对论原子结构软件，核心以 C 实现， Fortran 数值库提供底层支撑。主要功能包括：

- 基于 Dirac 方程与自洽场中心势的原子结构、能级与波函数，组态相互作用（CI）对角化；
- 电子碰撞激发（EIE）、电子碰撞电离（EII）；
- 辐射复合（RR）、双电子复合（DR）、自电离（AI）/Auger、电荷交换（CX）；
- 辐射跃迁率、振子强度、极化率与谱线偏振；
- 碰撞辐射模型（CRM）布居求解与光谱合成；
- Dirac R 矩阵、MBPT 等高级方法。

提供两套相互独立的接口：**PFAC**（Python 扩展模块 `pfac`，非线程安全，一个 Python 内核只能同时运行一个算例）与 **SFAC**（命令行程序 `sfac`、`scrm`、`spol`，输入语法近似 Python 但没有流程控制）。

## 2. 快速开始

```bash
./configure                 # 可按环境追加 --prefix、--with-mpi=omp 等选项
make                        # 构建 SFAC 可执行程序
make install
make pfac && make install-pfac   # 构建并安装 PFAC Python 模块
```

验证安装：

```bash
cd demo && make check
```

Python 侧典型调用链（详见 [`demo/structure/`](demo/structure/README.md)）：

```python
from pfac import fac
fac.SetAtom('Fe'); fac.Closed('1s')
fac.Config('2*8', group='n2'); fac.Config('n3', '2*7 3*1')
fac.ConfigEnergy(0); fac.OptimizeRadial(['n2']); fac.ConfigEnergy(1)
fac.Structure('ne.lev.b', ['n2','n3'])
fac.MemENTable('ne.lev.b'); fac.PrintTable('ne.lev.b', 'ne.lev', 1)
```

完整的安装选项、Anaconda 注意事项、CI 环境等内容见文末原始文档，以及 [`ci/`](ci/README.md)、[`.circleci/`](.circleci/README.md)。

## 3. 架构分层与数据流

```text
用户脚本 / 命令行输入
        │
        ├── PFAC 接口：python/（pfac.fac / crm / pol / util + atom/rfac/spm 封装）
        └── SFAC 接口：sfac/（sfac / scrm / spol + stoken 解析器）
        │
        ▼
核心物理库 faclib/（structure、excitation、ionization、recombination、
        transition、polarization、crm、rmatrix、mbpt、radial、orbital…）
        │
        ├── QED 修正：modqed/（自能、Uehling 真空极化、WK 项）
        ├── 连续态与库仑函数：coul/
        ├── 电离平衡拟合：ionis/
        └── 数值支撑：blas/、lapack/、minpack/、quadpack/、ode/、toms/、mpfun/
        │
        ▼
输出表格 .en / .tr / .ce / .ci / .rr / .ai / .sp / .rt
        │
        ▼
demo/ 示例与 ref/ 参考结果（回归测试）；doc/ 手册与论文（理论依据）
```

构建时各目录 `Makefile.in` 由顶层 `configure` 生成，目标文件统一归档进 `libfac.a`。

## 4. 目录导航

| 目录 | 角色 | 说明 |
|---|---|---|
| [`faclib/`](faclib/README.md) | 核心数值库 | 30 个 `.c` + 38 个 `.h`，实现原子结构与各类原子过程 |
| [`coul/`](coul/README.md) | 库仑工具库 | 连续态库仑波函数、Bessel/Gamma、WKB、特殊函数 |
| [`modqed/`](modqed/README.md) | QED 修正 | 自能、Uehling/WK 真空极化、有限核势、Dirac 方程 |
| [`ionis/`](ionis/README.md) | 电离平衡 | Arnaud & Raymond、Mazzotta、Verner 拟合 |
| [`mpfun/`](mpfun/README.md) | 高精度数值 | 四倍精度算术与缔合 Legendre 函数 |
| [`blas/`](blas/README.md) | 基础线性代数 | BLAS 双精度子集（20 个源文件） |
| [`lapack/`](lapack/README.md) | 线性代数 | LAPACK 双精度子集（112 个源文件） |
| [`minpack/`](minpack/README.md) | 最优化 | 最小二乘与非线性求解（8 个源文件） |
| [`quadpack/`](quadpack/README.md) | 数值积分 | 自适应求积（9 个源文件） |
| [`ode/`](ode/README.md) | ODE 求解 | LSODE（13 个源文件） |
| [`toms/`](toms/README.md) | TOMS 数值例程 | 插值、三角剖分、特殊函数、最优化（29 个源文件） |
| [`python/`](python/README.md) | PFAC 接口 | Python 模块与 C 扩展（`pfac.fac/crm/pol/util`） |
| [`sfac/`](sfac/README.md) | SFAC 接口 | `sfac`、`scrm`、`spol` 命令解析与驱动 |
| [`demo/`](demo/README.md) | 示例与回归测试 | structure/excitation/pirr/aidr/ionization/NeL/FeL/polariz/rmatrix/tests |
| [`doc/`](doc/README.md) | 手册与论文 | `manual.tex`、`misc/`、`papers/` |
| [`ci/`](ci/README.md) | 环境配置 | Python 2.7/3.6/3.7 与 OpenMP 测试环境 |
| [`.circleci/`](.circleci/README.md) | 文档 CI | 构建手册并发布 PDF |

## 5. 物理效应与公式索引

下表汇总核心效应、代表性公式与实现位置；各目录 README 给出完整推导、出处与逐文件源码对应。

| 效应 | 代表公式 | 源码 / 文档 |
|---|---|---|
| 相对论原子结构 | $H=\sum_i H_D(i)+\sum_{i<j}1/r_{ij},\ H\Psi=E\Psi$ | [`faclib/`](faclib/README.md) `structure.c`、`orbital.c`、`radial.c`；[`doc/papers/`](doc/papers/README.md) `structure.tex` |
| Dirac 径向方程 | $\left(\frac{d}{dr}+\frac{\kappa}{r}\right)P=\alpha(\varepsilon-V+2/\alpha^2)Q$ | `faclib/orbital.c`；[`faclib/README.md`](faclib/README.md) §3.1 |
| QED 自能与真空极化 | $\Delta E^{SE}\sim\frac{\alpha}{\pi}(Z\alpha)^4mc^2$；$V_U(r)$ Uehling 势 | [`modqed/`](modqed/README.md) `se_pot.f`、`uehling.f`、`wk.f` |
| 电子碰撞激发 | $\sigma_{ij}=\dfrac{\pi}{k_i^2 g_i}\Omega_{ij}$ | [`faclib/`](faclib/README.md) `excitation.c`；[`demo/excitation/`](demo/excitation/README.md) |
| 电子碰撞电离 | $\sigma(\varepsilon_0)=\int_0^{(\varepsilon_0-I)/2}\sigma(\varepsilon_0,\varepsilon)\,d\varepsilon$ | `faclib/ionization.c`；[`demo/ionization/`](demo/ionization/README.md) |
| 光电离 / 辐射复合 | $\sigma_{PI}=2\pi\alpha\,df/dE$；Milne 关系给出 $\sigma_{RR}$ | `faclib/recombination.c`；[`demo/pirr/`](demo/pirr/README.md) |
| 自电离 / 双电子复合 | $\alpha^{DR}(T)=\frac{h^3}{(2\pi m_e k_BT)^{3/2}}\sum_i \frac{g_i}{2g_f}A^a_i B_i e^{-E_{if}/k_BT}$ | `faclib/recombination.c`；[`demo/aidr/`](demo/aidr/README.md) |
| 辐射跃迁 | $A_{ji}=\dfrac{64\pi^4\nu^3}{3hc^3(2J_j+1)} \|\langle j\|D\|i\rangle \|^2$ | `faclib/transition.c` |
| 谱线偏振 | FAC 输出 $P=a/b=\sum_t F_tPL2_tA_tB_t\big/\sum_t PL_tA_tB_t$（球张量比值，非初等 $I_\parallel/I_\perp$ 字面式） | `faclib/polarization.c`；[`demo/polariz/`](demo/polariz/README.md) |
| 碰撞辐射模型 | $\dfrac{dn_i}{dt}=\sum_j n_jR_{ji}-n_i\sum_jR_{ij}$ | `faclib/crm.c`；[`demo/NeL/`](demo/NeL/README.md) |
| Dirac R 矩阵 | $\Omega_{ij}$ 由内区匹配到外部 Coulomb 波函数得到 | `faclib/rmatrix.c`；[`demo/rmatrix/`](demo/rmatrix/README.md) |

连续电子的库仑波函数见 [`coul/`](coul/README.md)；电离平衡稳态方程见 [`ionis/`](ionis/README.md)；拟合公式中不确定之处在各目录 README 中明确标注为文献通用形式。

**入门建议**：[`demo/NeL/`](demo/NeL/README.md) 是理解 FAC 全流程的首选示例——从 `ne.py` 的原子结构/CI 对角化、辐射跃迁与碰撞激发，到 `spec.py` 的 CRM 稳态布居与谱合成，配有逐 API 的输入/输出/物理含义详解与 Mermaid 流程图；`SpecTable` 的 photons/s 口径与 SP 表列语义以该文档 §7 为准。

## 6. README 文档体系约定

- **自底向上**：叶子目录（无子目录）逐文件说明源码/数据/配置与接口；父目录汇总子目录；本文件为总入口。
- **统一结构**：目录职责 → 组织形式 → 逐文件说明 → 接口与调用关系 → 物理效应（简介 / LaTeX 公式 / 源码对应）→ 上下游 → 导航。
- **中文正文**：全部 README 正文使用简体中文；唯一例外是本文件末尾逐字保留的英文原文。
- **原始文件保护**：除 README.md 交付文件外，源码、脚本、数据与配置均已设为只读，避免误修改；原有可执行方式未改变。
- **可读性**：函数名、文件名与命令保留英文并用反引号；目录间使用相对链接，便于人类浏览与 Agent 检索利用。

## 6.1 示例复现与构建口径

`demo/` 下 10 个示例的中文 README 已按“物理场景 → 公式与源码对应 → 脚本与 API 调用链 → Mermaid FAC 使用流程图 → Mermaid 数据流图 → 实际执行记录 → 回归比对 → 限制与构建兼容处理”的结构重写。复现环境为 WSL Ubuntu-22.04（gcc 9.5、gfortran 11.4、Python 3.10）；构建与运行在独立可写工作目录 `<WORK_ROOT>` 中完成，原始源码树保持只读。

执行状态：

- 已在 WSL 中跑到结束并通过 `demo/check.py` 回归比对：`structure`(2 项)、`excitation`(3 项)、`ionization`(2 项)、`pirr`(2 项)、`aidr`(2 项)、`tests`(2 项)、`NeL`(6 项)、`polariz`(3 项)，共 22 项。
- `rmatrix` 必须先运行 `rmx.py` 生成 R 矩阵基/表面文件，再运行 `cs.py` 计算碰撞强度；此前 `cs.py` 段错误的原因是缺少这些输入，而非物理模型错误。夜间复现中 `cs.py` 已返回 `0`，生成约 `886 MiB` 的 `r1.d`，状态见 `demo/rmatrix/README.md`。
- `FeL` 计算量很大，不在 `demo/Makefile` 的每日回归 `DIRS` 中；夜间完整复现中 `fe.py` 与 `spec.py` 均返回 `0`，生成 `data/` 下 Fe08/Fe09/Fe10 六类原子数据表及 `Fe08/` 谱表，状态见 `demo/FeL/README.md`。两个长耗时示例由独立调度脚本并行运行，总墙钟耗时 `2 h 39 min 42 s`。

**构建兼容处理及其物理/数值意义**（仅作用于独立可写工作目录，原树不变）：

1. 构建脚本 `configure`、`config.guess`、`config.sub`、`install.sh`、`mkinsdir.sh` 的 CRLF 行尾转为 LF。此改动只影响 shell 能否执行 `#!/bin/sh`，不改变任何物理或数值算法。
2. `sysdef.h` 中把 `#undef f2cFortran` 改为 `#define f2cFortran 1`。该宏只选择 C 与 Fortran 之间的 f2c 风格符号改名和参数传递约定（cfortran.h 桥接层），解决 gcc/gfortran 混编时的调用匹配问题；它不修改 Dirac 方程、碰撞强度、CRM 或谱合成公式，回归比对结果验证了数值一致性。
3. `rmatrix` 的执行顺序要求（先 `rmx.py` 后 `cs.py`）不是源码修改，而是工作流依赖：基文件与表面振幅编码内区本征态和边界匹配信息，是外区传播并得到碰撞强度的必要输入。

## 6.2 工程化入口与 README 维护

- Skill 唯一事实源：`skills/`，其中 [`fac-readme-maintainer`](skills/fac-readme-maintainer/SKILL.md) 负责自底向上维护 README 与公式注记，[`fac-hpc-parallel`](skills/fac-hpc-parallel/SKILL.md) 负责超算并行执行与参数矩阵。
- 常用脚本：`scripts/`；凭证管理：`scripts/credentials/`（namespace 默认 `specx`，支持未来 `flychk`）；场景体系：`scenarios/`；演示场景：`scenarios/fac_demo/`。
- Agent 上下文服务：`mcp_server.py`，只读暴露 skill、上下文协议与 README；依赖见 [`DEPENDENCIES.md`](DEPENDENCIES.md)。
- 公式核查结果以各底层目录 README 为准；源码未溯源公式使用 `\underline{$...$}` 标记，源码已溯源公式不加下划线。
- 新增目录必须先有 `README.md`，再由父目录汇总导航。

## 7. 原始文档（英文原文，逐字保留）

以下内容为本项目原有 `README.md` 全文，未作翻译、删减或重排。

# Flexible Atomic Code

[![travis](https://travis-ci.org/flexible-atomic-code/fac.svg?branch=master)](https://travis-ci.org/flexible-atomic-code/fac)

A software packge for the calculation of various atomic processes.

# Installation

There are two interfaces available to the FAC numerical lib. One makes use
of the Python scripting language, implemented as a package "pfac".
The other interface uses a simple command parser, compiled into executables.
The two interfaces are independent. Either one or both can be installed.


## 1. Download
Download the latest source packages from
[here](https://github.com/flexible-atomic-code/fac),
gunzip, and extract it.

## 2. Configure
Execute `configure` command.
You may need to specify some of the following options depending on your
environment.

#### 2-1. C/fortran compiler
If your C compiler is not gcc, then you need to supply the PIC (position
independent code) option with `--enable-cpic=***`.
If your F77 compiler is not g77, then you need to supply the PIC
option with `--enable-fpic=***`

Supply the optimization option for C and F77 compilers with
`--enable-copt=***` and `--enable-fopt=***` respectively if desired.

#### 2-2. cfortran
If your F77 compiler is not g77 or sun's f77, specify the option
`--with-cfortran=xxFortran`
see [faclib/cfortran.doc](faclib/cfortran.doc) for supported F77 compilers.

#### 2-3. Installation directory
If the default /usr/local is not what you want, specify `--prefix=my/dir`.
This dir only affects the installation of SFAC executables.

#### 2-4. Parallel computation
Some of the functions have a parallel version using MPI. You can build with MPI
enabled using the option `--with-mpi=***`, where `***` is the MPI implementation
installed on your machine. You have to supply the compile and link
flags to the C compiler with `--with-mpicompile` and `--with-mpilink`.

MPI support in FAC is rather limited. The primary mean of parallelization is through shared memory OpenMP directives. configure with --with-mpi=omp to enable OpenMP.

## 3. Install SFAC interface
To installs the SFAC interface, do
```
make
make install
```

## 4. Install Python interface
If you have Python 2.7 or later installed, then:
```
make pfac
make install-pfac
```
This installs the PFAC module into Python's default site-package dir corresponding to the python executable. To install for an alternative python, set env. var. PYTHON to the desired python executable, e.g., /usr/bin/python3, before configure, or invoke configure with ./configure PYTHON=/usr/bin/python3

install-pfac has been updated to use "pip install --prefix=$PYPREFIX", where PYPREFIX is the same as PREFIX=/usr/local by default. This should install python modules under $PYPREFIX/lib/python#.$/site-packages or in some systems dist-packages. PYPREFIX can be set when running configure. An extra option can be set during configure, PIPOPTS, which are passed to pip install. In newer versions of PIP, a virtual env is preferred, and it may refuse to install pfac into system python directories. In this case, set PIPOPTS=--break-system-packages will force pip to install pfac without virtual env setup.

#### 4-1 Anaconda distribution
If your are using Anaconda distribution for Python environment, it may be
necessary to install gcc compilers from Anacona.
Linux:
+ gcc_linux-64
+ gfortran_linux-64  

macOS:
+ clang_osx-64
+ clangxx_osx-64
```
conda install gcc_linux-64 gfortran_linux-64
```
For the details of the Anaconda's compiler, see [the official page](https://conda.io/docs/user-guide/tasks/build-packages/compiler-tools.html).

It would be better to create a new virtual environment for FAC, as the compiler
installation sometimes affects other Python packages.
For the details of the virtual environment, see [Anaconda's documentation](https://conda.io/docs/user-guide/tasks/manage-python.html#installing-a-different-version-of-python)


# Usage

### PFAC interface

The modules can be called just like any python modules, either from the
interpreter interactively, or pass the script to python.
e.g.,
```
python fe24_level.py
```
Some example scripts can be found in [demo](demo) directory.

Note that PFAC is not thread safe. Only one instance of calculation can be done
in one Python kernel.


### SFAC Interface

The non-python interface produces 3 executables, "sfac", "scrm" and "spol",
accepting input files as arguments. The syntax of the input file for both
programs is identical, and is very similar to the Python syntax, except for
the missing of flow controls.


### Manual

For more details, please read the [manual](https://github.com/flexible-atomic-code/fac/blob/release-pdf/manual.pdf), including the FAQ section of it.


# Contents of FAC

### Third party content that cannot be distributed under GPL.

These directories are bundled in fac_util.tar.gz,
and are listed in the UtilList file.
+ blas/,       BLAS routines in fortran.
+ coul/,       fortran routines related to coulomb functions.
+ ionis/,      ionization balance calculation of Arnaud&Raymond,
and that of Mazzotta et al. Rates fitted by Verner et al.
+ lapack/,     fortran routines from LAPACK.
+ minpack/,    minpack optimization package.
+ quadpack/,   some routines from quadpack for quadrature.
+ mpfun/,      it used to be the multi-precision floating point arithmetic
package by Beiley. Since v0.8.6, it was replaced by my own implementation of
quad-precision arithmetics. The associated Legendre functions are also put into
this directory.
+ ode/,	     Livermore Solver for odinary differential equations.
+ toms/,       some numerical routines from TOMS.

## Contents distributed under GPL.

These files are bundled in fac_core.tar.gz
+ README,      this file.
+ ChangeLog,   changes.
+ configure.ac,AutoConf input file
+ configure,   configure script after parsing configure.ac
+ setup.py,    python setup script for building the pfac interface
+ demo/,       some demo scripts.
+ doc/,        reference guide for FAC
+ doc/papers/, papers describe the theoretical backgrounds.
+ faclib/,     core numerical library.
+ python/,     python interface.
+ sfac/,       non-python interface.


# Contribution

For bugs and suggestions, please report to
[our issue page](https://github.com/flexible-atomic-code/fac/issues).


# Contact

mingfenggu2003@gmail.com


