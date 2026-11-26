# 原子结构与辐射跃迁原型

演示从组态定义到能级表与跃迁表的通用流程。

- 输入：元素、闭壳层、组态组、中心势初值。
- 核心 API：`Config`、`OptimizeRadial`、`Structure`、`TransitionTable`。
- 输出：`.en`、`.tr`、`.pot` 与二进制表。
- 验证：`check_en`、`check_tr`；先查 `E0`/`NBlocks`，再查行序与容差。
- 注意：ASCII 能量为 eV、二进制内部为 Hartree；不要重复换算。

导航：[`../../README.md`](../../README.md)。
