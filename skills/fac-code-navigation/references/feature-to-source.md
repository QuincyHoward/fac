# 功能到源码映射

本表给出稳定线索，不替代源码复核。C/Fortran 项目若语义工具无结果，使用定向文本检索到文件路径与符号名即可。

| 功能 | 首选目录/文件 | 关键符号/关键词 |
|---|---|---|
| 原子结构 / CI / 对角化 | `faclib/structure.c` | `SolveStructure`、`SetCILevel`、`ConstructHamilton`、`DiagnolizeHamilton` |
| 径向轨道与势 | `faclib/radial.c`、`orbital.c`、`config.c`、`angular.c` | 径向网格、自洽场、角动量耦合 |
| 辐射跃迁 | `faclib/transition.c`、`dbase.c` | `TRMultipole`、`PrintTRTable`、`OscillatorStrength` |
| 碰撞激发 CE | `faclib/excitation.c`、`rates.c`、`interpolation.c` | `CollisionStrength`、`CETableMSub`、`CERate`、`InterpolateCECross` |
| 碰撞电离 CI/EII | `faclib/ionization.c`、`rates.c` | `IonizeStrength`、`CIRadialQk`、`CIRate` |
| PI / RR | `faclib/recombination.c`、`coul/coulrad.f` | `RRRadialMultipole`、`BoundFreeOS`、`PIXZ1` |
| AI / DC / DR | `faclib/recombination.c`、`crm.c` | `AutoionizeRate`、`AIRadialPk`、`DRBranch`、`DRStrength`、`SetAIRates` |
| CRM | `faclib/crm.c` | `AddIon`、`SetBlocks`、`Set*Rates`、`BlockMatrix`、`LevelPopulation`、`Cascade` |
| 谱合成 | `faclib/crm.c`、`dbase.c`、`python/spm.py` | `SpecTable`、`PlotSpec`、`SelectLines`、`PrintSPTable` |
| 偏振 | `faclib/polarization.c`、`python/ppol.c`、`sfac/spol.c` | `PopulationTable`、`Orientation`、`PolarizationTable`、`a/b` |
| R 矩阵 | `faclib/rmatrix.c`、`coul/dcoul.f`、`ode/lsode.f` | `RMatrixBoundary`、`RMatrixBasis`、`RMatrixSurface`、`RMatrixCE` |
| QED | `modqed/*.f`、`faclib/orbital.c` | `QED1E`、`SetSE`、`SetVP`、`uehling`、`wk` |
| 特殊函数与数值支撑 | `coul/`、`mpfun/`、`toms/`、`quadpack/`、`lapack/`、`blas/` | 按函数名或 README 索引定位 |

## 输出表反查

| 输出表 | 打印/读取线索 |
|---|---|
| `.en` | `faclib/dbase.c` 的能级表打印；`python/rfac.py` 的 `read_lev` |
| `.tr` | `PrintTRTable`；`read_tr` |
| `.ce` / `.ceM` | `PrintCETable`；`read_ce` |
| `.ci` | `PrintCITable`；`read_ci` |
| `.rr` | `PrintRRTable`；`read_rr` |
| `.ai` | `PrintAITable`；`read_ai` |
| `.sp` | `PrintSPTable`；`read_sp` |
| `.rt` | 速率矩阵打印器；`read_rt` |
| `.ham` | 哈密顿量存储；`read_ham` |

## 语义定位策略

1. 对有名符号使用 `workspaceSymbol`。
2. 已知使用位置时用 `goToDefinition`。
3. 查调用者用 `findReferences` 或 `incomingCalls`。
4. 查调用链用 `outgoingCalls`。
5. LSP 无结果时，改用上面的文件与符号关键词做定向检索；不要全仓库盲扫。
