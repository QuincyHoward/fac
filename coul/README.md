# `coul/`：FAC 的库仑函数与连续态原子物理工具库

## 1. 目录定位

`coul/` 是 FAC 随源码捆绑的第三方 Fortran 工具库，根 `README.md` 的 “Third party content that cannot be distributed under GPL” 一节及 `UtilList` 均列出本目录，说明为 “fortran routines related to coulomb functions”。

它提供 FAC 连续态与库仑问题所需的一组底层数值内核：

- 复变量/实变量库仑波函数、Dirac-Coulomb 径向波函数；
- 正能、负能与类氢束缚—连续态波函数；
- 库仑相位、Sommerfeld 参数、归一化；
- 连续电子电多极矩阵元、光电离/自由—自由跃迁积分与 Gaunt 因子；
- Bessel、Gamma、超几何、指数积分等特殊函数；
- WKB/半经典近似与 Riccati 展开；
- 角动量重耦合系数；
- 有限核尺寸/QED 自能修正所需的 Mohr 表插值。

`doc/manual.tex` 从物理流程上说明：FAC 连续过程采用扭曲波（DW）近似（约 97–99 行），R 矩阵外边界默认使用 Dirac-Coulomb 函数（约 3117–3125 行），高分波尾部可用 Coulomb-Bethe 近似（约 3255–3260、3281–3323 行），连续轨道表以振幅/相位形式输出（约 3885–3890 行），`Y5N` 给出负能 Seaton 归一化库仑波函数（约 3893–3899 行）；FAQ 说明 FAC 使用标准 Dirac-Coulomb Hamiltonian（约 5031–5036 行）。本目录即这些连续态/库仑结构的数值实现来源之一。

---

## 2. 组织形式与函数族分类

目录内共 18 个 `.f` 文件，另有 `Makefile.in`。按用途可分为：

1. **核心库仑/Dirac-Coulomb 波函数**
   - `coulcc.f`：Steed 连分数法的复库仑波函数通用引擎。
   - `dcoul.f`：正/负能 Dirac-Coulomb 规则与不规则径向解。
   - `cphamp.f`：正能库仑波函数的振幅与相位。
   - `y5n.f`：负能 Seaton 归一化库仑波函数。

2. **连续电子矩阵元与类氢过程**
   - `cmultip.f`：电多极库仑激发径向矩阵元，含 Riccati 展开、Steed 连分数、WKB 分支与 Gauss 积分。
   - `coulrad.f`：类氢离子的 E1 束缚—束缚跃迁、光电离截面、自由—自由热平均 Gaunt 因子。

3. **特殊函数与数值支撑**
   - `clogam.f`、`dlogam.f`、`argam.f`：复/实 Gamma 对数与 Gamma 相位。
   - `f11.f`：合流超几何函数 $_1F_1$。
   - `besljn.f`、`beslik.f`：球 Bessel 函数与指数缩放的修正 Bessel $K$ 函数。
   - `expint.f`、`eione.f`：指数积分 $E_n(x)$、$E_1(x)$。
   - `d1mach.f`：机器常数。

4. **角动量重耦合**
   - `njsym.f`、`njintr.f`：通用重耦合系数计算及 FAC 接口。

5. **QED/有限核修正表**
   - `mohrfin.f`：Mohr 表的插值/外推，用于 1s、2s、2p- 对称性的有限核尺寸相关修正。

---

## 3. 物理效应（最重要）

### 3.1 简介

连续电子在点核库仑场中满足非相对论径向 Schrödinger 方程；在 FAC 的 relativistic 框架中，对应的是 Dirac-Coulomb Hamiltonian 下的连续轨道。`coul/` 中的 `COULCC`、`DCOUL`、`CPHAMP`、`Y5N`、`CMULTIP`、`PIXZ1` 等例程分别覆盖正能、负能、复能量、Dirac 两分量波函数、连续态相位/归一化以及连续电子与束缚态之间的多极矩阵元。

**符号约定提示（重要）**：源码各文件对电荷符号的约定并不完全一致。`cphamp.f` 注释写 `eta0: -z/k, z negtive for electron ion collision`，而 `dcoul.f` 头部写 `z Nuclear charge. positive for electron-ion system.`。下文采用连续态库仑函数的常见约定 $\eta=-Z/k$、$\rho=kr$；实际调用时应以各入口注释与 FAC 调用处传入的符号为准。

### 3.2 LaTeX 公式

**(a) 径向库仑方程与库仑波函数**

