## User

This is the beginning of an individual meeting with Immunologist to discuss your research project.

Here is the agenda for the meeting:

You are working on a research project to use machine learning to develop antibodies or nanobodies for the newest variant of the SARS-CoV-2 spike protein that also, ideally, have activity against other circulating minor variants and past variants. Your team previous decided to modify existing nanobodies to improve their binding to the newest variant of the SARS-CoV-2 spike protein. You are responsible for understanding the topic "SARS-CoV-2 spike protein" in the context of designing nanobody binders for SARS-CoV-2. You need to fine-tune yourself on the relevant literature on SARS-CoV-2 spike protein to improve your ability to design SARS-CoV-2 nanobody binders. Please use PubMed Central and search for relevant papers on SARS-CoV-2 spike protein using the query "SARS-CoV-2 spike protein structure and function" and request 100 articles with abstracts only. Read all of the abstracts and based on each abstract individually, decide whether you want to fine-tune yourself on the full text of that paper. Include as many papers as possible, but only include papers that are directly relevant to SARS-CoV-2 spike protein. Please provide the PMCIDs and titles of all the papers that you wish to fine-tune yourself on as a Python dictionary mapping PMCID as a double-quoted string to title as a double-quoted string.

Here are the agenda questions that must be answered:

1. What are the PMCIDs and titles of the papers you wish to fine-tune yourself on (as a Python dictionary mapping PMCID as a double-quoted string to title as double-quoted string)?

Immunologist, please provide your response to the agenda.

## Immunologist

Based on the abstracts provided, I have selected the following papers that are directly relevant to the SARS-CoV-2 spike protein and its implications for designing nanobody binders. Here is a Python dictionary mapping PMCID to the title of each selected paper:

```python
{
    "8651292": "Highly synergistic combinations of nanobodies that target SARS-CoV-2 and are resistant to escape",
    "7932109": "Structure-guided multivalent nanobodies block SARS-CoV-2 infection and suppress mutational escape",
    "11324185": "The S2 subunit of spike encodes diverse targets for functional antibody responses to SARS-CoV-2",
    "9492400": "Host cell membrane proteins located near SARS-CoV-2 spike protein attachment sites are identified using proximity labeling and proteomic analysis",
    "10954308": "Murine alveolar macrophages rapidly accumulate intranasally administered SARS-CoV-2 Spike protein leading to neutrophil recruitment and damage",
    "10865805": "Surface-modified measles vaccines encoding oligomeric, prefusion-stabilized SARS-CoV-2 spike glycoproteins boost neutralizing antibody responses to Omicron and historical variants, independent of measles seropositivity",
    "10114651": "Quantitative profiling of N-glycosylation of SARS-CoV-2 spike protein variants",
    "10384293": "SARS-CoV-2 Spike Protein Is Capable of Inducing Cell–Cell Fusions Independent from Its Receptor ACE2 and This Activity Can Be Impaired by Furin Inhibitors or a Subset of Monoclonal Antibodies",
    "8232969": "In vitro and in vivo functions of SARS-CoV-2 infection-enhancing and neutralizing antibodies",
    "10985062": "Immune Epitopes of SARS-CoV-2 Spike Protein and Considerations for Universal Vaccine Development",
    "10664894": "Antibody-mediated spike activation promotes cell-cell transmission of SARS-CoV-2",
    "10120727": "Murine Alveolar Macrophages Rapidly Accumulate Intranasally Administered SARS-CoV-2 Spike Protein leading to Neutrophil Recruitment and Damage",
    "9393763": "Antibody-mediated immunity to SARS-CoV-2 spike",
    "11389415": "SARS-CoV-2 spike fusion peptide trans interaction with phosphatidylserine lipid triggers membrane fusion for viral entry",
    "10986611": "Vero cell-adapted SARS-CoV-2 strain shows increased viral growth through furin-mediated efficient spike cleavage",
    "11562025": "Neutralisation resistance of SARS-CoV-2 spike-variants is primarily mediated by synergistic receptor binding domain substitutions",
    "11614295": "Comparison of a SARS-CoV-2 mRNA booster immunization containing additional antigens to a spike-based mRNA vaccine against Omicron BA.5 infection in hACE2 mice",
    "10663135": "The SARS-CoV-2 spike glycoprotein interacts with MAO-B and impairs mitochondrial energetics",
    "10695562": "Lys417 acts as a molecular switch that regulates the conformation of SARS-CoV-2 spike protein",
    "10683510": "Structural understanding of SARS-CoV-2 virus entry to host cells"
}
```

These papers cover a range of topics relevant to the structure, function, and immune interactions of the SARS-CoV-2 spike protein, which are crucial for designing effective nanobody binders.

## User

Tool Output:

Here are the top 100 articles on PubMed Central for the query "SARS-CoV-2 spike protein structure and function":

[begin paper 1]

PMCID = 10954308

Title = Murine alveolar macrophages rapidly accumulate intranasally administered SARS-CoV-2 Spike protein leading to neutrophil recruitment and damage

The trimeric SARS-CoV-2 Spike protein mediates viral attachment facilitating cell entry. Most COVID-19 vaccines direct mammalian cells to express the Spike protein or deliver it directly via inoculation to engender a protective immune response. The trafficking and cellular tropism of the Spike protein in vivo and its impact on immune cells remains incompletely elucidated. In this study, we inoculated mice intranasally, intravenously, and subcutaneously with fluorescently labeled recombinant SARS-CoV-2 Spike protein. Using flow cytometry and imaging techniques, we analyzed its localization, immune cell tropism, and acute functional impact. Intranasal administration led to rapid lung alveolar macrophage uptake, pulmonary vascular leakage, and neutrophil recruitment and damage. When injected near the inguinal lymph node medullary, but not subcapsular macrophages, captured the protein, while scrotal injection recruited and fragmented neutrophils. Widespread endothelial and liver Kupffer cell uptake followed intravenous administration. Human peripheral blood cells B cells, neutrophils, monocytes, and myeloid dendritic cells all efficiently bound Spike protein. Exposure to the Spike protein enhanced neutrophil NETosis and augmented human macrophage TNF-α (tumor necrosis factor-α) and IL-6 production. Human and murine immune cells employed C-type lectin receptors and Siglecs to help capture the Spike protein. This study highlights the potential toxicity of the SARS-CoV-2 Spike protein for mammalian cells and illustrates the central role for alveolar macrophage in pathogenic protein uptake.

[end paper 1]

[begin paper 2]

PMCID = 9655607

Title = In Silico Approach for the Evaluation of the Potential Antiviral Activity of Extra Virgin Olive Oil (EVOO) Bioactive Constituents Oleuropein and Oleocanthal on Spike Therapeutic Drug Target of SARS-CoV-2

Since there is an urgent need for novel treatments to combat the current coronavirus disease 2019 (COVID-19) pandemic, in silico molecular docking studies were implemented as an attempt to explore the ability of selected bioactive constituents of extra virgin olive oil (EVOO) to act as potent SARS-CoV-2 (severe acute respiratory syndrome coronavirus 2) antiviral compounds, aiming to explore their ability to interact with SARS-CoV-2 Spike key therapeutic target protein. Our results suggest that EVOO constituents display substantial capacity for binding and interfering with Spike (S) protein, both wild-type and mutant, via the receptor-binding domain (RBD) of Spike, or other binding targets such as angiotensin-converting enzyme 2 (ACE2) or the RBD-ACE2 protein complex, inhibiting the interaction of the virus with host cells. This in silico study provides useful insights for the understanding of the mechanism of action of the studied compounds at a molecular level. From the present study, it could be suggested that the studied active phytochemicals could potentially inhibit the Spike protein, contributing thus to the understanding of the role that they can play in future drug designing and the development of anti-COVID-19 therapeutics.

[end paper 2]

[begin paper 3]

PMCID = 8651292

Title = Highly synergistic combinations of nanobodies that target SARS-CoV-2 and are resistant to escape

The emergence of SARS-CoV-2 variants threatens current vaccines and therapeutic antibodies and urgently demands powerful new therapeutics that can resist viral escape. We therefore generated a large nanobody repertoire to saturate the distinct and highly conserved available epitope space of SARS-CoV-2 spike, including the S1 receptor binding domain, N-terminal domain, and the S2 subunit, to identify new nanobody binding sites that may reflect novel mechanisms of viral neutralization. Structural mapping and functional assays show that indeed these highly stable monovalent nanobodies potently inhibit SARS-CoV-2 infection, display numerous neutralization mechanisms, are effective against emerging variants of concern, and are resistant to mutational escape. Rational combinations of these nanobodies that bind to distinct sites within and between spike subunits exhibit extraordinary synergy and suggest multiple tailored therapeutic and prophylactic strategies.

[end paper 3]

[begin paper 4]

PMCID = 7904240

Title = A Biochemical Perspective of the Nonstructural Proteins (NSPs) and the Spike Protein of SARS CoV-2

The global pandemic that shut down the world in 2020 was caused by the virus, SARS CoV-2. The chemistry of the various nonstructural proteins (NSP3, NSP5, NSP12, NSP13, NSP14, NSP15, NSP16) of SARS CoV-2 is discussed. Secondly, a recent major focus of this pandemic is the variant strains of SARS CoV-2 that are increasingly occurring and more transmissible. One strain, called “D614G”, possesses a glycine (G) instead of an aspartate (D) at position 614 of the spike protein. Additionally, other emerging strains called “501Y.V1” and “501Y.V2” have several differences in the receptor binding domain of the spike protein (N501Y) as well as other locations. These structural changes may enhance the interaction between the spike protein and the ACE2 receptor of the host, increasing infectivity. The global pandemic caused by SARS CoV-2 is a rapidly evolving situation, emphasizing the importance of continuing the efforts to interrogate and understand this virus.

The online version contains supplementary material available at 10.1007/s10930-021-09967-8.

[end paper 4]

[begin paper 5]

PMCID = 10865805

Title = Surface-modified measles vaccines encoding oligomeric, prefusion-stabilized SARS-CoV-2 spike glycoproteins boost neutralizing antibody responses to Omicron and historical variants, independent of measles seropositivity

Serum titers of SARS-CoV-2-neutralizing antibodies (nAbs) correlate well with protection from symptomatic COVID-19 but decay rapidly in the months following vaccination or infection. In contrast, measles-protective nAb titers are lifelong after measles vaccination, possibly due to persistence of the live-attenuated virus in lymphoid tissues. We, therefore, sought to generate a live recombinant measles vaccine capable of driving high SARS-CoV-2 nAb responses. Since previous clinical testing of a live measles vaccine encoding a SARS-CoV-2 spike glycoprotein resulted in suboptimal anti-spike antibody titers, our new vectors were designed to encode prefusion-stabilized SARS-CoV-2 spike glycoproteins, trimerized via an inserted peptide domain, and displayed on a dodecahedral miniferritin scaffold. Additionally, to circumvent the blunting of vaccine efficacy by preformed anti-measles antibodies, we extensively modified the measles surface glycoproteins. Comprehensive in vivo mouse testing demonstrated the potent induction of high titer nAbs in measles-immune mice and confirmed the significant contributions to overall potency afforded by prefusion stabilization, trimerization, and miniferritin display of the SARS-CoV-2 spike glycoprotein. In animals primed and boosted with a measles virus (MeV) vaccine encoding the ancestral SARS-CoV-2 spike, high-titer nAb responses against ancestral virus strains were only weakly cross-reactive with the Omicron variant. However, in primed animals that were boosted with a MeV vaccine encoding the Omicron BA.1 spike, antibody titers to both ancestral and Omicron strains were robustly elevated, and the passive transfer of serum from these animals protected K18-ACE2 mice from infection and morbidity after exposure to BA.1 and WA1/2020 strains. Our results demonstrate that by engineering the antigen, we can develop potent measles-based vaccine candidates against SARS-CoV-2.

Although the live-attenuated measles virus (MeV) is one of the safest and most efficacious human vaccines, a measles-vectored COVID-19 vaccine candidate expressing the SARS-CoV-2 spike failed to elicit neutralizing antibody (nAb) responses in a phase-1 clinical trial, especially in measles-immune individuals. Here, we constructed a comprehensive panel of MeV-based COVID-19 vaccine candidates using a MeV with extensive modifications on the envelope glycoproteins (MeV-MR). We show that artificial trimerization of the spike is critical for the induction of nAbs and that their magnitude can be significantly augmented when the spike protein is synchronously fused to a dodecahedral scaffold. Furthermore, preexisting measles immunity did not abolish heterologous immunity elicited by our vector. Our results highlight the importance of antigen optimization in the development of spike-based COVID-19 vaccines and therapies.

[end paper 5]

[begin paper 6]

PMCID = 10535197

Title = The Effect of Select SARS-CoV-2 N-Linked Glycan and Variant of Concern Spike Protein Mutations on C-Type Lectin-Receptor-Mediated Infection

The SARS-CoV-2 virion has shown remarkable resilience, capable of mutating to escape immune detection and re-establishing infectious capabilities despite new vaccine rollouts. Therefore, there is a critical need to identify relatively immutable epitopes on the SARS-CoV-2 virion that are resistant to future mutations the virus may accumulate. While hACE2 has been identified as the receptor that mediates SARS-CoV-2 susceptibility, it is only modestly expressed in lung tissue. C-type lectin receptors like DC-SIGN can act as attachment sites to enhance SARS-CoV-2 infection of cells with moderate or low hACE2 expression. We developed an easy-to-implement assay system that allows for the testing of SARS-CoV-2 trans-infection. Using our assay, we assessed how SARS-CoV-2 Spike S1-domain glycans and spike proteins from different strains affected the ability of pseudotyped lentivirions to undergo DC-SIGN-mediated trans-infection. Through our experiments with seven glycan point mutants, two glycan cluster mutants and four strains of SARS-CoV-2 spike, we found that glycans N17 and N122 appear to have significant roles in maintaining COVID-19′s infectious capabilities. We further found that the virus cannot retain infectivity upon the loss of multiple glycosylation sites, and that Omicron BA.2 pseudovirions may have an increased ability to bind to other non-lectin receptor proteins on the surface of cells. Taken together, our work opens the door to the development of new therapeutics that can target overlooked epitopes of the SARS-CoV-2 virion to prevent C-type lectin-receptor-mediated trans-infection in lung tissue.

[end paper 6]

[begin paper 7]

PMCID = 9897555

Title = LRRC15 mediates an accessory interaction with the SARS-CoV-2 spike protein

The interactions between Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) and human host factors enable the virus to propagate infections that lead to Coronavirus Disease 2019 (COVID-19). The spike protein is the largest structural component of the virus and mediates interactions essential for infection, including with the primary angiotensin-converting enzyme 2 (ACE2) receptor. We performed two independent cell-based systematic screens to determine whether there are additional proteins by which the spike protein of SARS-CoV-2 can interact with human cells. We discovered that in addition to ACE2, expression of LRRC15 also causes spike protein binding. This interaction is distinct from other known spike attachment mechanisms such as heparan sulfates or lectin receptors. Measurements of orthologous coronavirus spike proteins implied the interaction was functionally restricted to SARS-CoV-2 by accessibility. We localized the interaction to the C-terminus of the S1 domain and showed that LRRC15 shares recognition of the ACE2 receptor binding domain. From analyzing proteomics and single-cell transcriptomics, we identify LRRC15 expression as being common in human lung vasculature cells and fibroblasts. Levels of LRRC15 were greatly elevated by inflammatory signals in the lungs of COVID-19 patients. Although infection assays demonstrated that LRRC15 alone is not sufficient to permit viral entry, we present evidence that it can modulate infection of human cells. This unexpected interaction merits further investigation to determine how SARS-CoV-2 exploits host LRRC15 and whether it could account for any of the distinctive features of COVID-19.

A systematic search for human proteins that can bind to the spike protein of SARS-CoV-2 reveals that LRRC15 can act as a host factor for the virus, and may therefore modulate infection with potential implications for COVID-19.

[end paper 7]

[begin paper 8]

PMCID = 9043892

Title = Passive Immunotherapy Against SARS-CoV-2: From Plasma-Based Therapy to Single Potent Antibodies in the Race to Stay Ahead of the Variants

The COVID-19 pandemic is now approaching 2 years old, with more than 440 million people infected and nearly six million dead worldwide, making it the most significant pandemic since the 1918 influenza pandemic. The severity and significance of SARS-CoV-2 was recognized immediately upon discovery, leading to innumerable companies and institutes designing and generating vaccines and therapeutic antibodies literally as soon as recombinant SARS-CoV-2 spike protein sequence was available. Within months of the pandemic start, several antibodies had been generated, tested, and moved into clinical trials, including Eli Lilly’s bamlanivimab and etesevimab, Regeneron’s mixture of imdevimab and casirivimab, Vir’s sotrovimab, Celltrion’s regdanvimab, and Lilly’s bebtelovimab. These antibodies all have now received at least Emergency Use Authorizations (EUAs) and some have received full approval in select countries. To date, more than three dozen antibodies or antibody combinations have been forwarded into clinical trials. These antibodies to SARS-CoV-2 all target the receptor-binding domain (RBD), with some blocking the ability of the RBD to bind human ACE2, while others bind core regions of the RBD to modulate spike stability or ability to fuse to host cell membranes. While these antibodies were being discovered and developed, new variants of SARS-CoV-2 have cropped up in real time, altering the antibody landscape on a moving basis. Over the past year, the search has widened to find antibodies capable of neutralizing the wide array of variants that have arisen, including Alpha, Beta, Gamma, Delta, and Omicron. The recent rise and dominance of the Omicron family of variants, including the rather disparate BA.1 and BA.2 variants, demonstrate the need to continue to find new approaches to neutralize the rapidly evolving SARS-CoV-2 virus. This review highlights both convalescent plasma- and polyclonal antibody-based approaches as well as the top approximately 50 antibodies to SARS-CoV-2, their epitopes, their ability to bind to SARS-CoV-2 variants, and how they are delivered. New approaches to antibody constructs, including single domain antibodies, bispecific antibodies, IgA- and IgM-based antibodies, and modified ACE2-Fc fusion proteins, are also described. Finally, antibodies being developed for palliative care of COVID-19 disease, including the ramifications of cytokine release syndrome (CRS) and acute respiratory distress syndrome (ARDS), are described.

The online version contains supplementary material available at 10.1007/s40259-022-00529-7.

[end paper 8]

[begin paper 9]

PMCID = 10785701

Title = Differences in syncytia formation by SARS-CoV-2 variants modify host chromatin accessibility and cellular senescence via TP53

Coronavirus disease 2019 (COVID-19) remains a significant public health threat due to the ability of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) variants to evade the immune system and cause breakthrough infections. Although pathogenic coronaviruses such as SARS-CoV-2 and Middle East respiratory syndrome (MERS)-CoV lead to severe respiratory infections, how these viruses affect the chromatin proteomic composition upon infection remains largely uncharacterized. Here, we use our recently developed integrative DNA And Protein Tagging methodology to identify changes in host chromatin accessibility states and chromatin proteomic composition upon infection with pathogenic coronaviruses. SARS-CoV-2 infection induces TP53 stabilization on chromatin, which contributes to its host cytopathic effect. We mapped this TP53 stabilization to the SARS-CoV-2 spike and its propensity to form syncytia, a consequence of cell-cell fusion. Differences in SARS-CoV-2 spike variant-induced syncytia formation modify chromatin accessibility, cellular senescence, and inflammatory cytokine release via TP53. Our findings suggest that differences in syncytia formation alter senescence-associated inflammation, which varies among SARS-CoV-2 variants.

Lee et al. find that spike-mediated cell-cell fusion triggers TP53 stabilization, chromatin accessibility changes, and activation of senescence. The extent of these effects differs based on the fusogenicity of various SARS-CoV-2 variant spike sequences.

[end paper 9]

[begin paper 10]

PMCID = 10702813

Title = Tetherin antagonism by SARS‐CoV‐2 ORF3a and spike protein enhances virus release

The antiviral restriction factor, tetherin, blocks the release of several different families of enveloped viruses, including the Coronaviridae. Tetherin is an interferon‐induced protein that forms parallel homodimers between the host cell and viral particles, linking viruses to the surface of infected cells and inhibiting their release. We demonstrate that SARS‐CoV‐2 infection causes tetherin downregulation and that tetherin depletion from cells enhances SARS‐CoV‐2 viral titres. We investigate the potential viral proteins involved in abrogating tetherin function and find that SARS‐CoV‐2 ORF3a reduces tetherin localisation within biosynthetic organelles where Coronaviruses bud, and increases tetherin localisation to late endocytic organelles via reduced retrograde recycling. We also find that expression of Spike protein causes a reduction in cellular tetherin levels. Our results confirm that tetherin acts as a host restriction factor for SARS‐CoV‐2 and highlight the multiple distinct mechanisms by which SARS‐CoV‐2 subverts tetherin function.

The anti‐viral restriction factor Tetherin blocks the egress of SARS‐CoV‐2. Expression of ORF3a and Spike protein antagonises tetherin to allow SARS‐CoV‐2 escape. 

[end paper 10]

[begin paper 11]

PMCID = 10986611

Title = Vero cell-adapted SARS-CoV-2 strain shows increased viral growth through furin-mediated efficient spike cleavage

Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) utilizes several host proteases to cleave the spike (S) protein to enter host cells. SARS-CoV-2 S protein is cleaved into S1 and S2 subunits by furin, which is closely involved in the pathogenicity of SARS-CoV-2. However, the effects of the modulated protease cleavage activity due to S protein mutations on viral replication and pathogenesis remain unclear. Herein, we serially passaged two SARS-CoV-2 strains in Vero cells and characterized the cell-adapted SARS-CoV-2 strains in vitro and in vivo. The adapted strains showed high viral growth, effective S1/S2 cleavage of the S protein, and low pathogenicity compared with the wild-type strain. Furthermore, the viral growth and S1/S2 cleavage were enhanced by the combination of the Δ68–76 and H655Y mutations using recombinant SARS-CoV-2 strains generated by the circular polymerase extension reaction. The recombinant SARS-CoV-2 strain, which contained the mutation of the adapted strain, showed increased susceptibility to the furin inhibitor, suggesting that the adapted SARS-CoV-2 strain utilized furin more effectively than the wild-type strain. Pathogenicity was attenuated by infection with effectively cleaved recombinant SARS-CoV-2 strains, suggesting that the excessive cleavage of the S proteins decreases virulence. Finally, the high-growth-adapted SARS-CoV-2 strain could be used as the seed for a low-cost inactivated vaccine; immunization with this vaccine can effectively protect the host from SARS-CoV-2 variants. Our findings provide novel insights into the growth and pathogenicity of SARS-CoV-2 in the evolution of cell-cell transmission.

