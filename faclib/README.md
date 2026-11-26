# faclib —— FAC 核心数值库

## 1. 定位

`faclib/` 是 **Flexible Atomic Code（FAC）** 的核心数值库，以 C 语言实现，遵循 **GPL v3+**（每个源文件头部均有 Copyright (C) 2001-2015 Ming Feng Gu 与 GPL 声明）。它实现了**相对论原子结构**以及**各类原子过程的从头计算（ab initio）**：

- 基于 Dirac 方程的自洽场中心势 + 组态相互作用（CI）求能级与波函数；
- 电子碰撞激发（EIE）、电离（EII）；
- 辐射复合（RR）、双电子复合（DR）、自电离（AI）/Auger、电荷交换（CX）；
- 辐射跃迁率（任意多极）、极化率与谱线偏振；
- Dirac R 矩阵（R-matrix）、MBPT（多体微扰论）；
- 碰撞辐射模型（CRM）求解能级布居与谱；
- 二进制数据库/表格读写、通用工具（数组、内存、并行、解析器、FFT、插值）。

### 与上下游的关系

- **上层接口**：
  - `python/`（**pfac**）：通过 SWIG/ctypes 风格绑定暴露本库的 C API；非线程安全，一个 Python 内核只能跑一个算例。
  - `sfac/`：基于简单命令解析器的可执行程序 `sfac`、`scrm`、`spol`，输入语法近似 Python 但无流程控制。
  - 二者都直接调用本目录编译出的 `libfac.a`。
- **底层外部库（多为 Fortran，非 GPL，单独打包 `fac_util.tar.gz`）**：
  - `blas/`、`lapack/`：矩阵对角化与线性代数（`DGEEV`/`DSPEVD`/`DGBSV` 等，见 `f2c.h` 中的 `f_dgeev`、`f_dspevd`、`f_dgbsv` 宏）。
  - `coul/`：Coulomb 函数、Bethe 积分、QED（自能）例程（`DCOUL`、`CMULTIP`、`MOHRFIN`、`GENQED`）。
  - `ode/`：LSODE 常微分方程求解器（CRM 时间演化）。
  - `quadpack/`：自适应积分（`DQAGI`、`DQAGS`、`DQNG`）。
  - `toms/`：插值/拟合（`UVIP3P`、`LMQN`、`SUBPLX`）与特殊函数。
  - `mpfun/`：自 v0.8.6 起为作者自实现的四倍精度算术与连带 Legendre 函数（`DXLEGF`）。
  - `ionis/`：Arnaud&Raymond、Mazzotta 等离子丰度及 Verner 拟合（`IONIS`、`RECOMB`、`RRFIT`、`DRFIT`）。
  - 这些 Fortran 例程通过 **`cf77.h` / `cfortran.h` / `f2c.h` / `f2c.f90`** 桥接为 C 可调用符号（详见第 5 节）。

## 2. 组织形式：按功能域分组

| 功能域 | 主要源文件 |
|---|---|
| 原子结构与轨道/径向/角动量/组态 | `structure.c`, `orbital.c`, `radial.c`, `config.c`, `angular.c`, `recouple.c`, `cfp.c`, `rcfp.c`, `nucleus.c`, `coulomb.c`, `mbpt.c` |
| 电子碰撞激发 | `excitation.c` |
| 电子碰撞电离 | `ionization.c` |
| 复合（RR/DR）与自电离、电荷交换 | `recombination.c` |
| 辐射跃迁率 | `transition.c` |
| 极化率与谱线偏振 | `polarization.c`（极化率系数亦见 `transition.c:PolarizeCoeff`） |
| 碰撞辐射模型 CRM | `crm.c` |
| Dirac R 矩阵 | `rmatrix.c` |
| MBPT | `mbpt.c` |
| 数据库/表格 | `dbase.c`, `interpolation.c`, `errms.h`, `grdcfg.h`, `grdcfg1.h` |
| 通用工具：数组/内存/并行/解析器/FFT/网格 | `array.c`, `pmalloc.c`, `mmalloc.c`, `omalloc.c`, `mpiutil.c`, `parser.c`, `fftsg.c`, `grid.c`, `init.c`, `rates.c` |

文件清单由 `Makefile.in` 的 `SRC` 变量给出，编译为对象文件后 `ar` 归档为 `$(TOPDIR)/libfac.a`；`f2c.o` 在定义 `F2C` 时由 `f2c.f90` 额外编译进库。

## 3. 物理效应章节（核心）

> 说明：以下公式的出处严格标注为 `doc/papers/*.tex`、`doc/manual.tex` 或源码实现；原子单位（a.u.）制下能量用 Hartree、长度用 Bohr、速率用 `RATE_AU`（`consts.h` 中 `4.13413733E16 s⁻¹`）。凡源码未显式给出同一形式常数者均注明"等价实现/需换算"，不作臆造。

### 3.1 相对论原子结构：Dirac 方程、SCF 中心势、能级与 CI 对角化

**简介**：FAC 全程采用相对论框架。多电子哈密顿量在原子单位下为（出处 `doc/papers/structure.tex`，式 `eq_hamilton`）：

$$
H = \sum_{i=1}^{N} H_{D}(i) + \sum_{i<j}^{N}\frac{1}{r_{ij}},\qquad H\Psi = E\Psi
$$

其中 $H_D(i)$ 为单电子 Dirac 哈密顿量。基态/激发态用组态态函数（CSF）$\Phi_\nu$ 展开，混合系数由对角化总哈密顿量得到（出处同上，式 `eq_asf`）：

$$
\psi = \sum_{\nu} b_{\nu}\,\Phi_{\nu},\qquad \Phi_\nu=\mathcal{A}\{\prod \varphi_{n\kappa m}\}
$$

单电子径向轨道由局域中心场 $V(r)$ 下的耦合 Dirac 方程求解（出处 `doc/papers/structure.tex`，式 `eq_dirac`）：

$$
\left(\frac{d}{dr}+\frac{\kappa}{r}\right)P_{n\kappa}=\alpha\left(\varepsilon_{n\kappa}-V+\frac{2}{\alpha^2}\right)Q_{n\kappa},\quad
\left(\frac{d}{dr}-\frac{\kappa}{r}\right)Q_{n\kappa}=-\alpha\left(\varepsilon_{n\kappa}-V\right)P_{n\kappa}
$$

$V(r)=V^N(r)+V^{ee}(r)$，其中 $V^{ee}$ 包含球平均经典势与局域交换（DFS 近似），并含 Breit、自能（SE）、真空极化（VP）等 QED 修正（`eq_nuclear`, `eq_ee`, `eq_nee`）；两电子项按 $1/r_{ij}$ 的张量分解 $X^k(\alpha\beta;\gamma\delta)Z^k\!\cdot\!Z^k$ 计算（`eq_2e`, `eq_yk`）。

**源码对应表**：

| 公式要素 | 文件 | 真实函数/宏 |
|---|---|---|
| 总哈密顿构造、$H\Psi=E\Psi$ 对角化 | `structure.c` | `ConstructHamilton`, `HamiltonElement`, `Hamilton1E`, `Hamilton2E`, `DiagnolizeHamilton`, `GenEigen` |
| CSF 组态、jj 耦合 | `config.c` | `Couple`, `ConfigFromString`, `PackShellState`, `GetKappaFromJL` |
| Dirac 方程求解（SCF 中心势） | `orbital.c` | `RadialSolver`, `RadialDiracCoulomb`, `DiracSmall`, `SetPotentialVc`, `SetPotentialVP`, `SetPotentialSE`, `SetPotentialW`, `SetPotentialZ` |
| Slater/Breit/QED 径向积分 | `radial.c` | `Slater`, `SlaterTotal`, `GetYk`, `Breit`, `BreitX`, `SelfEnergy`, `QED1E`, `OptimizeRadial` |
| 角动量 3j/6j/9j | `angular.c` | `W3j`, `W6j`, `W9j`, `ClebschGordan` |
| 重耦合矩阵元 | `recouple.c` | `AngularZ`, `AngularZxZ0`, `DecoupleShell`, `InteractingShells` |

