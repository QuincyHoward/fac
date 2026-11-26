# modqed —— FAC 的 QED（量子电动力学）修正模块

## 1. 目录定位

本目录是 FAC（Flexible Atomic Code）中专门处理 **QED 辐射修正** 的 Fortran 77 模块。它为相对论原子结构计算提供：

- 电子**自能**（self-energy, SE）修正——采用 Shabaev、Tupitsyn、Yerokhin（PRA 88, 012513 (2013)；CPC 189, p175 (2015)）的**模型 QED 势**；
- **真空极化**（vacuum polarization, VP）修正——Uehling 势（含有限核尺寸）与 Wichmann–Kroll（WK）高阶项；
- 为上述修正提供**核势生成、径向 Dirac 方程求解、半对数径向网格、数值积分、插值数据表**等基础设施。

与 FAC 其他部分的关系：

- `faclib/structure.c`：在组态相互作用（CI）哈密顿量矩阵元中调用 `QED1E(k0,k1)`，把 QED 修正加到库仑矩阵元上（例如 `structure.c:1454`、`structure.c:1507`、`structure.c:2094`），并在能级求和中加上 `QED1E(t,t)`（`structure.c:2936`）；这些调用最终由 `faclib/radial.c` 中的 `QED1E` 实现（`radial.c:9411`），`QED1E` 汇总 `RadialNMS`（有限核质量/反冲一类的核运动修正）、VP 积分和 `SelfEnergy`（`radial.c:9486`）。
- `coul/`：提供 `coul/mohrfin.f` 等有限核电荷分布拟合例程（被 `faclib/coulomb.c` 的 `MOHRFIN` 调用），与本模块的 `nucl.f` 功能互补：本模块自己实现 Fermi/均匀球/Gaussian 分布的核势与 Taylor 展开。
- `toms/`：提供三次样条插值例程 `toms/uvip3p.f`（`UVIP3P`），被本模块 `genqed.f`、`fse_dat.f`、`pot_wav.f` 以及 `faclib/coulomb.c` 等广泛使用。

手册层面：`doc/manual.tex` 第 94–96 行说明 FAC 用“氢样近似”处理自能与真空极化；第 5031–5036 行说明推迟与反冲等高阶 QED 只在零频 Breit 相互作用中计入，VP 与 SE 采用 screened-hydrogenic 近似；`SetSE`（`manual.tex:3528–3545`）与 `SetVP`（`manual.tex:3628–3636`）给出开关语义；第 2769 行说明输出势文件中的 $U(r)$ 即近似真空极化的 Uehling 势。

## 2. 组织形式与文件分类

按功能把 17 个 `.f` 文件分为六类：

| 类别 | 文件 | 职责 |
|---|---|---|
| 驱动与工具 | `potgen_main.f`、`iniqed.f`、`genqed.f`、`potuse1.f`、`potuse2.f`、`read_pot.f` | 生成/读取模型 QED 势数据文件并计算矩阵元的独立主程序、被 C 层调用的初始化入口及文件 I/O |
| 核势生成 | `atom_data.f`、`nucl.f` | 核半径数据表、核模型参数、点核/Fermi/均匀球/Gaussian 核势及电荷密度 |
| 径向网格 | `grid.f`、`segrid.f` | 半对数径向网格 $\rho(r)=al\cdot r+bt\ln r$ 的建立与网格参数回传 |
| Dirac 方程求解 | `dirac.f` | 有限核势下径向 Dirac 方程的数值求解（含原点 Taylor 展开、有限差分修正、节点计数与归一化） |
| 自能 self-energy | `se_pot.f`、`fse_dat.f`、`pot_wav.f` | 自能矩阵元表插值、局域/非局域（可分离）自能势构造、算符作用于波函数 |
| 真空极化 | `uehling.f`、`wk.f` | Uehling 势（Fullerton–Ringer 近似）与 Wichmann–Kroll 势（解析拟合） |
| 数据与插值 | `integr.f`、`segrid.f`（`rgmqed`）、`fse_dat.f`（`DInterpolation`）、`qedmod.inc` | Simpson 积分、网格参数回传、带“空洞”的 $Z$ 插值、公共维度参数 |

`Makefile.in` 中真正编入 `libfac.a` 的只有 12 个文件：`iniqed.f genqed.f atom_data.f segrid.f pot_wav.f se_pot.f dirac.f integr.f uehling.f fse_dat.f nucl.f wk.f`；`grid.f`、`potgen_main.f`、`potuse1.f`、`potuse2.f`、`read_pot.f` 是独立示例/驱动（详见第 6 节）。

## 3. 物理效应（核心章节）

### 3.1 相对论 Dirac 方程与库仑/有限核势下的径向方程

**(a) 简介。** 类氢离子的基准轨道由中心场 Dirac 方程给出，势能取点核库仑势 $-Z/r$ 加上有限核尺寸修正 $V_{\rm nuc}(r)+Z/r$。源码中该“非点核部分”记作 `unuc(i)`，与库仑部分 `y(i)=-z` 相加得到总势 `yi=y(i)+unuc(i)`（`dirac.f:163`）。求解采用半对数网格上的高阶有限差分 + 节点计数迭代法（`dirac.f` 头部注释：“solves numerically the Dirac equation for an extended nuclear potential”）。

**(b) 公式。** 源码未给出显式公式，此处为文献通用形式，需按 `dirac.f` 中的有限差分系数（`a(i), b(i), c(i), w(i)`，`dirac.f:160–169, 234–240`）与 `doc/manual.tex:5031` 核对：

$$
\left[c\,\boldsymbol{\alpha}\cdot\mathbf{p}+\beta mc^{2}+V(r)\right]\Psi(\mathbf r)=E\Psi(\mathbf r),\qquad V(r)=-\frac{Z}{r}+V_{\rm nuc}^{\rm(nonpoint)}(r).
$$

以 $\Psi=\frac{1}{r}\begin{pmatrix}P(r)\chi_{\kappa m}\\ iQ(r)\chi_{-\kappa m}\end{pmatrix}$ 分解，径向耦合方程（原子单位、$E$ 为束缚能）为：

$$
\frac{dP}{dr}+\frac{\kappa}{r}P=\frac{1}{c}\!\left[E-V(r)+2mc^{2}\right]Q,\qquad
\frac{dQ}{dr}-\frac{\kappa}{r}Q=-\frac{1}{c}\!\left[E-V(r)\right]P .
$$

原点处按 $P,Q\sim r^{\gamma}$ 展开，$\gamma=\sqrt{\kappa^{2}-(Z/c)^{2}}$（源码 `dirac.f:100`、`dirac.f:724` 用 `vp(1)/cl` 替代 $Z$，以兼容有限核势）。

