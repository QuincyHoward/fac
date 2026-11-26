# demo/excitation/ref 参考数据

## 目录定位

存放 FAC 生成的电子碰撞激发（**excitation**）算例参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 本目录即 Ne-like Fe 激发算例的基准输出（文件头为 `FAC 1.1.5`）。

生成脚本：`demo/excitation/fe17_excitation.py`、`demo/excitation/fe17_excitationM.py`（等价 SFAC 脚本 `fe17_excitation.sf`、`fe17_excitationM.sf`）。

## 逐文件说明

### 1. `ne.lev` —— 激发算例能级表（Type = 1）

- **数据格式**：头部 `Type = 1`、`Fe Z = 26.0`、`NBlocks = 1`、`E0 = 0, -3.12294465E+04`；块内 `NELE = 10`、`NLEV = 37`，列头 `ILEV IBASE ENERGY P VNL 2J` 加三列配置字符串。字段含义同 `python/rfac.py:511 read_lev()`：`ILEV` 全局序号、`IBASE` 基索引、`ENERGY`（eV，相对 `E0` 的激发能）、`P` 宇称、`VNL` 组态数值标签（**需按源码表格定义核对**）、`2J`、`ncomplex`/`sname`/`name` 名称串。
- **物理量**：Ne-like Fe（Fe XVII）基态 `2p6` 与激发组态 `2p5 3s/3p/3d` 的 37 个精细结构能级。
- **生成脚本**：两个脚本均有 `fac.Structure('ne.lev.b')`、`fac.MemENTable()`、`fac.PrintTable(..., 'ne.lev', 1)`。
- **make check 比对**：`demo/check.py:96 check_en()`；`ENERGY` 容差 `atol = 10`、`rtol = 0.01`；`E0` 容差 1%；`NBlocks` 必须相等；字符串列逐字一致。

### 2. `ne.ce` —— 电子碰撞激发截面表（Type = 3, MSUB = 0）

- **数据格式**：头部关键字段 `NELE = 10`、`NTRANS = 36`、`QKMODE = 0`、`NPARAMS = 0`、`MSUB = 0`、`PWTYPE = 0`、`NTEGRID = 2`（两行温度网格 `7.24092437E+02`、`9.44031529E+02`）、`TE0 = 8.34061980E+02`、`ETYPE = 1`、`NEGRID = 6`（6 个碰撞能量）。按 `python/rfac.py:810 read_ce()`：每条跃迁先给 `lower_index, lower_2J, upper_index, upper_2J, Delta E, nsub`，再给 Bethe/Born 系数行（`bethe`、`born0`、`born1`），随后对每个用户能量给出两列 `collision strength`（碰撞强度 $\Omega$）与 `crosssection`（截面）。无子能级时 `nsub = 1`。
- **物理量**：`2p6 → 2p5 3l` 的 36 条电子碰撞激发跃迁的碰撞强度与截面，含 Bethe/Born 近似系数。
- **生成脚本**：`demo/excitation/fe17_excitation.py:29-30` 的 `fac.CETable('ne.ce.b', ['n2'], ['n3'])` + `PrintTable`。
- **make check 比对**：`demo/check.py:138 check_ce()`；按 `lower_index`/`upper_index` 排序后比较：`collision strength` 容差 `atol = 1e-3`、`rtol = 0.05`；`crosssection` 容差 `atol = 0.01`、`rtol = 0.1`；`EGRID`、`TEGRID`、`USR`、`TE0` 容差 `atol = 1`、`rtol = 0.01`；`bethe`/`born` 相对误差 5%。

### 3. `ne.ceM` —— 磁子能级分辨的碰撞激发表（Type = 3, MSUB = 1）

