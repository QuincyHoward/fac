# ionis/ —— 电离平衡与速率系数拟合库

## 1. 定位

本目录是 FAC 中第三方电离平衡（ionization balance）与速率系数拟合模块，根 `README.md` 的 "Third party content that cannot be distributed under GPL" 段（即 `UtilList` 所列目录）对它的原文描述为：

> `+ ionis/,      ionization balance calculation of Arnaud&Raymond,`
> `and that of Mazzotta et al. Rates fitted by Verner et al.`

即本目录提供 Arnaud & Raymond（以及 Arnaud & Rothenflug）、Mazzotta et al. 的**平衡电离分数**相关拟合，以及 Verner et al. 的 RR/DR/光电离/碰撞电离拟合；另有 Bell et al.、Voronov、M. F. Gu 等的碰撞电离与复合速率拟合。全部为 Fortran 77 源码，编译进顶层 `libfac.a`。

## 2. 物理效应三段式

### 2.1 简介

给定电子密度 $n_e$ 与温度 $T$（或 $T_e$），各电荷态离子数密度 $n_i$ 满足电离—复合级联方程；稳态（电离平衡）下满足

$$
\frac{d n_i}{dt}=n_e\left[S_{i-1}n_{i-1}+\alpha_{i+1}n_{i+1}-(S_i+\alpha_i)n_i\right]=0,
\qquad f_i=\frac{n_i}{n_{\rm tot}} .
$$

其中 $S_i(T)$ 为从第 $i$ 态到 $i+1$ 态的碰撞电离速率系数，$\alpha_i(T)=\alpha_i^{\rm RR}+\alpha_i^{\rm DR}$ 为从第 $i+1$ 态复合到第 $i$ 态的辐射复合（RR）与双电子复合（DR）速率系数之和。FAC 的 C 层 `FracAbund()`（`faclib/rates.c`）即用相邻态比值 $a_{i}=a_{i-1}\,\alpha_{i-1}/S_i$ 迭代求出稳态分数 $f_i$。

### 2.2 LaTeX 公式

**(a) 速率系数的 Maxwell 平均积分定义（文献通用形式，源码未直接出现积分号；源码实现其解析拟合）：**

$$
S_i(T)=\left(\frac{8}{\pi m_e}\right)^{1/2}\frac{1}{(kT)^{3/2}}
\int_{E_i}^{\infty}\sigma_i^{\rm CI}(E)\,E\,e^{-E/kT}\,dE ,
$$

$$
\alpha_i^{\rm RR}(T)=\left(\frac{8}{\pi m_e}\right)^{1/2}\frac{1}{(kT)^{3/2}}
\int_{0}^{\infty}\sigma_i^{\rm RR}(E)\,E\,e^{-E/kT}\,dE ,
$$

DR 速率系数的常用拟合（Mazzotta 型，直接对应 `drfit.f` / `ndrfit.f` 源码）：

$$
\alpha^{\rm DR}(T)=\frac{1}{T^{3/2}}\sum_{j}c_j\,e^{-E_j/T}.
$$

**(b) Verner 型解析拟合（按源码实际系数形式）：**

- RR（`rrfit.f`，Verner & Ferland 型）：

$$
\alpha^{\rm RR}(T)=\frac{a_1}{\sqrt{T/a_3}\,\left(1+\sqrt{T/a_3}\right)^{1-a_2}\left(1+\sqrt{T/a_4}\right)^{1+a_2}},
$$

源码写作 `tt=sqrt(t/rnew(3,iz,in))`；
`r=rnew(1)/(tt*(tt+1)**(1-rnew(2))*(1+sqrt(t/rnew(4)))**(1+rnew(2)))`。
其余离子用幂律 `r=rrec(1)/tt**rrec(2)`（`tt=t*1e-4`），Fe I–XV 用 `r=fe(1)/tt**(fe(2)+fe(3)*log10(tt))`。

- 新 RR（`nrrfit.f`，M. F. Gu）：

$$
\alpha^{\rm RR}(T)=\frac{a}{\sqrt{T/t_0}\left(1+\sqrt{T/t_0}\right)^{1-b}\left(1+\sqrt{T/t_1}\right)^{1+b}},
\quad b\to b+b_1 e^{-t_2/T}\ (t_2>0).
$$

源码：`x0=sqrt(t/t0); x1=sqrt(t/t1); r=x0*(1+x0)**(1-b)*(1+x1)**(1+b); r=a/r`。