The efficacy of the S protein cleavage generally differs among the SARS-CoV-2 variants, resulting in distinct viral characteristics. The relationship between a mutation and the entry of SARS-CoV-2 into host cells remains unclear. In this study, we analyzed the sequence of high-growth Vero cell-adapted SARS-CoV-2 and factors determining the enhancement of the growth of the adapted virus and confirmed the characteristics of the adapted strain by analyzing the recombinant SARS-CoV-2 strain. We successfully identified mutations Δ68-76 and H655Y, which enhance viral growth and the S protein cleavage by furin. Using recombinant viruses enabled us to conduct a virus challenge experiment in vivo. The pathogenicity of SARS-CoV-2 introduced with the mutations Δ68-76, H655Y, P812L, and Q853L was attenuated in hamsters, indicating the possibility of the attenuation of excessive cleaved SARS-CoV-2. These findings provide novel insights into the infectivity and pathogenesis of SARS-CoV-2 strains, thereby significantly contributing to the field of virology.

[end paper 11]

[begin paper 12]

PMCID = 9937729

Title = Integrative network pharmacology and in silico analyses identify the anti-omicron SARS-CoV-2 potential of eugenol

Eugenol as a natural product is the source of isoniazid, and purified eugenol is extensively used in the cosmetics industry and the productive processes of edible spices. Accumulating evidence suggested that eugenol exerted potent anti-microorganism and anti-inflammation effects. Application of eugenol effectively reduced the risk of atherosclerosis, arterial embolism, and Type 2 diabetes. A previous study confirmed that treatment with eugenol attenuated lung inflammation and improved heart functions in SARS-CoV-2 spike S1-intoxicated mice. In addition to the study, based on a series of public datasets, computational analyses were conducted to characterize the acting targets of eugenol and the functional roles of these targets in COVID-19. The binding capacities of eugenol to conservative sites of SARS-CoV-2 like RNA-dependent RNA polymerase (RdRp) and mutable site as spike (S) protein, were calculated by using molecular docking following the molecular dynamics simulation with RMSD, RMSF, and MM-GBSA methods. The results of network pharmacology indicated that six targets, including PLAT, HMOX1, NUP88, CTSL, ITGB1 andTMPRSS2 were eugenol-SARS-CoV-2 interacting proteins. The omics results of in-silico study further implicated that eugenol increased the expression of SCARB1, HMOX1 and GDF15, especially HMOX1, which were confirmed the potential interacting targets between eugenol and SARS-CoV-2 antigens. Enrichment analyses indicated that eugenol exerted extensive biological effects such as regulating immune infiltration of macrophage, lipid localization, monooxyenase activity, iron ion binding and PPAR signaling. The results of the integrated analysis of eugenol targets and immunotranscription profile of COVID-19 cases shows that eugenol also plays an important role in strengthen of immunologic functions and regulating cytokine signaling. As a complement to the integrated analysis, the results of molecular docking indicated the potential binding interactions between eugenol and four proteins relating to cytokine production/release and the function of T type lymphocytes, including human TLR-4, TCR, NF-κB, JNK and AP-1. Furthermore, results of molecular docking and molecular dynamics (100ns) simulations implicated that stimulated modification of eugenol to the SARS-CoV-2 Omicron Spike-ACE2 complex, especially for human ACE2, and the molecular interaction of eugenol to SARS-CoV-2 RdRp, were no less favorable than two positive controls, molnupiravir and nilotinib. Dynamics (200ns) simulations indicated that the binding capacities and stabilities of eugenol to finger subdomain of RdRp is no less than molnupiravir. However, the simulated binding capacity of eugenol to SARS-CoV-2 wild type RBD and Omicron mutant RBD were less than nilotinib. Eugenol was predicted to have more favor LD50 value and lower cytotoxicity than two positive controls, and eugenol can pass through the blood-brain barrier (BBB). In a brief, eugenol is helpful for attenuating systemic inflammation induced by SARS-CoV-2 infection, due to the direct interaction of eugenol to SARS-CoV-2 proteins and extensive bio-manipulation of pro-inflammatory factors. This study carefully suggests eugenol is a candidate compound of developing drugs and supplement agents against SARS-CoV-2 and its Omicron variants.

[end paper 12]

[begin paper 13]

PMCID = 11324185

Title = The S2 subunit of spike encodes diverse targets for functional antibody responses to SARS-CoV-2

The SARS-CoV-2 virus responsible for the COVID-19 global pandemic has exhibited a striking capacity for viral evolution that drives continued evasion from vaccine and infection-induced immune responses. Mutations in the receptor binding domain of the S1 subunit of the spike glycoprotein have led to considerable escape from antibody responses, reducing the efficacy of vaccines and monoclonal antibody (mAb) therapies. Therefore, there is a need to interrogate more constrained regions of spike, such as the S2 subdomain. Here, we present a collection of S2 mAbs from two SARS-CoV-2 convalescent individuals that target multiple regions in S2, including regions outside of those commonly reported. One of the S2 mAbs, C20.119, which bound to a highly conserved epitope in the fusion peptide, was able to broadly neutralize across SARS-CoV-2 variants, SARS-CoV-1, and closely related zoonotic sarbecoviruses. The majority of the mAbs were non-neutralizing; however, many of them could mediate antibody-dependent cellular cytotoxicity (ADCC) at levels similar to the S1-targeting mAb S309 that was previously authorized for treatment of SARS-CoV-2 infections. Several of the mAbs with ADCC function also bound to spike trimers from other human coronaviruses (HCoVs), such as MERS-CoV and HCoV-HKU1. Our findings suggest S2 mAbs can target diverse epitopes in S2, including functional mAbs with HCoV and sarbecovirus breadth that likely target functionally constrained regions of spike. These mAbs could be developed for potential future pandemics, while also providing insight into ideal epitopes for eliciting a broad HCoV response.

The early successes of vaccines and antibody therapies against SARS-CoV-2, the virus responsible for the COVID-19 global pandemic, leveraged the considerable antibody response to the viral entry protein, spike, after vaccination or infection. These initial interventions were highly effective at protecting from infection and reducing severe disease or death. However, the rapid emergence of new SARS-CoV-2 variants has severely compromised the utility of COVID-19 vaccines and antibody-based treatments. SARS-CoV-2 shows no sign of abating, with the continued rise of new variants with distinct alterations most significantly in regions of the spike protein that elicit most of the anti-viral functional antibody response, which in turn facilitates viral escape from the immune response. These findings suggest a critical need to identify vaccine approaches and therapies that provide the broadest possible antibody responses, focused on regions of spike critical for SARS-CoV-2 infection and, therefore, do not undergo changes that could lead to immune evasion. Our study describes a panel of functional antibodies, from individuals after SARS-CoV-2 infection, that recognize regions of spike that appear conserved across SARS-CoV-2 variants and other closely related viruses, that could guide more effective vaccine design in the face of continued viral evolution.

[end paper 13]

[begin paper 14]

PMCID = 9393763

Title = Antibody-mediated immunity to SARS-CoV-2 spike

Despite effective spike-based vaccines and monoclonal antibodies, the SARS-CoV-2 pandemic continues more than two and a half years post-onset. Relentless investigation has outlined a causative dynamic between host-derived antibodies and reciprocal viral subversion. Integration of this paradigm into the architecture of next generation antiviral strategies, predicated on a foundational understanding of the virology and immunology of SARS-CoV-2, will be critical for success. This review aims to serve as a primer on the immunity endowed by antibodies targeting SARS-CoV-2 spike protein through a structural perspective. We begin by introducing the structure and function of spike, polyclonal immunity to SARS-CoV-2 spike, and the emergence of major SARS-CoV-2 variants that evade immunity. The remainder of the article comprises an in-depth dissection of all major epitopes on SARS-CoV-2 spike in molecular detail, with emphasis on the origins, neutralizing potency, mechanisms of action, cross-reactivity, and variant resistance of representative monoclonal antibodies to each epitope.

[end paper 14]

[begin paper 15]

PMCID = 10409496

Title = TMEM106B is a receptor mediating ACE2-independent SARS-CoV-2 cell entry

SARS-CoV-2 is associated with broad tissue tropism, a characteristic often determined by the availability of entry receptors on host cells. Here, we show that TMEM106B, a lysosomal transmembrane protein, can serve as an alternative receptor for SARS-CoV-2 entry into angiotensin-converting enzyme 2 (ACE2)-negative cells. Spike substitution E484D increased TMEM106B binding, thereby enhancing TMEM106B-mediated entry. TMEM106B-specific monoclonal antibodies blocked SARS-CoV-2 infection, demonstrating a role of TMEM106B in viral entry. Using X-ray crystallography, cryogenic electron microscopy (cryo-EM), and hydrogen-deuterium exchange mass spectrometry (HDX-MS), we show that the luminal domain (LD) of TMEM106B engages the receptor-binding motif of SARS-CoV-2 spike. Finally, we show that TMEM106B promotes spike-mediated syncytium formation, suggesting a role of TMEM106B in viral fusion. Together, our findings identify an ACE2-independent SARS-CoV-2 infection mechanism that involves cooperative interactions with the receptors heparan sulfate and TMEM106B.

TMEM106B directly engages the receptor-binding domain of SARS-CoV-2 spike

Substitution E484D increases TMEM106B binding, enhancing TMEM106B-mediated entry

TMEM106B-specific antibodies neutralize SARS-CoV-2 infection

TMEM106B promotes spike-mediated syncytium formation

The lysosomal transmembrane protein TMEM106B can serve as an alternative receptor for SARS-CoV-2 entry into ACE2-negative cells. Spike substitution E484D improves spike binding to TMEM106B, enhancing TMEM106B-mediated SARS-CoV-2 infection.

[end paper 15]

[begin paper 16]

PMCID = 11486371

Title = A genome-wide arrayed CRISPR screen identifies PLSCR1 as an intrinsic barrier to SARS-CoV-2 entry that recent virus variants have evolved to resist

Interferons (IFNs) play a crucial role in the regulation and evolution of host–virus interactions. Here, we conducted a genome-wide arrayed CRISPR knockout screen in the presence and absence of IFN to identify human genes that influence Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) infection. We then performed an integrated analysis of genes interacting with SARS-CoV-2, drawing from a selection of 67 large-scale studies, including our own. We identified 28 genes of high relevance in both human genetic studies of Coronavirus Disease 2019 (COVID-19) patients and functional genetic screens in cell culture, with many related to the IFN pathway. Among these was the IFN-stimulated gene PLSCR1. PLSCR1 did not require IFN induction to restrict SARS-CoV-2 and did not contribute to IFN signaling. Instead, PLSCR1 specifically restricted spike-mediated SARS-CoV-2 entry. The PLSCR1-mediated restriction was alleviated by TMPRSS2 overexpression, suggesting that PLSCR1 primarily restricts the endocytic entry route. In addition, recent SARS-CoV-2 variants have adapted to circumvent the PLSCR1 barrier via currently undetermined mechanisms. Finally, we investigate the functional effects of PLSCR1 variants present in humans and discuss an association between PLSCR1 and severe COVID-19 reported recently.

Interferons (IFNs) have a role in the regulation of virus-host interactions. This study uses genome-wide CRISPR knockout screen data to identify 28 genes that impact SARS-CoV-2 infection, including PLSCR1, which restricts spike-mediated SARS-CoV-2 entry independently of its IFN-related role.

[end paper 16]

[begin paper 17]

PMCID = 11099032

Title = Sequential glycosylations at the multibasic cleavage site of SARS-CoV-2 spike protein regulate viral activity

The multibasic furin cleavage site at the S1/S2 boundary of the spike protein is a hallmark of SARS-CoV-2 and plays a crucial role in viral infection. However, the mechanism underlying furin activation and its regulation remain poorly understood. Here, we show that GalNAc-T3 and T7 jointly initiate clustered O-glycosylations in the furin cleavage site of the SARS-CoV-2 spike protein, which inhibit furin processing, suppress the incorporation of the spike protein into virus-like-particles and affect viral infection. Mechanistic analysis reveals that the assembly of the spike protein into virus-like particles relies on interactions between the furin-cleaved spike protein and the membrane protein of SARS-CoV-2, suggesting a possible mechanism for furin activation. Interestingly, mutations in the spike protein of the alpha and delta variants of the virus confer resistance against glycosylation by GalNAc-T3 and T7. In the omicron variant, additional mutations reverse this resistance, making the spike protein susceptible to glycosylation in vitro and sensitive to GalNAc-T3 and T7 expression in human lung cells. Our findings highlight the role of glycosylation as a defense mechanism employed by host cells against SARS-CoV-2 and shed light on the evolutionary interplay between the host and the virus.

Here, the authors show that GalNAc-T3 and T7 regulate furin cleavage of the SARS-CoV-2 spike protein via O-glycosylation. This influences viral assembly and infection, highlighting glycosylation as a host defense mechanism.

[end paper 17]

[begin paper 18]

PMCID = 7932109

Title = Structure-guided multivalent nanobodies block SARS-CoV-2 infection and suppress mutational escape

Monoclonal antibodies are an important weapon in the battle against COVID-19. However, these large proteins are difficult to produce in the needed quantities and at low cost. Attention has turned to nanobodies, which are aptly named, single-domain antibodies that are easier to produce and have the potential to be administered by inhalation. Koenig et al. describe four nanobodies that bind to the severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) spike protein and prevent infection of cells (see the Perspective by Saelens and Schepens). Structures show that the nanobodies target two distinct epitopes on the SARS-CoV-2 spike protein. Multivalent nanobodies neutralize virus much more potently than single nanobodies, and multivalent nanobodies that bind two epitopes prevent the emergence of viral escape mutants.

Science, this issue p. eabe6230; see also p. 

SARS-CoV-2–neutralizing nanobodies were combined to design potent multivalent nanobodies.

The global scale and rapid spread of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) pose unprecedented challenges to society, health care systems, and science. In addition to effective and safe vaccines, passive immunization by antibody-related molecules offers an opportunity to harness the vertebrate immune system to fight viral infections in high-risk patients. Variable domains of heavy-chain–only antibodies (VHHs), also known as nanobodies, are suitable lead molecules in such efforts, as they are small, extremely stable, easy to engineer, and economic to produce in simple expression systems.

We engineered improved multivalent nanobodies neutralizing SARS-CoV-2 on the basis of two principles: (i) detailed structural information of their epitopes and binding modes to the viral spike protein and (ii) mechanistic insights into viral fusion with cellular membranes catalyzed by the spike.

Nanobodies specific for the receptor binding domain (RBD) of SARS-CoV-2 spike were identified by phage display using nanobody libraries from an alpaca and a llama immunized with the RBD and inactivated virus. Four of the resulting nanobodies—VHHs E, U, V, and W—potently neutralize SARS-CoV-2 and SARS-CoV-2–pseudotyped vesicular stomatitis virus. X-ray crystallography revealed that the nanobodies bind to two distinct epitopes on the RBD, interfaces “E” and “UVW,” which can be synergistically targeted by combinations of nanobodies to inhibit infection. Cryo–electron microscopy (cryo-EM) of trimeric spike in complex with VHH E and VHH V revealed that VHH E stabilizes a conformation of the spike with all three RBDs in the “up” conformation (3-up), a state that is typically associated with activation by receptor binding. In line with this observation, we found that VHH E triggers the fusion activity of spike in the absence of the cognate receptor ACE2. VHH V, by contrast, stabilizes spike in a 2-up conformation and does not induce fusion. On the basis of the structural information, we designed bi- and trivalent nanobodies with improved neutralizing properties. VHH EEE most potently inhibited infection, did not activate fusion, and likely inactivated virions by outcompeting interaction of the virus with its receptor. Yet evolution experiments revealed emergence of escape mutants in the spike with single–amino acid changes that were completely insensitive to inhibition by VHH EEE. VHH VE also neutralized more efficiently than VHH E or VHH V alone; stabilized the 3-up conformation of spike, as determined by cryo-EM; and more strongly induced the spike fusogenic activity. We conclude that the premature activation of the fusion machinery on virions was an unexpected mechanism of neutralization, as enhanced neutralization could not be attributed simply to better blocking of virus-receptor interactions. Activation of spike in the absence of target membranes likely induces irreversible conformational changes to assume the energetically favorable postfusion conformation without catalyzing fusion per se. Simultaneous targeting of two independent epitopes by VHH VE largely prevented the emergence of resistant escape mutants in evolution experiments.

Our results demonstrate the strength of the modular combination of nanobodies for neutralization. Premature activation of spike by nanobodies reveals an unusual mode of neutralization and yields insights into the mechanism of fusion.

On virions, SARS-CoV-2 spike trimers are mostly in an inactive configuration with all RBDs in the down conformation (left). Binding of bivalent nanobody VE stabilizes the spike in an active conformation with all RBDs up (middle), triggering premature induction of the postfusion conformation, which irreversibly inactivates the spike protein (right).

The pandemic caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) continues to spread, with devastating consequences. For passive immunization efforts, nanobodies have size and cost advantages over conventional antibodies. In this study, we generated four neutralizing nanobodies that target the receptor binding domain of the SARS-CoV-2 spike protein. We used x-ray crystallography and cryo–electron microscopy to define two distinct binding epitopes. On the basis of these structures, we engineered multivalent nanobodies with more than 100 times the neutralizing activity of monovalent nanobodies. Biparatopic nanobody fusions suppressed the emergence of escape mutants. Several nanobody constructs neutralized through receptor binding competition, whereas other monovalent and biparatopic nanobodies triggered aberrant activation of the spike fusion machinery. These premature conformational changes in the spike protein forestalled productive fusion and rendered the virions noninfectious.

[end paper 18]

[begin paper 19]

PMCID = 8732965

Title = Modeling SARS-CoV-2 spike/ACE2 protein–protein interactions for predicting the binding affinity of new spike variants for ACE2, and novel ACE2 structurally related human protein targets, for COVID-19 handling in the 3PM context

The rapid spread of new SARS-CoV-2 variants has highlighted the crucial role played in the infection by mutations occurring at the SARS-CoV-2 spike receptor binding domain (RBD) in the interactions with the human ACE2 receptor. In this context, it urgently needs to develop new rapid tools for quickly predicting the affinity of ACE2 for the SARS-CoV-2 spike RBD protein variants to be used with the ongoing SARS-CoV-2 genomic sequencing activities in the clinics, aiming to gain clues about the transmissibility and virulence of new variants, to prevent new outbreaks and to quickly estimate the severity of the disease in the context of the 3PM.

In our study, we used a computational pipeline for calculating the interaction energies at the SARS-CoV-2 spike RBD/ACE2 protein–protein interface for a selected group of characterized infectious variants of concern/interest (VoC/VoI). By using our pipeline, we built 3D comparative models of the SARS-CoV-2 spike RBD/ACE2 protein complexes for the VoC B.1.1.7-United Kingdom (carrying the mutations of concern/interest N501Y, S494P, E484K at the RBD), P.1-Japan/Brazil (RBD mutations: K417T, E484K, N501Y), B.1.351-South Africa (RBD mutations: K417N, E484K, N501Y), B.1.427/B.1.429-California (RBD mutations: L452R), the B.1.141 (RBD mutations: N439K), and the recent B.1.617.1-India (RBD mutations: L452R; E484Q) and the B.1.620 (RBD mutations: S477N; E484K). Then, we used the obtained 3D comparative models of the SARS-CoV-2 spike RBD/ACE2 protein complexes for predicting the interaction energies at the protein–protein interface.

Along SARS-CoV-2 mutation database screening and mutation localization analysis, it was ascertained that the most dangerous mutations at VoC/VoI spike proteins are located mainly at three regions of the SARS-CoV-2 spike “boat-shaped” receptor binding motif, on the RBD domain. Notably, the P.1 Japan/Brazil variant present three mutations, K417T, E484K, N501Y, located along the entire receptor binding motif, which apparently determines the highest interaction energy at the SARS-CoV-2 spike RBD/ACE2 protein–protein interface, among those calculated. Conversely, it was also observed that the replacement of a single acidic/hydrophilic residue with a basic residue (E484K or N439K) at the “stern” or “bow” regions, of the boat-shaped receptor binding motif on the RBD, appears to determine an interaction energy with ACE2 receptor higher than that observed with single mutations occurring at the “hull” region or with other multiple mutants. In addition, our pipeline allowed searching for ACE2 structurally related proteins, i.e., THOP1 and NLN, which deserve to be investigated for their possible involvement in interactions with the SARS-CoV-2 spike protein, in those tissues showing a low expression of ACE2, or as a novel receptor for future spike variants. A freely available web-tool for the in silico calculation of the interaction energy at the SARS-CoV-2 spike RBD/ACE2 protein–protein interface, starting from the sequences of the investigated spike and/or ACE2 variants, was made available for the scientific community at: https://www.mitoairm.it/covid19affinities.

In the context of the PPPM/3PM, the employment of the described pipeline through the provided webservice, together with the ongoing SARS-CoV-2 genomic sequencing, would help to predict the transmissibility of new variants sequenced from future patients, depending on SARS-CoV-2 genomic sequencing activities and on the specific amino acid replacement and/or on its location on the SARS-CoV-2 spike RBD, to put in play all the possible counteractions for preventing the most deleterious scenarios of new outbreaks, taking into consideration that a greater transmissibility has not to be necessarily related to a more severe manifestation of the disease.

The online version contains supplementary material available at 10.1007/s13167-021-00267-w.

[end paper 19]

[begin paper 20]

PMCID = 9206116

Title = Potent human broadly SARS-CoV-2–neutralizing IgA and IgG antibodies effective against Omicron BA.1 and BA.2

This study identifies broadly SARS-CoV-2–neutralizing IgA and IgG antibodies from Wuhan COVID-19 convalescents active against the variants of concern Alpha, Beta, Gamma, Delta, and Omicron BA.1 and BA.2.

