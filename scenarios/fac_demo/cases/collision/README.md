# 碰撞过程原型

演示碰撞激发与电离的通用流程，包括磁子能级扩展。

- 输入：结构表、初末能级、能量网格。
- 核心 API：`CETable`、`CETableMSub`、`SetUsrCIEGrid`、`CITable`。
- 输出：`.ce`、`.ceM`、`.ci`。
- 验证：碰撞强度与截面正值性、能量网格一致性、行序重排。
- 注意：CE 截面含 π，EII 截面不含 π；`ratio collision strength` 可能受死键影响。

导航：[`../../README.md`](../../README.md)。
