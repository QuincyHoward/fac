# BLAS 子程序目录（blas/）

## 1. 目录定位与来源

本目录收录经典第三方数值库 **BLAS（Basic Linear Algebra Subprograms）** 的 Fortran 77 实现子集。根 README「Third party content that cannot be distributed under GPL」一节与 `UtilList` 均将其列为随 FAC 打包的第三方内容（原文：`blas/, BLAS routines in fortran.`），随 `fac_util.tar.gz` 分发，不按 GPL 授权。

在 FAC 计算链中它处于最底层：为上层的 `lapack/`（本包的 LAPACK 子集大量调用本目录的矩阵/向量内核）以及核心库 `faclib` 提供基础线性代数运算（向量缩放、点积、矩阵-向量乘、矩阵-矩阵乘、三角方程求解等）。C 语言编写的 FAC 核心通过 `faclib/cf77.h`、`faclib/f2c.h`、`faclib/f2c.f90` 中的桥接层把 `ddot`、`dscal`、`dgemv` 暴露给业务代码。

## 2. 组织形式与文件分类

共 20 个 `.f` 文件与 1 个 `Makefile.in`，全部为单文件单入口的固定格式 Fortran 77 源码。按 BLAS 层次分类：

- **一级（向量-向量）**：`dasum.f`、`daxpy.f`、`dcopy.f`、`ddot.f`、`dnrm2.f`、`drot.f`、`dscal.f`、`dswap.f`、`idamax.f`
- **二级（矩阵-向量）**：`dgemv.f`、`dger.f`、`dspmv.f`、`dspr2.f`、`dtrmv.f`、`dtbsv.f`
- **三级（矩阵-矩阵）**：`dgemm.f`、`dtrmm.f`、`dtrsm.f`
- **辅助例程**：`lsame.f`（字符标志比较）、`xerbla.f`（参数错误处理器）

本目录只保留了 `d` 前缀的双精度实数版本，未打包单精度（`s`）、复数（`c`/`z`）版本。

## 3. 逐文件说明

- **`dasum.f`** — 功能：求向量各元素绝对值之和。入口签名：`double precision function dasum(n,dx,incx)`（`n` 元素个数；`dx` 双精度数组；`incx` 元素步长）。数值方法要点：逐步累加 `dabs`；对 `incx = 1` 使用 6 路循环展开，支持负步长从数组尾部反向遍历。在 FAC 中的调用方：未发现 FAC 直接调用（检索范围 `faclib`、`coul`、`modqed`、`mpfun`、`ionis`，下同）。

