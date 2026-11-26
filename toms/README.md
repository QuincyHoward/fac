# `toms/` — ACM TOMS 数值例程集合

## 1. 目录定位与来源

本目录汇集 ACM TOMS（ACM Transactions on Mathematical Software）风格的数值例程，供 FAC 的数值计算使用，涵盖插值与样条、三角剖分、特殊函数、最优化等。主要来源包括：

- Hiroshi Akima 的一元/二元插值例程（UVIP3P、RGBI3P、SDBI3P 系列，文件头注明 TOMS 论文与版本日期）；
- Robert J. Renka 的 TRIPACK 平面 Delaunay 三角剖分包；
- Stephen G. Nash 的截断牛顿（Truncated Newton）无约束优化包 `tn.f`；
- Tom Rowan（Univ. of Texas at Austin）的 subplex/simplex 无约束优化包（`subplx` 及其辅助例程）；
- W. Fullerton（IMSL）的 Fermi–Dirac 积分实现（`fdi.f`）及 `fm*` 系列有理逼近函数。

**第三方代码声明**：本目录属于 FAC 随附的第三方内容，不能按 GPL 重新分发。见上级 [`README.md`](../README.md) 的 “Third party content that cannot be distributed under GPL” 一节（`toms/`：“some numerical routines from TOMS”）以及 [`UtilList`](../UtilList) 中的 `toms` 条目。

## 2. 组织形式与按函数族分类

本目录共 29 个 `.f` 文件（外加 `Makefile.in`），按函数族可分：

- **一元插值（改进 Akima 法）**：`uvip3p.f`、`uvip3c.f`、`uvip3i.f`。
- **二元插值（修订 Akima 法）**：规则网格 `rgbi3p.f`、散点 `sdbi3p.f`。
- **三角剖分（TRIPACK）**：`tripack.f`。
- **Fermi–Dirac 积分与特殊函数**：`fdi.f`、`fm1p.f`、`fm1m.f`、`fm1pi.f`、`fm1mi.f`、`fm3p.f`、`fm3pi.f`、`fm5p.f`、`fm5pi.f`。
- **无约束优化（subplex / Nelder–Mead 单纯形）**：主入口 `subplx.f`、`simplx.f`；选项与辅助例程 `subopt.f`、`calcc.f`、`dist.f`、`evalf.f`、`fstats.f`、`newpt.f`、`order.f`、`partx.f`、`setstp.f`、`sortd.f`、`start.f`。
- **大规模无约束优化（截断牛顿）**：`tn.f`。

一个 `.f` 文件可包含多个例程（尤其 `fdi.f`、`tripack.f`、`tn.f`、`sdbi3p.f`、`rgbi3p.f`、`uvip3p.f`），下列“关键入口签名”给出该文件的主入口，并在“算法要点”中列出同文件内的主要配套例程。

## 3. 逐文件说明

### `uvip3p.f`
- **功能**：一元插值主控例程（改进 Akima 法），一次算出所有待插值点的函数值。
- **关键入口签名**：`SUBROUTINE UVIP3P(NP,ND,XD,YD,NI,XI,YI)`。`NP` 多项式次数（默认 3），`ND` 数据点数（≥2），`XD`/`YD` 单调递增的横/纵坐标数组，`NI` 待求点数（≥1），`XI`/`YI` 待求点横/纵坐标。同文件还含内部例程 `SCALEXY` 与备选入口 `UVIP3O`。
- **算法要点**：构造分段的三次（可选更高次）多项式，局部确定各区间斜率，兼顾精度并抑制曲线起伏；在区间外做线性外推。
- **在 FAC 中的调用方**：调用非常广泛——`faclib/rates.c`、`faclib/recombination.c`、`faclib/excitation.c`、`faclib/coulomb.c`、`faclib/dbase.c`、`faclib/rmatrix.c`、`faclib/crm.c`、`faclib/radial.c`、`faclib/orbital.c`，以及 `python/util.c`；经 `faclib/f2c.h`/`f2c.f90` 的 `UVIP3P`/`f_uvip3p` 包装。`coul/`、`modqed/` 未查到直接调用。

