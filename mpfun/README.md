# mpfun/ —— 四倍精度算术与缔合 Legendre 函数库

## 1. 定位

本目录是 FAC 的数值工具目录，包含两部分内容：

1. **自实现的四倍精度（quad-precision）算术**：根 `README.md` 的第三方目录说明（即 `UtilList` 条目）原文为：

   > `+ mpfun/,      it used to be the multi-precision floating point arithmetic`
   > `package by Beiley. Since v0.8.6, it was replaced by my own implementation of`
   > `quad-precision arithmetics. The associated Legendre functions are also put into`
   > `this directory.`

   即 Bailey MPFUN 多精度包自 v0.8.6 起已被 M. F. Gu 自实现的四倍精度算术取代；`mpfun.f` 文件头注明其算法来自 Linnainmaa（ACM TOMS Vol.7, pp.272）的伪代码。四倍精度数以**两个双精度数对** $(hi,lo)$ 表示，提供 `*、/、+、-` 及赋值、绝对值、双精度→四倍精度转换。

2. **缔合 Legendre 函数（SLATEC 扩展指数范围双精度版）**：`dx*.f` 系列来自 SLATEC/NBS（Smith, Lozier, Lozier & Smith），计算 $P_l^m$、$Q_l^m$ 及归一化 Legendre 多项式，使用 $(X,IX)=X\cdot{\rm RADIX}^{IX}$ 的扩展指数范围表示避免上溢/下溢。

## 2. 数值效应与用途

本目录实现的不是某个具体物理效应，而是支撑 FAC 高精度径向积分与角动量耦合的两类数值设施：

- **高精度径向积分**：`mpfun.f` 的 `MPADD/MPMUL/MPDIV/MPSUB/EXACTMUL` 等被 `coul/f11.f` 用于库仑函数（Coulomb functions）的连分式迭代（复数四倍精度运算：`MPADD`、`MPMUL`、`MPDIV`、`MPSUB`、`MPABS`、`MPEQ`），保证径向积分在高 $Z$、大能量范围下的数值稳定性。
- **缔合 Legendre 函数与多极场**：$P_l^m(x)$ 是球谐函数 $Y_{lm}$ 的核心因子，在角动量耦合、多极场展开以及复合/极化的角分布计算中必需。`DXLEGF` 直接被 FAC 主库调用：`faclib/recombination.c`（RR/PI 角分布，约 3987、3991 行，取 `ID=3` 正阶 $P$）、`faclib/polarization.c`（约 104 行）、`python/fac.c`（约 6688 行）、`python/util.c`（`PDXLEGF` 封装，导出到 Python）。

**缔合 Legendre 方程**（$x=\cos\theta$）：

$$
(1-x^2)y''-2xy'+\left[l(l+1)-\frac{m^2}{1-x^2}\right]y=0 .
$$

**源码所用递推关系**（以 $x=\cos\theta,\ SX=1/\sqrt{1-x^2}=1/\sin\theta$、扩展范围数对 $(PQA,IPQA)$ 表示；注意 $SX$ 是 $\sin\theta$ 的**倒数**）：

- 固定 $\nu$ 对阶数 $\mu$ 的向后递推（`dxpmu.f:55–60`）：源码写法等价于
  $P_{\nu}^{-(\mu-1)} = 2\mu\,x\,SX\,P_{\nu}^{-\mu} - (\nu-\mu)(\nu+\mu+1)\,P_{\nu}^{-(\mu+1)}$，
  即把负阶序列向低阶递推；其中 $SX=1/\sqrt{1-x^2}$（`dxlegf.f:165`）。
- 固定 $\mu$ 对 $\nu$ 的向前递推（`dxpqnu.f`、`dxqnu.f`）：由幂级数初值（含 `DXPSI` 的 $\psi$ 函数）出发，用
  $(\nu+1-\mu)P_{\nu+1}^{\mu}=(2\nu+1)x P_{\nu}^{\mu}-(\nu+\mu)P_{\nu-1}^{\mu}$ 型关系；注释明确 "forward nu-wise recurrence is stable for P for all mu and for Q for mu=0,1"。