- 光电离截面（`phfit2.f`，Verner et al. 型；源码形式）：

$$
\sigma^{PI}(E)=a\left[(y-1)^2+b^2\right]y^{q}\left(1+\sqrt{y/c}\right)^{p},
\quad y=E/E_0,\ \ p=p_1=-\mathrm{ph1}(5),\ \ q=-\tfrac{p_1}{2}-5.5-l .
$$

源码：`p1=-ph1(5,...); y=e/ph1(2,...); q=-0.5*p1-l(is)-5.5;`
`a=ph1(3)*((y-1)**2+ph1(6)**2); b=sqrt(y/ph1(4))+1; s1=a*y**q*b**p1`。
高能尾巴另用 `ph2` 参数以 `s=log(a)+q*log(z)+p1*log(b)` 形式给出。

- 直接碰撞电离（`cfit.f`，Voronov 1997 形式）：

$$
S(T)=C_3\,\frac{1+C_2\sqrt{u}}{C_4+u}\,u^{C_5}e^{-u},
\quad u=E_{\rm ion}/(kT),\ \ kT=T\cdot 8.617385\times10^{-5}\ {\rm eV}.
$$

- 碰撞电离（`colfit.f`，Arnaud & Raymond 型）用指数积分 $fcl1(x),fcl2(x)$：
$S=\dfrac{6.69\times10^{-7}}{kT\sqrt{kT}}\sum_i\dfrac{e^{-x}}{x}\big[\dots\big]$，
$x=E_i/(kT)$，源码 `c=6.69e-07*c/tk/sqrt(tk)`。

- 电离阈值能量辅助函数（`intexp.f`）：$FU,FA,FC,FD,FB,F2$ 为指数积分型近似，$FA=1-xFU(x)$、$FC=1-xFA(x)$ 等；用于 `ionis.f` 中
`SA=A*FA(X)+B*FB(X)+C*FU(X)+D*X*F2(X)`，
`DIR=1.D-14*6.692D+7*SD/AKTEV**1.5`。

**(c) 温度参数与无量纲变量约定：**

| 变量 | 单位 | 约定 |
| --- | --- | --- |
| `t` | K | `rrfit.f`、`recomb_Fe.f` 使用开尔文，**不做 eV 换算**：`rrfit.f:45–53` 直接用 K 单位参数 `rnew(3)/rnew(4)`、`tt=t*1e-4` |
| `t` → `te` | K→eV | `cfit.f:19` 用 `te=t*8.617385e-5`；`colfit.f:96` 用 `tk=8.6171e-5*t`；`recomb.f:129` 用 `KTEV=TE/11605.`（≈8.61706e-5）。三者常数略有差异，不能合并为同一换算式 |
| `t`, `AKTEV` | eV | `drfit.f`, `nrrfit.f`, `ndrfit.f`, `ionis.f`, `beli.f` 用电子伏 |
| `tt` | $10^4$ K | `rrfit.f`/`recomb` 幂律段 `tt=t*1e-4` |
| `x`, `u`, `y` | 无量纲 | `x=E_{\rm ion}/kT`，`u=E_{\rm ion}/(kT)`，`y=E/E_0` |
| `in`, `in0`, `ne` | — | 电子数；`in0` 为 `in-1`（0 到 iz-1，复合离子），`in` 为 1 到 iz（被电离离子） |

### 2.3 源码对应表

| 物理效应 / 拟合 | 源文件 | 真实入口名（SUBROUTINE / FUNCTION） |
| --- | --- | --- |
| 稳态电离平衡（相邻态比值） | 上层 C 库 `faclib/rates.c` | `FracAbund`（用 `Ionis` / `Recomb`） |
| 碰撞电离（Arnaud & Raymond / 直接+EA） | `colfit.f` | `colfit`, `ecolfit`, `ccolfit`, `fcl1`, `fcl2` |
| 碰撞电离（Voronov 1997） | `cfit.f` | `cfit`, `block data cifit` |
| 碰撞电离（Arnaud 参数 + 指数积分近似） | `ionis.f` | `ionis`, `redan` |
| 电离/激发自电离截面与速率（Bell 1983） | `beli.f` | `ebeli`, `cbeli`, `rbeli` |
| 指数积分辅助函数 | `intexp.f` | `fu`, `fa`, `fc`, `fd`, `fb`, `f2` |
| 辐射复合 RR（Verner & Ferland 等） | `rrfit.f` | `rrfit`, `block data radrec` |
| 双电子复合 DR（Mazzotta et al. 1998） | `drfit.f` | `drfit`, `block data drdata` |
| RR（M. F. Gu 新拟合） | `nrrfit.f` | `nrrfit`, `block data nrrdata` |
| DR（M. F. Gu 新拟合） | `ndrfit.f` | `ndrfit`, `block data ndrdata` |
| 光电离截面 / 阈值（Verner et al.） | `phfit2.f` | `phfit2`, `ephfit2` |
| 复合速率（老拟合，Aldrovandi & Pequignot 等） | `recomb.f` | `recomb` |
| 铁复合速率（专用） | `recomb_Fe.f` | `recombFe`, `alphadi` |

