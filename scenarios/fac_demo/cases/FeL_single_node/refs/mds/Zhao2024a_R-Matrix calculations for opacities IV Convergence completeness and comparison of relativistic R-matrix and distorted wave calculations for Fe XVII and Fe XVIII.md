# Zhao2024a_R-Matrix calculations for opacities IV Convergence completeness and comparison of relativistic R-matrix and distorted wave calculations for Fe XVII and Fe XVIII

- Source: `Zhao2024a_R-Matrix calculations for opacities IV Convergence completeness and comparison of relativistic R-matrix and distorted wave calculations for Fe XVII and Fe XVIII.pdf`
- Pages: 15

## Page 1

arXiv:2308.14880v1  [astro-ph.SR]  28 Aug 2023
R-Matrix calculations for opacities: IV.:
Convergence, completeness, and comparison of
relativistic R-matrix and distorted wave calculations
for Fe xvii and Fe xviii
L Zhao1, S N Nahar1, A K Pradhan1,2,3
1 Department of Astronomy, Ohio State University, Columbus, Ohio 43210, USA
2 Biophysics Graduate Program, 3 Chemical Physics Program, The Ohio State
University, Columbus, Ohio 43210, USA
Abstract.
To investigate the completeness of coupled channel (CC) Breit-Pauli R-
Matrix (BPRM) calculations for opacities, we employ the relativistic distorted wave
(RDW) method to complement (“top-up”) and compare the BPRM photoionization
cross sections for high-nℓlevels of both Fe xvii and Fe xviii . Good agreement is
found in background photoionization cross sections using these two methods, which
also ensures correct matching of bound level cross sections for completeness. In order
to top-up the CC-BPRM calculations, bound-bound transitions involving additional
bound levels, and a large number of doubly-excited quasi-bound levels corresponding
to BPRM autoionizing resonances described in paper RMOPII, are calculated using
the RDW method. Photoionization cross sections in the high energy region are also
computed and compared up to about 500 Ry, and contributions from higher core
level excitations than BPRM are considered. The eﬀect of conﬁguration interaction is
investigated, which plays a signiﬁcant role in correctly reproducing some background
cross sections. Owing to the fact that the additional RDW levels correspond to high-nℓ
bound levels that are negligibly populated according to the Mihalas-Hummer-D¨appen
equation-of-state (paper I), the eﬀect on opacities is expected to be small.
1. Introduction
Previous papers I-III in this series (hereafter RMPP1, RMOP2, RMOP3) reported
BPRM calculations and plasma eﬀects related to iron opacity at conditions similar
to the solar radiation/convection zone boundary or the base of the convection zone
(BCZ). As outlined in paper RMOP1, opacity calculations need to consider all possible
mechanisms for photon absorption and scattering from all atomic constituents, including
all levels that might possibly contribute. Furthermore, in order to resolve discrepancies
among various theoretical models based on the DW methods that include diﬀerent sets
of transition arrays, and experimental measurements [1, 2], it is necessary to establish
convergence of the BPRM calculations and completeness of transitions considered.


## Page 2