- 负阶转正阶的归一化变换（`dxpmup.f`、`dxpnrm.f`）：$P_\nu^{-\mu}=(-1)^\mu\dfrac{(\nu-\mu)!}{(\nu+\mu)!}P_\nu^{\mu}$ 型变换，归一化多项式用 $\sqrt{(2\nu+1)(\nu-\mu)!/(\nu+\mu)!}$ 型因子（源码以 `PROD`、`DMU` 累乘实现）。
- 扩展范围算术（`dxset.f`）：$(X,IX)*(Y,IY)=(X*Y,IX+IY)$、$(X,IX)/(Y,IY)=(X/Y,IX-IY)$；加减法由 `DXADD` 完成并将结果调整为 $RADIX^{-L}\le|X|<RADIX^{L}$（`DXADJ`）。

## 3. 逐文件说明（全部 22 个 .f）

### 四倍精度核心（1 个）

1. **`mpfun.f`** —— 双精度数对表示的四倍精度算术，算法出自 Linnainmaa, ACM TOMS 7, pp.272（`NBITS=53`、$CONST=2^{27}$ 拆分尾数实现精确乘积 `EXACTMUL`）。入口：`SUBROUTINE EXACTMUL(A,C,R)`、`MPMUL(A,C,R)`、`MPDIV(A,C,R)`、`MPADD(A,C,R)`、`MPSUB(A,C,R)`、`MPEQ(S,D)`、`MPDMC(H,L,R)`、`MPABS(A,R)`；参数均为 `DOUBLE PRECISION`，四倍数用长度 2 数组 `(hi,lo)`。调用方：`coul/f11.f`（连续分式迭代求库仑函数虚实部）、其他 `coul/` 例程。

### 扩展范围算术与 Legendre 函数（13 个）

2. **`dxset.f`** —— SLATEC `DXSET(IRAD,NRADPL,DZERO,NBITS,IERROR)`：扩展范围算术的**初始化例程**，须在任何其他 `DX*` 例程前调用；计算并存机器相关常数到 `DXBLK2/DXBLK1`，参数为 0 时用 `I1MACH` 推断。`DXLEGF` 内部以 `CALL DXSET(0,0,0.0D0,0,IERROR)` 自动初始化。

3. **`dxadd.f`** —— `DXADD(X,IX,Y,IY,Z,IZ,IERROR)`：扩展范围加法 `(Z,IZ)=(X,IX)+(Y,IY)`，结果调整为 adjusted form；输入不需调整但需满足 $RADIX^{-2L}\le|X|\le RADIX^{2L}$；调用 `DXADJ`。

4. **`dxadj.f`** —— `DXADJ(X,IX,IERROR)`：将 $(X,IX)$ 变换使 $RADIX^{-L}\le|X|<RADIX^{L}$；调用 `XERMSG`；读写 `DXBLK2`（`!$OMP THREADPRIVATE`）。

5. **`dxred.f`** —— `DXRED(X,IX,IERROR)`：若 $(X,IX)$ 在 $RADIX^{-2L}$–$RADIX^{2L}$ 范围内则约化使 `IX=0`，便于回到普通双精度计算；超出范围不动作。

6. **`dxlegf.f`** —— 主入口 `SUBROUTINE DXLEGF(DNU1,NUDIFF,MU1,MU2,THETA,ID,PQA,IPQA,IERROR)`。`X=COS(THETA)`；`ID=1` 负阶第一类 $P$、`ID=2` 第二类 $Q$、`ID=3` 正阶 $P$、`ID=4` 归一化多项式 $PN$；按 `NUDIFF=0` 或 `MU1=MU2` 决定沿 $\mu$ 还是 $\nu$ 生成序列（长度 `MU2-MU1+1` 或 `NUDIFF+1`）。内部依次调用 `DXSET`、`DXPMU`、`DXQMU`、`DXQNU`、`DXPQNU`、`DXPMUP`、`DXPNRM`、`DXRED`、`XERMSG`。调用方：`faclib/recombination.c`、`faclib/polarization.c`、`python/fac.c`、`python/util.c`。

7. **`dxpmu.f`** —— `DXPMU(NU1,NU2,MU1,MU2,THETA,X,SX,ID,PQA,IPQA,IERROR)`：`DXLEGF` 的辅助例程，固定 $\nu$ 对 $\mu$ **向后递推**生成 $P(-\mu_2,\nu,x)\dots P(-\mu_1,\nu,x)$；先两次调用 `DXPQNU` 取初值，再用 `DXADD`/`DXADJ` 递推。

