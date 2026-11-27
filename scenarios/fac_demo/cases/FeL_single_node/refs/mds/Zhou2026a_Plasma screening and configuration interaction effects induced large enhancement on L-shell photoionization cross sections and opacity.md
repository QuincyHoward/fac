# Zhou2026a_Plasma screening and configuration interaction effects induced large enhancement on L-shell photoionization cross sections and opacity

- Source: `Zhou2026a_Plasma screening and configuration interaction effects induced large enhancement on L-shell photoionization cross sections and opacity.pdf`
- Pages: 9

## Page 1

Plasma screening and configuration interaction effects induced large enhancement on
L-shell photoionization cross sections and opacity
Fuyang Zhou,1, ∗Shengbo Niu,2, ∗Simei Lu,3 Chuangying Li,4
Xiang Gao,4 Yong Wu,4, 5, † Yizhi Qu,6, ‡ and Jianguo Wang4
1National Key Laboratory of Computational Physics,
Institute of Applied Physics and Computational Mathematics, Beijing 100088, P. R. China
2School of Optoelectronics, University of Chinese Academy of Sciences, Beijing 100049, P. R. China
3School of Mathematics and Physics, Qinghai University, Xining, 810016, P. R. China
4National Key Laboratory of Computational Physics,
Institute of Applied Physics and Computational Mathematics, Beijing, 100088, P. R. China
5Center for Applied Physics and Technology, HEDPS,
Peking University, 100871, Beijing, P. R. China
6School of Optoelectronics, University of Chinese Academy of Sciences, Beijing, 100049, P. R. China
(Dated: July 24, 2026)
An opacity model that incorporates improved treatments of both plasma screening and configu-
ration interaction (CI) effects is proposed, and a 25-30% enhancement on the iron L-shell opacity is
predicted at solar interior temperatures. It is originated from the plasma screening induced 14-17%
enhancement on the photoionization cross sections and the CI induced 10-20% enhancement on
photoexcitation and photoionization cross sections for open L-shell ions. These explain the long-
standing discrepancy between theoretical and experimental iron opacity [Nature 517, 56], and the
relatively weaker enhancements on chromium and nickel opacity [Phys. Rev. Lett. 122, 235001] due
to the sensitivity of these effects to the different L-shell electron population and plasma tempera-
ture/density. This letter provides the systematic interpretation of L-shell opacity measurements at
solar interior temperatures, and advances the accurate simulation of opacity and radiative transport
in high-energy-density plasma.
I. INTRODUCTION
Radiative opacity quantifies the ability of photon ab-
sorption in matter and plays an important role on the
energy transport in high-energy-density plasma. In as-
trophysics, opacity is crucial to the simulations of stellar
structure and evolution, and its accuracy affects the pre-
cision of stellar models [1]. In recent decades, solar inte-
rior opacity has been questioned due to the discrepancy
between standard solar models and helioseismic obser-
vations, which could be resolved if the theoretical mean
opacity is increased by about 15% [2–5]. Moreover, the
laboratory measurements of iron (Z = 26 ) opacity at
the solar interior temperatures in the Sandia Z-pinch fa-
cility disagree considerably with predicted opacities by
30–400% in the wavelength range of 7–13 ˚A [6]. More sur-
prisingly, the chromium (Z = 24 ) and nickel (Z = 28 )
opacities measured with the same methods agree with the
opacity models [7]. The 30%–45% model-data disagree-
ments in the high-energy featureless direct photoioniza-
tion (bound-free continua) was observed only from iron
[6]. These systematic experimental studies reveal missing
physics in opacity models.
Motivated by this problem, various theoretical efforts
[8–17] have been devoted to investigate the multiple phys-
ical effects encountered in opacity models.
Pain and
Gilleron [8] investigated the effects of highly excited
states on opacity using a partial detailed-line-accounting
calculation. Krief et al. [9] demonstrated that increasing
line widths by two orders of magnitude can recover the
missing solar interior opacity. Fontes et al. [10] carefully
analyzed relativistic effects on opacity. More et al. [11]
and Pain [12] examined the contributions of two-photon
and multi-photon processes to opacity. Krief et al. [13]
examined the effects of ion-ion correlation on the ionic
structure and opacity, and indicated that these effects
indeed increase the Rosseland mean opacity near the con-
vection zone. Zeng et al. [14] proposed that the contin-
uum electrons lose phase and coherence in the radiative
processes, giving rise to a phenomenon of transient spa-
tial localization and considerably enhance the continuum
opacity. However, the reason why the predicted opacity is
lower than the data only for Fe at high temperature and
density has not been clearly demonstrated. Meanwhile,
these studies also reveal that modeling environmental ef-
fects of high-energy-density plasma and calculating photo
absorption for open L-shell excited states involve sub-
stantial complexities, indicating fundamental limitations
in approximations of previous opacity models.
In this letter, an opacity model that incorporates im-
proved treatments of both plasma screening and config-
uration interaction (CI) effects is proposed to investigate
this long-standing problem. This model predicts signifi-
cantly enhanced photoionization cross sections due to the
plasma screening effects, which is described by employing
atomic-state-dependent (ASD) electron screening model
[18] and ion-ion correlation (IC) model [13,19]. Addition-
ally, the CI effect is found to be crucial on photoexcita-
tion and photoionization cross sections for open L-shell
arXiv:2607.21238v1  [physics.atom-ph]  23 Jul 2026


