# PFAC Python 接口层（`python/`）

## 1. 目录定位与角色

本目录是 FAC（Flexible Atomic Code）的 **Python 接口层（PFAC）**：一方面用 C 语言编写 Python 扩展模块，把 `faclib` 的 C API（`libfac.a`）逐函数桥接为 `pfac.fac`、`pfac.crm`、`pfac.pol`、`pfac.util`；另一方面提供 `atom.py`、`rfac.py`、`config.py`、`spm.py`、`aa.py`、`table.py`、`const.py` 等高级 Python 封装，完成“组态生成 → 径向优化 → 能级结构 → 跃迁/速率 → CRM/光谱/偏振 → 数据文件读写与后处理”的完整科研工作流。此外 `mpy.c` 提供一个内嵌 CPython 解释器的最小启动程序，便于在 MPI 环境下运行 Python 脚本。

与 `sfac/`（三个命令行程序的命令解析与驱动层）的关系是：`python/fac.c` 等 C 扩展通过 `ConvertToSFAC()` / `ConvertToSCRM()` / `ConvertToSPOL()` 可把 Python 侧的调用原样转写为 `sfac` / `scrm` / `spol` 的输入脚本；`sfac/` 中的命令名与这里导出的 API 名一一对应。

## 2. 组织形式与文件分类

| 分类 | 文件 | 说明 |
|---|---|---|
| 包入口 | `__init__.py` | 声明 `pfac` 包与 `__all__` |
| C 扩展源码（对接 faclib） | `fac.c`（约 167 KB）、`pcrm.c`、`ppol.c`、`util.c` | 分别生成 `pfac.fac`、`pfac.crm`、`pfac.pol`、`pfac.util` |
| 高级 Python 封装 | `rfac.py`（约 97 KB）、`atom.py`（约 59 KB）、`aa.py`、`spm.py`、`config.py`、`table.py`、`const.py` | 文件读取、原子建模、平均原子、光谱后处理、组态语法、ApJ 表格、物理常数 |
| 启动器与构建 | `mpy.c`、`Makefile.in` | 内嵌 CPython/MPI 的 `mpy` 可执行文件及其构建规则 |

真实的 Python 模块/API 名称（以源码为准）：`pfac.fac`（C 扩展，含 `Config`、`SetAtom`、`ConfigEnergy`、`OptimizeRadial`、`Structure`、`TransitionTable` 等函数，以及 `VERSION`、`SPECSYMBOL`、`ATOMICSYMBOL`、`ATOMICMASS`、`QKMODE` 常量）、`pfac.crm`（C 扩展）、`pfac.pol`（C 扩展，`ppol.c` 生成；未列入 `__init__.py` 的 `__all__`，但可 `from pfac import pol`）、`pfac.util`（C 扩展）、`pfac.rfac`、`pfac.atom`、`pfac.aa`、`pfac.spm`、`pfac.config`、`pfac.table`、`pfac.const`。注意 `pfac.atom` 中 `Config`、`Closed`、`SetAtom`、`SPECSYMBOL` 等是从 `pfac.fac` 通配导入的 C API，而非自定义类；`__init__.py` 的 `__all__` 中还列有 `consts`，但本目录并不存在 `consts.py`（历史遗留）。

## 3. 逐文件说明

