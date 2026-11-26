# `ode/` — Livermore 常微分方程求解器（LSODE）子集

## 1. 目录定位与来源

本目录是 **LSODE（Livermore Solver for Ordinary Differential Equations）** 的双精度子集，源自 Lawrence Livermore National Laboratory 的 ODEPACK（作者 Alan C. Hindmarsh，`lsode.f` 文件头标注 1987-03-30 版本），求解一阶常微分方程初值问题 `dy/dt = f(t,y)`，可处理非刚性与刚性（stiff）系统。

在 FAC 中，该求解器被碰撞辐射模型（CRM）、径向/轨道积分等模块调用，用于把耦合方程组积分到指定端点。

**第三方代码声明**：本目录属于 FAC 随附的第三方内容，不能按 GPL 重新分发。见上级 [`README.md`](../README.md) 的 “Third party content that cannot be distributed under GPL” 一节（`ode/` 条目：“Livermore Solver for odinary differential equations”）以及 [`UtilList`](../UtilList) 中的 `ode` 条目。目录内未附原始用户手册，接口细节以 `lsode.f` 头部长注释为准。

## 2. 组织形式与按函数族分类

本目录共 13 个 `.f` 文件，按职责可分为四族：

- **积分器主例程**：`lsode.f`（对外唯一入口，驱动整段积分）。
- **单步积分与插值**：`stode.f`（单步前进）、`intdy.f`（由 Nordsieck 历史数组插值输出）。
- **Jacobi 矩阵与线性系统**：`prepj.f`（形成并预处理迭代矩阵）、`solsy.f`（求解弦迭代线性系统）、`dgefa.f`/`dgesl.f`（稠密 LU 分解与回代，LINPACK）、`dgbfa.f`/`dgbsl.f`（带状 LU 分解与回代，LINPACK）。
- **系数、误差与诊断**：`cfode.f`（方法系数）、`ewset.f`（误差权）、`vnorm.f`（加权 RMS 范数）、`xerrwv.f`（SLATEC 简化错误处理）。

除 `lsode` 外，其余例程均为包内辅助例程，通过 Fortran 公共块 `/ls0001/`（在支持 OpenMP 的构建中带 `!$OMP THREADPRIVATE(/ls0001/)`）共享状态；当前 FAC C/Python 层**没有**为这些辅助例程生成 f2c 包装，只有 `LSODE` 本体被包装暴露。

## 3. 逐文件说明

### `lsode.f`
- **功能**：LSODE 主驱动，求解刚性/非刚性一阶 ODE 初值问题，支持可选输入、续算与多种输出任务。
- **关键入口签名**：`subroutine lsode (f, neq, y, t, tout, itol, rtol, atol, itask, istate, iopt, rwork, lrw, iwork, liw, jac, mf)`。`f` 为外部右端例程，`neq(1)` 为方程数，`y` 为状态向量（输入/输出），`t` 当前自变量、`tout` 目标自变量，`itol` 误差控制类型，`rtol`/`atol` 相对/绝对容差，`itask` 任务，`istate` 状态标志（输入/输出），`iopt` 可选输入开关，`rwork(lrw)`/`iwork(liw)` 实/整工作数组，`jac` 外部 Jacobi 例程，`mf` 方法标志。用户右端例程形如 `subroutine f (neq, t, y, ydot)`；Jacobi 例程形如 `subroutine jac (neq, t, y, ml, mu, pd, nrowpd)`。
- **算法要点**：变阶变步长线性多步法；`mf = 10*meth + miter`，`meth=1` 为隐式 Adams（最高 12 阶），`meth=2` 为 BDF（最高 5 阶）；`miter` 决定迭代/雅可比处理方式；先积分越过 `tout` 再调用 `intdy` 插值输出。
- **在 FAC 中的调用方**：`faclib/rmatrix.c`（`IntegrateDiracCoulomb`、`IntegrateExternal`，约 2065/2145/2180 行）、`faclib/orbital.c`（`RadialFreeZMC`、`Amplitude0`、`Amplitude1`，约 2297/2901/2933 行）；经 `faclib/f2c.f90`（`f_lsode`）、`faclib/f2c.h`（`LSODE` 宏）、`faclib/cf77.h`、`faclib/genf2c.py` 暴露给 C。`coul/`、`modqed/`、`python/` 中未查到直接调用。