### 3.2 电子碰撞激发：碰撞强度 $\Omega_{ij}$、截面与 Maxwell 速率系数

**简介**：相对论扭曲波（DW）近似下，EIE 截面与碰撞强度的关系为（出处 `doc/papers/excitation.tex`，`eq` 紧接式 109；原子单位）：

$$
\sigma_{01}=\frac{\pi}{k_0^2 g_0}\,\Omega_{01}
$$

即题目所给 $\sigma_{ij}=\pi a_0^2\Omega_{ij}/[(2J_i+1)k_i^2]$ 的原子单位形式（$g_0=2J_0+1$）。碰撞强度写成分解式（出处同上，式 `eq_cs`/`eq_Qk`/`eq_Pk`）：

$$
\Omega_{01}=2\sum_{k}\sum_{\alpha_0\alpha_1,\beta_0\beta_1}Q^k(\alpha_0\alpha_1;\beta_0\beta_1)\,
\langle\psi_0\|Z^k(\alpha_0,\alpha_1)\|\psi_1\rangle
\langle\psi_0\|Z^k(\beta_0,\beta_1)\|\psi_1\rangle
$$

Maxwell 平均速率系数（等离子体常用形式，$T$ 以 K 计）：

$$
\gamma_{ij}(T)=\frac{8.63\times10^{-6}}{g_i\,T^{3/2}}\,
e^{-E_{ij}/kT}\,\Upsilon_{ij},\qquad \Upsilon_{ij}=\int \Omega_{ij}(E)e^{-E/kT}\,d(E/kT)
$$

**源码实现说明**：`rates.c` 中**没有** $8.63\times10^{-6}$ 字面量；代码在原子单位下计算 `a=2α³e²·strength·RATE_AU`（`rates.c:564–567`），其中 `RATE_AU=_RATE_AU*(m*e4)`、`_RATE_AU=4.13413733E16`（`consts.h:157`、`init.c:123`），即速率 a.u.→s⁻¹ 的换算因子。上式为等价文献写法。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| $\Omega_{ij}$（含 UTA/CB/Born） | `excitation.c` | `CollisionStrength`, `CollisionStrengthUTA`, `CollisionStrengthUTA0`, `CollisionStrengthEB`, `CERadialQk`, `CERadialPk`, `CERadialQkBorn`, `CoulombBetheTail` |
| $\sigma_{ij}$ / 表格插值 | `interpolation.c` | `InterpolateCECross`, `CECross`, `CEFCross` |
| Maxwell 积分与速率系数 | `rates.c`, `interpolation.c`, `consts.h` | `CERate`, `CERate1E`, `IntegrateRate`, `Maxwell`, `MaxwellRC`, `CEMaxwell`, `RATE_AU` |
| 部分波求和/高 $l$ Coulomb-Bethe | `excitation.c` | `PrepCEUTA`, `AllocCECache`, `SetCELMax`, `SetCELCB` |

### 3.3 电子碰撞电离：截面与 Maxwell 速率系数

**简介**：EII 微分截面由 EIE 公式把一个束缚轨道替换为电离电子的自由轨道并对角动量求和得到（出处 `doc/papers/ionization.tex`，式 `eq_cross`, `eq_cs`, `eq_scs`, `eq_total`；原子单位）：

$$
\sigma(\varepsilon_0,\varepsilon)=\frac{1}{k_0^2 g_0}\,\Omega_{01},\qquad
\sigma(\varepsilon_0)=\int_{0}^{(\varepsilon_0-I)/2}\sigma(\varepsilon_0,\varepsilon)\,d\varepsilon
$$

（相对 EIE 缺少因子 $\pi$，源于自由/束缚轨道归一化的差异，见原文说明。）总速率系数同样由 $\sigma$ 与入射电子速度分布卷积得到（`rates.c` 中 `CIRate` / `IntegrateRate`，Maxwell 分布 `Maxwell(e,p)=1.12837967\sqrt{e/T}\,e^{-e/T}/T` 见 `rates.c:1307`；`1.12837967` 是 $2/\sqrt{\pi}=1.128379167\ldots$ 的截断字面量，数值核查记录显示其归一化误差约 $4.5\times10^{-7}$）。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| EII 碰撞强度/微分截面 | `ionization.c` | `IonizeStrength`, `CIRadialQk`, `CIRadialQkIntegrated`, `CIRadialQkBED`, `CIRadialQkMSub` |
| 总截面插值 | `interpolation.c` | `InterpolateCICross`, `TotalCICross`, `TotalPICross`, `CIMCross` |
| Maxwell 速率系数 | `rates.c` | `CIRate`, `CIRate1E`, `VelocityFromE`, `IntegrateRate`, `Maxwell` |
| 表格保存 | `ionization.c` | `SaveIonization`, `SaveIonizationMSub` |

### 3.4 辐射复合 RR 与双电子复合 DR：Maxwell 积分形式的速率系数

**简介**：RR 截面通过 Milne 关系与光电离截面联系（出处 `doc/papers/pirr.tex`，紧接式 87；原子单位）：

$$
\sigma_{PI}=2\pi\alpha\frac{df}{dE},\qquad
\sigma_{RR}=\frac{\alpha^2}{2}\frac{g_i}{g_f}\frac{\omega^2}{\varepsilon(1+0.5\alpha^2\varepsilon)}\,\sigma_{PI}
$$

DR 速率系数（非原子单位出处 `doc/papers/aidr.tex`，式 `eq_rate`）：

$$
\alpha^{DR}(T)=\frac{h^3}{(2\pi m_e k_B T)^{3/2}}\sum_i \frac{g_i}{2g_f}\,
A^a(i\!\to\! f)\,B(i)\,\exp\!\left(-\frac{E_{if}}{k_B T}\right)
$$

其中 $B(i)$ 为辐射分支比（`eq_B`）：$B(i)=\big[\sum_k A^r(i\!\to\!k)+\sum_a A^r(i\!\to\!a)B(a)\big]\big/\big[\sum_{k'}A^a(i\!\to\!k')+\sum_k A^r(i\!\to\!k)+\sum_a A^r(i\!\to\!a)\big]$；DC 强度 $S_{DC}=\frac{g_i}{2g_f}\frac{\pi^2}{E_{if}}A^a$（`doc/papers/aidr.tex:130–132`，该式在论文中未编号）。**CE 的 Maxwell 速率系数**在源码中由 `217.16*sqrt(HARTREE_EV/(2*tms))*exp(-e/temp[t])*Σ` 给出（`CEMFMaxwell`/`CEFMaxwell`/`CEMaxwell`，`interpolation.c:1437,1562,1679`）：`217.16` 是硬编码系数，`tms=temp/bms` 与 `temp[t]` 在源码中是不同变量，不能合并为同一个 $T$。**RR 不同**：`RRMaxwell`（`interpolation.c:2686,2763`）使用 `217.16*sqrt(1/(2*egy[t]))*Σ/(g_f)`，温度为 eV 的 `egy[t]`，无指数因子。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| RR 截面（Milne、类氢 Gaunt） | `recombination.c`, `interpolation.c` | `RRCrossH`, `GauntBF`, `BoundFreeOS`, `RRRadialMultipole`, `RRCrossHn` |
| DR/AI 分支、 DC 强度 | `recombination.c`, `crm.c` | `DROpen`, `AutoionizeRate`, `AutoionizeRateUTA`, `DRBranch`, `DRStrength` |
| RR/DR 速率系数与拟合 | `rates.c` | `RRRate`, `RRRate1E`, `RRRateHydrogenic`, `DRFit`, `RRFit`, `NRRFit`, `NDRFit` |
| 表格插值 | `interpolation.c` | `InterpolateRRCross`, `RRMaxwell`, `RRCross` |