Memory B-cell and antibody responses to the SARS-CoV-2 spike protein contribute to long-term immune protection against severe COVID-19, which can also be prevented by antibody-based interventions. Here, wide SARS-CoV-2 immunoprofiling in Wuhan COVID-19 convalescents combining serological, cellular, and monoclonal antibody explorations revealed humoral immunity coordination. Detailed characterization of a hundred SARS-CoV-2 spike memory B-cell monoclonal antibodies uncovered diversity in their repertoire and antiviral functions. The latter were influenced by the targeted spike region with strong Fc-dependent effectors to the S2 subunit and potent neutralizers to the receptor-binding domain. Amongst those, Cv2.1169 and Cv2.3194 antibodies cross-neutralized SARS-CoV-2 variants of concern, including Omicron BA.1 and BA.2. Cv2.1169, isolated from a mucosa-derived IgA memory B cell demonstrated potency boost as IgA dimers and therapeutic efficacy as IgG antibodies in animal models. Structural data provided mechanistic clues to Cv2.1169 potency and breadth. Thus, potent broadly neutralizing IgA antibodies elicited in mucosal tissues can stem SARS-CoV-2 infection, and Cv2.1169 and Cv2.3194 are prime candidates for COVID-19 prevention and treatment.

[end paper 20]

[begin paper 21]

PMCID = 8917877

Title = SARS-CoV-2 gained a novel spike protein S1–N-Terminal Domain (S1-NTD)

The clue behind the SARS-CoV-2 origin is still a matter of debate. Here, we report that SARS-CoV-2 has gained a novel spike protein S1–N-terminal domain (S1-NTD). In our CLuster ANalysis of Sequences (CLANS) analysis, SARS-CoV/SARS-CoV-2 S1-NTDs displayed a close relationship with OC43 and HKU1. However, in the complete and S1-NTD-free spike protein, SARS-CoV/SARS-CoV-2 revealed closeness with MERS-CoV. Further, we have divided the S1-NTD of SARS-CoV-2 related viruses into three distinct types (Type-I to III S1-NTD) and the S1-NTD of viruses associated with SARS-CoVs into another three classes (Type-A to C S1-NTD) using CLANS and phylogenetic analyses. In particular, the results of our study indicate that SARS-CoV-2, RaTG13, and BANAL-20-52 viruses carry Type-I-S1-NTD and other SARS-CoV-2-related-bat viruses have Type-II and III. In addition, it was revealed that the Pangolin-GX and Pangolin-Guangdong lineages inherited Type-I-like and Type–II–like S1-NTD, respectively. Then our CLANS study shows the potential for evolution of Type-I and Type-III S1-NTD from SARS-CoV-related viruses Type-A and Type-B S1-NTDs, respectively. Furthermore, our analysis clarifies the possibility that Type-II S1-NTDs may have evolved from Type-A-S1-NTD of SARS-CoV-related viruses through Type-I S1-NTDs. We also observed that BANAL-20-103, BANAL-20-236, and Pangolin-Guangdong-lineage viruses containing Type–II–like S1-NTD are very close to SARS-CoV-2 in spike genetic areas other than S1-NTD. Possibly, it suggests that the common ancestor spike gene of SARS-CoV-2/RaTG13/BANAL-20-52-like virus may have evolved by recombining the Pangolin-Guangdong/BANAL-20-103/BANAL-20-236-like spike gene to Pangolin-GX-like Type-I-like-S1-NTD in the unsampled bat or undiscovered intermediate host or possibly pangolin. These may then have evolved into SARS-CoV-2, RaTG13, and BANAL-20-52 virus spike genes by host jump mediated evolution. The potential function of the novel Type-I-S1-NTD and other types of S1-NTDs needs to be studied further to understand better its importance in the ongoing COVID-19 outbreak and for future pandemic preparedness.

[end paper 21]

[begin paper 22]

PMCID = 11389415

Title = SARS-CoV-2 spike fusion peptide trans interaction with phosphatidylserine lipid triggers membrane fusion for viral entry

Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) spike is the fusion machine for host cell entry. Still, the mechanism by which spike protein interacts with the target lipid membrane to facilitate membrane fusion during entry is not fully understood. Here, using steady-state membrane fusion and single-molecule fluorescence resonance energy transfer imaging of spike trimers on the surface of SARS-CoV-2 pseudovirion, we directly show that spike protein interacts with phosphatidylserine (PS) lipid in the target membrane for mediating fusion. We observed that the fusion peptide of the spike S2 domain interacts with the PS lipid of the target membrane. Low pH and Ca2+ trigger the spike conformational change and bring fusion peptide in close proximity to the PS lipid of the membrane. The binding of the spike with PS lipid of its viral membrane (cis interaction) impedes the fusion activation. PS on the target membrane promotes spike binding via trans interaction, prevents the cis interaction, and accelerates fusion. Sequestering or absence of PS lipid abrogates the spike-mediated fusion process and restricts SARS-CoV-2 infectivity. We found that PS-dependent interaction for fusion is conserved across all the SARS-CoV-2 spike variants of concern (D614G, Alpha, Beta, Delta, and Omicron). Our study suggests that PS lipid is indispensable for SARS-CoV-2 spike-mediated virus and target membrane fusion for entry, and restricting PS interaction with spike inhibits the SARS-CoV-2 spike-mediated entry. Therefore, PS is an important cofactor and acts as a molecular beacon in the target membrane for SARS-CoV-2 entry.

The role of lipids in the host cell target membrane for severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) entry is not clear. We do not know whether SARS-CoV-2 spike protein has any specificity in terms of lipid for membrane fusion reaction. Here, using in vitro reconstitution of membrane fusion assay and single-molecule fluorescence resonance energy transfer imaging of SARS-CoV-2 spike trimers on the surface of the virion, we have demonstrated that phosphatidylserine (PS) lipid plays a key role in SARS-CoV-2 spike-mediated membrane fusion reaction for entry. Membrane-externalized PS lipid strongly promotes spike-mediated membrane fusion and COVID-19 infection. Blocking externalized PS lipid with PS-binding protein or in the absence of PS, SARS-CoV-2 spike-mediated fusion is strongly inhibited. Therefore, PS is an important target for restricting viral entry and intervening spike, and PS interaction presents new targets for COVID-19 interventions.

[end paper 22]

[begin paper 23]

PMCID = 9554601

Title = Potent monoclonal antibodies neutralize Omicron sublineages and other SARS-CoV-2 variants

The emergence and global spread of the SARS-CoV-2 Omicron variants, which carry an unprecedented number of mutations, raise serious concerns due to the reduced efficacy of current vaccines and resistance to therapeutic antibodies. Here, we report the generation and characterization of two potent human monoclonal antibodies, NA8 and NE12, against the receptor-binding domain of the SARS-CoV-2 spike protein. NA8 interacts with a highly conserved region and has a breadth of neutralization with picomolar potency against the Beta variant and the Omicron BA.1 and BA.2 sublineages and nanomolar potency against BA.2.12.1 and BA.4. Combination of NA8 and NE12 retains potent neutralizing activity against the major SARS-CoV-2 variants of concern. Cryo-EM analysis provides the structural basis for the broad and complementary neutralizing activity of these two antibodies. We confirm the in vivo protective and therapeutic efficacies of NA8 and NE12 in the hamster model. These results show that broad and potent human antibodies can overcome the continuous immune escape of evolving SARS-CoV-2 variants.

The emergence of new SARS-CoV-2 variants that escape neutralization can jeopardize the efficacy of vaccines and therapeutic antibodies. Chen et al. report the isolation of potent human antibodies that neutralize emerging variants of concern, including various Omicron sublineages. These antibodies show prophylactic and therapeutic efficacy in the hamster model.

[end paper 23]

[begin paper 24]

PMCID = 9159519

Title = Methodology-Centered Review of Molecular Modeling, Simulation, and Prediction of SARS-CoV-2

Despite tremendous efforts in the past two years, our understanding of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), virus–host interactions, immune response, virulence, transmission, and evolution is still very limited. This limitation calls for further in-depth investigation. Computational studies have become an indispensable component in combating coronavirus disease 2019 (COVID-19) due to their low cost, their efficiency, and the fact that they are free from safety and ethical constraints. Additionally, the mechanism that governs the global evolution and transmission of SARS-CoV-2 cannot be revealed from individual experiments and was discovered by integrating genotyping of massive viral sequences, biophysical modeling of protein–protein interactions, deep mutational data, deep learning, and advanced mathematics. There exists a tsunami of literature on the molecular modeling, simulations, and predictions of SARS-CoV-2 and related developments of drugs, vaccines, antibodies, and diagnostics. To provide readers with a quick update about this literature, we present a comprehensive and systematic methodology-centered review. Aspects such as molecular biophysics, bioinformatics, cheminformatics, machine learning, and mathematics are discussed. This review will be beneficial to researchers who are looking for ways to contribute to SARS-CoV-2 studies and those who are interested in the status of the field.

[end paper 24]

[begin paper 25]

PMCID = 9710838

Title = SARS-CoV-2 variant Alpha has a spike-dependent replication advantage over the ancestral B.1 strain in human cells with low ACE2 expression

Epidemiological data demonstrate that Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) variants of concern (VOCs) Alpha and Delta are more transmissible, infectious, and pathogenic than previous variants. Phenotypic properties of VOC remain understudied. Here, we provide an extensive functional study of VOC Alpha replication and cell entry phenotypes assisted by reverse genetics, mutational mapping of spike in lentiviral pseudotypes, viral and cellular gene expression studies, and infectivity stability assays in an enhanced range of cell and epithelial culture models. In almost all models, VOC Alpha spread less or equally efficiently as ancestral (B.1) SARS-CoV-2. B.1. and VOC Alpha shared similar susceptibility to serum neutralization. Despite increased relative abundance of specific sgRNAs in the context of VOC Alpha infection, immune gene expression in infected cells did not differ between VOC Alpha and B.1. However, inferior spreading and entry efficiencies of VOC Alpha corresponded to lower abundance of proteolytically cleaved spike products presumably linked to the T716I mutation. In addition, we identified a bronchial cell line, NCI-H1299, which supported 24-fold increased growth of VOC Alpha and is to our knowledge the only cell line to recapitulate the fitness advantage of VOC Alpha compared to B.1. Interestingly, also VOC Delta showed a strong (595-fold) fitness advantage over B.1 in these cells. Comparative analysis of chimeric viruses expressing VOC Alpha spike in the backbone of B.1, and vice versa, showed that the specific replication phenotype of VOC Alpha in NCI-H1299 cells is largely determined by its spike protein. Despite undetectable ACE2 protein expression in NCI-H1299 cells, CRISPR/Cas9 knock-out and antibody-mediated blocking experiments revealed that multicycle spread of B.1 and VOC Alpha required ACE2 expression. Interestingly, entry of VOC Alpha, as opposed to B.1 virions, was largely unaffected by treatment with exogenous trypsin or saliva prior to infection, suggesting enhanced resistance of VOC Alpha spike to premature proteolytic cleavage in the extracellular environment of the human respiratory tract. This property may result in delayed degradation of VOC Alpha particle infectivity in conditions typical of mucosal fluids of the upper respiratory tract that may be recapitulated in NCI-H1299 cells closer than in highly ACE2-expressing cell lines and models. Our study highlights the importance of cell model evaluation and comparison for in-depth characterization of virus variant-specific phenotypes and uncovers a fine-tuned interrelationship between VOC Alpha- and host cell-specific determinants that may underlie the increased and prolonged virus shedding detected in patients infected with VOC Alpha.

Epidemiological data show that SARS-CoV-2 variants of concern Alpha and Delta are more transmissible, infectious and pathogenic than previous variants, but their phenotypic properties remain understudied. A functional study of the Alpha variant identifies a single bronchial cell line that reflects its enhanced in vivo transmissibility.

[end paper 25]

[begin paper 26]

PMCID = 11407660

Title = Dual-role epitope on SARS-CoV-2 spike enhances and neutralizes viral entry across different variants

Grasping the roles of epitopes in viral glycoproteins is essential for unraveling the structure and function of these proteins. Up to now, all identified epitopes have been found to either neutralize, have no effect on, or enhance viral entry into cells. Here, we used nanobodies (single-domain antibodies) as probes to investigate a unique epitope on the SARS-CoV-2 spike protein, located outside the protein’s receptor-binding domain. Nanobody binding to this epitope enhances the cell entry of prototypic SARS-CoV-2, while neutralizing the cell entry of SARS-CoV-2 Omicron variant. Moreover, nanobody binding to this epitope promotes both receptor binding activity and post-attachment activity of prototypic spike, explaining the enhanced viral entry. The opposite occurs with Omicron spike, explaining the neutralized viral entry. This study reveals a unique epitope that can both enhance and neutralize viral entry across distinct viral variants, suggesting that epitopes may vary their roles depending on the viral context. Consequently, antibody therapies should be assessed across different viral variants to confirm their efficacy and safety.

Antibodies bind to specific epitopes on viral surface glycoproteins to perform their function: inhibiting viral infection, having no effect, or, in rare cases, enhancing viral infection. In our research, we used nanobodies (small, single-domain antibodies from camelid animals) as probes and identified a unique epitope on the SARS-CoV-2 spike protein with opposing functions across different SARS-CoV-2 variants. It enhances viral infection in pre-Omicron variants but inhibits it in the Omicron variant. We further investigated the molecular mechanism underlying these opposing effects. Although this epitope is not directly involved in receptor binding, nanobody binding to it modulates receptor binding and post-receptor-binding activities. This study marks the first discovery of a dual-function epitope on the SARS-CoV-2 spike protein that both enhances and inhibits viral infection across different viral variants. This discovery challenges the traditional categorization of epitopes, underscores the complex evolution of the SARS-CoV-2 spike protein, and offers new insights into antiviral antibody therapies.

[end paper 26]

[begin paper 27]

PMCID = 8776496

Title = Mutations in SARS-CoV-2 variants of concern link to increased spike cleavage and virus transmission

SARS-CoV-2 lineages have diverged into highly prevalent variants termed “variants of concern” (VOCs). Here, we characterized emerging SARS-CoV-2 spike polymorphisms in vitro and in vivo to understand their impact on transmissibility and virus pathogenicity and fitness. We demonstrate that the substitution S:655Y, represented in the gamma and omicron VOCs, enhances viral replication and spike protein cleavage. The S:655Y substitution was transmitted more efficiently than its ancestor S:655H in the hamster infection model and was able to outcompete S:655H in the hamster model and in a human primary airway system. Finally, we analyzed a set of emerging SARS-CoV-2 variants to investigate how different sets of mutations may impact spike processing. All VOCs tested exhibited increased spike cleavage and fusogenic capacity. Taken together, our study demonstrates that the spike mutations present in VOCs that become epidemiologically prevalent in humans are linked to an increase in spike processing and virus transmission.

Escalera et al. show that spike mutation H655Y, which is present in SARS-CoV-2 variants gamma and omicron, enhances spike protein cleavage, cell-cell fusion, and transmission in the hamster model. Additionally, SARS-CoV-2 variants of concern are shown to have independently acquired mutations associated with a gain in spike cleavage and syncytia formation.

[end paper 27]

[begin paper 28]

PMCID = 7334636

Title = Protein structure analysis of the interactions between SARS-CoV-2 spike protein and the human ACE2 receptor: from conformational changes to novel neutralizing antibodies

The recent severe acute respiratory syndrome, known as Coronavirus Disease 2019 (COVID-19) has spread so much rapidly and severely to induce World Health Organization (WHO) to declare a state of emergency over the new coronavirus SARS-CoV-2 pandemic. While several countries have chosen the almost complete lock-down for slowing down SARS-CoV-2 spread, the scientific community is called to respond to the devastating outbreak by identifying new tools for diagnosis and treatment of the dangerous COVID-19. With this aim, we performed an in silico comparative modeling analysis, which allows gaining new insights into the main conformational changes occurring in the SARS-CoV-2 spike protein, at the level of the receptor-binding domain (RBD), along interactions with human cells angiotensin-converting enzyme 2 (ACE2) receptor, that favor human cell invasion. Furthermore, our analysis provides (1) an ideal pipeline to identify already characterized antibodies that might target SARS-CoV-2 spike RBD, aiming to prevent interactions with the human ACE2, and (2) instructions for building new possible neutralizing antibodies, according to chemical/physical space restraints and complementary determining regions (CDR) mutagenesis of the identified existing antibodies. The proposed antibodies show in silico high affinity for SARS-CoV-2 spike RBD and can be used as reference antibodies also for building new high-affinity antibodies against present and future coronaviruses able to invade human cells through interactions of their spike proteins with the human ACE2. More in general, our analysis provides indications for the set-up of the right biological molecular context for investigating spike RBD–ACE2 interactions for the development of new vaccines, diagnostic kits, and other treatments based on the targeting of SARS-CoV-2 spike protein.

The online version of this article (10.1007/s00018-020-03580-1) contains supplementary material, which is available to authorized users.

[end paper 28]

[begin paper 29]

PMCID = 8232969

Title = In vitro and in vivo functions of SARS-CoV-2 infection-enhancing and neutralizing antibodies

SARS-CoV-2-neutralizing antibodies (NAbs) protect against COVID-19. A concern regarding SARS-CoV-2 antibodies is whether they mediate disease enhancement. Here, we isolated NAbs against the receptor-binding domain (RBD) or the N-terminal domain (NTD) of SARS-CoV-2 spike from individuals with acute or convalescent SARS-CoV-2 or a history of SARS-CoV infection. Cryo-electron microscopy of RBD and NTD antibodies demonstrated function-specific modes of binding. Select RBD NAbs also demonstrated Fc receptor-γ (FcγR)-mediated enhancement of virus infection in vitro, while five non-neutralizing NTD antibodies mediated FcγR-independent in vitro infection enhancement. However, both types of infection-enhancing antibodies protected from SARS-CoV-2 replication in monkeys and mice. Three of 46 monkeys infused with enhancing antibodies had higher lung inflammation scores compared to controls. One monkey had alveolar edema and elevated bronchoalveolar lavage inflammatory cytokines. Thus, while in vitro antibody-enhanced infection does not necessarily herald enhanced infection in vivo, increased lung inflammation can rarely occur in SARS-CoV-2 antibody-infused macaques.

Convalescent human-derived SARS-CoV-2 RBD and NTD antibodies mediated neutralization as well as infection enhancement in vitro, yet infusion of these antibodies in mice or cynomolgus macaques resulted in suppression of virus replication.

[end paper 29]

[begin paper 30]

PMCID = 8651051

Title = Bispecific antibodies targeting distinct regions of the spike protein potently neutralize SARS-CoV-2 variants of concern

Bispecific antibodies targeting multiple regions of the SARS-CoV-2 spike protein comparably neutralize variants of concern and wild-type virus.

Monoclonal antibodies (mAbs) have become an essential component of coronavirus disease 2019 (COVID-19) treatment. Most mAbs are administered as a cocktail of multiple antibodies that target different regions of the severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) virion. Here, Cho et al. further improved upon this strategy by identifying mAbs that, when combined as bispecific antibodies, neutralized SARS-CoV-2 better than cocktails of the parental mAbs. These bispecific antibodies bound to distinct regions of the SARS-CoV-2 spike protein, neutralized variants of concern, including the Delta variant, and conferred protection when administered to hamsters before SARS-CoV-2 infection. Together, these findings suggest that bispecific antibodies merit further consideration as variant-resistant SARS-CoV-2 therapeutics.

The emergence of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) variants of concern threatens the efficacy of existing vaccines and therapeutic antibodies and underscores the need for additional antibody-based tools that potently neutralize variants by targeting multiple sites of the spike protein. We isolated 216 monoclonal antibodies targeting SARS-CoV-2 from plasmablasts and memory B cells collected from patients with coronavirus disease 2019. The three most potent antibodies targeted distinct regions of the receptor binding domain (RBD), and all three neutralized the SARS-CoV-2 Alpha and Beta variants. The crystal structure of the most potent antibody, CV503, revealed that it binds to the ridge region of SARS-CoV-2 RBD, competes with the angiotensin-converting enzyme 2 receptor, and has limited contact with key variant residues K417, E484, and N501. We designed bispecific antibodies by combining nonoverlapping specificities and identified five bispecific antibodies that inhibit SARS-CoV-2 infection at concentrations of less than 1 ng/ml. Through a distinct mode of action, three bispecific antibodies cross-linked adjacent spike proteins using dual N-terminal domain–RBD specificities. One bispecific antibody was greater than 100-fold more potent than a cocktail of its parent monoclonals in vitro and prevented clinical disease in a hamster model at a dose of 2.5 mg/kg. Two bispecific antibodies in our panel comparably neutralized the Alpha, Beta, Gamma, and Delta variants and wild-type virus. Furthermore, a bispecific antibody that neutralized the Beta variant protected hamsters against SARS-CoV-2 expressing the E484K mutation. Thus, bispecific antibodies represent a promising next-generation countermeasure against SARS-CoV-2 variants of concern.

[end paper 30]

[begin paper 31]

PMCID = 8989121

Title = Impairment of SARS-CoV-2 spike glycoprotein maturation and fusion activity by nitazoxanide: an effect independent of spike variants emergence

SARS-CoV-2, the causative agent of COVID-19, has caused an unprecedented global health crisis. The SARS-CoV-2 spike, a surface-anchored trimeric class-I fusion glycoprotein essential for viral entry, represents a key target for developing vaccines and therapeutics capable of blocking virus invasion. The emergence of SARS-CoV-2 spike variants that facilitate virus spread and may affect vaccine efficacy highlights the need to identify novel antiviral strategies for COVID-19 therapy. Here, we demonstrate that nitazoxanide, an antiprotozoal agent with recognized broad-spectrum antiviral activity, interferes with SARS-CoV-2 spike maturation, hampering its terminal glycosylation at an endoglycosidase H-sensitive stage. Engineering multiple SARS-CoV-2 variant-pseudoviruses and utilizing quantitative cell–cell fusion assays, we show that nitazoxanide-induced spike modifications hinder progeny virion infectivity as well as spike-driven pulmonary cell–cell fusion, a critical feature of COVID-19 pathology. Nitazoxanide, being equally effective against the ancestral SARS-CoV-2 Wuhan-spike and different emerging variants, including the Delta variant of concern, may represent a useful tool in the fight against COVID-19 infections. 

The online version contains supplementary material available at 10.1007/s00018-022-04246-w.

[end paper 31]

[begin paper 32]

PMCID = 8920968

Title = The spike glycoprotein of SARS-CoV-2: A review of how mutations of spike glycoproteins have driven the emergence of variants with high transmissibility and immune escape

