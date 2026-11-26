# QUADPACK 积分程序目录（quadpack/）

## 1. 目录定位与来源

本目录是第三方数值库 **QUADPACK**（Robert Piessens、Elise de Doncker，K.U. Leuven，源码注释日期 1980/1981/1983）的 Fortran 77 子集。根 README「Third party content that cannot be distributed under GPL」与 `UtilList` 均列出本目录（原文：`quadpack/, some routines from quadpack for quadrature.`），随 `fac_util.tar.gz` 分发，不按 GPL 授权。

在 FAC 计算链中它承担**一维数值积分**角色：`faclib/rates.c` 用 `DQAGS` 计算速率积分，`faclib/orbital.c` 用 `DQAGS` 分段计算费米型积分。C 侧经 `faclib/cf77.h`、`faclib/f2c.h`、`faclib/f2c.f90` 桥接宏调用。

## 2. 组织形式与文件分类

共 9 个 `.f` 文件与 1 个 `Makefile.in`，全部为双精度（`d` 前缀）实现：

- **用户入口层**：`dqagi.f`（无限区间）、`dqags.f`（有限区间带端点奇异性）、`dqng.f`（光滑函数非自适应）
- **核心自适应积分器**：`dqagie.f`（`dqagi` 的内核）、`dqagse.f`（`dqags` 的内核）
- **求积规则层**：`dqk15i.f`（变换后 15 点 Gauss–Kronrod）、`dqk21.f`（21 点 Gauss–Kronrod）
- **收敛加速与排序辅助**：`dqelg.f`（epsilon 算法外推）、`dqpsrt.f`（误差序列排序）

内部调用关系：`dqagi` → `dqagie`；`dqags` → `dqagse`；`dqagie` → `dqk15i`、`dqpsrt`、`dqelg`；`dqagse` → `dqk21`、`dqpsrt`、`dqelg`；`dqk21`、`dqk15i`、`dqelg` 等还调用机器常数函数 `d1mach`（由 `coul/d1mach.f` 提供）。

## 3. 逐文件说明

- **`dqagi.f`** — 功能：无限区间上的自适应积分通用入口。入口签名：`subroutine dqagi(f,bound,inf,epsabs,epsrel,result,abserr,neval,ier,limit,lenw,last,iwork,work)`（`f` 被积函数（需 `external`）；`bound` 有限端点；`inf` 区间类型：1 为 `(bound,+∞)`、-1 为 `(-∞,bound)`、2 为双向无穷；`epsabs`/`epsrel` 绝对/相对精度；`result` 积分近似；`abserr` 误差估计；`neval` 求值次数；`ier` 状态码；`limit` 子区间上限；`lenw` 工作数组长度；`last` 最终子区间数；`iwork`/`work` 工作数组）。数值方法要点：变量变换把无穷区间映射到有限区间，再做全局自适应细分与外推，转调 `dqagie`。在 FAC 中的调用方：`faclib/cf77.h:352`、`faclib/f2c.h:102`、`faclib/f2c.f90:768` 中有桥接声明（`genf2c.py:150`、`genf2c.py:230` 负责生成）；未发现 FAC 业务逻辑直接调用。

- **`dqagie.f`** — 功能：`dqagi` 的核心积分器，处理无限区间。入口签名：`subroutine dqagie(f,bound,inf,epsabs,epsrel,limit,result,abserr,neval,ier,alist,blist,rlist,elist,iord,last)`（`alist`/`blist` 子区间端点；`rlist` 积分结果；`elist` 误差估计；`iord` 误差序指针；其余同 `dqagi`）。数值方法要点：变量替换后用 `dqk15i` 在 `(0,1)` 子区间上求积，`dqpsrt` 维护误差降序表以挑选下一次细分区间，`dqelg` 对区间序列做 epsilon 外推；`ier` 区分正常收敛、精度不可达、舍入误差主导等情形。在 FAC 中的调用方：未发现 FAC 直接调用（由同目录 `dqagi` 内部调用）。