### 3.5 自电离 / 自电离率与 Auger 过程

**简介**：自电离率（原子单位）由 Goldstone 图给出（出处 `doc/papers/aidr.tex`，紧接式 88 与式 99）：

$$
A^{a}=2\sum_{\kappa}\left|\left\langle\psi_f,\kappa;J_TM_T\left|\sum_{i<j}\frac{1}{r_{ij}}\right|\psi_i\right\rangle\right|^2
=2[J_i]^{-1}\sum_{\kappa}\left|\sum_{k,\alpha\gamma\delta}\langle\psi_f,\kappa\|Z^k(\alpha,\gamma)\!\cdot\!Z^k(\kappa,\delta)\|\psi_i\rangle P^k(\kappa\delta;\alpha\gamma)\right|^2
$$

其中 $P^k$ 为径向积分（与 EIE 同形式，只是把一条自由轨道换成束缚轨道）。"Auger 过程"即该内壳层空位退激发的自电离通道，源码以 `AI`（autoionization）统一处理。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| $A^a$ 计算 | `recombination.c` | `AutoionizeRate`, `AutoionizeRateUTA`, `AIRadial1E`, `AIRadialPk`, `PrepAIHeader`, `SaveAI` |
| AI 角系数缓存 | `recombination.c`, `structure.h` | `ProcessAICache`, `AllocAICache`, `ANGULAR_ZFB`, `ANGULAR_ZxZMIX` |
| AI 通道判定 | `dbase.c` | `ChannelAI`, `AIBranch`, `SetInnerAI` |
| AI 分支比 | `crm.c` | `DRBranch`, `SetAIRates`, `SetInnerAuger` |

### 3.6 辐射跃迁：自发辐射率 $A_{ji}$

**简介**：题目给出的长度形式爱因斯坦 A 系数：

$$
A_{ji}=\frac{64\pi^{4}\nu^{3}}{3hc^{3}(2J_j+1)}\,\left|\langle j\|D\|i\rangle\right|^{2}
$$

为公认标准形式；`doc/papers/structure.tex` 摘要仅说明"radiative transition rates are calculated in the single multipole approximation with arbitrary ranks"，`doc/papers/ebfield.tex` 给出 E1 线强 $S_{fi}=\sum_M|\sum_{\mu\nu}b_{f\mu}b_{i\nu}\sum_{\alpha\beta}\langle\phi_\mu\|Z^1_M\|\phi_\nu\rangle\langle\alpha\|C^1\|\beta\rangle M^1_{\alpha\beta}|^2$，并指出振子强度与跃迁率正比于该线强。**源码实际单位制**：`dbase.c:5452 OscillatorStrength` 以原子单位计算，对 E1 有 $gf=\frac{S}{3}\varepsilon$（$\varepsilon$ 为跃迁能，$S$ 为约化线强），并给出 $gA[\text{a.u.}]=2\alpha^{3}\varepsilon^{2}gf$，再由 `RATE_AU` 换算为 s⁻¹；多极阶由 `(aw)^(m2-2)` 给出，关系对各阶成立：

```text
aw = alpha*e;  x = s*s/(m2+1)*e*(aw)^(m2-2);  ga = x*2*(alpha*e)^2*alpha;  // gA (a.u.)
```

`PrintTRTable`（`dbase.c:5523–5525`）再用 `a = ga/(upper.j+1)*RATE_AU` 得到单能级 A（s⁻¹），故 `ga` 是 **gA = (2J_upper+1)·A**，不是单能级 A。原子单位下 $64\pi^4\nu^3/(3hc^3)$ 被吸收到 $\alpha$ 的幂次中。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| $A_{ji}$ / 振子强度换算 | `dbase.c` | `OscillatorStrength` |
| 多极跃迁线强 $S$ | `transition.c` | `TRMultipole`, `TRMultipoleUTA`, `TRMultipoleUTA0I`, `TRMultipoleEB` |
| 阶数/规范/截断设置 | `transition.c` | `SetTransitionMode`, `SetTransitionGauge`, `SetTransitionCut`, `SetOptionTransition` |
| 表格读写 | `dbase.c`, `transition.c` | `PrintTRTable`, `SaveTransition`, `WriteTRRecord`, `ReadTRRecord` |
| 双光子跃迁率 | `dbase.c` | `TwoPhotonRate` |

### 3.7 极化率与谱线偏振（polarization.c）

**简介**：外电场/磁场下的哈密顿量修正为 $H_E=\sum_i\mathbf{E}\cdot\mathbf{r}_i$（出处 `doc/papers/ebfield.tex:55–70`）。**核查说明**：该论文**未给出**二次 Stark 位移 $\Delta E=-\tfrac12\alpha_d|\mathbf{E}|^2$；`structure.c:HamiltonElementEB`（`:1367–1373`）是把 $\mathbf{E}\cdot\mathbf{r}$ 矩阵元直接加入哈密顿量并显式对角化，源码中**没有** $-\tfrac12\alpha_d E^2$ 项，也未在结构计算链中调用 `PolarizeCoeff`。`PolarizeCoeff` 是 `transition.c` 中独立的极化率系数函数，与外场结构求解不是同一路径。

谱线偏振度的初等定义常写作 $P=(I_{\parallel}-I_{\perp})/(I_{\parallel}+I_{\perp})$，但 **FAC 源码输出不是该字面比值**：`PolarizationTable`（`polarization.c:2098–2102`）输出第 7、8 列分别为 $b$、$a$，即

$$
P_{\rm FAC}=\frac{a}{b}
=\frac{\sum_t F_t\,PL2_t\,A_t\,B_t}{\sum_t PL_t\,A_t\,B_t},\qquad PL_t=P_{2t}(\cos\theta)
$$

其中 $PL_t$ 由 `DXLEGF` 得到，$PL2_t$ 为 $\mu=2$ 的缔合 Legendre 项且 $PL2_0=0$，$A_t$ 由 Wigner 3j/6j 给出，$F_t$ 在 $k<0$ 时变号（`polarization.c:2087–2091`）。该球张量比值是偏振度的角动量实现，符号与归一化以 `polarization.c` 为准，**不要**直接等同于 $I_\parallel/I_\perp$ 的初等定义。磁子能级布居系数 $B_k(J)$ 的实现在 `polarization.c:1798–1816`（不是 1682–1697）。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| 偏振度 $P$、$\parallel/\perp$ 强度比 | `polarization.c` | `PolarizationTable`, `Orientation` |
| 磁子能级布居求解 | `polarization.c` | `SetMLevels`, `PopulationTable`, `SetMIteration`, `SetIDR` |
| 磁子能级 CE/AI/CI 速率 | `polarization.c` | `SetMCERates`, `SetMAIRates`, `SetMCIRates` |
| 极化率系数（α） | `transition.c` | `PolarizeCoeff` |
| 微扰/场哈密顿矩阵元 | `structure.c` | `SetFields`, `GetFields`, `HamiltonElementEB` |

