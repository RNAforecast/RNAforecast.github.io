..
   GENERATED FILE — DO NOT EDIT DIRECTLY.
   Every word below comes from the canonical scientific source:
     insights/rna-structure-before-the-experiment/manuscript.tex
     insights/rna-structure-before-the-experiment/references.bib
     insights/rna-structure-before-the-experiment/metadata.yaml
   Edit those and run: make insight-web SLUG=rna-structure-before-the-experiment
   An edit made here is lost on the next build, and CI fails when this file
   does not match what the sources produce.

RNA Structure Before the Experiment
###################################

:subtitle: An ensemble view of therapeutic RNA design
:slug: rna-structure-before-the-experiment
:date: 2026-09-21
:modified: 2026-09-21
:author: Michael T. Wolfinger
:status: published
:description: How ensemble-aware RNA structure analysis makes the structural consequences of sequence choices visible before an experiment is run.
:summary: RNA therapeutics are designed as sequences, but a sequence change is also an intervention in a folding landscape. An ensemble-aware view of structure will not predict whether a construct works. However, it can make the structural consequences of sequence changes explicit and turn them into hypotheses that can be experimentally tested.
:bib_abstract: RNA therapeutics are designed as sequences, but the resulting molecules occupy folding landscapes that can change as they are synthesized, translated, bound, modified and degraded. Sequence changes can therefore alter structural ensembles, accessibility and folding behaviour even when their intended effect lies elsewhere. This perspective examines how ensemble-aware RNA structure analysis can make such consequences explicit before an experiment is run. Using examples from mRNA design, target accessibility, cotranscriptional folding and modified nucleotides, it discusses both the value and the limitations of thermodynamic structure models. Structural analysis does not predict therapeutic efficacy, but it can help identify relevant differences between variants, expose assumptions in a design and formulate experimentally testable hypotheses.
:tags: RNA structure, RNA therapeutics, mRNA, RNA folding, RNA ensembles
:version: 1.0
:series: RNA Forecast Insights
:number: 1
:doi: 10.5281/zenodo.22872982
:zenodo_url: https://zenodo.org/records/22872982
:license: CC BY 4.0

.. container:: lead

   When RNA itself is the therapeutic molecule, constructs are designed, specified, ordered and compared as sequences. When RNA is the therapeutic target, target sites are likewise usually defined by sequence. In either case, the RNA inside a tube or a cell is not just a string of letters. It is a physical object that can begin to fold as it is synthesised, and continues to fold and unfold as it is translated, bound, modified and degraded.

Sequence changes can alter the folding landscape of an RNA even when structure
is not the intended target of the design. A codon substitution, for example,
may change which regions are exposed or sequestered, the relative populations
of alternative conformations, and the overall stability of the molecule.
These effects are usually not visible in a construct map, but they can
influence how an RNA behaves.

Structural analysis cannot tell us whether a therapeutic concept will work.
It can, however, show how a sequence change is expected to affect RNA
structure and help turn those effects into experimentally testable hypotheses.

A sequence change is also a structural intervention
===================================================

A silent codon substitution changes no amino acid. It can change the set of
base pairs the molecule can form, and the relative weights of the structures in
that set. A change intended as neutral at the level of the protein need not be
neutral at the level of the RNA fold.