- **`dqags.f`** — 功能：有限区间上的自适应积分入口，可处理端点奇异。入口签名：`subroutine dqags(f,a,b,epsabs,epsrel,result,abserr,neval,ier,limit,lenw,last,iwork,work)`（`a`/`b` 积分上下限；`f`、`epsabs`、`epsrel`、`result`、`abserr`、`neval`、`ier`、`limit`、`lenw`、`last`、`iwork`、`work` 含义同 `dqagi`）。数值方法要点：以 `dqagse` 为内核，采用全局自适应细分加外推，对端点奇异更有效。在 FAC 中的调用方：`faclib/rates.c:346`、`faclib/rates.c:366`、`faclib/rates.c:384`（`IntegrateRate` 分段积分）；`faclib/orbital.c:5662`（费米型函数分段积分）；桥接声明见 `faclib/cf77.h:368`、`faclib/f2c.h:106`、`faclib/f2c.f90:825`。这是本目录在 FAC 中实际被使用最多的入口。

- **`dqagse.f`** — 功能：`dqags` 的核心积分器。入口签名：`subroutine dqagse(f,a,b,epsabs,epsrel,limit,result,abserr,neval,ier,alist,blist,rlist,elist,iord,last)`（参数同 `dqagie`，但区间为有限 `(a,b)`）。数值方法要点：先以 `dqk21` 计算整区间及二分结果，用 `dqpsrt` 维护误差排序逐次细分最大误差区间，并周期性调用 `dqelg` 做 epsilon 外推；用 `d1mach` 获取机器精度、下溢与上溢阈值。在 FAC 中的调用方：未发现 FAC 直接调用（由同目录 `dqags` 内部调用）。

- **`dqelg.f`** — 功能：用 Wynn epsilon 算法求近似序列的极限并给出误差估计。入口签名：`subroutine dqelg(n,epstab,result,abserr,res3la,nres)`（`n` 当前 epsilon 表第一列新元素个数；`epstab` 长度 52 的 epsilon 表数组；`result` 外推结果；`abserr` 由当前结果与前 3 个结果估计的误差；`res3la` 存最近 3 个结果；`nres` 调用次数，首次应为 0）。数值方法要点：只保留构造下一条对角线所需的elow 两条对角线元素，实现压缩 epsilon 表；用作自适应积分的收敛加速。在 FAC 中的调用方：未发现 FAC 直接调用（由 `dqagse`、`dqagie` 内部调用）。

- **`dqk15i.f`** — 功能：变换区间 `(0,1)` 子段上的 15 点 Gauss–Kronrod 求积规则。入口签名：`subroutine dqk15i(f,boun,inf,a,b,result,abserr,resabs,resasc)`（`boun` 原积分区间的有限端点，`inf = 2` 时置零；`inf` 原区间类型 -1/+1/+2；`a`、`b` 为 `(0,1)` 内的子区间；`result` 积分近似；`abserr` 误差估计；`resabs` 绝对函数积分近似；`resasc` 去均值绝对偏差积分近似）。数值方法要点：在 7 点 Gauss 规则上最优增加节点得 15 点 Kronrod 规则，用两规则之差估计误差；`inf = 2` 时把双向无穷积分拆成两个半轴之和。在 FAC 中的调用方：未发现 FAC 直接调用（由同目录 `dqagie` 内部调用）。

- **`dqk21.f`** — 功能：有限区间上的 21 点 Gauss–Kronrod 求积规则。入口签名：`subroutine dqk21(f,a,b,result,abserr,resabs,resasc)`（`a`、`b` 积分上下限；`result` 由 21 点 Kronrod 规则得到的近似；`abserr` 由其与 10 点 Gauss 规则之差给出的误差估计；`resabs`、`resasc` 同上）。数值方法要点：预置 10 个 Gauss 权与 11 个 Kronrod 节点/权，对称配对求值以减少函数调用；用 `d1mach` 处理机器精度与下溢。在 FAC 中的调用方：未发现 FAC 直接调用（由同目录 `dqagse` 内部调用）。

- **`dqng.f`** — 功能：光滑被积函数的非自适应积分入口。入口签名：`subroutine dqng(f,a,b,epsabs,epsrel,result,abserr,neval,ier)`（参数含义同 `dqags`，但无 `limit`/工作数组参数）。数值方法要点：在整个区间上依次尝试 21 点、43 点、87 点 Gauss–Kronrod–Patterson 规则，直到满足精度，不做区间细分。在 FAC 中的调用方：`faclib/cf77.h:361`、`faclib/f2c.h:104`、`faclib/f2c.f90:794` 中有桥接声明；未发现 FAC 业务逻辑直接调用。

