# demo/ionization/ref 参考数据

## 目录定位

存放 FAC 生成的电子碰撞电离（**ionization**）算例参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 文件头为 `FAC 1.1.5`。

生成脚本：`demo/ionization/fe17_ionization.py`（等价 SFAC 脚本 `fe17_ionization.sf`）。

## 逐文件说明

### 1. `ne_f.lev` —— 电离前后能级表（Type = 1）

- **数据格式**：头部 `Type = 1`、`Fe Z = 26.0`、`NBlocks = 2`、`E0 = 0, -3.12293444E+04`。块 1：`NELE = 10, NLEV = 1`（Ne-like Fe 基态 `2p6`，`ILEV = 0`）；块 2：`NELE = 9, NLEV = 3`（F-like Fe，`2p5` 双重态与 `2s1`）。列头 `ILEV IBASE ENERGY P VNL 2J` + 三列名称串；字段按 `python/rfac.py:511 read_lev()`：`ILEV` 全局序号、`IBASE`、`ENERGY`（相对 `E0` 的激发能，eV）、`P` 宇称、`VNL`（**需按源码表格定义核对**）、`2J`、`ncomplex`/`sname`/`name`。
- **物理量**：Fe XVII → Fe XVIII 电离初态与末态能级，末态能量差即电离阈值。
- **生成脚本**：`fe17_ionization.py:27-30` 的两次 `fac.Structure()`、`MemENTable()`、`PrintTable(..., 'ne_f.lev', 1)`。
- **make check 比对**：`demo/check.py:96 check_en()`：`NBlocks` 相等、`E0` 相对 1%、`ENERGY` `atol = 10`/`rtol = 0.01`、名称字符串一致。

### 2. `ne.ci` —— 电子碰撞电离截面表（Type = 6）

- **数据格式**：头部 `Type = 6`、`NELE = 10`、`NTRANS = 3`、`QKMODE = 5`、`NPARAMS = 4`、`PWTYPE = 0`、`NTEGRID = 2`（`1.26024832E+03`、`1.39456856E+03`）、`ETYPE = 1`、`NEGRID = 6`。用户能量网格由脚本 `fac.SetUsrCIEGrid([500.0, 900.0, 1.3e3, 1.7e3, 2.1e3, 4.2e3, 6.0e3, 8.0e3])` 指定。按 `python/rfac.py:927 read_ci()`：每条跃迁先给 `bound_index, bound_2J, free_index, free_2J, Delta E, Delta L`，随后一行 `NPARAMS = 4` 个参数 `parameters`，再对每个用户能量给两列 `collision strength`、`crosssection`（`a_sub[0]` 为碰撞能量，见 `read_ci()` 注释）。
- **物理量**：Ne-like Fe 基态/激发态电离为 F-like Fe 各末态的分波（`Delta L` 标记电离电子轨道角动量）碰撞强度与电离截面。
- **生成脚本**：`fe17_ionization.py:33-36` 的 `SetUsrCIEGrid` + `fac.CITable('ne.ci.b', ['fe17'], ['fe18'])` + `PrintTable`。
- **make check 比对**：`demo/check.py:158 check_ci()`；先按 `bound_index`/`free_index` 排序；`collision strength` `atol = 1e-3`/`rtol = 0.02`，`crosssection` `atol = 0.01`/`rtol = 0.1`，`Delta E` `atol = 1`/`rtol = 0.01`，`parameters`、`EGRID`、`TEGRID`、`USR`、`TE0` 相对误差 1%，`bethe`/`born` 1%。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **电离阈值与初末态结构**
   - 简介：由初态离子与电离后离子的能级差给出阈能 $\Delta E$。
   - 公式：$I_i=E_{\rm ion}^{(N-1)}+E_e-E_i^{(N)}$，连续态能量守恒。
   - 源码对应：`fe17_ionization.py:19-30`；`python/rfac.py:511 read_lev()`；`demo/check.py:96 check_en()`。

2. **电子碰撞电离（EII）截面**
   - 简介：入射电子击出束缚电子，末态含两个连续电子；FAC 用扭曲波展开。
   - 公式：$\sigma_{ij}(E)=\dfrac{a_0^2}{g_i}\dfrac{\Omega_{ij}(E)}{E_i}$，$E_i$ 为以 Ryd 计的入射能量。**EII 截面没有 $\pi$ 因子**（`doc/manual.tex:1053–1061`、`doc/papers/ionization.tex:94` 明确指出与 CE 的差别源于自由/束缚轨道归一化不同）；Maxwell 速率系数 $q_{ij}=\sqrt{8/(\pi m_e)}(kT)^{-3/2}\int\sigma_{ij}(E)E e^{-E/kT}dE$。
   - 源码对应：`fe17_ionization.py:35 fac.CITable()`；`python/rfac.py:927 read_ci()`；`demo/check.py:158 check_ci()`。

3. **分波/子壳层贡献（Delta L）**
   - 简介：`Delta L` 区分从不同亚壳层电离出的电子分波，反映部分截面。
   - 公式：$\sigma_{ij}=\sum_{l}\sigma_{ij}^{(l)}$，各 $l$ 通道在表中分行给出；具体分波约定**需按源码表格定义核对**。
   - 源码对应：`read_ci()` 第 974、994 行（`delta_l`、`Delta L` 字段）。

4. **Maxwell 平均速率（辅助）**
   - 简介：`demo/tests/maxwell_rate.py` 演示将截面表转为 Maxwell 速率系数。
   - 公式：$\langle\sigma v\rangle=\sqrt{\dfrac{8}{\pi m_e}}(kT)^{-3/2}\displaystyle\int_0^\infty \sigma(E)E\,e^{-E/kT}\,dE$（补上平方根；与 `faclib/rates.c` 的 `Maxwell=1.12837967√(e/T)e^{-e/T}/T` 归一化一致）。
   - 源码对应：`demo/tests/maxwell_rate.py:40-41 fac.MaxwellRate()`。

## 使用方式

- `cd demo/ionization && make check`：运行 `fe17_ionization.py` 生成 `ne_f.lev`、`ne.ci`，再 `python ../check.py ne.ci ref/ne.ci` 等。
- 手工比对：`python ../check.py ne_f.lev ref/ne_f.lev`；可用 `read_ci()` 查看各能量点碰撞强度。
- `make ref` 重新生成参考；`make clean` 清除 `*.b` 与输出。

## 注意事项

- `demo/README` 记载 FAC=1.1.4，实际文件头为 `FAC 1.1.5`。
- 用户自定义能量网格 `SetUsrCIEGrid` 的值（单位需核对）必须与原脚本一致，否则 `USR`/`EGRID` 比对失败。
- `check_ci` 按 `bound_index`/`free_index` 排序，`openmp` 顺序差异不影响结果。
- `QKMODE = 5`、`NPARAMS = 4` 的拟合参数定义以 FAC 手册/`python/rfac.py` 表格定义为准，需按源码表格定义核对。

## 验证状态

- 实测 `ne_f.lev`、`ne.ci` 两项 `check.py` 比对均 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- 命令、容差与产物清单见 [父 README](../README.md) §7–§8。

[返回上级](../README.md)