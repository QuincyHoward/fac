# 偏振原型

演示磁子能级布居、取向和谱线偏振的通用流程。

- 输入：结构表、多极跃迁、磁子能级碰撞强度。
- 核心 API：`TransitionTable(m=...)`、`CETableMSub`、`SetEnergy`、`Orientation`、`PolarizationTable`。
- 输出：三类表回归结果，以及 `pop.txt`、`pol.txt` 文本输出。
- 验证：表回归 + 文本人工检查。
- 注意：`a/b` 是球张量比，不是初等偏振度字面式；注释能量可能与代码值不一致。

导航：[`../../README.md`](../../README.md)。