## Page 2

2
ions. We suggest that the unexplained experimental ob-
servations and missing opacity in solar interior can be
interpreted by the combined influence of these effects.
II. PLASMA SCREENING EFFECT ON
PHOTOIONIZATION CROSS SECTIONS
For ions embedded in the Z-pinch plasma [6,7], strong
plasma screening effects will be encountered due to com-
plicated many-body interactions with the surrounding
ions and electrons, and significantly affects the atomic
wave functions and the photoionization cross sections.
Considering the plasma screening effect, the Dirac Hamil-
tonian for an atom is given by
HDC =
N
X
i=1

c αi·pi + (βi −1)c2 + V (ri)

+
N
X
i<j
1
rij
. (1)
where αi and βi are Dirac matrices, and pi is the mo-
mentum operator.
The central atomic potential V (ri)
includes the nuclear potential and the external field gen-
erated by plasma screening, and the present model rep-
resents it as
V (r) = −Z
r + Ve(r) + Vion(r).
(2)
Here, r = |r| is the distance from the center of the
nucleus, and Z is the nuclear charge.
The potential
Ve(r) =
R
ρe(r′)/|r −r′| d3r′ arises from the electron–
electron interaction with the plasma electrons, whereas
V+(r) = −
R
ρ+(r′)/|r −r′| d3r′ is due to the pene-
trating positive charges associated with the surrounding
ions. Here, ρe and ρ+ denote the spatial distributions of
the plasma electrons and positive charges, respectively.
The ASD model[18] is employed to calculate the plasma-
electron distribution ρe and the resulting screening effect.
Within a unified framework, the model accounts for con-
tributions from both elastic and inelastic collisions be-
tween the ion and plasma electrons. Its feasibility and va-
lidity have been demonstrated by successfully reproduc-
ing recent experimental results for spectral line shifts and
ionization-potential depression (IPD) over wide ranges of
temperature and density[18,20].
As shown in Figure 1(a) for Fe16+ ion embedded in
a dense plasma, the ion-electron and ion-ion pair distri-
bution functions indicate that the surrounding ions and
electrons of hot dense plasma can approach the nucleus
via collision processes and thereby screen the Coulomb
interaction between nucleus and bound electron. From
figure 1(b), it can be found from that the screening ef-
fects from surrounding ions become significant for ex-
cited orbitals. But the commonly used ion-sphere model,
which assumes each ion is enclosed within a sphere of
radius RW S, underestimated its impact [13,19]. There-
fore, to accurately describe the screening effect on excited
atomic orbitals, we extend the ASD model by incorpo-
rating the screening from surrounding ions within the IC
model [13,19], which allows ionic charges to penetrate
the ion sphere and contributes to screening of the central
potential. In this model, charge neutrality requires that
ρe(r) →ρ+(r) →ρ0 as r →∞, and
ρ0 =
X
Z∗N i
ion,
(3)
where Z∗is the nuclear charge minus the number of
bound electrons, N i
ion is the ion density of ion “i”. For
the IC model, we have
ρ+(r) =
X
i
Z∗ρ0gii(r)
(4)
and
Z ∞
0
[ρb(r) + ρe(r) −ρ+(r)]d3r = Z.
(5)
ρb(r) is the distribution of bound electrons, gii(r) is the
ion-ion pair distribution function and it has to satisfy
the hypernetted-chain (HNC) integral equation. The dis-
tributions ρe(r) and ρ+(r) are obtained through a self-
consistent iterative procedure.
Taking the Fe16+ ion embedded in plasma with Te =
180eV and ρ0 = 3 × 1022cm−3 as an example, figure
1(b) and 1(c) show that the change of central atomic
potential V (r) from plasma screening effect significantly
affects the atomic energy levels and wave functions of
continuum electrons, resulting in ionization potential de-
pression (IPD) and remarkable changes in the photoion-
ization cross sections.
As the density ρ0 increases to
ρ0 = 9 × 1022cm−3 , the screening effect further intensi-
fies its modification of both bound and continuum wave
functions. Figure 1(c) reveals that the changes in the cen-
tral atomic potential V (r) significantly broaden the spa-
tial range of continuum orbitals and enhances the spatial
overlap between bound and continuum wave functions,
ultimately leading to an increase of the photoionization
cross sections.
Figures 2(a) and 2(b) present the photoionization cross
sections for the 2p3/2 →εd5/2 transition channel of Fe16+
embedded in different plasma environments.
Plasma
screening leads to ionization-potential depression (IPD)
and significantly enhances the photoionization cross sec-
tions by increasing the spatial overlap between the bound
and continuum atomic wave functions.
Moreover, this
enhancement becomes stronger as the electron density
increases. At Te = 180 eV and ρ0 = 7.1 × 1021 cm−3, the
photoionization cross section for the 2p3/2 →εd5/2 chan-
nel is predicted to increase by 7–9%. The corresponding
enhancements reach 14–17% at ρ0 = 3.0 × 1022 cm−3,
corresponding to the conditions achieved at the Sandia
Z-pinch facility, and 23–29% at ρ0 = 9.0×1022 cm−3, cor-
responding to conditions near the boundary between the
solar convection and radiative zones. Furthermore, be-
cause excited orbitals have a greater radial extent, their