Late in 2019, SARS-CoV-2 (severe acute respiratory syndrome coronavirus-2) emerged, causing an unknown type of pneumonia today called coronaviruses disease 2019 (COVID-19). COVID-19 is still an ongoing global outbreak that has claimed and threatened many lives worldwide. Along with the fastest vaccine developed in history to fight SARS-CoV-2 came a critical problem, SARS-CoV-2. These new variants are a result of the accumulation of mutations in the sequence and structure of spike (S) glycoprotein, which is by far the most critical protein for SARS-CoV-2 to recognize cells and escape the immune system, in addition to playing a role in SARS-CoV-2 infection, pathogenicity, transmission, and evolution. In this review, we discuss mutation of S protein and how these mutations have led to new variants that are usually more transmissible and can thus mitigate the immunity produced by vaccination. Here, analysis of S protein sequences and structures from variants point out the mutations among them, how they emerge, and the behavior of S protein from each variant. This review brings details in an understandable way about how the variants of SARS-CoV-2 are a result of mutations in S protein, making them more transmissible and even more aggressive than their relatives.

[end paper 32]

[begin paper 33]

PMCID = 10114651

Title = Quantitative profiling of N-glycosylation of SARS-CoV-2 spike protein variants

With the global spread of the corona virus disease-2019 pandemic, new spike variants of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) continuously emerge due to increased possibility of virus adaptive amino acid mutations. However, the N-glycosylation profiles of different spike variants are yet to be explored extensively, although the spike protein is heavily glycosylated and surface glycans are well-established to play key roles in viral infection and immune response. Here, we investigated quantitatively the N-glycosylation profiles of seven major emerging spike variants including Original, Alpha (B.1.1.7), Beta (B.1.351), Gamma (P.1), Kappa (B.1.671.1), Delta (B.1.671.2), and Omicron (B.1.1.529). The aim was to understand the changing pattern of N-glycan profiles in SARS-CoV-2 evolution in addition to the widely studied amino acid mutations. Different spike variants exhibit substantial variations in the relative abundance of different glycan peaks and subclasses, although no specific glycan species are exclusively present in or absent from any specific variant. Cluster analysis shows that the N-glycosylation profiles may hold the potential for SARS-CoV-2 spike variants classification. Alpha and Beta variants exhibit the closest similarity to the Original, and the Delta variant displays substantial similarity to Gamma and Kappa variants, while the Omicron variant is significantly different from its counterparts. We demonstrated that there is a quantifiable difference in N-glycosylation profiles among different spike variants. The current study and observations herein provide a valuable framework for quantitative N-glycosylation profiling of new emerging viral variants and give us a more comprehensive picture of COVID-19 evolution.

[end paper 33]

[begin paper 34]

PMCID = 8104966

Title = SARS-CoV-2 requires cholesterol for viral entry and pathological syncytia formation

Many enveloped viruses induce multinucleated cells (syncytia), reflective of membrane fusion events caused by the same machinery that underlies viral entry. These syncytia are thought to facilitate replication and evasion of the host immune response. Here, we report that co-culture of human cells expressing the receptor ACE2 with cells expressing SARS-CoV-2 spike, results in synapse-like intercellular contacts that initiate cell-cell fusion, producing syncytia resembling those we identify in lungs of COVID-19 patients. To assess the mechanism of spike/ACE2-driven membrane fusion, we developed a microscopy-based, cell-cell fusion assay to screen ~6000 drugs and >30 spike variants. Together with quantitative cell biology approaches, the screen reveals an essential role for biophysical aspects of the membrane, particularly cholesterol-rich regions, in spike-mediated fusion, which extends to replication-competent SARS-CoV-2 isolates. Our findings potentially provide a molecular basis for positive outcomes reported in COVID-19 patients taking statins and suggest new strategies for therapeutics targeting the membrane of SARS-CoV-2 and other fusogenic viruses.

[end paper 34]

[begin paper 35]

PMCID = 9910744

Title = Fibroblast-expressed LRRC15 is a receptor for SARS-CoV-2 spike and controls antiviral and antifibrotic transcriptional programs

Although ACE2 is the primary receptor for Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) infection, a systematic assessment of host factors that regulate binding to SARS-CoV-2 spike protein has not been described. Here, we use whole-genome CRISPR activation to identify host factors controlling cellular interactions with SARS-CoV-2. Our top hit was a TLR-related cell surface receptor called leucine-rich repeat-containing protein 15 (LRRC15). LRRC15 expression was sufficient to promote SARS-CoV-2 spike binding where they form a cell surface complex. LRRC15 mRNA is expressed in human collagen-producing lung myofibroblasts and LRRC15 protein is induced in severe Coronavirus Disease 2019 (COVID-19) infection where it can be found lining the airways. Mechanistically, LRRC15 does not itself support SARS-CoV-2 infection, but fibroblasts expressing LRRC15 can suppress both pseudotyped and authentic SARS-CoV-2 infection in trans. Moreover, LRRC15 expression in fibroblasts suppresses collagen production and promotes expression of IFIT, OAS, and MX-family antiviral factors. Overall, LRRC15 is a novel SARS-CoV-2 spike-binding receptor that can help control viral load and regulate antiviral and antifibrotic transcriptional programs in the context of COVID-19 infection.

Molecular interactions between SARS-CoV-2 and its host dictate the course of COVID-19 disease progression; this study identifies LRRC15 as a new fibroblast SARS-CoV-2 spike receptor that can block infection, activate cellular antiviral programs, and suppress collagen production.

[end paper 35]

[begin paper 36]

PMCID = 11562025

Title = Neutralisation resistance of SARS-CoV-2 spike-variants is primarily mediated by synergistic receptor binding domain substitutions

The evolution of SARS-CoV-2 has led to the emergence of numerous variants of concern (VOCs), marked by changes in the viral spike glycoprotein, the primary target for neutralising antibody (nAb) responses. Emerging VOCs, particularly omicron sub-lineages, show resistance to nAbs induced by prior infection or vaccination. The precise spike protein changes contributing to this resistance remain unclear in infectious cell culture systems. In the present study, a large panel of infectious SARS-CoV-2 mutant viruses, each with spike protein changes found in VOCs, including omicron JN.1 and its derivatives KP.2 and KP.3, was generated using a reverse genetic system. The susceptibility of these viruses to antibody neutralisation was measured using plasma from convalescent and vaccinated individuals. Synergistic roles of combined substitutions in the spike receptor binding domain (RBD) were observed in neutralisation resistance. However, recombinant viruses with the entire spike protein from a specific VOC showed enhanced resistance, indicating that changes outside the RBD are also significant. In silico analyses of spike antibody epitopes suggested that changes in neutralisation could be due to altered antibody binding affinities. Assessing ACE2 usage for entry through anti-ACE2 antibody blocking and ACE2 siRNA revealed that omicron BA.2.86 and JN.1 mutant viruses were less dependent on ACE2 for entry. However, surface plasmon resonance analysis showed increased affinity for ACE2 for both BA.2.86 and JN.1 compared to the ancestral spike. This detailed analysis of specific changes in the SARS-CoV-2 spike enhances understanding of coronavirus evolution, particularly regarding neutralising antibody evasion and ACE2 entry receptor dependence.

[end paper 36]

[begin paper 37]

PMCID = 8941872

Title = Omicron: What Makes the Latest SARS-CoV-2 Variant of Concern So Concerning?

Emerging strains of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), the causative agent of the coronavirus disease 2019 (COVID-19) pandemic, that show increased transmission fitness and/or immune evasion are classified as “variants of concern” (VOCs). Recently, a SARS-CoV-2 variant first identified in November 2021 in South Africa has been recognized as a fifth VOC, termed “Omicron.” What makes this VOC so alarming is the high number of changes, especially in the viral Spike protein, and accumulating evidence for increased transmission efficiency and escape from neutralizing antibodies. In an amazingly short time, the Omicron VOC has outcompeted the previously dominating Delta VOC. However, it seems that the Omicron VOC is overall less pathogenic than other SARS-CoV-2 VOCs. Here, we provide an overview of the mutations in the Omicron genome and the resulting changes in viral proteins compared to other SARS-CoV-2 strains and discuss their potential functional consequences.

[end paper 37]

[begin paper 38]

PMCID = 10664894

Title = Antibody-mediated spike activation promotes cell-cell transmission of SARS-CoV-2

The COVID pandemic fueled by emerging SARS-CoV-2 new variants of concern remains a major global health concern, and the constantly emerging mutations present challenges to current therapeutics. The spike glycoprotein is not only essential for the initial viral entry, but is also responsible for the transmission of SARS-CoV-2 components via syncytia formation. Spike-mediated cell-cell transmission is strongly resistant to extracellular therapeutic and convalescent antibodies via an unknown mechanism. Here, we describe the antibody-mediated spike activation and syncytia formation on cells displaying the viral spike. We found that soluble antibodies against receptor binding motif (RBM) are capable of inducing the proteolytic processing of spike at both the S1/S2 and S2’ cleavage sites, hence triggering ACE2-independent cell-cell fusion. Mechanistically, antibody-induced cell-cell fusion requires the shedding of S1 and exposure of the fusion peptide at the cell surface. By inhibiting S1/S2 proteolysis, we demonstrated that cell-cell fusion mediated by spike can be re-sensitized towards antibody neutralization in vitro. Lastly, we showed that cytopathic effect mediated by authentic SARS-CoV-2 infection remain unaffected by the addition of extracellular neutralization antibodies. Hence, these results unveil a novel mode of antibody evasion and provide insights for antibody selection and drug design strategies targeting the SARS-CoV-2 infected cells.

SARS-CoV-2 has been found to mediate breakthrough infections in vaccinated individuals and re-infections of convalescent patients, but the molecular mechanism of its immune escaping strategies remains elusive. Unlike virus-to-cell transmission, spike promotes SARS-CoV-2 cell-to-cell transmission, which is strongly resistant to extracellular antibodies and patient plasma. Here we show that receptor binding-motif antibodies mediate the ACE2-independent activation of spike at the cell plasma membrane. This mode of spike activation is enabled by the protease-mediated S1/S2 cleavage event and can be genetically and pharmacologically prevented. Through targeting the S1/S2 site, antibody neutralization against spike-mediated cell-cell fusion can be restored in various SARS-CoV-2 variants. Hence, these data highlight a role for S1/S2-cleaved spike and inform therapeutic strategies to restore antibody neutralization against cell-cell transmission of SARS-CoV-2.

[end paper 38]

[begin paper 39]

PMCID = 11614295

Title = Comparison of a SARS-CoV-2 mRNA booster immunization containing additional antigens to a spike-based mRNA vaccine against Omicron BA.5 infection in hACE2 mice

The emergence of SARS-CoV-2 variants presents challenges to vaccine effectiveness, underlining the necessity for next-generation vaccines with multiple antigens beyond the spike protein. Here, we investigated a multiantigenic booster containing spike and a chimeric construct composed of nucleoprotein (N) and membrane (M) proteins, comparing its efficacy to a spike-only booster against Omicron BA.5 in K18-hACE2 mice. Initially, mice were primed and boosted with Beta (B.1.351) spike-only mRNA, showing strong spike-specific T cell responses and neutralizing antibodies, albeit with limited cross-neutralization to Omicron variants. Subsequently, a spike-NM multiantigenic vaccine was then examined as a second booster dose for protection in hACE2-transgenic mice. Mice receiving either homologous spike-only or heterologous spike-NM booster had nearly complete inhibition of infectious virus shedding in oral swabs and reduced viral burdens in both lung and nasal tissues following BA.5 challenge. Examination of lung pathology further revealed that both spike-only and spike-NM boosters provided comparable protection against inflammatory infiltrates and fibrosis. Moreover, the spike-NM booster demonstrated neutralization efficacy in a pseudovirus assay against Wuhan-Hu-1, Beta, and Omicron variants akin to the spike-only booster. These findings indicate that supplementing spike with additional SARS-CoV-2 targets in a booster immunization confers equivalent immunity and protection against Omicron BA.5. This work highlights a promising strategy for individuals previously vaccinated with spike-only vaccines, potentially offering enhanced protection against emerging coronaviruses.

[end paper 39]

[begin paper 40]

PMCID = 8420505

Title = Identification of lectin receptors for conserved SARS‐CoV‐2 glycosylation sites

New SARS‐CoV‐2 variants are continuously emerging with critical implications for therapies or vaccinations. The 22 N‐glycan sites of Spike remain highly conserved among SARS‐CoV‐2 variants, opening an avenue for robust therapeutic intervention. Here we used a comprehensive library of mammalian carbohydrate‐binding proteins (lectins) to probe critical sugar residues on the full‐length trimeric Spike and the receptor binding domain (RBD) of SARS‐CoV‐2. Two lectins, Clec4g and CD209c, were identified to strongly bind to Spike. Clec4g and CD209c binding to Spike was dissected and visualized in real time and at single‐molecule resolution using atomic force microscopy. 3D modelling showed that both lectins can bind to a glycan within the RBD‐ACE2 interface and thus interferes with Spike binding to cell surfaces. Importantly, Clec4g and CD209c significantly reduced SARS‐CoV‐2 infections. These data report the first extensive map and 3D structural modelling of lectin‐Spike interactions and uncovers candidate receptors involved in Spike binding and SARS‐CoV‐2 infections. The capacity of CLEC4G and mCD209c lectins to block SARS‐CoV‐2 viral entry holds promise for pan‐variant therapeutic interventions.

The lectin receptors Clec4g and CD209c bind to the glycosylated SARS‐CoV‐2 Spike protein to interfere with Spike binding to cell surfaces and SARS‐CoV‐2 infection.  

[end paper 40]

[begin paper 41]

PMCID = 10985062

Title = Immune Epitopes of SARS-CoV-2 Spike Protein and Considerations for Universal Vaccine Development

Despite the success of global vaccination programs in slowing the spread of COVID-19, these efforts have been hindered by the emergence of new SARS-CoV-2 strains capable of evading prior immunity. The mutation and evolution of SARS-CoV-2 have created a demand for persistent efforts in vaccine development. SARS-CoV-2 Spike protein has been the primary target for COVID-19 vaccine development, but it is also the hotspot of mutations directly involved in host susceptibility and virus immune evasion. Our ability to predict emerging mutants and select conserved epitopes is critical for the development of a broadly neutralizing therapy or a universal vaccine. In this article, we review the general paradigm of immune responses to COVID-19 vaccines, highlighting the immunological epitopes of Spike protein that are likely associated with eliciting protective immunity resulting from vaccination in humans. Specifically, we analyze the structural and evolutionary characteristics of the SARS-CoV-2 Spike protein related to immune activation and function via the TLRs, B cells, and T cells. We aim to provide a comprehensive analysis of immune epitopes of Spike protein, thereby contributing to the development of new strategies for broad neutralization or universal vaccination.

[end paper 41]

[begin paper 42]

PMCID = 10120727

Title = Murine Alveolar Macrophages Rapidly Accumulate Intranasally Administered SARS-CoV-2 Spike Protein leading to Neutrophil Recruitment and Damage

The trimeric SARS-CoV-2 Spike protein mediates viral attachment facilitating cell entry. Most COVID-19 vaccines direct mammalian cells to express the Spike protein or deliver it directly via inoculation to engender a protective immune response. The trafficking and cellular tropism of the Spike protein in vivo and its impact on immune cells remains incompletely elucidated. In this study we inoculated mice intranasally, intravenously, and subcutaneously with fluorescently labeled recombinant SARS-CoV-2 Spike protein. Using flow cytometry and imaging techniques we analyzed its localization, immune cell tropism, and acute functional impact. Intranasal administration led to rapid lung alveolar macrophage uptake, pulmonary vascular leakage, and neutrophil recruitment and damage. When injected near the inguinal lymph node medullary, but not subcapsular macrophages, captured the protein, while scrotal injection recruited and fragmented neutrophils. Wide-spread endothelial and liver Kupffer cell uptake followed intravenous administration. Human peripheral blood cells B cells, neutrophils, monocytes, and myeloid dendritic cells all efficiently bound Spike protein. Exposure to the Spike protein enhanced neutrophil NETosis and augmented human macrophage TNF-α and IL-6 production. Human and murine immune cells employed C-type lectin receptors and Siglecs to help capture the Spike protein. This study highlights the potential toxicity of the SARS-CoV-2 Spike protein for mammalian cells and illustrates the central role for alveolar macrophage in pathogenic protein uptake.

[end paper 42]

[begin paper 43]

PMCID = 10588992

Title = Antibodies targeting a quaternary site on SARS-CoV-2 spike glycoprotein prevent viral receptor engagement by conformational locking

SARS-CoV-2 continues to evolve, with many variants evading clinically authorized antibodies. To isolate monoclonal antibodies (mAbs) with broadly neutralizing capacities against the virus, we screened serum samples from convalescing COVID-19 patients. We isolated two mAbs, 12-16 and 12-19, which neutralized all SARS-CoV-2 variants tested, including the XBB subvariants, and prevented infection in hamsters challenged with Omicron BA.1 intranasally. Structurally, both antibodies targeted a conserved quaternary epitope located at the interface between the N-terminal domain and subdomain 1, uncovering a site of vulnerability on SARS-CoV-2 spike. These antibodies prevented viral receptor engagement by locking the receptor-binding domain (RBD) of spike in the down conformation, revealing a mechanism of virus neutralization for non-RBD antibodies. Deep mutational scanning showed that SARS-CoV-2 could mutate to escape 12-19, but such mutations are rarely found in circulating viruses. Antibodies 12-16 and 12-19 hold promise as prophylactic agents for immunocompromised persons who do not respond robustly to COVID-19 vaccines.

Isolated bnAbs 12-16 and 12-19 from a SARS-CoV-2 recovered/vaccinated individual

These mAbs target a conserved quaternary epitope at the interface between NTD-SD1

The mAbs neutralize all current SARS-CoV-2 VOCs by locking RBD in down conformation

12-19 escape mutations are rarely found in circulating SARS-CoV-2 viruses

Current variants of SARS-CoV-2 can evade clinically authorized antibodies. Liu et al. demonstrate that two monoclonal antibodies isolated from convalescing COVID-19 patients neutralize all current SARS-CoV-2 variants of concern via interaction with a mechanism that locks the RBD in the down conformation. Mutations in the epitope targeted by these mAbs are rarely found in circulating SARS-CoV-2 viruses, suggesting clinical applicability.

[end paper 43]

[begin paper 44]

PMCID = 7751883

Title = The SARS-CoV-2 Spike protein has a broad tropism for mammalian ACE2 proteins

SARS Coronavirus 2 (SARS-CoV-2) emerged in late 2019, leading to the Coronavirus Disease 2019 (COVID-19) pandemic that continues to cause significant global mortality in human populations. Given its sequence similarity to SARS-CoV, as well as related coronaviruses circulating in bats, SARS-CoV-2 is thought to have originated in Chiroptera species in China. However, whether the virus spread directly to humans or through an intermediate host is currently unclear, as is the potential for this virus to infect companion animals, livestock, and wildlife that could act as viral reservoirs. Using a combination of surrogate entry assays and live virus, we demonstrate that, in addition to human angiotensin-converting enzyme 2 (ACE2), the Spike glycoprotein of SARS-CoV-2 has a broad host tropism for mammalian ACE2 receptors, despite divergence in the amino acids at the Spike receptor binding site on these proteins. Of the 22 different hosts we investigated, ACE2 proteins from dog, cat, and cattle were the most permissive to SARS-CoV-2, while bat and bird ACE2 proteins were the least efficiently used receptors. The absence of a significant tropism for any of the 3 genetically distinct bat ACE2 proteins we examined indicates that SARS-CoV-2 receptor usage likely shifted during zoonotic transmission from bats into people, possibly in an intermediate reservoir. Comparison of SARS-CoV-2 receptor usage to the related coronaviruses SARS-CoV and RaTG13 identified distinct tropisms, with the 2 human viruses being more closely aligned. Finally, using bioinformatics, structural data, and targeted mutagenesis, we identified amino acid residues within the Spike–ACE2 interface, which may have played a pivotal role in the emergence of SARS-CoV-2 in humans. The apparently broad tropism of SARS-CoV-2 at the point of viral entry confirms the potential risk of infection to a wide range of companion animals, livestock, and wildlife.

A study using a combination of surrogate entry assays and live virus suggests that SARS-CoV-2 may have a broad host-range, revealing that the virus's spike protein can use a broad range of host ACE2 receptors to enter cells and that the sequence of this protein might have changed during the zoonotic jump into humans.

[end paper 44]

[begin paper 45]

PMCID = 10384293

Title = SARS-CoV-2 Spike Protein Is Capable of Inducing Cell–Cell Fusions Independent from Its Receptor ACE2 and This Activity Can Be Impaired by Furin Inhibitors or a Subset of Monoclonal Antibodies

Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), which was responsible for the COVID-19 pandemic, efficiently spreads cell-to-cell through mechanisms facilitated by its membrane glycoprotein spike. We established a dual split protein (DSP) assay based on the complementation of GFP and luciferase to quantify the fusogenic activity of the SARS-CoV-2 spike protein. We provide several lines of evidence that the spike protein of SARS-CoV-2, but not SARS-CoV-1, induced cell–cell fusion even in the absence of its receptor, angiotensin-converting enzyme 2 (ACE2). This poorly described ACE2-independent cell fusion activity of the spike protein was strictly dependent on the proteasomal cleavage of the spike by furin while TMPRSS2 was dispensable. Previous and current variants of concern (VOCs) differed significantly in their fusogenicity. The Delta spike was extremely potent compared to Alpha, Beta, Gamma and Kappa, while the Omicron spike was almost devoid of receptor-independent fusion activity. Nonetheless, for all analyzed variants, cell fusion was dependent on furin cleavage and could be pharmacologically inhibited with CMK. Mapping studies revealed that amino acids 652-1273 conferred the ACE2-independent fusion activity of the spike. Unexpectedly, residues proximal to the furin cleavage site were not of major relevance, whereas residue 655 critically regulated fusion. Finally, we found that the spike’s fusion activity in the absence of ACE2 could be inhibited by antibodies directed against its N-terminal domain (NTD) but not by antibodies targeting its receptor-binding domain (RBD). In conclusion, our BSL-1-compatible DSP assay allowed us to screen for inhibitors or antibodies that interfere with the spike’s fusogenic activity and may therefore contribute to both rational vaccine design and development of novel treatment options against SARS-CoV-2.

[end paper 45]

[begin paper 46]

PMCID = 9774211

Title = Surface-modified measles vaccines encoding oligomeric, fusion-stabilized SARS-CoV-2 spike glycoproteins bypass measles seropositivity, boosting neutralizing antibody responses to omicron and historical variants