### `fac.c`（C 扩展 `pfac.fac`，按函数族分组，独立条目）
- **功能**：PFAC 的核心 C 扩展，把 `faclib` 的组态、径向、结构、跃迁、速率、R-矩阵、数据库、MPI 等 C API 全部包装成 Python 函数；并支持把调用重定向为 `sfac` 脚本。
- **关键函数或类**：
  - 初始化/常量：`PyInit_fac`（Py2 下 `initfac`）、`InitFac0`；导出 `VERSION`、`SPECSYMBOL`、`ATOMICSYMBOL`、`ATOMICMASS`、`QKMODE`（`DEFAULT/EXACT/INTERPOLATE/FIT/CB/DW/BED`）。
  - 脚本转写：`ConvertToSFAC`、`CloseSFAC`、`SFACStatement`、`Print`、`System`。
  - 组态与角动量：`Config`、`AddConfig`、`RemoveConfig`、`ListConfig`、`ReadConfig`、`GetConfigNR`、`ConfigUTA`、`Closed`、`ClosedShells`、`SetAvgConfig`、`AvgConfig`、`GroupStat`、`CutMixing`、`GetW3j`、`GetW6j`、`GetW9j`、`GetCG`、`WignerDMatrix`、`PrepAngular`、`PrepCEUTA`、`PrepCIUTA`、`PrepRRUTA`、`PrepAIUTA`。
  - 原子/径向/势：`SetAtom`、`Reinit`、`ReinitConfig/Recouple/Radial/DBase/Structure/Excitation/Recombination/Ionization`、`SetRadialGrid`、`SolveBound`、`SolvePseudo`、`OptimizeRadial`、`OptimizeGroup`、`RefineRadial`、`FreezeOrbital`、`GetPotential`、`SetPotentialMode`、`SetBoundary`、`GetBoundary`、`SetExtraPotential`、`SetScreening`、`SetSE`、`SetModSE`、`OptimizeModSE`、`SetVP`、`SetBreit`、`SetMS`、`FermiRMS`、`FermiParamC`、`XCPotential`、`PlasmaScreen`、`SavePotential`、`RestorePotential`、`ModifyPotential`、`AverageAtom`、`FillClosedShell`、`RemoveClosedShell`、`ShellDegeneracy`、`GetGroundProp`。
  - 能级结构：`Structure`、`StructureMBPT`、`StructureEB`、`ConfigEnergy`、`SetConfigEnergyMode`、`AdjustEnergy`、`CorrectEnergy`、`SortLevels`、`LevelInfo`/`LevelInfor`、`OrbitalStats`、`Info`、`RecStates`、`RecoupleRO`、`ExpectationValue`、`ElectronDensity`、`PrintTable`、`SetFields`、`SetLepton`、`NucleusRadius`、`QuantumDefect`、`CoulombPhase`、`DiracCoulomb`、`DiracCoulomb`、`BreitX`、`PrintQED`、`PrintNucleus`。
  - 跃迁/截面/速率：`TransitionTable`（别名 `TRTable`）、`TransitionTableEB`（别名 `TRTableEB`）、`PolarizeCoeff`、`TRBranch`、`TRRateH`、`PICrossH`、`RRCrossH`、`RRCrossHn`、`TotalRRCross`、`TotalPICross`、`TotalCICross`、`CETable`、`CETableEB`、`CETableMSub`、`CITable`、`CITableMSub`、`RRTable`、`AIBranch`、`AITable`、`AITableMSub`、`CXTable`、`InterpCross`（别名 `CECross`）、`MaxwellRate`（别名 `CERate`）、`WaveFuncTable`、`BasisTable`、`LandauZenerCX`、`LandauZenerLD`、`CoulMultipole`。
  - R-矩阵族：`RMatrixExpansion`、`RMatrixFMode`、`RMatrixConvert`、`RMatrixNMultipoles`、`RMatrixRefine`、`RMatrixCE`、`TestRMatrix`、`RMatrixBoundary`、`RMatrixTargets`、`RMatrixBasis`、`RMatrixSurface`。
  - 网格/截断/选项：`SetCEGrid`、`SetCEGridLimits`、`SetCEGridType`、`SetUsrCEGrid`、`SetUsrCEGridType`、`SetCIEGrid`、`SetCIEGridLimits`、`SetUsrCIEGrid`、`SetPEGrid`、`SetPEGridLimits`、`SetUsrPEGrid`、`SetTEGrid`、`SetAngleGrid`、`SetRRTEGrid`、`SetCEBorn`、`SetCIBorn`、`SetBornFormFactor`、`SetBornMass`、`SetCEQkMode`、`SetCIQkMode`、`SetRecQkMode`、`SetCEPWOptions`、`SetCEPWGrid`、`SetCEPWFile`、`SetCIPWOptions`、`SetCIPWGrid`、`SetRecPWOptions`、`SetRecPWLimits`、`SetRecSpectator`、`SetTransitionCut`、`SetTransitionOptions`、`SetTransitionMode`、`SetTransitionGauge`、`SetTransitionMaxE`、`SetTransitionMaxM`、`SetAICut`、`SetMixCut`、`SetAngZOptions`、`SetAngZCut`、`SetMaxRank`、`SetOrbMap`、`SetOrbNMax`、`GetOrbNMax`、`SetOptimizeControl/MaxIter/Stabilizer/Print/Tolerance`、`SetCELQR/CELMax/CELCB/CETol`、`SetCILQR/CILMax/CILMaxEject/CILCB/CITol`、`SetCXTarget`、`SetCXEGrid`、`SetCXLDist`、`SetOption`、`SetSlaterCut`、`SetSlaterScale`、`SetUTA`、`SetTRF`、`DROpen`。
  - 数据库/内存/工具：`AppendTable`、`JoinTable`、`PreloadTable`、`JoinDBase`、`CombineDBase`、`CollapseDBase`、`ModifyTable`、`LimitArray`、`ReinitDBase`、`MemENTable`、`FreeMemENTable`、`FreeSlater`、`FreeMultipole`、`FreeResidual`、`FreeRecPk`、`FreeRecQk`、`FreeExcitationQk`、`FreeIonizationQk`、`CheckEndian`、`WallTime`、`InitializeMPI`、`MPIRank`、`MemUsed`、`FinalizeMPI`、`System`、`SetProcID`、`GeneralizedMoment`、`SlaterCoeff`、`PropogateDirection`、`Y5N`、`Legendre`、`Bessel`、`MaxwellRC`、`FermiFun`、`FermiDirac`、`Test*` 系列、`IntRadJn`、`ReportMultiStats`、`CoulombBethe`。
