# Nagayama2019a_Systematic study of L-shell opacity at stellar interior temperatures

- Source: `Nagayama2019a_Systematic study of L-shell opacity at stellar interior temperatures.pdf`
- Pages: 9

## Page 1

This is the accepted manuscript made available via CHORUS. The article has been
published as:
Systematic Study of L-Shell Opacity at Stellar Interior
Temperatures
T. Nagayama, J. E. Bailey, G. P. Loisel, G. S. Dunham, G. A. Rochau, C. Blancard, J. Colgan,
Ph. Cossé, G. Faussurier, C. J. Fontes, F. Gilleron, S. B. Hansen, C. A. Iglesias, I. E. Golovkin,
D. P. Kilcrease, J. J. MacFarlane, R. C. Mancini, R. M. More, C. Orban, J.-C. Pain, M. E. Sherrill,
and B. G. Wilson
Phys. Rev. Lett. 122, 235001 — Published 10 June 2019
DOI: 10.1103/PhysRevLett.122.235001


## Page 2

Systematic study of L-shell opacity at stellar interior temperatures 
 
T. Nagayama1, J. E. Bailey1, G. P. Loisel1, G. S. Dunham1, G. A. Rochau1, C. Blancard2, J. Colgan3,  
Ph. Cossé2, G. Faussurier2, C. J. Fontes3, F. Gilleron2, S. B. Hansen1, C. A. Iglesias4,  
I. E. Golovkin5, D. P. Kilcrease3, J. J. MacFarlane5, R.C. Mancini6, R. M. More*,1, C. Orban7, J.-C. Pain2, 
M.E. Sherrill3, and B.G. Wilson4 
 
1Sandia National Laboratories, Albuquerque, New Mexico 
2CEA, DAM, DIF, F-91297 Arpajon, France 
3Los Alamos National Laboratory, Los Alamos, New Mexico 
4Lawrence Livermore National Laboratory, Livermore, California 
5Prism Computational Sciences, Madison, Wisconsin 
6University of Nevada, Reno, Nevada 
7Ohio State University, Columbus, Ohio 
*Retired from the National Institute for Fusion Science, Toki, Gifu, Japan 
 
The first systematic study of opacity dependence on atomic number at stellar interior temperatures is used to 
evaluate discrepancies between measured and modeled iron opacity [J. E. Bailey et al, Nature 517, 56 (2015)]. High-
temperature (>180 eV) chromium and nickel opacities are measured with േ6-10% uncertainty, using the same 
methods employed in the previous iron experiments. The 10-20% experiment reproducibility demonstrates 
experiment reliability. The overall model-data disagreements are smaller than for iron. However, the systematic 
study reveals shortcomings in models for density effects, excited states, and open L-shell configurations. The 30-
45% underestimate in the modeled short-wavelength quasi-continuum opacity was observed only from iron and only 
at temperature above 180 eV. Thus, either opacity theories are missing physics that has non-monotonic dependence 
on the number of bound electrons, or there is an experimental flaw unique to the iron measurement at temperatures 
above 180 eV.   
 
Opacities quantify photon absorption in matter and 
are important for high-energy-density (HED) plasma 
simulations. HED plasma opacity is challenging to 
calculate and to experimentally validate. Due to lack of 
benchmark experiments, opacity-calculation accuracy has 
sometimes been suspected as a source of disagreement 
between astronomy observations and models. For 
example, in 1982 Simon requested [1] re-examination of 
opacity calculations for Cepheid variable stars. In 
response, new models were developed [2-6] that raised 
calculated opacities by ~3x for stellar envelopes and 
resolved the Cepheid variable problem. This precedent, 
combined with insufficient laboratory experiments to fully 
test theory, has led to continued speculation that models 
may underestimate opacity for variable stars [7-9].   
Recently, inaccuracy of calculated solar interior 
opacity was proposed as a potential explanation for 
disagreement between solar models and helioseismology 
[10,11]. The opacity at electron temperature ܶ௘ ~ 182 eV 
(2.11 ൈ10଺ ܭ) and density ݊
௘ ~ 9 ൈ10ଶଶ cmିଷ that exist 
near the solar convective and radiative zone boundary 
(CZB) is especially important. To test this hypothesis, 
frequency-resolved iron opacity was measured at ܶ
௘ൌ155-195 eV and ݊
௘ൌሺ7 െ40ሻൈ10ଶଵ cmିଷ [12,13] 
(hereafter BNLR15). The modeled and measured Fe 
opacities agreed reasonably well at the lowest ܶ௘ and ݊
௘, 
but models under-predict the opacity in several ways as ܶ௘ 
and ݊
௘ approach CZB conditions.  First, the calculated 
quasi-continuum opacity below 9Å is 30-45% lower than 
measured. 
Second, 
calculated 
bound-bound 
(BB) 
transitions appear stronger and narrower than the 
measurements. Third, opacity valleys (windows) are lower 
in the calculations. All three discrepancies contribute to 
lower 
calculated 
Rosseland-mean 
opacity. 
If 
the 
measurements are correct, this explains roughly half the 
opacity increase needed to resolve the solar problem. 
However, solving the solar problem ultimately relies on 
benchmarked opacity models. The required opacities for a 
wide range of elements and conditions cannot be provided 
by measurements alone. The goal of the work described 
here is testing hypotheses for the model-data discrepancy.     
Hypotheses for the source(s) of the discrepancies fall 
into two categories: i) there are undetected flaws in the 
experimental method and/or ii) photon absorption in HED 
matter is more complex than previously believed. Neither 
possibility can be ruled out until experiment and theory 
are reconciled. Experimental [11,14-18] and theoretical 
investigations [19-24] done up to now have not resolved 
the discrepancy.  
Systematic opacity measurements across atomic 
number are a powerful way to address this problem. The 
experiment drives different elements to roughly the same ܶ
௘ and ݊
௘, but the atom’s response to the conditions varies 
according to the nuclear binding energy. For example, in  
nickel (Ni:Z=28), electrons are more tightly bound, more 
difficult to ionize and excite than for iron (Fe:Z=26). 
Thus, the dominant charge state for Ni is the closed-shell 
Ne-like configuration [Fig. 1(c)]. In the closed-shell 


