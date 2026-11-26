# demo/NeL/ref 参考数据

## 目录定位

存放 FAC 生成的 Ne VIII（Z=10，3 电子）碰撞–辐射模型（CRM）算例参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 文件头为 `FAC 1.1.5`。

生成脚本：`demo/NeL/ne.py`（原子结构、跃迁、激发）与 `demo/NeL/spec.py`（CRM 布居与谱）。前缀 `Ne03a.*` 为输出表，`Ne03b.ham` 为哈密顿量文件（`p='Ne03'`，见两脚本）。字段口径与 API 链详解见 [上级 README](../README.md)。

## 逐文件说明

### 1. `Ne03a.en` —— 能级表（Type = 1）

- **数据格式**：头部 `Type = 1`、`Ne Z = 10.0`、`NBlocks = 3`、`E0 = 0, -2.79557571E+03`；三块 `NLEV` 分别为 **8 / 7 / 9（共 24 能级）**，块内 `NELE = 3`，列头 `ILEV IBASE ENERGY P VNL 2J` + 三列名称串（`python/rfac.py:511 read_lev()`：`ENERGY` 相对 `E0`，`P` 宇称，`VNL` 组态数值标签，`2J` 为 2 倍总角动量）。
- **物理量**：Ne VIII 的 `1s2 2s/2p`（n=2）、`3s/3p/3d`（n=3）、`4s/4p/4d/4f`（n=4）、`5s/5p/5d/5f/5g`（n=5）组态精细结构能级（脚本 `nmax = 5`）。
- **生成脚本**：`ne.py:39-45` 的 `Structure()`、`MemENTable()`、`PrintTable(..., 'Ne03a.en')`。
- **make check 比对**：`demo/check.py:96 check_en()`；`E0` 1%、`ENERGY` `atol = 10`/`rtol = 0.01`，名称串逐字一致。

### 2. `Ne03a.tr` —— 辐射跃迁率表（Type = 2）

- **数据格式**：头部 `Type = 2`、`NELE = 3`、`NBlocks = 10`，每块含 `NTRANS`、`MULTIP`、`GAUGE = 2`、`MODE = 1`。按 `python/rfac.py:690 read_tr()`，数据行 8 列为 `upper_index, upper_2J, lower_index, lower_2J, Delta E, gf, rate, multipole`：上下能级序号与 `2J`、跃迁能、`gf` 加权振子强度、跃迁率（s⁻¹）、多极矩参数。
- **物理量**：`g2→g3`、`g2→g4`、`g2→g5` 等组态间电偶极/高阶跃迁率。
- **生成脚本**：`ne.py:48-52` 的 `TRTable()` 循环与 `PrintTable(..., 'Ne03a.tr')`。
- **make check 比对**：`demo/check.py:122 check_tr()`；按 `lower_index`/`upper_index` 排序；`Delta E` `atol = 1`/`rtol = 0.01`，`gf` `atol = 1e-4`/`rtol = 0.02`，`rate` `atol = 1e4`/`rtol = 0.05`，`multipole` `atol = 1e-5`/`rtol = 0.05`。

### 3. `Ne03a.ce` —— 碰撞激发表（Type = 3）

- **数据格式**：头部 `Type = 3`、`NELE = 3`、`NBlocks = 5`，块内 `NTRANS = 1,2,15,21,27`，`QKMODE = 0`、`MSUB = 0`、`PWTYPE = 0`、`NTEGRID = 1`、`TE0 = 2.00527039E-01`、`ETYPE = 1`、`NEGRID = 6`。字段按 `python/rfac.py:810 read_ce()`：跃迁索引/`2J`/`Delta E`/`nsub`、Bethe/Born 系数、每个能量点的 `collision strength` 与 `crosssection`（ASCII 单位 $10^{-20}\,\mathrm{cm^2}$，见 `faclib/dbase.c:5809-5814`）。
- **物理量**：`g2 → g3/g4/g5` 的电子碰撞激发截面，供 CRM 的 `SetCERates` 使用。
- **生成脚本**：`ne.py:55-61` 的 `CETable()` 循环与 `PrintTable(..., 'Ne03a.ce')`。
- **make check 比对**：`demo/check.py:138 check_ce()`，容差同 excitation 目录（`collision strength` `atol = 1e-3`/`rtol = 0.05`；`crosssection` `atol = 0.01`/`rtol = 0.1`；网格 1%）。

### 4. `Ne03b.ham` —— 哈密顿量矩阵（二进制）

