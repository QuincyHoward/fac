# 底层诊断原型

演示哈密顿量、速率与简单 CRM 的底层诊断流程。

- 输入：组态、CI 开关、截面表、简单 CRM 参数。
- 核心 API：`SetCILevel`、`Structure`、`MaxwellRate`、CRM 基础调用。
- 输出：`.en`、`.cir/.cer`、`.sp` 与部分中间产物。
- 验证：有基准项走 `check_en/check_sp`；无基准产物只做合理性与量级检查。
- 注意：关闭 CI 时多条能量为 0 是预期；不要误把中间产物加入 `RESULTS`。

导航：[`../../README.md`](../../README.md)。