在原子单位下，对核电荷 $Z>0$ 的吸引势 $V(r)=-Z/r$、能量 $E=k^2/2$：

$$
\left[\frac{d^2}{dr^2}
-\frac{l(l+1)}{r^2}
+\frac{2Z}{r}
+k^2\right]P_{kl}(r)=0 .
$$

令

$$
\rho=kr,\qquad \eta=-\frac{Z}{k},
$$

则等价形式为

$$
\left[\frac{d^2}{d\rho^2}
-\frac{l(l+1)}{\rho^2}
-\frac{2\eta}{\rho}
+1\right]u_l(\rho)=0 .
$$

规则库仑函数 $F_l(\eta,\rho)$ 与不规则库仑函数 $G_l(\eta,\rho)$ 的大 $\rho$ 渐近相位可写为

$$
F_l(\eta,\rho)\sim \sin\theta_l,\qquad
G_l(\eta,\rho)\sim \cos\theta_l,
$$

$$
\theta_l
=
\rho-\eta\ln(2\rho)-\frac{l\pi}{2}+\sigma_l .
$$

其中 $\sigma_l$ 为库仑相位。上述 $F_l/G_l$ 与 $\eta,\rho$ 的定义是库仑波函数的通用形式；源码头注释未逐字打印该渐近式，但 `coulcc.f` 明确返回 $F,G,F',G',SIG$，并说明可处理 Coulomb Schrödinger、Klein-Gordon 及适当形式的 Dirac 方程，`cphamp.f` 则由 $F,G$ 构造振幅与相位。

**(b) 库仑相位与归一化**

库仑相位（Sommerfeld 参数 $\eta$）通常定义为

$$
\sigma_l=\arg\Gamma(l+1+i\eta)
=\operatorname{Im}\ln\Gamma(l+1+i\eta).
$$

源码中 `dcoul.f` 的 `FUNCTION DELTAC(ETA,RLAMB)` 直接实现

$$
\Delta_l=-i\,\operatorname{CLGAM}(l+1+i\eta)
\quad (\mathrm{mod}\ 2\pi),
$$

其实部即 $\operatorname{Im}\ln\Gamma(l+1+i\eta)$；`coulcc.f` 的 `SIG` 数组返回各阶库仑相位，`y5n.f` 用 `sig(k)` 与 Gamma 对数构造负能 Seaton 归一化。

`coulcc.f` 头部还给出出射/入射 Hankel 型组合：

$$
H^{+}=G+iF,\qquad H^{-}=G-iF \quad (KFN=0),
$$

或在 Bessel 情况下

$$
H^{(1)}=J+iY,\qquad H^{(2)}=J-iY .
$$

**(c) Dirac-Coulomb 径向波函数**

`dcoul.f` 中采用相对论参数（源码常量 `SL=137.036D0` 为 $1/\alpha$ 的近似）：

$$
\kappa_D=\frac{Z}{137.036},\qquad
\gamma=\sqrt{\kappa^2-\kappa_D^2},\qquad
\lambda=\gamma-\frac12 .
$$

源码用 `clgam`、复 $\eta$ 与 `COULCC` 组合出 Dirac 大分量 $P$、小分量 $Q$ 及其不规则解 `p1/q1`；正能分支直接取规则/不规则解的实部与虚部，负能分支用 `UVIP3P` 在 $\eta$ 偏移点上插值得到幅值、归一化与相位。

**(d) WKB / 半经典近似及适用条件**

通用半经典形式可写作（**说明：这是常见 WKB 形式，源码未直接打印此简式；实现细节与适用分区以 `cmultip.f` 注释为准**）：

