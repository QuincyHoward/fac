# CRM 与谱合成原型

演示从原子数据到稳态布居与谱表的通用流程。

- 输入：二进制 `.en/.tr/.ce`、温度与密度。
- 核心 API：`AddIon`、`SetBlocks`、`Set*Rates`、`LevelPopulation`、`SpecTable`、`RateTable`。
- 输出：`.sp`、`.rt`、`.r*`。
- 验证：布居归一、速率正值、谱表 `TYPE` 与强度口径。
- 注意：`TYPE≠0` 的 `strength` 为 photons/s，不含 $h\nu$；`read_sp()` 键名存在历史误命名。

文件：`run.py` 一键入口；`explain.py` 输出表头部解读；`plot.py` 双列谱图演示。

导航：[`../../README.md`](../../README.md)。