## Page 3

configurations, 
angular 
momentum 
coupling 
is 
appreciably simplified, theory is considered relatively 
accurate, and opacity is dominated by strong isolated lines. 
In contrast, as the atomic number is lowered to Fe or to 
chromium (Cr:Z=24), the dominant charge states shift to 
open-shell F-like and N-like ions, respectively. These 
open-shell ions are computationally more challenging and 
increase opacity complexity. Furthermore, bound-electron 
wavefunctions of lower-Z elements extend farther from 
the nucleus and are more easily perturbed by plasma 
particles. Thus, measuring opacities of Cr, Fe, and Ni not 
only provides more data to test the experimental platform, 
but can also help identify possible opacity-model 
revisions. The value of systematic opacity studies has been 
recognized for two decades [25,26], but previous 
experiments were at lower ܶ௘ and ݊
௘ and did not satisfy 
benchmark-experiment criteria such as independent 
plasma diagnostics and reproducibility. 
In this letter we describe the first systematic  
benchmark opacity experiments as a function of atomic 
number, at stellar interior temperatures. Cr and Ni 
frequency-resolved opacities were measured. Analysis of 
co-mixed Mg spectra confirmed that ܶ௘ and ݊
௘ are nearly 
the same as those of Fe. Opacities are reproduced within 
10-20% from repeated experiments with varied sample 
thicknesses. Averaging opacity spectra over multiple 
experiments reduces the uncertainty down to േ6% for Cr 
and േ10% for Ni. High reproducibility reflects smallness 
of experiment-to-experiment errors and demonstrates 
experiment-method reliability. 
Furthermore, the data reveal intriguing atomic-
number-dependent disagreements between data and 
models, which suggest three distinct opacity-model 
refinements. First, the opacity window disagreement is 
observed from Cr and Fe, but not from Ni. This suggests a 
calculational challenge for open L-shell configurations. 
Second, apparent line-shape disagreements in all three 
elements suggest insufficient understanding of atomic 
interaction with plasma environment and/or the treatment 
of excited states. Third, the modeled quasi-continuum 
opacity at short wavelength agrees with Cr and Ni 
measurements, in contrast to the Fe result. The Fe data use 
the same experimental method and should be as reliable as 
Cr and Ni. Also, Fe models agreed with lower ܶ
௘/݊
௘ measurements. Thus, these Cr, Fe, and Ni quasi-
continuum results suggest either models are missing 
opacity that becomes important at specific conditions that 
the high ܶ
௘/݊
௘ Fe experiments satisfied, or there is an 
undetected systematic flaw unique to Fe experiments at 
high ܶ௘/݊
௘.  
Opacity experimental technique has evolved and 
improved over 30 years [25,27-37]. Typically, frequency-
dependent opacity is inferred by measuring transmission 
through a heated sample. The sample transmission ܶఔ and 
opacity ߢఔ are related to the source ܫ଴ (backlight) and 
measured spectra ܫఔ:  ܶ
ఔൌܫఔ/ܫ଴ൌ݁ି
఑ഌఘ௅ 
where ߩܮ is the sample areal density.  
The 
measurement 
requirements 
are 
extensive 
[11,18,32]: (1) The sample is uniformly heated to 
conditions of interest, achieving local-thermodynamic 
equilibrium.  (2) Spectra (ܫ଴ and ܫఔ) and sample areal 
density ߩܮ need to be accurately measured. (3) The 
instrumental spectral resolving power has to be 
sufficiently high and accurately measured. (4) Backlight 
radiation and tamper transmission must be free of short-
scale wavelength-dependent structure. (5) Impact of 
plasma self-emission must be minimized. (6) Tamper-
transmission difference [18] must be minimized. (7) 
Sample temperature, density, and drive radiation must be 
independently diagnosed. (8) Measurements must be 
repeated with multiple sample thicknesses to ensure 
accurate opacity measurements over a wide dynamic 
range.  
The Sandia National Laboratories Z opacity platform 
(Fig. 1(a) ) has been developed over the last decade to 
meet these criteria [11,12,14,15,38].  The semicircular 
half-moon sample (i.e., Fe, Cr, or Ni comixed with Mg) is 
sandwiched between circular low-opacity (CH and/or Be) 
tamping materials [tamper, Fig. 1(b)]. The sample areal 
density is measured using Rutherford-Backscattering 
Spectroscopy (RBS) within േ4% error. The sample is 
volumetrically heated by energetic photons from the Z 
radiation source [34] to achieve uniform, near-equilibrium 
conditions. At stagnation, the source provides spectrally 
smooth 350-eV Planckian-like backlight radiation, which 
overwhelms the 180-eV plasma emission.  The sample-
attenuated backlight radiation is measured by multiple, 
slit-imaged, crystal spectrometers fielded along 0ל and 
േ9ל [39] with respect to the sample normal. Each 
spectrometer records multiple spectrally- and spatially-
resolved images with high signal-to-noise ratio (S/N). 
Thus, each experiment simultaneously records 16 to 36 
spectral images that further improves S/N and reduces 
instrument artifacts. The setup provides sample-attenuated 
(ܫఔ at ൅9ל) and unattenuated (ܫ଴ at െ9ל) spectra in each 
experiment.  
Continuous investigations since BNLR15 support the 
experiment reliability. The impact of temporal/spatial 
gradients, sample/tamper self-emission, and potential 
difference in tamper transmission at the tamper-only side 
and opacity-sample-embedded side were numerically 
investigated and found to be negligible [18]. Uncertainties 
in the inferred ܶ௘ and ݊
௘ due to the choice of analysis 
model have minor impact on the reported model-data 
disagreements [16]. The validity of the assumed 1-D 
expansion and the accuracy of RBS areal-density 
measurements were confirmed by good agreement of the 
Mg areal density inferred from Mg spectroscopy and that 
of the RBS measurement. 
For further constraints, we performed and repeated six 
Cr and five Ni opacity experiments with varied sample 


