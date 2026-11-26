---
name: fac-demo-readme-execution-update
overview: 基于已完成的 10 个 FAC demo 真实执行结果，就地更新 `demo/` 下全部 19 份 README.md：建立统一执行记录口径、修正过时/矛盾表述、补齐 ref 验证状态，不新增文档、不改源码与执行产物。
todos:
  - id: verify-readme-facts
    content: 使用 [subagent:code-explorer] 复核执行事实与README缺口
    status: completed
  - id: update-overview
    content: 更新 demo/README.md 总览执行索引与状态口径
    status: completed
    dependencies:
      - verify-readme-facts
  - id: normalize-daily-readmes
    content: 统一八个日常示例 README 执行记录模板
    status: completed
    dependencies:
      - verify-readme-facts
  - id: fix-long-readmes
    content: 修正 FeL 与 rmatrix 执行记录和路径说明
    status: completed
    dependencies:
      - verify-readme-facts
  - id: update-ref-readmes
    content: 补充八份 ref/README.md 验证状态说明
    status: completed
    dependencies:
      - verify-readme-facts
  - id: validate-readme-system
    content: 并行校验链接、章节一致性与事实准确性
    status: completed
    dependencies:
      - update-overview
      - normalize-daily-readmes
      - fix-long-readmes
      - update-ref-readmes
---

## 用户需求

- 当前 FAC 的全部 demo 示例已经真实执行完毕。
- 请详细更新 `demo/` 下的 README.md 体系，把执行状态、执行证据、比对结果、产物清单和已知限制系统地写回文档。
- 更新应覆盖 `demo/README.md`、10 个示例 README 和 8 份 `ref/README.md`，但不新增独立核查报告，不改源码与执行产物。

## 产品概述

形成一套与实测结果一致、可复现、可追溯的中文 README 文档体系。总览负责统一事实口径，示例 README 负责完整执行记录，ref README 负责标明参考表验证状态。

## 核心功能

- 建立 10 个 demo 的统一执行索引，区分每日测试示例与 FeL、rmatrix 长耗时示例。
- 将 8 个日常示例的 22 项 `check.py` 通过结果写入对应 README。
- 补充 FeL 与 rmatrix 的夜间执行时间、退出码、线程数、产物规模和非致命限制。
- 修正过时表述：旧 JSON 中的 SIGSEGV 与未运行状态不再作为当前结论。
- 统一 19 份 README 的执行记录模板、基准版本口径、路径写法和验证状态说明。

## 技术栈选择

- 文档格式：Markdown，沿用现有中文 README、表格、代码围栏和 Mermaid 图。
- 事实来源：现有 `temp_test/logs/`、`temp_test/runs/`、`temp_test/scripts/` 与 `demo/check.py`。
- 修改范围：仅 `demo/` 下 19 份 README.md；不新增文档，不改源码、Makefile、check.py、日志、runs 产物或 `temp_test/fac_src/demo/` 快照。

## 实施方法

采用“事实复核到总览口径统一到示例定点更新到 ref 状态补充到一致性校验”的流程。

关键决策：

- `demo/README.md` 作为唯一总入口，新增 10 例执行结果总表，集中呈现命令、退出码、检查数、输出和证据路径。
- 8 个日常示例仅补充统一执行章节；“耗时未记录”必须显式写明，避免编造。
- FeL 与 rmatrix 没有官方 `ref/`，只能写产物完整性与物理合理性检查，不能写自动回归通过。
- `wsl_reproduction_summary.json` 仅作为 8 个日常示例 22 项检查依据；其 rmatrix/FeL 旧状态作为历史过时信息说明。
- 保留全部物理公式、Mermaid 图、API 调用链、表字段和容差说明，只修正与执行状态相关的矛盾。

性能与可靠性：

- 读取不同 README、日志和产物清单可并行；写入同一 README 必须串行。
- 复杂度近似为 O(19 个文档加 N 份日志)，主要成本在口径一致性，不涉及计算瓶颈。

## 实施注意事项

