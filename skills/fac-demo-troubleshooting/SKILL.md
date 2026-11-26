---
name: fac-demo-troubleshooting
description: Structured diagnosis and resolution playbooks for FAC demo failures, including build errors, import errors, missing prerequisites, crashes, check.py mismatches, no-baseline cases, long runs, and unit or column misinterpretation. Use when the user reports a demo failing or asks how to troubleshoot FAC runs.
---

# FAC Demo 排障

## Overview

提供固定的排障顺序：分类 → 复现 → 隔离 → 定位 → 修复 → 验证。先排除环境、路径、输入依赖和比对机制问题，再怀疑物理实现；禁止通过改基准、放宽容差或改物理参数来“修好”失败。

## Fixed Workflow

1. **分类**：判断失败属于构建、导入、运行、崩溃、比对、无基准、长耗时还是单位/列语义问题。
2. **复现**：用最小命令复现，记录命令、环境、退出码和完整日志；不要只截最后一屏。
3. **隔离**：把输出放到独立目录，确认没有覆盖基准或污染共享产物；保留失败现场。
4. **定位**：按问题类型读取对应 playbook，先查最常见环境原因，再查源码与物理实现。
5. **修复**：只修改被证实的原因；所有副本补丁都要说明是否影响物理，并给出验证方式。
6. **验证**：重跑失败步骤 + 相关回归 + 产物检查；确认没有引入新的差异。

## 快速分诊

| 症状 | 首要怀疑 | 第一步 |
|---|---|---|
| `/bin/sh^M: bad interpreter` | 行尾格式 | 归一化 shell 脚本后重跑 configure |
| Fortran 符号未定义 / LOGICAL 异常 | C/Fortran ABI | 检查 `f2cFortran` 与 configure 选项 |
| `ModuleNotFoundError` / 找不到扩展 | `PYTHONPATH` 或 Python 版本 | 指向实际构建产物并最小导入 |
| 二阶段脚本崩溃 | 缺前置产物 | 检查第一阶段文件存在性与大小 |
| `make openmp` 无效 | 脚本未解析参数 | 查脚本参数分支和 `InitializeMPI` 调用 |
| 比对失败但数值接近 | 行序、容差、死键、单位 | 先查 `check.py` 契约，不改基准 |
| `TypeError: Unknown file extension` | 文件名被改或扩展名不匹配 | 恢复原始结果名 |
| 长任务无输出 | 资源或阶段未完成 | 查退出码、日志、产物大小、阶段计时 |
| 无 `ref/` | 不适用自动回归 | 改做产物与物理合理性检查 |

## 安全边界

- 不在原始源码树直接修补；只在独立可写工作目录验证。
- 不把“比对通过”等同于物理正确；死键或弱线容差可能让通过意义有限。
- 不凭输出头部版本差异判断结果错误；`check.py` 通常忽略版本与时间戳。
- 不把 Python 多线程当成 PFAC 并行方案；并行必须进程级且输出隔离。
- 不删除失败现场；定位完成前保留日志、部分产物和生成文件。

## References

- `references/error-patterns.md`：症状 → 原因 → 处理 → 验证的完整错误模式库。
- `references/diagnostic-playbooks.md`：按场景展开的分步诊断剧本。
- `references/known-limitations.md`：已知限制与“通过但需注意”的情况。