This is not a new observation. Across 154 synonymous variants of a single gene,
Kudla and colleagues [#kudla2009]_ found that codon bias did not correlate
with expression, whereas predicted mRNA folding stability around the ribosome
binding site explained more than half of the variation in protein levels.

The evidence is strongest for mRNA. Mauger and colleagues [#mauger2019]_
showed that increasing secondary structure in the coding region
raised protein output, and that the effect was primarily associated with a longer
functional half-life rather than a higher translation rate. Leppek and
colleagues [#leppek2022]_,
measuring degradation and ribosome load across a large designed panel, found
stability and translation could be co-optimised rather than traded off. Zhang and
colleagues [#zhang2023]_ optimised codon usage and folding energy
jointly, and their designed vaccine mRNAs showed longer half-life, higher
expression and substantially higher antibody titres in mice.

None of these results says that a more structured mRNA is a better mRNA.
What they establish is that sequence design also changes structural properties,
whether those changes are considered explicitly or not. A design process that
tracks only codon usage and untranslated-region identity therefore leaves part
of the molecule’s behaviour unexamined.

In other applications, structure can be the design target itself. In our recent
work on exoribonuclease-resistant RNAs [#walter2026]_, sequence design was
guided by the three-dimensional topology required for resistance to XRN1 rather
than by sequence conservation alone. Synthetic sequences with little similarity
to known xrRNAs nevertheless reproduced the required ring-like topology and
remained functional *in vitro*. This is a more specialised example, but it
shows that sequence design can be guided directly by structural principles.

The relevant object is a distribution
=====================================

A standard thermodynamic folding calculation is often summarised by the minimum
free energy structure, i.e. the single fold with the lowest predicted free energy.
This is a useful representation, but an incomplete one. At finite temperature,
an RNA generally populates an ensemble of conformations with probabilities
determined by their free energies.

Under an equilibrium thermodynamic model, that distribution is computable.
McCaskill’s partition function algorithm [#mccaskill1990]_ gives base pair
probabilities over the whole ensemble rather than a single fold, and Ding and
Lawrence’s stochastic sampling [#ding2003]_ draws representative structures
from it. Partition function calculations and Boltzmann-weighted stochastic
sampling are both implemented in widely used RNA folding packages, including the
ViennaRNA Package [#viennarna2011]_.

The ensemble also tells us something about how much confidence to place in a
predicted structure. Mathews [#mathews2004]_ showed that base pairs in the
minimum free energy structure are more likely to be correct when they also
have high pairing probabilities. Those probabilities therefore help identify
which parts of a predicted structure are well supported and which are not. Two
sequences can have the same minimum free energy structure and still differ
substantially in their ensembles. In one case, that structure may dominate
the ensemble, while in another, substantial probability may be distributed over
competing conformations. A single structure representation would miss that
difference, whereas the ensemble makes it visible.

Wayment-Steele and colleagues [#waymentsteele2021]_ showed that the
average unpaired probability (AUP) of an mRNA is related to its predicted
rate of in-line hydrolysis. Designs with lower AUP were predicted to have
longer hydrolytic half-lives while retaining properties associated with
efficient translation. This also illustrates why an ensemble description
can be useful in practice. Rather than asking whether a variant simply
“changes the structure”, one can ask how much it changes the ensemble,
and whether those changes occur in a region relevant to the question being studied.

Accessibility: useful, and not sufficient
=========================================

For mechanisms that require access to an unpaired region, including antisense
oligonucleotides (ASOs), siRNAs, RNA-binding proteins that recognise
single-stranded RNA, primers and engineered sensors, it is usually more
informative to consider the energetic cost of making a site accessible over
the ensemble than whether it happens to be paired in a single predicted structure.

Target accessibility has been used in this way for both siRNA and microRNA
target prediction. Tafer and colleagues [#tafer2008]_ found that
accessibility helped distinguish functional from non-functional siRNAs
and improved selection when combined with sequence and asymmetry criteria.
Kertesz and colleagues [#kertesz2007]_ incorporated the energetic cost
of opening the target site into microRNA target prediction together with
duplex formation energy. In both cases, accessibility contributed useful
information, but was not sufficient on its own.

Vickers and colleagues [#vickers2000]_ examined identical antisense target
sites placed in different structural contexts. Increased target structure
reduced antisense activity in cells, but this effect could be partly overcome
by using higher-affinity oligonucleotide chemistry. The result is a useful
reminder that accessibility matters, but does not act independently of the
other properties of the oligonucleotide and target.

Cellular RNA adds another layer of complexity. Thermodynamic models describe
a naked RNA at equilibrium, whereas in cells RNA is bound by proteins and
remodelled by energy-dependent processes. Rouskin and colleagues [#rouskin2014]_
found that mRNAs were substantially less structured in living cells than
after refolding *in vitro*, and that ATP depletion increased RNA
structure. Equilibrium calculations are therefore better viewed as estimates
of intrinsic folding behaviour than as direct representations of the structures
present in a cell.

Folding takes time, and time is part of the phenotype
=====================================================

Equilibrium is an assumption, and for an RNA that is synthesised
directionally over seconds it can be a substantial one. RNA can fold
co-transcriptionally, so that the 5′ end has already begun to form structure
before the 3′ end is available [#watters2016]_. As a consequence,
thermodynamically favourable structures may not be reached on biologically
relevant timescales, while metastable conformations can persist once they have
formed.

The effect can be seen directly in regulatory RNAs. Helmling and
colleagues [#helmling2017]_ combined NMR analysis of individual
transcription intermediates with cotranscriptional folding simulations of a
riboswitch. The simulations recapitulated the sequence of metastable
conformations seen experimentally and provided a mechanistic explanation
of how these intermediates contribute to regulation.

This kind of analysis requires models that describe not only which structures
are thermodynamically accessible, but also how folding proceeds over time.
Our recent work on KinPFN [#scheuer2025]_ approaches this problem with a
machine learning method based on prior-data fitted neural networks. Rather
than carrying out the full kinetic simulation for every query, KinPFN learns
to approximate the distribution of RNA folding times from simulated training
data and a small number of initial folding-time samples.

From ensemble shift to testable hypothesis
==========================================

In practice, ensemble calculations are most useful when they connect a sequence
change to a specific experimental question:

.. container:: blueprint chain

   #. sequence change

   #. ensemble shift

   #. structural consequence

   #. experimental hypothesis

For a given variant, one can first ask whether the sequence change alters
the predicted ensemble, and by how much. If it does, the next question
is whether this changes a feature relevant to the mechanism under study.
This may be a local region, such as a translation initiation region,
target window, protein-binding site or designed switch, but it can
also be a more global property of the ensemble. The structural
difference becomes experimentally useful when it can be linked to a
specific effect that can be measured and, in principle, ruled out.

For such an analysis to be informative, the modelling assumptions need to be
stated clearly. This includes the energy model and parameter set, temperature
and, where applicable, ionic conditionss, the regions that were analysed, and the size of the
predicted effect relative to variation among comparable sequences. The report
should also make clear which observation would be inconsistent with the proposed
interpretation.

What this does not do
=====================

Structural analysis does not predict therapeutic efficacy. Delivery, innate
immune sensing, manufacturing purity and cell type all influence what happens
between a predicted RNA structure and an experimental or therapeutic outcome,
and none of these factors is represented in a secondary structure model.
Nucleotide chemistry is a somewhat different case. Some modified nucleotides
can now be treated explicitly, but the available thermodynamic parameters are
still far from complete.

Most secondary structure calculations are based on nearest neighbour parameter
sets that were originally developed for RNA containing the four standard
nucleotides [#nndb2024]_. Parameters have since become available for several
modified nucleotides, including N\ :sup:`6`-methyladenosine
 [#szabat2022]_, inosine [#wright2007]_, pseudouridine
 [#shabangu2026psi]_, and N\ :sup:`1`-methylpseudouridine
 [#kierzek2026m1psi]_. The ViennaRNA Package can incorporate
modification-specific energy corrections for a number of such residues
 [#varenyk2023]_. The coverage is nevertheless uneven, and a calculation is
only as reliable as the parameterisation available for the modification and
structural context being considered.

Experimental measurements can provide additional information, but they do not
remove the modelling step. Structure probing experiments, for example, provide
reactivities that can be used to constrain a predicted ensemble, but converting
those measurements into structural information still requires assumptions about
how the experimental signal enters the folding model
 [#deigan2009]_ [#lorenz2016]_.

These limitations do not make the calculations uninformative, but they define
what can reasonably be concluded from them. Structural analysis can help decide
which variants are worth testing, identify assumptions that would otherwise
remain implicit, and make an experimental question more specific. The
experimental result remains the final test.


References
----------

.. container:: refs

  .. [#kudla2009] Kudla G, Murray AW, Tollervey D, Plotkin JB. Coding-sequence
     determinants of gene expression in *Escherichia coli*. *Science*
     324:255–258 (2009).
     `doi:10.1126/science.1170160 <https://doi.org/10.1126/science.1170160>`__
  .. [#mauger2019] Mauger DM, Cabral BJ, Presnyak V, et al. mRNA structure
     regulates protein expression through changes in functional half-life.
     *Proceedings of the National Academy of Sciences USA* 116:24075–24083
     (2019).
     `doi:10.1073/pnas.1908052116 <https://doi.org/10.1073/pnas.1908052116>`__
  .. [#leppek2022] Leppek K, Byeon GW, Kladwang W, et al. Combinatorial
     optimization of mRNA structure, stability, and translation for RNA-based
     therapeutics. *Nature Communications* 13:1536 (2022).
     `doi:10.1038/s41467-022-28776-w <https://doi.org/10.1038/s41467-022-28776-w>`__
  .. [#zhang2023] Zhang H, Zhang L, Lin A, et al. Algorithm for optimized mRNA
     design improves stability and immunogenicity. *Nature* 621:396–403
     (2023).
     `doi:10.1038/s41586-023-06127-z <https://doi.org/10.1038/s41586-023-06127-z>`__
  .. [#walter2026] Walter J, Sidl L, Gutenbrunner K, et al. Rational design of
     mechanically active RNAs: De novo engineering of functional
     exoribonuclease-resistant RNAs. *Nucleic Acids Research* 54(9):gkag473
     (2026).
     `doi:10.1093/nar/gkag473 <https://doi.org/10.1093/nar/gkag473>`__
  .. [#mccaskill1990] McCaskill JS. The equilibrium partition function and
     base pair binding probabilities for RNA secondary structure.
     *Biopolymers* 29:1105–1119 (1990).
     `doi:10.1002/bip.360290621 <https://doi.org/10.1002/bip.360290621>`__
  .. [#ding2003] Ding Y, Lawrence CE. A statistical sampling algorithm for RNA
     secondary structure prediction. *Nucleic Acids Research* 31:7280–7301
     (2003).
     `doi:10.1093/nar/gkg938 <https://doi.org/10.1093/nar/gkg938>`__
  .. [#viennarna2011] Lorenz R, Bernhart SH, Höner zu Siederdissen C, et al.
     ViennaRNA package 2.0. *Algorithms for Molecular Biology* 6:26 (2011).
     `doi:10.1186/1748-7188-6-26 <https://doi.org/10.1186/1748-7188-6-26>`__
  .. [#mathews2004] Mathews DH. Using an RNA secondary structure partition
     function to determine confidence in base pairs predicted by free energy
     minimization. *RNA* 10:1178–1190 (2004).
     `doi:10.1261/rna.7650904 <https://doi.org/10.1261/rna.7650904>`__
  .. [#waymentsteele2021] Wayment-Steele HK, Kim DS, Choe CA, et al.
     Theoretical basis for stabilizing messenger RNA through secondary
     structure design. *Nucleic Acids Research* 49:10604–10617 (2021).
     `doi:10.1093/nar/gkab764 <https://doi.org/10.1093/nar/gkab764>`__
  .. [#tafer2008] Tafer H, Ameres SL, Obernosterer G, et al. The impact of
     target site accessibility on the design of effective siRNAs. *Nature
     Biotechnology* 26:578–583 (2008).
     `doi:10.1038/nbt1404 <https://doi.org/10.1038/nbt1404>`__
  .. [#kertesz2007] Kertesz M, Iovino N, Unnerstall U, Gaul U, Segal E. The
     role of site accessibility in microRNA target recognition. *Nature
     Genetics* 39:1278–1284 (2007).
     `doi:10.1038/ng2135 <https://doi.org/10.1038/ng2135>`__
  .. [#vickers2000] Vickers TA, Wyatt JR, Freier SM. Effects of RNA secondary
     structure on cellular antisense activity. *Nucleic Acids Research*
     28:1340–1347 (2000).
     `doi:10.1093/nar/28.6.1340 <https://doi.org/10.1093/nar/28.6.1340>`__
  .. [#rouskin2014] Rouskin S, Zubradt M, Washietl S, Kellis M, Weissman JS.
     Genome-wide probing of RNA structure reveals active unfolding of mRNA
     structures in vivo. *Nature* 505:701–705 (2014).
     `doi:10.1038/nature12894 <https://doi.org/10.1038/nature12894>`__
  .. [#watters2016] Watters KE, Strobel EJ, Yu AM, Lis JT, Lucks JB.
     Cotranscriptional folding of a riboswitch at nucleotide resolution.
     *Nature Structural & Molecular Biology* 23:1124–1131 (2016).
     `doi:10.1038/nsmb.3316 <https://doi.org/10.1038/nsmb.3316>`__
  .. [#helmling2017] Helmling C, Wacker A, Wolfinger MT, et al. NMR structural
     profiling of transcriptional intermediates reveals riboswitch regulation
     by metastable RNA conformations. *Journal of the American Chemical
     Society* 139(7):2647–2656 (2017).
     `doi:10.1021/jacs.6b10429 <https://doi.org/10.1021/jacs.6b10429>`__
  .. [#scheuer2025] Scheuer D, Runge F, Franke JKH, et al. KinPFN: Bayesian
     approximation of RNA folding kinetics using prior-data fitted networks.
     *Proceedings of the thirteenth international conference on learning
     representations (ICLR)* (2025).
     `doi:10.5281/zenodo.15233965 <https://doi.org/10.5281/zenodo.15233965>`__
  .. [#nndb2024] Mittal A, Turner DH, Mathews DH. NNDB: An expanded database
     of nearest neighbor parameters for predicting stability of nucleic acid
     secondary structures. *Journal of Molecular Biology* 436:168549 (2024).
     `doi:10.1016/j.jmb.2024.168549 <https://doi.org/10.1016/j.jmb.2024.168549>`__
  .. [#szabat2022] Szabat M, Prochota M, Kierzek R, Kierzek E, Mathews DH. A
     test and refinement of folding free energy nearest neighbor parameters
     for RNA including N6-methyladenosine. *Journal of Molecular Biology*
     434:167632 (2022).
     `doi:10.1016/j.jmb.2022.167632 <https://doi.org/10.1016/j.jmb.2022.167632>`__
  .. [#wright2007] Wright DJ, Rice JL, Yanker DM, Znosko BM. Nearest neighbor
     parameters for inosineuridine pairs in RNA duplexes. *Biochemistry*
     46:4625–4634 (2007).
     `doi:10.1021/bi0616910 <https://doi.org/10.1021/bi0616910>`__
  .. [#shabangu2026psi] Shabangu TS, Kierzek E, Arteaga S, Hiltke OM, Mathews
     DH. Nearest neighbor parameters for estimating the folding stability of
     RNA including pseudouridine. *bioRxiv* (2026). Preprint.
     `doi:10.64898/2026.05.16.725682 <https://doi.org/10.64898/2026.05.16.725682>`__
  .. [#kierzek2026m1psi] Kierzek E, Shabangu TS, Hiltke OM, Arteaga S, Mathews
     DH. RNA folding nearest neighbor parameters including the modification
     1-methyl-pseudouridine. *bioRxiv* (2026). Preprint.
     `doi:10.64898/2026.04.09.717343 <https://doi.org/10.64898/2026.04.09.717343>`__
  .. [#varenyk2023] Varenyk Y, Spicher T, Hofacker IL, Lorenz R. Modified RNAs
     and predictions with the ViennaRNA Package. *Bioinformatics*
     39(11):btad696 (2023).
     `doi:10.1093/bioinformatics/btad696 <https://doi.org/10.1093/bioinformatics/btad696>`__
  .. [#deigan2009] Deigan KE, Li TW, Mathews DH, Weeks KM. Accurate
     SHAPE-directed RNA structure determination. *Proceedings of the National
     Academy of Sciences USA* 106:97–102 (2009).
     `doi:10.1073/pnas.0806929106 <https://doi.org/10.1073/pnas.0806929106>`__
  .. [#lorenz2016] Lorenz R, Luntzer D, Hofacker IL, Stadler PF, Wolfinger MT.
     SHAPE directed RNA folding. *Bioinformatics* 32:145–147 (2016).
     `doi:10.1093/bioinformatics/btv523 <https://doi.org/10.1093/bioinformatics/btv523>`__
