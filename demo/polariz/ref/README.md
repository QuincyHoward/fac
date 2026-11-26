# demo/polariz/ref 参考数据

## 目录定位

存放 FAC 偏振模块（`pfac.pol`）算例的参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 算例为类 He 铁（Fe XXV）谱线偏振；生成脚本：`demo/polariz/data.py`（FAC 表格）与 `demo/polariz/pol.py`（磁子能级布居与偏振）。

## 逐文件说明

### 1. `ta.en` —— 能级表（Type = 1）

- **数据格式**：头部 `Type = 1`、`Fe Z = 26.0`、`NBlocks = 1`、`E0 = 0, -1.81043457E+04`；块内 `NELE = 2`、`NLEV = 7`，列头 `ILEV IBASE ENERGY P VNL 2J` + 三列名称串。字段按 `python/rfac.py:511 read_lev()`：`ENERGY` 相对 `E0`、`P` 宇称、`VNL`（**需按源码表格定义核对**）、`2J`、组态名（`1s2`、`1s1 2s1`、`1s1 2p1`）。
- **物理量**：He-like Fe 的 7 个精细结构能级，作为偏振计算的初末态。
- **生成脚本**：`data.py:12-14` 的 `Structure('tb.en', ['g0','g1'])`、`MemENTable`、`PrintTable(..., 'ta.en', 1)`。
- **make check 比对**：`demo/check.py:96 check_en()`；因在 `RESULTS` 中，按 `E0` 1%、`ENERGY` `atol = 10`/`rtol = 0.01`、名称串一致比较。

### 2. `ta.tr` —— 辐射跃迁率表（Type = 2，含多种多极）

- **数据格式**：头部 `Type = 2`、`Fe Z = 26.0`、`NBlocks = 7`，每块含 `NELE`、`NTRANS`、`MULTIP`（如 -1，代表磁偶极 M1；脚本对 $m=-1,1,-2,2$ 生成 E1/M1/E2/M2）、`GAUGE = 2`、`MODE = 1`。数据行按 `python/rfac.py:690 read_tr()` 为 `upper_index, upper_2J, lower_index, lower_2J, Delta E, gf, rate, multipole`。
- **物理量**：`g0→g1`、`g1→g1` 之间各多极跃迁的率与 `gf`，供 `SetMLevels('tb.en','tb.tr')` 建立磁子能级跃迁率。
- **生成脚本**：`data.py:16-19` 的 `TransitionTable('tb.tr', ..., m)` 循环（$m=-1,1,-2,2$）与 `PrintTable(..., 'ta.tr', 1)`。
- **make check 比对**：`demo/check.py:122 check_tr()`；按上下能级索引排序；`gf` `atol = 1e-4`/`rtol = 0.02`，`rate` `atol = 1e4`/`rtol = 0.05`，`Delta E` 1%，`multipole` `atol = 1e-5`/`rtol = 0.05`。

### 3. `ta.ce` —— 磁子能级分辨激发表（Type = 3, MSUB = 1）

- **数据格式**：头部 `Type = 3`、`NELE = 2`、`NBlocks = 6`、`MSUB = 1`、`PWTYPE = 1`；多跃迁块。按 `python/rfac.py:810 read_ce()` 的 MSUB 分支：每条跃迁含上下能级序号/`2J`/`Delta E`/`nsub`，Bethe/Born 系数，每个能量点的 `collision strength`、`crosssection` 数组，以及 `ratio collision strength`。
- **物理量**：`g0→g1`、`g1→g1` 的磁子能级分辨碰撞激发率，`pol.py:7 SetMCERates('tb.ce')` 的输入。
- **生成脚本**：`data.py:21-23` 的 `CETableMSub('tb.ce', ['g0'], ['g1'])`、`CETableMSub('tb.ce', ['g1'], ['g1'])`、`PrintTable`。
- **make check 比对**：`demo/check.py:138 check_ce()`（`MSUB = 1` 分支），`ratio collision strength` `atol = 0.1`，其余同前。

