# FAC 杂项开发文档

本目录收录两篇与 FAC 开发、使用和协作密切相关的专题说明：`jj2ls.md` 讲述如何把 FAC 产生的 jj 耦合组态状态函数交给 GRASP2K 的 `jj2LSJ` 模块转换为 LS 耦合表象；`gitcommit.md` 则是向 FAC 上游仓库贡献代码时的 Git 操作清单。

## 1. jj2ls.md —— 在 FAC 中使用 jj2LSJ

### 用途
FAC 全程基于 Dirac 方程，采用全相对论的 **jj 耦合**；而大量原子数据库、文献与 LS 耦合程序使用 LSJ 项符号。FAC 的 `BasisTable` 函数可以直接生成 GRASP2K 所需的输入文件，借助 GRASP2K 的 `jj2LSJ` 模块把 jj 耦合 CSF 基底变换为 LS 耦合 CSF 基底，输出每个能级在 LSJ 表象下的组成（混合系数与百分比）。该工具是 FAC 结果与 LS 耦合世界之间的桥梁，便于交叉校验能级标记、与 Cowan / MCHF 等程序对比。

### 输入与 FAC 侧用法
示例脚本（针对 Be）如下：

```python
SetAtom('Be')

Config('g1', '1*2 2*2')
Config('g3', '1*2 2*1 3*1')
Config('g4', '1*2 2*1 4*1')

ConfigEnergy(0)
OptimizeRadial('g1')
ConfigEnergy(1)

Structure('Be.en', ['g1'])
Structure('Be.en', ['g3'])
Structure('Be.en', ['g4'])

BasisTable('Be', 10)
```

- `SetAtom` 指定原子；`Config` 定义三组组态组 `g1`/`g3`/`g4`。
- `ConfigEnergy(0)` → `OptimizeRadial('g1')` → `ConfigEnergy(1)` 完成平均组态径向势的自洽优化；只把最低组态放入 `OptimizeRadial`。
- 三次 `Structure` 把各组态写入同一个 `Be.en`。
- `BasisTable('Be', 10)` 生成 `Be_001.c` … `Be_008.c` 及 `Be_001.cm` … `Be_008.cm`。后缀 `_00*` 表示输出块号；由于 GRASP2K 每次只能处理一个块，这些文件必须分别传入。
- `*.c` 文件中的 `CSF(s)` 段以 jj 记号书写（如 `1s(2) 2p(1) 4p(1) 3/2 3/2 0+`），对应 FAC `.en` 文件的 `name` 字段。

### 必备的 GRASP2K 源码修正
要让 FAC 输出可被 `jj2lsj` 读取，至少需修补两处 bug（源码取自 http://cpc.cs.qub.ac.uk/summaries/ADZL_v1_1.html）：

1. `jj2lsj_code.f90` 的 `asf2ls` 子程序开头，在 `ISPAR(iw1+...)` 的索引中加上 `NCFMIN-1`：
   ```fortran
   wb = zero
   do LS_number = 1, asf_set_LS%csf_set_LS%nocsf
      if ((asf_set_LS%csf_set_LS%csf(LS_number)%parity == "+" &
         .and.  ISPAR(iw1+NCFMIN-1) == 1)  .or.                 &
         (asf_set_LS%csf_set_LS%csf(LS_number)%parity  == "-" &
         .and.  ISPAR(iw1+NCFMIN-1) == -1)) then
   ```
2. `jj2lsj_code.f90` 的 `setLS_job_count()` 子程序中，`if (all_occupation(isubc).eq.0) then` 分支改为：
   ```fortran
   if(all_occupation(isubc).eq.0) then
      if(isubc.gt.1) then
         Li(isubc)  = 0;          L_i(isubc) = L_i(isubc-1)
         Si(isubc)  = 0;          S_i(isubc) = S_i(isubc-1)
      else
         Li(isubc)  = 0;          L_i(isubc) = 0
         Si(isubc)  = 0;          S_i(isubc) = 0
      endif
      if(isubc .lt. asf_set_LS%csf_set_LS%nwshells) then
         call setLS_job_count(isubc + 1, rez)
      else
         if(ittk(S_i(isubc),L_i(isubc),J).eq.1) &
              call setLS_action(action_type, rez)
      end if
   else
   ```

