# demo/pirr/ref 参考数据

## 目录定位

存放 FAC 生成的光电离与辐射复合（**p**hoto**i**onization and **r**adiative recombination）算例参考结果，用于 `make check` 回归比对。依据 `demo/README` 原文：“`ref` in each example contains the reference results by FAC=1.1.4. In order to test FAC in your environment, execute `make check`.” 文件头为 `FAC 1.1.5`。

算例对象为 Li-like Fe（Fe XXIV）；生成脚本：`demo/pirr/fe24_pirr.py`（等价 SFAC 脚本 `fe24_pirr.sf`）。

## 逐文件说明

### 1. `li.lev` —— 复合前后能级表（Type = 1）

- **数据格式**：头部 `Type = 1`、`Fe Z = 26.0`、`NBlocks = 2`、`E0 = 7, -2.01497967E+04`。块 1：`NELE = 2, NLEV = 7`（He-like Fe：`1s2`、`1s1 2s1`、`1s1 2p1`）；块 2：`NELE = 3`（Li-like Fe：`1s2 2*1`，即 `rn2` 组态）。列头 `ILEV IBASE ENERGY P VNL 2J` + 三列名称串，字段按 `python/rfac.py:511 read_lev()`：`ENERGY` 相对 `E0`（eV）、`P` 宇称、`VNL`（**需按源码表格定义核对**）、`2J` 与组态名。
- **物理量**：辐射复合末态（He-like）与初态（Li-like）能级，能级差对应复合释放光子能量与光电离阈值。
- **生成脚本**：`fe24_pirr.py:22-25` 的两次 `fac.Structure()`、`MemENTable()`、`PrintTable(..., 'li.lev', 1)`。
- **make check 比对**：`demo/check.py:96 check_en()`：`NBlocks`、`E0`（1%）、`ENERGY`（`atol = 10`、`rtol = 0.01`）、名称串逐字一致。

### 2. `li.rr` —— 辐射复合/光电离截面表（Type = 4）

- **数据格式**：头部 `Type = 4`、`NELE = 3`、`NTRANS = 3`、`QKMODE = 2`、`MULTIP = 100`、`NPARAMS = 4`、`NTEGRID = 1`（温度点 `2.01309079E+03`）、`ETYPE = 1`、`NEGRID = 6`（6 个能量点）。按 `python/rfac.py:1004 read_rr()`：每条跃迁先给 `bound_index, bound_2J, free_index, free_2J, Delta E, Delta L`，再一行 `NPARAMS = 4` 个 `parameters`，随后每个能量点给三列 `RR crosssection`、`PI crosssection`、`gf`（振子强度）。
- **物理量**：Li-like Fe 自由电子被俘获到 He-like Fe 束缚态的辐射复合截面 `RR crosssection`、由详细平衡得到的光电离截面 `PI crosssection`，以及相应的 `gf`。`MULTIP = 100` 为多极/近似方式的代码（**需按源码表格定义核对**）。
- **生成脚本**：`fe24_pirr.py:27-28` 的 `fac.RRTable('li.rr.b', ['rn2'], ['n1'])` + `PrintTable`。
- **make check 比对**：`demo/check.py:178 check_rr()`；按 `bound_index`/`free_index` 排序；`RR crosssection`、`PI crosssection`、`gf`、`parameters` 相对误差 1%；`Delta E`/网格 `atol = 1`、`rtol = 0.01`。

## 涉及物理效应（简介 + 公式 + 源码对应）

1. **光电离与辐射复合（详细平衡 / Milne 关系）**
   - 简介：光电离 $X^{q+}+\hbar\nu\to X^{(q+1)+}+e^-$ 与逆过程辐射复合；两者截面通过详细平衡联系。
   - 公式（原子单位，此处用 $\chi$ 表示电离能、$\varepsilon$ 为自由电子能量）：
     $\sigma_{\rm RR}(\varepsilon)=\dfrac{g_b}{2g_f}\dfrac{(\chi+\varepsilon)^2}{c^2\varepsilon}\,\sigma_{\rm PI}(\chi+\varepsilon)$。
     表中 `RR crosssection` 与 `PI crosssection` 即由该关系成对给出。**核查说明**：这是忽略相对论小量 $1+\tfrac12\alpha^2\varepsilon$ 的等价写法；`doc/papers/pirr.tex` 只用 $\omega$（光子能量）与 $\varepsilon$，未引入 $\chi$ 记号。
   - 源码对应：`fe24_pirr.py:27 fac.RRTable()`；`faclib/recombination.c`；`python/rfac.py:1004 read_rr()`；`demo/check.py:178 check_rr()`。

2. **束缚–自由跃迁与末态结构**
   - 简介：复合到 He-like Fe 的不同精细结构能级，`bound_index`/`free_index` 标识束缚态与连续道，`Delta L` 标记自由电子角动量。
   - 公式：$\sigma_{\rm RR}^{(l)}\propto \sum_{k}\left|\langle \psi_b\|\mathbf{D}^{(k)}\|\psi_{\varepsilon l}\rangle\right|^2$，各分波求和得总截面。
   - 源码对应：`python/rfac.py:1047-1052`；`fe24_pirr.py:12-18`（`n1`、`n2`、`rn2` 组态定义与 `OptimizeRadial(['rn2'])`）。

3. **组态相互作用（末态）**
   - 简介：脚本注释指明 `n=1` 与 `n=2` 复合体之间的 CI 被包含。
   - 公式：$H_{ij}=\langle\Phi_i|\hat H|\Phi_j\rangle$，对角化给出混合态。
   - 源码对应：`fe24_pirr.py:20-23`、`python/rfac.py:511 read_lev()`。

4. **振子强度 `gf`**
   - 简介：与光电离截面等价的振子强度表示，便于等离子体模型使用。
   - 公式：$g f_{if}=\dfrac{2m_e h\nu}{e^2\hbar}\left|\langle f|\mathbf{D}|i\rangle\right|^2$（具体归一化**需按源码表格定义核对**）。
   - 源码对应：`read_rr()` 第 1065、1080 行（`gf_list`、`block['gf']`）。

## 使用方式

- `cd demo/pirr && make check`：运行 `fe24_pirr.py` 生成 `li.lev`、`li.rr`，再 `python ../check.py li.rr ref/li.rr` 等。
- 手工比对：`python ../check.py li.lev ref/li.lev`；可用 `rfac.read_rr()` 查看各能量点 RR/PI 截面。
- `make ref` 覆盖基准；`make clean` 清除结果。

## 注意事项

- `demo/README` 称 FAC=1.1.4 基准，实际头部为 `FAC 1.1.5`。
- `li.rr` 中 `QKMODE = 2`、`NPARAMS = 4` 的参数化形式与 `MULTIP = 100` 编码需按 FAC 手册/`python/rfac.py` 表格定义核对。
- `li.lev` 的 `E0` 索引为 7（非零），比对时 `E0` 必须一致（1% 容差）。
- `RR`/`PI` 截面容差较严（1%），网格点必须与原脚本一致。

## 验证状态

- 实测 `li.lev`、`li.rr` 两项 `check.py` 比对均 `EXIT=0` 通过；**耗时未记录**，不推断墙钟时间。
- 命令、容差与单位说明见 [父 README](../README.md) §7、§9。

[返回上级](../README.md)