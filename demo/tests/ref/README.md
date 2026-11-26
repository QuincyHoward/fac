# demo/tests/ref 参考数据

## 目录定位

存放 FAC 测试算例（**tests**）的参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 本目录包含哈密顿量对角化测试（`diagh_O_a.en`）与简单 CRM 谱测试（`O.sp`）；文件头为 `FAC 1.1.5`。

生成脚本：`demo/tests/diag_hamiltonian.py`（`diagh_O_a.en`）、`demo/tests/simple_crm.py`（`O.sp`）；`demo/tests/maxwell_rate.py` 为第三个测试脚本，但不生成 `ref/` 中的文件。

## 逐文件说明

### 1. `diagh_O_a.en` —— 无 CI 的氧能级表（Type = 1）

- **数据格式**：头部 `Type = 1`、`O Z = 8.0`、`NBlocks = 8`、`E0 = 2, -5.24760131E+02`。块 1：`NELE = 7, NLEV = 5`（O II `2p3`），可见多条 `ENERGY = 0` 的不同 $2J$ 能级（因 `SetCILevel(-1)` 关闭 CI，精细结构劈裂为零）；后续块含 `NELE = 8, NLEV = 78`（O I `2p4/2p3 3s/3d` 等）等。列头 `ILEV IBASE ENERGY P VNL 2J` + 三列名称串；字段按 `python/rfac.py:511 read_lev()`：`ENERGY` 相对 `E0`、`P` 宇称、`VNL`（**需按源码表格定义核对**）、`2J`、组态名。
- **物理量**：中性氧（及 O II 等离子）在**关闭组态相互作用**时的相对论能级，用于检验哈密顿量对角化与 CI 开关行为。
- **生成脚本**：`diag_hamiltonian.py:6-18` 的 `SetCILevel(-1)`、`Structure('diagh_O.en', ['g1','g3','g4','ion'])`、`MemENTable()`、`PrintTable(..., 'diagh_O_a.en')`。
- **make check 比对**：`demo/check.py:96 check_en()`；`NBlocks` 必须相等、`E0` 1%、`ENERGY` `atol = 10`/`rtol = 0.01`、字符串列逐字一致。

### 2. `O.sp` —— 氧 CRM 谱表（Type = 7）

- **数据格式**：头部 `Type = 7`、`O Z = 8.0`、`NBlocks = 53`。每块含 `NELE`、`NTRANS`、`TYPE = 0000000`、`IBLK`、`ICOMP`、`FBLK`、`FCOMP`（初/末块及组态标识）。按 `python/rfac.py:1085 read_sp()`，数据行 6 列：`block`、`level`、`abs. energy`（绝对能量）、`population`（布居）、`Delta E`（跃迁能）、`emissivity`（发射率）。示例首行 `0 0 0.000000E+00 5.2446E-01 5.0000E+00 0.0000E+00`。
- **物理量**：O I 简单 CRM 的线谱：电子温度 1.0（脚本 `SetEleDist(0, 1.0, -1, -1)`）、电子密度 1.0，含 TR/CE 速率的稳态布居与谱线发射率。
- **生成脚本**：`simple_crm.py:20-52` 的 `Structure`、`TransitionTable`、`CETable`，随后 `AddIon(8,1,'O_crm/O')`、`SetTRRates(0)`、`SetCERates(1)`、`LevelPopulation()`、`SpecTable('O.b.sp', 0)`、`PrintTable(..., 'O.sp')`。
- **make check 比对**：`demo/check.py:197 check_sp()`；`abs. energy`/`Delta E` `atol = 1`/`rtol = 0.01`，`emissivity` `atol = 1e-10`/`rtol = 0.05`，`population` `atol = 1e-30`/`rtol = 0.05`。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **能级结构与 CI 开关（哈密顿量对角化测试）**
   - 简介：`SetCILevel(-1)` 关闭组态相互作用，检验单组态 Dirac–Fock 对角化的确定性与可重复性。
   - 公式：$\hat H_{\rm DC}\psi_i=E_i\psi_i$；关闭 CI 时 $H$ 按组态块对角化，$E_i\approx\langle\Phi_i|\hat H|\Phi_i\rangle$。
   - 源码对应：`diag_hamiltonian.py:15-18`；`python/rfac.py:511 read_lev()`；`demo/check.py:96 check_en()`。