Serum titers of SARS-CoV-2 neutralizing antibodies (nAb) correlate well with protection from symptomatic COVID-19, but decay rapidly in the months following vaccination or infection. In contrast, measles-protective nAb titers are life-long after measles vaccination, possibly due to persistence of the live-attenuated virus in lymphoid tissues. We therefore sought to generate a live recombinant measles vaccine capable of driving high SARS-CoV-2 nAb responses. Since previous clinical testing of a live measles vaccine encoding a SARS-CoV-2 spike glycoprotein resulted in suboptimal anti-spike antibody titers, our new vectors were designed to encode prefusion-stabilized SARS-CoV-2 spike glycoproteins, trimerized via an inserted peptide domain and displayed on a dodecahedral miniferritin scaffold. Additionally, to circumvent the blunting of vaccine efficacy by preformed anti-measles antibodies, we extensively modified the measles surface glycoproteins. Comprehensive in vivo mouse testing demonstrated potent induction of high titer nAb in measles-immune mice and confirmed the significant incremental contributions to overall potency afforded by prefusion stabilization, trimerization, and miniferritin-display of the SARS-CoV-2 spike glycoprotein, and vaccine resurfacing. In animals primed and boosted with a MeV vaccine encoding the ancestral SARS-CoV-2 spike, high titer nAb responses against ancestral virus strains were only weakly cross-reactive with the omicron variant. However, in primed animals that were boosted with a MeV vaccine encoding the omicron BA.1 spike, antibody titers to both ancestral and omicron strains were robustly elevated and the passive transfer of serum from these animals protected K18-ACE2 mice from infection and morbidity after exposure to BA.1 and WA1/2020 strains. Our results demonstrate that antigen engineering can enable the development of potent measles-based SARS-CoV-2 vaccine candidates.

[end paper 46]

[begin paper 47]

PMCID = 8724751

Title = Monoclonal antibodies for COVID-19 therapy and SARS-CoV-2 detection

The coronavirus disease 2019 (COVID-19) pandemic is an exceptional public health crisis that demands the timely creation of new therapeutics and viral detection. Owing to their high specificity and reliability, monoclonal antibodies (mAbs) have emerged as powerful tools to treat and detect numerous diseases. Hence, many researchers have begun to urgently develop Ab-based kits for the detection of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) and Ab drugs for use as COVID-19 therapeutic agents. The detailed structure of the SARS-CoV-2 spike protein is known, and since this protein is key for viral infection, its receptor-binding domain (RBD) has become a major target for therapeutic Ab development. Because SARS-CoV-2 is an RNA virus with a high mutation rate, especially under the selective pressure of aggressively deployed prophylactic vaccines and neutralizing Abs, the use of Ab cocktails is expected to be an important strategy for effective COVID-19 treatment. Moreover, SARS-CoV-2 infection may stimulate an overactive immune response, resulting in a cytokine storm that drives severe disease progression. Abs to combat cytokine storms have also been under intense development as treatments for COVID-19. In addition to their use as drugs, Abs are currently being utilized in SARS-CoV-2 detection tests, including antigen and immunoglobulin tests. Such Ab-based detection tests are crucial surveillance tools that can be used to prevent the spread of COVID-19. Herein, we highlight some key points regarding mAb-based detection tests and treatments for the COVID-19 pandemic.

[end paper 47]

[begin paper 48]

PMCID = 10324094

Title = Evolution of Sequence and Structure of SARS-CoV-2 Spike Protein: A Dynamic Perspective

Novel coronavirus (SARS-CoV-2) enters its host cell through a surface spike protein. The viral spike protein has undergone several modifications/mutations at the genomic level, through which it modulated its structure–function and passed through several variants of concern. Recent advances in high-resolution structure determination and multiscale imaging techniques, cost-effective next-generation sequencing, and development of new computational methods (including information theory, statistical methods, machine learning, and many other artificial intelligence-based techniques) have hugely contributed to the characterization of sequence, structure, function of spike proteins, and its different variants to understand viral pathogenesis, evolutions, and transmission. Laying on the foundation of the sequence–structure–function paradigm, this review summarizes not only the important findings on structure/function but also the structural dynamics of different spike components, highlighting the effects of mutations on them. As dynamic fluctuations of three-dimensional spike structure often provide important clues for functional modulation, quantifying time-dependent fluctuations of mutational events over spike structure and its genetic/amino acidic sequence helps identify alarming functional transitions having implications for enhanced fusogenicity and pathogenicity of the virus. Although these dynamic events are more difficult to capture than quantifying a static, average property, this review encompasses those challenging aspects of characterizing the evolutionary dynamics of spike sequence and structure and their implications for functions.

[end paper 48]

[begin paper 49]

PMCID = 9257560

Title = A panel of nanobodies recognizing conserved hidden clefts of all SARS-CoV-2 spike variants including Omicron

We are amid the historic coronavirus infectious disease 2019 (COVID-19) pandemic. Imbalances in the accessibility of vaccines, medicines, and diagnostics among countries, regions, and populations, and those in war crises, have been problematic. Nanobodies are small, stable, customizable, and inexpensive to produce. Herein, we present a panel of nanobodies that can detect the spike proteins of five SARS-CoV-2 variants of concern (VOCs) including Omicron. Here we show via ELISA, lateral flow, kinetic, flow cytometric, microscopy, and Western blotting assays that our nanobodies can quantify the spike variants. This panel of nanobodies broadly neutralizes viral infection caused by pseudotyped and authentic SARS-CoV-2 VOCs. Structural analyses show that the P86 clone targets epitopes that are conserved yet unclassified on the receptor-binding domain (RBD) and contacts the N-terminal domain (NTD). Human antibodies rarely access both regions; consequently, the clone buries hidden crevasses of SARS-CoV-2 spike proteins that go undetected by conventional antibodies.

A panel of nanobodies are presented that can detect the spike proteins of five SARS-CoV-2 variants of concern and structural analyses show that one clone targets conserved epitopes on the receptor-binding domain and contacts the N-terminal domain.

[end paper 49]

[begin paper 50]

PMCID = 11612383

Title = Tight junction protein LSR is a host defense factor against SARS-CoV-2 infection in the small intestine

The identification of host factors with antiviral potential is important for developing effective prevention and therapeutic strategies against SARS-CoV-2 infection. Here, by using immortalized cell lines, intestinal organoids, ex vivo intestinal tissues and humanized ACE2 mouse model as proof-of-principle systems, we have identified lipolysis-stimulated lipoprotein receptor (LSR) as a crucial host defense factor against SARS-CoV-2 infection in the small intestine. Loss of endogenous LSR enhances ACE2-dependent infection by SARS-CoV-2 Spike (S) protein-pseudotyped virus and authentic SARS-CoV-2 virus, and exogenous administration of LSR protects against viral infection. Mechanistically, LSR interacts with ACE2 both in cis and in trans, preventing its binding to S protein, and thus inhibiting viral entry and S protein-mediated cell–cell fusion. Finally, a small LSR-derived peptide blocks S protein binding to the ACE2 receptor in vitro. These results identify both a previously unknown function for LSR in antiviral host defense against SARS-CoV-2, with potential implications for peptide-based pan-variant therapeutic interventions.

Host cell factors that affect the interaction of SARS-CoV-2 Spike (S) protein with its receptor ACE2 can modulate SARS-CoV-2 infection. This study shows that lipolysis-stimulated lipoprotein receptor (LSR) acts as a defense factor against SARS-CoV-2 by impairing S protein binding to ACE2.

LSR suppresses SARS-CoV-2 infection in the small intestine.

LSR blocks viral entry and restricts S protein-mediated cell–cell fusion.

LSR interacts with ACE2 both in cis and in trans, preventing its binding to S protein.

Lipolysis-stimulated lipoprotein receptor (LSR) and its peptide derivative inhibit SARS-CoV-2 entry into host cells by blocking interaction between viral Spike protein and its ACE2 receptor.

[end paper 50]

[begin paper 51]

PMCID = 8827021

Title = Analysis of Glycosylation and Disulfide Bonding of Wild-Type SARS-CoV-2 Spike Glycoprotein

The SARS-CoV-2 coronavirus, the etiologic agent of COVID-19, uses its spike (S) glycoprotein anchored in the viral membrane to enter host cells. The S glycoprotein is the major target for neutralizing antibodies elicited by natural infection and by vaccines. Approximately 35% of the SARS-CoV-2 S glycoprotein consists of carbohydrate, which can influence virus infectivity and susceptibility to antibody inhibition. We found that virus-like particles produced by coexpression of SARS-CoV-2 S, M, E, and N proteins contained spike glycoproteins that were extensively modified by complex carbohydrates. We used a fucose-selective lectin to purify the Golgi-modified fraction of a wild-type SARS-CoV-2 S glycoprotein trimer and determined its glycosylation and disulfide bond profile. Compared with soluble or solubilized S glycoproteins modified to prevent proteolytic cleavage and to retain a prefusion conformation, more of the wild-type S glycoprotein N-linked glycans are processed to complex forms. Even Asn 234, a significant percentage of which is decorated by high-mannose glycans on other characterized S trimer preparations, is predominantly modified in the Golgi compartment by processed glycans. Three incompletely occupied sites of O-linked glycosylation were detected. Viruses pseudotyped with natural variants of the serine/threonine residues implicated in O-linked glycosylation were generally infectious and exhibited sensitivity to neutralization by soluble ACE2 and convalescent antisera comparable to that of the wild-type virus. Unlike other natural cysteine variants, a Cys15Phe (C15F) mutant retained partial, but unstable, infectivity. These findings enhance our understanding of the Golgi processing of the native SARS-CoV-2 S glycoprotein carbohydrates and could assist the design of interventions.

IMPORTANCE The SARS-CoV-2 coronavirus, which causes COVID-19, uses its spike glycoprotein to enter host cells. The viral spike glycoprotein is the main target of host neutralizing antibodies that help to control SARS-CoV-2 infection and are important for the protection provided by vaccines. The SARS-CoV-2 spike glycoprotein consists of a trimer of two subunits covered with a coat of carbohydrates (sugars). Here, we describe the disulfide bonds that assist the SARS-CoV-2 spike glycoprotein to assume the correct shape and the composition of the sugar moieties on the glycoprotein surface. We also evaluate the consequences of natural virus variation in O-linked sugar addition and in the cysteine residues involved in disulfide bond formation. This information can expedite the improvement of vaccines and therapies for COVID-19.

[end paper 51]

[begin paper 52]

PMCID = 10683510

Title = Structural understanding of SARS-CoV-2 virus entry to host cells

Coronavirus disease 2019 (COVID-19), caused by the severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), is a major global health concern associated with millions of fatalities worldwide. Mutant variants of the virus have further exacerbated COVID-19 mortality and infection rates, emphasizing the urgent need for effective preventive strategies. Understanding the viral infection mechanism is crucial for developing therapeutics and vaccines. The entry of SARS-CoV-2 into host cells is a key step in the infection pathway and has been targeted for drug development. Despite numerous reviews of COVID-19 and the virus, there is a lack of comprehensive reviews focusing on the structural aspects of viral entry. In this review, we analyze structural changes in Spike proteins during the entry process, dividing the entry process into prebinding, receptor binding, proteolytic cleavage, and membrane fusion steps. By understanding the atomic-scale details of viral entry, we can better target the entry step for intervention strategies. We also examine the impacts of mutations in Spike proteins, including the Omicron variant, on viral entry. Structural information provides insights into the effects of mutations and can guide the development of therapeutics and vaccines. Finally, we discuss available structure-based approaches for the development of therapeutics and vaccines. Overall, this review provides a detailed analysis of the structural aspects of SARS-CoV-2 viral entry, highlighting its significance in the development of therapeutics and vaccines against COVID-19. Therefore, our review emphasizes the importance of structural information in combating SARS-CoV-2 infection.

[end paper 52]

[begin paper 53]

PMCID = 8341613

Title = Signatures in SARS-CoV-2 spike protein conferring escape to neutralizing antibodies

Understanding SARS-CoV-2 evolution and host immunity is critical to control COVID-19 pandemics. At the core is an arms-race between SARS-CoV-2 antibody and angiotensin-converting enzyme 2 (ACE2) recognition, a function of the viral protein spike. Mutations in spike impacting antibody and/or ACE2 binding are appearing worldwide, imposing the need to monitor SARS-CoV2 evolution and dynamics in the population. Determining signatures in SARS-CoV-2 that render the virus resistant to neutralizing antibodies is critical. We engineered 25 spike-pseudotyped lentiviruses containing individual and combined mutations in the spike protein, including all defining mutations in the variants of concern, to identify the effect of single and synergic amino acid substitutions in promoting immune escape. We confirmed that E484K evades antibody neutralization elicited by infection or vaccination, a capacity augmented when complemented by K417N and N501Y mutations. In silico analysis provided an explanation for E484K immune evasion. E484 frequently engages in interactions with antibodies but not with ACE2. Importantly, we identified a novel amino acid of concern, S494, which shares a similar pattern. Using the already circulating mutation S494P, we found that it reduces antibody neutralization of convalescent and post-immunization sera, particularly when combined with E484K and with mutations able to increase binding to ACE2, such as N501Y. Our analysis of synergic mutations provides a signature for hotspots for immune evasion and for targets of therapies, vaccines and diagnostics.

For a SARS-CoV-2 virion to enter a cell, the spike protein displayed at its surface must be recognized by the host ACE2 receptor. Serum neutralizing antibodies, shown to develop upon natural SARS-CoV-2 infection or vaccination, bind spike protein preventing the recognition by ACE2 and, consequently, infection. However, SARS-CoV-2 virus is constantly evolving, and can acquire mutations in spike that render this protein resistant to neutralizing antibodies and make vaccines ineffective. In this paper, we tested how single and a combination of mutations naturally occurring in spike, including in variants of concern, would synergize to affect antibody neutralizing capacity. We then integrated these findings with in silico analyses of amino acids binding to ACE2 and antibodies, and distributed them in a grid as amino acids important for binding to ACE2 or antibodies, or both. We found that changes in amino such as E484 and S494, which frequently interact with antibodies but not with ACE2, promptly evolve immune escape mutants, elicited by infection or vaccination, if the mutation severely alters the binding specificity of the antibody. Our work also suggests that the combination of these mutations with others promoting ACE2 binding, such as N501Y, increases their ability to escape neutralizing-antibody responses.

[end paper 53]

[begin paper 54]

PMCID = 10013841

Title = Cyanovirin-N binds to select SARS-CoV-2 spike oligosaccharides outside of the receptor binding domain and blocks infection by SARS-CoV-2

The antiviral lectin cyanovirin-N (CV-N) is shown to have potent activity against the syndromecoronavirus 2 (SARS-CoV-2) virus. CV-N showed improved binding and potency against more recent SARS-CoV-2 variants of concern and is shown to be able to reduce the severity of SARS-CoV-2 infections in test animals. The mechanism of action for CV-N is distinct from that of currently used anti-COVID therapeutics or from common vaccine targets on the receptor binding domain. CV-N is a potential broad-spectrum agent against infection from SARS-CoV-2.

Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) is an enveloped positive stranded RNA virus which has caused the recent deadly pandemic called COVID-19. The SARS-CoV-2 virion is coated with a heavily glycosylated Spike glycoprotein which is responsible for attachment and entry into target cells. One, as yet unexploited strategy for preventing SARS-CoV-2 infections, is the targeting of the glycans on Spike. Lectins are carbohydrate-binding proteins produced by plants, algae, and cyanobacteria. Some lectins can neutralize enveloped viruses displaying external glycoproteins, offering an alternative therapeutic approach for the prevention of infection with virulent β-coronaviruses, such as SARS-CoV-2. Here we show that the cyanobacterial lectin cyanovirin-N (CV-N) can selectively target SARS-CoV-2 Spike oligosaccharides and inhibit SARS-CoV-2 infection in vitro and in vivo. CV-N neutralizes Delta and Omicron variants in vitro better than earlier circulating viral variants. CV-N binds selectively to Spike with a Kd as low as 15 nM and a stoichiometry of 2 CV-N: 1 Spike but does not bind to the receptor binding domain (RBD). Further mapping of CV-N binding sites on Spike shows that select high-mannose oligosaccharides in the S1 domain of Spike are targeted by CV-N. CV-N also reduced viral loads in the nares and lungs in vivo to protect hamsters against a lethal viral challenge. In summary, we present an anti-coronavirus agent that works by an unexploited mechanism and prevents infection by a broad range of SARS-CoV-2 strains.

[end paper 54]

[begin paper 55]

PMCID = 8879608

Title = Phage-Displayed Mimotopes of SARS-CoV-2 Spike Protein Targeted to Authentic and Alternative Cellular Receptors

The evolution of the SARS-CoV-2 virus during the COVID-19 pandemic was accompanied by the emergence of new heavily mutated viral variants with increased infectivity and/or resistance to detection by the human immune system. To respond to the urgent need for advanced methods and materials to empower a better understanding of the mechanisms of virus’s adaptation to human host cells and to the immuno-resistant human population, we suggested using recombinant filamentous bacteriophages, displaying on their surface foreign peptides termed “mimotopes”, which mimic the structure of viral receptor-binding sites on the viral spike protein and can serve as molecular probes in the evaluation of molecular mechanisms of virus infectivity. In opposition to spike-binding antibodies that are commonly used in studying the interaction of the ACE2 receptor with SARS-CoV-2 variants in vitro, phage spike mimotopes targeted to other cellular receptors would allow discovery of their role in viral infection in vivo using cell culture, tissue, organs, or the whole organism. Phage mimotopes of the SARS-CoV-2 Spike S1 protein have been developed using a combination of phage display and molecular mimicry concepts, termed here “phage mimicry”, supported by bioinformatics methods. The key elements of the phage mimicry concept include: (1) preparation of a collection of p8-type (landscape) phages, which interact with authentic active receptors of live human cells, presumably mimicking the binding interactions of human coronaviruses such as SARS-CoV-2 and its variants; (2) discovery of closely related amino acid clusters with similar 3D structural motifs on the surface of natural ligands (FGF1 and NRP1), of the model receptor of interest FGFR and the S1 spike protein; and (3) an ELISA analysis of the interaction between candidate phage mimotopes with FGFR3 (a potential alternative receptor) in comparison with ACE2 (the authentic receptor).

[end paper 55]

[begin paper 56]

PMCID = 9016215

Title = Mitoxantrone modulates a heparan sulfate-spike complex to inhibit SARS-CoV-2 infection

Spike-mediated entry of SARS-CoV-2 into human airway epithelial cells is an attractive therapeutic target for COVID-19. In addition to protein receptors, the SARS-CoV-2 spike (S) protein also interacts with heparan sulfate, a negatively charged glycosaminoglycan (GAG) attached to certain membrane proteins on the cell surface. This interaction facilitates the engagement of spike with a downstream receptor to promote viral entry. Here, we show that Mitoxantrone, an FDA-approved topoisomerase inhibitor, targets a heparan sulfate-spike complex to compromise the fusogenic function of spike in viral entry. As a single agent, Mitoxantrone inhibits the infection of an authentic SARS-CoV-2 strain in a cell-based model and in human lung EpiAirway 3D tissues. Gene expression profiling supports the plasma membrane as a major target of Mitoxantrone but also underscores an undesired activity targeting nucleosome dynamics. We propose that Mitoxantrone analogs bearing similar heparan sulfate-binding activities but with reduced affinity for DNA topoisomerases may offer an alternative therapy to overcome breakthrough infections in the post-vaccine era.

[end paper 56]

[begin paper 57]

PMCID = 10695562

Title = Lys417 acts as a molecular switch that regulates the conformation of SARS-CoV-2 spike protein

SARS-CoV-2 spike protein plays a key role in mediating viral entry and inducing host immune responses. It can adopt either an open or closed conformation based on the position of its receptor-binding domain (RBD). It is yet unclear what causes these conformational changes or how they influence the spike’s functions. Here, we show that Lys417 in the RBD plays dual roles in the spike’s structure: it stabilizes the closed conformation of the trimeric spike by mediating inter-spike–subunit interactions; it also directly interacts with ACE2 receptor. Hence, a K417V mutation has opposing effects on the spike’s function: it opens up the spike for better ACE2 binding while weakening the RBD’s direct binding to ACE2. The net outcomes of this mutation are to allow the spike to bind ACE2 with higher probability and mediate viral entry more efficiently, but become more exposed to neutralizing antibodies. Given that residue 417 has been a viral mutational hotspot, SARS-CoV-2 may have been evolving to strike a balance between infection potency and immune evasion, contributing to its pandemic spread.

[end paper 57]

[begin paper 58]

PMCID = 8213968

Title = Extracellular vesicles carry SARS‐CoV‐2 spike protein and serve as decoys for neutralizing antibodies

In late 2019, a novel coronavirus named severe acute respiratory syndrome coronavirus 2 (SARS‐CoV‐2) emerged in Wuhan, China. SARS‐CoV‐2 and the disease it causes, coronavirus disease 2019 (COVID‐19), spread rapidly and became a global pandemic in early 2020. SARS‐CoV‐2 spike protein is responsible for viral entry and binds to angiotensin converting enzyme 2 (ACE2) on host cells, making it a major target of the immune system – particularly neutralizing antibodies (nAbs) that are induced by infection or vaccines. Extracellular vesicles (EVs) are small membraned particles constitutively released by cells, including virally‐infected cells. EVs and viruses enclosed within lipid membranes share some characteristics: they are small, sub‐micron particles and they overlap in cellular biogenesis and egress routes. Given their shared characteristics, we hypothesized that EVs released from spike‐expressing cells could carry spike and serve as decoys for anti‐spike nAbs, promoting viral infection. Here, using mass spectrometry and nanoscale flow cytometry (NFC) approaches, we demonstrate that SARS‐CoV‐2 spike protein can be incorporated into EVs. Furthermore, we show that spike‐carrying EVs act as decoy targets for convalescent patient serum‐derived nAbs, reducing their effectiveness in blocking viral entry. These findings have important implications for the pathogenesis of SARS‐CoV‐2 infection in vivo and highlight the complex interplay between viruses, extracellular vesicles, and the immune system that occurs during viral infections.

[end paper 58]

[begin paper 59]

PMCID = 8786652

Title = A Fc-enhanced NTD-binding non-neutralizing antibody delays virus spread and synergizes with a nAb to protect mice from lethal SARS-CoV-2 infection