## Page 3

3
0
5
10
15
20
25
30
r (a.u.)
0
1
2
3
4
5
g(r)
RWS of Fe16+
gie(r)
gii(r)
Plasma
Electron
Different ions
(a)
RWS
0.0
0.5
1.0
1.5
(r/RWS)1/2
-50
-40
-30
-20
-10
0
Potential (a.u.)
6p3/2 orbital energy
4p3/2 orbital energy
2p3/2 orbital energy
−Z/r
−Z/r+Ve(r)
−Z/r+Ve(r)+V +(r)
(b)
0.0
0.5
1.0
1.5
2.0
P2p3/2(r)
(c)
isolated ion
180 eV, 3×1022 cm−3
180 eV, 9×1022 cm−3
-1.0
-0.5
0.0
0.5
P4p3/2(r)
0
1
2
3
r (a.u.)
-1.0
-0.5
0.0
0.5
Pεd5/2(r)
FIG. 1.
Plasma screening effects on atomic radial wave functions. (a) The pair distribution functions of ion-electron and
ion-ion of Fe16+ ion embedded in plasma with temperature Te = 180eV and mean electron number density ρ0 = 3×1022cm−3.
RW S =
p
3Z∗/(4πρ0) is the Wigner-Seitz radius of Fe16+. (b) The central atomic potentials V (r) in the present model, as
well as the energies of 2p3/2, 4p3/2 and 6p3/2 orbitals calculated with these potentials. (c) Taking np →ϵd photoionization
as an examples, the plasma screening effects on the atomic radial wave functions of bound electron orbital (2p3/2, 4p3/2) and
continuum orbital (ϵp3/2 with ϵ = 0.1a.u.) are presented.
1100
1200
1300
1400
1500
Photon energy (eV)
0.2
0.4
0.6
0.8
Cross section (10−19 cm2)
2p3/2→εd5/2
(a)
Isolated ion
165 eV, 7×1021 cm−3
180 eV, 3×1022 cm−3
180 eV, 9×1022 cm−3
0
100
200
300
400
Photoelectron energy (eV)
100%
105%
110%
115%
120%
125%
130%
135%
140%
Screened/isolated ratio (%)
2p3/2→εd5/2
(b)
165 eV, 7×1021 cm−3
180 eV, 3×1022 cm−3
180 eV, 9×1022 cm−3
200
300
400
Photon energy (eV)
0.5
1.0
1.5
2.0
2.5
Cross section (10−19 cm2)
4p3/2→εd5/2
(c)
Isolated ion
165 eV, 7×1021 cm−3
180 eV, 3×1022 cm−3
180 eV, 9×1022 cm−3
0
100
200
Photoelectron energy (eV)
100%
120%
140%
160%
180%
200%
220%
240%
Screened/isolated ratio (%)
4p3/2→εd5/2
(d)
165 eV, 7×1021 cm−3
180 eV, 3×1022 cm−3
180 eV, 9×1022 cm−3
FIG. 2.
Plasma screening effects on photoionization cross
sections in dense plasma. (a) Photoionization cross sections
for the 2p3/2 →εd5/2 transition channel of Fe16+ embedded in
different plasma environments as a function of photon energy.
(b) Ratios of the screened cross sections to the isolated-ion
results for the 2p3/2 →εd5/2 transition channel as a function
of photoelectron energy.
(c) Photoionization cross sections
for the 4p3/2 →εd5/2 transition channel. (d) Corresponding
cross-section ratios for the 4p3/2 →εd5/2 transition channel.
photoionization processes are more strongly affected by
plasma screening. As shown in Figs. 2(c) and 2(d), the
photoionization cross section for the 4p3/2 →εd5/2 tran-
sition channel exhibits a larger enhancement than that
for the 2p3/2 →εd5/2 channel.
III. CONFIGURATION INTERACTION EFFECT
ON PHOTOIONIZATION AND OPACITY
At solar interior temperatures, iron is ionized to charge
states of 16+ and higher, generating numerous complex
open L-shell excited states.
Consequently, it is essen-
tial to examine the CI effect on the L-shell photoioniza-
tion and opacity of these Fe ions. In particular, main-
stream opacity codes typically adopt one orbital basis,
which is usually obtained from Dirac-Hartree-Fock cal-
culations on the ground configuration, to compute all
configurations.
Such a basis is not fully appropriate
for excited configurations, and the CI treatment may
be inadequate.
To address this, we employ the Flexi-
ble Atomic Code (FAC) [21] to examine the CI effects on
the L-shell photoionization of both closed-shell ground
configurations and open-shell excited configurations. As
an example, figure 3 illustrates the photoionization cross
sections obtained with CI and single-configuration (SC)
for closed L-shell state 2s22p6(1S) and open L-shell state
2s22p53p(1S0) of isolated Fe16+. For the closed L-shell
state 2s22p6, the direct photoionization cross sections
calculated using SC and CI methods are identical, and
difference arise only in the indirect resonance photoion-
ization processes, which proceed via photoexcitation into
autoionizing states. Due to the CI effects, the increase
in resonance ionization channels leads to local enhance-
ments to the photoionization cross sections, as demon-
strate by the additional resonance peak observed around
1650 eV in the CI calculations of figure 3(a). But for
the open L-shell state 2s22p53p, the CI effect can influ-
ences the direct photoionization cross section by approx-
imately 10%, as shown in figure 3(b). Additionally, for