## Page 4

thicknesses. The Cr data include four experiments with 
3.2 ൈ10ଵ଼ and two with 1.8 ൈ10ଵ଼ Cr/cmଶ. The Ni data 
include two experiments with 0.403 ൈ10ଵ଼, and one each 
with 1.19 ൈ10ଵ଼, 2.30 ൈ10ଵ଼, and 3.74 ൈ10ଵ଼ Ni/cmଶ. 
Plasma conditions inferred from Mg spectroscopy [14] 
were ܶ
௘ൌ181 േ6 ሺ3%ሻ eV and ݊
௘ൌሺ2.9 േ0.1ሻൈ
10ଶଶ ሺ3%ሻ cmିଷ for Cr  and ܶ௘ൌ187 േ6 ሺ3%ሻ eV and ݊
௘ൌሺ2.9 േ0.3ሻൈ10ଶଶ ሺ10%ሻ cmିଷ for Ni.  
Checking reproducibility from different sample 
thicknesses is critical for i) assessing the accuracy of 
analysis method and ii) confirming reliability of the 
experimental 
method. Opacity 
is 
most 
accurately 
measured when transmission falls in the 0.15-0.85 range 
[18]. The opacity determination depends on accuracy of 
transmission determination, background subtraction, and 
sample areal density in non-linear ways. Fortunately, these 
uncertainties affect the inferred opacity differently. Their 
impact depends strongly on the transmission values and 
thus on the sample thickness. For example, the impact of 
the background subtraction error (or transmission 
determination error) on the opacity error depends on the 
areal density. Thus, any significant systematic errors in 
those could be identified through thickness-dependence of 
measured opacity.  
Opacity is determined [11,12,13 (supplemental)], 
including formal propagation of the three uncertainties. 
Transmission uncertainty is analytically determined from 
calibration-shot statistics that are collected over a decade. 
Areal density is known within േ4% based on the RBS 
measurement and Mg spectroscopy. Line-saturation 
dependence on backlight brightness suggests a 10േ3% 
background exists. The expected opacity values and its 
uncertainties are determined at every wavelength by 
propagating 
these 
uncertainties 
using 
Monte-Carlo 
methods. Opacities inferred from repeated experiments 
agree within the inferred uncertainties, supporting the 
validity of the analysis and uncertainty values.  
Furthermore, the small variation in experiment-to-
experiment inferred opacity (Fig. 2) reflects the smallness 
of some systematic errors and all random errors. The 
excellent 
reproducibility 
supports 
the 
experiment 
reliability.  
The opacity model OP is widely available and 
extensively 
used 
for 
solar/stellar 
models 
[40]. 
Comparisons between OP and the opacity measurements 
(Fig. 3) provide essential clues for model refinements. 
Over the measured spectral range, opacity is believed to be 
mostly contributed by bound-bound (BB) transitions 
(ߢఔ
஻஻ן Σ௟݊
௟݂௟௨߶௟௨ሺߥሻ) at long wavelengths and bound-
free (BF) transitions ( ߢఔ
஻ிן Σ௟݊
௟ߪ௟௨ሺߥሻ) at short 
wavelengths.  ݊
௟ is a lower state population; ݂
௟௨ and 
߶௟௨ሺߥሻ are the BB-transition oscillator strength and area-
normalized spectral line shape from lower ݈ to upper ݑ 
states; ߪ௟௨ is the photoionization cross-section from a state ݈
 to an ionized state ݑ. Atomic data calculations affect ݂௟௨, 
