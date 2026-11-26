# demo/aidr/ref 参考数据

## 目录定位

存放 FAC 生成的自电离（**ai**dr）算例参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 即本目录为 FAC=1.1.4 的基准输出；注意实际文件头打印为 `FAC 1.1.5`（见下方注意事项）。

本目录对应算例：Ne-like Se 的双激发自电离（F-like Se 残余离子 + 自由电子），生成脚本为 `demo/aidr/se_ai.py`（等价 SFAC 脚本 `demo/aidr/se_ai.sf`）。

## 逐文件说明

### 1. `se.lev` —— 能级表（Type = 1）

- **数据格式**：文本表格。文件头为键值行（`FAC 1.1.5`、`Endian`、`TSess`、`Type = 1`、`Se Z = 34.0`、`NBlocks = 2`、`E0 = 0, -5.33765354E+04`）。每个块以 `NELE`、`NLEV` 开头，随后是列头 `ILEV IBASE ENERGY P VNL 2J`，再跟配置字符串三列。按 `python/rfac.py:511 read_lev()` 的定义：
  - `ILEV`：全局能级序号；`IBASE`：基组索引（本文件为 -1）；
  - `ENERGY`：能级能量，单位 **eV**（相对 `E0` 基准的激发能，基态为 0；`dbase.c:5371–5374` 在 verbose 输出中减去基态能量并乘 `HARTREE_EV`；`E0` 亦为 eV）；
  - `P`：宇称（0 偶、1 奇）；`VNL`：虚轨道/组态数值标签（**含义需按源码表格定义核对**）；`2J`：2 倍总角动量；
  - 其后三列为 `ncomplex`、`sname`、`name`（组态与能级名称字符串）。
- **内容**：块 1 为 `NELE = 9, NLEV = 2`（F-like Se，`2p5` 基态双重态）；块 2 为 `NELE = 10, NLEV = 47`（Ne-like Se 双激发组态 `2p4 3s2`、`2p4 3s1 3p1`）。
- **生成脚本**：`demo/aidr/se_ai.py` 中 `fac.Structure()`、`fac.MemENTable()`、`fac.PrintTable(..., 'se.lev', 1)`（第 21–24 行）。
- **make check 比对**：`demo/aidr/Makefile` 的 `RESULTS = se.ai se.lev`，`demo/Make.common` 执行 `python ../check.py se.lev ref/se.lev`。因扩展名匹配 `lev`，`demo/check.py:96 check_en()` 被调用：表头校验 `NBlocks` 相等、`E0` 相对误差 1%；`ENERGY` 允许 `atol = 10`、`rtol = 0.01`；字符串列（`name` 等）要求逐字相同。

### 2. `se.ai` —— 自电离率表（Type = 5）

- **数据格式**：文本表格。文件头 `Type = 5`、`NELE = 10`、`NTRANS = 94`、`EMIN = 0`、`NEGRID = 3` 及 3 行电子能量网格（`3.43465875E+02`、`4.37811295E+02`、`5.56958685E+02`；单位需核对，疑为 Ryd/eV）。按 `python/rfac.py:761 read_ai()` 的定义，数据行 7 列依次为：
  - `bound_index`、`bound_2J`：束缚态（F-like Se 残余离子）能级序号与 `2J`；
  - `free_index`、`free_2J`：自由电子分波道的序号与 `2J`；
  - `Delta E`：自电离能（释放电子动能）；
  - `AI rate`：自电离率（s⁻¹，由 FAC 内部原子单位换算）；
  - `DC strength`：双电子俘获（dielectronic capture）强度，单位为 $10^{-20}\,\mathrm{eV\,cm^2}$（`manual.tex:1672–1674`），不是无量纲量。