- **数据格式**：二进制，不可用文本读取。按 `python/rfac.py:1519 read_ham()`：先是 `ng0`、`ng`、对称群标识数组 `kg[]`、`ngp`、`kgp[]`；随后最多 `MAX_SYMMETries = 256` 个对称块，每块含 `s`、`dim`、`orig_dim`、`n_basis`、`basis[]`、非零元个数 `n`，以及三元组 `(i, j, value)`（`i`、`j` 为 4 字节整数，`value` 为 8 字节双精度）。具体存储顺序**需按源码表格定义核对**。
- **物理量**：CI 哈密顿量稀疏矩阵，对角化给出 `Ne03a.en` 的能级与混合系数。
- **生成脚本**：`ne.py:39`、`42` 中 `Structure(p+'b.en', p+'b.ham', [...])` 写出。
- **make check 比对**：`demo/check.py:221 check_ham()`；`read_ham()` 解析后逐块比较 `value`，容差 `atol = 1e-5`、`rtol = 1e-3`（字符串/结构字段须一致）。

### 5. `Ne03a.rt` —— CRM 速率矩阵表（Type = 8）

- **数据格式**：头部 `Type = 8`、`NBlocks = 1`、`NTRANS = 10`、`EDEN = 1.0`、`EDIST = 0`、`NPEDIS = 3`（电子温度分布参数：`1.25E+02`、`1.25E-18`、`1.25E+04`）、`PDEN = 0`、`PDIST = 0`、`NPPDIS = 3`。按 `python/rfac.py:1458 read_rt()`，数据行按固定列宽解析：`block`、`level`、`NB`（?）、`TR`、`CE`、`RR`、`AI`、`CI`（各物理过程对速率矩阵的贡献）与 `ncomplex`；`NB` 的含义**需按源码表格定义核对**。
- **物理量**：CRM 利率矩阵的稀疏行（每个能级的总跳出/进入率），含辐射跃迁 TR、碰撞激发 CE、辐射复合 RR、自电离 AI、碰撞电离 CI。
- **生成脚本**：`spec.py:58-63` 的 `spm.get_complexes()`、`RateTable()`、`PrintTable(..., 'Ne03a.rt', 1)`；另 `DumpRates('Ne03a.r0/r1/r3')` 未在 `RESULTS` 中。
- **make check 比对**：`demo/check.py:213 check_rt()`，使用默认容差 `atol = 1e-8`、`rtol = 1e-5`（数值型字段数组逐元素比较）。

### 6. `Ne03a.sp` —— CRM 谱表（Type = 7）

- **数据格式**：头部 `Type = 7`、`Ne Z = 10.0`、`NBlocks = 43`。每块含 `NELE`、`NTRANS`、`TYPE`、`IBLK`、`ICOMP`、`FBLK`、`FCOMP`（初/末复合体标识）。按 `faclib/dbase.c:6959-6964 PrintSPTable()`，数据行 **8 列**（UTA 时 9 列）：`upper, lower, energy, strength, rrate, trate, wimp, wstk`。
- **列语义（按 `TYPE` 区分）**：`TYPE=0000000` 为**布居块**（`FCOMP` 空），`strength`=$N_i$ 能级布居、`rrate`=$2J+1$ 统计权重、`trate`=上能级总衰变率 s⁻¹；`TYPE≠0` 为**线发射块**，`strength`=$N_iA_{ij}$（**photons/s**）、`rrate`=$A_{ij}$ s⁻¹、`trate`=上能级总衰变率 s⁻¹。`energy` 在二进制中为 Hartree，ASCII verbose 打印时乘 `HARTREE_EV` 转 eV。
- **`read_sp` 历史误命名**：`python/rfac.py:1110-1118` 只解析前 6 列并错名为 `block/level/abs. energy/population/Delta E/emissivity`，实际对应 `upper/lower/energy/strength/rrate/trate`；`demo/check.py:197 check_sp()` 沿用这些键名，因此其容差标签的物理含义需按此对照理解。
- **物理量**：CRM 求解后的各能级布居与谱线发射率，电子温度 $T=500[((1+z-n_e)/16)]^2$ eV（本例 $q=1+z-n_e=8$，即 125 eV Maxwell）、电子密度 $1.0\times10^{10}$ cm⁻³（见 `spec.py:24-25`）。
- **生成脚本**：`spec.py:53-55` 的 `SpecTable('Ne03b.sp', 0)` + `PrintTable(..., 'Ne03a.sp')`。
- **make check 比对**：`demo/check.py:197 check_sp()`；`abs. energy`(=energy) `atol = 1`/`rtol = 0.01`，`population`(=strength) `atol = 1e-30`/`rtol = 0.05`，`Delta E`(=rrate) `atol = 1`/`rtol = 0.01`，`emissivity`(=trate) `atol = 1e-10`/`rtol = 0.05`。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **能级结构与 CI 哈密顿量**
   - 公式：$\hat H\Psi_k=E_k\Psi_k$，基矢由组态态函数构成，稀疏矩阵见 `Ne03b.ham`。
   - 源码对应：`ne.py:28-45`；`python/rfac.py:1519 read_ham()`；`demo/check.py:221 check_ham()`。