## Page 4

4
0
2
4
6
8
10
Cross section (10−18 cm2)
2s22p6 (1S0)
Total PI of SC
Direct  PI of SC
Total PI of CI
Direct  PI of CI
indirect resonant peak
(a)
1000
1200
1400
1600
1800
2000
Photon energy (eV)
0
2
4
6
8
10
Cross section (10−18 cm2)
2s22p53p (1S0)
Total PI of SC
Direct  PI of SC
Total PI of CI
Direct  PI of CI
(b)
FIG. 3.
Configuration-interaction (CI) effects on the
photoionization (PI) cross sections of the ground state
2s22p6 (1S0) and the excited state 2s22p53p (1S0) of Fe16+.
The CI calculations include configurations generated by sin-
gle and double excitations from the valence orbitals to or-
bitals with principal quantum number n ≤8. Indirect res-
onant photoionization processes are also included using the
isolated-resonance approximation. To illustrate their effects
on the opacity, the widths of all resonance peaks are uniformly
set to 10 eV.
indirect resonance photoionization, the CI effect modi-
fies both resonance positions and intensities, leading to
an increased photoionization cross section at higher pho-
ton energies.
Subsequently, large-scale CI calculations
for a broad range of atomic parameters are carried out
to investigate the opacity at solar interior temperatures.
Figure 4(a) and 4(b) illustrate the CI effect on the
bound-bound (BB) and bound-free (BF) opacities of
Fe15+ and Fe16+ ions at Te = 180eV . Here, BB opacity
includes contributions from all bound-state photoexci-
tation and resonance photoionization, while BF opacity
arises from direct photoionization. For Fe15+ ion in fig-
ure 4(a), where all bound states have a closed L-shell, the
CI effect on the opacity contributed from both L-shell
BB transitions and photoionizations is almost negligible.
However, for Fe16+ ion in figure 4(b), CI significantly
alters the calculated results for photoexcitation and pho-
toionization from open L-shell excited states, resulting
in an approximate 10-20% increase in both BB and BF
opacities within photon energy of 1250-1600 eV. Overall,
the CI effect is found to be significant in opacity calcu-
lations for Fe ions with open L-shell.
As shown in the figure 4(c), for total opacity of Fe
plasma at Te = 180 and ne = 3.1 × 1022cm−3, our SC
calculation are generally consistent with the OP results
[7]. Plasma screening and CI effects increase the opac-
ity for photon energies above 1250 eV by about 17% and
1000
1100
1200
1300
1400
1500
1600
1700
1800
0
5000
10 000
15 000
Opacity (cm2/g)
Fe15+
BB opacity of SC
BF opacity of SC
BB opacity of CI
BF opacity of CI
(a)
1000
1100
1200
1300
1400
1500
1600
1700
1800
0
2000
4000
6000
8000
10 000
Opacity (cm2/g)
Fe16+
BB opacity of SC
BF opacity of SC
BB opacity of CI
BF opacity of CI
(b)
1100
1200
1300
1400
1500
1600
1700
1800
Photon energy (eV)
1000
2000
3000
4000
5000
6000
7000
Opacity (cm2/g)
Fe plasma
SC calculation
SC & Screening effect
CI & Screening effect
OP model [7]
(c)
FIG. 4.
Configuration interaction effects on iron opacity.
Configuration interaction effects onon BB and BF opacities
of Fe15+ and Fe16+ ion at Te = 180eV are presented in plots
(a) and (b). In the CI calculations, all energy levels, transition
rate, and photoionization cross sections were calculated based
on FAC code with considering the configuration obtained from
single excitation from both initial and final contributions to
orbitals n ≤6. (c) Configuration interaction effects on total
opacity of Fe plasma at Te = 180eV and ne = 3.1×1022cm−3.
8%, respectively. As a result, the refined calculation re-
sults are 25-30% larger than those from the SC and OP
models.
The results reveal that incomplete considera-
tion of these CI and plasma screening effects may lead to
theory-experiment discrepancies exceeding the measure-
ment uncertainty. It is noted that since plasma screening
effects are applied only to the direct photoionization cross
sections in this work, the coupling between screening and
CI effects is not fully included and requires self-consistent
treatment in future studies.
IV. ANALYSES AND EXPLANATION OF
OPACITY EXPERIMENTS ON THE Z-PINCH
After considering the plasma screening and CI effects
discussed above, the calculated spectrally resolved opac-
ity of Cr, Fe and Ni plasmas are compared with the ex-
periments on the Z-pinch [6,7] and theoretical results of
OP [7] in figure 5. The present theory is in much closer
agreement with the experiment, and there are two main
improvements of our new results. Firstly, due to the ap-