- **参数与返回值**：绝大多数为 `METH_VARARGS`，C 端用 `PyArg_ParseTuple(args, 格式串, ...)` 解析位置参数（字符串 `s`、整数 `i`、浮点 `d`、列表/元组 `O`），用 `Py_BuildValue("d"/"i"/"[]", ...)` 返回标量、列表，或返回 `Py_None`；仅 `Config`、`Reinit` 为 `METH_VARARGS|METH_KEYWORDS`（关键字参数）。出错通常打印信息/设 `fac.error`。
- **依赖与调用关系**：依赖 `Python.h`、`init.h`、`cf77.h`、`mpiutil.h`、`global.h` 及 `libfac.a`；调用 `InitFac0()` 完成库初始化，再由 `SpecSymbol`、`GetAtomicSymbolTable`、`GetAtomicMassTable` 生成模块级常量。所有 `P*` 包装函数调用同名/近名的 faclib C 函数；当 `ConvertToSFAC` 被激活时，改写走 `SFACStatement()` 输出脚本。

### `pcrm.c`（C 扩展 `pfac.crm`）
- **功能**：把 CRM（Collisional-Radiative Model）C API 包装为 Python 的 `pfac.crm`，提供能级布居、速率矩阵、谱表、速率系数拟合、NLTE 表等功能，并可转写为 `scrm` 脚本。
- **关键函数或类**：`PyInit_crm`（Py2 `initcrm`）、`ConvertToSCRM`、`CloseSCRM`、`SCRMStatement`；分布与密度 `EleDist`、`CxtDist`、`PhoDist`、`SetEleDist`、`SetCxtDist`、`SetPhoDist`、`SetEleDensity`、`SetCxtDensity`、`SetPhoDensity`、`IonDensity`、`IonRadiation`；速率 `SetCERates`、`SetCXRates`、`SetTRRates`、`SetCIRates`、`SetRRRates`、`SetAIRates`、`SetAIRatesInner`、`RateTable`、`RateCoefficients`、`ModifyRates`、`DumpRates`、`GauntFF`、`Bremss`；求解控制 `AddIon`、`SetBlocks`、`InitBlocks`、`SetNumSingleBlocks`、`SetIteration`、`SetRateAccuracy`、`SetCascade`、`Cascade`、`SetExtrapolate`、`SetEMinAI`、`SetInnerAuger`、`SetAbund`、`SetRateMultiplier`、`DRSuppression`、`DRSupFactor`、`LevelPopulation`、`TabNLTE`、`NormalizeMode`；谱与拟合 `SpecTable`、`SelectLines`、`PlotSpec`、`PrepInterpSpec`、`InterpSpec`、`PhFit`、`EPhFit`、`RRFit`、`DRFit`、`NRRFit`、`NDRFit`、`CBeli`、`CFit`、`ColFit`、`CColFit`、`EColFit`、`RBeli`、`EBeli`、`Ionis`、`Recomb`、`RRRateH`、`TwoPhoton`、`FracAbund`、`MaxAbund`、`DRBranch`、`DRStrength`、`RydBranch`、`ReinitCRM`；其他 `MicroFieldDist`、`MicroFieldMode`、`SetStarkZMP`、`SetGamma3B`、`SetOption`、`SetCXLDist`、`Voigt`、`QSReduction`、`ScaledSG`、`UnscaledSG`、`DebyeLength`、`ReadKronos`、`Print`、`PrintTable`、`WallTime`、`InitializeMPI`、`MPIRank`、`MemUsed`、`FinalizeMPI`、`System`、`SetProcID`、`SetUTA`、`CheckEndian`。
- **参数与返回值**：文件/字符串参数用 `"s"`、`"|s"`；数组用 `"O"`（列表/元组）转 `double*`；多数返回 `Py_None`，`Print` 等无返回。
- **依赖与调用关系**：依赖 `crm.h`、`global.h` 与 `libfac.a`；初始化调用 `InitCRM0()`；`ConvertToSCRM(fn)` 后所有调用经 `SCRMStatement()` 写为 scrm 脚本，供命令行复用。