ߪ௟௨, and BB line locations; population calculations affect ݊
௟; density can affect all of these parameters, but 
especially ߶௟௨ሺߥሻ. 
The OP calculation disagrees with measured BB line 
locations for all three elements, revealing fundamental 
deficiency in the OP atomic structure. The atomic 
structure is the basis for accurate calculation of ݂௟௨, ߪ௟௨, ݊
௟, and ߶௟௨ሺߥሻ, and its deficiency can impact the overall 
opacity-calculation accuracy.  
While OP opacity (Fig. 3) is widely used by 
astrophysicists due to its accessibility, other opacity 
models can generate opacities with a more complete set of 
atomic levels [21,41]. Selected comparisons (Fig. 4) over 
the BB and window regions with ATOMIC [19], OPAS 
[42], SCO-RCG [43], SCRAM [44], and TOPAZ [45] 
show that all these models predict the BB transition 
energies more accurately than OP. A couple of these 
models are beginning to be used for detailed solar 
structure calculations [19,46-51] though their codes are 
not publicly available. This large collection of models that 
employ diverse physics approaches can help to identify 
which physical approximations are most accurate. 
 The opacity window disagreement trend (Fig. 4, 
black arrows) suggests that models are challenged by open 
L-shell configurations, since the disagreement is not 
observed when ions are predominantly closed shell (i.e., 
Ni) [see Fig. 1 (c)]. Inaccuracy in wavelengths, strengths, 
and widths for the multitude of weak BB transitions that 
arise in open L-shell configurations might lead to windows 
that are less filled in the model calculations than the data. 
This hypothesis can be tested by performing Ni 
experiments at higher temperature, moving the Ni plasma 
away from the closed-shell electronic configuration.  
Calculated line-shape accuracy ߶௟௨ሺߥሻ is evaluated 
with the Ne-like Ni 2p-4d line near 9.98Å. This line is 
used because it is less blended with other lines and has 
relatively low continuum underneath. The area-normalized 
line shape for this transition measured in four experiments 
was reproducible to within 10 % [Fig. 5 (a)]. The two 
thick-sample measurements were not included in Fig. 5, 
since the lines are artificially broadened by the 
combination of the high line-center optical depth, line 
saturation, and finite instrument resolution. Figure 5(b) 
shows raw opacity calculations from four opacity models: 
ATOMIC, OPAS, SCO-RCG, and SCRAM. Some 
calculations are already after major refinements, motivated 
by preliminary model-data comparison [58]. The FWHM 
predictions from these models vary by approximately a 
factor of 2. These calculated opacities are compared with 
the measurements by first converting to transmission, 
convolving with the measured instrumental resolution, and 
then converting back to opacity. Line shapes ߶௟௨ሺߥሻ are 
extracted from the data and calculations by subtracting 
linear continuum and performing area normalization. 
While the line widths predicted by most models are 
significantly underestimated, SCO-RCG predictions agree 
well with the measured line shape [Fig. 5(c)]. A 60-90% 


## Page 5

