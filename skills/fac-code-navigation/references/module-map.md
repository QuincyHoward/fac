# FAC 模块地图

## 1. 顶层入口

| 路径 | 职责 |
|---|---|
| `README.md` | 项目总览、安装、物理公式索引、示例入口 |
| `configure` / `configure.ac` | 构建配置、编译器与 Python 选项 |
| `Makefile.in` | 构建目标骨架 |
| `setup.py` | 生成 Python 常量并编译 PFAC 四个扩展 |
| `demo/` | 示例、回归脚本、`check.py`、基准表 |
| `doc/` | 手册、论文、表格格式与理论出处 |

## 2. 核心源码

| 目录 | 职责 | 关键线索 |
|---|---|---|
| `faclib/` | C 核心物理库与数据表 | `structure.c`、`transition.c`、`excitation.c`、`ionization.c`、`recombination.c`、`crm.c`、`polarization.c`、`rmatrix.c`、`dbase.c` |
| `python/` | PFAC 接口 | `fac.c`、`pcrm.c`、`ppol.c`、`util.c`、`rfac.py`、`atom.py`、`spm.py` |
| `sfac/` | SFAC 命令接口 | `sfac.c`、`scrm.c`、`spol.c`、`stoken.c` |
| `coul/` | 库仑函数与连续态 | `coulrad.f`、`dcoul.f`、`besljn.f`、`expint.f`、`clogam.f` |
| `modqed/` | QED 修正 | `uehling.f`、`wk.f`、`se_pot.f`、`nucl.f` |
| `ionis/` | 电离平衡拟合 | 电离平衡与速率拟合例程 |
| `mpfun/` | 高精度与特殊函数 | `mpfun.f`、`dxlegf.f` |
| `ode/` | 常微分方程求解 | `lsode.f` |
| `quadpack/` | 积分 | `dqags.f` 等 |
| `blas/` `lapack/` `minpack/` `toms/` | 线性代数与数值支撑 | 标准数值例程 |

## 3. 数据表与读取器

- `faclib/dbase.c`：二进制表写入、ASCII 打印与格式分派。
- `python/rfac.py`：Python 侧表读取器，包含历史键名误命名。
- `demo/check.py`：基于 `rfac.read_*` 的回归比对。

## 4. 文档入口

- `doc/manual.tex`：手册与函数参考。
- `doc/papers/`：FAC 系列论文与理论出处。
- `doc/misc/`：表格格式与实用说明。

## 5. 定位顺序

1. 用户问目录职责：先读对应目录 README。
2. 用户问物理功能：先查 `faclib/`，再查 `coul/modqed/ionis` 等支撑库。
3. 用户问 Python 调用：查 `python/`。
4. 用户问 SFAC 命令：查 `sfac/`。
5. 用户问表格字段：查 `faclib/dbase.c`、`python/rfac.py`、`doc/` 表格说明。