### `ppol.c`（C 扩展 `pfac.pol`，偏振）
- **功能**：把偏振（polarization）模块 API 暴露给 Python，计算各向异性电子碰撞激发下的谱线偏振度表；可转写为 `spol` 脚本。
- **关键函数或类**：`PyInit_pol`（Py2 `initpol`）、`ConvertToSPOL`、`CloseSPOL`、`SPOLStatement`、`Print`、`System`、`Orientation`、`SetIDR`、`SetMaxLevels`、`SetMIteration`、`SetEnergy`、`SetDensity`、`SetMLevels`、`SetMCERates`、`SetMCIRates`、`SetMAIRates`、`PopulationTable`、`PolarizationTable`、`WallTime`、`InitializeMPI`、`MPIRank`、`MemUsed`、`FinalizeMPI`、`SetProcID`、`SetOption`。
- **参数与返回值**：`SetEnergy(e, es=0)`、`SetDensity(d)`、`SetMIteration(a, m=0, s=-1)`；`SetIDR(idr, pdr=None)` 接受列表作为方向分布；`PolarizationTable(fn, ifn|list=None, emin=0, emax=0, sth=0)` 写出偏振表；`MPIRank()` 返回 `[rank, size]`；`MemUsed()` 返回浮点。均通过 `PyArg_ParseTuple` 与 `Py_BuildValue`，返回 `Py_None` 为主。
- **依赖与调用关系**：依赖 `polarization.h`、`init.h`、`global.h` 与 `libfac.a`；初始化调用 `InitPolarization()`；与 `sfac/spol.c` 共用同一组 C API，物理实现在 `faclib/polarization.c`。

### `util.c`（C 扩展 `pfac.util`）
- **功能**：把数值工具（样条、插值、特殊函数）包装为 Python 函数。
- **关键函数或类**：`PyInit_util`（Py2 `initutil`）；`Spline`、`Splint`、`UVIP3P`、`DXLEGF`、`FM1MP`、`FERMID`、`FERINC`。
- **参数与返回值**：`Spline(x_list, y_list, dy1=1E30, dy2=1E30)` 返回二阶导列表 `y2`；`Splint(x, y, y2, x0)` 返回插值标量；`UVIP3P(x, y, x0, np=3)` 返回标量或列表；`DXLEGF(dnu, mu, cos_theta, id=3)` 内部 `acos` 后调用 `DXLEGF` 返回标量；`FM1MP(m, x, xm=0, xw0=0, xw1=0)` 按 `m` 选择 `FM1M/FM1MI/FM1P/FM1PI/FermiIntegral/FermiDegeneracy/SmoothedFD`；`FERMID/FERINC` 返回费米积分标量；模块导出 `util.error`。
- **依赖与调用关系**：依赖 `interpolation.h`、`cf77.h`、`orbital.h`、`global.h`；调用 faclib 的同名数值例程。

### `__init__.py`
- **功能**：`pfac` 包入口，导出版本与模块清单。
- **关键函数或类**：`from .version import version as __version__`；`__all__ = ['fac', 'crm', 'util', 'config', 'const', 'table', 'atom', 'spm', 'rfac', 'consts', '__version__']`。
- **参数与返回值**：无函数参数；`__version__` 为版本字符串。
- **依赖与调用关系**：依赖同包 `version.py`（不在本目录文件清单内，由上层生成）；C 扩展 `fac/crm/util/pol` 由动态模块提供。

### `config.py`
- **功能**：组态字符串的语法糖与展开工具，把“`2p2`、`3d*`、`[spd]`、`+/-`”等写法转成 `fac.AddConfig` 需要的 `(n, l, j, q)` 列表。
- **关键函数或类**：`avgconfig(configs)`、`closed(*configs)`、`config(*configs, group='')`、`expand(c)`、`cname(c)`、`distribute(s)`；模块变量 `_orbital_symbols`、`_group_name`、`_closed_shells`。
- **参数与返回值**：`distribute('2p2') -> ['2p-2','2p-1 2p+1','2p+2']` 形式的壳层分布列表；`config('3d*4s2', group='g')` 返回 `None` 并调用 `fac.AddConfig`；`expand` 返回所有组态展开；`cname` 返回规范化组态字符串。使用 `group.has_key`（Python 2 风格）。
- **依赖与调用关系**：`from pfac import fac`，依赖 `fac.SPECSYMBOL`、`fac.AddConfig`、`fac.SetAvgConfig`；被用户脚本及高级封装用于建模前的组态准备。

