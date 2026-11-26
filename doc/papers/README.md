# FAC 论文与图表归档（doc/papers/）

本目录保存描述 FAC（Flexible Atomic Code）各模块理论与实现的系列论文，以及配套的图形文件和参考文献库。核心是 7 篇 `.tex` 源文档：FAC 系列论文 I—V 分别覆盖原子结构、电子碰撞激发、光电离与辐射复合、自电离与双电子复合、电子碰撞电离；另有两篇专题论文分别讨论外电磁场中的原子理论（ebfield）与磁子能级间碰撞激发的因子化插值方法（mcross）。`facref.bib` 为全体论文共享的 BibTeX 文献库。目录中未包含 Makefile（构建请直接用 `latex`/`dvips` 等常规工具链）。

## 1. 全部文件一览表

| 文件名 | 类型 | 对应论文 / 主题 | 说明 |
|---|---|---|---|
| `structure.tex` | LaTeX 源 | FAC I：Atomic Structure | 相对论原子结构、自洽场与辐射跃迁率 |
| `structure.dvi` | DVI 产物 | FAC I | `structure.tex` 的 DVI 排版结果 |
| `structure.ps` | PS 产物 | FAC I | `structure.dvi` 转 PostScript |
| `str.eps` | EPS 插图 | FAC I | 结构论文中的示意图 |
| `excitation.tex` | LaTeX 源 | FAC II：Electron Impact Excitation | 电子碰撞激发（EIE）扭曲波理论 |
| `excitation.dvi` | DVI 产物 | FAC II | `excitation.tex` 的 DVI 排版结果 |
| `excitation.ps` | PS 产物 | FAC II | `excitation.dvi` 转 PostScript |
| `exc.eps` | EPS 插图 | FAC II |激发截面/碰撞强度图 |
| `pirr.tex` | LaTeX 源 | FAC III：Photoionization and Radiative Recombination | 光电离（PI）与辐射复合（RR） |
| `pirr.dvi` | DVI 产物 | FAC III | `pirr.tex` 的 DVI 排版结果 |
| `pirr.ps` | PS 产物 | FAC III | `pirr.dvi` 转 PostScript |
| `ionization.tex` | LaTeX 源 | FAC V：Electron Impact Ionization | 电子碰撞电离（EII） |
| `ionization.dvi` | DVI 产物 | FAC V | `ionization.tex` 的 DVI 排版结果 |
| `ionization.ps` | PS 产物 | FAC V | `ionization.dvi` 转 PostScript |
| `ion.eps` | EPS 插图 | FAC V | 电离截面图 |
| `aidr.tex` | LaTeX 源 | FAC IV：Autoionization and Dielectronic Recombination | 自电离（AI）与双电子复合（DR） |
| `aidr.dvi` | DVI 产物 | FAC IV | `aidr.tex` 的 DVI 排版结果 |
| `aidr.ps` | PS 产物 | FAC IV | `aidr.dvi` 转 PostScript |
| `ebfield.tex` | LaTeX 源 | 外电磁场原子理论 | mCVs 中 10⁵–10⁸ G 磁场下的 Zeeman/Stark 结构 |
| `ebfield.pdf` | PDF 产物 | 外电磁场原子理论 | `ebfield.tex` 的 PDF 排版结果 |
| `mcross.tex` | LaTeX 源 | 磁子能级碰撞激发 | 磁子能级间激发的因子化插值方法与线偏振 |
| `mcross.pdf` | PDF 产物 | 磁子能级碰撞激发 | `mcross.tex` 的 PDF 排版结果 |
| `rate.eps` | EPS 插图 | FAC IV / 速率系数 | 复合/电离速率系数图 |
| `tr.eps` | EPS 插图 | FAC I / 跃迁 | 辐射跃迁数据图 |
| `facref.bib` | BibTeX | 全部论文 | 共享参考文献数据库 |

## 2. 论文主题详解：简介 + 公式 + FAC 源码对应

### 2.1 structure —— 相对论原子结构与辐射跃迁（FAC I）
**简介**：FAC 系列首篇。束缚态在组态混合近似下求解，径向轨道由“修正的自洽 Dirac–Fock–Slater 迭代”在带分数占据数的虚拟平均组态上产生；随后构造 CSF 并对角化哈密顿量得到能级，辐射跃迁率在单多极近似下按任意阶多极算符计算。
$$
\hat H\Psi_k=E_k\Psi_k,\qquad
H=\sum_{i=1}^{N}H_D(i)+\sum_{i<j}\frac{1}{r_{ij}},\qquad
gf_{fi}=[L]^{-1}\omega(\alpha\omega)^{2L-2}S_{fi},\quad
gA_{fi}=2\alpha^{3}\omega^{2}gf_{fi}.
$$
**FAC 实现**：`faclib/structure.c`（结构/对角化）、`faclib/orbital.c`、`faclib/radial.c`（径向积分）、`faclib/transition.c`（跃迁率）；Python API `fac.Structure`/`fac.TransitionTable`。对应示例 [demo/structure/](../../demo/structure/README.md)（Ne-like Fe 的 `ne.lev`、`ne.tr`）。