- **`daxpy.f`** — 功能：常数乘向量再加向量。入口签名：`subroutine daxpy(n,da,dx,incx,dy,incy)`（`da` 标量系数；`dx`/`dy` 输入、输出向量；`incx`/`incy` 步长）。数值方法要点：对 `dx` 与 `dy` 分别按步长寻址，`da = 0` 或 `n <= 0` 时直接返回；步长均为 1 时 4 路展开。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dcopy.f`** — 功能：向量复制。入口签名：`subroutine dcopy(n,dx,incx,dy,incy)`（参数含义同 `daxpy`，无标量系数）。数值方法要点：按各自步长逐元素赋值；步长均为 1 时 7 路展开。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`ddot.f`** — 功能：两向量点积。入口签名：`double precision function ddot(n,dx,incx,dy,incy)`（两向量及各自步长）。数值方法要点：累加对应元素乘积；步长均为 1 时 5 路展开。在 FAC 中的调用方：`faclib/cf77.h:270`、`faclib/f2c.h:80`、`faclib/f2c.f90:533` 中有 cfortran/f2c 桥接声明；未发现 FAC 业务逻辑直接调用。

- **`dgemm.f`** — 功能：通用矩阵-矩阵乘及加（含转置选项）。入口签名：`SUBROUTINE DGEMM(TRANSA,TRANSB,M,N,K,ALPHA,A,LDA,B,LDB,BETA,C,LDC)`（`TRANSA`/`TRANSB` 指定是否转置；`M`/`N`/`K` 为矩阵维数；`ALPHA`/`BETA` 标量；`A`/`B`/`C` 矩阵；`LDA`/`LDB`/`LDC` 为主维数）。数值方法要点：按 `TRANSA`、`TRANSB` 分四种情况做分块循环，先赋 `BETA*C` 再累加乘项，内部使用 `lsame` 判断字符标志。在 FAC 中的调用方：未发现 FAC 直接调用；同包 `lapack/` 中大量例程依赖此内核。

- **`dgemv.f`** — 功能：矩阵-向量乘及加。入口签名：`SUBROUTINE DGEMV(TRANS,M,N,ALPHA,A,LDA,X,INCX,BETA,Y,INCY)`（`TRANS` 指定用 `A` 或转置；`X`/`Y` 向量及步长；其余同 `dgemm`）。数值方法要点：按转置标志选择行/列遍历，结果累加到 `Y`。在 FAC 中的调用方：`faclib/cf77.h:280`、`faclib/f2c.h:84`、`faclib/f2c.f90:559` 中有桥接声明；未发现 FAC 业务逻辑直接调用。

- **`dger.f`** — 功能：矩阵秩一更新。入口签名：`SUBROUTINE DGER(M,N,ALPHA,X,INCX,Y,INCY,A,LDA)`（`X` 长 `m`、`Y` 长 `n`，`A` 为 `m×n`）。数值方法要点：以 `X` 元素为因子对 `A` 的对应行做 `ALPHA` 缩放累加。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dnrm2.f`** — 功能：求向量欧氏范数。入口签名：`DOUBLE PRECISION FUNCTION DNRM2(N,X,INCX)`。数值方法要点：采用缩放平方和方式（内联 `DLASSQ` 逻辑，维护 `SCALE` 与 `SSQ`），最后乘 `SQRT`，避免中间溢出/下溢。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`drot.f`** — 功能：对两向量施加平面旋转。入口签名：`subroutine drot(n,dx,incx,dy,incy,c,s)`（`c`、`s` 为旋转系数）。数值方法要点：先算临时量再原地更新 `dx`、`dy`，支持任意（含负）步长。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dscal.f`** — 功能：向量按常数缩放。入口签名：`subroutine dscal(n,da,dx,incx)`。数值方法要点：对 `incx > 0` 按步长就地乘；`incx = 1` 时 5 路展开。在 FAC 中的调用方：`faclib/cf77.h:275`、`faclib/f2c.h:82`、`faclib/f2c.f90:542` 中有桥接声明；未发现 FAC 业务逻辑直接调用。

- **`dspmv.f`** — 功能：对称压缩存储矩阵的矩阵-向量乘。入口签名：`SUBROUTINE DSPMV(UPLO,N,ALPHA,AP,X,INCX,BETA,Y,INCY)`（`UPLO` 指定 `AP` 中存上三角还是下三角；`AP` 长度至少 `n(n+1)/2`，按列压缩）。数值方法要点：由 `UPLO` 决定读取压缩三角的两种索引路径，结果累加到 `Y`。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dspr2.f`** — 功能：对称压缩矩阵的秩二更新。入口签名：`SUBROUTINE DSPR2(UPLO,N,ALPHA,X,INCX,Y,INCY,AP)`。数值方法要点：对称地更新 `AP` 中上三角或下三角部分，避免重复存储。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dswap.f`** — 功能：交换两向量内容。入口签名：`subroutine dswap(n,dx,incx,dy,incy)`。数值方法要点：经临时变量逐元素互换；步长均为 1 时 3 路展开。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dtbsv.f`** — 功能：三角带状线性方程组求解。入口签名：`SUBROUTINE DTBSV(UPLO,TRANS,DIAG,N,K,A,LDA,X,INCX)`（`K` 为带宽参数，`A` 含 `k+1` 条对角线，`DIAG` 指定是否单位三角）。数值方法要点：按上/下三角与是否转置分情况做回代/前代；不进行奇异性检测，需调用方预先保证。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dtrmm.f`** — 功能：三角矩阵乘（矩阵-矩阵）。入口签名：`SUBROUTINE DTRMM(SIDE,UPLO,TRANSA,DIAG,M,N,ALPHA,A,LDA,B,LDB)`（`SIDE` 指定三角矩阵左乘或右乘）。数值方法要点：按 `SIDE`/`UPLO`/`TRANSA`/`DIAG` 组合分情况就地更新 `B`，利用三角结构跳过零块。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dtrmv.f`** — 功能：三角矩阵乘（矩阵-向量）。入口签名：`SUBROUTINE DTRMV(UPLO,TRANS,DIAG,N,A,LDA,X,INCX)`。数值方法要点：原地更新 `X`，按三角与转置标志选择遍历顺序。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`dtrsm.f`** — 功能：三角线性方程组求解（矩阵右端项）。入口签名：`SUBROUTINE DTRSM(SIDE,UPLO,TRANSA,DIAG,M,N,ALPHA,A,LDA,B,LDB)`。数值方法要点：求解后被覆盖写入 `B`；按左右乘与三角方向分情形回代。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`idamax.f`** — 功能：返回绝对值最大元素的下标。入口签名：`integer function idamax(n,dx,incx)`。数值方法要点：线性扫描维护当前最大值，`n < 1` 或 `incx <= 0` 返回 0。在 FAC 中的调用方：未发现 FAC 直接调用。