### `const.py`
- **功能**：物理常数与类氢能级公式。
- **关键函数或类**：常数 `AMU`、`Hartree_eV`、`Rate_AU/Rate_AU10/Rate_AU12`、`Area_AU20`、`Alpha`、`Ryd_eV`、`RBohr`、`FWHM`、`hc`、`hbc`、`Me_eV`、`Me_keV`、`Mp_MeV`、`Mp_keV`、`c`、`c10`、`e`、`e19`、`erg_eV`、`re`、`sig_t`、`kb`、`Maxwellian`；函数 `EnergyH(z, n, l, j)`。
- **参数与返回值**：`EnergyH` 按 Dockerfile 型相对论公式返回类氢能级（eV），`j=±1` 对应 `j=l±1/2`；非法参数抛出字符串异常（Python 2 风格）。
- **依赖与调用关系**：`from math import *`；被 `rfac.py`、`spm.py`、`aa.py` 等用于单位换算（`$e2v$`、速率单位、Maxwell 分布等）。

### `table.py`
- **功能**：实现符合 ApJ 机器可读表格格式的 ASCII `TABLE` 类。
- **关键函数或类**：`pad_text(t, p)`；`class TABLE`：`__init__(fname,title,authors,date,separator0,separator)`、`add_column(**c)`、`open(mode,fname='')`、`close()`、`write_header()`、`write_row(*data)`、`read_header()`、`read_columns(k,filter='',start=0,stop=-1)`、`convert2tex(tfn,k,...)`、`rewind()`。
- **参数与返回值**：列格式 `A/I/F/E+宽度` 转为 `%s/%d/%f/%E`；`read_columns` 按列下标返回列表的列表，`filter` 用 `eval` 按列名求值；`convert2tex` 输出 LaTeX 表格到文件。
- **依赖与调用关系**：仅依赖 `time`；被 `spm.py` 的 `tabulate_*` 用于生成速率表。

### `rfac.py`（按函数族分组，独立条目）
- **功能**：FAC 输出文件的读取器与后处理工具集（由京都大学 Keisuke Fujii 等贡献部分 `read_*` 函数）。
- **关键函数或类**：
  - 单位/角动量/组态工具：`e2v`、`k2lj`、`lj2k`、`cfgnr`、`nlq`、`nlqs`、`jenl`、`nqt`、`nqs`、`nstw`、`nstc`、`jsts`、`nsts`、`csts`、`remove_closed`。
  - 展宽：`voigt_fwhm(gw,lw)`、`doppler_fwhm(ti,z=1,m=0)`、`voigt(alpha,x)`、`convd(xd,yd,s0,gw,lw,x0,x1)`。
  - FAC 文本输出读取：`read_lev`、`read_en`、`read_enf`、`read_trf`、`read_tr`、`read_ai`、`read_ce`、`read_ci`、`read_rr`、`read_sp`、`read_wfun`、`read_den`、`read_pot`、`read_rra`、`read_rt`、`read_ham`、`valence_shells`、`read_bst`、`read_mix`、`interp_rra`。
  - 辅助解析：`_wrap_get_length`（内含 `get_lcomplex/get_lsname/get_lname`）、`_read_value`、`_get_header`、`comments`、`valid_lines`、`mix_header_lines`、`strnum`、`valid_nistlev`。
  - 外部能级/数据：`load_fac`、`load_atm`、`load_atbase`、`class FLEV`（`sort/add/copy/concat/combine/read_chianti/read_atbase/__init__/match/write/grotian`）、`class MLEV`、`aflev`、`cflev`、`pjflev`、`mflev`、`NISTCorr`、`EnergyMatch`、`jj2lsj`（调用外部 `jj2lsj` 程序）。
  - 电离势/压强电离：`read_rp`、`read_rps`、`read_rps_zk`、`interp_ipd_at`、`interp_ipd`、`read_ipd`、`tab_ipd`、`CorrCLow`、`jsp`、`ipd_more`、`ipd_ek`、`jsp_zd`。