## Page 5

5
proximately 25-30% enhancement of opacity from both
plasma screening and CI effect, the present work well ex-
plains the experimental opacity within photon energies of
1200-1500 eV for Fe plasma at 182eV and 3.1×1022cm−3,
as shown in figure 5(b). It is noted that the experiments
actually measured the transmissivity of FeMg mixture.
After including the screening effect on the transmissivity
of Mg, the original Fe calculations shown by the dashed
blue and magenta curves in figure 5(b) are corrected to
the corresponding solid curves. The correction is most
visible above 1500 eV, resulting in good agreement be-
tween the theory and experiment for the entire spectrally
resolved opacity spectrum. The details of the correction
are provided in supplemental material. Secondly, as seen
in Figures 5(a) and 5(c), the measured opacities of Cr and
Ni at similar temperature and density are also reasonably
reproduced by the present model. Due to the sensitivity
of CI and plasma screening effects to the L-shell electron
population and plasma temperature/density, the corre-
sponding enhancements on Cr and Ni opacity are rela-
tively weaker, e.g. about 15-18% enhancement for Cr. In
general, the opacities calculated for Cr, Fe, and Ni plas-
mas agree with the measure data within the experimental
uncertainties. The remaining difference may arise from
the uncertainties in temperature and density, as well as
the non-equilibrium effects on the populations of ions and
their excited states. By appropriately varying tempera-
ture and density, all calculated results can be brought
into better agreement with experimental values.
V. CONCLUSION
Opacity calculations involve challenging issues in
atomic and plasma physics, especially in accounting for
complex quantum many-body effects such as plasma
screening and configuration interaction. By employing
the ASD and IC models, the screening effects from both
electrons and ions of plasma on the photoionization cross
sections are investigated and found to be significant for
dense plasma. Additionally, the CI effect is found to play
an important role in opacity calculations of open L-shell
ions. By incorporating the improved treatments of both
plasma screening and CI effects, an novel opacity model
is proposed and provides a reasonable interpretation of
the systematic experimental opacity data obtained at so-
lar interior temperatures from the Sandia Z-pinch facility.
This work advances the understanding of radiative opac-
ity of high-energy-density plasma, and indicates that the
missing opacity in solar interior can be interpreted by
precisely treatments of plasma screening and CI effects.
This work was supported by the National Natural Sci-
ence Foundation of China (Grants No. U2430208). We
also acknowledge the National Key Laboratory of Com-
putational Physics.
1000
1200
1400
1600
1800
0
5000
10000
Opacity (cm2 g−1)
Expt.
This work
This work (Te +3%, ne −3%)
OP [7]
(a)
Cr, 180 eV, 2.9×1022 cm−3
1000
1200
1400
1600
1800
0
5000
10000
Opacity (cm2 g−1)
Expt.
This work
This work (Te −4%, ne +25%)
OP [7]
(b)
Fe, 182 eV, 3.1×1022 cm−3
1200
1400
1600
1800
Photon energy (eV)
0
5000
10000
15000
Opacity (cm2 g−1)
Expt.
This work
This work (Te +3%, ne −10%)
OP [7]
(c)
Ni, 187 eV, 2.9×1022 cm−3
FIG. 5.
Comparison of the calculated spectrally resolved
opacities of Cr, Fe, and Ni plasmas with the experimental
results of Refs.[6,7] and the OP calculations of Ref.[7]: (a)
Cr plasma at T = 180 eV and ne = 2.9 × 1022 cm−3; (b) Fe
plasma at T = 182 eV and ne = 3.1 × 1022 cm−3; and (c)
Ni plasma at T = 187 eV and ne = 2.9 × 1022 cm−3. Based
on the temperature and density uncertainties from refs. [6,7],
the impacts of these uncertainties on opacity calculations are
also shown. In panel (b), the dashed blue and magenta curves
show the original Fe calculations, whereas the corresponding
solid curves include the Mg correction described in the sup-
plemental material.
∗These authors contributed equally to this work.
† wu˙yong@iapcm.ac.cn
‡ yzqu@ucas.ac.cn
[1] F. Delahaye and M. Pinsonneault, Comparison of radia-
tive accelerations obtained with atomic data from OP
and OPAL, Astrophys. J. 625, 563 (2005).
[2] J. N. Bahcall, A. M. Serenelli, and M. Pinsonneault, How
accurately can we calculate the depth of the solar con-
vective zone?, Astrophys. J. 614, 464 (2004).
[3] N. Grevesse, M. Asplund, A. Sauval, and P. Scott, The
chemical composition of the Sun, Astrophys. Space Sci.
328, 179 (2010).
[4] A. M. Serenelli, S. Basu, J. W. Ferguson, and M. As-
plund, New solar composition: the problem with solar
models revisited, Astrophys. J. 705, L123 (2009).
[5] G. Buldgen et al., Helioseismic inference of the solar ra-
diative opacity, Nat. Commun. 16, 693 (2025).


