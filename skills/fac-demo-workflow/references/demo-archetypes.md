# Demo 通用原型表

本表刻意不使用具体示例名，只保留可迁移的模式。遇到新算例时先映射到原型，再套用对应流程。

| 原型 | 输入依赖 | 核心 API 类型 | 输出表 | 回归方式 | 资源级别 | 常见陷阱 |
|---|---|---|---|---|---|---|
| 原子结构 + 辐射跃迁 | 元素、闭壳层、组态组、中心势 | `Config`、`OptimizeRadial`、`Structure`、`TransitionTable` | `.en`、`.tr`、`.pot` | `check_en`、`check_tr` | 低—中 | `OptimizeRadial` 只用于低组态；ASCII eV 与二进制 Hartree；`E0` 非零索引 |
| 碰撞激发（含磁子态） | 结构表、上下能级、能量网格 | `CETable`、`CETableMSub`、`SetCEGrid*` | `.ce`、`.ceM` | `check_ce` | 中 | CE 截面含 π；索引语义；OpenMP 行序；死键影响相对容差 |
| 碰撞电离 | 初末电荷态结构、用户网格 | `SetUsrCIEGrid`、`CITable` | `.lev`、`.ci` | `check_en`、`check_ci` | 中 | EII 截面无 π；两次结构调用决定 block 顺序；网格需一致 |
| PI / RR | 复合前后组态、能级表 | `RRTable`、`PrintTable` | `.lev`、`.rr` | `check_en`、`check_rr` | 中 | 参数顺序、Milne 关系记号、1% 相对容差 |
| AI / DC | 双激发组态、残余离子组态 | `AITable` | `.lev`、`.ai` | `check_en`、`check_ai` | 中 | 表方向；DC 强度单位；完整 DR 还需分支比与辐射率 |
| CRM + 谱合成 | 二进制 `.en/.tr/.ce`、温度密度 | `Set*Rates`、`InitBlocks`、`LevelPopulation`、`SpecTable`、`RateTable` | `.sp`、`.rt`、`.r*` | `check_sp`、`check_rt` | 中 | `SetBlocks` 语义；`strength` 随 `TYPE` 变；弱线容差 |
| 大规模多离子谱 | 多电荷态全过程数据、温密网格 | `spm.spectrum`、`FracAbund`、`PlotSpec` | 大量 `.sp/.rt/.d*/.sav/.plt` | 无官方基准，产物 + 趋势检查 | 很高 | 电荷态范围不一致；相邻态缺失；小时级、GB 级输出 |
| 偏振 | 结构、多极跃迁、磁子能级 CE | `TransitionTable(m=...)`、`CETableMSub`、`Orientation`、`PolarizationTable` | `.en/.tr/.ce`、`pop.txt`、`pol.txt` | 三类表回归，文本人工检查 | 中 | `a/b` 不是初等强度比；能量注释与代码可能矛盾 |
| R 矩阵 | 靶态、边界、两区基与表面振幅 | `RMatrixTargets`、`RMatrixBoundary`、`RMatrixBasis`、`RMatrixSurface`、`RMatrixCE` | `.b*`、`.d*`、`r1.d` | 无官方基准，依赖完整性 + 网格 + Ω 合理性 | 极高 | 两阶段顺序；硬编码线程数；旧注释能量范围 |
| 底层诊断 | 组态、CI 开关、速率与简单 CRM | `SetCILevel`、`Structure`、`MaxwellRate` | `.en`、`.cir/.cer`、`.sp` | 部分有基准，部分不比对 | 低 | 关闭 CI 时多条能量为 0 是预期；中间产物不误入 `RESULTS` |

## 映射到流程的规则

- 只要输出 `.en` 且后续依赖它，就先走结构原型，再进入下游原型。
- 出现 `.sp/.rt` 时先确认是单离子 CRM 还是多离子谱流程，两者资源和验证方式不同。
- 出现 `.b*/.d*` 或两阶段命令时，先按 R 矩阵原型检查前置产物。
- 有 `pop.txt/pol.txt` 时，不把它们当回归表，除非用户明确提供了扩展后的比对规则。