### 2.2 excitation —— 电子碰撞激发（FAC II）
**简介**：相对论扭曲波（DW）近似下的直接碰撞激发。采用因子化–插值法将角向耦合与径向积分分离，连续波函数用 phase-amplitude 方法处理长程贡献，大角动量分波用 Coulomb–Bethe 近似补齐；论文给出 Ne-like Fe 的 2→3 与 Be-like Fe 的 2→2 跃迁结果。
$$
\sigma_{01}=\frac{\pi}{k_0^{2}g_0}\,\Omega_{01},\qquad
\Omega_{01}=2\sum_{\kappa_0\kappa_1}\sum_{J_T}[J_T]\,
\Big|\Big\langle\psi_0\kappa_0,J_TM_T\Big|\sum_{i<j}\frac1{r_{ij}}
\Big|\psi_1\kappa_1,J_TM_T\Big\rangle\Big|^{2}.
$$
**FAC 实现**：`faclib/excitation.c`（`CETable`、碰撞强度因子化与插值）、`faclib/rates.c`（Maxwell 速率系数）。对应示例 [demo/excitation/](../../demo/excitation/README.md)（Ne-like Fe 的 `ne.ce`、`ne.ceM`）。

### 2.3 pirr —— 光电离与辐射复合（FAC III）
**简介**：非共振光电离（PI）与辐射复合（RR）截面。连续态用相对论 DW 近似，束缚–自由微分振子强度用非相对论多极算符（光子能量小于电子静质量时精度足够），并由 Milne 关系把 PI 与 RR 联系起来；测试对象为 Li-like Fe。
$$
\sigma_{\rm PI}=2\pi\alpha\,\frac{df}{dE},\qquad
\sigma_{\rm RR}=\frac{\alpha^{2}}{2}\,\frac{g_i}{g_f}\,
\frac{\omega^{2}}{\varepsilon\left(1+\frac12\alpha^{2}\varepsilon\right)}\,\sigma_{\rm PI}.
$$
其中 $\omega$ 为光子能量、$\varepsilon$ 为出射光电子能量；原文未引入 $\chi$ 记号。
**FAC 实现**：`faclib/recombination.c`（`RRTable`、束缚–自由矩阵元）、`faclib/interpolation.c`。对应示例 [demo/pirr/](../../demo/pirr/README.md)（Li-like Fe 的 `li.lev`、`li.rr`）。

### 2.4 aidr —— 自电离与双电子复合（FAC IV）
**简介**：相对论 DW + 孤立共振近似下的自电离（AI）率与辐射无电子俘获（DC）率。AI/DC 是处理 DR、共振激发、共振电离的核心输入；论文以 Ne-like Se 双激发态的 AI 率及 F-like Fe 的 Δn=0 DR 速率系数为基准。
$$
A^{a}=2\sum_{\kappa}\Big|\Big\langle\psi_f,\kappa;J_TM_T\Big|
\sum_{i<j}\frac{1}{r_{ij}}\Big|\psi_i\Big\rangle\Big|^{2},
\qquad
S_{\rm DC}=\frac{g_i}{2g_f}\frac{\pi^{2}}{E_{if}}A^{a},
\qquad
B(i)\approx\frac{\sum_k A^{r}(i\to k)}
{\sum_{k'}A^{a}(i\to k')+\sum_k A^{r}(i\to k)}.
$$
**FAC 实现**：`faclib/recombination.c`（`AITable`/`AITableMSub`、`DRStrength`）、`faclib/rates.c`（Maxwell 平均）。对应示例 [demo/aidr/](../../demo/aidr/README.md)（Ne-like Se 的 `se.ai`）。

### 2.5 ionization —— 电子碰撞电离（FAC V）
**简介**：逐能级–能级的电子碰撞电离（EII）截面，在 DW 近似下把 EIE 的因子化–插值法推广到双连续电子末态；同时提供高效的 Coulomb–Born–Exchange（CBE）与 Binary-Encounter-Dipole（BED）方法，基准为 Ne-like Fe 的 2s/2p 电离。
$$
\sigma(\varepsilon_0,\varepsilon)=\frac{1}{k_0^{2}g_0}\,\Omega_{01},\qquad
\sigma(\varepsilon_0)=\int_{0}^{(\varepsilon_0-I)/2}\sigma(\varepsilon_0,\varepsilon)\,d\varepsilon .
$$
**FAC 实现**：`faclib/ionization.c`（`CITable`、角向/径向分离）、`faclib/rates.c`。对应示例 [demo/ionization/](../../demo/ionization/README.md)（Ne-like Fe 的 `ne.ci`）。