## Page 6

6
[6] J. E. Bailey et al., A higher-than-predicted measurement
of iron opacity at solar interior temperatures, Nature 517,
56 (2015).
[7] T. Nagayama et al., Systematic study of L-shell opacity
at stellar interior temperatures, Phys. Rev. Lett. 122,
235001 (2019).
[8] J.-C. Pain and F. Gilleron, Accounting for highly excited
states in detailed opacity calculations, High Energy Den-
sity Phys. 15, 30 (2015).
[9] M. Krief, A. Feigel, and D. Gazit, Line broadening and
the solar opacity problem, Astrophys. J. 824, 98 (2016).
[10] C. J. Fontes, C. L. Fryer, A. L. Hungerford, P. Hakel,
J. Colgan, D. P. Kilcrease, and M. E. Sherrill, Relativis-
tic opacities for astrophysical applications, High Energy
Density Phys. 16, 53 (2015).
[11] R. M. More, S. B. Hansen, and T. Nagayama, Opacity
from two-photon processes, High Energy Density Phys.
24, 44 (2017).
[12] J.-C. Pain, A note on the contribution of multi-photon
processes to radiative opacity, High Energy Density Phys.
26, 23 (2018).
[13] M. Krief, Y. Kurzweil, A. Feigel, and D. Gazit, The effect
of ionic correlations on radiative properties in the solar
interior and terrestrial experiments, Astrophys. J. 856,
135 (2018).
[14] J. Zeng, C. Gao, P. Liu, Y. Li, C. Meng, Y. Hou, D.
Kang, and J. Yuan, Electron localization enhanced pho-
ton absorption for the missing opacity in solar interior,
Sci. China Phys. Mech. Astron. 65, 233011 (2022).
[15] J. Colgan, D. P. Kilcrease, N. Magee, M. E. Sherrill, J.
Abdallah Jr, P. Hakel, C. J. Fontes, J. A. Guzik, and K.
Mussack, A new generation of Los Alamos opacity tables,
Astrophys. J. 817, 116 (2016).
[16] C. A. Iglesias and S. B. Hansen, Fe XVII opacity at solar
interior conditions, Astrophys. J. 835, 284 (2017).
[17] S. N. Nahar and A. K. Pradhan, Large enhancement
in high-energy photoionization of Fe XVII and missing
continuum plasma opacity, Phys. Rev. Lett. 116, 235003
(2016).
[18] F. Zhou, Y. Qu, J. Gao, Y. Ma, Y. Wu, and J. Wang,
Atomic-state-dependent screening model for hot and
warm dense plasmas, Commun. Phys. 4, 148 (2021).
[19] B. F. Rozsnyai, Equation of state calculations based on
the self-consistent ion-sphere and ion-correlation average
atom models, High Energy Density Phys. 10, 16 (2014).
[20] C. Wu, F. Zhou, J. Yan, X. Gao, Y. Wu, C. Zeng,
and J. Wang, Ionization potential depression model for
warm/hot and dense plasmas, Chin. Phys. Lett. 41,
085202 (2024).
[21] M. F. Gu, The flexible atomic code, Can. J. Phys. 86,
675 (2008).
[22] C.-Y. Li, X.-Y. Han, J.-G. Wang, and Y.-Z. Qu, Rela-
tivistic R-matrix studies of photoionization processes of
Ar5+, Chin. Phys. B 22, 123201 (2013).