**(c) 源码对应表。**

| 公式要素 | 目录 | 文件 | 子程序/函数 | 实现要点 |
|---|---|---|---|---|
| 总势 $V(r)$ 装配 | `modqed` | `dirac.f` | `dirac(n,kappa,p,q)` | `y(i)=-z`，`yi=y(i)+unuc(i)`（第 58–60、163 行） |
| 径向耦合有限差分 | `modqed` | `dirac.f` | `dirac` | `a(i)=t*(s*r(i)+yi)*v(i)/r(i)`、`b(i)=s*v(i)-a(i)`、`c(i)=hkappa*v(i)/r(i)`（第 154–169、234–240 行） |
| 原点边界与 Taylor 系数 | `modqed` | `dirac.f` | `origin(kappa,p,q)` | 递推式 `p1(i)=(-vp(1)*s1+t1*s2)/d`、`q1(i)=(-vq(1)*s2-t2*s1)/d`（第 736–750 行） |
| 有限差分高阶修正 | `modqed` | `dirac.f` | `correct(imin,imax,tn,p,q,cp,cq)` | 五点/七点修正累加到 `cp,cq` |
| 归一化 $\int(P^2+Q^2)dr=1$ | `modqed` | `dirac.f` | `dirac` + `integr.f:tint` | `d=tint(0,p,q,p,q,r,v); d=1/sqrt(d)`（第 546–551 行） |
| 能量本征值存放 | `modqed` | `dirac.f` | `dirac` | `p(ii+1)=e`，调用方取 `e=0.5d0*p(ii+1)` |
| 径向网格 | `modqed` | `segrid.f` / `grid.f` | `segrid`、`grid`、`tbr`、`rr` | $\rho=al\,r+bt\ln r$，Newton 迭代求 $r(\rho)$ |
| C 层网格参数回传 | `modqed` | `segrid.f` | `rgmqed(a,b)` | 被 `faclib/orbital.c:3510` 调用以重建 `pot->mqrho[i]` |

### 3.2 电子自能（self-energy）辐射修正

**(a) 简介。** 电子发射并重新吸收虚光子导致的能级移动，是 QED 领头阶辐射修正。对类氢离子，其量级随核电荷快速增大；FAC 有两种实现：传统的**屏蔽氢样近似**（`faclib/coulomb.c` 中的 GRASP 类表 `_qed_se0/_qed_se1`，由 `SetSE` 模式 `k=1` 选择），以及本模块实现的**模型 QED 势**（`k=4/5/6/7`，Shabaev 等模型）。模型算符是**局域 + 可分离 Nonlocal** 的形式：

$$
V_{\rm mod}=V_{\rm loc}+\sum_{a,b}|a\rangle D_{ab}\langle b|,\qquad
D_{ab}=S_{ab}^{-1}\left({\rm QED}_{ab}-V_{ab}\right)S_{ab}^{-1},
$$

其中 $|a\rangle$ 是投影波函数，$S_{ab}=\langle a|b\rangle$，$V_{ab}=\langle a|V_{\rm loc}|b\rangle$。`manual.tex:3541–3544` 说明模式第 3 位数字非 0 时可把局域部分放进径向 Dirac 方程，只在哈密顿量中计算非局域部分。

**(b) 公式。** 类氢能级自能修正量级（源码 `se_pot.f:118–127` 中以 `dn=dsqrt(dn1*dn2)`、`coef=alpha/pi*(z*alpha)**4/dn**3*cl**2` 实现，其中 `dn³=(n₁n₂)^{3/2}`、`cl` 为光速、原子单位下 $mc^2=c^2$）：

$$
\Delta E^{\rm SE}\sim\frac{\alpha}{\pi}\,(Z\alpha)^{4}\,m c^{2}\,\frac{F(Z\alpha)}{(n_1n_2)^{3/2}},
\qquad \alpha=\frac{1}{c},\quad c=137.03599911 .
$$

表中存的是无量纲 $F(Z\alpha)$（`fse_dat.f` 的 `FSE`/`FSEfns`），即 `qed_matrix(ni,nj)=FSE×coef`；对 $\kappa=-1$ 还加对数项以处理 $1s$ 态的反常维度。按源码 `fse_dat.f:36,40`，对数项的符号在插值前后相反：

$$
F_{1s}\;\to\;F_{1s}+\frac{8}{3}\ln\frac{Z}{\alpha_{\rm cl}^{-1}}\quad(\text{插值前}),\qquad -\frac{8}{3}\ln\frac{Z}{\alpha_{\rm cl}^{-1}}\;(\text{插值后}),\quad \alpha_{\rm cl}^{-1}=137.0359895 .
$$

局域势采用指数型试探形式（源码 `se_pot.f:189`：`vloc(i)=exp(-ri*cl)*ri`，即 $rV_{\rm loc}(r)\propto r e^{-cr}$），幅度由对角线自能矩阵元归一（`se_pot.f:204–205`）：

$$
\langle n\kappa|V_{\rm loc}|n\kappa\rangle = {\rm se\_loc}(\kappa),\qquad
V_{\rm loc}(r)=v_{0\kappa}\,\frac{e^{-cr}}{r}.
$$

投影波函数由 `ww(i)=e^{-cr} r` 与 `exp(-2Zr) r` 组合构成（`se_pot.f:285–298`），经 `tint(-1,...)` 归一化存入 `up,uq`。

**(c) 源码对应表。**