### `uvip3c.f`
- **功能**：为 `UVIP3I` 预计算插值区间与三次多项式系数，供多点重复插值复用。
- **关键入口签名**：`SUBROUTINE UVIP3C(NP,ND,XD,YD,C1,C2,C3)`。`NP`、`ND`、`XD`、`YD` 同上，`C1`/`C2`/`C3` 为输出系数数组。
- **算法要点**：按 Akima 方法在每个数据点求出斜率并整理成三套系数；对 `NP=1/2/3` 及端点区间分别处理。
- **在 FAC 中的调用方**：`faclib/radial.c`（约 11870–12263 行）、`faclib/orbital.c`（约 3505/3507 行）；`faclib/f2c.h`/`f2c.f90` 提供 `UVIP3C`/`f_uvip3c` 包装。

### `uvip3i.f`
- **功能**：利用 `UVIP3C` 生成的系数，在指定数据区间上做一次插值。
- **关键入口签名**：`SUBROUTINE UVIP3I(NP,ND,XD,YD,II,C1,C2,C3)`。`II` 为所求点所在的数据区间索引，其余参数同 `UVIP3C`。
- **算法要点**：按区间位置（内部/左端/右端）选择对应多项式并代入求值，适用于同一组数据上大量单点的快速插值。
- **在 FAC 中的调用方**：`faclib/interpolation.c`（约 603 行，另有若干注释掉的调用）；`faclib/f2c.h`/`f2c.f90` 提供 `UVIP3I`/`f_uvip3i` 包装。

### `tripack.f`
- **功能**：TRIPACK 包，构造平面上给定点的 Delaunay 三角剖分，并提供三角剖分的查询、增删与约束剖分能力。
- **关键入口签名**：主入口 `SUBROUTINE TRMESH (N,X,Y, LIST,LPTR,LEND,LNEW,IER)`（`N` 点数，`X`/`Y` 坐标，`LIST`/`LPTR`/`LEND`/`LNEW` 为邻接表与工作区，`IER` 错误码）。同文件主要例程还包括 `TRFIND`（定位点所在三角形）、`GETNP`（按距离递增枚举邻近点）、`ADDCST`（约束 Delaunay）、`ADDNOD`/`DELNOD`/`BDYADD`/`INTADD`/`DELARC`/`DELNB`（三角剖分增删）、`BNODES`、`CIRCUM`、`CRTRI`、`EDGE`、`INTSEC`、`LEFT`、`LSTPTR`、`NBCNT`、`NEARND`、`OPTIM`、`PERMUT`、`QKSORT`、`REORDR`、`STORE`、`SWAP`、`SWPTST`、`TRLIST`/`TRLPRT`/`TRPRNT`（转换与打印）、`TRMSHR`、`AREA P`、`INDXCC`、`INSERT` 等。
- **算法要点**：增量插入 + 空圆（circumcircle）判别与边交换的 Delaunay 三角剖分；邻接表用 `LIST`/`LPTR`/`LEND` 维护；约束版通过强制保留约束弧处理任意连通区域。
- **在 FAC 中的调用方**：在 `faclib`、`coul`、`modqed`、`python` 的 C/Python 源中**未查到直接调用**；`faclib/f2c.h`/`f2c.f90` 也未提供 `TRMESH` 等包装。该文件作为 `sdbi3p.f` 三角剖分依赖被一并编译进库。