width increase for the other models is needed to bring 
them into agreement with the data and with SCO-RCG.  
It is reasonable to expect similar width disagreements 
for other lines since models use the same method for them. 
Energy is transferred more readily in windows between 
narrow lines, and therefore narrower lines decrease the 
calculated mean opacity. In fact, almost all the lines do 
look broader in the data. However, further scrutiny is 
necessary to determine accuracy of other line shapes.  
The observed line-shape disagreement indicates 
insufficient understanding of impact collisions by dynamic 
electrons, the static-ion Stark broadening, and/or satellite 
lines from excited states. Opacity models commonly 
compute electron broadening based on the Baranger [52] 
approximation. The ion Stark effect is neglected or 
crudely approximated [53], despite a recent publication 
[24] describing its potential importance. Satellite-line 
contributions are also computed differently from one 
model to another. Investigations are underway to identify 
which aspect of line-broadening theory is responsible for 
the reported line-shape discrepancies.  
The model-data comparison (Fig. 6) over the short-
wavelength region shows that the systematically higher 
quasi-continuum opacity reported by BNLR15 is observed 
only from Fe. While this proves that the experiments are 
not always biased to measure higher-than-predicted 
continuum opacity, the question remains: Why is the 
predicted iron quasi-continuum lower than the data only 
for Fe and only at high ܶ௘/݊
௘ [12,13] ? 
Currently, there are two hypotheses for this intriguing 
finding. One is that models miss some important physics 
that becomes significant at conditions satisfied by the 
high-ܶ
௘/݊
௘ Fe experiments. The BF cross-section has 
never been experimentally validated for highly ionized 
ions. Furthermore, the quasi-continuum has significant 
contribution from billions of weak BB lines from states 
where multiple bound electrons are in excited orbitals 
simultaneously [13]. Currently, there is no consensus on 
how many multi-excited states opacity models should 
include. The disagreement could also come from some 
neglected 
processes. 
For 
example, 
preliminary 
calculations of two-photon absorption [22] suggest that 
this neglected process would substantially increase the 
absorption. Another idea for missing physics was also 
recently published [54]. Refined calculations need to 
evaluate whether these suggested contributions are 
consistent with the entire Cr, Fe, and Ni data set.  
The other hypothesis is that there is an undetected 
error in the high-ܶ௘/݊
௘ Fe-opacity result. According to 
this hypothesis, the problem must not exist in the Cr, Ni, 
or lower temperature Fe experiments since the modeled 
and measured quasi-continuum opacity agreed. This 
contradicts the assertion that the same methods were used 
for all the experiments. Nevertheless, it would be valuable 
to recheck the accuracy of BNLR15 by performing 
additional high ܶ௘/݊
௘ Fe experiments, as well as revisiting 
the data analysis.  
Ultimately, these complex results demonstrate the 
power of the systematic opacity study described here. 
Insisting that models and data should agree over a range of 
atomic numbers, temperatures, and densities is a powerful 
test for both opacity theory and experiment. This approach 
guides more accurate stellar interiors modeling and 
improved understanding of the internal structure of the 
Sun.  
The implication of our measurements is significant for 
the sun and many stars. Therefore, the measurements 
should be confirmed by independent experiments. 
However, this requires large HED facilities [55-57]. In 
addition, facility time and resources devoted must be 
sufficient to satisfy the key criteria reported here, such as 
high reproducibility and independent plasma diagnostics.  
The authors are grateful to the Z experiment team, the 
management team, and the target fabrication teams at 
General Atomics and Los Alamos National Laboratories 
for their hard work and generous support. Sandia National 
Laboratories is a multi-mission laboratory managed and 
operated by National Technology and Engineering 
Solutions of Sandia, LLC., a wholly owned subsidiary of 
Honeywell International, Inc., for the U.S. Department of 
Energy’s National Nuclear Security Administration under 
Contract No. DE-NA-0003525. This paper describes 
objective technical results and analysis. Any subjective 
views or opinions that might be expressed in the paper do 
not necessarily represent the views of the U.S. Department 
of Energy or the United States Government. Los Alamos 
National 
Laboratory 
is 
operated 
by Triad National 
Security, LLC, for the National Nuclear Security 
Administration of U.S. Department of Energy (Contract 
No. 89233218CNA000001). 
 
 
[1] 
N. R. Simon, Astrophys. J. 260, L87 (1982). 
[2] 
C. A. Iglesias, F. J. Rogers, and B. G. Wilson, 
Astrophys. J. 322, L45 (1987). 
[3] 
C. A. Iglesias, F. J. Rogers, and B. G. Wilson, 
Astrophys. J. 360, 221 (1990). 
[4] 
M. J. Seaton, Y. Yan, D. Mihalas, and A. K. 
Pradhan, Monthly Notices of the Royal 
Astronomical Society 266, 805 (1994). 
[5] 
F. J. Rogers and C. A. Iglesias, Science 263, 50 
(1994). 
[6] 
F. J. Rogers and C. A. Iglesias, Space Science 
Reviews 85, 61 (1998). 
[7] 
S. Salmon, J. Montalbán, T. Morel, A. Miglio, 
M.-A. Dupret, and A. Noels, Monthly Notices of 
the Royal Astronomical Society 422, 3460 
(2012). 
[8] 
E. Moravveji, Monthly Notices RAS Letters 455, 
L67 (2016). 


## Page 6

