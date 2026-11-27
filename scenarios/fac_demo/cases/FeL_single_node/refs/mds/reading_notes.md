# 参考文献通读笔记

本文件记录对 `mds/` 中 6 篇文献 Markdown 的通读结果，供 `scenarios/fac_demo/cases/FeL_single_node/opacity/docs/literature_comparison.md` 使用。所有结论来自本地 PDF 文本抽取；公式和曲线未做 OCR，涉及具体数值时以 PDF 图件为准。

## 1. Bailey et al. 2015 — *A higher-than-predicted measurement of iron opacity at solar interior temperatures*

- **条件**：Sandia Z-pinch，Fe/Mg 样品；`Te = 1.91e6 / 1.97e6 / 2.11e6 / 2.26e6 K`，对应 `ne ≈ 7e21 / 2e22 / 3.1e22 / 4e22 cm^-3`；接近太阳辐射/对流区边界。
- **能区**：Fe L-shell 主要贡献在 `6–16 Å`；文中强调 `7–13 Å` 的实测波长依赖不透明度比模型高 `30–400%`。
- **方法**：测透过率 `T`，用 `-ln(T)/面密度` 得到不透明度；对比 SCRAM、OPAL、OP、ATOMIC、OPAS、SCO-RCG 等模型。
- **关键结论**：随 `Te/ne` 升高，谱线特征相对准连续体收缩、窗口被填充、谱线变宽；模型在最低 `Te/ne` 符合较好，向 BCZ 条件靠近时偏差增大。短波准连续体被低估约 `30–45%`。系统误差（非 LTE、背景、样品、梯度、tamper）被评估为不足以解释偏差。
- **数据可用性**：正文中为图件，无机器可读透过率表；约 450 条谱、22 次实验用于建立重复性。
- **对本示例**：提供 Fe-L 谱形与实验背景；本示例是 0D 光薄 CRM，不能逐点比对，只作谱段和“模型可能低估准连续体”的定性依据。

## 2. Jin et al. 2009 — *Radiative Opacity of Iron Studied Using a Detailed Level Accounting Model*

- **条件**：LTE 铁等离子体；对比 Bailey 2007 的 `T=150 eV`、`ne=8.5e21 cm^-3`；另有 `T=20 eV`、`T=19.3 eV` 等温序列；系统范围 `T=10–1000 eV`、`rho=1e-5–1e-1 g/cm^3`。
- **能区**：Bailey 2007 对比中 `800–980 eV` 为 L→M，`990–1320 eV` 为 L→N/O；另有 `721–756 eV` 的 2p→3d 实验。
- **方法**：DLA（line-by-line），相对论 Dirac–Fock，组态内态混合；含 b–b、b–f、f–f、Thomson 散射；Voigt 线型（Stark + Doppler）；Saha-Boltzmann 布居与 Stewart–Pyatt IPD。
- **关键结论**：DLA 与实验整体吻合较好；未考虑内壳层轨道弛豫时 2p→3d 能量系统性偏高约 `6.5 eV`；低密度下 AA 高估 Rosseland 平均不透明度；高密度下 DLA 与 OP 差异明显。
- **数据可用性**：Figure 1–14 为图；Table 1–4 为能级/布居/ne 表，可下载 ASCII；无公开逐点透射谱 CSV。
- **对本示例**：最适合用于“吸收带位置/谱形”人工对照；也提示 FAC 类计算需关注 CI 与轨道弛豫，不能把谱线位置偏差直接当作程序错误。

## 3. Zhang et al. 2012 — *L- and M-shell absorption measurements of radiatively heated Fe plasma*

- **条件**：SGII 激光装置，辐射加热 Fe 等离子体；`T = 72 ± 4 eV`；密度未直接诊断，由 Multi-1D 辐射流体模拟给出。
- **能区**：`150–1200 eV`，同时覆盖 Fe L-shell 和 M-shell 跃迁；平场光栅谱仪 + 时间选通 MCP。
- **方法**：用掺 Al 的 Fe 样品吸收谱诊断电子温度；DCA 不透明度模型计算透过率并与实验比较。
- **关键结论**：宽能区透射谱与 DCA 总体符合较好；高能端谱仪分辨率不足导致 L-shell 结构不明显；样品均匀性、高阶衍射、MCP 非均匀、面密度不确定等仍需改进。
- **数据可用性**：OSTI/AIP 页面无原始数据下载。
- **对本示例**：给出宽能区 L+M 吸收形态参考；本示例仅 Fe XVII–XIX 的 L 壳层且无完整电离平衡，不能逐点比对。

## 4. Zhao, Nahar & Pradhan 2024 — *R-Matrix calculations for opacities IV: Fe XVII and Fe XVIII*