- **参数与返回值**：典型 `read_lev(filename)` 返回能级字典/列表；`e2v(e,m=0)` 由能量（eV）换算相对论速度（cm/s 量级）；`load_atbase(fn, trans=0)` 读取 ATBASE 格式；多数函数返回 `dict`/`list`/`numpy` 数组。
- **依赖与调用关系**：`numpy`、`pylab`、`pfac.fac/const/util`、`multiprocessing`、`struct`、`datetime`；是 `atom.py`/`aa.py`/`spm.py` 的数据来源。

### `atom.py`（按函数族分组，独立条目）
- **功能**：面向“一个离子”的完整 FAC 计算流程封装（组态生成、能级求解、TR/CE/CI/RR/AI、能量修正、表格输出），支持多进程。
- **关键函数或类**：
  - 组态/基组生成：`grdcfg0`、`dist_iqs`、`cfgene`、`gen_cfgs`、`split_acfg`、`gck`、`gcz`、`run1c`、`jes`、`c2i`、`gvn`、`i2c`、`r1e`、`a1e`、`rank_cfg`、`cs`。
  - 通用：`reinit`、`get_index`、`get_terms`。
  - `class COMPLEX`：`__init__(bname, nele)`、`set_terms`、`set_name`、`set_ground`、`set_excited`、`set_ionized`、`set_recombined`。
  - `class CGROUP`：`__init__(type)`、`add_complex`。
  - `class ATOM`：`__init__(nele, asym, dir)`、`set_atom`、`add_excited`、`add_ionized`、`add_recombined`、`run_tr_ce`、`run_ci_rr`、`run_ai`、`energy_corrections`、`run_en`、`run_tr_ce_all`、`run_ci_rr_all`、`run_ai_all`、`print_table`、`set_configs`、`run_fac`。
  - 顶层入口：`atomic_data(nele, asym, iprint=1, dir='', **kw)`。
- **参数与返回值**：`ATOM(n)` 中以 `asym`（元素符号）与 `nele`（电子数）确定离子；`run_fac()` 依次调用 `run_en()` → `run_tr_ce_all()` → `run_ci_rr_all()` → `run_ai_all()`，返回 `None`；`run1c(x)` 为多进程 worker。
- **依赖与调用关系**：`from pfac.fac import *`、`from pfac import rfac, const`、`numpy`、`multiprocessing`；内部调用 `SetAtom`、`Closed`、`Config`、`ConfigEnergy`、`OptimizeRadial`、`Structure`、`TransitionTable`、`CETable`、`CITable`、`RRTable`、`AITable` 等 C API。

### `aa.py`
- **功能**：平均原子模型（Average Atom）驱动：单组分或化合物（化学式如 `H0.56C0.42Cu0.02`）在给定密度/温度下的自洽求解。
- **关键函数或类**：`zw4c(s)`（化学式→原子序数/权重数组）；`class AA`：`__init__(z=1,d=1.0,t=1.0,wm=None,dd=None,pref='',cc=None,znb=0,nr=6,...)`、`aa1p`、`ploop`、`run1z`、`rdos`、`rden`、`rpot`、`wden`、`rvg`、`ida`、`runvg`、`cleanvg`、`run(tol=0.1,imd=1,cvg=1,p=0.0,ptol=0.01)`、`irun(dtol=0.1,init=True)`；顶层 `AAPD(z,t,d=1.0,p=0.0,ptol=0.01,...)`、`read_hvs(fmt,hdr,nd,typ='den',cfg=2)`。
- **参数与返回值**：`AA(29,18.0,100.0).run()` 表示 Cu、18 g/cc、100 eV；`run()` 返回 `None`，输出态密度、电子密度、势等文件；`rdos/rden/rpot` 读回数据。
- **依赖与调用关系**：`from pfac.fac import *`、`from pfac import util, const, rfac`、`numpy`、`multiprocessing`；调用 `AverageAtom`、`SetOption`、`GetPotential`、`ElectronDensity` 等 C API。

### `spm.py`
- **功能**：光谱/速率的后处理与制表：总电离与复合速率制表、速率数据存取、温度网格、光谱合成。
- **关键函数或类**：`tabulate_trates(dfile,neles,z=26,pref='Fe')`、`tabulate_rates`、`write_trates`、`write_rates`、`save_rates(rates,sfile,dfile,**kwd)`、`read_rates(nt,nd,nele,pref='Fe',dir='',nion=2,only_total=0)`（含内嵌 `compare`）、`get_tgrid(z,nele,dt=0.15,amin=1E-2,limits=[])`、`get_complexes(nelectrons)`、`spectrum(neles,temp,den,population,pref,...)`、`maxwell(e,t)`。
- **参数与返回值**：`tabulate_*` 用 `pfac.table.TABLE` 写 `E8.2` 等格式文件；`save_rates` 用 `pickle` 序列化；`read_rates` 返回速率字典；`spectrum` 返回合成谱数组。
- **依赖与调用关系**：`from pfac.crm import *`、`from pfac.table import *`、`pfac.const`、`pickle`；依赖 CRM/C 扩展的 `Recomb`、`Ionis` 等拟合函数。

