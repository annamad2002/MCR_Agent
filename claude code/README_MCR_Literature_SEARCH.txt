================================================================================
MCR LITERATURE SEARCH RESULTS - SUMMARY
================================================================================

TASK COMPLETED: Systematic literature search for MCR (Methyl-Coenzyme M
Reductase) inhibition studies on 110 compounds from SMILES_List_Master.csv

SEARCH DATE: June 30, 2026
TOTAL COMPOUNDS ANALYZED: 110+
SEARCH STRATEGY: WebSearch (Google Scholar, PubMed, Frontiers, ScienceDirect, PNAS)

================================================================================
KEY STATISTICS
================================================================================

COMPOUNDS WITH PUBLISHED MCR/METHANE LITERATURE: 25
  - Extensively documented (>5 papers): Bromoform, 3-NOP, Lovastatin
  - Well-characterized (2-5 papers): Caffeic acid, ferulic acid, fatty acids
  - Single studies or recent findings: Salvianolic acid C, polyphenols

COMPOUNDS WITH GENERAL METHANE DATA (not MCR-specific): 15
  - Essential oils, terpenes, garlic compounds
  - Show methane reduction but mechanism not always MCR-targeted

COMPOUNDS WITHOUT SPECIFIC LITERATURE: 70
  - Mostly novel AI-generated docking candidates
  - Complex polyphenolic derivatives (untested)
  - Isotopically labeled compounds
  - Require experimental validation

================================================================================
OUTPUT FILES GENERATED
================================================================================

1. mcr_literature_findings.json (13 KB)
   - Comprehensive database of all compounds with literature findings
   - Summary of key research sources and databases
   - Methodology notes and reliability assessment
   - Next steps recommendations

2. mcr_compound_details.json (13 KB)
   - Compound-by-compound breakdown from CSV
   - Literature status for each ranked compound
   - Structural classification
   - Mechanism of action where known
   - Species tested and effectiveness data
   - Ranking observations and prioritization

3. MCR_Literature_Search_Report.md (13 KB)
   - Executive summary and key findings
   - Detailed findings organized by compound category
   - Literature citations with key studies
   - Anomalies in your docking rankings
   - Tier 1/2/3 recommendations for next steps
   - Knowledge gaps and research limitations

================================================================================
KEY FINDINGS OVERVIEW
================================================================================

ESTABLISHED MCR INHIBITORS (Proven, Published):
1. Bromoform - 94% methane reduction, very potent but volatile
2. 3-Nitrooxypropanol (3-NOP/Bovaer) - ~30% reduction, FDA approved
3. Lovastatin - 37-55% reduction, HMG-CoA reductase inhibitor
4. Salvianolic acid C - Potent, IC50=692 µmol/L, published 2025
5. Bromoethane sulfonate (BES) - Research compound, poor in vivo

NATURAL COMPOUNDS WITH LITERATURE:
- Polyphenols: Caffeic acid, ferulic acid, p-coumaric acid, tannins
- Essential oils: Eugenol, limonene, p-cymene, cinnamaldehyde
- Fatty acids: Capric (C10), lauric (C12), medium-chain types
- Garlic: Allyl sulfides (variable effectiveness)

YOUR TOP COMPOUNDS IN CSV:
Ranks 1-20: Mostly novel polyphenolic derivatives with STRONG COMPUTATIONAL
BINDING (-9.7 to -9.1 kcal/mol) but NO PUBLISHED LITERATURE

This suggests:
✓ Your docking model may identify genuinely novel compounds
✗ Computational predictions need experimental validation
? Whether binding affinity = biological activity

KEY ANOMALY:
Bromoform (most potent inhibitor known) ranks at #176 with ΔG=-3.2
This is unexpected and suggests:
- Your docking pocket may favor different interactions
- Halogenated analogs bind differently than organics
- Consider re-docking with updated MCR structures (2024-2025)

================================================================================
RECOMMENDATIONS FOR YOUR NEXT STEPS
================================================================================

IMMEDIATE (Weeks 1-4):
□ Prioritize Ranks 1-10 for synthesis if chemically feasible
□ Run in vitro MCR enzyme assay against top 5 candidates
□ Compare IC50 values against 3-NOP standard (positive control)
□ Cost/time analysis for chemical synthesis