### `rgbi3p.f`
- **功能**：矩形网格上的二元插值（修订 Akima 法，双三次精度）。
- **关键入口签名**：`SUBROUTINE RGBI3P(MD,NXD,NYD,XD,YD,ZD,NIP,XI,YI, ZI,IER, WK)`。`MD` 计算模式（1=新数据，2=沿用旧数据），`NXD`/`NYD` 为 x/y 网格点数，`XD`/`YD` 单调网格坐标，`ZD` 网格函数值，`NIP` 待求点数，`XI`/`YI` 待求点坐标，`ZI` 输出插值，`IER` 错误码，`WK` 实工作区。同文件还含 `RGSF3P`（网格系数）、`RGPD3P`（偏导）、`RGLCTN`（定位）、`RGPLNL`（局部多项式）等。
- **算法要点**：每个矩形单元由局部数据确定一个双三次多项式；网格线可非等距；多次插值可用 `MD=2` 复用系数。
- **在 FAC 中的调用方**：`faclib/f2c.h`/`f2c.f90` 提供 `RGBI3P`/`f_rgbi3p` 包装，但在 `faclib`、`coul`、`modqed`、`python` 的实际调用代码中**未查到**。

### `sdbi3p.f`
- **功能**：散点数据的二元插值（修订 Akima 法，三次精度，要求数据点 ≥10）。
- **关键入口签名**：`SUBROUTINE SDBI3P(MD,NDP,XD,YD,ZD,NIP,XI,YI,ZI,IER,WK,IWK)`。`MD` 模式（1=新 XD-YD，2=旧 XD-YD 新 ZD，3=全部沿用），`NDP` 数据点数，`XD`/`YD`/`ZD` 散点坐标与函数值，`NIP`/`XI`/`YI` 待求点，`ZI` 输出，`IER` 错误码，`WK`/`IWK` 实/整工作区。同文件含 `SDSF3P`、`SDTRAN`、`SDTRCH`、`SDTRTT`、`SDPD3P`、`SDCLDP`、`SDCF3P`、`SDLEQN`、`SDLS1P`、`SDLCTN`、`SDPLNL`、`GRADC`、`GIVENS`、`ROTATE`、`SETRO3`、`ICOPY` 等。
- **算法要点**：先对散点做 Delaunay 三角剖分，再在每个三角形上构造局部三次曲面，并用梯度/Givens 旋转等辅助计算；依赖 `tripack.f` 的三角剖分例程。
- **在 FAC 中的调用方**：`faclib/f2c.h`/`f2c.f90` 提供 `SDBI3P`/`f_sdbi3p` 包装，但在 `faclib`、`coul`、`modqed`、`python` 的实际调用代码中**未查到**。

### `tn.f`
- **功能**：截断牛顿法（Truncated Newton）无约束优化，特别适合变量数较大的问题；另含箱式约束版本。
- **关键入口签名**：`SUBROUTINE TN (IERROR, N, X, F, G, W, LW, SFUN)`。`IERROR` 错误码（0 正常、2 求值次数超限、3 线搜索失败、-1 输入错误），`N` 变量数，`X` 输入初值/输出解，`F` 函数值，`G` 梯度，`W(LW)` 实工作区，`SFUN` 用户提供的值/梯度求值例程。同文件主入口还有 `SUBROUTINE TNBC (IERROR, N, X, F, G, W, LW, SFUN, LOW, UP, IPIVOT)`（带上下界）与 `LMQN`/`LMQNBC`（Lanczos 小子问题求解）以及 `MONIT`、`ZTIME`、`STPMAX`、`MODZ`、`CNVTST`、`CRASH`、`MODLNP`、`NDIA3`、`NEGVEC`、`LSOUT`、`STEP1`、`MCHPR1`、`CHKUCP`、`SETUCR`、`GTIMS`、`MSOLVE`、`MSLV`、`SSBFGS`、`INITPC`、`INITP3`、`SETPAR`、`LINDER`、`GETPTC`、`DXPY`、`FUNCTION LINT` 等辅助例程。
- **算法要点**：以 Lanczos 共轭梯度法近似求解牛顿方程并截断内层迭代，配合线搜索；不要求目标函数凸，但要求有下界，只保证局部极小。
- **在 FAC 中的调用方**：在 `faclib`、`coul`、`modqed`、`python` 中**未查到直接调用**，f2c 包装层也未提供 `TN`/`f_tn`。