### `mpy.c`
- **功能**：最小主程序，把 CPython 解释器嵌入 FAC 可执行环境。
- **关键函数或类**：`main(int argc, char *argv[])`，调用 `Py_Main(argc, argv)`；`USE_MPI==1` 时先 `MPI_Init` 后 `MPI_Finalize`。
- **参数与返回值**：透传命令行参数给 Python；正常返回 0，MPI 初始化失败则 `abort()`。
- **依赖与调用关系**：依赖 `Python.h`、`sysdef.h`、`mpi.h`（可选）；由本目录 `Makefile.in` 构建。

### `Makefile.in`
- **功能**：构建并安装 `mpy`。
- **关键函数或类**：变量 `BINDIR=@prefix@/bin`、`CPPFLAGS=@CPPFLAGS@ -I${PYINC}`、`LIBS=@LIBS@ @FLIBS@ ${PYLIB}`；目标 `all: mpy`、`mpy: mpy.c`、`install`、`clean`。
- **参数与返回值**：`make` 生成 `mpy`，`make install` 安装到 `${BINDIR}`。
- **依赖与调用关系**：`@PYINC@`/`@PYLIB@` 由上层 `configure` 填充；源码为 `mpy.c`。

## 4. 接口说明

**导入方式**
```python
from pfac import fac            # 核心 C API：SetAtom/Config/Structure/TransitionTable...
from pfac import crm            # CRM C API：LevelPopulation/RateCoefficients...
from pfac import pol            # 偏振 C API（ppol.c；注意不在 __all__ 中）
from pfac import util           # Spline/Splint/UVIP3P/FM1MP...
from pfac import rfac, atom, aa, spm, config, table, const
```
`from pfac import *` 依据 `__init__.py` 的 `__all__`（不含 `pol` 与 `aa`，需显式导入）。

**典型调用链**（与 `atom.py`、`config.py` 中代码一致）
```
SetAtom("Fe")  →  Closed(...)  →  Config("g", ...)  →  ConfigEnergy(0)
  →  OptimizeRadial("g")  →  Structure("g")
  →  TransitionTable("g","g","tr.trf") / CETable(...) / RRTable(...) / CITable(...) / AITable(...)
  →  （可选）crm.AddIon / LevelPopulation / SpecTable ；pol.Orientation / PolarizationTable
  →  rfac.read_* / spm.save_rates 进行后处理
```
`ATOM.run_fac()` 内部即按 `run_en → run_tr_ce_all → run_ci_rr_all → run_ai_all` 串联。

**C 扩展桥接方式**：每个 `fac.c`/`pcrm.c`/`ppol.c`/`util.c` 中静态 `P*` 函数用 `PyArg_ParseTuple` 把 Python 参数解成 C 的 `int/double/char*/double*`，调用 faclib 函数，再用 `Py_BuildValue` 回到 Python；方法表 `fac_methods/crm_methods/pol_methods/util_methods`（`PyMethodDef[]`）经 `PyModuleDef` 与 `PyInit_fac/PyInit_crm/PyInit_pol/PyInit_util`（Py2 为 `initfac/initcrm/initpol/initutil`）注册。`ConvertToSFAC/SCRM/SPOL(fn)` 打开文本文件，此后每个调用经 `SFACStatement/SCRMStatement/SPOLStatement` 写成相应命令行脚本，实现“Python 建模、命令行复算”。

## 5. 物理效应与公式

**偏振（`pfac.pol` ↔ `ppol.c` ↔ `faclib/polarization.c`）**：各向异性电子碰撞激发使磁子能级布居产生取向（alignment），辐射谱线呈线性偏振。设观测方向与各向异性轴夹角为 $\theta$，$P_{2t}(\cos\theta)$ 为偶阶勒让德多项式（源码 `PL[t]` 由 `DXLEGF` 得到，`PL2[t]` 为其 $m=\pm2$ 关联项），$B_t$ 为上能级磁子能级布居展开系数（源码 `BL[t][i1]`），$A_t$ 由 Wigner 3j/6j 角动量耦合给出（`AL[t]`），$F_t$ 为与多极阶 $k$ 有关的因子（`FL[t]`），则 `PolarizationTable` 输出的谱线偏振度（源码 2097–2103 行）可写为

