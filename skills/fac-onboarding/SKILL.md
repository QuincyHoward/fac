---
name: fac-onboarding
description: First-time FAC setup, clean rebuild, parallel rebuild planning, PFAC import verification, and first-run smoke checks. Use when the user asks how to start FAC, rebuild it, build PFAC in parallel, fix import errors, or verify a fresh build.
---

# FAC 上手与并行构建

## Overview

提供 FAC 从零上手、重新构建和首次冒烟检查的可复现流程。把原始源码树当作只读事实源，把构建与运行放在独立可写工作目录 `<WORK_ROOT>` 中；区分必须串行的前置步骤与可并行的编译/检查任务。

## Workflow Decision Tree

- 首次接触 FAC 或需要给出上手路线：执行“首次上手路径”。
- 已有构建但需要重建、清理后重编、或要求并行构建：执行“并行重建路径”。
- `from pfac import ...` 失败或找不到扩展模块：先执行“导入与路径检查”，再按需回到构建路径。
- 构建成功但不确定是否正确：执行“首次冒烟检查”。

## 首次上手路径

1. 确认工具链：Linux/WSL、`gcc`、`gfortran`、`make`、与扩展模块匹配的 Python 版本。Windows 宿主缺少这些工具时，优先使用 WSL；不要用 Windows Python 加载 Linux 编译的 `.so`。
2. 在 `<WORK_ROOT>` 准备独立可写工作目录，不修改原始源码树。
3. 按固定顺序完成前置步骤：归一化 shell 脚本行尾 → 运行 `configure` → 按需修正 `sysdef.h` 的 C/Fortran ABI 开关 → 阅读生成的 Makefile。
4. 构建 C 核心库、SFAC 命令和 PFAC 扩展；保留分阶段日志。
5. 设置 `PYTHONPATH` 指向构建产物与 Python 包目录，导入 `pfac.fac/crm/pol/util` 冒烟。
6. 在 `demo/` 执行 `make check`，确认基础回归通过。
7. 详细命令、configure 选项与环境矩阵见 `references/build-matrix.md`。

## 并行重建路径

1. 先判断是否真的需要全量重建；仅 Python 脚本变更不必重编 C/Fortran。
2. 串行完成所有全局前置：行尾归一化、`configure`、`sysdef.h` 补丁、生成配置文件。
3. 在独立目录、独立日志、独立输出路径下并行执行互不依赖的编译单元与冒烟检查。
4. 不要并发写同一 Makefile、同一基准目录、同一构建缓存或同一输出表；不要并发修改同一文件。
5. PFAC 非线程安全：并行必须是进程级，不能是 Python 多线程共享同一 PFAC 实例。
6. 收集每个并行任务的退出码和日志；任一失败时保留现场，先修复根因再继续。
7. 完整阶段划分、失败保留策略和汇总格式见 `references/parallel-rebuild.md`。

## 导入与路径检查

1. 确认 Python 版本与编译扩展时使用的一致。
2. 确认 `PYTHONPATH` 同时包含构建产物目录和 `python/` 源码目录。
3. 用最小导入检查四个模块：`pfac.fac`、`pfac.crm`、`pfac.pol`、`pfac.util`。
4. 若报符号未定义或导入崩溃，先查 ABI 开关，再查编译器混编选项；不要先改物理代码。
5. 若只在某个 shell 中失败，查环境变量作用域与绝对路径拼写。

## 首次冒烟检查

1. 导入四个 PFAC 模块并检查版本常量可读。
2. 在 `demo/` 中选择一个低资源、带基准的算例执行 `make check`。
3. 检查表头字段、退出码与 `Tests passed!` 输出；不要只看 stdout 是否为空。
4. 记录环境、Python 版本、构建选项和检查项；未记录的耗时写“未记录”。
5. 完整清单见 `references/first-run-checklist.md`。

## Safety

- 不要把基准表更新当作构建验证手段；`make ref` 只在物理结果确认正确后使用。
- 不要为了提高通过率而放宽容差或改物理参数。
- 不要在原始源码树中直接执行会改动文件的兼容补丁；补丁只作用于 `<WORK_ROOT>`。
- 构建产物隔离后，再判断结果差异来自环境还是物理实现。