R-Matrix calculations for opacities IV
2
Extensive CC-BPRM calculations R-Matrix (BPRM) calculations were carried
out for Fe xvii including 60 ﬁne-structure levels within the n ≤3 complexes in the
Fe xviii target ion [3], and 99 LS terms within n ≤4 (99LS-RM). They show strong
photon absorption due to core excitation, resulting in an increment of 35% in the
Rosseland mean opacity over the Opacity Project (OP) data [4]. Whereas these previous
calculations demonstrated that in the R-Matrix opacity calculations convergence of the
close-coupling expansion was a necessary condition for accuracy, completeness of all
possible excited conﬁgurations by additional contributions in the high-energy region
still remains to be ascertained [4, 5, 6]. At BCZ conditions Fe xvii , Fe xviii and
Fe xix are the three dominant iron ions. For example, at the measured iron opacity [2]
and temperature and density T=2.1 × 106 and Ne=3.1 × 1022cc, the three ionization
fractions are 0.19, 0.38 and 0.29, respectively [4].
In this paper, we consider the 218CC-BPRM calculation for Fe xvii and 276CC-
BPRM calculation for Fe xviii , as described in paper RMOP2.
The additional or
topup transitions for bound-bound and bound-free data are obtained from relativistic
distorted wave (RDW) calculations using the ﬂexible atomic code (FAC) [7]. In the
following sections, the speciﬁcations of the 218CC- and 276CC-BPRM calculations of
paper RMOP2 are summarized, followed by the top-up conﬁgurations and transitions
calculated using FAC. To ensure data correspondence from FAC, a procedure of
matching the bound levels from BPRM and FAC results is described, and the bound-
bound and bound-free top-up calculations detailed afterwards.
A key step in the matching-topup procedure is level identiﬁcation.
Unlike
atomic structure and DW calculations, BPRM calculations do not assign spectroscopic
designations a priori and bound states are obtained only as eigenvalues of the (e + ion)
Hamiltonian. As described in paper RMOP2, the code BPID (Fig. 1, RMOP-I) is used
to obtain relevant parameters and for spectroscopic identiﬁcation of levels computed in
BPRM calculations. The RDW calculations of course have a pre-assigned identiﬁcation
based on initial set of electronic conﬁgurations speciﬁed in the conﬁguration-interaction
(CI) basis.
In some instances exited level conﬁguration mixing is such that one
conﬁguration does not dominate the wavefunction expansion of a given state and
RDW and BPRM assignations do not match. It is then required to carefully examine
level parameters such as quantum defects and associated bound-bound and bound-free
transitions to ascertain matching data. Another consideration is that the precise number
of BPRM bound-state eigenvalues depends on an energy mesh or eﬀective quantum
number ν(E) obtained by ”scanning” at a ﬁne mesh with suﬃcient reﬁnement to ensure
convergence. The procedure and results are discussed in this paper.
A potentially important factor is that the close coupling approximation introduces
autoionizing resonances in photoionization cross section, which may be aﬀected by
radiative damping in highly charged H- or He-like ions, and thereby reduce eﬀective cross
sections considerably [16]. However, radiation damping occurs after photoabsorption,
and for ions such as Fe xvii and Fe xviii this eﬀect is negligible [13, 14]. Therefore,
undamped photoionization cross sections are used in opacity calculations, as reported


## Page 3

R-Matrix calculations for opacities IV
3
in paper RMOP2.
2. BPRM bound-free and bound-bound data
The current BPRM calculations for Fe xvii and Fe xviii are unprecedented in terms of
scope and magnitude of data produced and processed for opacity calculations, with the
maximum number of free channels 998 and 1288 respectively, from calculations reported
in RMOP2. For Fe xvii , 99LS-RM calculation [4] is extended to 218CC-BPRM by
including the ﬁne structure of the target states. The target conﬁgurations (1s is always
full, so omitted for brevity) included are 2s22p5, 2s2p6, 2s22p4nℓ, 2s2p5nℓ, 2p63ℓ′, where
n = 3, 4, and ℓ, ℓ′ ≤2, which have 99 LS terms, or 218 ﬁne structure levels. The
continuum orbitals included are ℓ≤9, and the number of continuum R-Matrix basis
functions included is 20. The bound states are found by scanning the eigenvalues of the
(e + ion) Hamiltonian on an eﬀective quantum number ν up to ν ≤10.1 [8]. However,
as mentioned above, unlike atomic structure calculations where electronic conﬁgurations
are speciﬁed a priori, R-matrix calculations do not provide spectroscopic spin-orbital
quantum number designations for the bound levels obtained, nor guarantee that all
possible bound levels are found within the ν-range of interest.
To resolve the ﬁrst issue, the computer program BPID [9] has been developed as
part of the RM opacity codes described in paper P1. Using the code BPID one can
identify most of the bound levels spectroscopically, albeit with a few remaining highly
mixed levels undetermined (viz. [10]). That obstacle might be overcome by comparing
some physical quantities of these levels calculated by an atomic structure code such
as SUPERSTRUCTURE [11] and FAC [7], as for example for photoionization cross
section to be described in the next section. The second issue depends on the scanning
∆−ν-mesh employed; ∆ν = 0.001 yields fewer bound levels in the 218CC-BPRM than
60CC-BPRM, so a ﬁner step 0.0001 or 0.0005 is used in the region where levels are
missing, which ﬁnally gives 464 bound levels, 10 more than 60CC-BPRM.
For the larger Fe xviii case, two sets of BPRM calculations are done with diﬀerent
target conﬁgurations.
One includes up to n = 3 target conﬁgurations, i.e.
2s22p4,
2s2p5, 2p6, 2s22p33ℓ, 2s2p43ℓ, where ℓ≤2, which yields 200 target ﬁne structure
levels. In addition to target conﬁgurations above, the other BPRM calculation includes
n = 4 conﬁgurations, i.e. 2s22p34ℓ, where ℓ≤2, which yield 276 ﬁne structure levels.
The parameters set for the continuum orbitals and basis functions are the same as for
Fe xvii 218CC-BPRM calculation. The 200CC-BPRM calculation ﬁnds 1149 bound
levels with ∆ν = 0.001, while 276CC-BPRM calculation ﬁnds 1163 bound levels with
0.001 as the initial attempt in ν-mesh, and 0.0001 or 0.0005 as the second attempt,
in the region where levels are missing compared with 200CC-BPRM. Thus we may be
conﬁdent of having converged with respect to possible number of bound levels with
BPRM calculations.
To compute iron opacities for Fe xvii and Fe xviii oscillator strengths from
the 60CC-BPRM and 200CC-BPRM calculations, and photoionization cross sections