8. **`dxpmup.f`** —— `DXPMUP(NU1,NU2,MU1,MU2,PQA,IPQA,IERROR)`：把 `PQA` 中负阶第一类 Legendre 函数原地变换为正阶 $P(\mu,\nu,x)$，用阶乘比 `PROD` 累乘（含 $PQA(J)=0$ 的 $\mu>\nu$ 情形）；调用 `DXADJ`。

9. **`dxpnrm.f`** —— `DXPNRM(NU1,NU2,MU1,MU2,PQA,IPQA,IERROR)`：把负阶 $P$ 数组原地变换为归一化 Legendre 多项式 `PN`；$\mu>\nu$ 时置零；调用 `DXADJ`。

10. **`dxpqnu.f`** —— `DXPQNU(NU1,NU2,MU,THETA,ID,PQA,IPQA,IERROR)`：辅助例程，用幂级数计算 $P(-\mu,\nu,x)$、$Q(0,\nu,x)$、$Q(1,\nu,x)$ 的初值再作沿 $\nu$ 的**向前递推**（对 $P$ 所有 $\mu$ 与 $Q$ 的 $\mu=0,1$ 稳定）；调用 `DXADD`、`DXADJ`、`DXPSI`，用 `DXBLK1` 中 `NBITSF` 决定展开项数 $J0$。

11. **`dxpsi.f`** —— `DOUBLE PRECISION FUNCTION DXPSI(A,IPSIK,IPSIX)`：Psi（digamma）函数值，用前 12 个 Bernoulli 数（`CNUM/CDENOM`）的渐近级数，大参数时 `DXPSI=LOG(B)-(C+.5D0/B)`；`DXPQNU` 调用。

12. **`dxqmu.f`** —— `DXQMU(NU1,NU2,MU1,MU2,THETA,X,SX,ID,PQA,IPQA,IERROR)`：固定 $\nu$ 对 $\mu$ **向前递推**生成 $Q(\mu_1,\nu,x)\dots Q(\mu_2,\nu,x)$；先由 `DXPQNU` 取 $Q(0,\nu_1,x)$、$Q(1,\nu_1,x)$，再用 `DXADD`/`DXADJ`。

13. **`dxqnu.f`** —— `DXQNU(NU1,NU2,MU1,THETA,X,SX,ID,PQA,IPQA,IERROR)`：固定 $\mu$ 对 $\nu$ **向后递推**生成 $Q(\mu,\nu_1,x)\dots Q(\mu,\nu_2,x)$；$\mu_1=1$ 时特殊处理；调用 `DXPQNU`、`DXADD`、`DXADJ`。

14. **`i1mach.f`** —— `INTEGER FUNCTION I1MACH(I)`：SLATEC 机器相关整数常数（$I=1\dots16$：标准输入/输出/错误单元、每字位数、整数基数、最大整数、浮点尾数位数/基数/指数范围等），`DXSET` 用它自动推断 `IRAD/NRADPL/DZERO/NBITS`。

### SLATEC XERROR 错误处理（8 个）

15. **`xermsg.f`** —— `XERMSG(LIBRAR,SUBROU,MESSG,NERR,LEVEL)`：XERROR 包主入口，按 `LEVEL` 与全局控制标志 `KONTRL` 处理诊断消息；`DXADJ`、`DXSET`、`DXLEGF` 等以 `CALL XERMSG('SLATEC','DXSET',...,201,1)` 形式报错。

16. **`xercnt.f`** —— `XERCNT(LIBRAR,SUBROU,MESSG,NERR,LEVEL,KONTRL)`：允许用户逐条覆盖错误处理控制值（$-2\le KONTRL\le2$），仅对当前消息生效。

17. **`xerhlt.f`** —— `XERHLT(MESSG)`：机器相关例程，打印 `MESSG` 并中止程序执行（`XERMSG` 在 LEVEL 要求时调用）。

18. **`xerprn.f`** —— `XERPRN(PREFIX,NPREF,MESSG,NWRAP)`：把 `XERMSG` 处理的消息按最多 16 字符前缀 `PREFIX` 与换行宽度 `NWRAP` 送到最多 5 个逻辑单元。

