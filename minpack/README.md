# MINPACK 优化程序目录（minpack/）

## 1. 目录定位与来源

本目录是第三方数值库 **MINPACK**（Argonne National Laboratory，Burton S. Garbow、Kenneth E. Hillstrom、Jorge J. Moré，源码注释标注 1980 与 1996 两个版本时间）的 Fortran 77 子集。根 README「Third party content that cannot be distributed under GPL」与 `UtilList` 均列出本目录（原文：`minpack/, minpack optimization package.`），随 `fac_util.tar.gz` 分发，不按 GPL 授权。

在 FAC 计算链中它承担**非线性最小二乘拟合**角色：核心库 `faclib/interpolation.c` 用它对插值/拟合参数做 Levenberg–Marquardt 优化（`LMDER`），并以 `CHKDER` 做梯度一致性校验。FAC 通过 `faclib/cf77.h`、`faclib/f2c.h`、`faclib/f2c.f90` 中的桥接宏调用这些例程。

## 2. 组织形式与文件分类

共 8 个 `.f` 文件与 1 个 `Makefile.in`，全部为双精度（`d` 前缀或不带前缀但内部双精度）实现：

- **用户级求解器**：`lmder.f`（完整控制参数版）、`lmder1.f`（简化参数版）
- **Levenberg–Marquardt 内部步骤**：`lmpar.f`（阻尼参数求解）、`qrfac.f`（带列主元的 QR 分解）、`qrsolv.f`（带对角约束的最小二乘求解）
- **机器参数与范数辅助**：`dpmpar.f`、`enorm.f`
- **梯度校验工具**：`chkder.f`

内部调用关系：`lmder1` → `lmder`；`lmder` → `qrfac`、`lmpar`、`enorm`、`dpmpar`；`lmpar` → `qrsolv`、`enorm`、`dpmpar`；`qrfac` → `enorm`、`dpmpar`；`chkder` → `dpmpar`。

## 3. 逐文件说明

- **`chkder.f`** — 功能：检查 `m` 个非线性函数在 `n` 个变量处的梯度与函数值是否一致。入口签名：`subroutine chkder(m,n,x,fvec,fjac,ldfjac,xp,fvecp,mode,err)`（`m` 函数个数、`n` 变量个数；`x` 求值点；`fvec` 函数值；`fjac` 梯度矩阵（每行一个函数的梯度）；`ldfjac` 主维；`xp` 相邻点；`fvecp` 在 `xp` 处的函数值；`mode` 调用阶段；`err` 输出梯度正确性度量）。数值方法要点：需调用两次——`mode = 1` 由 `x` 生成相邻点 `xp`，`mode = 2` 依据 `fvec`、`fvecp`、`fjac` 计算各梯度的相对误差估计；对舍入误差敏感，分量不可过小或为零。在 FAC 中的调用方：`faclib/interpolation.c:461`、`faclib/interpolation.c:465`（位于被 `/* ... */` 注释掉的雅可比校验调试段中，当前不生效）；桥接声明见 `faclib/cf77.h:262`、`faclib/f2c.h:78`、`faclib/f2c.f90:523`。

- **`dpmpar.f`** — 功能：返回双精度机器参数。入口签名：`double precision function dpmpar(i)`（`i` 取 1、2、3）。数值方法要点：`i = 1` 机器精度、`i = 2` 最小正数量级、`i = 3` 最大数量级；源码内含多组按机型（IBM 360/370、Honeywell、CDC、IEEE 等）准备的 `DATA` 语句，需按目标机器激活其中一组。在 FAC 中的调用方：未发现 FAC 直接调用（由本目录 `lmder`、`lmpar`、`qrfac`、`chkder` 内部调用）。

- **`enorm.f`** — 功能：计算 `n` 维向量的欧氏范数。入口签名：`double precision function enorm(n,x)`。数值方法要点：把分量按小、中、大三组分别累平方和，对小/大分量做缩放以防上溢/下溢；依赖常数 `rdwarf`、`rgiant`，并对中间分量使用未缩放平方和。在 FAC 中的调用方：未发现 FAC 直接调用（由本目录 `lmder`、`lmpar`、`qrfac` 内部调用）。