- **条件**：BCZ 背景 `T = 2.1e6 K`、`ne ≈ 3.1e22 cm^-3`；Fe XVII/XVIII/XIX 分数约 `0.19 / 0.38 / 0.29`。
- **方法**：218CC / 276CC Breit-Pauli R-matrix（BPRM）与相对论扭曲波（RDW，使用 FAC）比较并 top-up；按 `J, pi, energy, cross section` 匹配 BPRM 与 RDW 能级。
- **能区**：背景 PI 截面比较一致；高能截面延伸至约 `500 Ry` 光电子能量。
- **关键结论**：BPRM 与 RDW 的背景 PI 截面吻合良好；different-n CI 对正确再现背景截面重要；RDW 无法覆盖 BPRM 的密集共振结构，但可检验完备性与收敛性；新增高 nℓ 能级按 MHD EOS 布居极小，Rosseland 平均不透明度提升仅 `<5%`。
- **数据可用性**：Table 1/2 给出能级能量；截面比较仅为图，无 CSV。
- **对本示例**：为“FAC 扭曲波 PI 作为不透明度输入”提供方法学合理性；本示例的 bound-free 通道和能级映射可借用其 BPRM/RDW 匹配思想。

## 5. Nagayama et al. 2019 — *Systematic Study of L-Shell Opacity at Stellar Interior Temperatures*

- **条件**：Sandia Z-pinch；Cr、Fe、Ni 在 `>180 eV`；Fe 系列 `Te = 155–195 eV`、`ne = (7–40)e21 cm^-3`。
- **能区**：短波准连续体在 `<9 Å`；文中对比 BCZ 附近 `Te ≈ 182 eV`、`ne ≈ 9e22 cm^-3`。
- **方法**：同一实验方法跨 Z 系统测量；对比多种模型（SCO-RCG、OP、ATOMIC 等）。
- **关键结论**：Cr/Ni 的模型-实验差异小于 Fe；只有 Fe 在 `>180 eV` 出现 `30–45%` 的短波准连续体低估；模型普遍把 BB 线画得更强更窄，窗口更深；线宽需增加 `60–90%` 才能接近数据。
- **数据可用性**：PRL 正文和 accepted manuscript 无原始数据下载。
- **对本示例**：说明“Fe 特有偏差”不是普适仪器误差；本示例若出现准连续体偏低，应首先检查 PI 截面、CI 与等离子体屏蔽/线宽，而非直接归因实验。

## 6. Zhou et al. 2026 — *Plasma screening and configuration interaction effects induced large enhancement on L-shell photoionization cross sections and opacity*

- **条件**：ASD 电子屏蔽 + HNC 离子-离子关联；Fe XVI 示例 `Te=180 eV`，`rho0 = 0.71e22 / 3.0e22 / 9.0e22 cm^-3`；总 Fe 不透明度 `T=182 eV`、`ne=3.1e22 cm^-3`；与 Bailey 2015、Nagayama 2019、OP 比较。
- **能区**：`7–13 Å`、`1200–1600 eV`、`E > 1250 eV` 为关键增强区；CI 在 `1250–1600 eV` 对开 L-shell 离子增强约 `10–20%`。
- **方法**：FAC 做 CI 计算；plasma screening 施加于 direct PI；共振宽度统一取 `10 eV`。
- **关键结论**：plasma screening 使 PI 截面增强 `14–17%`（高密度可到 `23–29%`），CI 再增强 `8–10%`；合并后 Fe L-shell 不透明度比 SC/OP 高 `25–30%`，解释了长期实验-理论差异。
- **数据可用性**：仅有图线和公式，无机器可读谱表。
- **对本示例**：直接支持“基线 DW/单组态 PI 可能低估稠密等离子体不透明度”；但本示例为光薄 CRM，`10–18 Å` 默认窗口主要落在 `0.69–1.24 keV`，与 `1200–1600 eV` 仅部分重叠，只能定性对照。

## 综合判断

1. **谱段**：Fe-L 实验关注 `6–16 Å / 7–13 Å`，理论增强区 `1200–1600 eV`；本示例默认 `10–18 Å`（约 `0.69–1.24 keV`）与其部分重叠，需在文档中明确。
2. **物理状态差异**：文献多为高密度 LTE 或 Z-pinch 实验；本示例复用 FeL 的 0D 光薄 CRM 布居，因此不能逐点数值比对。
3. **方法学**：Zhao 2024 证明 FAC/RDW 背景 PI 与 BPRM 一致，支持用 FAC RR/PI 表做不透明度输入；Zhou 2026 提示 CI 与 plasma screening 是当前基线缺失的主要物理。
4. **验证边界**：6 篇文献均未提供可直接回归的机器可读谱表；只做谱形、吸收带位置、增强区间的定性对照，不纳入 `check.py`。
5. **口径提醒**：现有 `plots_inputs/temperatures.csv` 中 `T_K` 列实为 eV（`log10T=6.5` 对应约 `272 eV`），后续文档不得写成 272 K。