| 公式要素 | 目录 | 文件 | 子程序/函数 | 实现要点 |
|---|---|---|---|---|
| 标度因子 $\frac{\alpha}{\pi}(Z\alpha)^4/(n_1n_2)^{3/2}c^2$ | `modqed` | `se_pot.f` | `init_se` | `coef=alpha/pi*(z*alpha)**4/dn**3*cl**2`（第 121 行） |
| $F(Z\alpha)$ 表插值（点核/有限核） | `modqed` | `fse_dat.f` | `FSEdat(ka,n1,n2,iz,SE_pnt,SE_ext)`、`DInterpolation`、`ZInterp` | 表 `FSE(120,-3:2,5,5)`、`FSEfns(...)` |
| 点核表装载 | `modqed` | `fse_dat.f` | `se_pnt_stor()` | 第 1398 行起，`FSE(Z,ka,n1,n2)` 与误差 `errtot` |
| 有限核尺寸表装载 | `modqed` | `fse_dat.f` | `se_fn_stor()` | 第 157 行起，`FSEfns(Z,ka,n1,n2)` |
| 自能矩阵 $Q_{ij}$ | `modqed` | `se_pot.f` | `init_se` | 存于 `qed_matrix(maxns,maxns)`，按 `knucl` 选 `fse_pnt/fse_ext` |
| 局域势 $V_{\rm loc}$ | `modqed` | `se_pot.f` | `local_se_pot` | `vsemi_loc(i,kappa)=r V_{\rm loc}(r)` |
| 重叠/局域矩阵 $S_{ab},V_{ab}$ | `modqed` | `se_pot.f` | `nonlocal_se_pot` | `sint(vloc,...)`、`tint(-1,p,q,up,uq,r,v)` |
| $D_{ab}=S^{-1}(Q-V)S^{-1}$ | `modqed` | `se_pot.f` | `dab_matrix(qed_matrix)` | `dkl=0.5*(qkl+qlk)-vab(nk,nl)`（第 437 行） |
| 矩阵求逆 | `modqed` | `se_pot.f` | `dminv(a,n,nmax,d,l,m)` | Gauss–Jordan 法 |
| $V_{\rm mod}\psi$ | `modqed` | `pot_wav.f` | `se_pot_wav(n,kappa,iw,r,pp,qq,cp,cq)` | 局域项 + `Dab*dproj` 非局域项（第 57–94 行） |
| 抽出自能势给 C 层 | `modqed` | `pot_wav.f` | `locsep(i,nr,ur,vr)` | 经 `UVIP3P` 插值到 FAC 的 `mqrho` 网格 |
| C 层总入口 | `faclib` | `radial.c` / `coulomb.c` | `QED1E`、`SelfEnergy`、`HydrogenicSelfEnergy`、`FSEDAT` | `radial.c:9486`、`coulomb.c:610` |
| C 层声明 | `faclib` | `cf77.h` | `FSEDAT`、`INIQED`、`LOCSEP`、`RGMQED`、`UVIP3P` | cfortran `PROTOCCALLSFSUBn` 宏 |

说明：两圈（two-loop）修正通过 `SetSE` 的模式位 `k=3/5/7` 排除；源码中未见独立的两圈势计算子程序，需按 `faclib/coulomb.c` 中 `_qed_ex/_qed_rec` 表与 `manual.tex:3536–3541` 核对具体实现。

### 3.3 Uehling 势（真空极化）

**(a) 简介。** 虚电子–正电子对屏蔽核电荷，产生 Uehling 势（VP 的 $\alpha(Z\alpha)$ 阶项），是轻元素中最重要的 QED 修正。源码 `uehling.f` 采用 Fullerton 与 Ringer（PRA 13, 1283 (1976)）的**精确有理逼近**，对点核与有限核电荷分布均适用；气核输出 `uehl(i)=r V_U(r)`。手册 `manual.tex:2769` 把输出势文件中的 $U(r)$ 识别为 Uehling 势，`SetVP`（`manual.tex:3628–3636`）可关闭、仅取二阶、含四阶、含 WK 项，并可把 VP 势直接放进径向 Dirac 方程。

**(b) 公式。** 源码 `uehling.f:42–43,94–95` 用 `dk0/dk1` 拟合积分；点核 Uehling 势的标准积分形式为

$$
V_U(r)=-\frac{2\alpha}{3\pi}\frac{Z}{r}\int_1^{\infty}\!dt\;e^{-2m_ecr\,t}\left(1+\frac{1}{2t^{2}}\right)\frac{\sqrt{t^{2}-1}}{t^{2}} .
$$

若记 $\Phi_U(r)=-\dfrac{2\alpha}{3\pi}\displaystyle\int_1^{\infty}\!dt\;e^{-2m_ecr\,t}\left(1+\frac{1}{2t^{2}}\right)\dfrac{\sqrt{t^{2}-1}}{t^{2}}$，则 $V_U(r)=Z\,\Phi_U(r)/r$；**不要**再额外乘 $\alpha$ 或重复除以 $r$。源码点核实现 `rV_U=-dk_1(2cr)\cdot 8Z/(3\cdot4\pi c)` 与该式一致（$\alpha=1/c$）。

