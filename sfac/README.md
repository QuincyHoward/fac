# 命令行驱动层 `sfac/`：`sfac` / `scrm` / `spol`

## 1. 目录定位与角色

本目录实现三个**命令行可执行程序**及其共用的输入语言解析器：`sfac`（原子结构、跃迁与速率计算）、`scrm`（碰撞-辐射模型 CRM）、`spol`（谱线偏振）。它们不是 Python 解释器，而是把 `pfac` 的 API“翻译”成一种**语法近似 Python 的脚本语言**：支持函数式调用、变量赋值、`$变量` 引用、列表/元组、关键字参数 `#` 注释与 `\` 续行，但**没有 `if/for/while` 等流程控制**，也不执行真正的 `import`（`EvalFile` 显式跳过以 `from ` / `import ` 开头的行）。因此 `sfac.py` 风格的脚本可以直接喂给命令行复算。

与 `python/` 的关系：`python/fac.c`、`pcrm.c`、`ppol.c` 的 `ConvertToSFAC/SCRM/SPOL` 把 Python 调用写成这里的输入脚本；三套程序共用同一 faclib C API（`InitFac0/InitCRM0/InitPolarization`），命令名与 `pfac.fac/pfac.crm/pfac.pol` 导出名基本一一对应。

## 2. 组织形式与文件分类

| 文件 | 分类 | 说明 |
|---|---|---|
| `sfac.c`（约 132 KB） | 命令主程序+方法实现 | `sfac` 全部命令（结构/跃迁/速率/组态/数据库等） |
| `scrm.c` | 命令主程序+方法实现 | `scrm` 全部 CRM 命令 |
| `spol.c` | 命令主程序+方法实现 | `spol` 全部偏振命令 |
| `stoken.c` / `stoken.h` | 共用解析库 | 词法切分、变量、语句求值、命令行参数分派 |
| `Makefile.in` | 构建 | 链接 `libfac.a` 生成三个可执行并安装 |

## 3. 逐文件说明

### `sfac.c`（独立条目，按命令族理解）
- **功能**：`sfac` 命令的入口与所有 `P*` 命令处理器：解析 `SetAtom/Config/Structure/TransitionTable/...` 等语句并调用 faclib。
- **关键函数或类**：`main`（`InitFac0()` → `SetModName("fac")` → `ParseArgs`）；命令族包括——组态/组 `SetAtom`、`Config`、`Closed`、`ClosedShells`、`AvgConfig`、`AverageConfig`、`ReadConfig`、`AddConfig`、`RemoveConfig`、`ListConfig`、`SetGroup`、`GroupStat`、`ConfigEnergy`、`SetConfigEnergyMode`、`ConfigUTA`、`CutMixing`、`ReinitConfig/ReinitRecouple`；径向/结构 `SetRadialGrid`、`SolveBound`、`OptimizeRadial`、`OptimizeGroup`、`RefineRadial`、`FreezeOrbital`、`Structure`、`StructureEB`、`StructureMBPT`、`AdjustEnergy`、`CorrectEnergy`、`SortLevels`、`LevelInfo`、`OrbitalStats`、`AverageAtom`、`ReinitRadial/ReinitStructure`；跃迁/速率 `TransitionTable`、`CETable`、`CITable`、`RRTable`、`AITable`、`CXTable`、`AIBranch`、`SetCEGrid` 等网格与选项命令、`SetTransition*`；R-矩阵族、数据库表操作、势函数存取、MPI/工具命令等（方法表与 `python/fac.c` 的 `fac_methods[]` 对应，见源码第 5665 行起 `static METHOD methods[]`）。
- **参数与返回值**：每个处理器签名 `int P*(int argc, char *argv[], int argt[], ARRAY *variables)`；用 `DecodeArgs`、`DecodeGroupArgs`、`atoi/atof` 解析，返回 0 成功、 `-1` 参数错误；`SetModName("fac")` 使解释器接受 `SetAtom(...)`、`fac.SetAtom(...)`、`pfac.fac.SetAtom(...)` 三种前缀写法。
- **依赖与调用关系**：依赖 `init.h`、`cf77.h`、`stoken.h`、`mpiutil.h`、`global.h`、`libfac.a`；与 `stoken.c` 一起编译。

### `scrm.c`（独立条目）
- **功能**：`scrm` 命令入口与 CRM 命令集；调用 `InitCRM0()` 初始化 CRM 库。
- **关键函数或类**：`main`（`InitCRM0()` → `SetModName("crm")` → `ParseArgs`）；`static METHOD methods[]`（第 1033 行起）包含 `Print`、`Exit`、`SetUTA`、`CheckEndian`、`DRSuppression`、`EleDist/CxtDist/PhoDist`、`SetEleDist/SetCxtDist/SetPhoDist`、`SetEleDensity/SetCxtDensity/SetPhoDensity`、`SetNumSingleBlocks`、`SetExtrapolate`、`SetEMinAI`、`SetInnerAuger`、`SetCascade`、`SetIteration`、`SetRateAccuracy`、`SetBlocks`、`RateTable`、`AddIon`、`SetCERates/SetCXRates/SetTRRates/SetCIRates/SetRRRates/SetAIRates/SetAIRatesInner`、`SetAbund`、`SetRateMultiplier`、`InitBlocks`、`LevelPopulation`、`Cascade`、`SpecTable`、`PlotSpec`、`PrepInterpSpec`/`InterpSpec`、`TabNLTE`、`SelectLines`、`PrintTable`、`ReinitCRM`、`DRBranch`、`DRStrength`、`DumpRates`、`ModifyRates`、`RydBranch`、`NormalizeMode`、`SetBornFormFactor`、`SetBornMass`、`SetGamma3B`、`ReadKronos`、`SetStarkZMP`、`SetOption`、`SetCXLDist`、`MemENTable`、`RateCoefficients`、`WallTime`、`InitializeMPI`、`MPIRank`、`MemUsed`、`FinalizeMPI`、`System`、`SetProcID`。
- **参数与返回值**：同 `sfac.c` 的 `P*` 约定；`InitBlocks` 前需 `AddIon` 与 `Set*Rates`；`LevelPopulation`/`SpecTable` 无 Python 式返回，结果写入文件或标准输出。
- **依赖与调用关系**：依赖 `crm.h`（经 `global.h`）、`stoken.h` 与 `libfac.a`；与 `python/pcrm.c`（`pfac.crm`）共享同一 C API。

### `spol.c`（独立条目）
- **功能**：`spol` 命令入口与偏振命令集；调用 `InitPolarization()`。
- **关键函数或类**：`main`（`InitPolarization()` → `SetModName("spol")` → `ParseArgs`）；`methods[]`（第 378 行起）含 `Print`、`Exit`、`Orientation`、`SetIDR`、`SetMaxLevels`、`SetMIteration`、`SetEnergy`、`SetDensity`、`SetMLevels`、`SetMCERates`、`SetMAIRates`、`SetMCIRates`、`PopulationTable`、`PolarizationTable`、`WallTime`、`InitializeMPI`、`MPIRank`、`MemUsed`、`FinalizeMPI`、`System`、`SetProcID`、`SetOption`。
- **参数与返回值**：`P*` 处理器用 `DecodeArgs` 把列表转为 `double*` 传给 `SetIDR(idr, pdr)`、`PolarizationTable(fn, ifn, emin, emax, sth)` 等；返回 0/-1。
- **依赖与调用关系**：依赖 `polarization.h`、`init.h`、`global.h`、`stoken.h` 与 `libfac.a`；与 `python/ppol.c`（`pfac.pol`）共享 API。

### `stoken.c`（独立条目）
- **功能**：三个命令共用的输入语言解释器：读行、去注释与续行、分词、变量代换、语句求值、命令行分派。
- **关键函数或类**：`SetModName`（生成 `sfac.`/`pfac.fac.` 或 `crm.`/`pfac.crm.`、`spol.`/`pfac.spol.` 前缀）、`VariableExists`、`DecodeArgs`、`GetLine`（stdin 打印 `>>> `）、`GetValidLine`、`MethodIndex`、`TokenizeLine`、`EvalFile`、`EvalStatement`、`ErrorOcurred`、`ParseArgs`。
- **参数与返回值**：`ParseArgs(argc, argv, methods)` 分派三种模式——无文件参数：读 stdin 并逐行执行（`exebyline=1`）；`-e "语句"`：单行求值；其余：把每个文件当作参数，先整体解析再依次求值（`exebyline=0`）。错误码 `ERR_LINEUNTERMINATED=-1`、`ERR_LINETOOLONG=-2`、`ERR_NOVARIABLE=-3`、`ERR_ARGSTOOMANY=-4`、`ERR_SYNTAX=-5`、`ERR_EVAL=-6`。
- **依赖与调用关系**：依赖 `stoken.h`、`parser.h`（`Parse/SetParserWhite/SetParserBreak/SetParserQuote/StrTrim`）、`array.h`、`global.h`；被三个 `main` 调用。

### `stoken.h`（独立条目）
- **功能**：解析器的类型、常量与接口声明。
- **关键函数或类**：宏 `MAXNARGS 5000`、`MAXLINELENGTH 100000`、`MAXMETHODNAME 128`，标记 `NUMBER/STRING/TUPLE/LIST/KEYWORD`、`COMMENT '#'`、`CONTINUE '\\'`，错误码；结构体 `METHOD{name, func, arg_style}`、`VARIABLE{name,value,type}`、`STATEMENT{nline,imethod,argc,argv[],argt[]}`；声明 `VariableExists/DecodeArgs/GetLine/GetValidLine/MethodIndex/TokenizeLine/EvalFile/EvalStatement/FreeStatementData/FreeVariableData/ErrorOcurred/SetModName/ParseArgs`。
- **参数与返回值**：函数指针类型 `int (*func)(int argc, char *argv[], int argt[], ARRAY *variables)`，定义命令处理器的统一签名。
- **依赖与调用关系**：包含 `array.h`、`parser.h`、`stdlib/stdio/ctype/string.h`；由 `stoken.c` 与三个 `*.c` 包含。

### `Makefile.in`（独立条目）
- **功能**：构建三个命令行工具。
- **关键函数或类**：`all: sfac scrm spol`；`sfac: sfac.c stoken.c ${TOPDIR}/libfac.a` → `${CC} -o sfac sfac.c stoken.c ${ALL_CFLAGS}`，`scrm`、`spol` 同理；`install` 安装到 `@prefix@/bin`；`clean` 删除产物。
- **参数与返回值**：`make` 生成 `sfac/scrm/spol`，`make install` 安装，`make clean` 清理。
- **依赖与调用关系**：依赖上层 `configure` 提供的 `CC/CFLAGS/CPPFLAGS/LDFLAGS/LIBS/TOPDIR` 与静态库 `libfac.a`。

## 4. 接口说明

**用法**（`ParseArgs` 定义）
```
sfac                      # 交互式从 stdin 读取，提示符 ">>> "，逐行执行
sfac -e 'SetAtom("Fe")'   # 执行单条语句
sfac in1.in in2.in        # 依次执行多个脚本文件（先整体解析再执行）
scrm [同上]               # CRM 计算
spol [同上]               # 偏振计算
```

**输入文件语法**（由 `DecodeArgs/TokenizeLine` 决定）
- 函数调用形如 `方法名(参数...)`；可带模块前缀：`Config(...)`、`fac.Config(...)`、`pfac.fac.Config(...)`（`SetModName` 决定合法前缀；`scrm` 为 `crm.`/`pfac.crm.`，`spol` 为 `spol.`/`pfac.spol.`）。
- 参数类型：`NUMBER`（裸 token）、`STRING`（`"..."`/`'...'`）、`TUPLE`（`(a,b)`）、`LIST`（`[a,b]`）、`KEYWORD`（`name=value`）；变量用 `$name` 引用，赋值写作 `name = value`（`TokenizeLine` 中 `brkpos==1` 分支）。
- `#` 为行注释；行尾 `\` 续行（最多 `MAXLINELENGTH=100000`）；单行最多 `MAXNARGS=5000` 个参数；以 `from ` 或 `import ` 开头的行被忽略。
- 无流程控制：不支持 `if/for/while/def`；出错由 `ErrorOcurred` 打印行号与类型（文件模式直接 `exit(1)`）。