## Page 4

R-Matrix calculations for opacities IV
4
Table 1. Selected packed levels of Fe xvii (J = 4, π = 0) and Fe xviii (J = 5/2, π = 0)
(Note: the energy is z-scaled, and in unit of 10−2Ry)
level index
60CC-BPRM
218CC-BPRM
Fe xvii
23
-1.242945
-1.239702
24
-1.239540
-1.238049
25
-1.237855
-1.236506
26
-1.236421
-1.235733
27
-1.235081
-1.235227
28
-1.234742
-1.234723
level index
200CC-BPRM
276CC-BPRM
Fe xviii
31
-3.996445
-4.004678
32
-3.993010
-4.003468
33
-3.989362
-4.000058
from the 218CC-BPRM and 276CC-BPRM calculations, are used respectively (paper
RMOP2). So in doing the FAC top-up calculations, matching the bound levels for each
BPRM calculation is necessary but complicated by the fact that they have diﬀerent
number of bound levels, especially energy regions where levels are densely packed (see
table 1) and the order of their spectroscopic designations may be mismatched and needs
to be shuﬄed (see ﬁgure 1).‡ Photoionization cross sections of 6 levels of Fe xvii are
plotted in ﬁgure 1 for 60CC-BPRM and 276CC-BPRM, and we ﬁnd distinct diﬀerence
in level 24 and 26. Similar issue arises in ﬁgure 1 of Fe xviii . Even though these levels
have similar energy, they may have distinctive conﬁgurations (see section 3.1), which is
the reason why we should redo the identiﬁcation for diﬀerent CC-BPRM calculations.
After being switched, these levels show good agreement (see ﬁgure 1).
3. Complementarity between BPRM and RDW: the top-up procedure
The Opacity Project [12] employed a small (e + ion) wavefunction expansion including
outer open Shell conﬁgurations in the close-coupling approximation and R-Matrix
method in LS-coupling to calculate non-relativistic photoionization cross sections in the
low energy region, and adopted the Kramer approximation (”tail”) to ﬁt and extend to
higher energies afterwards. In previous calculations, [13] replaced the Kramer tails with
the RDW results including the contribution from inner-shell processes. Later opacity
tables were updated by also including inner-shell transitions [15]. In this section, we
describe the procedure employed to compare and complement BPRM data with RDW
data from FAC. That requires careful matching between BPRM and FAC cross sections
for all bound levels, and detailed bound-bound and bound-free top-up calculations. We
‡ It bears emphasis that the opacities per se are independent of any spectroscopic labels; however,
they are necessary for processing the bound-bound and bound-free radiative atomic transitions, and
for comparing with other data sources.


## Page 5

