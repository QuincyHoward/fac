---
name: fac-readme-maintainer
description: Maintain the FAC README system bottom-up from source code and scripts. Use when the user asks to update, rebuild, audit, or synchronize README files, verify formulas against source code, add missing per-directory READMEs, or mark formulas whose implementation is not found in source.
---

# FAC README 体系维护

## Overview

以源码和脚本为事实源，自底向上维护 FAC 项目每个受管理目录的 `README.md`。先读底层实现与输出器，再更新目录文档，最后向上汇总到父目录与根 README。公式必须逐条核查；源码未找到实现或依据时，紧贴公式下方添加下划线注记。

## Maintenance Workflow

1. **生成目录清单**：列出当前受管理目录与已有 README，标记缺失项；新增 `scripts/`、`scenarios/`、`skills/` 后必须纳入清单。
2. **确定阅读顺序**：按 `references/bottom-up-order.md` 从数值支撑库读到根 README；同一目录内先脚本/源码，再旧 README。
3. **抽取事实**：记录目录职责、关键文件、函数/宏、输入输出、调用关系、输出表字段与单位。
4. **核查公式**：按 `references/formula-check-rules.md` 逐条确认源码依据；未命中时按规则加下划线注记。
5. **写入 README**：按 `references/readme-template.md` 输出中文文档；保持路径相对化，不写死外部机器路径。
6. **向上汇总**：子目录更新后，再更新父目录 README 的导航、职责摘要与状态说明；根目录最后更新。
7. **验证**：按 `references/validation-checklist.md` 检查目录覆盖、链接、围栏、公式注记与术语一致性。

## Formula Rule

- 完整公式、积分、求和与系数关系使用独立 LaTeX 展示块 `$$...$$`；简短变量可用 `$...$`。
- **源码已实现**：保留普通 LaTeX 公式，并给出函数、文件或输出器位置。
- **源码未溯源**：直接把公式写成 `\underline{$<formula>$}`，不另加说明性下划线或文字。
- 禁止 `<u>...</u>` 与 `\underline{\text{...}}` 形式的说明性注记。

证据优先级：源码实现/输出器 > 生成文件头与实测记录 > 项目 README > 历史注释。

## Safety

- 不把论文或旧 README 当最终证据；不要为了“看起来完整”伪造公式出处。
- 不修改源码、Makefile、`check.py`、构建脚本或运行产物。
- 不覆盖基准表；不把文档更新与数值回归混为一谈。
- 同一 README 写入串行；不同目录可并行读取和起草，但写入前必须确认无冲突。
- 所有路径使用相对路径或 `<WORK_ROOT>` 占位。

## Outputs

每次执行必须报告：

- 受管理目录清单与 README 缺口。
- 已更新 README 清单。
- 公式核查清单与源码证据。
- 下划线注记清单。
- 未解决项与需人工核查项。

## References

- `references/bottom-up-order.md`：完整阅读与更新顺序。
- `references/formula-check-rules.md`：公式核查与下划线注记规则。
- `references/readme-template.md`：统一 README 模板。
- `references/validation-checklist.md`：验证门禁。