- **`lsame.f`** — 功能：判断两字符是否等价（忽略大小写）。入口签名：`LOGICAL FUNCTION LSAME(CA,CB)`。数值方法要点：文件内含多套机器相关版本（CDC 6/12 位表示、ASCII 等）以源码注释/并列定义形式给出，实际生效版本取决于编译器所选分支；使用字符偏移实现大小写归一。在 FAC 中的调用方：未发现 FAC 直接调用（作为底层辅助例程供 BLAS/LAPACK 内部使用）。

- **`xerbla.f`** — 功能：LAPACK/BLAS 参数错误处理器。入口签名：`SUBROUTINE XERBLA(SRNAME,INFO)`（`SRNAME` 为出错例程名，`INFO` 为非法参数序号）。数值方法要点：打印固定格式错误消息后执行 `STOP` 终止；源码注明安装者可改写 `STOP` 以接入系统异常处理。在 FAC 中的调用方：未发现 FAC 直接调用（同包 `lapack/` 例程的参数校验入口）。

## 4. 接口与调用约定

- 全部为 **Fortran 77 固定格式**：第 1 列为 `C`/`*` 表示注释，续行在第 6 列，语句区从第 7 列起；变量名遵循 6 字符限制。
- 前缀含义：`D` = DOUBLE PRECISION（双精度实数）。常见 BLAS 前缀还有 `S`（单精度）、`C`/`Z`（复数/双复数），本目录未包含。`LSAME`、`XERBLA` 无精度前缀，属于通用辅助例程。
- 向量以 `(*)` 或 `(1)` 形式声明，元素由 `INCX`/`INCY` 步长寻址；步长为负表示从数组末端反向遍历，步长不得为零。
- 矩阵按列主序存放，`LDA`/`LDB`/`LDC` 是调用方声明的首维（主维）长度，必须不小于对应行数。
- 字符标志采用单字符约定：`'N'/'T'/'C'`（不转置/转置/共轭转置）、`'U'/'L'`（上/下三角）、`'S'/'R'`（左/右乘）；大小写等价由 `lsame` 保证。
- 一级向量运算中 `dasum`、`ddot`、`dnrm2`、`idamax` 为**函数**，结果经函数名返回；其余为**子程序**，结果写入输出参数（如 `dy`、`y`、`a`、`x`）。
- 参数错误不返回错误码，而是调用 `xerbla` 打印信息并终止程序。

## 5. 与上下游目录关系、构建方式

- 无更底层依赖，是 FAC  bundled 数值栈的最底层。`lapack/` 中的 `dgesv`、`dgeev`、`dlarfb`、`dtrevc` 等大量例程直接调用这里的 BLAS 内核。
- 对上：`faclib` 通过 `cf77.h`（cfortran 宏）与 `f2c.h`/`f2c.f90`（f2c 生成的 Fortran 90 包装）桥接 `ddot`、`dscal`、`dgemv`；`genf2c.py` 负责生成这些包装。
- 构建：先运行根 `configure` 生成各目录 `Makefile`。本目录 `Makefile.in` 中 `FC = @F77@`、`FFLAGS = @FFLAGS@`，`SRC` 列出 20 个 `.f`，经模式规则 `.f.o` 编译为 `.o`，目标 `blas` 用 `ar r ${TOPDIR}/libmblas.a $(OBJS)` 归档为独立的 **`libmblas.a`**（注意：不同于 `minpack`/`quadpack` 归入 `libfac.a`）。`make clean` 删除 `*.o`、`*.a`、`*~`。
- 根 `Makefile.in` 的 `lib` 目标首先执行 `cd blas; make`，随后才构建 `lapack`、`coul`、`ode`、`toms`、`mpfun`、`minpack`、`quadpack`、`ionis`、`modqed`、`faclib`，最后 `ranlib libfac.a`；因此本目录必须最先构建。

## 6. README 维护记录（自底向上）

- **定位与职责**：最底层 BLAS 双精度子集，先于其他数值库构建，产物为 `libmblas.a`。
- **底层依据**：`ddot.f`、`dscal.f`、`dgemv.f`、`dgemm.f`、`xerbla.f`；由 `genf2c.py` 生成 C 桥接包装。
- **输入/输出**：向量与矩阵参数；输出 BLAS 标准运算结果。
- **验证与回归**：无独立基准；通过上层 LAPACK、`faclib/` 与 `demo` 回归间接验证。
- **已知限制**：第三方代码，不能按 GPL 重新分发；不要修改原始版权头。
- **公式核查**：源码未找到独立于 Fortran 实现的数学公式原文，算法依据需按 BLAS 规范人工核查。
- **导航**：父级 [`../README.md`](../README.md)；上层 [`../lapack/README.md`](../lapack/README.md)。

[返回上级](../README.md)