### `calcc.f`
- **功能**：计算去掉函数值最高顶点后的单纯形质心。
- **关键入口签名**：`subroutine calcc (ns,s,ih,inew,updatc,c)`。`ns` 子空间维数，`s(ns,ns+3)` 单纯形工作数组，`ih` 最高点索引，`inew` 新点索引，`updatc` 逻辑开关（真则增量更新、假则从头计算），`c` 输出质心。
- **算法要点**：基于 BLAS `daxpy`/`dcopy`/`dscal` 对顶点做增量平均，避免重复求和。
- **在 FAC 中的调用方**：仅由 `simplx.f` 内部调用；FAC 核心目录中未查到直接调用。

### `dist.f`
- **功能**：计算 n 维空间中两点之间的距离。
- **关键入口签名**：`double precision function dist (n,x,y)`。`n` 分量数，`x`、`y` 为两个 n 维点。
- **算法要点**：先取最大分量差做缩放再求平方和开方，避免中间溢出/下溢。
- **在 FAC 中的调用方**：仅由 `simplx.f` 内部使用；FAC 核心目录中未查到直接调用。

### `evalf.f`
- **功能**：把子空间向量映射到全空间后求值用户目标函数，并维护求值统计。
- **关键入口签名**：`subroutine evalf (f,ns,ips,xs,n,x,sfx,nfe)`。`f` 用户函数，`ns` 子空间维数，`ips` 置换向量，`xs` 子空间向量，`n` 问题维数，`x` 全空间向量，`sfx` 输出带符号函数值，`nfe` 函数求值计数（输入/输出）；通过公共块 `/usubc/`、`/isubc/` 记录最优值统计。
- **算法要点**：用 `ips` 把 `xs` 的分量替换进 `x` 的对应位置，调用 `f(n,x)`，并按 `minf` 等选项折算符号后调用 `fstats`。
- **在 FAC 中的调用方**：由 `subplx.f`（及其 `simplx`）内部调用；FAC 核心目录中未查到直接调用。

### `fstats.f`
- **功能**：更新公共块 `/usubc/` 中关于最优函数值的统计量 `nfxe`、`fxstat`。
- **关键入口签名**：`subroutine fstats (fx,ifxwt,reset)`。`fx` 当前最优处函数值，`ifxwt` 权重，`reset` 逻辑开关（真则初始化、假则更新）。
- **算法要点**：维护当前/历史最优值及加权计数，用于停机判据与噪声抑制。
- **在 FAC 中的调用方**：由 `evalf.f` 调用；FAC 核心目录中未查到直接调用。

### `newpt.f`
- **功能**：按单纯形法的反射、扩张、收缩、缩边系数生成新点。
- **关键入口签名**：`subroutine newpt (ns,coef,xbase,xold,new,xnew,small)`。`ns` 维数，`coef` 策略系数，`xbase` 基点，`xold` 旧点，`new` 逻辑开关（结果写入 `xnew` 或 `xold`），`small` 输出是否过小。
- **算法要点**：按 `xbase + coef*(xbase - xold)` 计算；`coef>0` 为反射，`coef<0` 为扩张/收缩/缩边。
- **在 FAC 中的调用方**：仅由 `simplx.f` 内部调用；FAC 核心目录中未查到直接调用。

### `order.f`
- **功能**：在单纯形中找出函数值最低、次高、最高的顶点索引。
- **关键入口签名**：`subroutine order (npts,fs,il,is,ih)`。`npts` 顶点数，`fs` 各顶点函数值，`il` 输入最低点索引，`is`/`ih` 输出次高/最高点索引。
- **算法要点**：以上次的最低点为起点循环扫描，更新三个索引，避免全表排序。
- **在 FAC 中的调用方**：仅由 `simplx.f` 内部调用；FAC 核心目录中未查到直接调用。