**sfac 典型脚本**
```
SetAtom("Fe")
Closed("1s2 2s2 2p6")
Config("g", "3d6 4s2")
ConfigEnergy(0)
OptimizeRadial("g")
Structure("g")
TransitionTable("g", "g", "fe.trf")
CETable("fe.ce")
```

**scrm 典型脚本**：`AddIon(...)` → `SetCERates/SetCIRates/SetRRRates/SetAIRates(...)` → `SetEleDensity(...)` → `InitBlocks()` → `LevelPopulation()` → `SpecTable(...)`；`spol` 典型脚本：`SetEnergy(e, es)` → `SetDensity(d)` → `Orientation(etrans, fn)`（`etrans` 为跃迁能，第二参为可选输出文件名字符串，无参即 `Orientation()`；源码 `faclib/polarization.c:1704 Orientation(char *fn, double etrans)`，命令解析见 `sfac/spol.c:266–283`，Python 绑定见 `python/ppol.c:379–381`）→ `SetIDR(idr,[...])` → `SetMLevels(...)`/`SetMCERates(...)` → `PolarizationTable("pol.out", ...)`。

## 5. 物理效应与公式

**scrm（CRM 速率）**：`scrm` 解稳态碰撞-辐射方程组
$$
\sum_j R_{ij}\,N_j=0,\qquad \sum_i N_i=1,
$$
$R_{ij}$ 由 `SetCERates`（电子碰撞激发）、`SetCIRates`（碰撞电离）、`SetRRRates`/`SetTRRates`（复合）、`SetAIRates`（自电离）、`SetCXRates`（电荷交换）及辐射跃迁构成；`DRSuppression`、`SetDensity`、`SetGamma3B` 等控制密度效应。`RateCoefficients`/`TabNLTE` 输出有效速率与 NLTE 布居。**注**：方程为 CRM 通用形式（源码未给出公式注释），对应关系依据 `crm.c`/`pcrm.c` 命令语义。

