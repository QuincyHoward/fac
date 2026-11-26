# FAC 内置 LAPACK 子集（lapack/）

## 1. 目录定位

`lapack/` 是随 FAC（Flexible Atomic Code）核心库一同 bundled 的 LAPACK 子集（**LAPACK 3.0/3.1，仅含双精度实数 `d` 系列例程**）。它为 FAC 核心库提供稠密与带状线性代数能力：奇异值分解（SVD）、对称/非对称矩阵特征值、LU / QR / LQ / Cholesky 相关分解、线性方程组求解，以及大量正交变换与矩阵工具例程。

本目录属于**第三方代码**，不能按 GPL 分发。根据根目录 `README.md` "Contents of FAC" 中 **UtilList** 原始章节的说明，`blas/`、`coul/`、`ionis/`、`lapack/`、`minpack/`、`quadpack/`、`mpfun/`、`ode/`、`toms/` 等目录随 `fac_util.tar.gz` 分发，列于 `UtilList` 文件中（参见 [根 README](../README.md)）；而 `faclib/`、`python/`、`sfac/` 等核心目录则以 GPL 随 `fac_core.tar.gz` 分发。本目录中的源码头部均保留 LAPACK 原始版权与版本声明，请勿修改。

## 2. 组织形式

共 112 个 Fortran 77 源码文件（111 个列入 `Makefile.in` 的 `SRC`，`dlamch.f` 单独以无优化选项编译）。按其所属的 LAPACK 函数族可归为：

1. **线性方程组驱动例程**：`dgesv`、`dgbsv`。
2. **LU / 带状 LU 分解与 utilities**：`dgetrf`/`dgetf2`/`dgetrs`、`dgbtrf`/`dgbtf2`/`dgbtrs`、`dlaswp`。
3. **一般（非对称）矩阵特征值**：`dgeev`、`dgebal`/`dgebak`、`dgehd2`/`dgehrd`、`dhseqr`/`dlahqr`、`dlanv2`、`dtrevc`、`dlaln2`、`dlahrd`。
4. **对称矩阵特征值（打包/带状/三对角）**：`dspev`/`dspevd`/`dsbev`、`dsbtrd`/`dsptrd`、`dstedc`/`dsteqr`/`dsterf`、`dlae2`/`dlaev2`、`dopgtr`/`dopmtr`，以及范数函数 `dlansb`/`dlansp`/`dlanst`。
5. **对称三对角特征值分治辅助（DLAED 族）**：`dlaed0`–`dlaed9`、`dlaeda`。
6. **SVD 驱动与双对角化**：`dgesdd`、`dgebrd`/`dgebd2`/`dlabrd`、`dbdsdc`/`dbdsqr`。
7. **双对角 SVD 分治辅助（DLASD 族）**：`dlasd0`–`dlasd8`、`dlasda`、`dlasdq`、`dlasdt`。
8. **dqds 奇异值辅助（DLASQ 族）**：`dlasq1`–`dlasq6`。
9. **QR / LQ 分解与正交矩阵生成/应用**：`dgeqr2`/`dgeqrf`、`dgelq2`/`dgelqf`、`dlarfg`/`dlarf`/`dlarft`/`dlarfb`/`dlarfx`、`dorg*` 与 `dorm*` 系列。
10. **平面旋转与向量工具**：`dlartg`、`dlartv`、`dlar2v`、`dlargv`、`dlasr`、`dladiv`。
11. **通用工具、范数与机器环境常数**：`dlamch`、`dlabad`、`ilaenv`、`ieeeck`、`dlapy2`、`dlas2`/`dlasv2`、`dlascl`、`dlaset`、`dlacpy`、`dlassq`、`dlamrg`、`dlasrt`、`dlange`、`dlanhs`。

> 调用情况说明：FAC C 核心**直接调用**的 LAPACK 例程只有 7 个——`DGESV`、`DGBSV`、`DGEEV`、`DGESDD`、`DSPEV`、`DSBEV`、`DSPEVD`。它们经 `faclib/f2c.h`、`faclib/cf77.h`、`faclib/f2c.f90` 中的桥接层暴露给 C。其余例程均为这些驱动例程或 LAPACK 内部层级所调用的工具/辅助例程，FAC 本身不直接调用。

## 3. 逐文件说明

下表中"FAC 调用者"一栏，凡标注"通用 LAPACK 例程"者，表示在 `faclib/`、`coul/`、`modqed/`、`mpfun/` 中未发现 FAC 直接调用点。