$$
u(\rho)\sim
\frac{1}{\sqrt{p(\rho)}}
\sin\!\left(\int^\rho p(\rho')\,d\rho'+\phi\right),
$$

其中局域波数由库仑径向方程决定：`cmultip.f` 的 `WKB(DRHO,NPAR,DF,DG)` 计算库仑函数的半经典正弦/余弦形式，`CLMINT` 注释说明其库仑积分组合了渐近展开、Gauss 积分与 WKB 近似。

源码给出的区域选择（见 `cmultip.f:DCOULM` / `COULOM` 注释）为：

- 原点附近 Riccati 展开：$\eta>30$、$\rho<2\eta-6.75\eta^{0.4}$ 且 $\rho\eta>12$；
- 渐近 Riccati 展开：$\eta>30$、$\rho>2\eta+20\eta^{0.25}$，或 $\eta<-8$、$\rho\eta>-30$；
- 其余 $\eta$-$\rho$ 平面使用 Steed 连分数法，但 $\rho<0.2\rho_{\mathrm{turning}}$ 的区域除外；
- `CLMINT` 在大参数/远离转折点的库仑积分中调用 WKB 分支。

**(e) Bessel、Gamma 与指数积分在连续态矩阵元中的作用**

- $\log\Gamma(z)$ 用于库仑相位、归一化、负能波函数与统计率中的阶乘比：
  `clogam.f:CLOGAM`、`dlogam.f:dlogam`、`argam.f:argam`。
- 球 Bessel $j_l/y_l$ 是 $\eta\to0$ 时的库仑函数极限，用于在 `faclib/radial.c` 中构造连续径向积分的相位/振幅因子：`besljn.f:BESLJN`。
- 指数缩放的修正 Bessel $K_\lambda$ 通过 `coulcc(KFN=3)` 得到：`beslik.f:beslik`。
- 合流超几何 $_1F_1$ 是 Steed 库仑算法中规则解的级数核心：`f11.f:F11`。
- 指数积分
  $$
  E_n(x)=\int_1^\infty e^{-xt}t^{-n}\,dt,\qquad x>0,n>0,
  $$
  由 `expint.f:EXPINT` 计算，`E_1(x)` 由 `eione.f:EIONE` 提供；FAC 在 `faclib/recombination.c` 的相关积分因子中使用 `EXPINT`。

**(f) `eione.f` / `mohrfin.f` 对应的物理问题（按源码注释）**

- `eione.f` **不是库仑电离例程**。其头部说明计算与指数积分有关的积分；`IOPT=1/2/3` 分别对应 $\int e^t/t\,dt$、$E_1(x)=\int_x^\infty e^{-t}/t\,dt$ 及其缩放形式，并引用 Cody & Thacher (1968/1969) 与 NATS-FUNPACK。注释还提到可用于 Landau-Zener 计算。`expint.f` 调用它得到 $E_1$。
- `mohrfin.f` 计算 $F(Z\alpha)$ 函数，针对 1s、2s、2p- 对称性，对 P. J. Mohr (At. Data Nucl. Data Tables 29, 453, 1983) 的表做插值/外推；源码注释还列出 `INTERP`，实际代码用 `UVIP3P`。FAC 的 `faclib/coulomb.c` 在考虑有限核电荷半径 `rms` 的 QED 自能修正时调用 `MOHRFIN`。因此它对应的是**有限核尺寸/QED 自能表修正**，不是连续电子库仑散射。
- `coulrad.f` 则明确处理类氢束缚—束缚 E1 跃迁、束缚—自由光电离与自由—自由 Gaunt 因子，属于连续态跃迁积分，而非 collisional ionization 本身。

### 3.3 源码对应表

| 物理效应 / 公式对象 | 源文件与真实例程 | 源码作用 |
|---|---|---|
| 复库仑函数 $F,G,F',G',\sigma$、Hankel/Bessel 模式 | `coulcc.f: COULCC`；内部 `CF1C`, `CF2`, `CF1R`, `F20`, `CF1A`, `RCF`, `TIDY` | Steed 连分数法，支持复 $x,\eta,\lambda$、多阶 $\lambda$，KFN=0/1/2/3 分别选 Coulomb/球 Bessel/柱 Bessel/修正柱 Bessel |
| 正/负能 Dirac-Coulomb $P,Q$ | `dcoul.f: DCOUL`；`DCOUL1`, `FCOUL`, `SUM2F0`, `DELTAC`, `CLGAM` | 相对论库仑波函数；负能用 `UVIP3P` 插值，正能取复解实/虚部；`FCOUL` 用 Steed + 递推 + 渐近展开 |
| 正能库仑振幅/相位 | `cphamp.f: cphamp` | 由 $F,G$ 得 $A=\sqrt{F^2+G^2}$、$\phi=\mathrm{atan2}(F,G)$ 及可选导数 |
| 负能 Seaton $y5$ 波函数 | `y5n.f: y5n` | 负能库仑波函数， Gamma 归一化，内部调用 `COULCC` |
| 电多极库仑激发矩阵元 | `cmultip.f: CMULTIP`, `RECMUD`, `RECLIP`, `DCOULM`, `DRCWFF`, `CLMINT`, `COULOM`, `RICCAT`, `STEED`, `WKB`, `GAUSS`, `INTEGR`, `DPHASE` | 连续电子电多极径向矩阵元，Riccati/Steed/WKB/Gauss 组合 |
| 类氢 E1 跃迁与光电离/Gaunt | `coulrad.f: ACOFZ1`, `PIXZ1`, `GFFZ1` | E1 跃迁率/径向元、光电离截面、热平均自由—自由 Gaunt 因子 |
| 库仑相位 $\arg\Gamma$ | `dcoul.f: DELTAC`；`clogam.f: CLOGAM`；`dlogam.f: dlogam`；`argam.f: argam` | $\ln\Gamma(z)$、其实部、虚部或 $-i\ln\Gamma$ 形式 |
| Bessel 函数 | `besljn.f: BESLJN`；`beslik.f: beslik` | 球 Bessel $j/y$；指数缩放 $K_\lambda$ |
| $_1F_1$ 超几何 | `f11.f: F11` | `COULCC` 中规则库仑函数的级数核心 |
| 指数积分 | `eione.f: EIONE`；`expint.f: EXPINT` | $E_1$ 与 $E_n$ 的有理/级数近似 |
| 角动量重耦合 | `njsym.f: NJSYM`, `GENSUM`, `DRACAH`；`njintr.f: NJFORM`, `NJSUM`, `CPYDAT`, `NJDBUG` | 两套耦合方案之间的重耦合系数及 FAC 数据接口 |
| 有限核/QED 表修正 | `mohrfin.f: MOHRFIN` | Mohr $F(Z\alpha)$ 表插值/外推，给 1s/2s/2p- 修正 |

---

## 4. 逐文件说明

### 4.1 `argam.f`

- **功能**：返回复数 $z=x+iy$ 的 $\Gamma(z)$ 相位（虚部），模 $2\pi$。
- **关键入口签名**：`function argam(x, y)`。
- **算法要点**：用 `CLOGAM(DCMPLX(x,y))` 求 $\ln\Gamma(z)$，取虚部，并按正负做 `DMOD(...,2π)`。
- **FAC 调用方**：`faclib/coulomb.c:693` 在库仑相位计算中调用 `ARGAM`；`faclib/f2c.h`、`faclib/f2c.f90` 暴露 C 包装。

### 4.2 `beslik.f`

- **功能**：计算实阶指数缩放的修正 Bessel $K_\lambda(x)$ 及其导数。
- **关键入口签名**：`subroutine beslik(lambda, x0, dk, dkp)`。
- **算法要点**：令 $\eta=0$、$x=x_0$、`zlmin=lambda`、`KFN=3`，调用 `COULCC(MODE=-1)`，取 `GC` 与 `GCP` 的实部；`MODE1<0` 表示结果按 `EXP(-|SCALE|)` 缩放。
- **FAC 调用方**：`faclib/f2c.h:59-60`、`faclib/f2c.f90:354-356` 提供包装；`faclib/interpolation.c:169` 仅留有注释调用 `//BESLIK(k,t2,&dk,&dp);`，当前未发现有效 C 调用。

### 4.3 `besljn.f`

- **功能**：实正变量下的球 Bessel 第一类 $j_n(x)$ 与第二类/Neumann $y_n(x)$。
- **关键入口签名**：`FUNCTION BESLJN(JY,N,X)`，`JY=1/2` 选 Bessel/Neumann，`JY>2` 时减 2 并置内部标志。
- **算法要点**：按 Abramowitz & Stegun (1974) pp.435–478，小自变量用幂级数，其余用递推/渐近分支；负变量打印错误并 `STOP`。
- **FAC 调用方**：`faclib/radial.c` 多处调用，如 8222、8237–8239、8267–8269、8326、8498–8539、8688、8702、9944–9968、10052、10119、10139，用于连续态径向积分与相位/振幅因子；`faclib/f2c.h:61-62` 暴露包装。

### 4.4 `clogam.f`

- **功能**：任意复变量 $\ln\Gamma(z)$。
- **关键入口签名**：`FUNCTION CLOGAM(Z)`。
- **算法要点**：使用 Bernoulli 系数展开、反射公式和有理逼近；源码说明精度可由 `CALL LOGAM` 预置，但本 bundled 版本主要由 `ARGAM`、`DLOGAM`、`Y5N`、`COULCC` 使用。
- **FAC 调用方**：主要作为 `coul/` 内部支撑；当前未在 `faclib/*.c` 中发现直接调用。

### 4.5 `cmultip.f`

- **功能**：电多极库仑激发径向矩阵元，是连续电子—离子库仑问题的大型算法集合。
- **关键入口签名**：`SUBROUTINE CMULTIP(DRM1, DRM2, DZ, DWNI, DWNF, LAMB, LMIN, LMAX, DRST, MODE, IERR)`。
- **算法要点**：`MODE0=1/2/3/4` 选择 FF/GF/FG/GG 积分组合，`LAMB` 限定 1–6；内部 `RECMUD`/`RECLIP` 做递推与积分，`DCOULM`/`DRCWFF`/`COULOM`/`RICCAT`/`STEED` 按 $\eta,\rho$ 区域选择 Riccati 展开或 Steed 连分数，`CLMINT`/`WKB`/`GAUSS`/`INTEGR` 负责大参数库仑积分；还含 NAG 带状矩阵例程 `F01LBF`/`F04LDF` 与 `P01AAF`/`X02AAF`/`X04AAF`。
- **FAC 调用方**：`faclib/coulomb.c:922`、`faclib/coulomb.c:925`、`faclib/coulomb.c:1116` 在 Coulomb-Bethe 径向表生成中调用 `CMULTIP`；`faclib/f2c.h:69-70` 暴露包装。

### 4.6 `coulcc.f`

- **功能**：本目录的核心复库仑波函数引擎，Steed 连分数法。
- **关键入口签名**：`SUBROUTINE COULCC(XX,ETA1,ZLMIN,NL,FC,GC,FCP,GCP,SIG,MODE1,KFN,IFAIL)`。
- **算法要点**：对复 $x,\eta,\lambda$ 返回 $F,G,F',G',SIG$；`MODE1=1/2/3/4` 控制输出量，`MODE1=11/12/21/22` 返回 $H^\pm$，负值启用指数缩放；`KFN=0/1/2/3` 选择 Coulomb/球 Bessel/柱 Bessel/修正柱 Bessel；支持 Klein-Gordon 与适当 Dirac 形式。内部调用 `F11`、`CF1A`、`CF1C`、`CF2`、`CF1R`、`F20`、`RCF`、`CLOGAM/CDIGAM`。
- **FAC 调用方**：当前 `faclib/*.c` 未发现直接调用；它是 `dcoul.f`、`y5n.f`、`cphamp.f`、`beslik.f` 的内部核心。`doc/manual.tex:3898` 说明 `Y5N` 内部调用 `coulcc`。

### 4.7 `coulrad.f`

- **功能**：类氢离子径向跃迁与连续态积分工具集。
- **关键入口签名**：
  - `SUBROUTINE ACOFZ1(Z,AM,NU,NL,AC,ANC,NDL,IOPT)`；
  - `SUBROUTINE PIXZ1(Z,AM,NE,NL,PHE,PC,PCP,PNC,NDE,NDL,IOPT,IPCP)`；
  - `SUBROUTINE GFFZ1(Z,T,XLF,G,IOPT,NE,NDE,IFLAG)`。
- **算法要点**：`ACOFZ1` 对给定上/下主量子数直接递推 E1 径向矩阵元与跃迁率（Storey & Hummer 1991 CPC），`IOPT=2` 初始化阶乘/指数表；`PIXZ1` 计算束缚—自由光电离截面，`IPCP` 控制是否给分波截面；`GFFZ1` 用二维 Chebyshev 展开生成热平均自由—自由 Gaunt 因子（Karzas & Latter 1961；Hummer 1988 ApJ 327, 477）。
- **FAC 调用方**：`ACOFZ1` 在 `faclib/coulomb.c:219`、`faclib/coulomb.c:225`；`PIXZ1` 在 `faclib/recombination.c:566`、`faclib/recombination.c:575`；`faclib/f2c.h:71-74` 暴露 `ACOFZ1`/`PIXZ1` 包装。当前未发现 `GFFZ1` 的 C 端直接调用。

### 4.8 `cphamp.f`

- **功能**：正能库仑连续波函数的振幅、相位与振幅导数。
- **关键入口签名**：`subroutine cphamp(lambda, eta0, x0, a0, phase, a0p, ierr)`。
- **算法要点**：`eta0` 注释为 $-\eta/z/k$ 型 Sommerfeld 参数（$z$ 取负对应电子-离子），`x0=kr`；调用 `COULCC(KFN=0,MODE=1)` 得 $F,G$，输出 $a_0=\sqrt{F^2+G^2}$、$\phi=\mathrm{atan2}(F,G)$；`ierr=1/2/3` 控制只算振幅、振幅+相位、再加导数；`lambda>MAXL=2500` 时用递推数组偏移。
- **FAC 调用方**：当前 `faclib/*.c` 与 `python/fac.c` 未发现直接调用；作为工具例程保留。

### 4.9 `d1mach.f`

- **功能**：双精度机器常数 `D1MACH(I)`（最小正数、最大数、相对间距、$\log_{10}B$），并含 `I1MCRY`。
- **关键入口签名**：`DOUBLE PRECISION FUNCTION D1MACH(I)`；内部 `SUBROUTINE I1MCRY(A, A1, B, C, D)`。
- **算法要点**：Netlib 风格自动适配多种机器的 constants 表；`cmultip.f`、`coulcc.f` 等用其设置浮点阈值。
- **FAC 调用方**：`faclib/mpiutil.c:254` 调用 `D1MACH(1)`；`faclib/f2c.h`、`faclib/f2c.f90` 提供包装；多个 `coul/` 例程内部使用。

### 4.10 `dcoul.f`

- **功能**：正/负能 Dirac-Coulomb 径向波函数及规则/不规则解。
- **关键入口签名**：`subroutine dcoul(z, e, k, r, p, q, p1, q1, ierr)`。
- **算法要点**：$\gamma=\sqrt{k^2-(z/137.036)^2}$、$\lambda=\gamma-1/2$；负能用 `COULCC(MODE=11)` 在多个 $\eta$ 偏移点计算并用 `UVIP3P` 插值幅值/归一化/相位；正能取复解实部/虚部分别给不规则与规则 $P,Q$。同文件 `DCOUL1` 计算自由态 Dirac-Coulomb 波函数，`FCOUL` 用 Steed 连分数 + 递推 + 渐近展开，`SUM2F0` 求 $_2F_0$ 渐近级数，`DELTAC` 给库仑相移，`CLGAM` 给复 $\ln\Gamma$。
- **FAC 调用方**：`faclib/rmatrix.c:2380`、`2392`、`2396` 在 Gailitis 外边界匹配中调用 `DCOUL`；`faclib/orbital.c:1949`、`1988` 在连续轨道节点/归一化匹配中调用；`faclib/f2c.h:65-68` 暴露 `DCOUL`/`DCOUL1` 包装。

### 4.11 `dlogam.f`

- **功能**：实变量 $\ln\Gamma(x)$。
- **关键入口签名**：`function dlogam(x)`。
- **算法要点**：将 $x$ 转为复数 $x+0i$，调用 `CLOGAM`，取实部。
- **FAC 调用方**：`faclib/rates.c:206`、`1403`；`faclib/orbital.c:454`、`456`；`faclib/crm.c:7507`、`8383`、`8384`；`faclib/coulomb.c:1310`、`1311`；`faclib/f2c.h:57-58` 提供包装。

### 4.12 `eione.f`

- **功能**：指数积分相关函数的 DOUBLE PRECISION 近似。
- **关键入口签名**：`DOUBLE PRECISION FUNCTION EIONE(IOPT,ARG)`。
- **算法要点**：`IOPT=1` 计算主值型 $\int_{-\infty}^{arg} e^t/t\,dt$ 或其负变量形式；`IOPT=2` 计算 $E_1(ARG)=\int_{ARG}^{\infty}e^{-t}/t\,dt$；`IOPT=3` 计算缩放形式。采用 Cody & Thacher 的系数表，含溢出/下溢/零参数错误处理。源码注释提到可用于 Landau-Zener 计算。
- **FAC 调用方**：`expint.f` 内部调用；`faclib/f2c.h:21-22`、`faclib/f2c.f90:69-72` 提供包装。当前未发现 `faclib/*.c` 直接调用 `EIONE`。

### 4.13 `expint.f`

- **功能**：$E_n(x)=\int_1^\infty e^{-xt}t^{-n}dt$，$x>0,n>0$。
- **关键入口签名**：`DOUBLE PRECISION FUNCTION EXPINT(X,N)`。
- **算法要点**：`x>10` 用有理逼近；`x<10^{-3}` 用含 Euler 常数系数的多项式并减 $\ln x$（结果再乘 $e^x$）；中间区间用 `EIONE(2,x)`。**源码在缩放量 $F_n\equiv e^{x}E_n(x)$ 上递推**：`expint.f:50` 字面为 `EXPINT=(1-X*EXPINT)/I`（$i=2,\dots,n$），即 $F_n=(1-xF_{n-1})/n$；标准式 $E_n=(e^{-x}-xE_{n-1})/(n-1)$ 只是其等价数学形式，不是代码字面实现。源码头部说明 S. Bienstock, 1982-12-05。
- **FAC 调用方**：`faclib/recombination.c:4749` 计算指数积分因子 `f3`；`faclib/f2c.h:19-20`、`faclib/f2c.f90:62-65` 暴露包装。

### 4.14 `f11.f`

- **功能**：复数合流超几何函数 $_1F_1(a;b;z)$。
- **关键入口签名**：`FUNCTION F11(X,ETA,ZL,P,EPS,LIMIT,KIND,ERR,NITS,FPMAX,ACC8,ACC16)`。
- **算法要点**：源码定义 $a=ZL+1-\eta P$、$b=2(ZL+1)$、$z=2PX$；`KIND=0` 用扩展精度实数运算，`KIND=1/2` 用复数运算，后者带 `CDIGAM` 因子；`LIMIT` 控制最大项数，`ERR`/`NITS` 返回误差与迭代数。
- **FAC 调用方**：`coulcc.f` 的规则解计算内部使用；当前未发现 `faclib/*.c` 直接调用。

### 4.15 `mohrfin.f`

- **功能**：1s、2s、2p- 对称性的 $F(Z\alpha)$ 函数值及参数。
- **关键入口签名**：`SUBROUTINE MOHRFIN (N,KAPPA,Z,R,DELTAFZ,para,parb,parc,parp)`。
- **算法要点**：内置 Mohr (1983) 表；对 $Z<26$ 返回零修正和默认 `para=0,parb=0,parc=0,parp=1`；否则用 `UVIP3P(3,...)` 插值得到 `PARA/PARB/PARC/PARP`，并按 $R$ 与参考半径 $R_{\rm REF}$ 的幂律差加表值得到 `DELTAFZ`；`N<0` 时只输出拟合参数。
- **FAC 调用方**：`faclib/coulomb.c:528`、`545`、`563` 在有限核尺寸 QED 自能修正分支调用；`faclib/f2c.h:37-38`、`faclib/f2c.f90:149-151` 提供包装。

### 4.16 `njintr.f`

- **功能**：角动量重耦合例程的 FAC 接口与调试工具。
- **关键入口签名**：
  - `subroutine njdbug(ibg)`；
  - `subroutine cpydat(nd, idata, id)`；
  - `subroutine njform(im, nb, ij2, ij3, ifree)`；
  - `subroutine njsum(ij1, r)`。
- **算法要点**：`NJFORM` 填充 `COMMON/COUPLE` 后调用 `NJSYM`；`NJSUM` 调用 `GENSUM` 得到重耦合值；`CPYDAT` 在当前实现中打印 `not implemented`，但 FAC C 端仍调用以兼容接口；common block 标记 `!$OMP THREADPRIVATE`。
- **FAC 调用方**：`faclib/recouple.c:1703` (`CPYDAT`)、`1705` (`NJSUM`)、`1728` (`NJFORM`)、`1730` (`CPYDAT`)；`faclib/f2c.h:147-151` 暴露包装。

### 4.17 `njsym.f`

- **功能**：通用角动量重耦合系数计算。
- **关键入口签名**：`SUBROUTINE NJSYM (J6C,J7C,J8C,JWC,K6,K7,K8,KW,RECUP,ICOUNT,J2TEST,J3TEST)`。
- **算法要点**：Burke 编写、Scott/Hibbert 修改；通过 $K6/K7/K8/KW$ 描述 $\sqrt{2J+1}$、相位因子与 Racah 系数，调用 `GENSUM` 求和；同文件含 `GENJ45`、`GENI9`、`GENSUM`、`FACTT`、`DRACAH` 等内部例程；多个 common block 使用 OpenMP `THREADPRIVATE`。
- **FAC 调用方**：由 `njintr.f:NJFORM`/`NJSUM` 间接调用；当前未在 `faclib/*.c` 中发现对 `NJSYM` 的直接调用。

### 4.18 `y5n.f`

- **功能**：负能库仑波函数（Seaton 归一化）及其导数。
- **关键入口签名**：`subroutine y5n(lambda, xi, eta0, x0, y5, y5i, y5p, y5pi, ierr)`。
- **算法要点**：令 $x=i x_0$、$\eta=i\eta_0$、`zlmin=lambda+i xi`，以 `KFN=0,MODE=11` 调用 `COULCC`；用 `sig(k)`、`clogam(eta0+lambda+xi+1)`、`clogam(eta0-lambda-xi)` 构造归一化和相位；输出实部/虚部及关于 $r$ 的导数（源码中用 $-i\,d/d\rho$ 处理导数）。
- **FAC 调用方**：`python/fac.c:5135` 的 `PY5N` 调用，并注册为 Python 函数 `Y5N`（`python/fac.c:7075`）；`faclib/f2c.h:63-64`、`faclib/f2c.f90:376-378` 提供包装；`doc/manual.tex:3893-3899` 记录 `Y5N(n,l,r)` 接口。

---

## 5. 接口、上下游关系与构建

### 5.1 接口层次

1. **Fortran 核心层**：本目录 18 个 `.f` 文件，提供上述 SUBROUTINE/FUNCTION。
2. **C 绑定层**：`faclib/f2c.f90` 用 Fortran 2003 ISO C Binding 定义 `f_*` 包装函数/子程序；`faclib/f2c.h` 用 `#define` 把大写 Fortran 名映射到这些包装，例如 `DCOUL(...)` → `f_dcoul(...)`、`EXPINT(...)` → `f_expint(...)`。
3. **FAC 业务层**：
   - `faclib/coulomb.c`：Coulomb-Bethe 多极积分 `CMULTIP`、类氢 E1 率 `ACOFZ1`、库仑相位 `ARGAM`、QED 有限核修正 `MOHRFIN`；
   - `faclib/radial.c`：连续态径向积分、球 Bessel `BESLJN`；
   - `faclib/orbital.c`、`faclib/rmatrix.c`：`DCOUL` 连续轨道渐近匹配和量子缺陷/R 矩阵边界；
   - `faclib/recombination.c`：`PIXZ1` 光电离、`EXPINT` 指数积分因子；
   - `faclib/recouple.c`：`NJFORM`/`NJSUM`/`CPYDAT` 角动量重耦合；
   - `faclib/rates.c`、`faclib/crm.c`：`DLOGAM` 统计率/分布计算。
4. **外部依赖**：`dcoul.f`、`mohrfin.f` 使用 `toms/uvip3p.f` 的 `SUBROUTINE UVIP3P(NP,ND,XD,YD,NI,XI,YI)` 做三次插值；`coulcc.f`/`cmultip.f` 使用 `D1MACH` 和机器精度相关 common block；重耦合例程使用 `!$OMP THREADPRIVATE` common block 以保持线程私有状态。

### 5.2 `Makefile.in`

- `FC = @F77@`，`FFLAGS = @FFLAGS@`，`FFLAGSNO = @FFLAGSNO@`，`TOPDIR = @TOPDIR@`。
- `SRCNO = d1mach.f clogam.f f11.f coulcc.f`，这组使用 `FFLAGSNO` 编译，生成 `OBJSNO`。
- `SRC = y5n.f cphamp.f dlogam.f argam.f besljn.f beslik.f coulrad.f dcoul.f njsym.f njintr.f cmultip.f mohrfin.f expint.f eione.f`，共 14 个文件，使用 `FFLAGS` 编译，生成 `OBJS`。
- 目标 `coul` 先用 `$(FC) -c ${FFLAGSNO} ${SRCNO}` 编译 `SRCNO`，再执行 `ar r ${TOPDIR}/libfac.a ${OBJS} ${OBJSNO}`，把本目录全部目标文件归档进顶层 `libfac.a`。
- `clean` 删除 `*.o *.a *~`。

## 6. README 维护记录（自底向上）

- **定位与职责**：`coul/` 提供库仑函数、连续态、特殊函数与相位计算，是 `faclib/` 的重要数值支撑。
- **底层依据**：`coulcc.f`、`dcoul.f`、`cphamp.f`、`argam.f`、`besljn.f`、`coulrad.f`、`expint.f`。
- **输入/输出**：输入角动量、能量与库仑参数；输出库仑函数、相位、指数积分与连续态相关量。
- **验证与回归**：无独立基准目录；通过 `faclib/` 和 `demo` 计算链的数值稳定性间接验证。
- **已知限制**：部分例程使用 `FFLAGSNO` 编译；源码注释与文献记号可能不同；旧函数名需按实际调用核对。
- **公式核查**：\underline{$F_l\sim\sin\theta_l,\quad G_l\sim\cos\theta_l$}；\underline{$\sigma_l=\arg\Gamma(l+1+i\eta)$}。
- **导航**：父级 [`../README.md`](../README.md)；核心库 [`../faclib/README.md`](../faclib/README.md)。

[返回上级](../README.md)