- **`dqpsrt.f`** — 功能：维护局部误差估计的降序排列。入口签名：`subroutine dqpsrt(limit,last,maxerr,ermax,elist,iord,nrmax)`（`limit` 表容量；`last` 当前误差个数；`maxerr` 指向第 `nrmax` 大误差的下标；`ermax` 该误差值；`elist` 误差数组；`iord` 指向误差的指针数组；`nrmax` 当前最大误差在 `iord` 中的位置）。数值方法要点：每次调用插入两个新误差估计，用自上而下查最大、自下而上查最小的顺序搜索法维持排序，避免全表重排。在 FAC 中的调用方：未发现 FAC 直接调用（由 `dqagse`、`dqagie` 内部调用）。

## 4. 接口与调用约定

- **Fortran 77 固定格式**，全部双精度（`D` 前缀）实数版本；单精度 `sq*` 版本未打包。
- 被积函数 `f` 以过程名（函数名）传入，调用方必须用 `external f` 声明；回调形如以 `x` 为自变量、返回双精度值的函数。C 侧通过 `cf77.h` 的 `ROUTINE` 参数类型把 C 函数（如 `RateIntegrand`、`FermiIntegrand`）传入。
- 精度由 `epsabs`、`epsrel` 共同控制；源码注明若 `epsabs <= 0` 且 `epsrel` 小于 `max(50*机器精度, 0.5d-28)`，例程以 `ier = 6` 结束。目标精度表述为：结果误差不超过 `max(epsabs, epsrel*|真值|)`。
- 返回参数统一包括 `result`（积分近似）、`abserr`（绝对误差估计）、`neval`（被积函数求值次数）、`ier`（状态码：`0` 正常，正数异常终止）。
- 工作数组有两种组织方式：**用户入口**（`dqagi`/`dqags`）只暴露 `lenw`、`iwork`、`work`，由入口内部分配给 `alist`/`blist`/`rlist`/`elist`/`iord`；**核心层**（`dqagie`/`dqagse`）直接暴露这 5 个数组与 `limit`、`last`。
- `inf` 取值为整数：1 表示 `(bound,+∞)`、-1 表示 `(-∞,bound)`、2 表示 `(-∞,+∞)`。
- 机器常数函数 `d1mach` 不在本目录，需由 `coul/d1mach.f` 提供，链接时一并纳入。

## 5. 与上下游目录关系、构建方式

- 上游依赖：`coul/d1mach.f`（机器精度、最小正规数、上溢阈值、相对机器精度）；本目录不调用 `blas/`。
- 下游：`faclib/rates.c`、`faclib/orbital.c` 直接调用 `DQAGS`；`DQAGI`、`DQNG` 仅在桥接层声明；内部例程 `DQAGSE`、`DQAGIE`、`DQELG`、`DQK15I`、`DQK21`、`DQPSRT` 由本目录入口互相调用。
- 构建：根 `configure` 后进入本目录执行 `make`。`Makefile.in` 中 `FC = @F77@`、`FFLAGS = @FFLAGS@`，`SRC` 列出 9 个 `.f`，`.f.o` 规则编译后由 `ar r ${TOPDIR}/libfac.a $(OBJS)` **直接并入顶层 `libfac.a`**（与 `minpack/` 相同，不生成独立库）。`make clean` 删除 `*.o`、`*.a`、`*~`。
- 根 `Makefile.in` 的 `lib` 目标在 `minpack` 之后、`ionis`/`modqed`/`faclib` 之前执行 `cd quadpack; make`，最后统一 `ranlib libfac.a`。

## 6. README 维护记录（自底向上）

- **定位与职责**：自适应求积例程集，产物直接并入 `libfac.a`。
- **底层依据**：`dqags.f`、`dqagse.f`、`dqk21.f`、`dqelg.f`、`dqagi.f`；被 `faclib/rates.c`、`orbital.c` 调用。
- **输入/输出**：被积函数、积分区间与容差；输出积分值与误差估计。
- **验证与回归**：通过速率积分与 `demo` 回归间接验证。
- **已知限制**：第三方代码；机器常数依赖 `coul/d1mach.f`。
- **公式核查**：源码未找到独立于 Fortran 实现的求积公式原文，需按 QUADPACK 文档人工核查。
- **导航**：父级 [`../README.md`](../README.md)。

[返回上级](../README.md)