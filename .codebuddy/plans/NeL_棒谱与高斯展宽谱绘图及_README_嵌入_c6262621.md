---
name: NeL 棒谱与高斯展宽谱绘图及 README 嵌入
overview: 为 demo/NeL 新增一个不依赖 PFAC 的独立绘图脚本，从 ref/Ne03a.sp 生成棒谱与高斯展宽谱 PNG 图片，并将图片与运行说明嵌入 README §10.5。
todos:
  - id: create-plot-script
    content: 新增 demo/NeL/plot_spec.py，独立解析 SP 表并绘制棒谱与高斯展宽谱
    status: completed
  - id: generate-spectra
    content: 运行脚本生成 NeL_stick.png 与 NeL_gauss.png 并检查图像内容
    status: completed
    dependencies:
      - create-plot-script
  - id: embed-readme
    content: 更新 README §10.5，嵌入两张谱图与运行说明
    status: completed
    dependencies:
      - generate-spectra
  - id: verify-artifacts
    content: 核查图片路径、README 代码块闭合与物理口径说明
    status: completed
    dependencies:
      - embed-readme
---

## 产品概述

为 `demo/NeL —— Ne VIII 碰撞辐射模型与谱合成` 生成两张可复现的谱图：棒谱与高斯展宽谱，并将图片、说明与运行方法嵌入该 README，使读者能直观看到 `Ne03a.sp` 中的线光度分布与展宽后的连续谱效果。

## 核心功能

- 从 `Ne03a.sp` 提取线发射块，跳过布居块，得到每条谱线的光子能量与线光度。
- 绘制棒谱：突出 Ne VIII 主要强线，坐标轴明确标注波长与 photons/s，便于线识别。
- 绘制高斯展宽谱：在强线波段用高斯仪器展宽展示连续谱形态，并注明展宽参数与物理口径。
- 将两张图保存到 `demo/NeL/`，在 README 中用相对路径嵌入，并给出运行命令、图注和单位说明。
- 保证绘图流程不依赖 PFAC 扩展，可在当前 Windows 环境直接运行。

## 技术栈与选型

- 语言与库：Python 3，标准库 `argparse` / `pathlib`，`numpy`，`matplotlib`。
- 数据源：`demo/NeL/ref/Ne03a.sp`；该文件是稳定参考表，不依赖重新运行 `ne.py` / `spec.py`。
- 图像输出：PNG 文件，保存在 `demo/NeL/`，供 README 相对路径引用。
- 不使用 `rfac.read_sp()`：`python/rfac.py` 依赖 `pfac.fac` / `pfac.const` / `pfac.util`，当前 Windows 宿主未构建 PFAC，不能直接运行；独立解析器更符合“手动可复现”的目标。

## 实现方案

新增一个独立绘图脚本，直接解析 SP 文本表。解析逻辑按块读取：识别 `TYPE` 块头，`TYPE=0000000` 为布居块跳过；其他块读取每个数据行的第 3、4 列，即 `energy`（eV）与 `strength`（photons/s）。波长换算采用 `λ[Å] = 12398.4198 / E[eV]`。

棒谱图采用分面设计：主面板显示 60–1000 Å  EUV/XUV 强线区，因强度跨十几个数量级，纵轴使用对数坐标；辅助面板放大 760–780 Å 的 2p→2s 双线区，并在图中标注最强两条线（约 765.95 Å、775.56 Å）。这样既避免 10⁶ Å 极弱长波线压垮视觉，又能展示最显著的物理谱线。

高斯展宽谱采用波段化卷积：默认聚焦 760–780 Å 双线区，可选 60–200 Å EUV 波段；在用户指定波长网格上逐线累加高斯核，输出单位为 photons/s/Å。脚本打印线数、波长范围、输出文件路径等简要信息；不记录敏感信息。

## 性能与可靠性

- SP 表解析复杂度为 `O(N)`，N 为文本行数；本例约数百行，开销可忽略。
- 卷积复杂度为 `O(M·G)`，M 为选定波段内的线数，G 为波长网格点数；通过限制波段和网格分辨率避免跨越 60–10⁶ Å 的超大网格。
- 脚本对空线表、无有效 `TYPE≠0` 线、指定波段无线等情况给出明确错误或警告而非崩溃。
- 图像标签使用英文，避免 Windows 下中文字体缺失导致乱码；中文解释放在 README 正文。

## 架构设计

保持简单单文件结构：一个脚本负责解析、绘图、保存；README 负责展示图片和解释。脚本默认从自身目录下的 `ref/Ne03a.sp` 读取数据，也支持命令行传入其他 `.sp` 文件与输出目录，便于后续复用于运行目录中的 `Ne03a.sp`。

## 目录结构

```
R/
└── demo/
    └── NeL/
        ├── plot_spec.py        # [NEW] 独立绘图脚本。解析 SP 文本表，跳过布居块，生成棒谱与高斯展宽谱 PNG；仅依赖 numpy/matplotlib/标准库；支持命令行输入路径、波段、σ、输出目录。
        ├── NeL_stick.png       # [NEW] 棒谱图。由 plot_spec.py 从 ref/Ne03a.sp 生成；展示 60–1000 Å 主强线区与 760–780 Å 放大区。
        ├── NeL_gauss.png       # [NEW] 高斯展宽谱图。由 plot_spec.py 生成；展示双线区或 EUV 波段的高斯仪器展宽示意。
        └── README.md           # [MODIFY] 更新 §10.5：加入推荐运行方式、两张图片的 Markdown 嵌入、图注、运行命令、物理口径提醒；保留原 rfac 版本作为已构建 PFAC 环境下的参考。
```

## 实施注意事项

- 不修改 `ne.py`、`spec.py`、`ref/Ne03a.sp` 或其他示例文档，避免扩大影响面。
- README 图片路径使用 `![...](NeL_stick.png)`、`![...](NeL_gauss.png)`，与图片同目录。
- 图注明确：纵轴为 photons/s 或 photons/s/Å，是光子数口径；能量发射率需另乘 `hν`。
- 高斯图明确标注为仪器展宽示意，不等同于真实 Voigt 线型；本例 `wimp`/`wstk` 为 0。
- 完成后实际运行脚本生成 PNG，并用图片查看或文件存在性检查确认输出有效。