- **`lmder.f`** — 功能：用修正的 Levenberg–Marquardt 算法最小化 `m` 个非线性函数在 `n` 个变量下的平方和，用户同时提供函数与雅可比。入口签名：`subroutine lmder(fcn,m,n,x,fvec,fjac,ldfjac,ftol,xtol,gtol,maxfev,diag,mode,factor,nprint,info,nfev,njev,ipvt,qtf,wa1,wa2,wa3,wa4)`（`fcn` 用户回调；`x` 初值/解；`fvec` 残差；`fjac` 雅可比与上三角 R；`ftol`/`xtol`/`gtol` 收敛判据；`maxfev` 函数求值上限；`diag` 变量缩放，`mode = 1` 时由用户给定；`factor` 初始阻尼因子；`nprint` 打印控制；`info` 终止状态；`nfev`/`njev` 求值计数；`ipvt` 主元数组；`qtf`、`wa1`~`wa4` 工作区）。数值方法要点：每步用 `qrfac` 做带列主元 QR 分解，再经 `lmpar` 求阻尼参数解信赖域子问题；用户回调约定 `subroutine fcn(m,n,x,fvec,fjac,ldfjac,iflag)`，`iflag = 1` 只算函数、`iflag = 2` 只算雅可比，置负整数可主动终止。在 FAC 中的调用方：`faclib/interpolation.c:476`（插值/拟合主求解入口）；桥接声明见 `faclib/cf77.h:248`、`faclib/f2c.h:76`、`faclib/f2c.f90:504`。

- **`lmder1.f`** — 功能：`lmder` 的简化接口，只暴露单一相对误差容差 `tol`。入口签名：`subroutine lmder1(fcn,m,n,x,fvec,fjac,ldfjac,tol,info,ipvt,wa,lwa)`（`tol` 收敛容差；`wa` 长度 `lwa` 的工作区；`ipvt` 主元数组；其余同 `lmder`）。数值方法要点：内部设定 `ftol`、`xtol`、`gtol`、`maxfev`、`mode`、`factor` 等默认控制参数后转调 `lmder`；用户回调 `fcn` 约定与 `lmder` 相同。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`lmpar.f`** — 功能：给定 QR 分解结果，求阻尼参数 `par` 使缩放后解的范数满足信赖域约束。入口签名：`subroutine lmpar(n,r,ldr,ipvt,diag,qtb,delta,par,x,sdiag,wa1,wa2)`（`r` 上三角 R（`ldr` 主维）；`ipvt` 主元；`diag` 对角缩放；`qtb` 为 `(q^T)b` 前 `n` 项；`delta` 信赖域半径；`par` 输入初值/输出阻尼；`x` 解；`sdiag`、`wa1`、`wa2` 工作区）。数值方法要点：利用 `R` 与置换矩阵把带约束最小二乘化为上三角问题；迭代最多 10 次，每次经 `qrsolv` 求解并调整 `par`，用 `enorm` 计算缩放范数。在 FAC 中的调用方：未发现 FAC 直接调用（由 `lmder` 内部调用）。

- **`qrfac.f`** — 功能：用可选列主元的 Householder 变换计算 `m×n` 矩阵的 QR 分解。入口签名：`subroutine qrfac(m,n,a,lda,pivot,ipvt,lipvt,rdiag,acnorm,wa)`（`a` 输入矩阵/`lda` 主维；`pivot` 是否列主元；`ipvt`（长度 `lipvt`）主元数组；`rdiag` R 的对角元素；`acnorm` 各列范数；`wa` 工作区）。数值方法要点：Householder 向量以紧凑形式存于 `a` 的下梯形部分，R 的对角元按模递减排列，保证数值稳定。在 FAC 中的调用方：未发现 FAC 直接调用（由 `lmder` 内部调用）。