[9] 
A. Hui-Bon-Hoa and S. Vauclair, Astronomy 
and Astrophysics 610, L15 (2018). 
[10] 
S. Basu and H. M. Antia, Physics Reports 457, 
217 (2008). 
[11] 
J. E. Bailey, G. A. Rochau, R. C. Mancini, C. A. 
Iglesias, J. J. MacFarlane, I. E. Golovkin, C. 
Blancard, P. Cosse, and G. Faussurier, Phys. 
Plasmas 16, 058101 (2009). 
[12] 
J. E. Bailey, G. A. Rochau, C. A. Iglesias, J. J. 
Abdallah, J. J. MacFarlane, I. Golovkin, P. 
Wang, R. C. Mancini, P. W. Lake, T. C. Moore, 
M. Bump, O. Garcia, and S. Mazevet, Phys. Rev. 
Lett. 99, 265002 (2007). 
[13] 
J. E. Bailey, T. Nagayama, G. P. Loisel, G. A. 
Rochau, C. Blancard, J. Colgan, P. Cosse, G. 
Faussurier, C. J. Fontes, F. Gilleron, I. Golovkin, 
S. B. Hansen, C. A. Iglesias, D. P. Kilcrease, J. J. 
MacFarlane, R. C. Mancini, S. N. Nahar, C. 
Orban, J. C. Pain, A. K. Pradhan, M. Sherrill, 
and B. G. Wilson, Nature 517, 56 (2015). 
[14] 
T. Nagayama, J. E. Bailey, G. Loisel, S. B. 
Hansen, G. A. Rochau, R. C. Mancini, J. J. 
MacFarlane, and I. Golovkin, Phys. Plasmas 21, 
056502 (2014). 
[15] 
T. Nagayama, J. E. Bailey, G. Loisel, G. A. 
Rochau, and R. E. Falcon, Rev. Sci. Instrum. 85, 
11D603 (2014). 
[16] 
T. Nagayama, J. E. Bailey, R. C. Mancini, C. A. 
Iglesias, S. B. Hansen, C. Blancard, H. K. 
Chung, J. Colgan, P. Cosse, G. Faussurier, R. 
Florido, C. J. Fontes, F. Gilleron, I. E. Golovkin, 
D. P. Kilcrease, G. Loisel, J. J. MacFarlane, J. C. 
Pain, G. A. Rochau, M. E. Sherrill, and R. W. 
Lee, High Energ. Dens. Phys. 20, 17 (2016). 
[17] 
T. Nagayama, J. E. Bailey, G. Loisel, G. A. 
Rochau, J. J. MacFarlane, and I. Golovkin, Phys. 
Rev. E 93, 023202 (2016). 
[18] 
T. Nagayama, J. E. Bailey, G. P. Loisel, G. A. 
Rochau, J. J. MacFarlane, and I. E. Golovkin, 
Phys. Rev. E 95, 063206 (2017). 
[19] 
J. Colgan, D. P. Kilcrease, N. H. Magee, M. E. 
Sherrill, J. J. Abdallah, P. Hakel, C. J. Fontes, J. 
A. Guzik, and K. A. Mussack, Astrophys. J. 817, 
116 (2016). 
[20] 
S. N. Nahar and A. K. Pradhan, Phys. Rev. Lett. 
116, 235003 (2016). 
[21] 
C. A. Iglesias and S. B. Hansen, 835, 284 (2017). 
[22] 
R. M. More, S. B. Hansen, and T. Nagayama, 
High Energ. Dens. Phys. 24, 44 (2017). 
[23] 
D. P. Kilcrease, J. Colgan, P. Hakel, C. J. Fontes, 
and M. E. Sherrill, High Energ. Dens. Phys. 16, 
36 (2015). 
[24] 
R. C. Mancini, Journal of Physics Conference 
Series 717, 012069 (2016). 
[25] 
G. Winhart, K. Eidmann, C. Iglesias, and A. 
Bar-Shalom, Phys. Rev. E 53, R1332 (1996). 
[26] 
G. Loisel, P. Arnault, S. Bastiani Ceccotti, T. 
Blenski, T. Caillaud, J. Fariaut, W. Fölsner, F. 
Gilleron, J. C. Pain, M. Poirier, C. Reverdin, V. 
Silvert, F. Thais, S. Turck-Chieze, and B. 
Villette, 5, 173 (2009). 
[27] 
S. J. Davidson, J. M. Foster, C. C. Smith, K. A. 
Warburton, and S. J. Rose, Appl. Phys. Lett. 52, 
847 (1988). 
[28] 
T. Perry, S. Davidson, F. Serduke, D. Bach, C. 
Smith, J. Foster, R. Doyas, R. Ward, C. Iglesias, 
F. Rogers, J. Abdallah, R. Stewart, J. Kilkenny, 
and R. Lee, Phys. Rev. Lett. 67, 3784 (1991). 
[29] 
J. Foster, D. Hoarty, C. Smith, P. Rosen, S. 
Davidson, S. Rose, T. Perry, and F. Serduke, 
Phys. Rev. Lett. 67, 3255 (1991). 
[30] 
L. Da Silva, B. MacGowan, D. Kania, B. 
Hammel, C. Back, E. Hsieh, R. Doyas, C. 
Iglesias, F. Rogers, and R. Lee, Phys. Rev. Lett. 
69, 438 (1992). 
[31] 
P. Springer, D. Fields, B. Wilson, J. Nash, W. 
Goldstein, C. Iglesias, F. Rogers, J. Swenson, M. 
Chen, A. Bar-Shalom, and R. Stewart, Phys. 
Rev. Lett. 69, 3735 (1992). 
[32] 
T. Perry, P. Springer, D. Fields, D. Bach, F. 
Serduke, C. Iglesias, F. Rogers, J. Nash, M. 
Chen, B. Wilson, W. Goldstein, B. Rozsynai, R. 
Ward, J. Kilkenny, R. Doyas, L. Da Silva, C. 
Back, R. Cauble, S. Davidson, J. Foster, C. 
Smith, A. Bar-Shalom, and R. Lee, Phys. Rev. E 
54, 5617 (1996). 
[33] 
P. T. Springer, K. L. Wong, C. A. Iglesias, J. H. 
Hammer, J. L. Porter, A. Toor, W. H. Goldstein, 
B. G. Wilson, F. J. Rogers, C. Deeney, D. S. 
Dearborn, C. Bruns, J. Emig, and R. E. Stewart, 
J. Quant. Spectrosc. Radiat. Transfer 58, 927 
(1997). 
[34] 
C. Chenais Popovics, H. Merdji, T. Missalla, F. 
Gilleron, J. C. Gauthier, T. Blenski, F. Perrot, M. 
Klapisch, C. Bauche-Arnoult, J. Bauche, A. 
Bachelier, and K. Eidmann, Astrophys. J. Suppl. 
Ser. 127, 275 (2000). 
[35] 
C. Chenais-Popovics, M. Fajardo, F. Gilleron, U. 
Teubner, J. C. Gauthier, C. Bauche-Arnoult, A. 
Bachelier, J. Bauche, T. Blenski, F. Thais, F. 
Perrot, A. Benuzzi, S. Turck-Chieze, J. P. 
Chièze, F. Dorchies, U. Andiel, W. Foelsner, 
and K. Eidmann, Phys. Rev. E 65, 016413 
(2001). 
[36] 
J. E. Bailey, P. Arnault, T. Blenski, G. Dejonghe, 
O. Peyrusse, J. J. MacFarlane, R. C. Mancini, M. 
E. Cuneo, D. S. Nielsen, and G. A. Rochau, J. 
Quant. Spectrosc. Radiat. Transfer 81, 31 (2003). 
[37] 
P. Renaudin, C. Blancard, J. Bruneau, G. 
Faussurier, J. E. Fuchs, and S. Gary, J. Quant. 
Spectrosc. Radiat. Transfer 99, 511 (2006). 