- **物理量**：Ne-like Se 双激发态 `2p4 3s2 / 2p4 3s3p` → F-like Se `2p5` + 自由电子的自电离跃迁率与共振俘获强度。
- **生成脚本**：`demo/aidr/se_ai.py:26-27` 的 `fac.AITable('se.ai.b', ['n33'], ['n2'])` 与 `fac.PrintTable('se.ai.b', 'se.ai', 1)`。
- **make check 比对**：`demo/check.py:106 check_ai()`。先用 `bound_index`/`free_index` 排序（OpenMP 下顺序可能不同），再逐块比较：`AI rate` 相对误差 5%（默认 `atol=1e-8`）；`Delta E` 允许 `atol=0.5`、`rtol=0.01`；`DC strength` 相对误差 5%；`EGRID` 相对误差 1%。`check.py` 中的 `atols/rtols['rate']` 是遗留死键（`read_ai()` 无 `rate` 列），不实际生效。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **相对论原子结构与组态相互作用（能级）**
   - 简介：求解 Dirac–Fock / 组态相互作用哈密顿量得到束缚能级与波函数，再用优化径向势做自洽迭代。
   - 公式：$\hat H_{\rm DC}\,\psi_i=E_i\psi_i,\quad E_i=\langle\psi_i|\hat H_{\rm DC}+\hat H_{\rm B}+\hat H_{\rm QED}|\psi_i\rangle$。
   - 源码对应：`demo/aidr/se_ai.py:10-24`（`Config`、`ConfigEnergy`、`OptimizeRadial`、`Structure`、`MemENTable`）；`python/rfac.py:511 read_lev()`；`demo/check.py:96 check_en()`。

2. **自电离（Auger 衰变）**
   - 简介：双激发态通过电子–电子关联向连续态跃迁，率由费米黄金规则给出。
   - 公式：$A^{a}_{i\to f}=\dfrac{2\pi}{\hbar}\left|\langle\Phi_f^{E}|V|\Psi_i\rangle\right|^{2}$，其中 $\Phi_f^{E}$ 为残余离子 + 自由电子的连续态。
   - 源码对应：`demo/aidr/se_ai.py:26 fac.AITable()`；`faclib` 自电离率计算；`python/rfac.py:761 read_ai()`；`demo/check.py:106 check_ai()`。

3. **双电子俘获 / 共振强度（DC strength）**
   - 简介：自电离的逆过程，决定介电离复合共振贡献；与辐射复合竞争。
   - 公式（示意）：$S_{\rm DC}\propto \dfrac{g_i}{g_j}\dfrac{A^{a}_{j\to i}A^{r}_{j\to k}}{\sum_m A_m}$，具体归一化**需按源码表格定义核对**。
   - 源码对应：`AITable` 输出的第 7 列；`python/rfac.py:804-805`（`AI rate`、`DC strength` 字段）。

## 使用方式

- **回归检查**：在 `demo/` 下执行 `make check`（等价于进入 `aidr/` 执行 `make check`）。该目标先依赖 `all` 运行 `python se_ai.py` 生成工作文件 `se.ai`、`se.lev`，再逐个执行 `python ../check.py <结果> ref/<结果>`；全部通过打印 `Tests passed!`。
- **手工比对**：`cd demo/aidr && python ../check.py se.ai ref/se.ai`，同理 `se.lev`。可用 `python -c "from sys import path; path.insert(0,'../../python'); from rfac import read_ai; ..."` 读取表格查看字段。
- **更新参考**：`make ref` 会先 `make` 再用 `cp` 覆盖 `ref/`；仅在确认物理结果正确时使用。

## 注意事项

- `demo/README` 声明参考值来自 FAC=1.1.4，但文件头实际为 `FAC 1.1.5`；比对脚本忽略版本/时间戳，只校验数据字段。
- `check.py` 忽略 `TSess` 等头部字段，但要求 `NBlocks` 与 `E0`（1% 内）一致；`ENERGY` 容差较宽（10 eV 绝对、1% 相对）。
- 使用 `make openmp` 时输出顺序可能变化，`check_ai` 会按索引对数组重排；不要手工打乱行序后比对。
- 单位列的含义与换算请以 `python/rfac.py` 的 `read_*` 表格定义与 FAC 手册为准，不确定处需按源码表格定义核对。

## 验证状态

- 实测 `se.lev`、`se.ai` 两项 `check.py` 比对均 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- 命令、环境、产物清单与已知限制见 [父 README](../README.md) §7、§9。

[返回上级](../README.md)