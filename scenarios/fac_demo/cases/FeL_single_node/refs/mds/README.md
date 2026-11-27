# 参考文献 Markdown 索引

本目录由 `../convert_refs.py` 从 `../pdfs/` 自动生成。PDF 只重命名，不修改内容；Markdown 为逐页文本抽取结果，保留 `## Page N` 分页标记。

## 转换口径

- 转换工具：Python 3.14 + PyMuPDF 2.1（MuPDF 1.28.6）。
- 编码：UTF-8。
- 长路径：Windows 最长目标文件名超过 `MAX_PATH`，脚本使用 `\\?\` 长路径前缀。
- 图件与公式：仅抽取文本层；公式、图线和表格图像未做 OCR，需回看同名 PDF。

## 重命名映射

规则：`{第一作者}{年份}{a/b/c}_{文献标题}.pdf`。当前 6 篇第一作者/年份均不重复，故全部用 `a`。

| 原文件名 | 现文件名 | 页数 |
|---|---|---:|
| `2308.14880.pdf` | `Zhao2024a_R-Matrix calculations for opacities IV Convergence completeness and comparison of relativistic R-matrix and distorted wave calculations for Fe XVII and Fe XVIII.pdf` | 15 |
| `2607.21238.pdf` | `Zhou2026a_Plasma screening and configuration interaction effects induced large enhancement on L-shell photoionization cross sections and opacity.pdf` | 9 |
| `a-higher-than-predicted-measurement-of-iron-opacity-at-solar-4vx7wp39j8.pdf` | `Bailey2015a_A higher-than-predicted measurement of iron opacity at solar interior temperatures.pdf` | 12 |
| `jin2009.pdf` | `Jin2009a_Radiative opacity of iron studied using a detailed level accounting model.pdf` | 13 |
| `PhysRevLett.122.235001-accepted.pdf` | `Nagayama2019a_Systematic study of L-shell opacity at stellar interior temperatures.pdf` | 9 |
| `zhang2012.pdf` | `Zhang2012a_L- and M-shell absorption measurements of radiatively heated Fe plasma.pdf` | 7 |

## 文件清单

- `Bailey2015a_A higher-than-predicted measurement of iron opacity at solar interior temperatures.md`
- `Jin2009a_Radiative opacity of iron studied using a detailed level accounting model.md`
- `Nagayama2019a_Systematic study of L-shell opacity at stellar interior temperatures.md`
- `Zhang2012a_L- and M-shell absorption measurements of radiatively heated Fe plasma.md`
- `Zhao2024a_R-Matrix calculations for opacities IV Convergence completeness and comparison of relativistic R-matrix and distorted wave calculations for Fe XVII and Fe XVIII.md`
- `Zhou2026a_Plasma screening and configuration interaction effects induced large enhancement on L-shell photoionization cross sections and opacity.md`
- [`reading_notes.md`](reading_notes.md)：逐篇通读笔记与对本示例的可用性判断。