## Page 7

Supplemental material
I. Effect of the Mg subtraction on the inferred Fe opacity
The Fe opacity reported by Bailey et al. [1] was inferred from transmission measurements through mixed
Fe/Mg samples, the measured optical depth of which is
𝜏meas
Fe+Mg(𝐸) = ΣFe𝜅Fe(𝐸) + ΣMg𝜅Mg(𝐸).
(S1)
Here, 𝐸is the photon energy, 𝜏meas
Fe+Mg is the measured optical depth of the mixed Fe/Mg sample, ΣFe and ΣMg
are the Fe and Mg areal mass densities, and 𝜅Fe and 𝜅Mg are the Fe and Mg opacities. The Fe opacity inferred
from the mixed sample is given by
𝜅inf
Fe (𝐸) =
𝜏meas
Fe+Mg(𝐸) −ΣMg𝜅ref
Mg(𝐸)
ΣFe
,
(S2)
where 𝜅inf
Fe is the inferred Fe opacity and 𝜅ref
Mg is the calculated Mg opacity from the PrismSPECT model used
in Ref. [1]. If the calculated Mg opacity is underestimated, a residual Mg contribution persists in the inferred
Fe opacity derived from the experimental work [1]. Since plasma screening significantly affects the calculated
Fe opacity and transmission as discussed in the main text, the corresponding effect on the Mg opacity must
also be further examined.
Figure S2. Comparison of Mg opacity obtained with different methods. The orange solid curve is the present Mg
opacity at 𝑇𝑒= 182 eV and 𝑛𝑒= 3.1 × 1022 cm−3. The blue and green solid curves show the impact of changing plasma
conditions, with 𝑇𝑒increased by 3% and 𝑛𝑒varied by −25% and +25%. The black dotted curve is the PrismSPECT Mg
opacity from Ref. [1]. The colored dashed lines represent the differences in Mg opacity between the present calculations
and the PrismSPECT results, which are approximately linear corrections.
Figure S2 compares the Mg opacity used for the subtraction in Ref. [1] with our Mg calculations including
configuration interaction and plasma-screening effects. In the bound-free region, the present Mg opacity
1