- **数据格式**：同 Type 3，但头部 `MSUB = 1`、`PWTYPE = 1`、`NTRANS = 7`；由 `fac.CETableMSub('ne.ceM.b', [0], [2,4,16,22,26,30,32])` 生成，参数是**能级序号**列表[0] 与 [2,4,16,22,26,30,32]（**索引指向 `ne.lev` 的 ILEV，需按脚本与表格定义核对**）。按 `read_ce()` 的 `MSUB` 分支：每条跃迁除常规字段外，还包含每个子跃迁的 `ratio collision strength`（碰撞强度比）以及按子能级展开的 `collision strength`、`crosssection` 数组（转置存储）。
- **物理量**：从基态能级 0 到 7 个指定磁子能级的激发，按磁子态拆分，可直接用于偏振计算。
- **生成脚本**：`demo/excitation/fe17_excitationM.py:21-22`。
- **make check 比对**：`demo/check.py:241` 中 `actual_file[-3:] in ['.ce', 'ceM']` 同样分派到 `check_ce()`；因为 `MSUB = 1`，会额外比较 `ratio collision strength`（`atol = 0.1`），其余容差同上。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **原子能级与轨道优化**
   - 简介：类 Ne 铁自洽场计算，`OptimizeRadial('n2')` 优化基组径向势。
   - 公式：$\left[-\frac12\nabla^2+V_{\rm eff}(r)\right]\psi=E\psi$，能级由对角化得到。
   - 源码对应：`fe17_excitation.py:21-27`；`python/rfac.py:511 read_lev()`。

2. **电子碰撞激发（EIE）截面与速率系数**
   - 简介：入射电子使离子从 $i$ 激发到 $j$，用碰撞强度 $\Omega$ 表示。
   - 公式：$\sigma_{ij}(E)=\dfrac{\pi a_0^2}{g_i}\dfrac{\Omega_{ij}(E)}{E_i}$（$E_i$ 以 Ryd 计）； Maxwell 速率系数 $q_{ij}=\sqrt{\dfrac{8}{\pi m_e}}\,(kT)^{-3/2}\displaystyle\int \sigma_{ij}(E)\,E\,e^{-E/kT}\,dE$。
   - 源码对应：`fe17_excitation.py:29 fac.CETable()`；`faclib/excitation.c`；`python/rfac.py:810 read_ce()`；`demo/check.py:138 check_ce()`。

3. **高能 Bethe / Born 近似系数**
   - 简介：`bethe`、`born` 列为截面在高能区的渐近参数，用于外推。
   - 公式（示意）：$\Omega(E)\sim c_{\rm Bethe}\ln E + c_{\rm Born}^{(0)} + c_{\rm Born}^{(1)}/E$；具体系数定义**需按源码表格定义核对**。
   - 源码对应：`read_ce()` 第 863–865、908–909 行；`check_ce()` 的 `bethe`/`born` 容差表。

4. **磁子能级分辨激发与偏振**
   - 简介：按 $M_J$ 子能级展开碰撞强度，是线偏振计算的输入。
   - 公式：$\Omega_{iM_i\rightarrow jM_j}$ 满足 $\sum_{M_i M_j}\Omega_{iM_i\to jM_j}=(2J_i+1)(2J_j+1)\Omega_{ij}/[(2J_i+1)]$（归一化约定**需按源码核对**）。
   - 源码对应：`fe17_excitationM.py:21 fac.CETableMSub()`；`python/rfac.py:871-891`（MSUB 分支）；`demo/polariz/pol.py:7` 使用 `SetMCERates('tb.ce')`。

## 使用方式

- `cd demo/excitation && make check`：依次运行两个脚本生成 `ne.ce`、`ne.ceM`、`ne.lev`，再 `python ../check.py <file> ref/<file>`。
- 手工比对：`python ../check.py ne.ceM ref/ne.ceM`；`make openmp` 需要 MPI 初始化/收尾，脚本已支持。
- `make ref` 覆盖参考文件；`make clean` 删除结果文件与 `*.b`。

## 注意事项

- `demo/README` 称参考值来自 FAC=1.1.4，而文件头为 `FAC 1.1.5`；比对只看数据字段。
- `CE`/`ceM` 判定依赖扩展名切片 `actual_file[-3:]`；文件名需保持原样，否则 `check.py` 会抛 `TypeError`。
- OpenMP 下跃迁顺序可能不同，`check_ce` 会按上下能级索引重排；`ne.ceM` 的能级序号列表直接对应 `ne.lev` 的 `ILEV`，改动结构会改变物理含义。
- 能量、温度、网格单位以 FAC 内部单位为准，列含义不确定处需按 `python/rfac.py` 表格定义核对。

## 验证状态

- 实测 `ne.lev`、`ne.ce`、`ne.ceM` 三项 `check.py` 比对均 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- `ratio collision strength` 的相对容差受 `check.py` 死键影响，实际只有绝对容差生效；详见 [父 README](../README.md) §8。

[返回上级](../README.md)