### `stode.f`
- **功能**：执行 ODE 积分的一个单步，完成预测—校正迭代、局部误差检验、步长/阶数调整。
- **关键入口签名**：`subroutine stode (neq, y, yh, nyh, yh1, ewt, savf, acor, wm, iwm, f, jac, pjac, slvs)`。`yh(nyh,*)` 为 Nordsieck 历史数组，`ewt` 误差权，`savf` 保存的右端值，`acor` 校正量，`wm`/`iwm` 矩阵工作区，`pjac`/`slvs` 为传入的预处理与线性求解例程（通常为 `prepj`/`solsy`）。
- **算法要点**：与 `miter` 无关的单步核心；用 `vnorm` 做误差范数，按 `cfode` 提供的 `elco`/`tesco` 选步长与阶数，失败时重试。
- **在 FAC 中的调用方**：仅由 `lsode.f` 内部调用；在 `faclib`、`coul`、`modqed`、`python` 中未查到直接调用。

### `intdy.f`
- **功能**：在给定时刻 `t` 对状态向量的第 `k` 阶导数做插值，结果写入 `dky`；包内以 `k=0, t=tout` 调用。
- **关键入口签名**：`subroutine intdy (t, k, yh, nyh, dky, iflag)`。`t` 插值时刻，`k` 导数阶（0 至当前阶），`yh` Nordsieck 数组，`nyh` 首维，`dky` 输出，`iflag` 状态（越界为负）。
- **算法要点**：直接用 Nordsieck 历史数组对应的多项式做反向求和插值；`k` 或 `t` 越界返回负 `iflag`。
- **在 FAC 中的调用方**：仅由 `lsode.f` 内部调用（约 1277/1285 行）；FAC 核心目录中未查到直接调用。

### `prepj.f`
- **功能**：计算并处理迭代矩阵 `p = i - h*el(1)*j`，其中 `j` 为 Jacobi 近似；为后续线性求解做 LU 分解。
- **关键入口签名**：`subroutine prepj (neq, y, yh, nyh, ewt, ftem, savf, wm, iwm, f, jac)`。`wm` 实工作区（输出 LU 分解或对角逆矩阵），`iwm` 整工作区（主元/带宽），`ftem` 临时数组，`savf` 为预测点处右端值。
- **算法要点**：`miter=1/4` 用用户 `jac`；`miter=2/3/5` 用有限差分（对角近似对应 `miter=3`）；非对角情形用 `dgefa`（`miter=1/2`）或 `dgbfa`（`miter=4/5`）分解。
- **在 FAC 中的调用方**：仅由 `stode.f` 内部调用；FAC 核心目录中未查到直接调用。

### `solsy.f`
- **功能**：管理弦迭代中线性系统的求解，按 `miter` 分派到稠密/带状回代或对角更新。
- **关键入口签名**：`subroutine solsy (wm, iwm, x, tem)`。`x` 输入为右端向量、输出为解向量，`tem` 为未用的长度 `n` 工作向量；`iersl` 经公共块输出。
- **算法要点**：`miter=1/2` 调 `dgesl`，`miter=4/5` 调 `dgbsl`，`miter=3` 更新 `h*el0` 后直接除以对角逆元；`wm(2)` 保存上一次 `h*el0`。
- **在 FAC 中的调用方**：仅由 `stode.f` 内部调用；FAC 核心目录中未查到直接调用。

### `cfode.f`
- **功能**：按 `meth` 一次性生成当前方法在所有阶上的系数与误差测试常数。
- **关键入口签名**：`subroutine cfode (meth, elco, tesco)`。`meth` 方法标志（1=Adams，2=BDF），`elco(13,12)` 基本方法系数，`tesco(3,12)` 步长/阶数选择用测试常数。
- **算法要点**：用生成多项式分别构造隐式 Adams 与 BDF 的 `elco`，并给出降阶/同阶/升阶三档 `tesco`；最大阶分别为 12 与 5。
- **在 FAC 中的调用方**：仅由 `stode.f` 在初始化与方法切换时调用（约 145/174 行）；FAC 核心目录中未查到直接调用。