### 3.8 碰撞辐射模型（crm.c）：速率方程组与稳态求解

**简介**：CRM 求解各电荷态/能级的布居方程（题目给定形式，也是标准 form）：

$$
\frac{dn_i}{dt}=\sum_{j}n_j R_{ji}-n_i\sum_j R_{ij}
$$

其中 $R_{ij}$ 包含电子碰撞激发/电离、辐射复合、自电离、电荷交换、辐射跃迁等速率系数乘以相应密度（电子密度 `electron_density` 单位 $10^{10}\,\mathrm{cm^{-3}}$，光子密度 `photon_density` 单位 erg·cm⁻³，见 `crm.c:54-60`）。源码把每个 ion 的能级按 block 组织，`total_rate[j]` 累加第 $j$ 能级的流出率，`bmatrix` 存放速率矩阵，通过 `BlockRelaxation`/`LevelPopulation` 迭代到稳态（$\frac{dn_i}{dt}=0$）；含辐射级联 `Cascade`。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| 布居方程、稳态迭代 | `crm.c` | `BlockMatrix`, `BlockPopulation`, `BlockRelaxation`, `LevelPopulation`, `Cascade` |
| 速率矩阵/流率累加 | `crm.c` | `AddRate`, `SetBlocks`, `InitBlocks`, `total_rate`（结构体字段）, `bmatrix` |
| 各类速率装载 | `crm.c` | `SetCERates`, `SetCIRates`, `SetRRRates`, `SetAIRates`, `SetTRRates`, `SetCXRates` |
| 外推/线表/谱 | `crm.c` | `ExtrapolateTR`, `ExtrapolateRR`, `ExtrapolateAI`, `RateTable`, `SpecTable`, `PlotSpec` |
| 数据结构 | `crm.h` | `ION`, `LBLOCK`, `RATE`, `LINEREC` |

### 3.9 Dirac R 矩阵（rmatrix.c）基本方程

**简介**：源码实现的是**内部区域 R 矩阵方法 + Buttle 外推 + 外部区域传播**的标准流程：在边界半径 $a$ 处由表面振幅构造 R 矩阵（标准 Wigner 形式为 $R_{ij}(a,E)=\dfrac{w_i(a)w_j(a)}{2a\,[E-E_i]}$），经 `RMatrixPropogate` 传播到渐近区，`RMatrixKMatrix` 得到 K 矩阵，`SMatrix` 得到 S 矩阵，由此给出碰撞强度/截面（`RMatrixCE`）。**核查说明**：`rmatrix.c` 中**未找到**该极点和的字面公式；源码在 `RMatrixBoundary`（`:422`）、`RMatrixBasis`（`:531`）、`RMatrixSurface`（`:1379`）中构造并保存表面振幅 `wik0/wik1`，在 `RMatrixCEW`（`:3954`）中对角化并匹配。`doc/papers/` 无 R 矩阵专文，上式仅为标准理论与源码函数流程的对应说明，归一化以源码为准。

**源码对应表**：

| 公式要素 | 文件 | 真实函数 |
|---|---|---|
| R 矩阵（边界处） | `rmatrix.c` | `RMatrix`, `RMatrixBoundary`, `PrepDiracCoulomb`, `IntegrateDiracCoulomb` |
| Buttle 基/外推 | `rmatrix.c` | `RMatrixBasis`, `ExtrapolateButtle`, `GailitisExp` |
| 外部传播 | `rmatrix.c` | `RMatrixPropogate`, `PropogateExternal`, `IntegrateExternal`, `TransformQ` |
| K/S 矩阵与碰撞强度 | `rmatrix.c` | `RMatrixKMatrix`, `SMatrix`, `RMatrixCE`, `RMatrixCEW`, `SaveRMatrixCE` |
| 数据结构 | `rmatrix.h` | `RMATRIX`, `RBASIS`, `SMATRIX`, `RMXCE`, `DCFG` |

### 3.10 MBPT（mbpt.c）基本方程

**简介**：FAC 的 MBPT 以 CI 波函数为 $P$ 空间，把 $Q$ 空间（单、双激发）贡献折叠为**有效哈密顿量**：

$$
H_{\mathrm{eff}}(E)=H_{PP}+H_{PQ}\frac{1}{E-H_{QQ}}H_{QP},\qquad
(H_{PP}+H_{\mathrm{eff}})\Psi=E\Psi
$$

**核查说明**：`MBPT_EFF` 是数据结构而非上述公式；`mbpt.c:5800–5815` 实际以 `a=h0[k]`、`b=SumInterpH(...,hab,...)`、`heff[m]=a+b` 构造有效哈密顿，二/三阶修正的分母形如 `de*(de+e0[i]-e0[ib])`（`H3rd0:1971,1986`），能量依赖部分由 `SumInterpH`（`:1857–1889`）插值。上式是 Bloch 有效哈密顿的**标准形式**，源码未出现该 LaTeX 式；跃迁算符修正由 `MBPT_TR`/`MBPT_PMA`（`tma`, `rma`）表达。严格系数以源码实现为准。

**源码对应表**：

| 公式要素 | 文件 | 真实函数/结构 |
|---|---|---|
| 有效哈密顿构造 | `mbpt.c` | `StructureMBPT0`, `StructureMBPT1`, `SetExtraMBPT`, `SetOptMBPT`, `AdjustAngularZ` |
| $H_{\mathrm{eff}}$ 矩阵元 | `mbpt.c`, `mbpt.h` | `MBPT_EFF`（`heff`, `heff0`, `hab`, `hab1`…） |
| 跃迁算符修正 | `mbpt.c`, `mbpt.h` | `TransitionMBPT`, `TRTableMBPT`, `SaveTransitionMBPT`, `MBPT_TR`, `MBPT_PMA` |
| 对称性解包/角系数 | `mbpt.c` | `UnpackSymStateMBPT`, `UnpackSymStateTR`, `AngZCutMBPT` |

## 4. 逐文件说明（30 个 `.c` + 38 个 `.h`，无遗漏）

### 4.1 源文件 `.c`（30 个）