2. **辐射跃迁率与振子强度**（FAC 口径，$\omega$ 以 Hartree 计，$L=|m|$）
   - 公式：$gA_{ji}=2\alpha^3\omega^2 gf_{ij}$，$gf_{ij}=\dfrac{\omega(\alpha\omega)^{2L-2}}{2L+1}|M|^2$；$A_{ji}[\mathrm{s^{-1}}]=\dfrac{2\alpha^3\omega^2}{2J_j+1}gf_{ij}\times R_{\rm AU}$，$R_{\rm AU}=4.13413733\times10^{16}\,\mathrm{s^{-1}}$。
   - 源码对应：`doc/manual.tex:601-620`；`faclib/dbase.c:5452-5473`；`ne.py:48-52 TRTable()`；`python/rfac.py:690 read_tr()`。

3. **电子碰撞激发截面/速率**
   - 公式：$\sigma_{ij}(E)=\dfrac{\pi}{k_i^2g_i}\Omega_{ij}$（$k_i^2=2E_i$，$E_i$ 以 Hartree 计；$g_i=2J_i+1$），$q_{ij}=\langle\sigma v\rangle_T$。
   - 源码对应：`doc/manual.tex:785-791,2853-2859`；`faclib/excitation.c:3718`；`ne.py:55-61 CETable()`；`python/rfac.py:810 read_ce()`。

4. **碰撞–辐射模型（CRM）布居方程**
   - 简介：求解能级布居的稳态线性方程组，速率矩阵由 TR/CE/RR/AI/CI 组成。
   - 公式：$\dfrac{dN_i}{dt}=\sum_{j\neq i}N_j R_{j\to i}-N_i\sum_{j\neq i}R_{i\to j}=0$。
   - 源码对应：`spec.py:33-50`（`AddIon`、`SetTRRates`、`SetCERates`、`LevelPopulation`）；`RateTable()` → `Ne03a.rt`；`python/rfac.py:1458 read_rt()`。

5. **谱线发射率（谱）**
   - 简介：由布居与跃迁率合成线光度；`TYPE≠0` 线发射块的 `strength` 为 **photons/s**，`TYPE=0` 布居块的 `strength` 为 $N_i$。
   - 公式：$S_{ij}=N_iA_{ij}$（photons/s）；能量发射率 $\varepsilon_{ij}(\nu)=N_iA_{ij}h\nu\,\phi(\nu-\nu_{ij})$ 须另乘 $h\nu$（`faclib/crm.c:4495`、`doc/manual.tex:1141–1143`）。
   - 源码对应：`spec.py:53 SpecTable()` → `Ne03a.sp`；`faclib/dbase.c:6955-6964 PrintSPTable()`；`python/rfac.py:1085 read_sp()`；`demo/check.py:197 check_sp()`。

## 使用方式

- `cd demo/NeL && make check`（`RESULTS = Ne03a.ce Ne03a.en Ne03a.rt Ne03a.sp Ne03a.tr Ne03b.ham`），先运行 `ne.py`、`spec.py`，再逐个 `python ../check.py <file> ref/<file>`。
- 手工比对：`python ../check.py Ne03a.sp ref/Ne03a.sp`；二进制哈密顿量用 `check_ham()` 或 `rfac.read_ham()` 读取。
- `make ref` 更新基准；`make clean` 删除结果与 `*.b`。

## 注意事项

- `demo/README` 声明 FAC=1.1.4 基准，文件头却为 `FAC 1.1.5`。
- `Ne03a.sp` 块数多（43），`read_sp` 键 `emissivity`(=trate) / `population`(=strength) 使用绝对容差极小值（1e-10/1e-30），弱线数值差异需关注相对误差；键名为历史误命名，见上文列语义。
- `DumpRates` 生成的 `Ne03a.r0/.r1/.r3` 不在 `RESULTS`，不受 `make check` 覆盖。
- `Ne03b.ham` 为二进制，`read_ham()` 直接 `struct.unpack`，不可用文本编辑器查看；`RT` 中 `NB` 等字段含义需按源码表格定义核对。
- 逐 API 的输入/输出/物理含义与 Mermaid 流程图见 [上级 README](../README.md) §4–§5。

## 验证状态

- 实测 `Ne03a.ce`、`Ne03a.en`、`Ne03a.rt`、`Ne03a.sp`、`Ne03a.tr`、`Ne03b.ham` 六项 `check.py` 比对全部 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- `DumpRates` 产物不在 `RESULTS`，不参与回归；复现流程见 [父 README](../README.md) §6。

[返回上级](../README.md)