## Page 7

[38] 
J. E. Bailey, G. A. Rochau, R. C. Mancini, C. A. 
Iglesias, J. J. MacFarlane, I. E. Golovkin, J. C. 
Pain, F. Gilleron, C. Blancard, P. Cosse, G. 
Faussurier, G. A. Chandler, T. J. Nash, D. S. 
Nielsen, and P. W. Lake, Rev. Sci. Instrum. 79, 
113104 (2008). 
[39] 
G. Loisel, J. E. Bailey, G. A. Rochau, G. S. 
Dunham, L. B. Nielsen-Weber, and C. R. Ball, 
Rev. Sci. Instrum. 83, 10E133 (2012). 
[40] 
A. M. Serenelli, Astrophysics and Space Science 
328, 13 (2009). 
[41] 
C. Blancard, J. Colgan, P. Cosse, G. Faussurier, 
C. J. Fontes, F. Gilleron, I. Golovkin, S. B. 
Hansen, C. A. Iglesias, D. P. Kilcrease, J. J. 
MacFarlane, R. M. More, J. C. Pain, M. Sherrill, 
and B. G. Wilson, Phys. Rev. Lett. 117, 249501 
(2016). 
[42] 
C. Blancard, P. Cossé, and G. Faussurier, 
Astrophys. J. 745, 10 (2012). 
[43] 
J.-C. Pain and F. Gilleron, High Energ. Dens. 
Phys. 15, 30 (2015). 
[44] 
S. Hansen, J. Bauche, C. Bauche-Arnoult, and 
M. F. Gu, High Energ. Dens. Phys. 3, 109 
(2007). 
[45] 
C. A. Iglesias, 15, 4 (2015). 
[46] 
G. Mondet, C. Blancard, P. Cossé, and G. 
Faussurier, Astrophys. J. Suppl. Ser. 220, 2 
(2015). 
[47] 
M. Le Pennec, S. Turck-Chieze, S. Salmon, C. 
Blancard, P. Cossé, G. Faussurier, and G. 
Mondet, Astrophys. J. 813, L42 (2015). 
[48] 
P. Walczak, C. J. Fontes, J. Colgan, D. P. 
Kilcrease, and J. A. Guzik, Astronomy and 
Astrophysics 580, L9 (2015). 
[49] 
J. Daszyńska-Daszkiewicz, A. A. Pamyatnykh, 
P. Walczak, J. Colgan, C. J. Fontes, and D. P. 
Kilcrease, Monthly Notices of the Royal 
Astronomical Society 466, 2284 (2017). 
[50] 
G. Buldgen, S. J. A. J. Salmon, M. Godart, A. 
Noels, R. Scuflaire, M.-A. Dupret, D. R. Reese, 
J. Colgan, C. J. Fontes, P. Eggenberger, P. Hakel, 
D. P. Kilcrease, and O. Richard, Monthly 
Notices RAS Letters 472, L70 (2017). 
[51] 
G. Buldgen, S. J. A. J. Salmon, A. Noels, R. 
Scuflaire, D. R. Reese, M.-A. Dupret, J. Colgan, 
C. J. Fontes, P. Eggenberger, P. Hakel, D. P. 
Kilcrease, and S. Turck-Chieze, Astronomy and 
Astrophysics 607, A58 (2017). 
[52] 
M. Baranger, Phys. Rev. 112, 855 (1958). 
[53] 
B. F. Rozsnyai, J. Quant. Spectrosc. Radiat. 
Transfer 17, 77 (1977). 
[54] 
P. Liu, C. Gao, Y. Hou, J. Zeng, and J. Yuan, 
Communications Physics 2018 1:1 1, 95 (2018). 
[55] 
E. M. Campbell and W. J. Hogan, Plasma Phys. 
Control. Fusion 41, B39 (1999). 
[56] 
J.-L. Miquel, C. Lion, and P. Vivini, Journal of 
Physics Conference Series 688, 012067 (2016). 
[57] 
N. W. Hopps, T. H. Bett, N. Cann, C. N. Danson, 
S. J. Duffield, D. A. Egan, S. P. Elsmere, M. T. 
Girling, E. J. Harvey, D. I. Hillier, D. J. Hoarty, 
P. M. R. Jinks, M. J. Norman, S. J. F. Parker, P. 
A. Treadwell, and D. N. Winter, in High Power 
Lasers for Fusion Research, edited by A. A. S. 
Awwal, A. M. Dunne, H. Azechi, and B. E. 
Kruschwitz (International Society for Optics and 
Photonics, 2011), p. 79160C. 
 [58] 