19. **`xersve.f`** —— `XERSVE(LIBRAR,SUBROU,MESSG,KFLAG,NERR,LEVEL,ICOUNT)`：记录错误发生（供 `XERCNT` 拦截与重复计数），`J4SAVE` 保存全局状态。

20. **`xgetua.f`** —— `XGETUA(IUNITA,N)`：返回错误消息当前发送到的逻辑单元号数组（1 到 5 个，0 表示默认单元，由 `I1MACH` 定义）。

21. **`j4save.f`** —— `FUNCTION J4SAVE(IWHICH,IVALUE,ISET)`：保存/读取错误处理例程所需全局变量（当前错误号、控制标志、输出单元、最大打印次数等），`IWHICH` 为索引。

22. **`fdump.f`** —— `SUBROUTINE FDUMP`：机器相关的符号转储桩例程（应本地实现为打印子程序嵌套表），由 XERROR 在致命错误时调用，需向 `XGETUA` 给出的最多 5 个文件输出。

## 4. 接口、上下游、构建、导航

- **Fortran→C 接口**：`DXLEGF` 通过 cfortran/f2c 约定从 C 直接调用（如 `faclib/recombination.c:3987`：
  `DXLEGF(nu1, nudiff, mu1, mu1, theta, 3, pqa, ipqa, &ierr);`）；`python/util.c:149` 的 `PDXLEGF` 把它包装为 Python 的 `fac.DXLEGF`（`python/util.c:219` 注册表 `{"DXLEGF", PDXLEGF, METH_VARARGS}`）。四倍精度 `MP*` 例程主要供 `coul/` 内部 Fortran 调用。
- **上游（调用方）**：`faclib/recombination.c`、`faclib/polarization.c`、`python/fac.c`、`python/util.c`（Legendre）；`coul/f11.f` 等（四倍精度）；`dx*.f` 内部互相调用（`DXLEGF`→`DXPMU/DXQMU/DXQNU/DXPQNU/DXPMUP/DXPNRM/DXRED`，`DXPQNU`→`DXPSI` 等）；所有错误处理经 `XERMSG`→`XERCNT/XERSVE/XERPRN/XERHLT/XGETUA/J4SAVE/FDUMP`。
- **初始化约定**：使用 `DX*` 扩展范围例程前必须调用 `DXSET`（`DXLEGF` 已内置无菌初始化），否则 `DXBLK1/DXBLK2` 未定义；这些公共块在 FAC 中标注 `!$OMP THREADPRIVATE`，支持 OpenMP。
- **构建**：`Makefile.in` 中
  `SRC = mpfun.f dxadd.f dxadj.f dxlegf.f dxpmu.f dxpmup.f dxpnrm.f dxpqnu.f dxpsi.f dxqmu.f dxqnu.f dxred.f dxset.f fdump.f i1mach.f j4save.f xercnt.f xerhlt.f xermsg.f xerprn.f xersve.f xgetua.f`，
  `FC=@F77@`，`mpfun:` 目标用 `ar r ${TOPDIR}/libfac.a ${OBJS}` 归档，`make clean` 清理目标文件。
- **第三方属性**：随 `fac_util.tar.gz` 分发（见根 `README.md` 与 `UtilList` 中的 `mpfun` 条目）；SLATEC 例程带原始 `*DECK` / `C***PROLOGUE` 头。

## 5. README 维护记录（自底向上）

- **定位与职责**：`mpfun/` 提供高精度算术与 Legendre/特殊函数例程，支撑重组、偏振等计算。
- **底层依据**：`mpfun.f`、`dxlegf.f`、`dxpmu.f`、`dxpqnu.f`、`dxpmup.f`、`dxset.f`。
- **输入/输出**：输入阶数、自变量与精度控制；输出 Legendre 函数、归一化因子与高精度算术结果。
- **验证与回归**：通过调用方（`recombination.c`、`polarization.c`、Python 扩展）间接验证；使用 `DX*` 扩展例程前需正确初始化。
- **已知限制**：随 `fac_util.tar.gz` 分发；公共块使用 OpenMP threadprivate；旧 SLATEC 头保留原始版权声明。
- **公式核查**：\underline{$(1-x^2)y''-2xy'+\left[l(l+1)-\frac{m^2}{1-x^2}\right]y=0$}。
- **导航**：父级 [`../README.md`](../README.md)；核心库 [`../faclib/README.md`](../faclib/README.md)。

[返回上级](../README.md)