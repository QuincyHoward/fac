# FAC 夜间示例复现 — 执行记忆

## 2026-11-25 02:00（首次记录，此前无本文件）
- 结果：两个长耗时示例均跑到结束并成功。`night_status.txt` 记录 `CS_EXIT=0`、`FE_EXIT=0`、`SPEC_EXIT=0`，窗口 02:00:58–04:40:40（+08:00），总墙钟 2 h 39 min 42 s。
- 产物：`rmatrix/r1.d` 约 886 MiB；`FeL/data/` 36 个 Fe08/09/10 表；`FeL/Fe08/` 210 个速率/谱文件。复用已有 `rmx.b*`/`rmx.d*`，未重跑 `rmx.py`。
- 文档：仅更新根 `README.md`、`demo/README.md`、`demo/rmatrix/README.md`、`demo/FeL/README.md` 的执行状态；未改原树源码，未新增核查报告。
- 验证：38 份 README、0 问题；英文原文附录与 HEAD 逐字一致；476 个已跟踪原树源文件全部只读且 `git diff --name-only` 仅 `README.md`。
- 注意：`spec.py` 有 16 条 `Fe07b.en` 缺失的非致命警告且只生成 `Fe08/`（脚本 `neles=range(8,9)`）；后续若需 Fe09/Fe10 谱需修改运行副本范围。