Emerging evidence indicates that both neutralizing and Fc-mediated effector functions of antibodies contribute to protection against SARS-CoV-2. It is unclear whether Fc-effector functions alone can protect against SARS-CoV-2. Here, we isolated CV3-13, a non-neutralizing antibody, from a convalescent individual with potent Fc-mediated effector functions. The cryoelectron microscopy structure of CV3-13 in complex with the SARS-CoV-2 spike reveals that the antibody binds from a distinct angle of approach to an N-terminal domain (NTD) epitope that only partially overlaps with the NTD supersite recognized by neutralizing antibodies. CV3-13 does not alter the replication dynamics of SARS-CoV-2 in K18-hACE2 mice, but its Fc-enhanced version significantly delays virus spread, neuroinvasion, and death in prophylactic settings. Interestingly, the combination of Fc-enhanced non-neutralizing CV3-13 with Fc-compromised neutralizing CV3-25 completely protects mice from lethal SARS-CoV-2 infection. Altogether, our data demonstrate that efficient Fc-mediated effector functions can potently contribute to the in vivo efficacy of anti-SARS-CoV-2 antibodies.

The in vivo impact of non-nAbs on SARS-CoV-2 infection is unclear. Here, Beaudoin-Bussières et al. show that a Fc-enhanced version of non-nAb CV3-13 delays SARS-CoV-2 spread and death in mice. Fc-enhanced CV3-13 combined with a Fc-compromised nAb synergizes to protect mice, revealing the importance of non-nAbs during SARS-CoV-2 infection.

[end paper 59]

[begin paper 60]

PMCID = 10232722

Title = How helpful were molecular dynamics simulations in shaping our understanding of SARS-CoV-2 spike protein dynamics?

The SARS-CoV-2 spike protein (S) represents an important viral component that is required for successful viral infection in humans owing to its essential role in recognition of and entry to host cells. The spike is also an appealing target for drug designers who develop vaccines and antivirals. This article is important as it summarizes how molecular simulations successfully shaped our understanding of spike conformational behavior and its role in viral infection. MD simulations found that the higher affinity of SARS-CoV-2-S to ACE2 is linked to its unique residues that add extra electrostatic and van der Waal interactions in comparison to the SARS-CoV S. This illustrates the spread potential of the pandemic SARS-CoV-2 relative to the epidemic SARS-CoV. Different mutations at the S-ACE2 interface, which is believed to increase the transmission of the new variants, affected the behavior and binding interactions in different simulations. The contributions of glycans to the opening of S were revealed via simulations. The immune evasion of S was linked to the spatial distribution of glycans. This help the virus to escape the immune system recognition. This article is important as it summarizes how molecular simulations successfully shaped our understanding of spike conformational behavior and its role in viral infection. This will pave the way to us preparing for the next pandemic as the computational tools are tailored to help fight new challenges.

[end paper 60]

[begin paper 61]

PMCID = 10289268

Title = SARS-CoV-2 protein ORF8 limits expression levels of Spike antigen and facilitates immune evasion of infected host cells

Recovery from COVID-19 depends on the ability of the host to effectively neutralize virions and infected cells, a process largely driven by antibody-mediated immunity. However, with the newly emerging variants that evade Spike-targeting antibodies, re-infections and breakthrough infections are increasingly common. A full characterization of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) mechanisms counteracting antibody-mediated immunity is therefore needed. Here, we report that ORF8 is a virally encoded SARS-CoV-2 factor that controls cellular Spike antigen levels. We show that ORF8 limits the availability of mature Spike by inhibiting host protein synthesis and retaining Spike at the endoplasmic reticulum, reducing cell-surface Spike levels and recognition by anti-SARS-CoV-2 antibodies. In conditions of limited Spike availability, we found ORF8 restricts Spike incorporation during viral assembly, reducing Spike levels in virions. Cell entry of these virions then leaves fewer Spike molecules at the cell surface, limiting antibody recognition of infected cells. Based on these findings, we propose that SARS-CoV-2 variants may adopt an ORF8-dependent strategy that facilitates immune evasion of infected cells for extended viral production.

[end paper 61]

[begin paper 62]

PMCID = 7978432

Title = Single-component, self-assembling, protein nanoparticles presenting the receptor binding domain and stabilized spike as SARS-CoV-2 vaccine candidates

SARS-CoV-2 receptor binding domain and S2GΔHR2 spike elicited potent immune responses when displayed on protein nanoparticles.

Vaccination against SARS-CoV-2 provides an effective tool to combat the COVID-19 pandemic. Here, we combined antigen optimization and nanoparticle display to develop vaccine candidates for SARS-CoV-2. We first displayed the receptor-binding domain (RBD) on three self-assembling protein nanoparticle (SApNP) platforms using the SpyTag/SpyCatcher system. We then identified heptad repeat 2 (HR2) in S2 as the cause of spike metastability, designed an HR2-deleted glycine-capped spike (S2GΔHR2), and displayed S2GΔHR2 on SApNPs. An antibody column specific for the RBD enabled tag-free vaccine purification. In mice, the 24-meric RBD-ferritin SApNP elicited a more potent neutralizing antibody (NAb) response than the RBD alone and the spike with two stabilizing proline mutations in S2 (S2P). S2GΔHR2 elicited twofold higher NAb titers than S2P, while S2GΔHR2 SApNPs derived from multilayered E2p and I3-01v9 60-mers elicited up to 10-fold higher NAb titers. The S2GΔHR2-presenting I3-01v9 SApNP also induced critically needed T cell immunity, thereby providing a promising vaccine candidate.

[end paper 62]

[begin paper 63]

PMCID = 8910562

Title = A Deadly Embrace: Hemagglutination Mediated by SARS-CoV-2 Spike Protein at Its 22 N-Glycosylation Sites, Red Blood Cell Surface Sialoglycoproteins, and Antibody

Rouleaux (stacked clumps) of red blood cells (RBCs) observed in the blood of COVID-19 patients in three studies call attention to the properties of several enveloped virus strains dating back to seminal findings of the 1940s. For COVID-19, key such properties are: (1) SARS-CoV-2 binds to RBCs in vitro and also in the blood of COVID-19 patients; (2) although ACE2 is its target for viral fusion and replication, SARS-CoV-2 initially attaches to sialic acid (SA) terminal moieties on host cell membranes via glycans on its spike protein; (3) certain enveloped viruses express hemagglutinin esterase (HE), an enzyme that releases these glycan-mediated bindings to host cells, which is expressed among betacoronaviruses in the common cold strains but not the virulent strains, SARS-CoV, SARS-CoV-2 and MERS. The arrangement and chemical composition of the glycans at the 22 N-glycosylation sites of SARS-CoV-2 spike protein and those at the sialoglycoprotein coating of RBCs allow exploration of specifics as to how virally induced RBC clumping may form. The in vitro and clinical testing of these possibilities can be sharpened by the incorporation of an existing anti-COVID-19 therapeutic that has been found in silico to competitively bind to multiple glycans on SARS-CoV-2 spike protein.

[end paper 63]

[begin paper 64]

PMCID = 11324024

Title = The histamine receptor H1 acts as an alternative receptor for SARS-CoV-2

Numerous host factors, in addition to human angiotensin-converting enzyme 2 (hACE2), have been identified as coreceptors of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), demonstrating broad viral tropism and diversified druggable potential. We and others have found that antihistamine drugs, particularly histamine receptor H1 (HRH1) antagonists, potently inhibit SARS-CoV-2 infection. In this study, we provided compelling evidence that HRH1 acts as an alternative receptor for SARS-CoV-2 by directly binding to the viral spike protein. HRH1 also synergistically enhanced hACE2-dependent viral entry by interacting with hACE2. Antihistamine drugs effectively prevent viral infection by competitively binding to HRH1, thereby disrupting the interaction between the spike protein and its receptor. Multiple inhibition assays revealed that antihistamine drugs broadly inhibited the infection of various SARS-CoV-2 mutants with an average IC50 of 2.4 µM. The prophylactic function of these drugs was further confirmed by authentic SARS-CoV-2 infection assays and humanized mouse challenge experiments, demonstrating the therapeutic potential of antihistamine drugs for combating coronavirus disease 19.

In addition to human angiotensin-converting enzyme 2, severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) can utilize alternative cofactors to facilitate viral entry. In this study, we discovered that histamine receptor H1 (HRH1) not only functions as an independent receptor for SARS-CoV-2 but also synergistically enhances ACE2-dependent viral entry by directly interacting with ACE2. Further studies have demonstrated that HRH1 facilitates the entry of SARS-CoV-2 by directly binding to the N-terminal domain of the spike protein. Conversely, antihistamine drugs, primarily HRH1 antagonists, can competitively bind to HRH1 and thereby prevent viral entry. These findings revealed that the administration of repurposable antihistamine drugs could be a therapeutic intervention to combat coronavirus disease 19.

[end paper 64]

[begin paper 65]

PMCID = 10059852

Title = SARS-CoV-2 Spike-Mediated Entry and Its Regulation by Host Innate Immunity

The constantly evolving severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) variants of concern (VOC) fuel the worldwide coronavirus disease (COVID-19) pandemic. The spike protein is essential for the SARS-CoV-2 viral entry and thus has been extensively targeted by therapeutic antibodies. However, mutations along the spike in SARS-CoV-2 VOC and Omicron subvariants have caused more rapid spread and strong antigenic drifts, rendering most of the current antibodies ineffective. Hence, understanding and targeting the molecular mechanism of spike activation is of great interest in curbing the spread and development of new therapeutic approaches. In this review, we summarize the conserved features of spike-mediated viral entry in various SARS-CoV-2 VOC and highlight the converging proteolytic processes involved in priming and activating the spike. We also summarize the roles of innate immune factors in preventing spike-driven membrane fusion and provide outlines for the identification of novel therapeutics against coronavirus infections.

[end paper 65]

[begin paper 66]

PMCID = 10663135

Title = The SARS-CoV-2 spike glycoprotein interacts with MAO-B and impairs mitochondrial energetics

SARS-CoV-2 infection is associated with both acute and post-acute neurological symptoms. Emerging evidence suggests that SARS-CoV-2 can alter mitochondrial metabolism, suggesting that changes in brain metabolism may contribute to the development of acute and post-acute neurological complications. Monoamine oxidase B (MAO-B) is a flavoenzyme located on the outer mitochondrial membrane that catalyzes the oxidative deamination of monoamine neurotransmitters. Computational analyses have revealed high similarity between the SARS-CoV-2 spike glycoprotein receptor binding domain on the ACE2 receptor and MAO-B, leading to the hypothesis that SARS-CoV-2 spike glycoprotein may alter neurotransmitter metabolism by interacting with MAO-B. Our results empirically establish that the SARS-CoV-2 spike glycoprotein interacts with MAO-B, leading to increased MAO-B activity in SH-SY5Y neuron-like cells. Common to neurodegenerative disease pathophysiological mechanisms, we also demonstrate that the spike glycoprotein impairs mitochondrial bioenergetics, induces oxidative stress, and perturbs the degradation of depolarized aberrant mitochondria through mitophagy. Our findings also demonstrate that SH-SY5Y neuron-like cells expressing the SARS-CoV-2 spike protein were more susceptible to MPTP-induced necrosis, likely necroptosis. Together, these results reveal novel mechanisms that may contribute to SARS-CoV-2-induced neurodegeneration.

The SARS-CoV-2 spike (S) glycoprotein interacts with and increases MAO-B activity.

SARS-CoV-2 S impairs mitochondrial bioenergetics and induces oxidative stress.

Impaired mitophagy results in the accumulation of aberrant mitochondria.

SARS-CoV-2 S increases the susceptibility to MPTP-induced necrosis in neuron-like cells.

[end paper 66]

[begin paper 67]

PMCID = 10197516

Title = Evolving spike-protein N-glycosylation in SARS-CoV-2 variants

Since >3 years, SARS-CoV-2 has plunged humans into a colossal pandemic. Henceforth, multiple waves of infection have swept through the human population, led by variants that were able to partially evade acquired immunity. The co-evolution of SARS-CoV-2 variants with human immunity provides an excellent opportunity to study the interaction between viral pathogens and their human hosts. The heavily N-glycosylated spike-protein of SARS-CoV-2 plays a pivotal role in initiating infection and is the target for host immune-response, both of which are impacted by host-installed N-glycans. Using highly-sensitive DeGlyPHER approach, we compared the N-glycan landscape on spikes of the SARS-CoV-2 Wuhan-Hu-1 strain to seven WHO-defined variants of concern/interest, using recombinantly expressed, soluble spike-protein trimers, sharing same stabilizing-mutations. We found that N-glycan processing is conserved at most sites. However, in multiple variants, processing of N-glycans from high mannose- to complex-type is reduced at sites N165, N343 and N616, implicated in spike-protein function.

[end paper 67]

[begin paper 68]

PMCID = 10265947

Title = Identification of broad, potent antibodies to functionally constrained regions of SARS-CoV-2 spike following a breakthrough infection

SARS-CoV-2 infections can result in diverse clinical outcomes, including severe disease. Monoclonal antibodies (mAbs) have been used therapeutically to treat infection, but the emergence of variants has compromised their efficacy. Thus, identifying mAbs that are more durable in the face of SARS-CoV-2 evolution is a pressing need. Here, we describe four mAbs isolated from a Delta-breakthrough infection that can potently neutralize diverse variants, including multiple Omicron variants. In addition, one mAb shows broader activity against coronaviruses. The breadth of these mAbs is due to their focus on highly conserved regions of the viral protein antigen, including regions that are required for the virus to enter the cell. These properties make them promising candidates for therapeutic use.

The antiviral benefit of antibodies can be compromised by viral escape especially for rapidly evolving viruses. Therefore, durable, effective antibodies must be both broad and potent to counter newly emerging, diverse strains. Discovery of such antibodies is critically important for SARS-CoV-2 as the global emergence of new variants of concern (VOC) has compromised the efficacy of therapeutic antibodies and vaccines. We describe a collection of broad and potent neutralizing monoclonal antibodies (mAbs) isolated from an individual who experienced a breakthrough infection with the Delta VOC. Four mAbs potently neutralize the Wuhan-Hu-1 vaccine strain, the Delta VOC, and also retain potency against the Omicron VOCs through BA.4/BA.5 in both pseudovirus-based and authentic virus assays. Three mAbs also retain potency to recently circulating VOCs XBB.1.5 and BQ.1.1 and one also potently neutralizes SARS-CoV-1. The potency of these mAbs was greater against Omicron VOCs than all but one of the mAbs that had been approved for therapeutic applications. The mAbs target distinct epitopes on the spike glycoprotein, three in the receptor-binding domain (RBD) and one in an invariant region downstream of the RBD in subdomain 1 (SD1). The escape pathways we defined at single amino acid resolution with deep mutational scanning show they target conserved, functionally constrained regions of the glycoprotein, suggesting escape could incur a fitness cost. Overall, these mAbs are unique in their breadth across VOCs, their epitope specificity, and include a highly potent mAb targeting a rare epitope outside of the RBD in SD1.

[end paper 68]

[begin paper 69]

PMCID = 8142859

Title = An infectivity-enhancing site on the SARS-CoV-2 spike protein targeted by antibodies

Antibodies against the receptor-binding domain (RBD) of the SARS-CoV-2 spike protein prevent SARS-CoV-2 infection. However, the effects of antibodies against other spike protein domains are largely unknown. Here, we screened a series of anti-spike monoclonal antibodies from coronavirus disease 2019 (COVID-19) patients and found that some of antibodies against the N-terminal domain (NTD) induced the open conformation of RBD and thus enhanced the binding capacity of the spike protein to ACE2 and infectivity of SARS-CoV-2. Mutational analysis revealed that all of the infectivity-enhancing antibodies recognized a specific site on the NTD. Structural analysis demonstrated that all infectivity-enhancing antibodies bound to NTD in a similar manner. The antibodies against this infectivity-enhancing site were detected at high levels in severe patients. Moreover, we identified antibodies against the infectivity-enhancing site in uninfected donors, albeit at a lower frequency. These findings demonstrate that not only neutralizing antibodies but also enhancing antibodies are produced during SARS-CoV-2 infection.

A subset of antibodies detected in patients with severe COVID-19 target a specific region of the N-terminal domain of the spike protein and enhance binding of the virus to the ACE2 receptor.

[end paper 69]

[begin paper 70]

PMCID = 8877688

Title = Allosteric Determinants of the SARS-CoV-2 Spike Protein Binding with Nanobodies: Examining Mechanisms of Mutational Escape and Sensitivity of the Omicron Variant

Structural and biochemical studies have recently revealed a range of rationally engineered nanobodies with efficient neutralizing capacity against the SARS-CoV-2 virus and resilience against mutational escape. In this study, we performed a comprehensive computational analysis of the SARS-CoV-2 spike trimer complexes with single nanobodies Nb6, VHH E, and complex with VHH E/VHH V nanobody combination. We combined coarse-grained and all-atom molecular simulations and collective dynamics analysis with binding free energy scanning, perturbation-response scanning, and network centrality analysis to examine mechanisms of nanobody-induced allosteric modulation and cooperativity in the SARS-CoV-2 spike trimer complexes with these nanobodies. By quantifying energetic and allosteric determinants of the SARS-CoV-2 spike protein binding with nanobodies, we also examined nanobody-induced modulation of escaping mutations and the effect of the Omicron variant on nanobody binding. The mutational scanning analysis supported the notion that E484A mutation can have a significant detrimental effect on nanobody binding and result in Omicron-induced escape from nanobody neutralization. Our findings showed that SARS-CoV-2 spike protein might exploit the plasticity of specific allosteric hotspots to generate escape mutants that alter response to binding without compromising activity. The network analysis supported these findings showing that VHH E/VHH V nanobody binding can induce long-range couplings between the cryptic binding epitope and ACE2-binding site through a broader ensemble of communication paths that is less dependent on specific mediating centers and therefore may be less sensitive to mutational perturbations of functional residues. The results suggest that binding affinity and long-range communications of the SARS-CoV-2 complexes with nanobodies can be determined by structurally stable regulatory centers and conformationally adaptable hotspots that are allosterically coupled and collectively control resilience to mutational escape.

[end paper 70]

[begin paper 71]

PMCID = 11666439

Title = Unraveling the impact of SARS-CoV-2 mutations on immunity: insights from innate immune recognition to antibody and T cell responses

Throughout the COVID-19 pandemic, the emergence of new viral variants has challenged public health efforts, often evading antibody responses generated by infections and vaccinations. This immune escape has led to waves of breakthrough infections, raising questions about the efficacy and durability of immune protection. Here we focus on the impact of SARS-CoV-2 Delta and Omicron spike mutations on ACE-2 receptor binding, protein stability, and immune response evasion. Delta and Omicron variants had 3–5 times higher binding affinities to ACE-2 than the ancestral strain (KDwt = 23.4 nM, KDDelta = 8.08 nM, KDBA.1 = 4.77 nM, KDBA.2 = 4.47 nM). The pattern recognition molecule mannose-binding lectin (MBL) has been shown to recognize the spike protein. Here we found that MBL binding remained largely unchanged across the variants, even after introducing mutations at single glycan sites. Although MBL binding decreased post-vaccination, it increased by 2.6-fold upon IgG depletion, suggesting a compensatory or redundant role in immune recognition. Notably, we identified two glycan sites (N717 and N801) as potentially essential for the structural integrity of the spike protein. We also evaluated the antibody and T cell responses. Neutralization by serum immunoglobulins was predominantly mediated by IgG rather than IgA and was markedly impaired against the Delta (5.8-fold decrease) and Omicron variants BA.1 (17.4-fold) and BA.2 (14.2-fold). T cell responses, initially conserved, waned rapidly within 3 months post-Omicron infection. Our data suggests that immune imprinting may have hindered antibody and T cell responses toward the variants. Overall, despite decreased antibody neutralization, MBL recognition and T cell responses were generally unaffected by the variants. These findings extend our understanding of the complex interplay between viral adaptation and immune response, underscoring the importance of considering MBL interactions, immune imprinting, and viral evolution dynamics in developing new vaccine and treatment strategies.

[end paper 71]

[begin paper 72]

PMCID = 9535765

Title = Evolutionary remodelling of N‐terminal domain loops fine‐tunes SARS‐CoV‐2 spike

The emergence of SARS‐CoV‐2 variants has exacerbated the COVID‐19 global health crisis. Thus far, all variants carry mutations in the spike glycoprotein, which is a critical determinant of viral transmission being responsible for attachment, receptor engagement and membrane fusion, and an important target of immunity. Variants frequently bear truncations of flexible loops in the N‐terminal domain (NTD) of spike; the functional importance of these modifications has remained poorly characterised. We demonstrate that NTD deletions are important for efficient entry by the Alpha and Omicron variants and that this correlates with spike stability. Phylogenetic analysis reveals extensive NTD loop length polymorphisms across the sarbecoviruses, setting an evolutionary precedent for loop remodelling. Guided by these analyses, we demonstrate that variations in NTD loop length, alone, are sufficient to modulate virus entry. We propose that variations in NTD loop length act to fine‐tune spike; this may provide a mechanism for SARS‐CoV‐2 to navigate a complex selection landscape encompassing optimisation of essential functionality, immune‐driven antigenic variation and ongoing adaptation to a new host.

The functional importance of the SARS‐CoV‐2 spike N‐terminal domain is poorly understood. This study demonstrates that length variation in flexible loops within the NTD can modulate spike activity to optimise SARS‐CoV‐2 entry. 

[end paper 72]

[begin paper 73]

PMCID = 8853550

Title = Structural and antigenic variations in the spike protein of emerging SARS-CoV-2 variants

The Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) virus is continuously evolving, and this poses a major threat to antibody therapies and currently authorized Coronavirus Disease 2019 (COVID-19) vaccines. It is therefore of utmost importance to investigate and predict the putative mutations on the spike protein that confer immune evasion. Antibodies are key components of the human immune system’s response to SARS-CoV-2, and the spike protein is a prime target of neutralizing antibodies (nAbs) as it plays critical roles in host cell recognition, fusion, and virus entry. The potency of therapeutic antibodies and vaccines partly depends on how readily the virus can escape neutralization. Recent structural and functional studies have mapped the epitope landscape of nAbs on the spike protein, which illustrates the footprints of several nAbs and the site of escape mutations. In this review, we discuss (1) the emerging SARS-CoV-2 variants; (2) the structural basis for antibody-mediated neutralization of SARS-CoV-2 and nAb classification; and (3) identification of the RBD escape mutations for several antibodies that resist antibody binding and neutralization. These escape maps are a valuable tool to predict SARS-CoV-2 fitness, and in conjunction with the structures of the spike-nAb complex, they can be utilized to facilitate the rational design of escape-resistant antibody therapeutics and vaccines.