2. **辐射跃迁与碰撞激发（CRM 输入）**
   - 公式：$A_{ji}\propto \omega^{2k+1}|\langle j\|D^{(k)}\|i\rangle|^2$；$\sigma_{ij}=\pi a_0^2\Omega_{ij}/(g_i E_i)$。
   - 源码对应：`simple_crm.py:34-35 TransitionTable()/CETable()`；`python/rfac.py:690 read_tr()`、`810 read_ce()`。

3. **碰撞–辐射模型布居（CRM）**
   - 简介：求解稳态速率方程得到各能级布居。
   - 公式：$\sum_{j\neq i}N_j R_{j\to i}-N_i\sum_{j\neq i}R_{i\to j}=0$，其中 $R$ 含辐射跃迁率与电子碰撞速率系数。
   - 源码对应：`simple_crm.py:42-50`（`AddIon`、`SetBlocks`、`SetEleDist`、`SetTRRates`、`SetCERates`、`SetEleDensity`、`LevelPopulation`）。

4. **谱线发射率**
   - 公式：$\varepsilon_{ij}=N_i A_{ij}$（**photons/s**，乘归一化线型后为谱）；`hν` 单独存于 `r.energy`，若需能量发射率须另乘 $h\nu_{ij}$（`faclib/crm.c:4495`、`manual.tex:1141–1143`）。
   - 源码对应：`simple_crm.py:51-52 SpecTable()`、`PrintTable(..., 'O.sp')`；`python/rfac.py:1085 read_sp()`；`demo/check.py:197 check_sp()`。

5. **Maxwell 速率系数（测试脚本，不存参考表）**
   - 公式：$\langle\sigma v\rangle=\sqrt{\dfrac{8}{\pi m_e}}(kT)^{-3/2}\int\sigma(E)E e^{-E/kT}dE$。
   - 源码对应：`demo/tests/maxwell_rate.py:40-41 fac.MaxwellRate()`；该脚本产物 `Neb.cir`/`Neb.cer` 不在 `ref/` 与 `RESULTS` 中。

## 使用方式

- `cd demo/tests && make check`：`RESULTS = diagh_O_a.en O.sp`，先运行 `simple_crm.py`、`diag_hamiltonian.py`、`maxwell_rate.py`，再对两项结果执行 `python ../check.py <file> ref/<file>`。
- 手工比对：`python ../check.py O.sp ref/O.sp`；用 `rfac.read_sp()` 查看 `population`、`emissivity`。
- `make ref` 仅拷贝 `RESULTS` 列表文件；`make clean` 清理输出与 `O_crm/` 之外的 `*.b`（脚本自建 `O_crm` 目录需手工清理）。

## 注意事项

- `demo/README` 声明 FAC=1.1.4 基准，文件头为 `FAC 1.1.5`。
- `diagh_O_a.en` 中多条能级能量严格为 0 是关闭 CI 的预期结果；若误开 CI 将导致 `ENERGY` 比对失败。
- `O.sp` 的 `population`、`emissivity` 使用极小绝对容差（1e-30、1e-10）配合 5% 相对容差，弱线的数值噪声需关注。
- `maxwell_rate.py` 属于测试脚本但不产生参考数据；`Makefile` 中 `RESULTS` 仅列两项。字段/单位不确定处需按 `python/rfac.py` 表格定义核对。

## 验证状态

- 实测 `diagh_O_a.en`、`O.sp` 两项 `check.py` 比对均 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- `maxwell_rate.py` 产物无基准、不参与回归；命令与容差见 [父 README](../README.md) §7、§9。

[返回上级](../README.md)