- 8 个日常示例来源：`temp_test/runs/standalone/wsl_reproduction_summary.json` 第 28 到 38 行，`total_checks_passed` 为 22。
- 夜间执行来源：`temp_test/logs/night_status.txt`，开始时间为 `2026-11-25T02:00:58+08:00`，结束时间为 `2026-11-25T04:40:40+08:00`，`CS_EXIT`、`FE_EXIT`、`SPEC_EXIT` 均为 0。
- rmatrix 应写明 16 线程、复用 `rmx.b*` 与 `rmx.d*`、`r1.d` 约 886 MiB，以及先前 SIGSEGV 的根因是缺少前置产物。
- FeL 应写明 8 线程、顺序执行 `fe.py` 和 `spec.py`、产物规模，以及 `Fe07b.en` 警告非致命。
- 修正 `demo/FeL/README.md` 中不存在的 `ref/Fe08a.en` 比对命令和 `make check` 表述。
- 统一 FAC 基准版本措辞：文档原基准称 FAC 1.1.4，实际参考表文件头多为 FAC 1.1.5。
- `check.py` 死键与 `pol.py` 注释矛盾只保留为已知限制，不在本次修改代码。
- 路径改为仓库相对路径或清晰占位说明，避免混用 Windows 绝对路径与 WSL 路径。
- 不同步 `temp_test/fac_src/demo/` 下 19 份 README 快照，避免正式文档再次分叉。

## 架构设计

文档事实链为：执行日志与 JSON 汇总形成事实源，`demo/README.md` 形成总览索引，各示例 README 形成详细说明，各 `ref/README.md` 形成验证状态补充，最终通过链接、章节和数值事实校验闭环。

## 目录结构

本次修改范围如下，所有文件均为就地更新，不新增文件。

```text
demo/README.md
  # [MODIFY] 总览：新增 10 例执行状态总表、日常 22 项检查口径、夜间执行结论、过时 JSON 说明和 FeL/rmatrix 例外说明

demo/structure/README.md
  # [MODIFY] 统一执行记录章节；补充日志来源、退出码、比对项与耗时未记录说明

demo/excitation/README.md
  # [MODIFY] 统一执行记录章节；保留 check.py 死键限制并补充实测比对结论

demo/pirr/README.md
  # [MODIFY] 统一执行记录章节；标注 2 项检查通过、退出码与耗时未记录

demo/aidr/README.md
  # [MODIFY] 统一执行记录章节；明确 SIGSEGV 旧状态不适用本例并保留 Se 记号更正

demo/ionization/README.md
  # [MODIFY] 统一执行记录章节；补充 2 项检查、日志路径与耗时未记录说明

demo/polariz/README.md
  # [MODIFY] 统一执行记录章节；保留能量注释矛盾为已知限制

demo/NeL/README.md
  # [MODIFY] 统一手动复现章节；补充 6 项检查通过、日志来源和耗时口径说明

demo/tests/README.md
  # [MODIFY] 统一执行记录章节；补充 RUN 与 CHECK 退出码及 2 项检查通过结论

demo/FeL/README.md
  # [MODIFY] 修正无 ref 的比对命令和 make check 表述；补充夜间执行、产物规模、警告解释和可移植路径

demo/rmatrix/README.md
  # [MODIFY] 补充 16 线程、前置产物、r1.d 产物、夜间退出码和路径写法修正

demo/aidr/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 2 项检查通过，保留字段、单位和容差说明

demo/excitation/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 3 项检查通过，保留死键限制说明

demo/ionization/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 2 项检查通过，保留表格说明

demo/NeL/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 6 项检查通过，保留 FAC 版本口径说明

demo/pirr/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 2 项检查通过，保留字段说明

demo/polariz/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 3 项检查通过，保留偏振数据说明

demo/structure/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 2 项检查通过，保留能级与跃迁表说明

demo/tests/ref/README.md
  # [MODIFY] 追加验证状态：父 README 中 2 项检查通过，保留诊断数据说明
```

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 复核 19 份 README、执行日志、状态 JSON 和各示例流程之间的事实一致性。
- Expected outcome: 提供逐文件缺口清单、权威执行事实来源路径和需修正的矛盾表述。