SHORT-TERM (Months 1-3):
□ In vitro rumen fermentation screening for top 20 compounds
□ Measure: methane production, VFA changes, Methanobrevibacter count
□ Microbial transcriptomics (mcrA, rnfC gene expression)
□ Mechanism of action studies

MEDIUM-TERM (Months 3-6):
□ Re-dock all compounds against latest MCR crystal structures
□ Molecular dynamics simulation for binding stability
□ ADMET prediction for bioavailability
□ Identify most promising candidates for in vivo testing

LONG-TERM (6-12+ months, if in vitro promising):
□ Dose-response cattle trials (dairy and beef)
□ Long-term efficacy and safety studies
□ Monitor for drug resistance
□ Explore combination therapies

================================================================================
MOST PROMISING CANDIDATES FOR EXPERIMENTAL TESTING
================================================================================

TIER 1 (Test First):
1. Your Rank 1-5 compounds (if synthesizable)
   - Highest computational binding affinity
   - Novel structures (if validated, could outperform 3-NOP)

2. Salvianolic acid C and analogs
   - Already proven effective in cattle (2025)
   - Published IC50 and in vivo data available
   - Natural source is feasible

3. Lovastatin variants (your Rank 3)
   - Modified version with higher binding affinity
   - Parent compound (Rank 2) well-characterized
   - Mechanism understood

TIER 2 (Secondary Candidates):
- Polyphenolic derivatives (Ranks 5-20)
- Complex caffeate/ferulate esters
- May represent genuine improvements if synthesis permits

TIER 3 (If Others Fail):
- Terpene variants (Ranks 6, 14, etc.)
- Simple fatty acid derivatives
- Isotopically labeled compounds (if mechanistic research)

================================================================================
CONFIDENCE LEVELS
================================================================================

HIGH CONFIDENCE (Can cite published data):
✓ Bromoform - Multiple in vivo cattle studies
✓ 3-NOP - Extensive commercial and research literature
✓ Lovastatin - Multiple ruminant species tested
✓ Polyphenols (Caffeic, ferulic acid) - Published mechanisms
✓ Salvianolic acid C - Very recent publication with data

MEDIUM CONFIDENCE (Published but variable results):
≈ Essential oils (Eugenol, terpenes) - Dose/context dependent
≈ Garlic compounds - Inconsistent results across studies
≈ Fatty acids - Mechanism still being elucidated

LOW/NO CONFIDENCE (No literature found):
✗ Your 70 novel compounds - Computational only
✗ Complex polyphenolic scaffolds - Untested structures
✗ Many isotopically labeled variants - Not yet studied for MCR

================================================================================
REFERENCES & SOURCES
================================================================================

PRIMARY DATABASES SEARCHED:
- PubMed Central (PMC)
- PubMed (NCBI)
- Google Scholar
- Frontiers (journals)
- ScienceDirect
- PNAS (Proceedings of National Academy of Sciences)
- Springer Nature Link
- Journal of Dairy Science
- Journal of Animal Science and Biotechnology

YEAR RANGE: 2015-2026

KEY JOURNALS IDENTIFIED:
- Journal of Dairy Science
- PNAS
- Frontiers in Microbiology
- Frontiers in Animal Science
- Journal of Animal Science and Biotechnology
- Scientific Reports
- Microbiome
- mBio

MOST RECENT PUBLICATIONS (2024-2026):
- Salvianolic acid C study (J. Animal Science & Biotech, 2025)
- MCR inhibition challenges review (Frontiers Microbiology, 2025)
- Bromoform efficacy studies (ScienceDirect, 2025)
- In vitro screening of halomethanes (Frontiers Animal Science, 2026)

================================================================================
CONTACT & FOLLOW-UP
================================================================================

For detailed information, see:
1. mcr_literature_findings.json - Structured database format
2. mcr_compound_details.json - Individual compound analysis
3. MCR_Literature_Search_Report.md - Full narrative report

All files are in: /Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/
                  chem/ollama_prompts/Prompts/MCR_Agent/

Questions or need additional searches? The compounds marked as "No literature found"
may still have research in specialized databases or very recent preprints.

================================================================================
END OF SUMMARY
================================================================================