### 4. `pop.txt` —— 磁子能级布居表（文本，由 `pfac.pol` 输出）

- **数据格式**：文本，头部注释 `# FAC 1.1.5`、`# Energy = 8.00000E+03`、`# ESigma = 1.20000E+01`、`# Density = 1.00000E+00`、`# IDR = -1`。按 `faclib/polarization.c:1682-1697 PopulationTable()` 的写文件格式：
  - 每个能级先一行 `i  dtotal`：能级序号与该能级总布居；
  - 随后对每个磁量子数 $m_1$（从 $-J$ 到 0）一行 `p  -m1  c`：`p = levels[i].ic` 为组态/复合体序号，`-m1` 为磁量子数投影（非负），$c = {\rm pop}[t]/{\rm dtotal}$（$m_1\neq0$ 时再乘 0.5）为归一化子能级布居；每个能级后空一行。
- **物理量**：在电子束能量 8 keV、能量展宽 12 eV、密度 1.0 条件下求解的磁子能级布居，体现碰撞激发的各向异性。
- **生成脚本**：`pol.py:4-11` 的 `SetMLevels()`、`SetEnergy()`、`SetMCERates()`、`SetDensity()`、`PopulationTable('pop.txt')`。
- **make check 比对**：**不参与**。`demo/polariz/Makefile` 中 `# RESULTS = ta.ce ta.en ta.tr pol.txt pop.txt` 被注释，实际 `RESULTS = ta.en ta.tr ta.ce`；`demo/check.py:check()` 也没有 `.txt` 分派（会抛 `TypeError`）。这是人工检查的辅助输出。

### 5. `pol.txt` —— 谱线偏振表（文本，由 `pfac.pol` 输出）

- **数据格式**：文本，头部注释比 `pop.txt` 多一行 `# ETrans = 0.00000E+00`。按 `faclib/polarization.c:2122-2123 PolarizationTable()` 的 `fprintf` 格式，数据行 8 列依次为：
  - `levels[i1].nele`（上能级电子数）、`i1`（上能级序号）、`i2`（下能级序号）、`k`（多极矩，带符号：E1=1、M1=-1、E2=2、M2=-2）、`e`（跃迁能，eV，`(E_upper-E_lower)*HARTREE_EV`）、`tem`（$N_{\rm upper}A$，线强权重）、`b`（未偏振总强度）、`a`（偏振分量）；偏振度 $P=a/b$。
- **物理量**：各条谱线的偏振度，由磁子能级布居与 3j/6j 符号给出。
- **生成脚本**：`pol.py:13-16` 的 `Orientation()` 与 `PolarizationTable('pol.txt')`。
- **make check 比对**：**不参与**（同 `pop.txt`，见 Makefile 注释行与 `check.py` 扩展名分派）。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **能级与辐射跃迁（E1/M1/E2/M2）**
   - 公式：$A_{ji}\propto \omega^{2k+1}|\langle j\|D^{(k)}\|i\rangle|^2/(2J_j+1)$。
   - 源码对应：`data.py:12-19`；`python/rfac.py:690 read_tr()`；`demo/check.py:122 check_tr()`。

2. **磁子能级布居与取向/排列参数**
   - 简介：定向电子碰撞使磁子能级非统计布居，产生排列（alignment）与取向（orientation）。
   - 公式：$B_k(J)=\sum_{M}(-1)^{J-M}\sqrt{2k+1}\begin{pmatrix}J&k&J\\-M&0&M\end{pmatrix}\rho_{MM}$；$\rho_{MM}={\rm pop}_M/\sum_M{\rm pop}_M$。
   - 源码对应：`faclib/polarization.c:1798–1816`（`B_k`/`BL[k][i]` 的真实实现；1682–1697 只是写表函数）；`pol.py:10-13 PopulationTable()/Orientation()`；`pop.txt` 数据行。