### `partx.f`
- **功能**：按各分量变化量相近的原则把变量划分成若干子空间。
- **关键入口签名**：`subroutine partx (n,ip,absdx,nsubs,nsvals)`。`n` 问题维数，`ip` 置换向量，`absdx` 各分量变化量，`nsubs` 输出子空间个数，`nsvals` 输出各子空间维数。
- **算法要点**：先经 `sortd` 按变化量排序，再按 `/usubc/` 中的 `nsmin`/`nsmax` 约束切分，使各组内变化量尺度接近。
- **在 FAC 中的调用方**：仅由 `subplx.f` 内部调用；FAC 核心目录中未查到直接调用。

### `setstp.f`
- **功能**：按解向量的变化量为各分量设置新的步长。
- **关键入口签名**：`subroutine setstp (nsubs,n,deltax,step)`。`nsubs` 子空间个数，`n` 问题维数，`deltax` 解向量变化量，`step` 输入/输出步长。
- **算法要点**：用 BLAS `dasum` 求尺度并按 `/usubc/` 中的 `omega` 等系数缩放步长。
- **在 FAC 中的调用方**：仅由 `subplx.f` 内部调用；FAC 核心目录中未查到直接调用。

### `simplx.f`
- **功能**：在单个子空间上执行 Nelder–Mead 单纯形法最小化。
- **关键入口签名**：`subroutine simplx (f,n,step,ns,ips,maxnfe,cmode,x,fx,nfe,s,fs,iflag)`。`f` 用户函数，`n` 问题维数，`step` 各分量步长，`ns` 子空间维数，`ips` 置换向量，`maxnfe` 求值上限，`cmode` 逻辑开关（首次/继续），`x`/`fx` 输入初值及输出最优，`nfe` 求值计数，`s(ns,ns+3)`/`fs(ns+1)` 单纯形与函数值工作区，`iflag` 标志（-1 超限、0 单纯形按 `psi` 缩小、1 机器精度极限、2 达到 `fstop`）。
- **算法要点**：调用 `start` 构造初始单纯形，`order` 定位高/低点，`calcc` 求质心，`newpt` 生成反射/扩张/收缩/缩边点，`evalf` 求值，并按 `psi` 周期缩小单纯形。
- **在 FAC 中的调用方**：仅由 `subplx.f` 内部调用；FAC 核心目录中未查到直接调用。

### `sortd.f`
- **功能**：用 shakersort 按键值降序排序索引向量（不移动键值本身）。
- **关键入口签名**：`subroutine sortd (n,xkey,ix)`。`n` 元素数，`xkey` 双精度键数组，`ix` 输入/输出索引数组，满足 `xkey(ix(i)) >= xkey(ix(i+1))`。
- **算法要点**：双向冒泡，近有序数组约 O(n)，完全无序约 O(n²)，仅适合小规模。
- **在 FAC 中的调用方**：由 `subplx.f` 内部（经 `partx`）使用；FAC 核心目录中未查到直接调用。

### `start.f`
- **功能**：为 `simplx` 构造初始单纯形。
- **关键入口签名**：`subroutine start (n,x,step,ns,ips,s,small)`。`n` 问题维数，`x` 当前最优点，`step` 步长，`ns` 子空间维数，`ips` 置换向量，`s(ns,ns+3)` 输出初始单纯形（前 `ns+1` 列），`small` 输出是否存在重合点。
- **算法要点**：以 `x(ips(i))` 为基点，逐维按 `step` 扰动生成顶点。
- **在 FAC 中的调用方**：仅由 `simplx.f` 内部调用；FAC 核心目录中未查到直接调用。

### `subopt.f`
- **功能**：为 `subplx` 设置默认优化策略参数。
- **关键入口签名**：`subroutine subopt (n)`。`n` 问题维数；参数写入公共块 `/usubc/`。
- **算法要点**：默认反射 `alpha=1`、收缩 `beta=0.5`、扩张 `gamma=2`、缩边 `delta=0.5`、单纯形缩小 `psi=0.25`、步长缩小 `omega=0.1`、`nsmin=min(2,n)`、`nsmax=min(5,n)`；用户可在调用 `subplx` 前先改公共块并用 `mode` 声明使用自定义选项。
- **在 FAC 中的调用方**：由 `subplx.f` 内部（及用户显式设置时）调用；FAC 核心目录中未查到直接调用。