1. **`angular.c`** — 类型：角动量；功能：Wigner 3j/6j/9j、Clebsch-Gordan、Wigner-Eckart 因子，源自 Gaigalas et al. CPC 139 (2001) 263（对 3j 改进以避免大角动量溢出）；关键函数：`InitAngular`, `Triangle`, `W3j`, `W6j`, `W9j`, `WignerEckartFactor`, `ClebschGordan`, `ReducedCL`, `WignerDMatrix`；依赖：被 `config.c`/`recouple.c`/`structure.c`/`transition.c` 调用，依赖 `ln_factorial` 表。
2. **`array.c`** — 类型：通用容器；功能：变长一维 `ARRAY` 与多维 `MULTI` 数组（三种实现 S/N/M），哈希索引、矩阵；关键函数：`ArrayInit`, `ArrayGet`, `ArraySet`, `ArrayAppend`, `NMultiInit/Get/Set`, `SMultiInit/Get/Set`, `MMultiInit`, `Hash2`, `InitMatrix`, `MatMulV`；被几乎所有模块使用。
3. **`cfp.c`** — 类型：角动量（历史遗留）；功能：查表给出 $j\le 9/2$ 相对论子壳层分数父系数（源自 de-Shalit & Talmi《Nuclear Shell Theory》1963）；关键函数：`CFP`, `GetIndex`；依赖：头文件注明"已不再使用，改用 `rcfp.c`"。
4. **`config.c`** — 类型：组态；功能：电子组态生成、子壳层占用、jj 耦合、对称性与组态组管理、组态名构造、UTA/非相对论模式；关键函数：`GetConfigFromString`, `Couple`, `GetAverageConfig`, `AddGroup`, `AddStateToSymmetry`, `ExciteConfig`, `ConfigUTA`, `ShellsFromString`；依赖 `array/nucleus/dbase/parser`，被 `structure/radial/orbital` 调用。
5. **`coulomb.c`** — 类型：原子物理（类氢）；功能：类氢偶极/期望值/自能、Coulomb 相位与 Bethe 高角动量近似、Gaunt 因子；关键函数：`InitCoulomb`, `HydrogenicDipole`, `HydrogenicExpectation`, `HydrogenicSelfEnergy`, `TRRateHydrogenic`, `CoulombPhaseShift`, `PrepCoulombBethe`, `CoulombBethe`, `GauntHummer`, `GauntIFF`；依赖 `orbital/radial/grid/angular`。
6. **`crm.c`** — 类型：CRM；功能：离子/能级块装配、速率矩阵、稳态布居迭代、谱表与线宽（Stark/微观场）、DR 分支；关键函数（函数族）：`InitCRM0/1`, `AddIon`, `SetBlocks`, `InitBlocks`, `SetCERates/SetCIRates/SetRRRates/SetAIRates/SetTRRates/SetCXRates`, `BlockMatrix`, `BlockPopulation`, `BlockRelaxation`, `LevelPopulation`, `Cascade`, `SpecTable`, `DRBranch`, `SetOptionCRM`；依赖 `dbase/rates/interpolation/coulomb`；被 `sfac/scrm`、`python` 调用。
7. **`dbase.c`** — 类型：数据库/表格；功能：全部二进制表（EN/TR/CE/RR/AI/CI/SP/RT/DR/RO/CX/RC 等）读写、打印、字节序交换、表合并、振子强度/双光子率；关键函数族：`ReadENHeader/Record`, `ReadCERecord`, `WriteTRRecord`, `PrintTable`, `OscillatorStrength`, `OpenFile`, `JoinDBase`, `PreloadCE`, `TwoPhotonRate`, `SetOptionDBase`；被所有过程模块与上层接口调用。
8. **`excitation.c`** — 类型：EIE（超大文件）；功能：按函数族分组——(a) 缓存：`AllocCECache/FreeCECache/ProcessCECache`；(b) 网格/选项：`SetCETEGrid/SetCEEGrid/SetAngleGrid/SetCEQkMode/SetCEBorn/SetOptionExcitation`；(c) 径向积分：`CERadialPk`, `CERadialQk`, `CERadialQkBorn`, `CERadialQkBornMSub`, `CERadialQkFromFit`；(d) 碰撞强度：`CollisionStrength`, `CollisionStrengthUTA`, `CollisionStrengthUTA0`, `CollisionStrengthEB`, `CollisionStrengthEBD`；(e) 输出：`SaveExcitation`, `SaveExcitationEB`, `SaveExcitationEBD`；(f) 生命周期：`InitExcitation`, `ReinitExcitation`；依赖 `coulomb/structure/transition`。
9. **`fftsg.c`** — 类型：数值（FFT，Ooura 实现）；功能：复数/实数 FFT、DCT/DST；关键函数：`cdft`, `rdft`, `ddct`, `ddst`, `dfct`, `dfst`；被 `orbital.c` 等调用。
10. **`grid.c`** — 类型：数值网格；功能：部分波 $\ell$、碰撞能量、能量、线性网格构造；关键函数：`AddPW`, `SetPWGrid`, `SetTEGrid`, `SetTEGridDetail`, `SetEGrid`, `SetLinearGrid`；被 `excitation/ionization/recombination` 调用。
11. **`init.c`** — 类型：初始化/总控；功能：一次性/分步初始化所有子模块、选项分发、轻子（lepton）种类设置；关键函数：`InitFac0`, `InitFac1`, `ReinitFac`, `Initialized`, `Info`, `SetOption`, `SetOptionGlobal`, `SetLepton`；include 几乎所有模块头。
12. **`interpolation.c`** — 类型：插值/拟合/后处理（大文件）；功能：样条、SVD/非线性拟合、Simpson/Newton-Cotes、Maxwell 卷积、各类截面转速率系数与表格处理；关键函数族：`spline/splint`, `SVDFit`, `NLSQFit`, `MaxwellRC`, `CEMaxwell/CIMaxwell/RRMaxwell`, `InterpolateCECross`, `TotalCICross`, `CECross`, `voigt`, `ModifyTable`；依赖 `dbase/array/consts`。
13. **`ionization.c`** — 类型：EII；功能：直接电离径向积分（DW/CBE/BED）、$\bar Q^k$ 对电离能的插值、MSub 输出；关键函数：`IonizeStrength`, `CIRadialQk`, `CIRadialQkIntegrated`, `CIRadialQkBED`, `CIRadialQkMSub`, `SaveIonization`, `PrepCIHeader`, `InitIonization`；依赖 `structure/excitation/recombination`。
14. **`mbpt.c`** — 类型：MBPT（超大文件）；功能：有效哈密顿、二/三阶关联、虚轨道激发组、跃迁算符微扰；关键函数族：`InitMBPT`, `StructureMBPT0/1`, `StructureReadMBPT`, `TransitionMBPT`, `TRTableMBPT`, `SetOptMBPT`, `SetExcMBPT`, `SetOptionMBPT`；依赖 `dbase/structure/transition/cf77`。
15. **`mmalloc.c`** — 类型：内存；功能：简易 `malloc/calloc/realloc/free` 包装（默认 `PMALLOC==0` 时通过 `global.h` 生效），含 `msize` 统计；关键函数：`mmalloc`, `mcalloc`, `mrealloc`, `mfree`, `mmsize`, `dmsize`；宏定义见 `mmalloc.h`。
16. **`mpiutil.c`** — 类型：并行/缓冲工具；功能：MPI/OpenMP 抽象（`SkipWMPI`, `MPrintf`, 锁、wid 工作分配）、缓冲文件 `BFILE`、排序/随机数、Landau-Zener 分布；关键函数：`InitializeMPI`, `MPIRank`, `MyRankMPI`, `BFileOpen/Read/Write/GetLine`, `RandList`, `SortUnique`, `LandauZenerLD`；`global.h` 把 `FOPEN/FGETS/...` 映射到 `BFile*`。
17. **`nucleus.c`** — 类型：原子物理（核）；功能：核半径/Fermi 分布、元素符号与质量表、电荷分布、额外势、CX 靶、基态性质查询；关键函数：`InitNucleus`, `NucleusRadius`, `SetupFermi`, `FermiParamC`, `SetAtom`, `GetAtomicMassTable`, `GetGroundIP`, `SetCXTarget`；依赖 `interpolation`。
18. **`omalloc.c`** — 类型：内存；功能：使用外部 malloc 库（tcmalloc/jemalloc，`PMALLOC==2/3`）时的 `omsize` 统计；关键函数：`omsize`；由 `omalloc.h` 在 `1<=PMALLOC<10` 时引入。
19. **`orbital.c`** — 类型：轨道/中心势（大文件）；功能：SCF 势构造（$V_c$、VP、SE、交换、自由电子密度/有限温度 Fermi）、Dirac 方程数值求解、束缚/连续/Sturm/Rydberg 轨道；关键函数族：`SetPotentialVc/VT/VP/SE/U/W`, `RadialSolver`, `RadialBound`, `RadialFree`, `RadialSturm`, `DrLargeSmall`, `FermiIntegral`, `FreeElectronDensity`, `SetOrbitalRGrid`；依赖 `fftsg/global/mpiutil`。
20. **`parser.c`** — 类型：通用工具；功能：字符串分割/去空白/引号与转义处理/大小写转换；关键函数：`StrSplit`, `QuotedStrSplit`, `StrTrim`, `Parse`, `SetParserQuote`, `StrReplace`, `StrLower/Upper`；被 `sfac` 与 `dbase.c` 使用。
21. **`pmalloc.c`** — 类型：内存；功能：带文件名/行号追踪的调试型分配器（`PMALLOC>=10`）；关键函数：`pmalloc`, `pcalloc`, `prealloc`, `pfree`, `pmsize`, `pmalloc_check`；宏见 `pmalloc.h`。
22. **`polarization.c`** — 类型：谱线偏振；功能：磁子能级布局求解、取向（orientation）、偏振度表；关键函数：`InitPolarization`, `SetMLevels`, `PopulationTable`, `Orientation`, `PolarizationTable`, `SetMCERates/MAIRates/MCIRates`, `SetOptionPolarization`；依赖 `dbase/rates/interpolation/cf77`。
23. **`radial.c`** — 类型：径向积分（超大文件，约 357 KB）；功能：按函数族分组——(a) 势/SCF：`SetPotential`, `PotentialHX`, `OptimizeRadial`, `SolvePseudo`, `AverageAtom`, `PlasmaScreen`；(b) 轨道表：`SolveDirac`, `OrbitalIndex`, `GetOrbital`, `AddOrbMap`；(c) 径向积分：`GetYk`, `Integrate`, `Slater`, `SlaterTotal`, `MultipoleRadialFR`, `GeneralizedMoments`；(d) QED/Breit：`SelfEnergy`, `QED1E`, `Breit`, `BreitX`；(e) I/O：`SavePotential`, `RestorePotential`, `SaveRadialMultipole`；(f) 生命周期：`InitRadial`, `ReinitRadial`, `SetOptionRadial`；依赖 `orbital/config/coulomb/recouple/angular`。
24. **`rates.c`** — 类型：速率系数；功能：电子/光子/电荷交换分布管理、速率积分、CE/CI/RR 速率、外部拟合（Beli/Kronos/Verner）；关键函数族：`SetEleDist/CxtDist/PhoDist`, `IntegrateRate/IntegrateRate2`, `CERate`, `CIRate`, `RRRate`, `CXRate`, `TRRate`, `RRRateHydrogenic`, `RRFit/DRFit/Ionis/Recomb`, `InitRates`；依赖 `dbase`。
25. **`rcfp.c`** — 类型：角动量；功能：约化分数父系数、产生/湮灭算子的约化矩阵元（Gaigalas et al. CPC 139 (2001) 263）；关键函数：`ReducedCFP`, `ReducedW`, `ReducedA`, `ReducedAxW`, `ReducedWxA`, `CompleteReducedW`, `ClebschGordanQuasispin`；依赖 `angular`。
26. **`recombination.c`** — 类型：RR/DR/AI/CX（大文件）；功能：按函数族分组——(a) RR：预制备：`SetRRTEGrid`, `RRRadialQk`, `RRRadialMultipole`, `TopUpRRRadialQk`, `BoundFreeOS`, `SaveRecRR`；(b) AI/DC：`AIRadialPk`, `AutoionizeRate`, `PrepAIHeader`, `SaveAI`, `DROpen`；(c) CX：`LandauZenerCX`, `SaveCX`；(d) 网格/选项：`SetPEGrid`, `SetRecQkMode`, `SetRecSpectator`, `SetOptionRecombination`；(e) 生命周期：`InitRecombination`, `ReinitRecombination`；依赖 `structure/excitation/transition/coulomb`。
27. **`recouple.c`** — 类型：角动量；功能：重耦合系数、相互作用壳层判定、$Z^k$ 与 $Z^k\!\cdot\!Z^{k'}$ 约化矩阵元、拓扑公式；关键函数：`DecoupleShell`, `AngularZ`, `AngularZxZ0`, `GetInteract`, `InteractingShells`, `GenerateFormula`, `EvaluateTensor`, `InitRecouple`；依赖 `config/angular/rcfp`；被 `structure/radial` 调用。
28. **`rmatrix.c`** — 类型：R 矩阵（大文件）；功能：Buttle 基构造/外推、边界 R 矩阵、外部传播、K/S 矩阵、碰撞强度；关键函数族：`RMatrixBasis`, `ExtrapolateButtle`, `RMatrixBoundary`, `RMatrix`, `RMatrixPropogate`, `RMatrixKMatrix`, `SMatrix`, `GailitisExp`, `RMatrixCE`, `SetOptionRMatrix`；依赖 `structure/radial`。
29. **`structure.c`** — 类型：原子结构/CI（超大文件，约 176 KB）；功能：按函数族分组——(a) 对称性/布居：`SetSymmetry`, `SetCILevel`, `FlagClosed`, `AddToLevels`, `SortLevels`；(b) 哈密顿：`ConstructHamilton`, `ConstructHamiltonDiagonal`, `ConstructHamiltonFrozen`, `HamiltonElement`, `Hamilton1E/2E`, `HamiltonElementFB`；(c) 角系数：`AngularZMix`, `AngularZxZMixStates`, `AddToAngularZxZ`, `PrepAngular`；(d) 对角化：`DiagnolizeHamilton`, `GenEigen`；(e) I/O：`ReadHamilton`, `WriteHamilton`, `SaveLevels`；(f) 生命周期：`InitStructure`, `ReinitStructure`, `SetOptionStructure`；依赖 `config/radial/recouple/rcfp/dbase`。
30. **`transition.c`** — 类型：辐射跃迁；功能：多极线强（含 UTA、EB 场）、振子强度、输出；关键函数：`TRMultipole`, `TRMultipoleUTA`, `TRMultipoleUTA0I`, `TRMultipoleEB`, `PolarizeCoeff`, `SaveTransition`, `SetTransitionMode`, `SetOptionTransition`；依赖 `structure/angular/config`。

> 注：用户提示中提到的 `fac.c`、`cmultip` 不在本目录（`fac.c` 属 `sfac/`，`cmultip` 属 `coul/`），故不作条目。

### 4.2 头文件 `.h`（38 个）

1. **`angular.h`** — 声明 3j/6j/9j、CG、Wigner-Eckart 等；宏 `LnFactorial`, `MAX_FACTORIAL`；被 `coulomb/config/recouple/radial/structure/transition/recombination/init` 包含。
2. **`array.h`** — 定义 `DATA`, `ARRAY`, `MULTI`, `IDXARY`, `MATRIX`；`USE_NMULTI` 选择 `MultiInit/Get/Set` 实现；几乎所有模块包含。
3. **`cf77.h`** — C↔Fortran 桥接总头：`MOD_F2C` 时包含 `f2c.h`，否则包含 `cfortran.h` 并用 `PROTOCCALLSFFUN*`/`CCALLSFFUN*` 声明 ERF/FM5P/… 等符号；被所有调用 Fortran 的 `.c` 包含。
4. **`cfp.h`** — 旧分数父系数 `CFP`, `GetIndex` 声明（历史遗留）。
5. **`config.h`** — 定义 `SHELL`, `SHELL_STATE`, `CONFIG`, `AVERAGE_CONFIG`, `CONFIG_GROUP`, `STATE`, `SYMMETRY` 及大量组态函数；被 `orbital/radial/structure/transition/recombination/init` 包含。
6. **`consts.h`** — 物理常数与全局开关：`VERSION`, `PI`, `HARTREE_EV`, `RATE_AU`（`4.13413733E16`），`QK_*`、`G_COULOMB/G_BABUSHKIN`、`WCOEF`（CRM 速率→线宽）等；被 `global.h` 包含。
7. **`coulomb.h`** — 类氢与 Coulomb-Bethe 函数声明（`NucleusRRMS`, `HydrogenicDipole`, `CoulombBethe`, `Gaunt*`）。
8. **`crm.h`** — 定义 `RECOMBINED`, `LBLOCK`, `BLK_RATE`, `ION`, `IONIZED`, `RATE`, `LINEREC`, `INTERPSP` 及 CRM API；包含 `array/dbase/rates/nucleus/interpolation/coulomb/init`。
9. **`dbase.h`** — 数据库核心头：记录类型宏 `DB_EN..DB_CX`（`NDB=18`）、`F_HEADER` 及各 `*_HEADER/*_RECORD` 结构，读写/打印 API；被所有过程模块包含。
10. **`errms.h`** — `SETUPERRMS` 宏，初始化误差函数表 `_errms[][]`（数值常量表，供统计/拟合使用）。
11. **`excitation.h`** — `CEPW_SCRATCH`, `CEPK`, `CEPKK`, `CEQKK`, `CECACHE` 结构与 EIE API；包含 `coulomb/structure/transition`。
12. **`f2c.h`** — 由 `genf2c.py` 从 `cf77.h` 生成：Fortran 符号的 `extern f_*` 声明与 `#define` 别名（`ERF→f_erf`, `DGEEV→f_dgeev`, `LSODE→f_lsode`, `DQAGI→f_dqagi`, `IONIS→f_ionis` 等）。
13. **`fftsg.h`** — FFT 原型：`cdft`, `rdft`, `ddct`, `ddst`, `dfct`, `dfst`。
14. **`global.h`** — 全局头：包含标准头、`sysdef.h`、按 `PMALLOC` 选内存头、`USE_MPI` 选 `mpi.h`/omp、锁宏 `LOCK/SetLock/...`、`TFILE`→`BFILE` 映射、`FOPEN/FGETS/...` 宏、调试标志、尾部声明 `UTAGrid`, `RelativisticMaxwell`, `SetXCEMode` 等。
15. **`grdcfg.h`** — 超大数据表头（约 428 KB）：`SETUPGROUND` 等宏，内含各元素基态电离能/组态常量数组（如 `_ipot`）。
16. **`grdcfg1.h`** — 超大数据表头（约 539 KB）：扩展的基态/组态数据宏表（如 `SETUPGROUND` 的补充表），供 `nucleus.c` 构建基态信息。
17. **`grid.h`** — 网格函数原型（`SetPWGrid`, `SetTEGrid`, `SetEGrid`, `SetLinearGrid` 等）。
18. **`init.h`** — 总初始化 API：`InitFac0/1`, `ReinitFac`, `Initialized`, `Info`, `SetOption`, `SetLepton`；包含全部模块头。
19. **`interpolation.h`** — `MOD_RECORD` 结构与样条/拟合/积分/截面转速率 API（`spline`, `SVDFit`, `MaxwellRC`, `CEMaxwell`, `RRMaxwell`, `voigt` 等）。
20. **`ionization.h`** — EII API：`IonizeStrength`, `CIRadialQk*`, `SetCIPWOptions`, `SaveIonization`, `BEScale` 等；包含 `structure/excitation/recombination`。
21. **`mbpt.h`** — `TR_OPT`, `MBPT_EFF`, `MBPT_PMA`, `MBPT_TR`, `CORR_CONFIG`, `MBPT_HAM`, `CONFIG_PAIR` 结构与 MBPT API（`StructureMBPT0/1`, `TransitionMBPT`, `SetOptMBPT` 等）。
22. **`mmalloc.h`** — 简易分配器宏：`#define malloc mmalloc` 等，`mmalloc/mcalloc/mrealloc/mfree/mmsize` 原型。
23. **`mpiutil.h`** — `RANDIDX`, `PTRIDX`, `MPID`, `BFILE` 结构与并行/缓冲/排序 API（`MPIRank`, `MPrintf`, `BFileOpen`, `RandList`, `SortUnique`, `LandauZenerLD`）。
24. **`nucleus.h`** — `NUCLEUS`, `CXTGT` 结构与核/元素数据 API（`InitNucleus`, `NucleusRadius`, `GetGroundIP`, `SetCXTarget` 等）。
25. **`omalloc.h`** — 外部分配器（tcmalloc/jemalloc）头，`omsize` 声明；按 `PMALLOC==2/3` 引入。
26. **`orbital.h`** — `POTENTIAL`, `ORBITAL` 结构（含 $V_c,V^{ee}$, VP/SE/Breit、Fermi 场等字段）与轨道求解 API（`RadialSolver`, `SetPotential*`, `RadialFree`, `DiracSmall`, `SetOptionOrbital` 等）。
27. **`parser.h`** — 字符串/解析函数原型（`StrSplit`, `Parse`, `SetParserQuote`, `StrLower/Upper` 等）。
28. **`pmalloc.h`** — 调试分配器宏（带 `__FILE__/__LINE__`）：`pmalloc/pcalloc/prealloc/pfree/pmsize` 等。
29. **`polarization.h`** — `MLEVEL`, `MTR`, `MCE`, `MAI`, `MCI`, `MLINE` 结构与偏振 API（`InitPolarization`, `Orientation`, `PolarizationTable` 等）。
30. **`radial.h`** — `ORBMAP` 结构与径向/SCF/QED 积分 API（`SolveDirac`, `SetPotential`, `GetYk`, `Slater`, `Breit`, `SelfEnergy`, `OptimizeRadial`, `SetOptionRadial` 等）。
31. **`rates.h`** — `DISTRIBUTION`, `KRONOS` 结构与速率分布/积分 API（`SetEleDist`, `IntegrateRate`, `CERate`, `RRRate`, `Ionis`, `Recomb`, `UVoigt` 等）；`RT_CE/CI/RR/CX` 宏。
32. **`rcfp.h`** — `RCFP_STATE`, `RCFP_TERM`, `REDUCED_COEFF`, `RCFP_OPERATOR` 结构与约化 CFP API（`ReducedCFP`, `ReducedW`, `ReducedA`, `CompleteReducedW*` 等）。
33. **`recombination.h`** — `REC_COMPLEX`, `AICACHE` 结构与 RR/AI/CX API（`RRRadialQk`, `BoundFreeOS`, `AutoionizeRate`, `DROpen`, `LandauZenerCX`, `SetOptionRecombination` 等）。
34. **`recouple.h`** — `INTERACT_SHELL`, `INTERACT_DATUM`, `FORMULA`, `TRIADS` 与重耦合 API（`AngularZ`, `AngularZxZ0`, `DecoupleShell`, `GetInteract`, `RecoupleTensor` 等）；`MAXJ/MAXNJGD`。
35. **`rmatrix.h`** — `RBASIS`, `RMATRIX`, `SMATRIX`, `RMXCE`, `DCFG` 结构与 R 矩阵 API（`RMatrix`, `RMatrixBasis`, `RMatrixKMatrix`, `SMatrix`, `RMatrixCE` 等）。
36. **`structure.h`** — `HAMILTON`, `LEVEL`, `SHAMILTON`, `ANGULAR_ZMIX`, `ANGULAR_FROZEN` 等核心结构与 CI API（`ConstructHamilton`, `DiagnolizeHamilton`, `AddToLevels`, `AngularZMix`, `SetOptionStructure` 等）。
37. **`transition.h`** — 跃迁设置与线强 API（`SetTransitionMode/Gauge/Cut`, `TRMultipole`, `TRMultipoleUTA`, `SaveTransition`, `PolarizeCoeff`, `SetOptionTransition`）。
38. **`cfortran.h`** — 第三方 cfortran 工具头（约 126 KB）：提供 `PROTOCCALLSFFUN*`/`CCALLSFFUN*`/`PROTOCCALLSFSUB*` 等宏，实现 C 调用 Fortran 的 ABI 桥接；用法见 `cfortran.doc`。

## 5. 接口说明

### C API 命名规律

- `InitXxx()` / `ReinitXxx(int m)`：模块初始化与多实例重初始化（`InitFac0/1`, `InitRadial`, `InitStructure`, `InitExcitation`, `InitRecombination`, `InitIonization`, `InitRMatrix`, `InitPolarization`, `InitCRM0/1`, `InitDBase`, `InitRates`）。
- `SetXxx(...)`：参数设置/网格/选项；统一尾部 `SetOptionXxx(char *s, char *sp, int ip, double dp)` 供脚本解析器按字符串分发。
- `GetXxx()`：查询/取值（`GetLevel`, `GetHamilton`, `GetOrbital`, `GetNumLevels` 等）。
- 动作函数：`SolveStructure`, `DiagnolizeHamilton`, `CollisionStrength`, `IonizeStrength`, `AutoionizeRate`, `RMatrixCE`, `BlockRelaxation` 等。
- 保存/读取：`SaveXxx`, `ReadXxxHeader/Record`, `WriteXxxHeader/Record`, `PrintXxxTable`。

### f2c/cfortran 桥接

- 默认路径：源文件 `#include "cf77.h"` → 包含 `cfortran.h`（第 3 方宏），把 Fortran 例程声明为 `CCALLSFFUN*/CCALLSFSUB*`（如 `ERF`, `FM5P`, `DCOUL`, `DQAGI`, `DGEEV`, `LSODE`, `RRFIT`, `IONIS`）。
- 可选路径（`MOD_F2C`）：`#include "f2c.h"` → 符号重定向为 `f_*`；`genf2c.py` 读取 `cf77.h` 自动生成 `f2c.h`（C 侧 extern 声明 + `#define`）与 `f2c.f90`（Fortran `iso_c_binding` + `bind(C)` 包装，如 `function f_erf(a0) bind(C,name='f_erf')`）。`Makefile.in` 在定义 `F2C` 时把 `f2c.o` 链入 `libfac.a`。
- 支持编译器配置见 `cfortran.doc` 与顶层 `README`。

### 关键数据结构

- `LEVEL`（`structure.h`）：某 $J^\pi$ 对称性下的一条能级——`energy`, `mixing[]`, `basis[]`, `pj`, `nele`, `iham`；由 `DiagnolizeHamilton` + `AddToLevels` 产生，被过程模块以整数下标引用。
- `CONFIG` / `SHELL` / `SHELL_STATE`（`config.h`）：组态与子壳层（$n,\kappa$、占据数、seniority）。
- `HAMILTON`（`structure.h`）：CI 哈密顿（`hamilton[]`, `mixing[]`, `basis[]`, 维数与对角化工作区）；`SHAMILTON` 为对称性容器。
- `ARRAY` / `MULTI` / `MATRIX`（`array.h`）：动态数组与稀疏矩阵，是 FAC 一切大表（角系数、径向积分、速率）的底座。
- `POTENTIAL` / `ORBITAL`（`orbital.h`）：SCF 中心势与 Dirac 轨道（大/小分量 `wfun`）。
- `DBASE` 相关（`dbase.h`）：`F_HEADER` + 各 `*_HEADER/*_RECORD`（`EN_RECORD`, `TR_RECORD`, `CE_RECORD`, `RR_RECORD`, `AI_RECORD`, `CI_RECORD`, `SP_RECORD`, `DR_RECORD`…），`NDB=18` 张表；可直接复制 `consts.h/dbase.h/dbase.c` 到外部代码读取二进制结果。
- `ION` / `LBLOCK`（`crm.h`）：CRM 的电荷态-能级块与速率集合。
- `RMATRIX` / `RBASIS`（`rmatrix.h`）、`MBPT_EFF` / `MBPT_TR`（`mbpt.h`）。

## 6. 上下游、构建与导航

- **构建**：在顶层执行 `./configure`（可加 `--enable-cpic/--enable-fpic`、`--with-cfortran`、`--prefix`、`--with-mpi=omp` 等）后，`make` 会递归进入本目录，由 `Makefile.in` 将 `SRC` 中 30 个 `.c` 编译为 `.o`（可选加 `f2c.o`），`ar r $(TOPDIR)/libfac.a` 归档。主要并行方式为 **OpenMP**（`USE_MPI==2`），MPI 支持有限（`USE_MPI==1`）。
- **依赖方向**：本库 → （Fortran）`blas/lapack/coul/ode/quadpack/toms/mpfun/ionis`；上层 `python/`（pfac）与 `sfac/`（sfac/scrm/spol）→ 本库 `libfac.a`。
- **理论文档**：`doc/manual.tex`（函数参考、二进制/ASCII 输出格式、FAQ）、`doc/papers/{structure,excitation,ionization,pirr,aidr,mcross,ebfield}.tex`（各过程理论论文）；安装与快速上手见顶层 `README.md`。

## 7. README 维护记录（自底向上）

- **定位与职责**：`faclib/` 是 FAC 的 C 核心物理库，向上支撑 PFAC 与 SFAC，向下依赖数值与物理支撑库。
- **底层依据**：`consts.h`（单位/常数）、`structure.c`、`transition.c`、`excitation.c`、`ionization.c`、`recombination.c`、`crm.c`、`polarization.c`、`rmatrix.c`、`dbase.c`。
- **输入/输出**：输入为脚本设置的组态、能级、网格与速率参数；输出为 `.en/.tr/.ce/.ci/.rr/.ai/.sp/.rt` 二进制表及其 ASCII 打印结果。
- **验证与回归**：通过 `demo/make check` 和 `demo/check.py` 间接验证；表头、单位、行序与容差规则见 [`../demo/README.md`](../demo/README.md)。
- **已知限制**：C 层大量全局状态导致 PFAC/SFAC 非线程安全；并行须进程级隔离；部分历史公式与源码实现不同名。
- **公式核查**：
  - Maxwell 速率系数：\underline{$\frac{8.63\times10^{-6}}{g_i T^{3/2}}$}
  - 自发辐射率：\underline{$A_{ji}=\frac{64\pi^4\nu^3}{3hc^3(2J+1)}|D|^2$}
  - DR 热速率系数：\underline{$\alpha^{\rm DR}(T)=\frac{h^3}{(2\pi m_e k_BT)^{3/2}}\sum_i\frac{g_i}{2g_f}A_i^aB_i e^{-E_{if}/k_BT}$}
  - R 矩阵极点式：\underline{$R_{ij}(E)=\sum_k\frac{w_{ik}w_{jk}}{2a(E_k-E)}$}
  - MBPT 有效哈密顿量：\underline{$H_{\rm eff}=H_{PP}+H_{PQ}(E-H_{QQ})^{-1}H_{QP}$}
  - 二次 Stark 位移：\underline{$\Delta E=-\frac{1}{2}\alpha_d|E|^2$}
- **导航**：父级 [`../README.md`](../README.md)；接口 [`../python/README.md`](../python/README.md)、[`../sfac/README.md`](../sfac/README.md)；示例 [`../demo/README.md`](../demo/README.md)。

[返回上级](../README.md)