3. **谱线偏振度**
   - 简介：观测方向垂直于电子束时，线偏振度由排列参数与 Wigner 3j/6j 符号决定。
   - 公式：FAC 输出的是第 8 列与第 7 列之比 $P=a/b$，其中 $a=\sum_t F_t PL2_t A_t B_t(J_i)$、$b=\sum_t PL_t A_t B_t(J_i)$，$PL_t=P_{2t}(\cos\theta)$、$PL2_t$ 为 $\mu=2$ 缔合 Legendre 项且 $PL2_0=0$，$k<0$ 时 $F_t$ 变号（`faclib/polarization.c:2087–2091,2098–2102`）。**手册与源码均未定义 $I_\parallel/I_\perp$ 的符号约定**，不能把 $a/b$ 断定为初等比值 $(I_\perp-I_\parallel)/(I_\perp+I_\parallel)$ 或其反号；$A_t\propto (2k+1)\sqrt{(2J_i+1)(4t+1)}(-1)^{(J_i+J_f)/2}\begin{pmatrix}k&k&2t\\1&-1&0\end{pmatrix}\begin{Bmatrix}k&k&2t\\J_i&J_i&J_f\end{Bmatrix}$。
   - 源码对应：`faclib/polarization.c:2073-2105`（`W3j`/`W6j` 计算 `AL[t]`、`FL[t]` 与 `a`、`b`）与 `2122-2123`（写 `pol.txt`）；`python/ppol.c:387 PPolarizationTable()`；`pol.py:16`。

4. **磁子能级碰撞激发率**
   - 公式：$\Omega_{iM_i\to jM_j}$ 由 `CETableMSub` 给出，进入 $\rho_{MM}$ 的速率方程 $0=\sum_{jM'} \rho_{jM'}R_{jM'\to iM}-\rho_{iM}\sum_{jM'}R_{iM\to jM'}$。
   - 源码对应：`data.py:21-23`；`pol.py:7`；`python/rfac.py:810 read_ce()`（MSUB 分支）。

## 使用方式

- `cd demo/polariz && make check`：先运行 `data.py`、`pol.py` 生成 `ta.en`、`ta.tr`、`ta.ce`（以及 `pop.txt`、`pol.txt`），再对 `RESULTS` 中三个文件执行 `python ../check.py <file> ref/<file>`。
- 手工检查偏振：`python pol.py` 后查看 `pop.txt`（布居）与 `pol.txt`（末两列比值 $P=a/b$）；`pop.txt`/`pol.txt` 不在自动回归范围。
- `make ref` 只拷贝 `RESULTS` 列表中的三个文件到 `ref/`。

## 注意事项

- `demo/README` 声明 FAC=1.1.4 基准，文件头为 `FAC 1.1.5`。
- `pol.txt`、`pop.txt` 是 `pfac.pol` 的文本输出，**不在 `make check` 覆盖范围**（Makefile 中对应行被注释，`check.py` 无 `.txt` 分派）；若要纳入回归需扩展 `check.py`。
- `pol.txt` 中多极列 `k` 为带符号整数，`k=0` 的行被跳过；偏振度由 `a/b` 计算，与电子束方向约定有关（`SetEnergy` 中 8 keV 与 12 eV 展宽需与参考一致）。
- `ta.ce`/`ta.tr` 的磁子能级索引与 `ta.en` 的 `ILEV` 对应，修改任一结构文件都会破坏偏振结果；列含义不确定处需按 `faclib/polarization.c`、`python/rfac.py` 表格定义核对。

## 验证状态

- 实测 `ta.en`、`ta.tr`、`ta.ce` 三项 `check.py` 比对均 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- `pop.txt`、`pol.txt` 不在 `RESULTS`，仅作人工检查；详见 [父 README](../README.md) §6、§8。

[返回上级](../README.md)