### 2.6 ebfield —— 外电磁场中的原子结构
**简介**：针对磁 CV 中 10⁵–10⁸ G 的弱场区（Zeeman/Stark 劈裂远小于库仑作用，但与电子关联能可比），用组态相互作用在有限基组中同时处理关联与外场；磁场破坏球对称，电场进一步破坏柱/镜对称，哈密顿量矩阵显著变大。基于 FAC 框架实现新的原子理论。
$$
H=H_0+H_B^{(1)}+H_B^{(2)}+H_E,\qquad
H_B^{(1)}=\sum_i\mu_B\big(2\mathbf S_i+\mathbf L_i\big)\cdot\mathbf B,
$$
$$
H_B^{(2)}=\sum_i\frac12\mu_B^{2}\big|\mathbf B\times\mathbf r_i\big|^{2},
\qquad
H_E=\sum_i\mathbf E\cdot\mathbf r_i,\qquad
\mu_B=5.788\times10^{-5}\ {\rm eV/T}.
$$
**FAC 实现**：以 `faclib/structure.c` 的哈密顿量构建与对角化为基础扩展外场算符；CRM 应用涉及 `faclib/crm.c`。无独立 demo，可参照 [demo/NeL/](../../demo/NeL/README.md) 的 CRM 流程。

### 2.7 mcross —— 磁子能级间碰撞激发与线偏振
**简介**：把 DW 碰撞激发的因子化理论推广到磁子能级（magnetic sublevel）间的激发，用于电子束碰撞产生的线偏振建模（太阳耀斑、托卡马克、EBIT）。碰撞强度分解为只含单电子径向波函数的径向部分与含靶态角向耦合的角向部分，可快速插值得到整个跃迁阵列的磁子能级碰撞强度。
$$
B_{m_{si}}^{m_{sf}}=\frac{2\pi}{k_i}
\sum_{l_i m_{li} j_i m_i\atop l_f m_{lf} j_f m_f}
i^{\,l_i-l_f+1}e^{i(\delta_i+\delta_f)}
Y_{l_i}^{m_{li}*}(\hat{\mathbf k}_i)Y_{l_f}^{m_{lf}}(\hat{\mathbf k}_f)
C\!\left(l_i\tfrac12 m_{li}m_{si};j_im_i\right)
C\!\left(l_f\tfrac12 m_{lf}m_{sf};j_fm_f\right)T(\alpha_i,\alpha_f),
$$
线偏振度的初等定义常写作 $P=(I_\parallel-I_\perp)/(I_\parallel+I_\perp)$，但 `mcross.tex` **未给出**该定义；FAC 实际输出由 `faclib/polarization.c` 的球张量比值 $a/b$ 给出（见 `faclib/README.md` §3.7）。
**FAC 实现**：`faclib/excitation.c`（`CETableMSub`）、`faclib/polarization.c`（偏振、取向参数）；Python 接口 `pfac.pol`。对应示例 [demo/excitation/](../../demo/excitation/README.md) 的磁子能级表 `ne.ceM` 与 [demo/polariz/](../../demo/polariz/README.md)。

## 3. 图表与文献库说明

- `str.eps`、`exc.eps`、`ion.eps`、`rate.eps`、`tr.eps` 为插入相应论文的 EPS 图，分别对应结构、激发、电离、速率与跃迁主题。
- `structure.dvi/.ps`、`excitation.dvi/.ps`、`pirr.dvi/.ps`、`aidr.dvi/.ps`、`ionization.dvi/.ps` 为系列论文 I—V 的排版产物；`ebfield.pdf`、`mcross.pdf` 为两篇专题论文的 PDF 版。
- `facref.bib` 集中存放上述论文引用的文献条目，供所有 `.tex` 共同 `\bibliography{facref}` 使用。

## 4. README 维护记录（自底向上）

- **定位与职责**：`doc/papers/` 存放 FAC 系列论文与专题论文，是理论公式的文献来源，不是实现依据。
- **底层依据**：`structure.tex`、`excitation.tex`、`ionization.tex`、`pirr.tex`、`aidr.tex`、`mcross.tex`、`ebfield.tex`。
- **输入/输出**：输入 LaTeX 与 EPS 图；输出 DVI/PS/PDF 论文及 `facref.bib` 文献库。
- **验证与回归**：通过 `make` 编译论文；不参与数值回归。
- **已知限制**：论文记号与源码变量名可能不同；公式是否在源码实现，以对应源码目录 README 的下划线注记为准。
- **公式核查**：本目录不新增源码实现证据；所有公式引用必须回溯到 `faclib/`、`modqed/`、`coul/`、`ionis/` 或 `demo/` 的核查结论。
- **导航**：父级 [`../README.md`](../README.md)；根 [`../../README.md`](../../README.md)。

[返回上级](../README.md)