## 3. 逐文件说明（全部 12 个 .f）

1. **`intexp.f`** —— 指数积分近似辅助函数库。入口：`FUNCTION FU(X)`、`FA(X)`、`FC(X)`、`FD(X)`、`FB(X)`、`F2(X)`（均 `IMPLICIT REAL*8`）。`FU` 对 $x\in[0.02,10]$ 用 M-S-(1978) 近似 `DLOG(R)-(0.36+0.03*((X+0.01)**EPS))*Q2`，大 $x$ 用渐近展开，小 $x$ 用 `DEXP(X)*(-DLOG(X)-0.5772+X)`；`FA=1-X*FU`，`FC=1-X*FA`；`F2` 用 14 阶有理式（系数 `AP/AQ`）。调用方：`ionis.f`（`SA`、`SEA` 表达式）、`faclib/crm.c`（`FU`）。

2. **`ionis.f`** —— 电子碰撞电离速率（cm³/s），Arnaud 型直接电离 + 激发自电离，数据以 `DATA` 内嵌（`ZR/IR/KR/IDIR/AR..DR`，`ZRE/IRE/AEA..EEA`；M. F. Gu 2002-02-02 由读文件改为内嵌）。入口 `SUBROUTINE IONIS(z,ION,AKTEV,AUTO,DIR,RION)`：`z` 核电荷，`ION` 罗马电荷+1，`AKTEV` 温度(eV)，输出 `AUTO` 自电离速率、`DIR` 直接电离速率、`RION=DIR+AUTO`；另含 `SUBROUTINE REDAN(AKTEV,REDAC)`（Fe XVI Gattuttu & Hahn REDA 修正）。调用方：`faclib/rates.c` 的 `Ionis()`（m=0，经 `f2c.h` 的 `IONIS` 宏→`f_ionis`），上层 `python/pcrm.c`。

3. **`recomb.f`** —— 老式复合速率拟合，注释指明用 Aldrovandi & Pequignot、Shull et al.、Seaton、Pradhan、Younger、Storey、Bely-Dubau、Jacobs 数据。入口 `SUBROUTINE RECOMB(Z,S,TE,RR,RDIEL)`：`Z` 核电荷，`S` 待复合离子的电离度，`TE` 温度(K)，`RR` 辐射复合速率、`RDIEL` 双电子复合速率（cm³/s）。`KTEV=TE/11605.`，`TL=DLOG10(TE)`。调用方：`faclib/rates.c::Recomb()`（m=0 且 Z≠26）。

4. **`recomb_Fe.f`** —— 仅铁（Z=26）的复合速率。入口 `SUBROUTINE RECOMBFe(Z,S,TE,RR,RDIEL)`（参数含义同上），氢样离子用 Seaton 公式 `RR=5.197D-14*Z*DSQRT(ALAM)*(.4288+.5*DLOG(ALAM)+.469*ALAM**(-1/3))`；其他用 `TE4**(ETA+BETA*log10)` 幂律。另含 `function alphadi(n,j,t)`：DR 速率，项形如 `t**-1.5*a*exp(-e1*11590/t)`，数据源 Karim&Bhalla、Chen、Badnell、Roszman 等。调用方：`faclib/rates.c::Recomb()`（m=0 且 Z=26）。

5. **`cfit.f`** —— Voronov 1997（ADNDT 65, 1）直接碰撞电离拟合，H 到 Ni（Z≤28）。入口 `subroutine cfit(iz,in,t,c)`；`iz` 原子序数，`in` 电子数(1..iz)，`t` 温度(K)，`c` 速率系数(cm³/s)。`common/CF/CF(5,28,28)` 由 `block data cifit` 填充 5 个拟合参数 $(E_{\rm ion},\,C_2,\,C_3,\,C_4,\,C_5)$；核心 `c=cf(3)*(1+cf(2)*sqrt(u))/(cf(4)+u)*u**cf(5)*exp(-u)`，`u=cf(1)/te`。调用方：`faclib/rates.c::CFit()` 及 `ColFit()` 的兜底。