## Page 8

is found to be systematically higher than the PrismSPECT Mg opacity due to the plasma-screening effect.
In order to reduce the interference from resonance peaks, we approximate the Mg opacity difference
Δ𝜅Mg(𝐸) = 𝜅present
Mg
(𝐸) −𝜅ref
Mg(𝐸) using a linear interpolation between its values in the bound-free region,
taken at 1506 and 1760 eV. Here, Δ𝜅lin
Mg represents the linear interpolation of the Mg opacity difference and is
given by
Δ𝜅lin
Mg(𝐸) = Δ𝜅Mg(1506 eV) + Δ𝜅Mg(1760 eV) −Δ𝜅Mg(1506 eV)
1760 −1506
(𝐸−1506).
(S3)
From Eq. (S2), the above Mg correction to the Fe opacity is defined as
Δ𝜅corr
Fe (𝐸) = 𝜂Δ𝜅lin
Mg(𝐸),
𝜂≡ΣMg
ΣFe
.
(S4)
Here, ΣMg and ΣFe are the areal mass densities of Mg and Fe in the mixed sample, respectively.
For comparison, we use the atomic areal densities for Z2624, as given in Extended Data Fig. 2d of Ref. [1],
which are 𝑁Fe = 0.926 × 1018 cm−2 and 𝑁Mg = 1.40 × 1018 cm−2. The ratio of areal mass densities is given
by
𝜂= 24.30 𝑁Mg
55.85 𝑁Fe
= 0.658.
(S5)
Overall, the experimental Fe opacity inferred in Ref. [1] should be compared with the calculated results that
include the estimated residual Mg contribution:
𝜅calc
Fe (𝐸) + Δ𝜅corr
Fe (𝐸) = 𝜅calc
Fe (𝐸) + 𝜂Δ𝜅lin
Mg(𝐸).
(S6)
Figure S3. Effect of the estimated residual Mg contribution on the Fe opacity. Dashed curves show the original Fe
calculations, and solid curves are obtained by adding the areal-density-scaled residual Mg contribution. The black curve
is the experimental Fe opacity inferred from Ref. [1], and the red curve is the OP opacity [2].
Figure S3 shows the effect of the estimated residual Mg contribution on the Fe opacity. The dashed curves are
the original Fe opacity calculations, whereas the solid curves include the correction Δ𝜅corr
Fe (𝐸) = 𝜂Δ𝜅lin
Mg(𝐸).
2


## Page 9

The correction significantly affects the opacity in the high-energy bound-free region, where the Mg opacity
used in the original subtraction is lower than that from the present calculation.
For the Cr and Ni opacity measurements, the corresponding Mg areal densities are unavailable, and the
theoretical Mg opacity used in the experimental subtraction was not reported. Moreover, the Cr and Ni opacity
data were obtained primarily at sample areal densities of approximately 3 × 1018 cm−2 [2], roughly three
times higher than the Fe areal density discussed above. Since the Mg-subtraction error on the inferred opacity
of element X scales as ΣMg/ΣX, the associated uncertainty should be significantly smaller for Cr and Ni than
for Fe. Therefore, no similar correction was applied to the Cr and Ni opacities presented in the main text.
References
[1] J. E. Bailey et al., “A higher-than-predicted measurement of iron opacity at solar interior temperatures,”
Nature 517, 56 (2015).
[2] T. Nagayama et al., “Systematic study of L-shell opacity at stellar interior temperatures,” Phys. Rev. Lett.
122, 235001 (2019).
3