**spol（谱线偏振）**：`spol` 处理电子束/等离子体各向异性激发导致的磁子能级取向（alignment）。取向轴由 `Orientation(e, fn)` 给出（$e$ 为能量或取向参数），束方向分布由 `SetIDR` 给出，电子密度由 `SetDensity` 给出；`PolarizationTable` 对每条线输出强度 $b$ 与偏振度 $a$。按 `faclib/polarization.c`（`a/b`，第 2097–2103 行）：
$$
P=\frac{\sum_t F_t\,PL2_t\,A_t\,B_t}{\sum_t PL_t\,A_t\,B_t},\qquad PL_t=P_{2t}(\cos\theta),
$$
其中 $B_t$ 为上能级磁子能级布居系数、$A_t$ 为 3j/6j 角动量因子、$F_t$ 为多极阶相关因子。**注**：这是按源码还原的表达式，符号与归一化以 `faclib/polarization.c` 为准（例如 `PL2[0]=0`、`k<0` 时 $F_t$ 变号），不可简单等同于初等的 $(I_\parallel-I_\perp)/(I_\parallel+I_\perp)$。

## 6. 上下游关系、构建方式、注意事项

- **上游**：`${TOPDIR}/libfac.a`（faclib 静态库）；`python/` 侧 `ConvertToSFAC/SCRM/SPOL` 生成的脚本是主要输入来源之一。
- **下游**：输出 `.en/.trf/.ce/.ci/.rr/.ai`、布居表、速率表、偏振表，供 `pfac.rfac`/`pfac.spm` 读取和绘图。
- **构建**：在 FAC 顶层 `configure && make` 后由本目录 `Makefile.in` 编译（`make -C sfac` / `make install` 安装到 `@prefix@/bin`）；三个程序均把 `stoken.c` 与各自主文件、静态库一起链接。
- **注意事项**：脚本语言无流程控制，`import` 行仅被忽略而非执行；`sfac` 中 `SetModName("fac")` 略显反直觉（实际接受 `fac.`/`pfac.fac.` 前缀）；文件模式先解析全部语句再执行，语法错误会整体退出；与 PFAC 一样**非线程安全**（faclib 全局状态），请使用多进程或独立进程并行；`MAXNARGS/MAXLINELENGTH` 有限制，超大输入需分块。

## 7. README 维护记录（自底向上）

- **定位与职责**：`sfac/` 提供 SFAC/SCRM/SPOL 命令行前端，是同一核心物理库的非 Python 入口。
- **底层依据**：`sfac.c`、`scrm.c`、`spol.c`、`stoken.c`；命令最终调用 `faclib/` 的同一组核心函数。
- **输入/输出**：输入类 Python 脚本语言文件；输出 `.en/.trf/.ce/.ci/.rr/.ai`、布居、速率和偏振表。
- **验证与回归**：与 PFAC 共享后端结果口径；可对照 PFAC 生成表做一致性检查。
- **已知限制**：脚本语言无流程控制；`import` 行被忽略；文件模式先解析全部语句；同样非线程安全。
- **公式核查**：\underline{$\sum_j R_{ij}N_j=0,\quad \sum_i N_i=1$}。
- **导航**：父级 [`../README.md`](../README.md)；核心库 [`../faclib/README.md`](../faclib/README.md)；PFAC [`../python/README.md`](../python/README.md)。

[返回上级](../README.md)