### `ewset.f`
- **功能**：按 `itol` 设置局部误差权向量 `ewt`。
- **关键入口签名**：`subroutine ewset (n, itol, rtol, atol, ycur, ewt)`。`n` 维数，`itol` 决定 `rtol`/`atol` 是标量还是数组，`ycur` 当前解，`ewt` 输出。
- **算法要点**：逐分量组合相对项与绝对项，`itol=1..4` 分别对应两种容差的标量/数组组合。
- **在 FAC 中的调用方**：仅由 `lsode.f` 包内调用；FAC 核心目录中未查到直接调用。

### `vnorm.f`
- **功能**：计算向量的加权均方根范数。
- **关键入口签名**：`double precision function vnorm (n, v, w)`。`n` 长度，`v` 向量，`w` 权向量。
- **算法要点**：`sqrt` 之后按 `1/n` 归一化的加权平方和，供局部误差检验使用。
- **在 FAC 中的调用方**：由 `stode.f`、`prepj.f` 内部使用；FAC 核心目录中未查到直接调用。

### `xerrwv.f`
- **功能**：SLATEC 错误处理包的简化实现，打印数值消息并可按级别中止。
- **关键入口签名**：`subroutine xerrwv (msg, nmes, nerr, level, ni, i1, i2, nr, r1, r2)`。`msg`/`nmes` 为消息与长度，`level` 0/1 可恢复、2 致命，`ni`/`nr` 为附带的整数/实数个数，`i1,i2,r1,r2` 为待打印值；通过公共块 `/eh0001/` 保存打印标志与输出单元（配套例程 `xsetf`/`xsetun` 未包含在本目录）。
- **算法要点**：机器相关、面向 Hollerith 字符的简化实现，`level=2` 时执行 `stop`。
- **在 FAC 中的调用方**：由 LSODE 包内报错路径调用；FAC 核心目录中未查到直接调用。

### `dgefa.f`
- **功能**：LINPACK 稠密双精度矩阵的带主元高斯消元 LU 分解。
- **关键入口签名**：`subroutine dgefa(a,lda,n,ipvt,info)`。`a` 输入矩阵/输出 `l*u`，`lda` 首维，`n` 阶，`ipvt` 主元索引，`info` 奇异指示（非零表示某对角元为零）。
- **算法要点**：列主元消元，依赖 BLAS 的 `daxpy`、`dscal`、`idamax`。
- **在 FAC 中的调用方**：由 `prepj.f`（`miter=1/2`）调用；FAC 核心目录中未查到直接调用（相邻的 `lapack/`、`blas/` 为独立目录）。

### `dgesl.f`
- **功能**：用 `dgefa` 的分解结果求解稠密线性系统 `a*x=b` 或 `trans(a)*x=b`。
- **关键入口签名**：`subroutine dgesl(a,lda,n,ipvt,b,job)`。`job=0` 解原系统，非零解转置系统；`b` 输入右端、输出解。
- **算法要点**：先按 `ipvt` 置换，再前代/回代；依赖 BLAS `daxpy`、`dscal`。
- **在 FAC 中的调用方**：由 `solsy.f`（`miter=1/2`）调用；FAC 核心目录中未查到直接调用。

### `dgbfa.f`
- **功能**：LINPACK 带状双精度矩阵的带主元 LU 分解。
- **关键入口签名**：`subroutine dgbfa(abd,lda,n,ml,mu,ipvt,info)`。`abd(lda,n)` 为带存储（`lda >= 2*ml+mu+1`），`ml`/`mu` 为下/上带宽，`ipvt` 主元，`info` 奇异指示。
- **算法要点**：带存储下的列主元消元，输出上三角与乘子。
- **在 FAC 中的调用方**：由 `prepj.f`（`miter=4/5`）调用；FAC 核心目录中未查到直接调用。

### `dgbsl.f`
- **功能**：用 `dgbfa` 的分解结果求解带状系统 `a*x=b` 或 `trans(a)*x=b`。
- **关键入口签名**：`subroutine dgbsl(abd,lda,n,ml,mu,ipvt,b,job)`，参数含义同上，`job` 选择原系统或转置系统。
- **算法要点**：带存储下的置换、前代与回代。
- **在 FAC 中的调用方**：由 `solsy.f`（`miter=4/5`）调用；FAC 核心目录中未查到直接调用。