[end paper 73]

[begin paper 74]

PMCID = 10974403

Title = Discordant Antigenic Properties of Soluble and Virion SARS-CoV-2 Spike Proteins

Efforts to develop vaccine and immunotherapeutic countermeasures against the COVID-19 pandemic focus on targeting the trimeric spike (S) proteins of SARS-CoV-2. Vaccines and therapeutic design strategies must impart the characteristics of virion S from historical and emerging variants onto practical constructs such as soluble, stabilized trimers. The virus spike is a heterotrimer of two subunits: S1, which includes the receptor binding domain (RBD) that binds the cell surface receptor ACE2, and S2, which mediates membrane fusion. Previous studies suggest that the antigenic, structural, and functional characteristics of virion S may differ from current soluble surrogates. For example, it was reported that certain anti-glycan, HIV-1 neutralizing monoclonal antibodies bind soluble SARS-CoV-2 S but do not neutralize SARS-CoV-2 virions. In this study, we used single-molecule fluorescence correlation spectroscopy (FCS) under physiologically relevant conditions to examine the reactivity of broadly neutralizing and non-neutralizing anti-S human monoclonal antibodies (mAbs) isolated in 2020. Binding efficiency was assessed by FCS with soluble S trimers, pseudoviruses and inactivated wild-type virions representing variants emerging from 2020 to date. Anti-glycan mAbs were tested and compared. We find that both anti-S specific and anti-glycan mAbs exhibit variable but efficient binding to a range of stabilized, soluble trimers. Across mAbs, the efficiencies of soluble S binding were positively correlated with reactivity against inactivated virions but not pseudoviruses. Binding efficiencies with pseudoviruses were generally lower than with soluble S or inactivated virions. Among neutralizing mAbs, potency did not correlate with binding efficiencies on any target. No neutralizing activity was detected with anti-glycan antibodies. Notably, the virion S released from membranes by detergent treatment gained more efficient reactivity with anti-glycan, HIV-neutralizing antibodies but lost reactivity with all anti-S mAbs. Collectively, the FCS binding data suggest that virion surfaces present appreciable amounts of both functional and nonfunctional trimers, with neutralizing anti-S favoring the former structures and non-neutralizing anti-glycan mAbs binding the latter. S released from solubilized virions represents a nonfunctional structure bound by anti-glycan mAbs, while engineered soluble trimers present a composite structure that is broadly reactive with both mAb types. The detection of disparate antigenicity and immunoreactivity profiles in engineered and virion-associated S highlight the value of single-virus analyses in designing future antiviral strategies against SARS-CoV-2.

[end paper 74]

[begin paper 75]

PMCID = 8181738

Title = Scrutinizing Coronaviruses Using Publicly Available Bioinformatic Tools: The Viral Structural Proteins as a Case Study

Since early 2020, the world suffers from a new beta-coronavirus, called SARS-CoV-2, that has devastating effects globally due to its associated disease, Covid-19. Until today, Covid-19, which not only causes life-threatening lung infections but also impairs various other organs and tissues, has killed hundreds of thousands of people and caused irreparable damage to many others. Since the very onset of the pandemic, huge efforts were made worldwide to fully understand this virus and numerous studies were, and still are, published. Many of these deal with structural analyses of the viral spike glycoprotein and with vaccine development, antibodies and antiviral molecules or immunomodulators that are assumed to become essential tools in the struggle against the virus. This paper summarizes knowledge on the properties of the four structural proteins (spike protein S, membrane protein M, envelope protein E and nucleocapsid protein N) of the SARS-CoV-2 virus and its relatives, SARS-CoV and MERS-CoV, that emerged few years earlier. Moreover, attention is paid to ways to analyze such proteins using freely available bioinformatic tools and, more importantly, to bring these proteins alive by looking at them on a computer/laptop screen with the easy-to-use but highly performant and interactive molecular graphics program DeepView. It is hoped that this paper will stimulate non-bioinformaticians and non-specialists in structural biology to scrutinize these and other macromolecules and as such will contribute to establishing procedures to fight these and maybe other forthcoming viruses.

[end paper 75]

[begin paper 76]

PMCID = 10963270

Title = High-throughput screening of genetic and cellular drivers of syncytium formation induced by the spike protein of SARS-CoV-2

Mapping mutations and discovering cellular determinants that cause the spike protein of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) to induce infected cells to form syncytia would facilitate the development of strategies for blocking the formation of such cell–cell fusion. Here we describe high-throughput screening methods based on droplet microfluidics and the size-exclusion selection of syncytia, coupled with large-scale mutagenesis and genome-wide knockout screening via clustered regularly interspaced short palindromic repeats (CRISPR), for the large-scale identification of determinants of cell–cell fusion. We used the methods to perform deep mutational scans in spike-presenting cells to pinpoint mutable syncytium-enhancing substitutions in two regions of the spike protein (the fusion peptide proximal region and the furin-cleavage site). We also used a genome-wide CRISPR screen in cells expressing the receptor angiotensin-converting enzyme 2 to identify inhibitors of clathrin-mediated endocytosis that impede syncytium formation, which we validated in hamsters infected with SARS-CoV-2. Finding genetic and cellular determinants of the formation of syncytia may reveal insights into the physiological and pathological consequences of cell–cell fusion.

High-throughput methods based on droplet microfluidics and size-exclusion selection allow for the identification of genetic and cellular drivers of syncytium formation induced by the spike protein of SARS-CoV-2 and of inhibitors of such cell–cell fusion.

[end paper 76]

[begin paper 77]

PMCID = 11727448

Title = Structural Immunology of SARS‐CoV‐2

The SARS‐CoV‐2 spike (S) protein has undergone significant evolution, enhancing both receptor binding and immune evasion. In this review, we summarize ongoing efforts to develop antibodies targeting various epitopes of the S protein, focusing on their neutralization potency, breadth, and escape mechanisms. Antibodies targeting the receptor‐binding site (RBS) typically exhibit high neutralizing potency but are frequently evaded by mutations in SARS‐CoV‐2 variants. In contrast, antibodies targeting conserved regions, such as the S2 stem helix and fusion peptide, exhibit broader reactivity but generally lower neutralization potency. However, several broadly neutralizing antibodies have demonstrated exceptional efficacy against emerging variants, including the latest omicron subvariants, underscoring the potential of targeting vulnerable sites such as RBS‐A and RBS‐D/CR3022. We also highlight public classes of antibodies targeting different sites on the S protein. The vulnerable sites targeted by public antibodies present opportunities for germline‐targeting vaccine strategies. Overall, developing escape‐resistant, potent antibodies and broadly effective vaccines remains crucial for combating future variants. This review emphasizes the importance of identifying key epitopes and utilizing antibody affinity maturation to inform future therapeutic and vaccine design.

[end paper 77]

[begin paper 78]

PMCID = 10222255

Title = Quantitative Mutation Analysis of Genes and Proteins of Major SARS-CoV-2 Variants of Concern and Interest

Of various SARS-CoV-2 variants, some have drawn special concern or interest because of their heightened disease threat. The mutability of individual SARS-CoV-2 genes/proteins presumably varies. The present study quantified gene/protein mutations in 13 major SARS-CoV-2 variants of concern/interest, and analyzed viral protein antigenicity using bioinformatics. The results from 187 carefully perused genome clones showed significantly higher mean percent mutations in the spike, ORF8, nucleocapsid, and NSP6 than in other viral proteins. The ORF8 and spike proteins also tolerated higher maximal percent mutations. The omicron variant presented more percent mutations in the NSP6 and structural proteins, whereas the delta featured more in the ORF7a. Omicron subvariant BA.2 exhibited more mutations in ORF6, and omicron BA.4 had more in NSP1, ORF6, and ORF7b, relative to omicron BA.1. Delta subvariants AY.4 and AY.5 bore more mutations in ORF7b and ORF8 than delta B.1.617.2. Predicted antigen ratios of SARS-CoV-2 proteins significantly vary (range: 38–88%). To overcome SARS-CoV-2 immune evasion, the relatively conserved, potentially immunogenic NSP4, NSP13, NSP14, membrane, and ORF3a viral proteins may serve as more suitable targets for molecular vaccines or therapeutics than the mutation-prone NSP6, spike, ORF8, or nucleocapsid protein. Further investigation into distinct mutations of the variants/subvariants may help understand SARS-CoV-2 pathogenesis.

[end paper 78]

[begin paper 79]

PMCID = 9519379

Title = A molecularly engineered, broad-spectrum anti-coronavirus lectin inhibits SARS-CoV-2 and MERS-CoV infection in vivo

“Pan-coronavirus” antivirals targeting conserved viral components can be designed. Here, we show that the rationally engineered H84T-banana lectin (H84T-BanLec), which specifically recognizes high mannose found on viral proteins but seldom on healthy human cells, potently inhibits Middle East respiratory syndrome coronavirus (MERS-CoV), severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) (including Omicron), and other human-pathogenic coronaviruses at nanomolar concentrations. H84T-BanLec protects against MERS-CoV and SARS-CoV-2 infection in vivo. Importantly, intranasally and intraperitoneally administered H84T-BanLec are comparably effective. Mechanistic assays show that H84T-BanLec targets virus entry. High-speed atomic force microscopy depicts real-time multimolecular associations of H84T-BanLec dimers with the SARS-CoV-2 spike trimer. Single-molecule force spectroscopy demonstrates binding of H84T-BanLec to multiple SARS-CoV-2 spike mannose sites with high affinity and that H84T-BanLec competes with SARS-CoV-2 spike for binding to cellular ACE2. Modeling experiments identify distinct high-mannose glycans in spike recognized by H84T-BanLec. The multiple H84T-BanLec binding sites on spike likely account for the drug compound’s broad-spectrum antiviral activity and the lack of resistant mutants.

H84T-BanLec inhibits human-pathogenic coronaviruses through inhibition of viral entry

H84T-BanLec protects against MERS-CoV and SARS-CoV-2 infections in vivo

H84T-BanLec binds to multiple SARS-CoV-2 spike high-mannose sites with high affinity

This unique mechanism likely accounts for H84T-BanLec’s broad-spectrum activity

Chan et al. investigate the antiviral activity and mechanism of H84T-BanLec against human-pathogenic coronaviruses. H84T-BanLec possesses pan-coronaviral antiviral activity through inhibition of viral entry and protects against MERS-CoV and SARS-CoV-2 infections in vivo. Binding of H84T-BanLec to multiple high-mannose glycans in spike likely accounts for its lack of resistant mutants.

[end paper 79]

[begin paper 80]

PMCID = 10136776

Title = SARS-CoV-2 Enters Human Leydig Cells and Affects Testosterone Production In Vitro

Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), a SARS-like coronavirus, continues to produce mounting infections and fatalities all over the world. Recent data point to SARS-CoV-2 viral infections in the human testis. As low testosterone levels are associated with SARS-CoV-2 viral infections in males and human Leydig cells are the main source of testosterone, we hypothesized that SARS-CoV-2 could infect human Leydig cells and impair their function. We successfully detected SARS-CoV-2 nucleocapsid in testicular Leydig cells of SARS-CoV-2-infected hamsters, providing evidence that Leydig cells can be infected with SARS-CoV-2. We then employed human Leydig-like cells (hLLCs) to show that the SARS-CoV-2 receptor angiotensin-converting enzyme 2 is highly expressed in hLLCs. Using a cell binding assay and a SARS-CoV-2 spike-pseudotyped viral vector (SARS-CoV-2 spike pseudovector), we showed that SARS-CoV-2 could enter hLLCs and increase testosterone production by hLLCs. We further combined the SARS-CoV-2 spike pseudovector system with pseudovector-based inhibition assays to show that SARS-CoV-2 enters hLLCs through pathways distinct from those of monkey kidney Vero E6 cells, a typical model used to study SARS-CoV-2 entry mechanisms. We finally revealed that neuropilin-1 and cathepsin B/L are expressed in hLLCs and human testes, raising the possibility that SARS-CoV-2 may enter hLLCs through these receptors or proteases. In conclusion, our study shows that SARS-CoV-2 can enter hLLCs through a distinct pathway and alter testosterone production.

[end paper 80]

[begin paper 81]

PMCID = 8939767

Title = A human antibody reveals a conserved site on beta-coronavirus spike proteins and confers protection against SARS-CoV-2 infection

Broadly neutralizing antibodies (bnAbs) to coronaviruses (CoVs) are valuable in their own right as prophylactic and therapeutic reagents to treat diverse CoVs and, importantly, as templates for rational pan-CoV vaccine design. We recently described a bnAb, CC40.8, from a coronavirus disease 2019 (COVID-19)-convalescent donor that exhibits broad reactivity with human beta-coronaviruses (β-CoVs). Here, we showed that CC40.8 targets the conserved S2 stem-helix region of the coronavirus spike fusion machinery. We determined a crystal structure of CC40.8 Fab with a SARS-CoV-2 S2 stem-peptide at 1.6 Å resolution and found that the peptide adopted a mainly helical structure. Conserved residues in β-CoVs interacted with CC40.8 antibody, thereby providing a molecular basis for its broad reactivity. CC40.8 exhibited in vivo protective efficacy against SARS-CoV-2 challenge in two animal models. In both models, CC40.8-treated animals exhibited less weight loss and reduced lung viral titers compared to controls. Furthermore, we noted CC40.8-like bnAbs are relatively rare in human COVID-19 infection and therefore their elicitation may require rational structure-based vaccine design strategies. Overall, our study describes a target on β-CoV spike proteins for protective antibodies that may facilitate the development of pan-β-CoV vaccines.

A human mAb isolated from a COVID-19 donor defines a protective cross-neutralizing epitope for pan-beta-coronavirus vaccine design strategies.

[end paper 81]

[begin paper 82]

PMCID = 7914343

Title = MERS-CoV and SARS-CoV-2 replication can be inhibited by targeting the interaction between the viral spike protein and the nucleocapsid protein

Background: The molecular interactions between viral proteins form the basis of virus production and can be used to develop strategies against virus infection. The interactions of the envelope proteins and the viral RNA-binding nucleocapsid (N) protein are essential for the assembly of coronaviruses including the Middle East respiratory syndrome coronavirus (MERS-CoV).

Methods: Using co-immunoprecipitation, immunostaining, and proteomics analysis, we identified a protein interacting with the spike (S) protein in the cells infected with MERS-CoV or SARS-CoV-2. To confirm the interaction, synthetic peptides corresponding to the C-terminal domain of the S protein (Spike CD) were produced and their effect on the interaction was investigated in vitro. In vivo effect of the Spike CD peptides after cell penetration was further investigated using viral plaque formation assay. Phylogeographic analyses were conducted to deduce homology of Spike CDs and N proteins.

Results: We identified a direct interaction between the S protein and the N protein of MERS-CoV that takes place during virus assembly in infected cells. Spike CD peptides of MERS-CoV inhibited the interaction between the S and N proteins in vitro. Furthermore, cell penetration by the synthetic Spike CD peptides inhibited viral plaque formation in MERS-CoV-infected cells. Phylogeographic analyses of Spike CDs and N proteins showed high homology among betacoronavirus lineage C strains. To determine if Spike CD peptides can inhibit the replication of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), we used the same strategy and found that the SARS-CoV-2 Spike CD peptide inhibited virus replication in SARS-CoV-2-infected cells.

Conclusions: We suggest that the interaction between the S protein and the N protein can be targeted to design new therapeutics against emerging coronaviruses, including SARS-CoV-2.

[end paper 82]

[begin paper 83]

PMCID = 10747160

Title = The Antiviral Activity of the Lectin Griffithsin against SARS-CoV-2 Is Enhanced by the Presence of Structural Proteins

Although COVID-19 transmission has been reduced by the advent of vaccinations and a variety of rapid monitoring techniques, the SARS-CoV-2 virus itself has shown a remarkable ability to mutate and persist. With this long track record of immune escape, researchers are still exploring prophylactic treatments to curtail future SARS-CoV-2 variants. Specifically, much focus has been placed on the antiviral lectin Griffithsin in preventing spike protein-mediated infection via the hACE2 receptor (direct infection). However, an oft-overlooked aspect of SARS-CoV-2 infection is viral capture by attachment receptors such as DC-SIGN, which is thought to facilitate the initial stages of COVID-19 infection in the lung tissue (called trans-infection). In addition, while immune escape is dictated by mutations in the spike protein, coronaviral virions also incorporate M, N, and E structural proteins within the particle. In this paper, we explored how several structural facets of both the SARS-CoV-2 virion and the antiviral lectin Griffithsin can affect and attenuate the infectivity of SARS-CoV-2 pseudovirus. We found that Griffithsin was a better inhibitor of hACE2-mediated direct infection when the coronaviral M protein is present compared to when it is absent (possibly providing an explanation regarding why Griffithsin shows better inhibition against authentic SARS-CoV-2 as opposed to pseudotyped viruses, which generally do not contain M) and that Griffithsin was not an effective inhibitor of DC-SIGN-mediated trans-infection. Furthermore, we found that DC-SIGN appeared to mediate trans-infection exclusively via binding to the SARS-CoV-2 spike protein, with no significant effect observed when other viral proteins (M, N, and/or E) were present. These results provide etiological data that may help to direct the development of novel antiviral treatments, either by leveraging Griffithsin binding to the M protein as a novel strategy to prevent SARS-CoV-2 infection or by narrowing efforts to inhibit trans-infection to focus on DC-SIGN binding to SARS-CoV-2 spike protein.

[end paper 83]

[begin paper 84]

PMCID = 10371867

Title = PLSCR1 is a cell-autonomous defence factor against SARS-CoV-2 infection

Understanding protective immunity to COVID-19 facilitates preparedness for future pandemics and combats new SARS-CoV-2 variants emerging in the human population. Neutralizing antibodies have been widely studied; however, on the basis of large-scale exome sequencing of protected versus severely ill patients with COVID-19, local cell-autonomous defence is also crucial. Here we identify phospholipid scramblase 1 (PLSCR1) as a potent cell-autonomous restriction factor against live SARS-CoV-2 infection in parallel genome-wide CRISPR–Cas9 screens of human lung epithelia and hepatocytes before and after stimulation with interferon-γ (IFNγ). IFNγ-induced PLSCR1 not only restricted SARS-CoV-2 USA-WA1/2020, but was also effective against the Delta B.1.617.2 and Omicron BA.1 lineages. Its robust activity extended to other highly pathogenic coronaviruses, was functionally conserved in bats and mice, and interfered with the uptake of SARS-CoV-2 in both the endocytic and the TMPRSS2-dependent fusion routes. Whole-cell 4Pi single-molecule switching nanoscopy together with bipartite nano-reporter assays found that PLSCR1 directly targeted SARS-CoV-2-containing vesicles to prevent spike-mediated fusion and viral escape. A PLSCR1 C-terminal β-barrel domain—but not lipid scramblase activity—was essential for this fusogenic blockade. Our mechanistic studies, together with reports that COVID-associated PLSCR1 mutations are found in some susceptible people, identify an anti-coronavirus protein that interferes at a late entry step before viral RNA is released into the host-cell cytosol.

Phospholipid scramblase 1 (PLSCR1), a protein induced by IFNγ, acts as a defence factor against SARS-CoV-2 and other coronaviruses by inhibiting the fusion of the virus with host-cell membranes.

[end paper 84]

[begin paper 85]

PMCID = 8297464

Title = The Spike of SARS-CoV-2: Uniqueness and Applications

The Spike (S) protein of the SARS-CoV-2 virus is critical for its ability to attach and fuse into the host cells, leading to infection, and transmission. In this review, we have initially performed a meta-analysis of keywords associated with the S protein to frame the outline of important research findings and directions related to it. Based on this outline, we have reviewed the structure, uniqueness, and origin of the S protein of SARS-CoV-2. Furthermore, the interactions of the Spike protein with host and its implications in COVID-19 pathogenesis, as well as drug and vaccine development, are discussed. We have also summarized the recent advances in detection methods using S protein-based RT-PCR, ELISA, point‐of‐care lateral flow immunoassay, and graphene-based field-effect transistor (FET) biosensors. Finally, we have also discussed the emerging Spike mutants and the efficacy of the Spike-based vaccines against those strains. Overall, we have covered most of the recent advances on the SARS-CoV-2 Spike protein and its possible implications in countering this virus.

[end paper 85]

[begin paper 86]

PMCID = 9890279

Title = A scalable and high yielding SARS-CoV-2 spike protein receptor binding domain production process

The Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) spike protein is of interest for the development of vaccines and therapeutics against COVID-19. Vaccines are designed to raise an immune response against the spike protein. Other therapies attempt to block the interaction of the spike protein and mammalian cells. Therefore, the spike protein itself and specific interacting regions of the spike protein are reagents required by industry to enable the advancement of medicines to combat SARS-CoV-2. Early production methods of the SARS-CoV-2 spike protein receptor binding domain (RBD) were labor intensive with scalability challenges. In this work, we describe a high yielding and scalable production process for the SARS-CoV-2 RBD. Expression was performed in human embryonic kidney (HEK) 293 cells followed by a two-column purification process including immobilized metal affinity chromatography (IMAC) followed by Ceramic Hydroxyapatite (CHT). The improved process showed good scalability, enabling efficient purification of 2.5 g of product from a 200 L scale bioreactor.

[end paper 86]

[begin paper 87]

PMCID = 9528568

Title = Broad tricyclic ring inhibitors block SARS-CoV-2 spike function required for viral entry

Entry of severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) into host cells requires binding of the viral spike protein to the angiotensin converting enzyme 2 (ACE2) receptor, which triggers subsequent conformational changes to facilitate viral and cellular fusion at the plasma membrane or following endocytosis. Here, we experimentally identified selective and broad inhibitors of SARS-CoV-2 entry that share a tricyclic ring (or similar) structure. Inhibitory effect was restricted to early steps during infection and the entry inhibitors interacted with the receptor binding domain of SARS-CoV-2 spike but did not significantly interfere with receptor (ACE2) binding. Instead, some of these compounds induced conformational changes or affected spike assembly and blocked SARS-CoV-2 spike cell-cell fusion activity. The broad inhibitors define a highly conserved binding pocket that is present on the spikes of SARS-CoV-1, SARS-CoV-2, and all circulating SARS-CoV-2 variants tested, and block SARS-CoV spike activity required for mediating viral entry. These compounds provide new insights into the SARS-CoV-2 spiks topography as well as into critical steps on the entry pathway, and can serve as lead candidates for the development of broad-range entry inhibitors against SARS-CoVs.

