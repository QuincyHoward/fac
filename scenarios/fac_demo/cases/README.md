# fac_demo 原型场景

本目录按物理原型组织演示场景，每个子目录自包含 `README.md`、`scene.json` 与 `run.py`。

- 结构和辐射跃迁
- 碰撞激发/电离
- 光电离与辐射复合
- 自电离与双电子俘获
- CRM 与谱合成
- 偏振
- R 矩阵
- 底层诊断
- FeL 单节点满核大计算（HPC 验证场景）

场景身份由 `scene.json` 派生，目录可手动整理；整理后运行 `python ../../../scripts/06_scenarios/audit_scenarios.py` 验证。

父级 [`../README.md`](../README.md)。