## 4. 接口与调用约定

- 语言为 **Fortran 77**（含 `double precision`、`external`、`data` 与公共块），单精度/双精度混合调用需谨慎；本目录全部为双精度版本。
- **用户回调**：右端 `f(neq,t,y,ydot)`；Jacobi `jac(neq,t,y,ml,mu,pd,nrowpd)`（`mf=21` 时为满矩阵，忽略 `ml`/`mu`；`mf=24` 时按带存储装载）。
- **关键参数**：
  - `mf = 10*meth + miter`。`meth=1` 隐式 Adams，`meth=2` BDF；标准取值 `10`（非刚性）、`21`/`22`（刚性，满 Jacobi：用户/内部）、`24`/`25`（刚性，带 Jacobi：用户/内部，需 `ml`、`mu`）。
  - `itask`：`1` 正常积分到 `tout`（越过并插值）；`2` 只走一步；`3/4/5` 与临界点 `tcrit` 配合，控制是否停在 `tout`/`tcrit`。
  - `istate`：输入 `1` 首次调用（续算保持上次输出值）；输出 `2` 成功，负值为错误（`-1` 工作量过大、`-2` 精度过严、`-3` 非法输入、`-4` 重复误差测试失败等）。
  - `itol` 与 `rtol`/`atol` 共同决定误差控制；`iopt=0` 表示不启用可选输入。
  - `rwork`/`iwork` 为长度受 `mf` 约束的工作数组（例如 `mf=10` 至少 `20+16*neq`，`mf=21/22` 至少 `22+9*neq+neq**2`），**两次调用之间不得改动**。
- **状态共享**：包内经公共块 `/ls0001/`（实/整标量、方法参数、统计计数）通信，OpenMP 构建中声明为线程私有，因此不同线程各自持有求解器状态。
- **C 侧调用**：由 `faclib/f2c.f90` 的 `f_lsode`（`bind(C)`）与 `faclib/f2c.h` 的 `LSODE(...)` 宏转发；`faclib/cf77.h` 提供 `PROTOCCALLSFSUB17(LSODE,...)` 的 cfortran 声明，`faclib/genf2c.py` 维护这些包装的生成规则。辅助例程不对外暴露。

## 5. 与上下游目录关系与构建方式

- **上游（调用方）**：`faclib/` 的 `rmatrix.c`、`orbital.c`（经 f2c/cfortran 桥接）；`blas/` 提供 `dgefa`/`dgesl`/`dgbfa`/`dgbsl` 及 `prepj`/`solsy` 所需的底层 BLAS 例程。`coul/`、`modqed/`、`python/` 未发现直接调用。
- **下游/产物**：编译目标为顶层 `libfac.a`，与 `blas/`、`lapack/`、`toms/` 等目录的目标文件一起归档。
- **构建**：由顶层 `configure` 根据 `Makefile.in` 生成 `Makefile`，顶层构建脚本执行 `cd ode; make`（见上级 `Makefile.in`）。本目录 `Makefile.in` 使用 `@F77@`、`@FFLAGS@`、`@TOPDIR@`，将 `SRC` 中 13 个 `.f` 编成 `.o` 后 `ar r ${TOPDIR}/libfac.a ${OBJS}`；`make clean` 删除 `*.o *.a *~`。

## 6. README 维护记录（自底向上）

- **定位与职责**：LSODE 常微分方程求解器，支撑轨道与 R 矩阵外区传播，产物并入 `libfac.a`。
- **底层依据**：`lsode.f`、`stode.f`、`intdy.f`、`prepj.f`、`cfode.f`。
- **输入/输出**：ODE 初值与容差；输出时间序列解与状态信息。
- **验证与回归**：通过轨道积分、R 矩阵工作流与 `demo` 间接验证。
- **已知限制**：第三方代码；目录未附原始用户手册，接口以 `lsode.f` 头注释为准。
- **公式核查**：源码未找到独立于 Fortran 实现的 ODE 方法公式原文，需按 LSODE 文档人工核查。
- **导航**：父级 [`../README.md`](../README.md)。

[返回上级](../README.md)