Synopsis: Tricyclic ring inhibitors (e.g., aminobenztropine) block SARS-CoV-2 entry into target cells.

[end paper 87]

[begin paper 88]

PMCID = 8284657

Title = Mutants of human ACE2 differentially promote SARS-CoV and SARS-CoV-2 spike mediated infection

SARS-CoV and SARS-CoV-2 encode spike proteins that bind human ACE2 on the cell surface to enter target cells during infection. A small fraction of humans encode variants of ACE2, thus altering the biochemical properties at the protein interaction interface. These and other ACE2 coding mutants can reveal how the spike proteins of each virus may differentially engage the ACE2 protein surface during infection. We created an engineered HEK 293T cell line for facile stable transgenic modification, and expressed the major human ACE2 allele or 28 of its missense mutants, 24 of which are possible through single nucleotide changes from the human reference sequence. Infection with SARS-CoV or SARS-CoV-2 spike pseudotyped lentiviruses revealed that high ACE2 cell-surface expression could mask the effects of impaired binding during infection. Drastically reducing ACE2 cell surface expression revealed a range of infection efficiencies across the panel of mutants. Our infection results revealed a non-linear relationship between soluble SARS-CoV-2 RBD binding to ACE2 and pseudovirus infection, supporting a major role for binding avidity during entry. While ACE2 mutants D355N, R357A, and R357T abrogated entry by both SARS-CoV and SARS-CoV-2 spike proteins, the Y41A mutant inhibited SARS-CoV entry much more than SARS-CoV-2, suggesting differential utilization of the ACE2 side-chains within the largely overlapping interaction surfaces utilized by the two CoV spike proteins. These effects correlated well with cytopathic effects observed during SARS-CoV-2 replication in ACE2-mutant cells. The panel of ACE2 mutants also revealed altered ACE2 surface dependencies by the N501Y spike variant, including a near-complete utilization of the K353D ACE2 variant, despite decreased infection mediated by the parental SARS-CoV-2 spike. Our results clarify the relationship between ACE2 abundance, binding, and infection, for various SARS-like coronavirus spike proteins and their mutants, and inform our understanding for how changes to ACE2 sequence may correspond with different susceptibilities to infection.

SARS-like coronaviruses, such as SARS-CoV-2, use their spike proteins to bind a common surface on the human ACE2 protein to gain entry and subsequently infect cells. We used site-specific genomic integration and expression of WT ACE2 or its missense variants, many of them previously observed in human exomes, to determine how ACE2 sequence and abundance correspond to infectability by SARS-CoV or SARS-CoV-2. We found that reduced binding only partially corresponded to infection, and mainly only at lower ACE2 abundance levels. We observed some human ACE2 variants differentially affect SARS-CoV, SARS-CoV-2, or SARs-CoV-2 N501Y spike variant pseudovirus entry, showing that each viral spike binds ACE2 in a unique manner. Our results provide improved quantitative understanding for how ACE2 sequence and abundance correlate with infectivity, with implications for how natural human ACE2 variants, or variants observed in related species, may impact susceptibility to infection. These genetic tools can be repurposed to characterize future SARS-CoV-2 spike variants, or to better understand how receptor protein sequences correspond with entry by zoonotic viruses during cross-species transmission events.

[end paper 88]

[begin paper 89]

PMCID = 9555207

Title = The Spike-Stabilizing D614G Mutation Interacts with S1/S2 Cleavage Site Mutations To Promote the Infectious Potential of SARS-CoV-2 Variants

Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) remained genetically stable during the first 3 months of the pandemic, before acquiring a D614G spike mutation that rapidly spread worldwide and then generating successive waves of viral variants with increasingly high transmissibility. We set out to evaluate possible epistatic interactions between the early-occurring D614G mutation and the more recently emerged cleavage site mutations present in spike of the Alpha, Delta, and Omicron variants of concern. The P681H/R mutations at the S1/S2 cleavage site increased spike processing and fusogenicity but limited its incorporation into pseudoviruses. In addition, the higher cleavage rate led to higher shedding of the spike S1 subunit, resulting in a lower infectivity of the P681H/R-carrying pseudoviruses compared to those expressing the Wuhan wild-type spike. The D614G mutation increased spike expression at the cell surface and limited S1 shedding from pseudovirions. As a consequence, the D614G mutation preferentially increased the infectivity of P681H/R-carrying pseudoviruses. This enhancement was more marked in cells where the endosomal route predominated, suggesting that more stable spikes could better withstand the endosomal environment. Taken together, these findings suggest that the D614G mutation stabilized S1/S2 association and enabled the selection of mutations that increased S1/S2 cleavage, leading to the emergence of SARS-CoV-2 variants expressing highly fusogenic spikes.

IMPORTANCE The first SARS-CoV-2 variant that spread worldwide in early 2020 carried a D614G mutation in the viral spike, making this protein more stable in its cleaved form at the surface of virions. The Alpha and Delta variants, which spread in late 2020 and early 2021, respectively, proved increasingly transmissible and pathogenic compared to the original strain. Interestingly, Alpha and Delta both carried the mutations P681H/R in a cleavage site that made the spike more cleaved and more efficient at mediating viral fusion. We show here that variants with increased spike cleavage due to P681H/R were even more dependent on the stabilizing effect of the D614G mutation, which limited the shedding of cleaved S1 subunits from viral particles. These findings suggest that the worldwide spread of the D614G mutation was a prerequisite for the emergence of more pathogenic SARS-CoV-2 variants with highly fusogenic spikes.

[end paper 89]

[begin paper 90]

PMCID = 8835786

Title = SARS-CoV-2-Specific Immune Response and the Pathogenesis of COVID-19

The review aims to consolidate research findings on the molecular mechanisms and virulence and pathogenicity characteristics of coronavirus disease (COVID-19) causative agent, severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), and their relevance to four typical stages in the development of acute viral infection. These four stages are invasion; primary blockade of antiviral innate immunity; engagement of the virus’s protection mechanisms against the factors of adaptive immunity; and acute, long-term complications of COVID-19. The invasion stage entails the recognition of the spike protein (S) of SARS-CoV-2 target cell receptors, namely, the main receptor (angiotensin-converting enzyme 2, ACE2), its coreceptors, and potential alternative receptors. The presence of a diverse repertoire of receptors allows SARS-CoV-2 to infect various types of cells, including those not expressing ACE2. During the second stage, the majority of the polyfunctional structural, non-structural, and extra proteins SARS-CoV-2 synthesizes in infected cells are involved in the primary blockage of antiviral innate immunity. A high degree of redundancy and systemic action characterizing these pathogenic factors allows SARS-CoV-2 to overcome antiviral mechanisms at the initial stages of invasion. The third stage includes passive and active protection of the virus from factors of adaptive immunity, overcoming of the barrier function at the focus of inflammation, and generalization of SARS-CoV-2 in the body. The fourth stage is associated with the deployment of variants of acute and long-term complications of COVID-19. SARS-CoV-2’s ability to induce autoimmune and autoinflammatory pathways of tissue invasion and development of both immunosuppressive and hyperergic mechanisms of systemic inflammation is critical at this stage of infection.

[end paper 90]

[begin paper 91]

PMCID = 9446661

Title = Identification of hACE2-interacting sites in SARS-CoV-2 spike receptor binding domain for antiviral drugs screening

The key structure of the interface between the spike protein of Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) and human angiotensin-converting enzyme 2 (hACE2) acts as an essential switch for cell entry by the virus and drugs targets. However, this is largely unknown. Here, we tested three peptides of spike receptor binding domain (RBD) and found that peptide 391–465 aa is the major hACE2-interacting sites in SARS-CoV-2 spike RBD. We then identified essential amino acid residues (403R, 449Y, 454R) of peptide 391–465 aa that were critical for the interaction between the RBD and hACE2. Additionally, a pseudotyped virus containing SARS-CoV-2 spike with individual mutation (R454G, Y449F, R403G, N439I, or N440I) was determined to have very low infectivity compared with the pseudotyped virus containing the wildtype (WT) spike from reference strain Wuhan 1, respectively. Furthermore, we showed the key amino acids had the potential to drug screening. For example, molecular docking (Docking) and infection assay showed that Cephalosporin derivatives can bind with the key amino acids to efficiently block infection of the pseudoviruses with wild type spike or new variants. Moreover, Cefixime inhibited live SARS-CoV-2 infection. These results also provide a novel model for drug screening and support further clinical evaluation and development of Cephalosporin derivatives as novel, safe, and cost-effective drugs for prevention/treatment of SARS-CoV-2.

[end paper 91]

[begin paper 92]

PMCID = 8498651

Title = Structural mechanism of SARS-CoV-2 neutralization by two murine antibodies targeting the RBD

The severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) pandemic has necessitated the rapid development of antibody-based therapies and vaccines as countermeasures. Here, we use cryoelectron microscopy (cryo-EM) to characterize two protective anti-SARS-CoV-2 murine monoclonal antibodies (mAbs) in complex with the spike protein, revealing similarities between epitopes targeted by human and murine B cells. The more neutralizing mAb, 2B04, binds the receptor-binding motif (RBM) of the receptor-binding domain (RBD) and competes with angiotensin-converting enzyme 2 (ACE2). By contrast, 2H04 binds adjacent to the RBM and does not compete for ACE2 binding. Naturally occurring sequence variants of SARS-CoV-2 and corresponding neutralization escape variants selected in vitro map to our structurally defined epitopes, suggesting that SARS-CoV-2 might evade therapeutic antibodies with a limited set of mutations, underscoring the importance of combination mAb therapeutics. Finally, we show that 2B04 neutralizes SARS-CoV-2 infection by preventing ACE2 engagement, whereas 2H04 reduces host cell attachment without directly disrupting ACE2-RBM interactions, providing distinct inhibitory mechanisms used by RBD-specific mAbs.

Errico et al. use cryoelectron microscopy to solve the structure of two murine-derived neutralizing antibodies against the SARS-CoV-2 receptor-binding domain, showing that they target discrete epitopes and utilize distinct mechanisms of neutralization.

[end paper 92]

[begin paper 93]

PMCID = 9511875

Title = Non-uniform aspects of the SARS-CoV-2 intraspecies evolution reopen question of its origin

Several hypotheses have been presented on the origin of severe acute respiratory syndrome coronavirus-2 (SARS-CoV-2) from its identification as the agent causing the current coronavirus disease 19 (COVID-19) pandemic. So far, no solid evidence has been found to support any hypothesis on the origin of this virus, and the issue continue to resurface over and over again. Here we have unfolded a pattern of distribution of several mutations in the SARS-CoV-2 proteins in 24 geo-locations across different continents. The results showed an evenly uneven distribution of the unique protein variants, distinct mutations, unique frequency of common conserved residues, and mutational residues across these 24 geo-locations. Furthermore, ample mutations were identified in the evolutionarily conserved invariant regions in the SARS-CoV-2 proteins across almost all geo-locations studied. This pattern of mutations potentially breaches the law of evolutionary conserved functional units of the beta-coronavirus genus. These mutations may lead to several novel SARS-CoV-2 variants with a high degree of transmissibility and virulence. A thorough investigation on the origin and characteristics of SARS-CoV-2 needs to be conducted in the interest of science and for the preparation of meeting the challenges of potential future pandemics.

[end paper 93]

[begin paper 94]

PMCID = 9788845

Title = A new intracellular targeting motif in the cytoplasmic tail of the spike protein may act as a target to inhibit SARS-CoV-2 assembly

Infection with severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) poses a threat to global public health, underscoring the urgent need for the development of preventive and therapeutic measures. The spike (S) protein of SARS-CoV-2, which mediates receptor binding and subsequent membrane fusion to promote viral entry, is a major target for current drug development and vaccine design. The S protein comprises a large N-terminal extracellular domain, a transmembrane domain, and a short cytoplasmic tail (CT) at the C-terminus. CT truncation of the S protein has been previously reported to promote the infectivity of SARS-CoV and SARS-CoV-2 pseudoviruses. However, the underlying molecular mechanism has not been precisely elucidated. In addition, the CT of various viral membrane glycoproteins play an essential role in the assembly of virions, yet the role of the S protein CT in SARS-CoV-2 infection remains unclear. In this study, through constructing a series of mutations of the CT of the S protein and analyzing their impact on the packaging of the SARS-CoV-2 pseudovirus and live SARS-CoV-2 virus, we identified V1264L1265 as a new intracellular targeting motif in the CT of the S protein, that regulates the transport and subcellular localization of the spike protein through the interactions with cytoskeleton and vesicular transport-related proteins, ARPC3, SCAMP3, and TUBB8, thereby modulating SARS-CoV-2 pseudovirus and live SARS-CoV-2 virion assembly. Either disrupting the V1264L1265 motif or reducing the expression of ARPC3, SCAMP3, and TUBB8 significantly repressed the assembly of the live SARS-CoV-2 virion, raising the possibility that the V1264L1265 motif and the host responsive pathways involved could be new drug targets for the treatment of SARS-CoV-2 infection. Our results extend the understanding of the role played by the S protein CT in the assembly of pseudoviruses and live SARS-CoV-2 virions, which will facilitate the application of pseudoviruses to the study of SARS-CoV-2 and provide potential strategies for the treatment of SARS-CoV-2 infection.

[end paper 94]

[begin paper 95]

PMCID = 9595563

Title = LRRC15 inhibits SARS-CoV-2 cellular entry in trans

Severe Acute Respiratory Syndrome Coronavirus 2 (SARS-CoV-2) infection is mediated by the entry receptor angiotensin-converting enzyme 2 (ACE2). Although attachment factors and coreceptors facilitating entry are extensively studied, cellular entry factors inhibiting viral entry are largely unknown. Using a surfaceome CRISPR activation screen, we identified human LRRC15 as an inhibitory attachment factor for SARS-CoV-2 entry. LRRC15 directly binds to the receptor-binding domain (RBD) of spike protein with a moderate affinity and inhibits spike-mediated entry. Analysis of human lung single-cell RNA sequencing dataset reveals that expression of LRRC15 is primarily detected in fibroblasts and particularly enriched in pathological fibroblasts in COVID-19 patients. ACE2 and LRRC15 are not coexpressed in the same cell types in the lung. Strikingly, expression of LRRC15 in ACE2-negative cells blocks spike-mediated viral entry in ACE2+ cell in trans, suggesting a protective role of LRRC15 in a physiological context. Therefore, LRRC15 represents an inhibitory attachment factor for SARS-CoV-2 that regulates viral entry in trans.

SARS-CoV-2 infection is mediated by the entry receptor ACE2, but cellular entry factors that inhibit viral entry are largely unknown. This study shows that human LRRC15 protein is expressed in pathological fibroblasts, directly binds to the receptor-binding domain of spike protein, and inhibits SARS-CoV-2 spike-mediated viral entry in neighboring cells.

[end paper 95]

[begin paper 96]

PMCID = 8491763

Title = Mechanisms of SARS-CoV-2 entry into cells

The unprecedented public health and economic impact of the COVID-19 pandemic caused by infection with severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) has been met with an equally unprecedented scientific response. Much of this response has focused, appropriately, on the mechanisms of SARS-CoV-2 entry into host cells, and in particular the binding of the spike (S) protein to its receptor, angiotensin-converting enzyme 2 (ACE2), and subsequent membrane fusion. This Review provides the structural and cellular foundations for understanding the multistep SARS-CoV-2 entry process, including S protein synthesis, S protein structure, conformational transitions necessary for association of the S protein with ACE2, engagement of the receptor-binding domain of the S protein with ACE2, proteolytic activation of the S protein, endocytosis and membrane fusion. We define the roles of furin-like proteases, transmembrane protease, serine 2 (TMPRSS2) and cathepsin L in these processes, and delineate the features of ACE2 orthologues in reservoir animal species and S protein adaptations that facilitate efficient human transmission. We also examine the utility of vaccines, antibodies and other potential therapeutics targeting SARS-CoV-2 entry mechanisms. Finally, we present key outstanding questions associated with this critical process.

Entry of SARS-CoV-2 into host cells is mediated by the interaction between the viral spike protein and its receptor angiotensin-converting enzyme 2, followed by virus–cell membrane fusion. Worldwide research efforts have provided a detailed understanding of this process at the structural and cellular levels, enabling successful vaccine development for a rapid response to the COVID-19 pandemic.

[end paper 96]

[begin paper 97]

PMCID = 7799268

Title = The impact of structural bioinformatics tools and resources on SARS-CoV-2 research and therapeutic strategies

SARS-CoV-2 is the causative agent of COVID-19, the ongoing global pandemic. It has posed a worldwide challenge to human health as no effective treatment is currently available to combat the disease. Its severity has led to unprecedented collaborative initiatives for therapeutic solutions against COVID-19. Studies resorting to structure-based drug design for COVID-19 are plethoric and show good promise. Structural biology provides key insights into 3D structures, critical residues/mutations in SARS-CoV-2 proteins, implicated in infectivity, molecular recognition and susceptibility to a broad range of host species. The detailed understanding of viral proteins and their complexes with host receptors and candidate epitope/lead compounds is the key to developing a structure-guided therapeutic design.

Since the discovery of SARS-CoV-2, several structures of its proteins have been determined experimentally at an unprecedented speed and deposited in the Protein Data Bank. Further, specialized structural bioinformatics tools and resources have been developed for theoretical models, data on protein dynamics from computer simulations, impact of variants/mutations and molecular therapeutics.

Here, we provide an overview of ongoing efforts on developing structural bioinformatics tools and resources for COVID-19 research. We also discuss the impact of these resources and structure-based studies, to understand various aspects of SARS-CoV-2 infection and therapeutic development. These include (i) understanding differences between SARS-CoV-2 and SARS-CoV, leading to increased infectivity of SARS-CoV-2, (ii) deciphering key residues in the SARS-CoV-2 involved in receptor–antibody recognition, (iii) analysis of variants in host proteins that affect host susceptibility to infection and (iv) analyses facilitating structure-based drug and vaccine design against SARS-CoV-2.

[end paper 97]

[begin paper 98]

PMCID = 9492400

Title = Host cell membrane proteins located near SARS-CoV-2 spike protein attachment sites are identified using proximity labeling and proteomic analysis

Coronavirus disease represents a real threat to the global population, and understanding the biological features of the causative virus, that is, severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), is imperative for mitigating this threat. Analyses of proteins such as primary receptors and coreceptors (cofactors), which are involved in the entry of SARS-CoV-2 into host cells, will provide important clues to help control the virus. Here, we identified host cell membrane protein candidates present in proximity to the attachment sites of SARS-CoV-2 spike proteins, using proximity labeling and proteomic analysis. The identified proteins represent key candidate factors that may be required for viral entry. We found SARS-CoV-2 host protein DPP4, cell adhesion protein Cadherin 17, and glycoprotein CD133 colocalized with cell membrane–bound SARS-CoV-2 spike proteins in Caco-2 cells and thus showed potential as candidate factors. Additionally, our analysis of the experimental infection of HEK293T cells with a SARS-CoV-2 pseudovirus indicated a 2-fold enhanced infectivity in the CD133-ACE2-coexpressing HEK293T cells compared to that in HEK293T cells expressing ACE-2 alone. The information and resources regarding these coreceptor labeling and analysis techniques could be utilized for the development of antiviral agents against SARS-CoV-2 and other emerging viruses.

[end paper 98]

[begin paper 99]

PMCID = 8947964

Title = Structural diversity of the SARS-CoV-2 Omicron spike

Aided by extensive spike protein mutation, the SARS-CoV-2 Omicron variant overtook the previously dominant Delta variant. Spike conformation plays an essential role in SARS-CoV-2 evolution via changes in receptor-binding domain (RBD) and neutralizing antibody epitope presentation, affecting virus transmissibility and immune evasion. Here, we determine cryo-EM structures of the Omicron and Delta spikes to understand the conformational impacts of mutations in each. The Omicron spike structure revealed an unusually tightly packed RBD organization with long range impacts that were not observed in the Delta spike. Binding and crystallography revealed increased flexibility at the functionally critical fusion peptide site in the Omicron spike. These results reveal a highly evolved Omicron spike architecture with possible impacts on its high levels of immune evasion and transmissibility.

Gobeil, Henderson, Stalls et al. identify diverse Omicron S ectodomain conformations demonstrating altered architecture that exhibits tight packing of the 3-RBD-down state, NTD-to-RBD (N2R) linker rearrangements, and changes in fusion peptide conformational dynamics. These distinct conformational features of its S protein may underlie Omicron’s higher transmissibility and immune evasion.

[end paper 99]

[begin paper 100]

PMCID = 8015430

Title = Neutralization potency of monoclonal antibodies recognizing dominant and subdominant epitopes on SARS-CoV-2 Spike is impacted by the B.1.1.7 variant

Interaction of the SARS-CoV-2 Spike receptor binding domain (RBD) with the receptor ACE2 on host cells is essential for viral entry. RBD is the dominant target for neutralizing antibodies, and several neutralizing epitopes on RBD have been molecularly characterized. Analysis of circulating SARS-CoV-2 variants has revealed mutations arising in the RBD, N-terminal domain (NTD) and S2 subunits of Spike. To understand how these mutations affect Spike antigenicity, we isolated and characterized >100 monoclonal antibodies targeting epitopes on RBD, NTD, and S2 from SARS-CoV-2-infected individuals. Approximately 45% showed neutralizing activity, of which ∼20% were NTD specific. NTD-specific antibodies formed two distinct groups: the first was highly potent against infectious virus, whereas the second was less potent and displayed glycan-dependant neutralization activity. Mutations present in B.1.1.7 Spike frequently conferred neutralization resistance to NTD-specific antibodies. This work demonstrates that neutralizing antibodies targeting subdominant epitopes should be considered when investigating antigenic drift in emerging variants.

Potent nAbs were isolated from an asymptomatic donor with low plasma neutralization

RBD-specific nAbs target epitopes overlapping with known RBD antibody classes

NTD mutations in B.1.1.7 Spike confer neutralization resistance to NTD-specific nAbs

Most RBD-specific nAbs retain potent neutralization of the B.1.1.7 variant

The impact of mutations arising in SARS-CoV-2 Spike on antigenicity is still not known. Graham et al. isolate potent neutralizing monoclonal antibodies from individuals experiencing a range of COVID-19 disease severity that target RBD, NTD, and non-S1 epitopes. The B.1.1.7 variant of concern was most resistant to NTD-specific nAbs whereas RBD-specific nAbs retained potent neutralization.

[end paper 100]