- **`qrsolv.f`** — 功能：在已有 QR 分解基础上求解带对角约束的最小二乘系统。入口签名：`subroutine qrsolv(n,r,ldr,ipvt,diag,qtb,x,sdiag,wa)`（`r` 上三角 R、`ldr` 主维；`ipvt` 主元；`diag` 对角矩阵；`qtb` 右端；`x` 解；`sdiag`、`wa` 工作/输出）。数值方法要点：把原问题等价变换为上三角系统后回代，秩亏时给出最小二乘解；同时输出因子 `S` 的上三角部分，供后续阻尼迭代复用。在 FAC 中的调用方：未发现 FAC 直接调用（由 `lmpar` 内部调用）。

## 4. 接口与调用约定

- **Fortran 77 固定格式**，双精度（`DOUBLE PRECISION`）实数运算；数组采用显式长度声明如 `x(n)`、`fjac(ldfjac,n)`。
- **用户回调是关键约定**：求解器通过 `external fcn` 接收用户子程序，统一签名为 `subroutine fcn(m,n,x,fvec,fjac,ldfjac,iflag)`；`iflag = 1` 仅填 `fvec`，`iflag = 2` 仅填 `fjac`，不得改动另一个；`iflag < 0` 可中止求解。C 侧在 `faclib/interpolation.c` 中提供 `MinFunc` 作为该回调，再由 `cf77.h` 的 `ROUTINE` 参数类型传入。
- 矩阵以列主序存放，`ldfjac`/`ldr`/`lda` 为主维长度；`ipvt` 记录列交换置换，使 `a*p = q*r`。
- `info` 返回终止状态码；`nfev`、`njev` 返回函数与雅可比求值次数；`diag` 配合 `mode` 决定变量是否由用户预缩放（`mode = 1`）还是内部自动缩放（`mode = 2`）。
- 工作区数组（`wa1`~`wa4`、`qtf`、`sdiag` 等）由调用方分配，`lmder1` 还要求给出 `lwa` 以便内部拆分。
- `dpmpar` 的机器相关 `DATA` 语句需要安装者按目标平台选择，这是移植时的主要手工步骤。

## 5. 与上下游目录关系、构建方式

- 上游：本目录不调用 `blas/`，而是自带 `enorm` 完成范数计算；`dpmpar` 提供机器常数。与 `quadpack/` 为并列关系，两者产物都链入同一库。
- 下游：`faclib/interpolation.c` 是唯一实际使用方（`LMDER` 活跃，`CHKDER` 仅在注释调试段中）；C 代码经 `faclib/cf77.h`、`faclib/f2c.h`、`faclib/f2c.f90` 与 `genf2c.py` 生成的包装层调用。
- 构建：根 `configure` 后进入本目录执行 `make`。`Makefile.in` 中 `FC = @F77@`、`FFLAGS = @FFLAGS@`，`SRC` 列出 8 个 `.f`，`.f.o` 规则编译后由 `ar r ${TOPDIR}/libfac.a $(OBJS)` 把目标文件**直接并入顶层 `libfac.a`**（不生成独立库）。`make clean` 删除 `*.o`、`*.a`、`*~`。
- 根 `Makefile.in` 的 `lib` 目标在 `blas`、`lapack`、`coul`、`ode`、`toms`、`mpfun` 之后、`quadpack` 之前执行 `cd minpack; make`，最后统一 `ranlib libfac.a`。

## 6. README 维护记录（自底向上）

- **定位与职责**：最小二乘与非线性求解例程集，产物直接并入 `libfac.a`。
- **底层依据**：`lmder.f`、`lmpar.f`、`qrfac.f`、`qrsolv.f`、`chkder.f`；主要被 `faclib/interpolation.c` 使用。
- **输入/输出**：残差函数与初值；输出拟合参数与协方差相关信息。
- **验证与回归**：通过插值与 `demo` 计算链间接验证。
- **已知限制**：第三方代码；`chkder.f` 仅用于调试段。
- **公式核查**：源码未找到独立于 Fortran 实现的最小二乘数学公式原文，需按 MINPACK 文档人工核查。
- **导航**：父级 [`../README.md`](../README.md)。

[返回上级](../README.md)