编译安装：在 GRASP2K 根目录执行 `source make-environment-gfort`（gfortran；其他编译器见 GRASP2K README），再 `cd src && make`，可执行文件 `jj2lsj` 生成于 `$GRASP$/bin`。

### 运行与输出
- 当前目录必须存在 `isodata` 文件（含原子序数、质量数、Fermi 分布参数 a/c、核质量、核自旋、核偶极与四极矩等）；`jj2lsj` 运行前只检查其存在性，数值本身不关键。
- `jj2lsj` 是交互式程序，启动后打印横幅并提示 `Name of state`。输入块名（如 `Be_002`，对应 `Be_002.c`/`.cm`）后，依次加载配置对称列表与混合系数；遇到 “Mixing coefficients from a CI calc.?” 等问题一般连续回答 `y`。
- 完成后得到 `Be_002.lsj.lbl`，每行含 `Pos J Parity Energy Total Comp. of ASF`，并给出 LSJ 组成，例如某能级 99.7% 为 `1s(2).2s_2S.4s_1S`、0.6% 为 `1s(2).2p_2P.4p_1S`。

### 与 FAC 开发的关系
`BasisTable` 属于 FAC 的结构/组态输出功能（对应 `faclib/config.c`、`faclib/structure.c`）。本文记录了 FAC 到 GRASP2K 的完整数据通道以及所需补丁，使开发者在发布和校验原子结构数据时，可以把 FAC 的 jj 标记映射到广泛使用的 LSJ 项符号，并与 LS 耦合代码进行一致性比对。

## 2. gitcommit.md —— 向 FAC 上游贡献代码的 Git 清单

### 用途
一份极简的 fork + topic branch 工作流备忘录，供 FAC 开发者把本地改动整理成独立分支、推送到个人仓库，与上游 `master` 同步后再发起合并请求（PR）。

### 输入与命令序列
```bash
git checkout -b bname               # 新建并切换到主题分支 bname
git commit -a -m 'msgs'             # 提交所有已跟踪文件的改动并写明提交信息
git push origin bname              # 把主题分支推送到个人 fork
git checkout master                # 回到本地 master
git fetch upstream                 # 拉取上游仓库最新引用
git merge upstream/master          # 把上游更新合并进本地 master
git push                           # 同步本地 master 到 origin
git branch -D bname                # 删除本地主题分支
git push origin --delete bname     # 删除远端 fork 上的主题分支
```

### 输入 / 输出
- 输入：一个已配置 `origin`（个人 fork）与 `upstream`（FAC 上游）远端、且本地有未提交改动的仓库；`bname` 为分支名，`msgs` 为提交说明。
- 输出：无程序输出。执行后个人 fork 的 `master` 与上游同步，主题分支被推送供 PR 审查，本地与远端的临时分支均被清理。

### 与 FAC 开发的关系
FAC 采用 GitHub fork / Pull Request 协作模式。该清单保证每次改动都在独立分支上完成、本地 `master` 始终与 `upstream` 同步，便于维护者逐项审查和合并，是参与 FAC 开发的标准操作约定。

## 3. README 维护记录（自底向上）

- **定位与职责**：`doc/misc/` 存放开发流程与实用脚本说明，不承载核心物理公式。
- **底层依据**：`gitcommit.md`、`jj2ls.md` 等实际脚本与操作清单。
- **输入/输出**：输入仓库状态与提交参数；输出协作流程说明或文件列表。
- **验证与回归**：按文档命令在安全环境执行；不参与数值回归。
- **已知限制**：开发流程依赖团队约定；任何会改写仓库状态的命令都需人工确认。
- **公式核查**：无物理公式；无需下划线注记。
- **导航**：父级 [`../README.md`](../README.md)；根 [`../../README.md`](../../README.md)。

[返回上级](../README.md)