T. Nagayama, J. E. Bailey, C. Blancard, J. 
Colgan, Ph. Cossé, G. Faussurier, C. J. Fontes, 
F. Gilleron, S. B. Hansen, C. A. Iglesias, D. P. 
Kilcrease, J. -C. Pain, M. E. Sherrill, B. G. 
Wilson (private communication) 
 
 
 


## Page 8

FIG 1. (color) (a) Opacity-experiment setup. (b) Target side view. (c) Dominant electron configurations of Cr, Fe, and Ni at 
achieved conditions. Vacancies in the shells are indicated by open circles. 
 
 
FIG 2. (color) Reproducibility in measured opacities for (a) Cr and (b) Ni. Each color corresponds to independent 
experiments with their sample areal densities (cm2/g) embedded in the figure.  
 
 
FIG 3. (color) Comparison of OP opacity (red) and measured opacity (black) approximately at 180 eV and 3 ൈ10ଶଶ cmିଷ 
for (a) Cr, (b) Fe, and (c) Ni. Fe data and calculation are adopted from Fig. 3 of BNLR15. Opacities over 9.1-9.3 Å depend 
on the accuracy of Mg He-α removal and are not shown here. Wavelength upper limit is determined by the onset of strong 
lines from n=2Æ3 transitions, which are still under investigation.  
 


## Page 9

 
FIG 4. (color) Blow-up comparison of measured (black) and modeled (colored) opacities for (a) Cr, (b) Fe, and (c) Ni over 
the window and 2p-4d bound-bound lines. While only two models are compared in each plot for clarity, the level of 
disagreement is similar for all models.  The opacity-window (black arrows) disagreement is not observed for Ni, potentially 
due to closed-L-shell configuration.  
 
 
 
FIG 5. (color) (a) Reproducibility in Ne-like Ni 2p-4d line shapes (b) Model-dependent variation of calculated Ne-like Ni 
2p-4d line opacity (without instrument-broadening effects). (c) comparisons of measured (black) and modeled (colored) line 
shapes (with instrumental transmission resolution; see text). Only the broadest one shows good agreement; other models 
require 60-90% extra broadening.  
 
 
 
FIG 6. (color) Comparison of measured (black) and modeled (colored) quasi-continuum opacities for (a) Cr, (b) Fe, and (c) 
Ni, revealing notable discrepancy only from Fe. Models: ATOMIC (green), OPAS (purple), SCO-RCG (cyan), SCRAM 
(orange), and TOPAZ (gray).  
 

