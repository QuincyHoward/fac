# API 调用链地图

## 1. 两套前端

| 前端 | 入口 | 特点 |
|---|---|---|
| PFAC | `python/fac.c`、`pcrm.c`、`ppol.c`、`util.c` + `rfac.py`、`atom.py`、`spm.py` | Python 函数调用核心 C；非线程安全；适合组合流程 |
| SFAC | `sfac/sfac.c`、`scrm.c`、`spol.c`、`stoken.c` | 命令式脚本；无复杂流程控制；语法接近 Python |

同一物理过程通常共用 `faclib/` 核心实现；差异主要在参数解析和流程组织。

## 2. 典型调用顺序

```text
结构：
SetAtom / Closed / Config / ConfigEnergy
→ OptimizeRadial（仅低组态）
→ Structure
→ MemENTable / PrintTable

辐射跃迁：
Structure → TransitionTable → PrintTable

碰撞激发：
Structure → CETable 或 CETableMSub → PrintTable

碰撞电离：
两次 Structure（初末电荷态）→ SetUsrCIEGrid → CITable → PrintTable

PI/RR：
Structure → RRTable → PrintTable

AI/DC：
Structure（双激发 + 残余态）→ AITable → PrintTable

CRM/谱：
AddIon / SetBlocks → Set*Rates → InitBlocks
→ SetIteration → LevelPopulation → RateTable / SpecTable

偏振：
Structure → TransitionTable(m=...) → CETableMSub
→ SetMLevels / SetEnergy / SetMCERates
→ PopulationTable → Orientation → PolarizationTable

R 矩阵：
RMatrixTargets → Boundary → Basis → Surface
→ RMatrixCE
```

## 3. 如何追某个 API

1. 确认用户说的是 Python 暴露名、SFAC 命令名还是核心 C 函数名。
2. Python 暴露名先在 `python/` 查绑定，再追到 `faclib/`。
3. SFAC 命令名先在 `sfac/` 查解析，再追到 `faclib/`。
4. 核心 C 函数名先在 `faclib/` 查定义与头文件声明。
5. 用引用关系确认谁调用它；用调用关系确认它调用什么。
6. 若存在 Python 包装类（如 `atom.py`、`spm.py`），再查上层封装如何组合核心命令。

## 4. 验证映射

- 给出前端命令、核心符号、输出表类型三项中的至少两项。
- 对照一个最小算例的脚本调用顺序，确认不是仅凭命名推断。
- 对输出表字段问题，用读取器列名与文件头交叉核对。
- 不确定时明确标注“需源码核对”，不要伪造函数名或行号。
