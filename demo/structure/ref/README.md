# demo/structure/ref 参考数据

## 目录定位

存放 FAC 生成的原子结构（**structure**）算例参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 算例为 Ne-like Fe 的能级与辐射跃迁；生成脚本：`demo/structure/fe17_structure.py`（等价 SFAC 脚本 `fe17_structure.sf`）。

## 逐文件说明

### 1. `ne.lev` —— 能级表（Type = 1）

- **数据格式**：头部 `FAC 1.1.5`、`Endian = 0`、`TSess`、`Type = 1`、`Fe Z = 26.0`、`NBlocks = 1`、`E0 = 0, -3.12294465E+04`。块内 `NELE = 10`、`NLEV = 37`，列头 `ILEV IBASE ENERGY P VNL 2J`，后接三列组态/能级字符串。按 `python/rfac.py:511 read_lev()`：`ILEV` 全局能级序号、`IBASE` 基索引、`ENERGY`（eV，相对 `E0` 的激发能；`dbase.c:5371–5374` 在 verbose 输出中乘 `HARTREE_EV`）、`P` 宇称（0/1）、`VNL` 数值标签（**需按源码表格定义核对**）、`2J` 为 2 倍总角动量，`ncomplex`/`sname`/`name` 为组态名称串。
- **物理量**：Fe XVII（1s 闭壳层）基态 `2*8`（即 `2p6`）与激发组态 `2*7 3*1`（`2p5 3s/3p/3d`）的 37 个精细结构能级。
- **生成脚本**：`fe17_structure.py:16-35` 的 `SetAtom('Fe')`、`Closed('1s')`、`Config(...)`、`OptimizeRadial(['n2'])`、`Structure('ne.lev.b', ['n2','n3'])`、`MemENTable()`、`PrintTable(..., 'ne.lev', 1)`。
- **make check 比对**：`demo/check.py:96 check_en()`（扩展名 `lev`）；校验 `NBlocks` 相等、`E0` 相对误差 ≤1%、`ENERGY` `atol = 10`、`rtol = 0.01`，字符串列逐字一致。

### 2. `ne.tr` —— 辐射跃迁率表（Type = 2）

- **数据格式**：头部 `Type = 2`、`Fe Z = 26.0`、`NBlocks = 1`；块内 `NELE = 10`、`NTRANS = 30`、`MULTIP = 0`、`GAUGE = 2`、`MODE = 1`。按 `python/rfac.py:690 read_tr()`，数据行 8 列为 `upper_index`、`upper_2J`、`lower_index`、`lower_2J`、`Delta E`、`gf`、`rate`、`multipole`：上下能级序号与 `2J`、跃迁能、`gf` 加权振子强度、辐射跃迁率（s⁻¹）、多极参数。`MULTIP = 0` 与 `GAUGE = 2` 的具体含义**需按源码表格定义核对**（通常 $GAUGE=2$ 对应长度/速度规范之一）。
- **物理量**：`n2 → n3` 组态间 30 条辐射跃迁的 Einstein $A$ 率与振子强度。
- **生成脚本**：`fe17_structure.py:37-38` 的 `fac.TransitionTable('ne.tr.b', ['n2'], ['n3'])` + `fac.PrintTable(..., 'ne.tr', 1)`。
- **make check 比对**：`demo/check.py:122 check_tr()`；按 `lower_index`/`upper_index` 排序（适配 OpenMP 乱序）；`Delta E` `atol = 1`、`rtol = 0.01`；`gf` `atol = 1e-4`、`rtol = 0.02`；`rate` `atol = 1e4`、`rtol = 0.05`；`multipole` `atol = 1e-5`、`rtol = 0.05`。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **相对论原子结构（能级）**
   - 简介：Dirac–Fock 自洽场 + 组态相互作用；`OptimizeRadial` 对基组轨道优化径向势，`MemENTable` 生成能量表。
   - 公式：$\hat H_{\rm DC}\psi_i=E_i\psi_i$，$E_i=\langle\psi_i|\hat H_{\rm DC}+\hat H_{\rm Breit}+\hat H_{\rm QED}|\psi_i\rangle$。
   - 源码对应：`fe17_structure.py:21-35`（含 `GetPotential('ne.pot')`）；`python/rfac.py:511 read_lev()`；`demo/check.py:96 check_en()`。

2. **辐射跃迁率与振子强度**
   - 简介：多极辐射跃迁，由偶极/多极矩阵元给出 Einstein $A$ 和 $gf$。
   - 公式：$A_{ji}=\dfrac{2\pi}{\hbar}\dfrac{1}{2J_j+1}\dfrac{\omega^{2k+1}}{(2k+1)!!^2}\left|\langle j\|\mathbf{D}^{(k)}\|i\rangle\right|^2$，$gf_{ij}=\dfrac{2\Delta E}{3(2J_i+1)}\left|\langle i\|\mathbf{D}\|j\rangle\right|^2$（$k=1$ 为 E1；归一化**需按源码表格定义核对**）。
   - 源码对应：`fe17_structure.py:37 fac.TransitionTable()`；`python/rfac.py:690 read_tr()`；`demo/check.py:122 check_tr()`。

3. **规范（gauge）与多极选择定则**
   - 简介：`MULTIP = 0` 表示按选择定则自动选取多极，`GAUGE = 2` 指定跃迁算符规范；长度/速度规范一致性是精度检验。
   - 公式（长度规范 E1）：$\mathbf{D}=-e\sum_i \mathbf{r}_i$；（速度规范）$\mathbf{D}\propto \mathbf{p}/(m_e c\omega)$。
   - 源码对应：`read_tr()` 第 706-708 行（`MULTIP`/`GAUGE`/`MODE` 字段）；`faclib` 跃迁率模块；具体编码需按源码表格定义核对。

## 使用方式

- `cd demo/structure && make check`：先 `python fe17_structure.py` 生成 `ne.lev`、`ne.tr`，再执行 `python ../check.py ne.lev ref/ne.lev`、`python ../check.py ne.tr ref/ne.tr`。
- 手工比对：`python ../check.py ne.tr ref/ne.tr`；可用 `python -c "import sys; sys.path.insert(0,'../../python'); from rfac import read_tr; h,b=read_tr('ne.tr'); print(h)"` 查看块字段。
- `make openmp` 走 `InitializeMPI(2)` 路径；`make ref` 更新基准；`make clean` 删除结果与 `*.b`。

## 注意事项

- `demo/README` 声明参考来自 FAC=1.1.4，而文件头为 `FAC 1.1.5`；`check.py` 忽略版本/`TSess`。
- `ENERGY` 容差较宽（10 eV 绝对、1% 相对），`gf` 容差 2%，强跃迁 `rate` 容差 5%；弱线（$A$ 很小）以绝对容差 1e4 兜底。
- `openmp` 输出顺序可能变化，`check_tr` 会先按上下能级索引排序，不要手工重排行序。
- 能量单位与 `VNL`/`GAUGE`/`MULTIP` 编码以 `python/rfac.py` 表格定义和 FAC 手册为准，需按源码表格定义核对。

## 验证状态

- 实测 `ne.lev`、`ne.tr` 两项 `check.py` 比对均 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- 命令、容差与产物清单见 [父 README](../README.md) §7–§8。

[返回上级](../README.md)