有限核电荷分布 $\rho(\mathbf r')$ 下的推广：

$$
V_U(r)=-\frac{2\alpha}{3\pi}\int d^{3}r'\,\frac{\rho(r')}{|\mathbf r-\mathbf r'|}
\int_1^{\infty}\!dt\;e^{-2m_ec|\mathbf r-\mathbf r'|t}\left(1+\frac{1}{2t^{2}}\right)\frac{\sqrt{t^{2}-1}}{t^{2}} .
$$

源码实际采用的函数形式（与上式等价的逼近实现）：

$$
rV_U(r)\big|_{\rm point}= -\,dk_1(2cr)\,\frac{8Z}{3\,4\pi c},\qquad
rV_U(r)\big|_{\rm finite}= -\frac{2}{3\,4\pi c^{2}}\int_{r_0}^{r_{\rm nuc}}
\!\Big[dk_0\big(2c|r-r'|\big)-dk_0\big(2c(r+r')\big)\Big]\rho(r')\,r'^{2}\,d\ln r' .
$$

其中 `coef1=-2.d0/3.d0/cl**2/(4*pi)`、`coef2=-z*8.d0/3.d0/cl/(4*pi)`（`uehling.f:42–43`），积分在对数网格上用 4×maxii 个点和端点微分校正（`uehling.f:52–86`）。`dk0`、`dk1` 在 $x\le1$ 与 $x>1$ 两段分别用 7 阶多项式 + [2/2] 有理式与指数渐近式拟合（`uehling.f:107–206`）。

**(c) 源码对应表。**

| 公式要素 | 目录 | 文件 | 子程序/函数 | 实现要点 |
|---|---|---|---|---|
| $rV_U(r)$ 主驱动 | `modqed` | `uehling.f` | `uehling(maxii,r,unuc,uehl)` | 点核走 `dk1` 分支；有限核走对数积分分支（第 48–96 行） |
| 点核核电荷输入 | `modqed` | `uehling.f` | `uehling` | `x=2*cl*rr`，`Uehl(ir)=dk1(x)*coef2` |
| 有限核电荷密度 | `modqed` | `nucl.f` | `ro_nucl(r)` | Fermi/均匀球/Gaussian 三种 $\rho(r)$ |
| 核半径上界 $r_{\rm nuc}$ | `modqed` | `nucl.f` | `nucl` | `unuc(ii+3)=inucl`（有效截断） |
| 核外截断判据 | `modqed` | `uehling.f` | `uehling` | `abs(uehl/r)>1e-40` 决定 `imax`，写入 `uehl(ii+3)` |
| VP 矩阵元 | `modqed` | `integr.f` | `sint(c,p,q,a,b,r,v)` | $\int c(r)(pa+qb)/r\,dr$，Simpson 法 |
| C 层 VP 装配 | `faclib` | `radial.c` / `orbital.c` | `QED1E`、`SetPotentialVP` | `ZVP[i]`、`potential->mvp`（`radial.c:9475–9484`） |

### 3.4 有限核尺寸效应（核电荷分布势）

**(a) 简介。** 实际原子核电荷分布在有限半径内，消除了点核势在原点的奇异性；对 $s_{1/2}$ 轨道以及高 $Z$ 的能级影响显著。本模块支持三种有限核模型（`knucl=0/1/2/3`，见 `atom_data.f:7–10`、`nucl.f`）：点核、Fermi 分布、均匀球分布、Gaussian 分布。有限核修正以 `unuc(i)=r\,[V_{\rm nuc}(r)+Z/r]` 的形式进入 Dirac 方程，同时以 `FSEfns` 表的形式进入自能修正（`fse_dat.f:157` 起）。

**(b) 公式。** 点核：$V(r)=-Z/r$。源码给出的展开系数（`nucl.f:75–76`）：

$$
\text{均匀球：}\quad V_{\rm sphere}(r)=-\frac{3Z}{2R}+\frac{Z r^{2}}{2R^{3}}+\cdots,\qquad
\texttt{vnuc(2)}=-\frac{3Z}{2R},\ \texttt{vnuc(4)}=\frac{Z}{2R^{3}} .
$$

Fermi 分布（源码 `nucl.f:238–245`、`nucl.f:98–122` 给出参数与归一化）：

$$
\rho(r)=\frac{\rho_{0}}{1+\exp[(r-c)/a]},\quad
t=2.30,\quad a=\frac{t}{4\ln 3}\,\text{(fm}\to\text{a.u.)},\quad
c=\sqrt{\frac{5}{3}r_{\rm nuc,0}^{2}-\frac{7}{3}\pi^{2}a^{2}},
$$

$$
\rho_{0}=Z\Big/\left\{\frac{c^{3}}{3}\Big[1+\Big(\frac{\pi a}{c}\Big)^{2}
-6\Big(\frac{a}{c}\Big)^{3}\mathrm{Sk}(3,-c/a)\Big]\right\},\qquad
\mathrm{Sk}(k,x)=\sum_{N=1}^{\infty}\frac{(-1)^{N}e^{Nx}}{N^{k}} .
$$

其势由 `vpot_fermi(z,c,a,r)` 用两段闭式计算（源码 `nucl.f:268–281`，细节见 F.A. Parpia、A.K. Mohanty, PRA 46, 3735 (1992)）。Gaussian 分布（`nucl.f:144`、`nucl.f:296`）：

$$
\rho(r)=Z\,4\pi\left(\frac{1.5}{\pi r_{\rm nuc,0}^{2}}\right)^{3/2}e^{-1.5(r/r_{\rm nuc,0})^{2}},\qquad
V_{\rm Gauss}(r)=-\frac{Z\,\mathrm{erf}\!\left(\sqrt{3/2}\,r/R_{\rm rms}\right)}{r}.
$$

核半径数据取自 I. Angeli、K.P. Marinova, Atomic Data and Nuclear Data Tables 99, 69–95 (2013)，缺失时按 Johnson–Soff 经验式 `rms=0.836 A^{1/3}+0.570`（$Z<91$）与 `0.77 A^{1/3}+0.980`（$Z>90$）估计（`atom_data.f:92–102, 348–355`）。

**(c) 源码对应表。**

| 公式要素 | 目录 | 文件 | 子程序/函数 | 实现要点 |
|---|---|---|---|---|
| 核模型参数与 $R_{\rm rms}$ | `modqed` | `atom_data.f` | `atom_data`、`init_atom_data` | `Rrms(120)`、`Am(120)`、`name_at(120)`；`rfermi=rms*sqrt(5/3)` |
| $rV_{\rm nuc}^{({\rm nonpoint})}$ 与 Taylor 系数 | `modqed` | `nucl.f` | `nucl(maxii,r,unuc)` | `vnuc(1..10)`、`unuc(ii+5+m)` |
| Fermi $\rho(r)$ | `modqed` | `nucl.f` | `ro_nucl(r)` | `ro0/(1+exp((r-cc)/aa))` |
| Fermi 势 | `modqed` | `nucl.f` | `vpot_fermi(z,c,a,r)` | `r<c` 与 `r>=c` 两段闭式 |
| $Sk(k,x)$ 求和 | `modqed` | `nucl.f` | `sk(k,x)` | 级数至相对误差 $10^{-20}$ |
| Fermi 径向矩 | `modqed` | `nucl.f` | `rm(M,C,A)`、`fxneax`、`dfac`、`stpdi` | 用于 `vnuc(2)=-rm1*ro0` |
| Gaussian 势与误差函数 | `modqed` | `nucl.f` | `vpot_gauss`、`erf` | NSWC 数学库双精度 `erf` |
| 网格在核边界对齐 | `modqed` | `grid.f` / `segrid.f` | `grid`、`segrid` | `knucl.eq.2` 时令 `r(inucl)=rnucl` |
| 核半径拟合（C 层） | `faclib` | `coulomb.c` | `MOHRFIN`/`UVIP3P` 路径 | `coul/mohrfin.f`，用于偏离标准 $R_{\rm rms}$ 时的自能修正 |

### 3.5 Wichmann–Kroll 项及反冲/高阶 QED 的处理范围

**(a) 简介。** WK 项是真空极化中 $\alpha(Z\alpha)^3$ 阶及更高阶的部分，只在近核区域显著。`wk.f` 使用 Fainshtein、Manakov、Nekipelov（源码写为 J.Phys. E: At.Mol.Opt.Phys. 23 (1990) 559–569，实际期刊应为 J. Phys. B）的**解析拟合式**，仅针对**点核**。手册 `SetVP` 的第 3 位打开 WK 项。反冲（recoil）与推迟（retardation）等高阶 QED 在本模块中**没有独立的径向求解器**：`doc/manual.tex:5033–5035` 明确它们只在零交换光子能量极限的 Breit 相互作用里计入；C 层 `QED1E` 中的 `RadialNMS`（`radial.c:9473`）属于核质量/反冲类修正，但与本模块源码不是同一实现，需按 `faclib/radial.c` 核对。

**(b) 公式。** `wk.f:422–437` 显式给出点核 WK 势的大 $x$ 渐近展开（`x=cr$），源码在 `:426` 再乘 `(Z\alpha)^3`、在 `:437` 除以 $\pi c$：

$$
V_{\rm WK}(r)\sim \frac{(Z\alpha)^{3}}{\pi c}\left[\frac{2}{225x^{5}}+\frac{59}{1323x^{7}}
+\frac{1977+20(Z\alpha)^{2}}{4725x^{9}}+\cdots\right],\qquad x=cr .
$$

小 $x$ 区用 `p(n)`、`q(n)`、`a(i,m,n)`、`f(m,n)` 系数表构造对数/有理逼近，并含因子 `dlam=1-sqrt(1-Z/c)*sqrt(1+Z/c)`（`wk.f:368`）。注意 WK 势在原点有 $1/r^{2}$ 型奇异，源码将 `v_wk(i)=u_wk(x)*r(i)` 存为 $rV_{\rm WK}$ 以配合 `sint` 积分。

**(c) 源码对应表。**

| 公式要素 | 目录 | 文件 | 子程序/函数 | 实现要点 |
|---|---|---|---|---|
| $rV_{\rm WK}$ 主驱动 | `modqed` | `wk.f` | `wk(maxii,r,v_wk)` | 逐点 `x=r(i)*cl`，`v_wk(i)=u_wk(x)*r(i)` |
| 系数表初始化 | `modqed` | `wk.f` | `wk_init` | `p(0:35)`、`q(0:15)`、`f(15,5)`、`a(4,0:7,4)`、`s(4,4)` |
| 分段拟合求值 | `modqed` | `wk.f` | `u_wk(x)` | $x<0.15/1.5/4/10$ 分段，含 $x\ge10$ 渐近展开 |
| 调试输出 | `modqed` | `wk.f` | `wk` | 被注释的 `wk.dat` 写盘代码（第 47–61 行） |

## 4. 逐文件说明（17 个 `.f` 文件 + `qedmod.inc`）

### 4.1 `atom_data.f`
- **功能**：元素符号、原子量、核均方根半径 $R_{\rm rms}$ 的预存表；设置核模型与原子盒大小。
- **关键入口**：`subroutine atom_data`（无参数，公共块 `/z/z/r2/r2/cl/cl`、`/name/name`、`/knucl/knucl/rnucl/rnucl`、`/Rrms/Rrms(120)/name_at/name_at(120)/nprms/rms0`）；`subroutine init_atom_data`（无参数，公共块 `/Am/Am(120)`）。
- **依赖与调用方**：被 `iniqed.f`/`potgen_main.f` 首先调用；`rms0>0` 时用外部传入的 $R_{\rm rms}$ 覆盖表值；`Z<=15` 且 `knucl=1` 时自动改为均匀球（第 55 行）。
- **备注**：`cl=137.03599911d0`，`r2=150/z`；$Z<10$ 或 $Z>120$ 不受支持。

### 4.2 `dirac.f`
- **功能**：在任意核电荷分布下数值求解径向 Dirac 方程，输出归一化的 $P(r),Q(r)$ 与能量。
- **关键入口**：
  - `subroutine dirac(n,kappa,p,q)` —— `n` 主量子数，`kappa` 相对论角动量量子数，`p,q` 长度 `maxii` 的大/小分量数组；能量经公共块 `p(ii+1)` 与外层 `e=0.5*p(ii+1)` 返回。
  - `subroutine correct(imin,imax,tn,p,q,cp,cq)` —— 有限差分高阶修正。
  - `subroutine origin(kappa,p,q)` —— 原点 Taylor 系数 `p(ii+5+n),q(ii+5+n)`。
- **依赖与调用方**：调用 `tint`（`integr.f`）、`exit1`；被 `iniqed.f`、`potgen_main.f`、`potuse1.f`、`genqed.f`（示例）调用；C 层通过 `QED1E` → `HydrogenicSelfEnergy` 路径间接用到氢样轨道。
- **备注**：迭代上限 `niter>200` 报错；`nmax=9`；`cp/cq` 公共块同时被 `se_pot.f` 复用（存在共用别名，使用时需注意）。

### 4.3 `fse_dat.f`
- **功能**：Shabaev 等（PRA 88, 012513 (2013)）自能矩阵元表的装载与对 $Z$ 插值，给出点核与有限核尺寸修正后的无量纲 $F(Z\alpha)$。
- **关键入口**：
  - `subroutine FSEdat(ka,n1,n2,iz,SE_pnt,SE_ext)` —— `ka` 为 $\kappa$（$-3..2$），`n1,n2` 主量子数（1..5），`iz` 取整电荷；输出 `SE_pnt`、`SE_ext`。
  - `real*8 function DInterpolation(iz,Func)`、`real*8 function ZInterp(iz,Func,np)` —— 带空洞数组的 3/4 点插值。
  - `subroutine se_pnt_stor()`（第 1398 行）、`subroutine se_fn_stor()`（第 157 行）。
- **依赖与调用方**：调用 `UVIP3P`（`toms/uvip3p.f`）；被 `se_pot.f:init_se` 与 C 层 `faclib/coulomb.c:610` 的 `FSEDAT(k,n,n,z,&a,&b)` 调用。
- **备注**：文件约 206 KB，绝大部分为数据表；`errtot` 存对应误差；`acl=137.0359895d0` 与 `atom_data.f` 中的 `cl` 略有差异，需核对一致性。

### 4.4 `genqed.f`
- **功能**：示例/工具子程序——从磁盘读取模型 QED 势，计算其与类氢 Dirac 波函数的矩阵元。
- **关键入口**：`subroutine genqed(n0,n1,ka,iw,nr,r0,p0,q0,p1,q1,dse)`；`character*7 function GetState(n,kappa)`（生成 `2p3/2` 之类谱项记号）。
- **依赖与调用方**：调用 `read_pot`、`uvip3p`、`se_pot_wav`、`tint`、`sint`；从标准输入读数据文件名；编译进 `libfac.a`（`Makefile.in` 的 `SRC` 含此文件）。
- **备注**：头部注释自称 "example #1"，但实现为带参数的 subroutine；`l>2` 时直接返回 `dse=0`；第 122 行 `GetState(n,kappa)` 使用了未传入的局部变量 `n,kappa`，疑为遗留代码，使用时需核对。

### 4.5 `grid.f`
- **功能**：半对数径向网格的**旧版**实现（与 `segrid.f` 高度重复）。
- **关键入口**：`subroutine grid`（无参数）；`subroutine tbr(ii,r1,h,al,bt,r,v)`；`function rr(ro,r0)`。
- **依赖与调用方**：被 `potgen_main.f` 调用；`grid` 写单元 11（`potgen.res`），`segrid` 不写。
- **备注**：**未列入 `Makefile.in` 的 `SRC`**；不填充 `rho(i)`，也没有 `rgmqed`，故 C 层实际用的是 `segrid.f`。

### 4.6 `iniqed.f`
- **功能**：模型 QED 势生成器的主入口（C 层调用）；计算辅助数据并写入外部文件。
- **关键入口**：`subroutine iniqed(z0,nmax0,knucl0,rms)`；辅助 `subroutine read_func(ni,v1,v2,nrec)`、`write_func(ni,v1,v2,nrec)`、`radfnd(ik,rn)`、`exit1`。
- **依赖与调用方**：依次调用 `atom_data`、`segrid`、`nucl`、`init_se`、`dirac`、`uehling`、`wk`、`local_se_pot`、`nonlocal_se_pot`、`write_pot`；给出的 `z0,knucl0,rms` 参数在代码开头被标准输入覆盖（第 141–153 行）。
- **备注**：C 层声明见 `faclib/cf77.h:103–105`，调用点 `faclib/nucleus.c:565` 与 `faclib/radial.c:13078,13087,13100,13112`（有效核电荷 $R_{\rm rms}$ 拟合）；日志写 `potgen.res`。注意此文件与 `potgen_main.f` 存在三个同名子程序（`read_func/write_func/exit1`），不能同时链接两份目标文件。

### 4.7 `integr.f`
- **功能**：非均匀网格上的 Simpson 数值积分（含小 $r$ 端的幂律外推）。
- **关键入口**：
  - `function tint(k,p,q,a,b,r,v)` —— $\langle p,q|r^{k}|a,b\rangle=\int (pa+qb)\,r^{k}\,dr$。
  - `function sint(c,p,q,a,b,r,v)` —— $\langle p,q|c(r)/r|a,b\rangle=\int c(r)(pa+qb)/r\,dr$。
  - 参数：`p,q` 左波函数大/小分量，`a,b` 右波函数，`r` 径向网格，`v` Simpson 权重；公共块 `/h/h/ii/ii`。
- **依赖与调用方**：被 `dirac.f`、`se_pot.f`（`local_se_pot`、`nonlocal_se_pot`、`se_pot_wav`）、`genqed.f`、`potuse1/2.f` 调用。
- **备注**：末端按振幅 $<10^{-20}$ 截断；点数奇偶分别用四点 Simpson 与标准三点 Simpson。

### 4.8 `nucl.f`
- **功能**：核电荷分布与非点核势；提供 Fermi/均匀球/Gaussian 的电荷密度、势、Taylor 系数与 $Z$ 依赖工具函数。
- **关键入口**：
  - `subroutine nucl(maxii,r,unuc)` —— `r(i)` 输入网格，`unuc(i)=r[V_{\rm nuc}(r)+Z/r]` 输出。
  - `real*8 function ro_nucl(r)` —— 电荷密度 $\rho(r)$。
  - `function vpot_fermi(z,c,a,r)`、`function vpot_gauss(z,rms,r)`。
  - 辅助：`sk(k,x)`、`rm(M,C,A)`、`fxneax(N,A,X)`、`dfac(n)`、`stpdi(X,I)`、`DOUBLE PRECISION FUNCTION erf(x)`。
- **依赖与调用方**：调用 `exit1`；被 `iniqed.f`、`potgen_main.f`、`uehling.f`（通过 `ro_nucl`）调用。
- **备注**：`knucl=1` 且 $c^{2}\le0$（$Z$ 太小）时自动退回均匀球模型（第 102–110 行）；`erf` 来自 NSWC 数学库。

### 4.9 `potgen_main.f`
- **功能**：独立可执行的 QED 势生成器主程序（与 `iniqed.f` 流程几乎相同）。
- **关键入口**：`program main_potgen`；附带 `read_func`、`write_func`、`exit1`。
- **依赖与调用方**：调用 `atom_data`、`grid`（旧版）、`nucl`、`init_se`、`dirac`、`uehling`、`wk`、`local_se_pot`、`nonlocal_se_pot`、`write_pot`。
- **备注**：**未列入 `Makefile.in`**；需手工编译链接，且因与 `iniqed.f` 有同名子程序，不能与 `iniqed.o` 同时链接；用户输入 $Z\in[10,120]$、`knucl`、输出文件名。

### 4.10 `potuse1.f`
- **功能**：使用示例 1——读入模型 QED 势，用类氢 Dirac 波函数计算 Uehling/WK/SE 矩阵元并以 $F(Z\alpha)$ 为单位打印。
- **关键入口**：`program main_potuse`；`character*7 function GetState(n,kappa)`；`subroutine exit1`。
- **依赖与调用方**：`read_pot` → `dirac` → `se_pot_wav` → `tint`/`sint`；对 $\kappa=\pm1,\pm2,\pm3$、$n=1..3$ 循环。
- **备注**：**未列入 `Makefile.in`**；源码中 `call se_pot_wav(n,kappa,r,p,q,cp,cq)` 只有 6 个实参，而 `pot_wav.f` 中的定义有 8 个（`n,kappa,iw,r,pp,qq,cp,cq`），说明该示例的参数列表已过时，直接编译可能出错，需按 `pot_wav.f` 核对。

### 4.11 `potuse2.f`
- **功能**：使用示例 2——读入模型 QED 势与**磁盘上已存的波函数**，计算 QED 算符期望值及不同态之间的差值。
- **关键入口**：`program main_potuse`；`subroutine wfunc_interpolate(KA,NnA,x,GA,FA)`（五点插值）；`subroutine wfunc_read(nwf,dir_name)`；`FUNCTION LENGTH(STRING)`；`GetState`、`exit1`。
- **依赖与调用方**：`read_pot`、`wfunc_read`、`wfunc_interpolate`、`se_pot_wav`、`tint`、`sint`。
- **备注**：**未列入 `Makefile.in`**；波函数文件名形如 `1s_p.dat`、`2p_m.dat`（`_p`/`_m` 由 $j>2l$ 判断），首行存 `kappa, n, energy`；`se_pot_wav` 调用同样存在与 4.10 相同的参数个数疑点。

### 4.12 `pot_wav.f`
- **功能**：模型 QED 算符作用于波函数；同时提供 C 层抽取局域自能势的接口。
- **关键入口**：
  - `subroutine se_pot_wav(n,kappa,iw,r,pp,qq,cp,cq)` —— 输入波函数 `pp,qq`，输出 `cp,cq=V_mod (pp,qq)`；`iw=0` 时包含局域部分。
  - `subroutine locsep(i,nr,ur,vr)` —— `i` 为 $\kappa$ 索引（`il=i+1`），`ur` 为 FAC 网格 `mqrho`，`vr` 输出 `ZSE[i]`。
- **依赖与调用方**：调用 `tint`、`uvip3p`；公共块 `/vsemi_loc/`、`/Dab/`、`/up/uq/`；被 `genqed.f`、`potuse1/2.f` 与 C 层 `LOCSEP`（`faclib/orbital.c:4129`）调用。
- **备注**：`se_pot_wav` 用 `pp(ii+3/ii+4)` 传递网格点数与 $\gamma$ 等“带外”信息，属于老式 Fortran 约定，更换调用方式时需小心。

### 4.13 `read_pot.f`
- **功能**：从用户指定的数据文件读回径向网格、Uehling/WK 势、局域势、投影波函数 `up,uq` 与非局域矩阵 `Dab`。
- **关键入口**：`subroutine read_pot(data_filename)`，`character*(*)` 参数；打开单元 13，失败则 `stop`。
- **依赖与调用方**：被 `genqed.f`、`potuse1.f`、`potuse2.f` 调用；与 `se_pot.f:write_pot` 的写出格式严格对应。
- **备注**：**未列入 `Makefile.in`**，但被列入 `SRC` 的 `genqed.f` 依赖它；单独编译示例程序时必须一并链接；读入后重建 `v(i)=r(i)/(al*r(i)+bt)`。

### 4.14 `segrid.f`
- **功能**：C 层实际使用的半对数径向网格初始化（含网格参数回传）。
- **关键入口**：
  - `subroutine segrid` —— 计算 `ii,r1,r2,h,al,bt,r(i),v(i),rho(i)`。
  - `subroutine rgmqed(a,b)` —— 返回 `al,bt`，C 宏 `RGMQED`。
  - `subroutine tbr(...)`、`function rr(ro,r0)` —— 同 `grid.f`。
- **依赖与调用方**：被 `iniqed.f` 调用；C 层 `faclib/orbital.c:3510` 调用 `RGMQED(&a,&b)` 重建 `pot->mqrho[i]=b*ln(r)+a*r`。
- **备注**：`rho(i)` 只在 `segrid` 中填充（`grid.f` 不填），这对 `locsep` 的 `uvip3p` 插值至关重要。

### 4.15 `se_pot.f`
- **功能**：自能模型势的核心——表插值→矩阵→局域/非局域势→写盘。
- **关键入口**：
  - `subroutine init_se`
  - `subroutine local_se_pot`
  - `subroutine nonlocal_se_pot`
  - `subroutine dab_matrix(qed_matrix)`
  - `subroutine write_pot(output_filename)`
  - `subroutine dminv(a,n,nmax,d,l,m)`
- **依赖与调用方**：调用 `FSEdat`（`fse_dat.f`）、`sint/tint`（`integr.f`）、`read_func`（`iniqed.f` 或 `potgen_main.f`）；被 `iniqed.f`/`potgen_main.f` 调用。
- **备注**：`ns_proj` 由 `init_se` 自动设定（$\kappa=-1,1,-2,2,-3$，$n\le3$，共约 11 个投影态）；`Dab` 的非对角元在 `SetSE` 模式 `k=6/7` 时才用于 CI；矩阵求逆后有 `abs(del)<1e-10` 的自检输出。

### 4.16 `uehling.f`
- **功能**：Uehling 真空极化势（点核/有限核，Fullerton–Ringer 近似）。
- **关键入口**：`subroutine uehling(maxii,r,unuc,uehl)`；`real*8 function dk0(x)`、`real*8 function dk1(x)`。
- **依赖与调用方**：调用 `ro_nucl`（`nucl.f`）；被 `iniqed.f`、`potgen_main.f` 调用。
- **备注**：输出 `uehl(i)=r V_U(r)`，`uehl(ii+3)=imax` 为有效格点数；有限核分支的对数积分上限取 `r(inucl)`，故 `nucl` 必须先执行。

### 4.17 `wk.f`
- **功能**：点核 Wichmann–Kroll 高阶真空极化势（解析近似）。
- **关键入口**：`subroutine wk(maxii,r,v_wk)`、`subroutine wk_init`、`real*8 function u_wk(x)`。
- **依赖与调用方**：被 `iniqed.f`、`potgen_main.f` 调用；公共块 `/wk_coeff/f(15,5),p(0:35),q(0:15),a(4,0:7,4),s(4,4)` 在 `wk_init` 中初始化。
- **备注**：只适用于点核（手册 `SetVP` 第二位数字为 1 时不考虑有限核尺寸才对应点核 VP）；被注释的 `wk.dat` 输出可用于调试；`f(13..15,1)` 与 `f(14,1)` 等赋值存在重复下标（源码第 187–202 行），疑为笔误，需核对。

### 4.18 `qedmod.inc`（单独说明）
- 仅一行：`parameter (maxii=4*512,maxns=24)`。
- 定义全模块公共数组维度：径向网格最多 2048 点，投影态/SE 矩阵最多 24 个；几乎所有 `.f` 文件都 `include 'qedmod.inc'`。
- 修改它必须同步检查 `vsemi_loc(maxii,6)`、`Dab(maxns,maxns)`、`qed_matrix(maxns,maxns)` 及 C 层 `NKSEP` 等尺寸约束。

## 5. 接口说明

### 5.1 Fortran 驱动流程
1. `atom_data` 设置 $Z$、$R_{\rm rms}$、核模型 → `segrid` 建网格 → `nucl` 生成 `unuc`；
2. `init_se` 读表 `FSEdat` 得 `qed_matrix`；`dirac` 求解氢样波函数并用 `write_func` 存入公共块 `/ff/`；
3. `uehling`、`wk` 生成 VP 势；`local_se_pot`、`nonlocal_se_pot` 构造 $V_{\rm loc}$、`up/uq`、`Dab`；
4. `write_pot(output_filename)` 写盘；`read_pot` 读回；`se_pot_wav` + `tint/sint` 算矩阵元。
   独立示例 `potuse1.f`/`potuse2.f`/`genqed.f` 演示第 4 步。

### 5.2 C 层（faclib）接口
宏定义集中在 `faclib/cf77.h`（cfortran `CCALLSFSUBn`）：

| C 宏 | Fortran 子程序 | 声明位置 | 调用点 | 含义 |
|---|---|---|---|---|
| `INIQED(z,n,knucl,rms)` | `iniqed(z0,nmax0,knucl0,rms)` | `cf77.h:103–105` | `faclib/nucleus.c:565`、`faclib/radial.c:13078` 等 | 初始化模型 QED 势（$10\le Z\le120$，`knucl=1` 表示有限核） |
| `RGMQED(&a,&b)` | `rgmqed(a,b)` | `cf77.h:87–89` | `faclib/orbital.c:3510` | 取半对数网格参数 `al,bt` |
| `LOCSEP(i,nr,ur,vr)` | `locsep(i,nr,ur,vr)` | `cf77.h:83–85` | `faclib/orbital.c:4129`（`SetPotentialSE`） | 把局域自能势插值到 FAC 径向网格 `pot->ZSE[i]`（写出前取负号） |
| `FSEDAT(k,n,n,z,&a,&b)` | `FSEdat(ka,n1,n2,iz,SE_pnt,SE_ext)` | `cf77.h:91–94` | `faclib/coulomb.c:610` | 取无量纲点核/有限核自能 $F(Z\alpha)$ |
| `RADFND(i,&r)` | `radfnd(ik,rn)` | `cf77.h:81` | `faclib/orbital.c:4137` | 节点位置（有效核电荷） |
| `UVIP3P(...)` | `toms/uvip3p.f` | `cf77.h:115–122` | 多处 | Akima 三次样条插值 |

`faclib/radial.c:9411` 的 `QED1E(k0,k1)` 汇总 `RadialNMS`（$nms$）、VP（`potential->ZVP[i]`）与 `SelfEnergy`，经 `qed1e_array` 缓存（带 OpenMP 锁）；`faclib/structure.c` 在矩阵元（`structure.c:1454,1507,2094`）与能级（`structure.c:2936`）中加入该修正。模式控制来自 `SetSE`/`SetVP`（`radial.c:1753–1795`）与脚本函数（手册 `manual.tex:3528–3545,3628–3636`）。

### 5.3 输入输出数据文件
- `potgen.res`：日志（单元 11），记录网格、氢样波函数能量与迭代次数、控制检查表。
- 用户命名的辅助数据文件（`write_pot`/`read_pot`）：依次存 `ii`、`z`、`kk_se(1:5)`、$r$ 与 $rV_{\rm loc}(\kappa)$、$rV_U$、$rV_{\rm WK}$、$rV_{\rm nuc}^{\rm(nonpoint)}$、`ns_proj` 与各态量子数、`Dab`、各投影波函数 `up/uq`、最后存 `knucl,inucl,rnucl,al,bt,h`。
- `wk.dat`：`wk.f` 中被注释掉的 WK 势调试输出。
- `1s_p.dat`、`2p_m.dat` 等：`potuse2.f` 读入的波函数文件，首行 `kappa n energy`，其后每行 `r G(r) F(r)`。
- 常见参数：`z` 电荷（10–120）、`knucl`（0 点核 / 1 Fermi / 2 均匀球 / 3 Gaussian；C 入口只接受 0/1）、`rms` 核均方根半径（fm，0 表示点核）、`nmax` 最大主量子数、`n/iw` 主量子数/是否含局域势开关、`nr` 目标网格点数、`al/bt/h/r1/r2` 网格参数、`uehl/v_wk/unuc` 均为“乘过 $r$”的势。

## 6. 上下游关系与构建（`Makefile.in`）

- `Makefile.in` 使用 `@SET_MAKE@`、`@F77@`、`@FFLAGS@`、`@TOPDIR@` 等 autoconf 变量；规则 `.f.o: ${FC} -c ${FFLAGS} $<`；目标 `modqed: ${OBJS}` 执行 `ar r ${TOPDIR}/libfac.a ${OBJS}`，即把 12 个目标文件并入 FAC 主库；`clean` 删除 `*.o *.a *~`。
- 纳入 `SRC` 的 12 个文件：`iniqed.f genqed.f atom_data.f segrid.f pot_wav.f se_pot.f dirac.f integr.f uehling.f fse_dat.f nucl.f wk.f`。
- 未纳入 `SRC` 的 5 个文件：`grid.f`（旧网格，已被 `segrid.f` 取代）、`potgen_main.f`（旧主程序，与 `iniqed.f` 符号冲突）、`potuse1.f`/`potuse2.f`（示例主程序）、`read_pot.f`（被示例依赖，但 `genqed.o` 也需要它，故独立链接 `genqed` 时需手工补上）。
- 依赖方向：`faclib`（C 层）→ `libfac.a` 中的 `iniqed/rgmqed/locsep/fsedat` → Fortran 内部依赖 `dirac/integr/nucl/uehling/wk/se_pot/fse_dat` → `toms/uvip3p.f`（插值）与 `coul/mohrfin.f`（C 层核半径拟合）。
- 用户侧开关：脚本函数 `SetSE(n,m[,s,p])`（模式 `k=4/5/6/7` 启用本模块模型势）、`SetVP(vp)`、`PrintQED()`；`ConfigEnergy` 的 `m=2` 表示只包含自能能量移动（手册 `manual.tex:3374–3376`）。

## 7. README 维护记录（自底向上）

- **定位与职责**：`modqed/` 提供 QED 自能与真空极化修正，由 `faclib/` C 层调用并并入 `libfac.a`。
- **底层依据**：`dirac.f`、`se_pot.f`、`uehling.f`、`wk.f`、`fse_dat.f`、`iniqed.f`、`rgmqed.f`。
- **输入/输出**：输入核电荷、轨道与径向网格；输出 QED 势、能量修正与用户侧开关 `SetSE/SetVP/PrintQED` 所需数据。
- **验证与回归**：无独立自动基准；通过原子结构输出、能量移动和 `demo` 回归间接验证。
- **已知限制**：部分旧主程序未纳入构建；`potgen_main.f` 与 `iniqed.f` 符号冲突；QED 开关改变物理模型，不能视为兼容补丁。
- **公式核查**：
  - 相对论 Dirac 耦合径向方程：\underline{$\left(\frac{d}{dr}+\frac{\kappa}{r}\right)P=\alpha\left(\varepsilon-V+\frac{2}{\alpha^2}\right)Q$}
  - 1s 对数项：\underline{$\pm\frac{8}{3}\ln(Z/137.0359895)$}
  - SE 标度因子 $\frac{\alpha}{\pi}\frac{(Z\alpha)^4}{dn^3}c^2$：源码命中 `se_pot.f`、`iniqed.f`。
- **导航**：父级 [`../README.md`](../README.md)；核心库 [`../faclib/README.md`](../faclib/README.md)；手册 [`../doc/README.md`](../doc/README.md)。

[返回上级](../README.md)