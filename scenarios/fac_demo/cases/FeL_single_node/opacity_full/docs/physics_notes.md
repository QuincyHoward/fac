# Full-physics 不透明度物理笔记

## 1. 为什么基线平滑

基线 `opacity/` 只使用 `RRTable` 产生的 6 点非共振光电离截面，且 `bound_bound.enabled=false`；因此输出本质是 smooth bound-free background，不可能出现 Fe-L 谱线森林。

## 2. bound-bound 吸收

吸收线截面采用

`σ(E) = (πe²/m_ec) f_lu φ(E-E_lu)`

其中 `f_lu` 来自 `*.tr` 的 gf，`E_lu` 为跃迁能量，`φ` 为归一化 Voigt 线型。下能级布居来自 `.sp` 的 `TYPE=0000000` 布居块。

本场景使用 pseudo-Voigt：高斯核来自 Doppler 宽度与可用仪器宽度，洛伦兹核来自自然宽度和 `.sp` 中的 Stark/impact 宽度字段。它是示例级线型实现，不是实验级辐射转移模型。

## 3. Doppler / Stark / 自然宽度

- Doppler FWHM：`ΔE_D = E0 sqrt(8 kT ln2 / (M c²))`，`T` 来自 `temperatures.csv`（该列虽名为 `T_K`，实际单位为 eV）。
- 自然 FWHM：`ΔE_N = ħ A_ul / (2π)`。
- Stark/impact：若 `.sp` 线块提供 `wimp/wstk`，按其数值作为附加宽度；否则仅用 Doppler + 自然宽度，并在 metadata 中记录 `stark_missing`。

## 4. 密集 PI

优先调用 `fac.TotalPICross(binary_rr, out, level, energies)` 从 `DB_RR` 读取拟合参数并输出 10^-20 cm² 截面。PFAC 不可用时退化为基线 ASCII 6 点 log-log 插值，并明确标注 `pi_source=ascii_rr_loglog`。

## 5. AI/DR 共振

FAC 没有单一 `TotalResonantPICross()` API。本场景预留 `resonant_pi.py` 从 `DB_AI`/`DB_DR` 及 `AITable/DRStrength/AIBranch` 构造详细平衡近似下的共振贡献；若表缺失或 PFAC 不可用，则输出零贡献并记录 `resonance_source=zero_fallback`。该实现仅用于示例级谱形和物理趋势验证，不替代完整 R-matrix 共振计算。

## 6. 不可直接比对

文献多为高密度 LTE 或 Z-pinch 实验，且包含完整电离平衡、辐射转移和自吸收。本场景复用 FeL 0D 光薄 CRM，输出 `cm² per Fe ion`，因此只做谱形与吸收带位置的图像级对照。
