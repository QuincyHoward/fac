---
name: fac-code-navigation
description: FAC project overview, module map, feature-to-source lookup, API call-chain tracing, and PFAC/SFAC interface mapping. Use when the user asks what FAC does, where a physics feature is implemented, which function to call, or how to locate source code for an output table.
---

# FAC 概述与源码导航

## Overview

把用户的物理功能或输出表问题映射到 FAC 源码位置。先按模块地图缩小范围，再按功能到源码表和 API 调用链定位实现；优先用语义导航，必要时退回文本检索。

## Navigation Workflow

1. **判断问题类型**：目录职责、物理功能、API 名称、输出表字段或调用顺序。
2. **先查模块地图**：用 `references/module-map.md` 确定最可能的目录，避免全仓库扫描。
3. **再查功能映射**：用 `references/feature-to-source.md` 把物理过程映射到 C 文件、Fortran 文件或 Python/SFAC 接口。
4. **追调用链**：用 `references/api-call-map.md` 判断前端命令如何落到核心函数；同时核对 PFAC 与 SFAC 两套入口。
5. **语义定位**：对有名符号优先 `workspaceSymbol` / `goToDefinition` / `findReferences`；C/Fortran 项目若 LSP 无索引，立即退回定向文本检索。
6. **验证映射**：至少给出文件路径、符号名或输出表字段之一；不确定处标注“需源码核对”。

## 模块快速图

- `faclib/`：核心物理与数据表实现，绝大多数原子过程入口在此。
- `python/`：PFAC 扩展绑定、`rfac.py`、`atom.py`、`spm.py`。
- `sfac/`：SFAC 命令解析与 `sfac`/`scrm`/`spol` 前端。
- `coul/`：库仑函数、连续态、特殊函数。
- `modqed/`：QED 势与修正。
- `ionis/`：电离平衡与拟合。
- `mpfun/`、`ode/`、`quadpack/`、`blas/`、`lapack/`、`minpack/`、`toms/`：数值支撑。
- `doc/`：手册、论文、输出表格式与理论出处。

## 功能查找策略

- 用户给物理名词：先映射到 `faclib/` 的功能文件，再查接口绑定。
- 用户给 API 名：先找前端绑定，再追核心函数；注意 Python 暴露名和 C 函数名可能不同。
- 用户给输出表类型：先找读取器与打印器，例如 `dbase.c` 的 `Print*Table`，再反查生成该表的物理函数。
- 用户给错误消息：按字面文本检索日志/源码；不要把它当符号名处理。
- 用户给目录职责：先读该目录 README，再查源码。

## API 调用链原则

- PFAC 典型链路：Python 命令 → `python/*.c` 绑定 → `faclib/*.c` 核心 → 二进制表 → `rfac.read_*`。
- SFAC 典型链路：脚本命令 → `sfac/*.c` 解析 → `faclib/*.c` 核心 → 输出表。
- 同一物理过程在 PFAC 与 SFAC 中常共享核心实现，只是前端语法不同。
- `Structure`、`TransitionTable`、`CETable`、`RRTable`、`CITable`、`AITable`、`LevelPopulation`、`SpecTable`、`RMatrixCE` 等是跨入口常见抽象名；具体定义位置见 references。

## References

- `references/module-map.md`：目录职责与源码入口。
- `references/feature-to-source.md`：物理功能到源码文件/符号映射。
- `references/api-call-map.md`：PFAC/SFAC 调用链与定位方法。