R-Matrix calculations for opacities IV
5
-5
-2
1
4
23
23
-7
-4
-1
2
24
24
-4
-1
2
25
25
-7
-4
-1
2
26
26
-7
-4
-1
2
27
27
10
20
30
40
50
60
70
80
90
100
110
-7
-4
-1
2
28
28
Photon Energy (Ry)
log σPI
10
(Mb)
-5
-2
1
4
23
23
-7
-4
-1
2
26
24
-4
-1
2
25
25
-6
-3
0
3
24
26
-7
-4
-1
2
27
27
10
20
30
40
50
60
70
80
90
100
110
-7
-4
-1
2
28
28
Photon Energy (Ry)
log σPI
10
(Mb)
-6
-4
-2
0
2
4
31
31
-5
-3
-1
1
3
32
32
10
20
30
40
50
60
70
80
90
100
110
-4
-2
0
2
33
33
Photon Energy (Ry)
log σPI
10
(Mb)
-6
-4
-2
0
2
4
33
31
-5
-3
-1
1
3
32
32
10
20
30
40
50
60
70
80
90
100
110
-4
-2
0
2
31
33
Photon Energy (Ry)
log σPI
10
(Mb)
Figure 1. Photoionization cross section of 6 closely packed levels for Fe xvii and 3
levels for Fe xviii before and after being switched. 60CC-BPRM (red), 218CC-BPRM
(black); 200CC-BPRM (red), 276CC-BPRM (black)
also discuss the eﬀect of conﬁguration interaction on photoionization cross sections.
3.1. Matching
In BPRM calculations, bound levels with continuum orbitals ℓ≤9 and eﬀective
quantum number ν ≤10.1 are formed by coupling the n = 2 core states with the
continuum ν and ℓof the outer electron. So in FAC we set the bound conﬁgurations
as a permutation of the n = 2 core conﬁgurations and an outer electron with principle
quantum number n ≤10. With the same n-complex conﬁguration interaction included,
atomic structure is solved and sorted by total angular momentum J and parity π, and
ordered in energy, we ﬁnd excellent agreement in the energy between BPRM and FAC
values.
In calculating photoionization cross sections we include the whole n-complex of


## Page 6