### `subplx.f`
- **功能**：Subplex 法求解无约束优化，对含噪声或在解处不连续的目标函数尤其适用；默认最小化。
- **关键入口签名**：`subroutine subplx (f,n,tol,ftol,maxnfe,mode,scale,x,fx,nfe,work,iwork,iflag)`。`f` 用户函数，`n` 维数，`tol` 相对误差容差，`ftol` 绝对容差，`maxnfe` 求值上限，`mode` 位开关（bit0：首次/继续；bit1：默认/用户选项），`scale` 缩放与初始步长，`x`/`fx` 输入初值及输出最优，`nfe` 求值计数，`work`/`iwork` 实/整工作区，`iflag` 标志（-2 非法输入、-1 超限、0 满足 `tol`、1 机器精度极限、2 达到 `fstop`）。
- **算法要点**：把变量空间划分为若干子空间，在每个子空间上用 `simplx` 做 Nelder–Mead 搜索，逐轮按 `psi` 缩小子单纯形并重启，兼顾鲁棒性与效率。
- **在 FAC 中的调用方**：`faclib/radial.c`（约 4499 行 `EnergyHXS`、5477 行 `EnergyFunc` 的优化）；`faclib/f2c.h`/`f2c.f90`（`SUBPLX`/`f_subplx`）、`faclib/cf77.h`、`faclib/genf2c.py` 提供包装。

### `fdi.f`
- **功能**：Fermi–Dirac 积分与相关特殊函数包（W. Fullerton，IMSL，1983）。
- **关键入口签名**：主例程 `subroutine fdm (xnu, alpha, fd)`（`xnu` 为 -0.5 到 4.0 之间 0.5 的整数倍，`alpha` 自变量，`fd` 输出，约 10 位精度）。对外常用入口 `SUBROUTINE FERMID(ORD, X, RELERR, FD, IERR)`（`ORD` 阶数、`X` 自变量、`RELERR` 相对误差、`FD` 结果、`IERR` 错误码）与 `SUBROUTINE FERINC(ORD, X, B, RELERR, FDI, IERR)`（部分积分，`B` 为积分上限相关参数）。同文件还含 `FDNINT`、`FDNEG`、`FDPOS`、`FDETA`、`FDASYM`、`M1KUMM`、`U1KUMM`、`ETARIE`、`ETALEV`、`ETAN`、`FERERR`、`GAMMAC`、`WHIZ`、`MACHAR`、`ALNREL`、`INITS`、`CSEVL`、`R1MACH` 等。
- **算法要点**：按阶数与自变量区间分别采用切比雪夫级数、递推与渐近展开；`ALNREL`/`CSEVL`/`R1MACH`/`MACHAR` 为底层数值辅助。
- **在 FAC 中的调用方**：`FERMID` 用于 `faclib/orbital.c`（约 5548/5549、5894–5898 行）、`python/util.c`（172 行）、`python/fac.c`（6780 行）；`FERINC` 用于 `python/util.c`（183 行）；经 `faclib/f2c.h`/`f2c.f90`（`f_fermid`/`f_ferinc`）与 `faclib/cf77.h` 包装。`coul/`、`modqed/` 未查到直接调用。

### `fm1p.f`
- **功能**：计算阶数 +1/2 的完全 Fermi–Dirac 积分值的有理逼近。
- **关键入口签名**：`double precision function fm1p(x)`，单参数 `x`。
- **算法要点**：以内置系数为分子的有理式分段逼近：`x<2` 时用 `exp(x)` 的幂级数比，`x>=2` 时用 `1/x**2` 的展开；`f2c.f90` 提供 `f_fm1p` 包装。
- **在 FAC 中的调用方**：`faclib/f2c.h`/`f2c.f90` 提供 `FM1P`/`f_fm1p` 包装，但在 `faclib`、`coul`、`modqed`、`python` 的实际调用代码中**未查到直接调用**。