$$
P=\frac{\displaystyle\sum_{t=0}^{\mathrm{MAXPOL}} F_t\,PL2_t\,A_t\,B_t}
        {\displaystyle\sum_{t=0}^{\mathrm{MAXPOL}} PL_t\,A_t\,B_t},
\qquad PL_t=P_{2t}(\cos\theta).
$$

表中每行含 `nele, upper, lower, k, E(eV), 发射率, 强度 b(=分母), 偏振度 a(=比值)`。**注**：上式是按源码逐项还原的写法，符号/归一化约定（如 $F_t$ 中的 $(-1)^{(j_1+j_2)/2}$、$k<0$ 取反等）请以 `faclib/polarization.c` 为准；偏振度并非简单 $(I_\parallel-I_\perp)/(I_\parallel+I_\perp)$ 的字面实现，而是通过球张量展开计算。`Orientation(e, fn)` 设置取向轴/能量，`SetIDR` 给出入射方向分布，`SetEnergy(e, es)` 给出束能量及展宽。

**CRM 速率（`pfac.crm`）**：`LevelPopulation`/`TabNLTE` 求解稳态碰撞-辐射方程
$$
\sum_j R_{ij} N_j = 0,\qquad \sum_i N_i = 1,
$$
其中 $R_{ij}$ 含碰撞激发/电离（CE/CI）、辐射复合（RR）、双电子复合（DR）、自电离（AI）、电荷交换（CX）等，速率由 `SetCERates/SetCIRates/SetRRRates/SetAIRates` 提供；`PhFit/RRFit/DRFit/CFit/...` 给出拟合系数。**注**：该方程是 CRM 的标准形式，源码未以公式注释出现，此处为对 `crm.h`/`pcrm.c` API 的物理解读。

## 6. 上下游关系、构建方式、注意事项

- **上游**：`faclib`（`libfac.a`，C/Fortran 数值内核）与 `init.h/global.h/crm.h/polarization.h` 等头文件；`Python.h` 与 MPI（可选）。
- **下游**：用户 Python 脚本与 `sfac/scrm/spol` 命令行（通过 `ConvertTo*` 生成的脚本）；输出 `.en/.trf/.ce/.ci/.rr/.ai` 等表格由 `rfac.py` 再读取。
- **构建**：由 FAC 上层构建系统把 `fac.c/pcrm.c/ppol.c/util.c` 编译为 `pfac` 的 C 扩展；本目录 `Makefile.in`（`PYINC/PYLIB` 由 `configure` 替换）仅构建内嵌解释器的 `mpy`。
- **注意事项**：PFAC **非线程安全**——C 层大量使用全局/静态状态（`_state`、静态 `ErrorObject`、`sfac_file/scrm_file/spol_file` 及 faclib 内部全局表），GIL 并不保证多次调用间的状态隔离；源码中的并行方案是 `multiprocessing`（`rfac.py`、`atom.py`、`aa.py`），应按离子/任务分进程而非多线程。`config.py`、`const.py` 含 Python 2 风格写法（`has_key`、`raise 'string'`），移植到 Python 3 需修改；`__all__` 中的 `consts` 无对应文件，勿直接 `from pfac import consts`。

## 7. README 维护记录（自底向上）

- **定位与职责**：`python/` 是 PFAC 接口层，把 Python 命令映射到 `faclib/` 核心实现，并提供表读取与后处理工具。
- **底层依据**：`fac.c`、`pcrm.c`、`ppol.c`、`util.c`、`rfac.py`、`atom.py`、`spm.py`；LSP 命中 `python/const.py` 中的 `Rate_AU` 相关符号。
- **输入/输出**：输入 Python 脚本调用与组态/网格参数；输出二进制表及 `rfac.read_*` 解析结果。
- **验证与回归**：最小导入 `pfac.fac/crm/pol/util` 后运行 `demo/make check`；失败先查 `PYTHONPATH`、ABI 与 Python 版本。
- **已知限制**：PFAC 非线程安全；并行必须多进程；`config.py`/`const.py` 含 Python 2 风格写法；`__all__` 中的 `consts` 无对应文件。
- **公式核查**：\underline{$\sum_j R_{ij}N_j=0,\quad \sum_i N_i=1$}。
- **导航**：父级 [`../README.md`](../README.md)；核心库 [`../faclib/README.md`](../faclib/README.md)；SFAC [`../sfac/README.md`](../sfac/README.md)。

[返回上级](../README.md)