---
name: fac-demo-workflow
description: Abstract FAC demo workflow for choosing an execution path, identifying input dependencies, classifying regression modes, estimating resource needs, and interpreting output tables. Use when the user asks how to run or organize a demo without binding the answer to a specific case.
---

# FAC Demo 通用工作流

## Overview

把 `demo/` 中的示例抽象成可复用的工作流：先按物理过程和输出表类型分类，再判断输入依赖、回归方式、资源消耗和常见陷阱。本 skill 不绑定具体示例名；具体分类见 `references/demo-archetypes.md`。

## Workflow Decision Tree

1. **识别原型**：根据目标输出表与核心 API 判断属于结构/跃迁、碰撞过程、复合/自电离、CRM/谱、偏振、R 矩阵或底层诊断中的哪一类。
2. **检查前置产物**：确认二进制结构表、能量网格、温度密度点、靶态文件等是否已生成；二阶段工作流不可颠倒顺序。
3. **选择回归方式**：有官方基准时走 `make check`；无基准时走产物完整性、正值性、趋势与能量网格检查。
4. **估算资源**：按原型判断是否属于小时级、GB 级或多阶段任务；长任务单独调度，不混入每日检查。
5. **隔离执行**：在独立工作目录运行，独立日志、独立输出表；不要覆盖基准目录。
6. **验证输出**：检查表头、字段、单位、退出码和物理合理性；记录未测项，不推断耗时。

## 输入依赖规则

- 结构计算通常是后续过程的前置：先得到能级表，再做跃迁、碰撞、复合或 CRM。
- 磁子能级、偏振、R 矩阵等类型依赖更细的中间表；缺文件时先补前置步骤，不要先怀疑数值算法。
- 多电荷态谱任务要求各电荷态数据表覆盖完整；相邻电离态缺失会产生警告或影响谱线选择。
- 二阶段工作流的第一阶段输出是第二阶段的物理输入；把文件存在性、大小和文件头纳入检查。

## 回归方式判定

- `.en/.tr/.ce/.ceM/.ci/.rr/.ai/.sp/.rt/.ham` 等标准表且有基准：使用 `check.py` 分派比对。
- `pop.txt`、`pol.txt`、中间速率转储等文本或辅助产物：通常不在自动回归范围，转人工或物理合理性检查。
- 无官方基准：禁止声称自动回归通过；明确写“无基准，执行产物与物理合理性检查”。
- 比对失败先查文件尾部分派、表头、行序、容差和单位；完整契约见 `references/checkpy-contract.md`。

## 资源与安全分级

- 低资源：单原子、少组态、少能量点；可纳入快速冒烟。
- 中资源：多组态、多能量点、磁子能级或 CRM 迭代；使用独立日志。
- 高资源：多电荷态、多温度点、小时级或 GB 级输出；单独调度、记录墙钟与内部计时。
- 并行只走独立进程与独立输出目录；PFAC 非线程安全。

## 输出表判读

1. 先读文件头：版本、时间戳、`NBlocks`、`E0`、`NELE`、`NTRANS`、`TYPE`。
2. 再确认单位：ASCII 能量多为 eV，二进制内部多为 Hartree；截面与强度按表类型换算。
3. 最后看物理趋势：正值性、对称性、阈值、共振、布居归一与谱线强度口径。
4. 单位与列语义速查见 `references/table-units.md`。

## References

- `references/demo-archetypes.md`：十类通用原型、输入依赖、API 类型、输出表、资源级别与陷阱。
- `references/checkpy-contract.md`：`check.py` 分派、容差、行序、死键、无基准与耗时口径。
- `references/table-units.md`：能量、截面、强度、布居、偏振与谱表列语义。