6. **`colfit.f`** —— Arnaud & Raymond 1992 (Fe)、Arnaud & Rothenflug 1985（其余元素，含 Verner & Yakovlev 1990 修正）碰撞电离拟合，H 到 Zn（Z≤30），$10^4$–$10^9$ K，含激发自电离。入口：`subroutine ecolfit(iz,in,is,e)`（返回壳层电离阈值 eV，`is=0` 返回最外壳）；`subroutine colfit(iz,in,is,t,ca,c)`（总/分壳层速率，`ca` 自电离贡献，`is=0` 为总速率）；`subroutine ccolfit(iz,in,is,t,ca,c)`（截面版）；`double precision function fcl1(x)`、`fcl2(x)`（指数积分近似）。`common/clion`、`common/eafe`。调用方：`faclib/rates.c::ColFit()` / `CFit()`（`COLFIT`/`ECFIT` 宏）。

7. **`phfit2.f`** —— Verner, Ferland, Korista, Yakovlev 1996（OP 元素外壳）与 Verner & Yakovlev 1995（内壳及非 OP 元素外壳）光电离拟合，H 到 Zn。入口：`subroutine ephfit2(nz,ne,is,s)`（壳层 `is` 的电离阈值 eV）；`subroutine phfit2(nz,ne,is,e,s)`（光子能量 `e` eV，返回部分光电离截面 Mb）。使用 `common/ph1/ph1(6,30,30,7)`、`ph2(7,30,30)`、`ninn/ntot`，`l(7)` 为壳层自旋轨道参数。调用方：`faclib/rates.c::PhFit2()`（经 `PHFIT2` 宏），`python/pcrm.c`。

8. **`rrfit.f`** —— Verner & Ferland 1996（H/He/Li/Na 样）、Pequignot 1991（C/N/O/Ne 重拟合）、Arnaud & Raymond 1992（Fe XVII–XXIII）、Shull & Van Steenberg 1982、Landini & Monsignori Fossi 1990/1991 等辐射复合速率。入口 `subroutine rrfit(iz,in0,t,r)`：`in0` 为复合离子的电子数减 1（M. F. Gu 改动），`t` 为 K，`r` 为 cm³/s。用 `common/rrec`、`rnew`、`ferr` 与 `block data radrec`。调用方：`faclib/rates.c::RRFit()`（经 `RRFIT` 宏），并作为 `NRRFit()` 的兜底。

9. **`drfit.f`** —— Mazzotta et al. A&AS 133, 403 的双电子复合速率。入口 `subroutine drfit(iz,in,t,r)`：`iz` 核电荷(2..28)，`in` 复合离子电子数(0..iz-1)，`t` 温度(eV)，`r` cm³/s。公式 `r=Σ drc(j,i)*exp(-dre(j,i)/t) / t**1.5`（4 项），`block data drdata` 存 378 组系数，`ind(iz)` 首次调用时初始化偏移。调用方：`faclib/rates.c::DRFit()`（经 `DRFIT` 宏），`python/pcrm.c`。

10. **`nrrfit.f`** —— M. F. Gu 的新 RR 拟合（ApJ，内部文注释）。入口 `subroutine nrrfit(iz,in,t,r)`：`t` 为 eV，`r` 单位 $10^{-10}$ cm³/s，负值表示无数据。参数 `common/nrr/ind(28),rrpar(6,70)`，6 个参数 `(a,b,t0,t1,b1,t2)`；4 参数 Verner 型主体 + `b1*exp(-t2/t)` 修正。调用方：`faclib/rates.c::NRRFit()`。

11. **`ndrfit.f`** —— M. F. Gu 的新 DR 拟合。入口 `subroutine ndrfit(iz,in,t,r)`：`t` 为 eV，`r` 单位 $10^{-10}$ cm³/s，负值表示无数据。最多 16 项 `drc*exp(-dre/t)` 之和除以 `t**1.5`，`common/ndr/ind(28),dre(16,70),drc(16,70)`；`in=0` 或 >10 返回 -1。调用方：`faclib/rates.c::NDRFit()`，并作为 `DRFit` 的兜底。