### 3.1 线性方程组驱动例程

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dgesv.f` | 线性方程组驱动 | 求解实一般方阵 `A*X=B`（A 为 N×N，X/B 为 N×NRHS） | `SUBROUTINE DGESV(N, NRHS, A, LDA, IPIV, B, LDB, INFO)` | `faclib/rmatrix.c`、`faclib/crm.c`、`faclib/polarization.c`、`faclib/structure.c`（经 `f2c.h`/`cf77.h`/`f2c.f90` 桥接） | 部分主元 LU 分解 `A=P*L*U` 后回代求解 |
| `dgbsv.f` | 线性方程组驱动 | 求解实带状矩阵方程组 `A*X=B`（KL 条次对角线、KU 条超对角线） | `SUBROUTINE DGBSV(N, KL, KU, NRHS, AB, LDAB, IPIV, B, LDB, INFO)` | `faclib/orbital.c`（ orbitals  Commentary 中说明用于求解带状矩阵方程；经桥接层） | 带状 LU（部分主元、行交换）分解后回代 |

### 3.2 LU / 带状 LU 分解与工具

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dgetrf.f` | LU 分解 | 计算一般 M×N 矩阵的 LU 分解 `A=P*L*U` | `SUBROUTINE DGETRF(M, N, A, LDA, IPIV, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | blocking（Level 3 BLAS）的右看式 partial pivoting LU |
| `dgetf2.f` | LU 分解 | 计算一般 m×n 矩阵的 LU 分解（非阻塞版） | `SUBROUTINE DGETF2(M, N, A, LDA, IPIV, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 右看式 Level 2 BLAS 的 partial pivoting LU |
| `dgetrs.f` | 线性方程组求解 | 用 `DGETRF` 的 LU 因子求解 `A*X=B` 或 `A'*X=B` | `SUBROUTINE DGETRS(TRANS, N, NRHS, A, LDA, IPIV, B, LDB, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 前代/回代求解，TRANS 控制转置 |
| `dgbtrf.f` | 带状 LU 分解 | 计算 m×n 带状矩阵的 LU 分解（阻塞版） | `SUBROUTINE DGBTRF(M, N, KL, KU, AB, LDAB, IPIV, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带存储下 partial pivoting、调用 Level 3 BLAS |
| `dgbtf2.f` | 带状 LU 分解 | 计算 m×n 带状矩阵的 LU 分解（非阻塞版） | `SUBROUTINE DGBTF2(M, N, KL, KU, AB, LDAB, IPIV, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带存储下 partial pivoting、调用 Level 2 BLAS |
| `dgbtrs.f` | 带状方程组求解 | 用 `DGBTRF` 的带状 LU 因子求解 `A*X=B` 或 `A'*X=B` | `SUBROUTINE DGBTRS(TRANS, N, KL, KU, NRHS, AB, LDAB, IPIV, B, LDB, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带状前代/回代求解 |
| `dlaswp.f` | 矩阵工具 | 对矩阵 A 执行一系列行交换（行 K1 至 K2） | `SUBROUTINE DLASWP(N, A, LDA, K1, K2, IPIV, INCX)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 按 IPIV 向量逐行交换，LU 主元的核心操作 |

### 3.3 一般（非对称）矩阵特征值

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dgeev.f` | 非对称特征值驱动 | 计算 N×N 实非对称矩阵的特征值，及可选左/右特征向量 | `SUBROUTINE DGEEV(JOBVL, JOBVR, N, A, LDA, WR, WI, VL, LDVL, VR, LDVR, WORK, LWORK, INFO)` | `faclib/structure.c`（`GenEigen` 等多处，`dgeev_mode` 控制；经桥接层） | 平衡→Hessenberg 化简→DHSEQR 的 QR 算法→回代特征向量 |
| `dgebal.f` | 平衡 | 对一般实矩阵 A 做置换与对角相似变换平衡，改善特征值精度 | `SUBROUTINE DGEBAL(JOB, N, A, LDA, ILO, IHI, SCALE, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 可选用置换隔离特征值 + 对角缩放 |
| `dgebak.f` | 平衡回变换 | 对 `DGEBAL` 平衡后矩阵的特征向量做逆变换，得到原矩阵特征向量 | `SUBROUTINE DGEBAK(JOB, SIDE, N, ILO, IHI, SCALE, M, V, LDV, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 按 SCALE/置换执行逆相似变换 |
| `dgehd2.f` | Hessenberg 化简 | 将一般矩阵化为上 Hessenberg 形（非阻塞版） | `SUBROUTINE DGEHD2(N, ILO, IHI, A, LDA, TAU, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 正交相似变换 `Q'*A*Q=H`，初等反射器 |
| `dgehrd.f` | Hessenberg 化简 | 将一般矩阵化为上 Hessenberg 形（阻塞版） | `SUBROUTINE DGEHRD(N, ILO, IHI, A, LDA, TAU, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 `DLAHRD` 的块反射器压缩表示 |
| `dhseqr.f` | Schur 分解 | 计算实上 Hessenberg 矩阵特征值，及可选 Schur 形 T 与 Schur 向量 Z | `SUBROUTINE DHSEQR(JOB, COMPZ, N, ILO, IHI, H, LDH, WR, WI, Z, LDZ, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 双重步隐式位移 QR（多位移/小矩阵回退 `DLAHQR`） |
| `dlahqr.f` | Schur 辅助 | `DHSEQR` 的辅助例程，处理 ILO:IHI 的 Hessenberg 子块 | `SUBROUTINE DLAHQR(WANTT, WANTZ, N, ILO, IHI, H, LDH, WR, WI, ILOZ, IHIZ, Z, LDZ, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 传统双重位移隐式 QR（含例外位移） |
| `dlanv2.f` | 2×2 Schur | 计算实 2×2 非对称矩阵的 Schur 分解，返回实或共轭复特征值 | `SUBROUTINE DLANV2(A, B, C, D, RT1R, RT1I, RT2R, RT2I, CS, SN)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 用平面旋转化为标准 Schur 形 |
| `dtrevc.f` | 特征向量 | 计算实上准三角矩阵 T 的部分或全部左/右特征向量 | `SUBROUTINE DTREVC(SIDE, HOWMNY, SELECT, N, T, LDT, VL, LDVL, VR, LDVR, MM, M, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 反向代换（含复共轭 2×2 块处理） |
| `dlaln2.f` | 小型线性系统 | 求解 `(ca*A - w*D)*X = s*B` 类 1×1/2×2 系统（可缩放/扰动） | `SUBROUTINE DLALN2(LTRANS, NA, NW, SMIN, CA, A, LDA, D1, D2, B, LDB, WR, WI, X, LDX, SCALE, XNORM, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带缩放的小规模直接求解，用于逆迭代 |
| `dlahrd.f` | Hessenberg 辅助 | 化简 n×(n-k+1) 矩阵的前 NB 列至第 k 次次对角线以下为零，返回块反射器 V、T 与 Y | `SUBROUTINE DLAHRD(N, K, NB, A, LDA, TAU, T, LDT, Y, LDY)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块反射器 `H=I-V*T*V'`，供 `DGEHRD` 调用 |

### 3.4 对称矩阵特征值（打包/带状/三对角）

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dspev.f` | 对称特征值驱动 | 计算打包存储实对称矩阵的全部特征值及可选特征向量 | `SUBROUTINE DSPEV(JOBZ, UPLO, N, AP, W, Z, LDZ, WORK, INFO)` | `faclib/structure.c`（`GenEigen` 等；经桥接层） | `DSPTRD` 化三对角 + `DSTEQR` QL/QR |
| `dspevd.f` | 对称特征值驱动 | 计算打包实对称矩阵特征值及可选特征向量（分治法求特征向量） | `SUBROUTINE DSPEVD(JOBZ, UPLO, N, AP, W, Z, LDZ, WORK, LWORK, IWORK, LIWORK, INFO)` | 已在 `faclib/f2c.h`、`faclib/cf77.h`、`faclib/f2c.f90` 桥接，未发现 FAC 直接调用点 | `DSPTRD` + `DSTEDC` 分治求特征向量 |
| `dsbev.f` | 对称特征值驱动 | 计算实对称带状矩阵的全部特征值及可选特征向量 | `SUBROUTINE DSBEV(JOBZ, UPLO, N, KD, AB, LDAB, W, Z, LDZ, WORK, INFO)` | `faclib/structure.c`（`geneign` 带状路径；经桥接层） | `DSBTRD` 化三对角 + `DSTEQR` |
| `dsptrd.f` | 三对角化 | 将打包存储的实对称矩阵经正交相似变换化为对称三对角 T | `SUBROUTINE DSPTRD(UPLO, N, AP, D, E, TAU, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | Householder 反射器，`Q'*A*Q=T` |
| `dsbtrd.f` | 三对角化 | 将实对称带状矩阵经正交相似变换化为对称三对角 T | `SUBROUTINE DSBTRD(VECT, UPLO, N, KD, AB, LDAB, D, E, Q, LDQ, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带状 Householder 化简，可选累积 Q |
| `dstedc.f` | 三对角特征值驱动 | 用分治法计算对称三对角矩阵全部特征值及可选特征向量 | `SUBROUTINE DSTEDC(COMPZ, N, D, E, Z, LDZ, WORK, LWORK, IWORK, LIWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 分治 + 秩一修正的割线方程求解 |
| `dsteqr.f` | 三对角特征值 | 用隐式 QL/QR 计算对称三对角矩阵特征值及可选特征向量 | `SUBROUTINE DSTEQR(COMPZ, N, D, E, Z, LDZ, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 隐式 QL/QR 迭代（小问题用 `DLAEV2`） |
| `dsterf.f` | 三对角特征值 | 仅计算对称三对角矩阵的全部特征值 | `SUBROUTINE DSTERF(N, D, E, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | Pal-Walker-Kahan 变体的 QL/QR |
| `dlae2.f` | 2×2 特征值 | 计算 2×2 对称矩阵 `[A B;B C]` 的两个特征值 | `SUBROUTINE DLAE2(A, B, C, RT1, RT2)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 稳定闭式解，RT1 绝对值较大 |
| `dlaev2.f` | 2×2 特征分解 | 计算 2×2 对称矩阵的特征值及单位右特征向量 (CS1,SN1) | `SUBROUTINE DLAEV2(A, B, C, RT1, RT2, CS1, SN1)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 平面旋转对角化 2×2 对称矩阵 |
| `dopgtr.f` | 正交矩阵生成 | 生成 `DSPTRD` 返回的 n 阶正交矩阵 Q（打包存储反射器） | `SUBROUTINE DOPGTR(UPLO, N, AP, TAU, Q, LDQ, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 累积 n-1 个初等反射器 |
| `dopmtr.f` | 正交矩阵应用 | 用 `DSPTRD` 的 Q 或 Q^T 左/右乘一般矩阵 C | `SUBROUTINE DOPMTR(SIDE, UPLO, TRANS, M, N, AP, TAU, C, LDC, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 不解压缩直接应用打包反射器 |
| `dlansb.f` | 矩阵范数 | 返回实对称带状矩阵的 1-范数/Frobenius/∞-范数/最大绝对值元素 | `DOUBLE PRECISION FUNCTION DLANSB(NORM, UPLO, N, K, AB, LDAB, WORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | LAPACK 3.1 版，按 NORM 分支累加 |
| `dlansp.f` | 矩阵范数 | 返回打包存储实对称矩阵的各类范数或最大绝对值元素 | `DOUBLE PRECISION FUNCTION DLANSP(NORM, UPLO, N, AP, WORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 按 NORM 选择列和/对角线/逐元素最大值 |
| `dlanst.f` | 矩阵范数 | 返回实对称三对角矩阵的各类范数或最大绝对值元素 | `DOUBLE PRECISION FUNCTION DLANST(NORM, N, D, E)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 基于对角 D 与次对角 E 的范数计算 |

### 3.5 对称三对角特征值分治辅助（DLAED 族）

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dlaed0.f` | 分治特征值辅助 | 用分治法计算对称三对角矩阵全部特征值及对应特征向量 | `SUBROUTINE DLAED0(ICOMPQ, QSIZ, N, D, E, Q, LDQ, QSTORE, LDQS, WORK, IWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 递归分治 + 秩一修正（ICOMPQ 控制紧凑/显式） |
| `dlaed1.f` | 分治特征值辅助 | 计算对角矩阵经秩一对称修正后的更新特征系统（三对角全特征向量情形） | `SUBROUTINE DLAED1(N, D, Q, LDQ, INDXQ, RHO, CUTPNT, WORK, IWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | `T=Q(D+RHO*Z*Z')Q'`，调用 DLAED2/3/4 |
| `dlaed2.f` | 分治特征值辅助 | 合并两组特征值并排序，尝试收缩（deflation）以缩减割线方程阶数 | `SUBROUTINE DLAED2(K, N, N1, D, Q, LDQ, INDXQ, RHO, Z, DLAMDA, W, Q2, INDX, INDXC, INDXP, COLTYP, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 相近特征值或 Z 中小元素触发收缩 |
| `dlaed3.f` | 分治特征值辅助 | 求 D、W、RHO 定义的割线方程在 1..K 间的根并更新特征向量 | `SUBROUTINE DLAED3(K, N, N1, D, Q, LDQ, RHO, DLAMDA, Q2, INDX, CTOT, W, S, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 `DLAED4` 求根后做特征向量矩阵乘法 |
| `dlaed4.f` | 分治特征值辅助 | 计算秩一修正对角矩阵的第 I 个更新特征值（D 有序、RHO>0） | `SUBROUTINE DLAED4(N, I, D, Z, DELTA, RHO, DLAM, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带保护的牛顿法求割线方程根 |
| `dlaed5.f` | 分治特征值辅助 | 计算 2×2 对角矩阵秩一修正的第 I 个特征值 | `SUBROUTINE DLAED5(I, D, Z, DELTA, RHO, DLAM)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 2 阶割线方程闭式解 |
| `dlaed6.f` | 分治特征值辅助 | 求三项有理函数 `f(x)=rho+z1/(d1-x)+z2/(d2-x)+z3/(d3-x)` 最靠近原点的正/负根 | `SUBROUTINE DLAED6(KNITER, ORGATI, RHO, D, Z, FINIT, TAU, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 中值/牛顿混合迭代求根 |
| `dlaed7.f` | 分治特征值辅助 | 计算对角矩阵秩一修正后的更新特征系统（稠密对称矩阵三对角化情形） | `SUBROUTINE DLAED7(ICOMPQ, N, QSIZ, TLVLS, CURLVL, CURPBM, D, Q, LDQ, INDXQ, RHO, CUTPNT, QSTORE, QPTR, PRMPTR, PERM, GIVPTR, GIVCOL, GIVNUM, WORK, IWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 分治递归层，调用 DLAED8/9 |
| `dlaed8.f` | 分治特征值辅助 | 合并两组特征值排序并收缩（对应 DLAED7 的紧凑存储版本） | `SUBROUTINE DLAED8(ICOMPQ, K, N, QSIZ, D, Q, LDQ, INDXQ, RHO, CUTPNT, Z, DLAMDA, Q2, LDQ2, W, PERM, GIVPTR, GIVCOL, GIVNUM, INDXP, INDX, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 相近特征值 / Z 中小元素触发收缩，记录 Givens 旋转 |
| `dlaed9.f` | 分治特征值辅助 | 求割线方程在 KSTART..KSTOP 间的根并存储新特征向量矩阵 | `SUBROUTINE DLAED9(K, KSTART, KSTOP, N, D, Q, LDQ, RHO, DLAMDA, W, S, LDS, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 `DLAED4` 逐段求根 |
| `dlaeda.f` | 分治特征值辅助 | 计算分治合并过程 CURLVL 步、CURPBM 问题对应的 Z 向量 | `SUBROUTINE DLAEDA(N, TLVLS, CURLVL, CURPBM, PRMPTR, PERM, GIVPTR, GIVCOL, GIVNUM, Q, QPTR, Z, ZTEMP, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 依据排列与 Givens 旋转历史重建 Z |

### 3.6 SVD 驱动与双对角化

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dgesdd.f` | SVD 驱动 | 计算实 M×N 矩阵 SVD `A=U*SIGMA*V^T`，可选左右奇异向量（分治法） | `SUBROUTINE DGESDD(JOBZ, M, N, A, LDA, S, U, LDU, VT, LDVT, WORK, LWORK, IWORK, INFO)` | `faclib/interpolation.c`（插值/SVD 降秩；经桥接层） | `DGEBRD` 双对角化 + `DBDSDC` 分治 SVD；支持 `LWORK=-1` 工作区查询 |
| `dgebrd.f` | 双对角化 | 将一般 M×N 矩阵经正交变换化为上/下双对角形 `Q'*A*P=B`（阻塞版） | `SUBROUTINE DGEBRD(M, N, A, LDA, D, E, TAUQ, TAUP, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 `DLABRD` 的块 Householder 双对角化 |
| `dgebd2.f` | 双对角化 | 将一般 m×n 矩阵化为双对角形（非阻塞版） | `SUBROUTINE DGEBD2(M, N, A, LDA, D, E, TAUQ, TAUP, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | `DLARFG` + `DLARF` 的初等反射器双对角化 |
| `dlabrd.f` | 双对角化辅助 | 化简一般 m×n 矩阵的前 NB 行/列至双对角形，返回变换矩阵 X、Y | `SUBROUTINE DLABRD(M, N, NB, A, LDA, D, E, TAUQ, TAUP, X, LDX, Y, LDY)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | `DGEBRD` 的块核心 |
| `dbdsdc.f` | 双对角 SVD | 用分治法计算实 N×N 双对角矩阵 B 的 SVD `B=U*S*VT`，可选紧凑存储奇异向量 | `SUBROUTINE DBDSDC(UPLO, COMPQ, N, D, E, U, LDU, VT, LDVT, Q, IQ, WORK, IWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 分治 + 割线方程（仅奇异值时转 `DLASDQ`） |
| `dbdsqr.f` | 双对角 SVD | 计算实 N×N 双对角矩阵 B 的 SVD `B=Q*S*P'`，可选累积 `U*Q`、`P'*VT`、`Q'*C` | `SUBROUTINE DBDSQR(UPLO, N, NCVT, NRU, NCC, D, E, VT, LDVT, U, LDU, C, LDC, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | Demmel-Kahan / Parlett-Fernando 的高相对精度 QR 迭代 |

### 3.7 双对角 SVD 分治辅助（DLASD 族）

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dlasd0.f` | SVD 分治辅助 | 用分治法计算实上双对角 N×M 矩阵的 SVD（显式 U、VT） | `SUBROUTINE DLASD0(N, SQRE, D, E, U, LDU, VT, LDVT, SMLSIZ, IWORK, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 递归分治，`DLASD1`/`DLASDA` 分派 |
| `dlasd1.f` | SVD 分治辅助 | 计算上双对角矩阵 B（N=NL+NR+1）的 SVD，由 DLASD0 调用 | `SUBROUTINE DLASD1(NL, NR, SQRE, D, ALPHA, BETA, U, LDU, VT, LDVT, IDXQ, IWORK, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 秩一修正后调用 DLASD2/3 |
| `dlasd2.f` | SVD 分治辅助 | 合并两组奇异值排序并收缩，缩减割线方程阶数 | `SUBROUTINE DLASD2(NL, NR, SQRE, K, D, Z, ALPHA, BETA, U, LDU, VT, LDVT, DSIGMA, U2, LDU2, VT2, LDVT2, IDXP, IDX, IDXC, IDXQ, COLTYP, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 相近奇异值或 Z 中小元素触发收缩 |
| `dlasd3.f` | SVD 分治辅助 | 求割线方程全部根的平方根并更新奇异向量 | `SUBROUTINE DLASD3(NL, NR, SQRE, K, D, Q, LDQ, DSIGMA, U, LDU, U2, LDU2, VT, LDVT, VT2, LDVT2, IDXC, CTOT, Z, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 `DLASD4`，再做奇异向量矩阵更新 |
| `dlasd4.f` | SVD 分治辅助 | 计算正定对角矩阵秩一修正第 I 个更新特征值的平方根 | `SUBROUTINE DLASD4(N, I, D, Z, DELTA, RHO, SIGMA, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带保护牛顿法求割线方程根的平方根 |
| `dlasd5.f` | SVD 分治辅助 | 计算 2×2 对角矩阵（`diag(D)^2+RHO*Z*Z'`）秩一修正第 I 个特征值的平方根 | `SUBROUTINE DLASD5(I, D, Z, DELTA, RHO, DSIGMA, WORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 2 阶情形解析求根 |
| `dlasd6.f` | SVD 分治辅助 | 计算合并两个较小双对角矩阵（追加一行）后更新双对角矩阵 B 的 SVD（紧凑/分解形式） | `SUBROUTINE DLASD6(ICOMPQ, NL, NR, SQRE, D, VF, VL, ALPHA, BETA, IDXQ, PERM, GIVPTR, GIVCOL, LDGCOL, GIVNUM, LDGNUM, POLES, DIFL, DIFR, Z, K, C, S, WORK, IWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 DLASD7/8 的紧凑分治合并 |
| `dlasd7.f` | SVD 分治辅助 | 合并两组奇异值排序并收缩（对应 DLASD6，紧凑奇异向量） | `SUBROUTINE DLASD7(ICOMPQ, NL, NR, SQRE, K, D, Z, ZW, VF, VFW, VL, VLW, ALPHA, BETA, DSIGMA, IDX, IDXP, IDXQ, PERM, GIVPTR, GIVCOL, LDGCOL, GIVNUM, LDGNUM, C, S, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 相近奇异值 / Z 中小元素触发收缩 |
| `dlasd8.f` | SVD 分治辅助 | 求割线方程根的平方根，记录每个 D 到最近两极点的距离并更新奇异向量 | `SUBROUTINE DLASD8(ICOMPQ, K, D, Z, VF, VL, DIFL, DIFR, LDDIFR, DSIGMA, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 `DLASD4`，计算 DIFL/DIFR |
| `dlasda.f` | SVD 分治辅助 | 用分治法计算上双对角 N×M 矩阵的 SVD，U/VT 以紧凑形式给出 | `SUBROUTINE DLASDA(ICOMPQ, SMLSIZ, N, SQRE, D, E, U, LDU, VT, K, DIFL, DIFR, Z, POLES, GIVPTR, GIVCOL, LDGCOL, PERM, GIVNUM, C, S, WORK, IWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 递归调用 DLASD6 的紧凑分治 |
| `dlasdq.f` | SVD 分治辅助 | 计算（上/下）双对角矩阵的 SVD，可选累积变换（仅奇异值路径常用） | `SUBROUTINE DLASDQ(UPLO, SQRE, N, NCVT, NRU, NCC, D, E, VT, LDVT, U, LDU, C, LDC, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 子问题用 QR 或分治，按尺寸分派 |
| `dlasdt.f` | SVD 分治辅助 | 为双对角分治创建子问题树（subproblem tree） | `SUBROUTINE DLASDT(N, LVL, ND, INODE, NDIML, NDIMR, MSUB)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 递归二分构造问题层级 |

### 3.8 dqds 奇异值辅助（DLASQ 族）

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dlasq1.f` | dqds 奇异值 | 用微分 qd 算法计算实 N×N 双对角矩阵的奇异值（高相对精度） | `SUBROUTINE DLASQ1(N, D, E, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | D 与 E 平方构造 qd 数组后调用 `DLASQ2` |
| `dlasq2.f` | dqds 奇异值 | 计算 qd 数组 Z 对应对称正定三对角矩阵的全部特征值（高相对精度） | `SUBROUTINE DLASQ2(N, Z, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | dqds 迭代 + 收缩、翻转（flip）策略 |
| `dlasq3.f` | dqds 辅助 | 检查收缩、计算位移 TAU 并调用 dqds，失败时更换位移重试 | `SUBROUTINE DLASQ3(I0, N0, Z, PP, DMIN, SIGMA, DESIG, QMAX, NFAIL, ITER, NDIV, IEEE)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 位移策略 + `DLASQ5`/`DLASQ6` 变换 |
| `dlasq4.f` | dqds 辅助 | 用前次变换的 d 值近似最小特征值作为位移 TAU | `SUBROUTINE DLASQ4(I0, N0, Z, PP, N0IN, DMIN, DMIN1, DMIN2, DN, DN1, DN2, TAU, TTYPE)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 牛顿式位移估计与类型判别 |
| `dlasq5.f` | dqds 辅助 | 执行一次 ping-pong 形式的 dqds 变换（IEEE/非 IEEE 两版本） | `SUBROUTINE DLASQ5(I0, N0, Z, PP, TAU, DMIN, DMIN1, DMIN2, DN, DNM1, DNM2, IEEE)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 带位移的微分 qd 变换 |
| `dlasq6.f` | dqds 辅助 | 执行一次 ping-pong 形式的 dqd 变换（位移为零），防止上/下溢 | `SUBROUTINE DLASQ6(I0, N0, Z, PP, DMIN, DMIN1, DMIN2, DN, DNM1, DNM2)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 零位移 qd 变换，含溢出保护 |

### 3.9 QR / LQ 分解与正交矩阵生成、应用

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dgeqr2.f` | QR 分解 | 计算实 m×n 矩阵 QR 分解 `A=Q*R`（非阻塞版） | `SUBROUTINE DGEQR2(M, N, A, LDA, TAU, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | Householder 反射器（Level 2 BLAS） |
| `dgeqrf.f` | QR 分解 | 计算实 M×N 矩阵 QR 分解 `A=Q*R`（阻塞版） | `SUBROUTINE DGEQRF(M, N, A, LDA, TAU, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块反射器（Level 3 BLAS），`LWORK=-1` 查询 |
| `dgelq2.f` | LQ 分解 | 计算实 m×n 矩阵 LQ 分解 `A=L*Q`（非阻塞版） | `SUBROUTINE DGELQ2(M, N, A, LDA, TAU, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | Householder 反射器 |
| `dgelqf.f` | LQ 分解 | 计算实 M×N 矩阵 LQ 分解 `A=L*Q`（阻塞版） | `SUBROUTINE DGELQF(M, N, A, LDA, TAU, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块反射器（Level 3 BLAS） |
| `dlarfg.f` | 反射器生成 | 生成 n 阶实初等反射器 H，使 `H*[alpha;x]=[beta;0]` | `SUBROUTINE DLARFG(N, ALPHA, X, INCX, TAU)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 稳定构造 Householder 向量与 TAU |
| `dlarf.f` | 反射器应用 | 将单个实初等反射器 H 从左/右作用于矩阵 C | `SUBROUTINE DLARF(SIDE, M, N, V, INCV, TAU, C, LDC, WORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | `H=I-tau*v*v'`，按 SIDE 分支 |
| `dlarft.f` | 块反射器 | 构造由 k 个初等反射器乘积定义的块反射器 H 的三角因子 T | `SUBROUTINE DLARFT(DIRECT, STOREV, N, K, V, LDV, TAU, T, LDT)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | DIRECT/STOREV 决定 T 上/下三角与递推顺序 |
| `dlarfb.f` | 块反射器应用 | 将实块反射器 H 或 H' 从左/右作用于矩阵 C | `SUBROUTINE DLARFB(SIDE, TRANS, DIRECT, STOREV, M, N, K, V, LDV, T, LDT, C, LDC, WORK, LDWORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块 Householder 应用（Level 3 BLAS） |
| `dlarfx.f` | 反射器应用 | 将实初等反射器 H 作用于矩阵 C（对 V 无 INCV 的变体） | `SUBROUTINE DLARFX(SIDE, M, N, V, TAU, C, LDC, WORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | `DLARF` 的简化变体 |
| `dorg2r.f` | 正交矩阵生成 | 生成 QR 分解返回的 m×n 正交矩阵 Q（前 n 列，非阻塞版） | `SUBROUTINE DORG2R(M, N, K, A, LDA, TAU, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 累积 k 个反射器 |
| `dorgqr.f` | 正交矩阵生成 | 生成 QR 分解返回的 m×n 正交矩阵 Q（阻塞版） | `SUBROUTINE DORGQR(M, N, K, A, LDA, TAU, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块反射器累积 |
| `dorgl2.f` | 正交矩阵生成 | 生成 LQ 分解返回的正交矩阵 Q（前 m 行，非阻塞版） | `SUBROUTINE DORGL2(M, N, K, A, LDA, TAU, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 累积反射器（按行） |
| `dorglq.f` | 正交矩阵生成 | 生成 LQ 分解返回的正交矩阵 Q（阻塞版） | `SUBROUTINE DORGLQ(M, N, K, A, LDA, TAU, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块反射器累积（按行） |
| `dorg2l.f` | 正交矩阵生成 | 生成 `DGEQLF` 返回的 m×n 正交矩阵 Q（后 n 列，非阻塞版） | `SUBROUTINE DORG2L(M, N, K, A, LDA, TAU, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 累积反射器（后列） |
| `dorgbr.f` | 正交矩阵生成 | 生成 `DGEBRD` 双对角化决定的正交矩阵 Q 或 P^T | `SUBROUTINE DORGBR(VECT, M, N, K, A, LDA, TAU, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | VECT='Q'/'P' 分别生成 |
| `dorghr.f` | 正交矩阵生成 | 生成 `DGEHRD` 返回的 n 阶正交矩阵 Q（H(ILO..IHI-1) 之积） | `SUBROUTINE DORGHR(N, ILO, IHI, A, LDA, TAU, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 累积 Hessenberg 化简反射器 |
| `dorm2r.f` | 正交矩阵应用 | 用 `DGEQRF` 的 Q/Q^T 左/右乘矩阵 C（非阻塞版） | `SUBROUTINE DORM2R(SIDE, TRANS, M, N, K, A, LDA, TAU, C, LDC, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 逐个应用反射器，不显式生成 Q |
| `dormqr.f` | 正交矩阵应用 | 用 `DGEQRF` 的 Q/Q^T 左/右乘矩阵 C（阻塞版） | `SUBROUTINE DORMQR(SIDE, TRANS, M, N, K, A, LDA, TAU, C, LDC, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块反射器应用 |
| `dorml2.f` | 正交矩阵应用 | 用 `DGELQF` 的 Q/Q^T 左/右乘矩阵 C（非阻塞版） | `SUBROUTINE DORML2(SIDE, TRANS, M, N, K, A, LDA, TAU, C, LDC, WORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 逐个应用 LQ 反射器 |
| `dormlq.f` | 正交矩阵应用 | 用 `DGELQF` 的 Q/Q^T 左/右乘矩阵 C（阻塞版） | `SUBROUTINE DORMLQ(SIDE, TRANS, M, N, K, A, LDA, TAU, C, LDC, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 块反射器应用 |
| `dormbr.f` | 正交矩阵应用 | 用 `DGEBRD` 的 Q/P^T 左/右乘矩阵 C | `SUBROUTINE DORMBR(VECT, SIDE, TRANS, M, N, K, A, LDA, TAU, C, LDC, WORK, LWORK, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | VECT/SIDE/TRANS 组合决定乘法形式 |

### 3.10 平面旋转与向量工具

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dlartg.f` | 平面旋转 | 生成平面旋转使 `[CS SN;-SN CS]*[F;G]=[R;0]`（`CS^2+SN^2=1`） | `SUBROUTINE DLARTG(F, G, CS, SN, R)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 比 `DROTG` 更稳健准确，F/G 不变 |
| `dlartv.f` | 平面旋转应用 | 对向量 x、y 的对应元素施加一组实平面旋转 | `SUBROUTINE DLARTV(N, X, INCX, Y, INCY, C, S, INCC)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 逐元素 `(x,y)<-R(c,s)(x,y)` |
| `dlar2v.f` | 平面旋转应用 | 从两侧对一列 2×2 实对称矩阵（由 x,y,z 定义）施加一组平面旋转 | `SUBROUTINE DLAR2V(N, X, Y, Z, INCX, C, S, INCC)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | `R*[[x,z],[z,y]]*R'`，对称三角化用 |
| `dlargv.f` | 平面旋转生成 | 由实向量 x、y 生成一组平面旋转使 `[c s;-s c][x;y]=[a;0]` | `SUBROUTINE DLARGV(N, X, INCX, Y, INCY, C, INCC)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 调用 `DLARTG` 逐元素生成 |
| `dlasr.f` | 平面旋转应用 | 对矩阵 A 应用一串平面旋转（左右、前推/后推、顶/底 pivot） | `SUBROUTINE DLASR(SIDE, PIVOT, DIRECT, M, N, C, S, A, LDA)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | SIDE/PIVOT/DIRECT 控制旋转施加方式 |
| `dladiv.f` | 复数工具 | 用实数运算实现复数除法 `(a+ib)/(c+id)=p+iq` | `SUBROUTINE DLADIV(A, B, C, D, P, Q)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | Robert L. Smith 算法（Knuth Vol.2 p.195） |

### 3.11 通用工具、范数与机器环境常数

| 文件名 | 函数族/类别 | 功能（中文） | 关键入口签名 | FAC 调用者 | 算法要点 |
|---|---|---|---|---|---|
| `dlamch.f` | 机器常数 | 返回双精度机器参数（eps、sfmin、base、溢出/下溢阈值等，由 CMACH 指定） | `DOUBLE PRECISION FUNCTION DLAMCH(CMACH)` | 通用 LAPACK 例程，未发现 FAC 直接调用（`Makefile.in` 中以 `FFLAGSNO` 单独编译） | CMACH 字符选择，平台相关常量表 |
| `dlabad.f` | 机器常数 | 调整 `DLAMCH` 得到的上/下溢阈值（指数范围很大时取平方根） | `SUBROUTINE DLABAD(SMALL, LARGE)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | `LOG10(LARGE)` 足够大时对 SMALL/LARGE 开平方 |
| `ilaenv.f` | 环境参数 | 供 LAPACK 例程按环境/问题规模 ISPEC、NAME、OPTS、N1..N4 选择调优参数 | `INTEGER FUNCTION ILAENV(ISPEC, NAME, OPTS, N1, N2, N3, N4)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 按 ISPEC 返回块大小/阈值等（不可全转小写） |
| `ieeeck.f` | 环境探测 | 被 `ILAENV` 调用，验证 Infinity 及（可选）NaN 算术是否安全（不触发 trap） | `INTEGER FUNCTION IEEECK(ISPEC, ZERO, ONE)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | ISPEC=0 测无穷、=1 测无穷与 NaN |
| `dlapy2.f` | 数值工具 | 返回 `sqrt(x^2+y^2)`，避免不必要上溢 | `DOUBLE PRECISION FUNCTION DLAPY2(X, Y)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 先归一化再缩放求平方和 |
| `dlas2.f` | 2×2 奇异值 | 计算 2×2 上三角矩阵 `[F G;0 H]` 的奇异值（SSMIN/SSMAX） | `SUBROUTINE DLAS2(F, G, H, SSMIN, SSMAX)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 稳定闭式解，避免上/下溢 |
| `dlasv2.f` | 2×2 SVD | 计算 2×2 三角矩阵的 SVD，返回奇异值与左右奇异向量 (CSL,SNL)/(CSR,SNR) | `SUBROUTINE DLASV2(F, G, H, SSMIN, SSMAX, SNR, CSR, SNL, CSL)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 平面旋转双向对角化 2×2 |
| `dlascl.f` | 矩阵工具 | 将 M×N 矩阵 A 乘以标量 CTO/CFROM，避免中途中上/下溢（支持 full/三角/Hessenberg/带状） | `SUBROUTINE DLASCL(TYPE, KL, KU, CFROM, CTO, M, N, A, LDA, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | TYPE 指定矩阵结构，分块缩放 |
| `dlaset.f` | 矩阵工具 | 将 m×n 矩阵 A 的对角置 BETA、非对角置 ALPHA | `SUBROUTINE DLASET(UPLO, M, N, ALPHA, BETA, A, LDA)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 按 UPLO 选择性填充 |
| `dlacpy.f` | 矩阵工具 | 将二维矩阵 A 的全部或部分复制到矩阵 B | `SUBROUTINE DLACPY(UPLO, M, N, A, LDA, B, LDB)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | UPLO 指定复制上/下三角或全部 |
| `dlassq.f` | 数值工具 | 返回 SCALE、SUMSQ 使 `SCALE^2*SUMSQ = Σx(i)^2 + 原SCALE^2*原SUMSQ`（防溢出平方和） | `SUBROUTINE DLASSQ(N, X, INCX, SCALE, SUMSQ)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 逐元素缩放累加，用于范数计算 |
| `dlamrg.f` | 排序工具 | 生成排列 INDEX，把两个已独立排序的集合 A 合并为一个升序集合 | `SUBROUTINE DLAMRG(N1, N2, A, DTRD1, DTRD2, INDEX)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 双指针归并（DTRD1/DTRD2 为升降序标志） |
| `dlasrt.f` | 排序工具 | 对数组 D 按升序（ID='I'）或降序（ID='D'）排序 | `SUBROUTINE DLASRT(ID, N, D, INFO)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 快速排序，规模≤20 回退插入排序 |
| `dlange.f` | 矩阵范数 | 返回实矩阵 A 的 1-范数/Frobenius/∞-范数/最大绝对值元素 | `DOUBLE PRECISION FUNCTION DLANGE(NORM, M, N, A, LDA, WORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 按 NORM 分支的列和/行和/平方和 |
| `dlanhs.f` | 矩阵范数 | 返回 Hessenberg 矩阵 A 的各类范数或最大绝对值元素 | `DOUBLE PRECISION FUNCTION DLANHS(NORM, N, A, LDA, WORK)` | 通用 LAPACK 例程，未发现 FAC 直接调用 | 利用 Hessenberg 结构优化列/行和 |

## 4. 接口与调用约定

- **Fortran 77 风格**：所有源码均为固定格式 F77，接口为 `SUBROUTINE` / `FUNCTION`（如 `DOUBLE PRECISION FUNCTION DLAMCH(CMACH)`）。标量多按**引用**传递，字符串为 `CHARACTER*1`/`CHARACTER*(*)`；行主序二维数组以 `LDA` 等 leading dimension 描述。
- **C 核心桥接**：FAC C 核心通过两条桥接路径调用这些例程：
  1. **cfortran 风格**：`faclib/cf77.h` 中的 `PROTOCCALLSFSUBn` / `CCALLSFSUBn` 宏（如 `DGESV`、`DGEEV`、`DGESDD`、`DGBSV`、`DSPEV`、`DSBEV`、`DSPEVD`）。
  2. **ISO C Binding（f2c）风格**：`faclib/f2c.h` 声明 `f_dgeev`、`f_dgesv`、`f_dgesdd`、`f_dgbsv`、`f_dsbev`、`f_dspevd`、`f_dspev` 等；`faclib/f2c.f90` 中以 `bind(C, name='f_xxx')` 定义的包装子程序把 C 的 `value` 标量/`*` 数组映射到 F77 调用。
  - 根 `README.md` 说明若 F77 编译器非 g77/sun f77，需通过 `--with-cfortran=xxFortran` 指定（详见 `faclib/cfortran.doc`）。
- **Workspace 查询模式**：阻塞型驱动例程（`DGEQRF`、`DGEBRD`、`DGEHRD`、`DGESDD`、`DSTEDC`、`DSPEVD`、`DHSEQR` 等）带 `WORK`/`LWORK`（部分还有 `IWORK`/`LIWORK`）参数；将 `LWORK=-1` 传入可在 `WORK(1)`（及 `IWORK(1)`）中获得最优工作区大小，随后按该大小分配再调用。例如 `dgesdd.f` 中 `LQUERY = (LWORK.EQ.-1)`，且 `WORK(1)` 在 `INFO=0` 时返回最优 `LWORK`。
- **INFO 约定**：`INFO=0` 成功；`<0` 表示第 `-INFO` 个参数非法；`>0` 通常表示分解中检测到奇异/零主元或算法未收敛。
- **精度与版本**：全部为双精度（`d` 前缀），源码头部标注 LAPACK version 3.0 或 3.1，保留原始机构版权声明。

## 5. 与上下游目录关系、构建方式

- **上游依赖**：本目录的例程在 BLAS 层之上运行（矩阵乘/向量运算依赖 `blas/` 的 `ddot`、`dscal`、`dgemv`、`dgemm`、`drot` 等；`faclib/f2c.h` 中亦声明这些 BLAS 包装）。本目录产生静态库 `libmlapack.a`，与 `libblas.a` 等一同被链接进最终 `libfac.a`。
- **下游消费者**：`faclib/` 核心数值库通过 `cf77.h`/`f2c.h` 直接调用 `DGESV`、`DGBSV`、`DGEEV`、`DGESDD`、`DSPEV`、`DSBEV`、`DSPEVD`，用于原子结构能级求解（`structure.c`）、轨道方程带状求解（`orbital.c`）、矩阵操作（`rmatrix.c`）、组态相互作用递归矩阵（`crm.c`）、极化率（`polarization.c`）、插值（`interpolation.c`）等。`coul/`、`modqed/`、`mpfun/` 中未发现直接调用。
- **构建方式**：本目录的 `Makefile.in` 由顶层 `configure`（`configure.ac`）生成 `Makefile`。变量 `FC=@F77@`、`FFLAGS`、`FFLAGSNO`、`TOPDIR` 由 configure 注入。目标 `lapack` 把 `SRC`（111 个 `.f`）编译为 `.o`，再以 `FFLAGSNO` 单独编译 `dlamch.f`（避免激进优化破坏机器常数判断），最后 `ar r ${TOPDIR}/libmlapack.a` 归档。顶层 `Makefile.in` 的 `lib` 目标中 `cd lapack; make` 在 `cd blas; make` 之后执行；`clean` 目标亦含 `cd lapack; make clean`。

## 6. 导航

## 7. README 维护记录（自底向上）

- **定位与职责**：LAPACK 双精度子集，在 BLAS 之上提供矩阵分解与求解，产物为 `libmlapack.a`。
- **底层依据**：`dgesv.f`、`dgbsv.f`、`dgetrf.f`、`dgeev.f`、`dtrevc.f`；被 `faclib/structure.c`、`orbital.c`、`rmatrix.c` 等调用。
- **输入/输出**：矩阵与右端项；输出解、特征值与分解因子。
- **验证与回归**：无独立基准；通过原子结构对角化与 `demo` 回归间接验证。
- **已知限制**：第三方代码，不能按 GPL 分发；`dlamch.f` 使用 `FFLAGSNO` 单独编译。
- **公式核查**：源码未找到独立于 Fortran 实现的数学公式原文，算法依据需按 LAPACK 文档人工核查。
- **导航**：父级 [`../README.md`](../README.md)；底层 [`../blas/README.md`](../blas/README.md)。

[返回上级](../README.md)