R-Matrix calculations for opacities IV
6
core conﬁgurations for CI (hereafter CI) purpose, but only the transitions to core
conﬁgurations that are included in BPRM calculations. To delineate photoionization
cross sections at the edges of energy grid, the energy mesh is created in such a
way that within any two adjacent thresholds 10 points are uniformly assigned. The
partial photoionization cross section is the computed in the default 6 energy grids,
and interpolated/extrapolated in our mesh, and summed to give total cross sections
for each bound level.
To investigate the eﬀect of CI, two sets of RDW calculation
are carried out.
Both sets only allow the same-n-complex conﬁguration interaction
for bound conﬁgurations, but for the core conﬁgurations one of them only allows the
same-n-complex CI and the other allows diﬀerent n-complexes. We mix all the core
conﬁgurations together.
In RDW calculations, the photoionization cross section is
related to the dipole operator matrix < ψi|D|ψf >. The |ψi > involves the electron
in the bound state to the continuum and all other electrons, and must stay the same if
only same-n-complex conﬁguration interaction is allowed. It can be diﬀerent if diﬀerent-
n-complex CI is considered [7].
To match bound state levels from BPRM and RDW, it is necessary to compare
cross sections to ensure the correctness of matching.
We plot BPRM and RDW
photoionization cross sections in the order of energy for each J, π symmetry pair,
and a level is matched when the energy and the photoionization cross section agree
reasonably well (here the background of the BPRM data and RDW are compared).
Photoionization cross sections of majority of bound levels show excellent consistency at
the ﬁrst attempt (see ﬁgure 1 for Fe xvii and Fe xviii . The LS-term notation ( S and
L) can not be determined from FAC output for all levels, so only conﬁguration and total
angular momentum J are given). However, when several levels are almost degenerate
(see table 2), distinctive diﬀerences may yet occur in cross sections. Such levels need to
be switched till good matching is achieved (See ﬁgure 3 for Fe xvii and Fe xviii The
process is justiﬁed since level identiﬁcation of near-degenerate BPRM levels may not
exactly correspond in energy from diﬀerent atomic structure codes such as FAC, since
spectroscopic designations depend on CI included and coupling schemes employed for
the (e + ion) system§.
In table 2, we can see the energy levels computed in BPRM and RDW agree quite
well. For Fe xvii , levels 13 and 14 , and levels 15 and 16 lie very close to each other,
and in ﬁgure 3, levels 13 and 16 achieve good agreement, while levels 14 and 15 don’t.
So we switch the order of levels 14 and 15 in RDW calculation and recompare with good
agreement. Thus levels 13 - 16 in BPRM calculation are matched with those in RDW
calculation. The same procedure is applied to levels 65 and 66 of Fe xviii in table 2,
and the result is show in ﬁgure 3.
In ﬁgures 2 and 3, we show two sets of RDW calculation as described above, and
study the eﬀect of conﬁguration interaction on photoionization cross sections, with the
upper panel of ﬁgure 2 as an example. The dominant conﬁguration of the bound state
§ All BPRM photoionization cross sections include a small region below the lowest ionization threshold
for each level [12], where no RDW data are shown.


## Page 7

R-Matrix calculations for opacities IV
7
Table 2. Selected levels of Fe xvii (J = 3, π = 1) and Fe xviii (J = 1/2, π = 1) to be
matched (Note: the energy is z-scaled, and in unit of 10−2Ry)
level index
BPRM
RDW
Fe xvii
12
-3.670657
-3.67960
13
-2.873930
-2.84319
14
-2.868775
-2.84238
15
-2.842915
-2.83761
16
-2.835625
-2.83555
17
-2.774853
-2.77998
level index
BPRM
RDW
Fe xviii
64
-1.275887
-1.27703
65
-1.234865
-1.24175
66
-1.226084
-1.23724
67
-1.136909
-1.14691
after being matched with RDW is 2s22p54d, so with only the same-n-complex CI of core
conﬁgurations considered, the transitions can only happen to core conﬁgurations 2s22p5,
2s2p54ℓ, 2s22p44ℓand 2p64ℓ, where ℓ= s, p, d, while with diﬀerent-n-complex CI of core
conﬁgurations additional contribution can be from all other core conﬁgurations. From
the upper panel of ﬁgure 2 we can see that the same-n-complex conﬁguration interaction
gives reasonably good background, though with some big gaps, while diﬀerent-n-complex
CI ﬁlls up the big gap and improves the background signiﬁcantly. Similar phenomenon
can be found in the rest of the ﬁgures 2 and 3, and there are still some gaps remaining
after diﬀerent-n-complex CI is allowed∥
3.2. Bound-free data
As BPRM calculations are carried out in the lower part of the whole energy range, they
include low-nℓcore conﬁgurations with n ≤4. We use the RDW method to extend it
to higher regions up to 500 Ry in photoelectron energy, and to include higher-nℓcore
conﬁgurations n = 5, 6. The following part of this section gives detailed description of
these aspects.
3.2.1. High energy cross sections
As shown in ﬁgure 2, the RDW data can be matched
almost perfectly to background BPRM cross sections. However, we also ﬁnd there are
cases where they don’t match well in the right region of energy (see ﬁgure 4). In the
top panels diﬀerent-n CI introduces many transitions, but they are not strong enough
to raise to the background of BPRM. In the middle panel of ﬁgure 4, diﬀerent-n CI
introduces many edges at positions where the background of BPRM jumps, and raises
∥In ﬁgure 2 and 3, the oscillation in the background of the BPRM data can be eliminated with a
larger number of continuum basis functions [13].


## Page 8

R-Matrix calculations for opacities IV
8
-4
-2
0
2
4
218CC BPRM
RDW (same-n CI)
RDW (different-n CI)
0
20
40
60
80
100
120
-7
-4
-1
2
5
218CC BPRM
RDW (same-n CI)
RDW (different-n CI)
2s2 2p5 4d (J =2)
2s2 2p5 5g (J =3)
log
σPI
10 (Mb)
Photon Energy (Ry)
-4
-3
-2
-1
0
1
2
3
276CC BPRM
RDW (same-n CI)
RDW (different-n CI)
0
20
40
60
80
100
120
-8
-6
-4
-2
0
2
276CC BPRM
RDW (same-n CI)
RDW (different-n CI)
2s2 2p4 4d (J =5/2)
2s2 2p4 6h (J =7/2)
log
σPI
10 (Mb)
Photon Energy (Ry)
Figure 2.
Most of the levels are matched at the ﬁrst attempt with excellent
consistency in photoionization cross section. The conﬁguration is attached with each
level. BPRM (black), RDW(blue and red). “Same-n CI” means only same-n-complex
CI is considered for core conﬁgurations, and “diﬀerent-n CI” refers to both same-n-
and diﬀerent-n-complex CI is considered.
the background higher than BPRM. While in the middle panel of ﬁgure 4, around 105Ry,
compared with same-n CI, diﬀerent-n CI moves the background up on the left side, and
down on the right side, i.e. converging to the background of BPRM. As close-coupling
approximation treats CI more completely and accurately, we multiply the RDW data
in the higher energy region by a factor which is the ratio of BPRM value and RDW
value at the last point of BPRM calculation for each level (see ﬁgure 5), to account for
the discrepancy between BPRM and RDW. In ﬁgure 5, the distribution of the factors
applied in the higher region is very alike for Fe xvii and Fe xviii , and there are around
60% of the bound levels lying around ratio = 1. Among the high-ratio cases, some are
caused by the oscillation of the background of BPRM, which is due to the small number


## Page 9

R-Matrix calculations for opacities IV
9
-7
-3
1
13
13 (different-n CI)
13 (same-n CI)
-5
-2
1
14
14 (different-n CI)
14 (same-n CI)
-7
-3
1
15
15 (different-n CI)
15 (same-n CI)
-4
-1
2
16
16 (different-n CI)
16 (same-n CI)
-7
-3
1
14
15 (different-n CI)
15 (same-n CI)
0
20
40
60
80
100
120
-4
-1
2
15
14 (different-n CI)
14 (same-n CI)
Photon Energy (Ry)
log
σPI
10 (Mb)
2s1 2p6 4f (J =3)
2s2 2p5 4d (J =3)
2s1 2p6 4f (J =3)
2s2 2p5 4d (J =3)
-7
-3
1
65
65 (different-n CI)
65 (same-n CI)
-5
-2
1
66
66 (different-n CI)
66 (same-n CI)
-5
-2
1
65
66 (different-n CI)
66 (same-n CI)
0
20
40
60
80
100
120
-7
-3
1
66
65 (different-n CI)
65 (same-n CI)
Photon Energy (Ry)
log
σPI
10 (Mb)
2s2 2p4 7p (J =1/2)
2s2 2p4 4f (J =1/2)
Figure 3. Multiple attempts are needed to ensure the correct matching when the
levels are found with discrepancy in the photoionization cross section. In ?? and ??
the discrepancy is shown in upper panel and the ﬁnal matching is in the lower one.
Find the conﬁguration attached for each level. BPRM (black), RDW(blue and red).
“Same-n CI” refers to only same-n-complex CI is considered for core conﬁgurations,
and “diﬀerent-n CI” refers to both same-n- and diﬀerent-n-complex CI are considered.


## Page 10

R-Matrix calculations for opacities IV
10
of continuum basis functions used in the wavefunction expansion [13] (see the bottom
panels of ﬁgure 4.
The energy mesh used in the region is created in such a way that 10 points are
uniformly assigned between any adjacent ionization thresholds due to the other core
conﬁgurations (see section 3.2.2).
3.2.2. Highly excited core conﬁgurations
Using RDW with diﬀerent-n-complex CI, we
calculate photoionization cross section due to other core conﬁgurations up to n = 6
that are not included in the BPRM calculation. To top-up 218CC BPRM for Fe xvii
, we include core conﬁgurations 2s22p44f, 2s2p54f, 2p64ℓ′, 2sS2pP5ℓ′′ and 2sS2pP6ℓ′′′,
where ℓ′, ℓ′′, ℓ′′′ are all possible subshells in the corresponding shell, and s, p are any
possible non-negative integers satisfying S + P = 6.
To top-up 276CC BPRM for
Fe xviii , we include core conﬁgurations 2p53ℓ′, 2s22p34f, 2s2p44ℓ′, 2p54ℓ′′, 2sS2pP5ℓ′′′
and 2sS2pP6ℓ′′′′, where ℓ′, ℓ′′, ℓ′′′ and ℓ′′′′ are all possible subshells in the corresponding
shell, and S, P are any possible non-negative integers satisfying S + P = 5. The energy
mesh is same as the one used in BPRM calculation merged with the one in the high
energy region as described in section ??.
As shown in ﬁgure 6, the BPRM data is merged with the scaled RDW tail, and the
contribute from other core conﬁgurations varies from negligible to noticeable.
3.2.3. Highly excited bound levels
In RDW, we consider all the bound state levels with
n ≤10, so we collect all such levels that are not included in BPRM calculation, and
calculate the photoionization cross section due to all core conﬁgurations, i.e. the core
conﬁgurations included in the BPRM calculation and the other ones displayed in section
3.2.2, with diﬀerent-n-complex CI.
3.3. Bound-bound data
To top-up the bound-bound oscillator strength, we divide it into two parts. One is from
bound states to pure bound states. i.e. between negative energy levels. We calculate
all such possible transitions, but only collect the ones that are not calculated in BPRM
calculations.
The other part is from bound states to quasi-bound states, i.e.
from
negative energy bound levels to positive energy doubly excited states in the continuum.
BPRM calculations treat direct photoionization and autoionization as a single uniﬁed
quantum-mechanical process, as in section 3.2 that discusses direct photoionization is
done. To simulate autoionizing resonances, we calculate the oscillator strengths from
bound to doubly excited states, among all pairs of negative-positive energies.
We
consider transitions that excite an electron from L-shell to a higher one, forming a doubly
excited conﬁguration that can not be formed by combining a core conﬁguration used in
BPRM calculations with another electron. Take Fe xviii for an example, we consider
transitions from 2sS2pP3ℓto only 2p53ℓ′nℓ′′, where S, P are any possible non-negative
integers satisfying S + P = 6, and ℓ, ℓ′, ℓ′′ can be any sub-shell in the corresponding


## Page 11

R-Matrix calculations for opacities IV
11
-4
-2
0
2
4
218CC BPRM
RDW (different-n CI)
RDW (same-n CI)
-4
-1
2
218CC BPRM
RDW (different-n CI)
RDW (same-n CI)
0
20
40
60
80
100
120
-8
-5
-2
1
218CC BPRM
RDW (different-n CI)
RDW (same-n CI)
Photon Energy (Ry)
log
σPI
10 (Mb)
2s2 2p5 5d (J =2)
2s2 2p5 4f (J =4)
2s2 2p5 6h (J =8)
-5
-3
-1
1
3
276CC BPRM
RDW (different-n CI)
RDW (same-n CI)
-4
-2
0
2
276CC BPRM
RDW (different-n CI)
RDW (same-n CI)
0
20
40
60
80
100
120
-10
-6
-2
2
276CC BPRM
RDW (different-n CI)
RDW (same-n CI)
Photon Energy (Ry)
log
σPI
10 (Mb)
2s2 2p4 5f (J =3)
2s2 2p4 4f (J =5)
2s2 2p4 7i (J =7)
Figure 4.
Diﬀerent-n CI improves the background signiﬁcantly, but there is still
very large discrepancy in the right region of energy for some levels. BPRM (black),
RDW(blue and red).
“Same-n CI” refers to only same-n-complex conﬁguration
interaction is considered for core conﬁgurations, and “diﬀerent-n CI” refers to both
same-n- and diﬀerent-n-complex conﬁguration interaction are considered.


## Page 12

R-Matrix calculations for opacities IV
12
0
2
4
6
8
10
0
10
20
30
40
50
60
70
Fe XVII
width = 2
width = 1
width = 0.1
0
2
4
6
8
10
Fe XVIII
width = 2
width = 1
width = 0.1
Percentage (%)
ratio (BPRM / FAC)
Figure 5. The distribution of the factors multiplied to RDW data in the higher energy
region for Fe xvii and Fe xviii . “width” is the width of the bins.
shell, and n = 3 −6. Since 2s22p3 and 2s2p4 are included in 276CC BPRM calculation,
2s22p33ℓ′nℓ′′ and 2s2p43ℓ′nℓ′′ are considered naturally. Thus they are excluded in the
top-up calculations.
The number of quasibound positive energy levels in the continuum is far larger
than bound negative energy levels. For Fe xvii we have 587 bound levels as opposed to
∼72,000 positive energy levels included as top-up. For Fe xviii we obtain 1,154 bound
levels vs. ∼175,000 quasibound levels. All possible oscillator strengths among these
large number of levels are computed and considered in opacities calculations¶.
4. Conclusion
In order to investigate the eﬀect of convergence and completeness of RMOP data for
opacities calculations, complete sets of relativistic distorted wave calculations are carried
out for Fe xvii and Fe xviii to compare with and topup the 218CC and 276CC BPRM
calculations, respectively. Bound state levels are matched between BPRM and RDW
calculation by comparing quantum numbers J, π, energy, and cross sections. With such
¶ We also note that oscillator strength data for transitions among quasibound positive energy levels
are employed for free-free contribution to plasma broadening of autoionizing resonances, discussed in
paper RMOP3


## Page 13

R-Matrix calculations for opacities IV
13
-4
-2
0
2
4
218CC BPRM
Tail
Total (including other cores)
0
100
200
300
400
500
-10
-7
-4
-1
2
5
218CC BPRM
Tail
Total (including other cores)
2s2 2p5 4d (J =2)
2s2 2p5 5g (J =3)
log σPI
10
(Mb)
Photon Energy (Ry)
-4
-3
-2
-1
0
1
2
3
276CC BPRM
Tail
Total (including other cores)
0
100
200
300
400
500
-11
-8
-5
-2
1
276CC BPRM
Tail
Total (including other cores)
2s2 2p4 4d (J =5/2)
2s2 2p4 6h (J =7/2)
log σPI
10
(Mb)
Photon Energy (Ry)
Figure 6. The photoionization cross section of the same four levels as in ﬁgure 2 are
extended to higher energy region and the contribution from other core conﬁgurations


## Page 14

R-Matrix calculations for opacities IV
14
level correspondence, BPRM photoionization cross sections in the higher energy region
are extended by scaled RDW data, and contribution from other core conﬁgurations up
to n = 6 is added, to examine the eﬀect of convergence over and above the n ≤4 BPRM
data. Higher bound state levels are also included with photoionization cross sections
due to all core conﬁgurations up to n = 6.
Oscillator strength data corresponding
to the additional levels are also topped-up, with contribution from bound-bound and
bound-quasibound transitions.
The eﬀects of CI on photoionization cross sections are discussed, including same-
n-complex and diﬀerent-n-complexes, showing its signiﬁcant role in reproducing the
background of BPRM cross sections using RDW. However, the extensive resonance
structures that dominate BPRM photoionization cross sections throughout the energy
range considered can not be compared owing to their absence in the RDW data.
Nevertheless, the RDW method may provide useful checks on completeness and
convergence of CC-BPRM results.
We have extensively studied the correspondence and complementarity between
BPRM and RDW results with a view to ascertain possible impact on opacities. However,
the local-thermodynamic-equilibrium (LTE) Mihalas-Hummer-D¨appen equation-of-
state valid in stellar interiors yields extremely small occupation probabilities and level
populations for the high energy and high (e + ion) spin-angular momenta states nSLJ
(discussed in paper P1), implying that the actual eﬀect on opacities would be small.
Indeed, preliminary opacities calculations indicate that Rosseland Mean Opacities are
enhanced by only a few percent <5% (results to be reported elsewhere).
5. Acknowledgments
One of the authors (ZL) would like to thank Dr. Ming Feng Gu for helpful advice in
using FAC and thank the following colleagues for helping run the BPRM calculation with
their resources in ASC Unity cluster at the Ohio State University (names in alphabetic
order): Jiaxin wu, Keng Yuan Meng, Max Westphal, Xiankun Li, Yonas Getachew and
Zhefu yu. This research was supported by a teaching assistantship from the Dept. of
Physics and the Dept. of Astronomy of Ohio State University (OSU) and by the US
National Science Foundation and Dept. of Energy. Computations were carried out at
the Ohio Supercomputer Center, the OSU Dept. of Astronomy and the ASC Unity
cluster of OSU.
References
[1] Pradhan A K 2018 ASP Conf. Ser. 515 7
[2] Bailey J Nagayama T and Loisel G P et al. 2015 Nature 517 56
[3] Nahar S N Pradhan A K Chen G X and Eissner W 2011 Phys. Rev. A 83 053417
[4] Nahar S N and Pradhan A K Phys. Rev. Lett. 2016 116 235003
[5] Nahar S N and Pradhan A K Phys. Rev. Lett. 2016 117 249502
[6] Iglesias C and Hansen S 2017 Astrophys. J. 835 5


## Page 15

R-Matrix calculations for opacities IV
15
[7] Gu, M. F. 2008, Can. J. Phys., 86, 675;
[8] Seaton M J 1985 J. Phys. B 18 2111
[9] Nahar S N and Pradhan A K 2000 Phys. Scr. 61 675
[10] Nahar S N, Delayaye F Pradhan A K et al. 2000 Astron. Astrophys. Suppl. Ser. 144 141
[11] Eissner W, Jones M and Nussbaumer H 1974 Comput. Phys. Commun. 8 270
[12] The Opacity Project Team, The Opacity Project Vol.1 1995; Ibid. Vol. 2 1997, IOP Publishing
Bristol
[13] Zhang H 1998 Phys. Rev. A 57 2640
[14] Zhang H Nahar S and Pradhan A 1999 J. Phys. B 32 1459
[15] Badnell N R and Seaton M J 2003 J. Phys. B 36, 4367 private communication
[16] Pradhan A K and Zhang H L 1997 J. Phys. B 30 L571