12. **`beli.f`** —— Bell et al. J. Phys. Chem. Ref. Data 12, 891 (1983) 电离数据。入口：`subroutine ebeli(z,n,e)`（阈值 eV）；`subroutine cbeli(z,n,ene,ea,dir,e)`（入射能量 `ene` eV，返回 `ea` 自电离截面、`dir` 直接电离截面，单位 $10^{-20}$ cm²，`e` 为相对误差%）；`subroutine rbeli(z,n,t,ea,dir)`（15 点 Gauss–Legendre 积分求速率系数，单位 $10^{-10}$ cm³/s，`t` 为 eV）。共用 `common/idata/error(406),cdi(7,406),cea(8,406)`；索引 `k=1+z(z-1)/2+(z-n)`。调用方：`faclib/rates.c::EBeli/CBeli/RBeli`（经 `EBELI/CBELI/RBELI` 宏），`rbeli` 亦被 `cbeli` 内的速率测试调用（第 163 行 `call cbeli(...)`）。

## 4. 接口、上下游、构建、导航

- **Fortran→C 接口**：`faclib/f2c.h` 定义 `IONIS`、`RECOMB`、`RRFIT`、`DRFIT`、`NRRFIT`、`NDRFIT`、`PHFIT2`、`EBELI`、`CBeli`、`RBELI`、`CFIT`、`COLFIT`、`FU` 等宏映射到 `f_xxx` 符号；`faclib/cf77.h` 另有大写版本。`faclib/rates.h` 声明 C 包装函数。
- **上游（被调用）**：`faclib/rates.c` 的 `Ionis/Recomb/RRFit/DRFit/NRRFit/NDRFit/PhFit2/EBeli/CBeli/RBeli/CFit/ColFit/FracAbund`；`faclib/crm.c`（用 `FU`）；`python/pcrm.c`（命令 `ordered/...` 等）；SFAC 命令解析层经 rates.c 间接使用。
- **副作用/约定**：`Ionis()` m=0 时把外部 `nele` 转成罗马数 `z+1-nele` 并把结果乘 $10^{10}$；`Recomb()` m=0 时把 eV 温度除以 $8.617385\times10^{-5}$ 转成 K；速率下限钳制为 $10^{-30}$。
- **构建**：`Makefile.in`（Autoconf 模板）中 `SRC = intexp.f ionis.f recomb.f recomb_Fe.f cfit.f colfit.f phfit2.f rrfit.f drfit.f nrrfit.f ndrfit.f beli.f`，`FC=@F77@`、`FFLAGS=@FFLAGS@`，`ionis:` 目标用 `ar r ${TOPDIR}/libfac.a $(OBJS)` 归档；`make clean` 清除 `*.o *.a *~`。由顶层 `configure` 生成的 Makefile 驱动。
- **第三方属性**：随 `fac_util.tar.gz` 分发（非 GPL），见根 `README.md` "Third party content that cannot be distributed under GPL" 与 `UtilList`。

## 5. README 维护记录（自底向上）

- **定位与职责**：`ionis/` 提供电离平衡与速率系数的解析拟合，供 `faclib/rates.c` 与 CRM 调用。
- **底层依据**：`rrfit.f`、`nrrfit.f`、`cfit.f`、`colfit.f`、`drfit.f`、`ndrfit.f`、`ionis.f`。
- **输入/输出**：输入电荷态、温度与拟合参数；输出 RR/DR/CI 等速率系数及电离平衡量；部分接口带 eV→K 与 $10^{10}$ 密度换算约定。
- **验证与回归**：通过 `faclib/rates.c`、`faclib/crm.c` 与上层示例间接验证；拟合系数不得随意修改。
- **已知限制**：随 `fac_util.tar.gz` 分发；实现是拟合而非逐点积分；温度单位与密度因子容易误读。
- **公式核查**：\underline{$S_i(T)=\left(\frac{8}{\pi m_e}\right)^{1/2}\int_0^\infty \sigma(E)E e^{-E/k_BT}\,dE$}；\underline{$\alpha_i^{\rm RR}(T)=\left(\frac{8}{\pi m_e}\right)^{1/2}(k_BT)^{-3/2}\int_0^\infty \sigma^{\rm RR}(E)E e^{-E/k_BT}\,dE$}。
- **导航**：父级 [`../README.md`](../README.md)；核心库 [`../faclib/README.md`](../faclib/README.md)。

[返回上级](../README.md)