### `fm1m.f`
- **功能**：计算阶数 -1/2 的完全 Fermi–Dirac 积分值的有理逼近。
- **关键入口签名**：`double precision function fm1m(x)`，单参数 `x`。
- **算法要点**：与 `fm1p` 同构的分段有理逼近（`x<2` 用 `exp(x)`，`x>=2` 用 `1/x**2` 展开，系数不同）。
- **在 FAC 中的调用方**：`faclib/crm.c`（约 8429、8462、8485 行，与 `FM1PI` 配套使用）；`faclib/f2c.h`/`f2c.f90` 提供 `FM1M`/`f_fm1m` 包装。

### `fm1pi.f`
- **功能**：`fm1p`（阶 +1/2）的逆函数，由函数值反求自变量。
- **关键入口签名**：`double precision function fm1pi(f)`，单参数 `f` 为函数值。
- **算法要点**：`f<4` 时用有理式配合对数（`dlog(f*rn/den)`），大 `f` 时用 `1/f**(1/(1+an))` 型展开。
- **在 FAC 中的调用方**：`faclib/crm.c`（约 8428、8461、8484 行，用于由给定密度反解约化化学势）；`faclib/f2c.h`/`f2c.f90` 提供 `FM1PI`/`f_fm1pi` 包装。

### `fm1mi.f`
- **功能**：`fm1m`（阶 -1/2）的逆函数，由函数值反求自变量。
- **关键入口签名**：`double precision function fm1mi(f)`，单参数 `f`。
- **算法要点**：`f<4` 时多项式有理逼近，`f>=4` 时用幂展开，内部使用 `an=-0.5`。
- **在 FAC 中的调用方**：`faclib/f2c.h`/`f2c.f90` 提供 `FM1MI`/`f_fm1mi` 包装；在 `faclib`、`coul`、`modqed`、`python` 的实际调用代码中**未查到直接调用**。

### `fm3p.f`
- **功能**：计算阶数 +3/2 的完全 Fermi–Dirac 积分值的有理逼近。
- **关键入口签名**：`double precision function fm3p(x)`，单参数 `x`。
- **算法要点**：与 `fm1p` 同构，`x<2` 用 `exp(x)` 分支、`x>=2` 用 `1/x**2` 分支，系数为阶 3/2 专门拟合。
- **在 FAC 中的调用方**：`faclib/radial.c`（约 5155 行）；`faclib/f2c.h`/`f2c.f90` 提供 `FM3P`/`f_fm3p` 包装。

### `fm3pi.f`
- **功能**：`fm3p`（阶 +3/2）的逆函数。
- **关键入口签名**：`double precision function fm3pi(f)`，单参数 `f`。
- **算法要点**：小 `f` 分支用有理式加对数，大 `f` 分支用 `1/f**(1/(1+an))` 展开（`an=1.5`）。
- **在 FAC 中的调用方**：`faclib/f2c.h`/`f2c.f90` 提供 `FM3PI`/`f_fm3pi` 包装；实际调用代码中**未查到直接调用**。

### `fm5p.f`
- **功能**：计算阶数 +5/2 的完全 Fermi–Dirac 积分值的有理逼近。
- **关键入口签名**：`double precision function fm5p(x)`，单参数 `x`。
- **算法要点**：同构分段有理逼近，`an=2.5`、`x>=2` 分支使用 `1/x**2` 展开。
- **在 FAC 中的调用方**：`faclib/radial.c`（约 5157 行）；`faclib/f2c.h`/`f2c.f90` 提供 `FM5P`/`f_fm5p` 包装。

### `fm5pi.f`
- **功能**：`fm5p`（阶 +5/2）的逆函数。
- **关键入口签名**：`double precision function fm5pi(f)`，单参数 `f`。
- **算法要点**：小 `f` 分支用有理式加对数，大 `f` 分支用幂展开（`an=2.5`）。
- **在 FAC 中的调用方**：`faclib/f2c.h`/`f2c.f90` 提供 `FM5PI`/`f_fm5pi` 包装；实际调用代码中**未查到直接调用**。

## 4. 接口与调用约定

- 语言为 **Fortran 77**（`IMPLICIT DOUBLE PRECISION`、`DATA` 系数表、公共块），多数入口为 `SUBROUTINE`，特殊函数族 `fm*`/`dist` 为 `DOUBLE PRECISION FUNCTION`。
- **工作数组约定**：`UVIP3P`/`RGBI3P`/`SDBI3P` 要求调用方提供足够大的实/整工作区（例如 `SDBI3P` 需 `WK` 为 `NDP*17`、`IWK` 为 `NDP*39`）；`SDBI3P`/`RGBI3P` 用 `MD` 模式在多点插值间复用已算好的系数，复用期间不得改动输入数据数组。
- **反通信（reverse communication）**：本目录整体采用**直接调用 + 用户回调**约定，而非显式 `reverse communication` 标志循环。需要用户回调的接口有：`SUBPLX`/`SIMPLX`/`EVALF` 的 `f(n,x)`，`TN`/`TNBC` 的 `SFUN`（值/梯度）。其中 `subplx` 的 `mode` 与 `simplx` 的 `cmode` 允许跨调用续算，状态保存在公共块 `/usubc/`、`/isubc/`（在 OpenMP 构建中带 `!$OMP THREADPRIVATE`）；`iflag` 在续算期间不得重置。
- **C 侧调用**：`faclib/f2c.h` 提供 `UVIP3P`、`UVIP3C`、`UVIP3I`、`RGBI3P`、`SDBI3P`、`SUBPLX`、`FM*`、`FERMID`/`FERINC` 等宏，`faclib/f2c.f90` 提供对应的 `bind(C)` 包装，`faclib/cf77.h` 提供 cfortran 声明，`faclib/genf2c.py` 维护生成规则。`TN` 与 `TRIPACK` 系列未生成包装。

## 5. 与上下游目录关系与构建方式

- **上游（调用方）**：`faclib/` 为主（`rmatrix.c`、`rates.c`、`excitation.c`、`recombination.c`、`coulomb.c`、`radial.c`、`orbital.c`、`crm.c`、`interpolation.c`、`dbase.c` 等），`python/util.c`、`python/fac.c` 亦有调用；`coul/`、`modqed/` 未发现直接调用。`tripack.f` 为 `sdbi3p.f` 提供三角剖分能力；`blas/` 为 subplex/simplex 辅助例程提供 `dcopy`、`daxpy`、`dscal`、`dasum`。
- **下游/产物**：编译进顶层 `libfac.a`，与 `blas/`、`lapack/`、`ode/` 等目录目标文件一并归档。
- **构建**：顶层 `configure` 由 `Makefile.in` 生成 `Makefile`，顶层脚本执行 `cd toms; make`（见上级 `Makefile.in`）。本目录 `Makefile.in` 使用 `@F77@`、`@FFLAGS@`、`@TOPDIR@`，将 `SRC` 中 29 个 `.f` 编成 `.o` 后 `ar r ${TOPDIR}/libfac.a ${OBJS}`；`make clean` 删除 `*.o *.a *~`。

## 6. README 维护记录（自底向上）

- **定位与职责**：TOMS 数值例程集合，覆盖插值、三角剖分、特殊函数与最优化，产物并入 `libfac.a`。
- **底层依据**：`uvip3p.f`、`uvip3c.f`、`uvip3i.f`、`rgbi3p.f`、`tripack.f`。
- **输入/输出**：依例程而定；输出插值、网格、特殊函数或优化结果。
- **验证与回归**：通过 `faclib/` 调用与 `demo` 回归间接验证。
- **已知限制**：第三方代码；不同例程版权与许可需分别保留。
- **公式核查**：源码未找到独立于 Fortran 实现的数学公式原文，需按各 TOMS 算法论文人工核查。
- **导航**：父级 [`../README.md`](../README.md)。

[返回上级](../README.md)