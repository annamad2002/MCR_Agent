# Complete Extraction - Files Index

This directory now contains comprehensive extraction results from all prompt chat logs (1-13). Below is a guide to the generated files.

## Generated Files

### 1. **final_extraction_comprehensive.json** (31 KB)
**Format:** JSON  
**Best for:** Programmatic access, data analysis in Python/R  

**Contents:**
- Metadata about the extraction task
- Summary by prompt (prompt number, compounds, files, columns)
- All 127 compound entries with complete data
- All 82 unique SMILES with occurrence information

**Structure:**
```json
{
  "metadata": { ... },
  "summary_by_prompt": { ... },
  "all_unique_compounds": [ ... ],
  "total_statistics": { ... }
}
```

**Use cases:**
- Load into pandas/R dataframe
- Filter by prompt or column
- Statistical analysis
- Integration with other tools

---

### 2. **EXTRACTION_FINDINGS.md** (10 KB)
**Format:** Markdown  
**Best for:** Comprehensive understanding, report generation  

**Contents:**
- Executive summary with key numbers
- Complete prompt-by-prompt analysis (all 13 prompts)
  - File locations
  - Number of compounds
  - Table structure
  - Column information
  - Sample SMILES
- Summary statistics
- Column frequency analysis
- Key findings about compounds in multiple prompts
- Analysis of design evolution across prompts
- Conclusions and recommendations

**Sections:**
1. Prompt-by-Prompt Analysis (detailed for each prompt 1-13)
2. Summary Statistics
3. Key Findings: SMILES Appearing in Multiple Prompts
4. Column Evolution Across Prompts
5. Data Quality Assessment
6. Conclusions

**Use cases:**
- Comprehensive report writing
- Understanding experimental progression
- Identifying consensus candidates
- Decision-making about next steps

---

### 3. **EXTRACTION_SUMMARY_REPORT.txt** (7.1 KB)
**Format:** Plain text  
**Best for:** Quick reference, overview  

**Contents:**
- Overview of prompt status
- Detailed breakdown by prompt (status, model, compounds, columns)
- Compound statistics with distribution
- Top 5 most common table columns
- Key findings
- Column variations by prompt stage
- Observations and notes

**Quick lookup for:**
- Which prompts have final summaries
- How many compounds in each prompt
- What columns are in each table
- General patterns and observations

---

### 4. **UNIQUE_SMILES_LIST.txt** (11 KB)
**Format:** Structured plain text  
**Best for:** Identifying consensus compounds, checking specific SMILES  

**Contents:**
- Total count of unique SMILES (82)
- List of SMILES appearing in multiple prompts (consensus compounds)
- Frequency count for each SMILES
- Which prompts each SMILES appears in
- Which files contain each SMILES

**Organization:**
- First section: SMILES appearing in 2+ prompts (45 compounds)
- Second section: Complete list of all 82 unique SMILES

**Use cases:**
- Find which prompts recommend the same compound
- Identify the most robust candidates (appearing multiple times)
- Filter for compounds of interest
- Cross-reference with other data

---

### 5. **EXTRACTION_README.txt** (6.4 KB)
**Format:** Plain text  
**Best for:** Quick start, methodology explanation  

**Contents:**
- Task description
- List of all generated files with descriptions
- Key results at a glance
- Prompt status summary (✓ or ✗)
- Design evolution across prompts
- Strongest consensus candidates
- Notable findings
- How to use each file
- Methodology notes

**Quick reference for:**
- Understanding what was extracted
- File selection based on use case
- Design progression overview
- Top candidates summary

---

## Quick Access by Use Case

### "I need a quick overview"
→ Read: **EXTRACTION_README.txt** (5 min read)

### "I need to understand all the details"
→ Read: **EXTRACTION_FINDINGS.md** (20 min read)

### "I need to identify the best candidate compounds"
→ Read: **UNIQUE_SMILES_LIST.txt** + check multi-prompt SMILES

### "I need to analyze the data programmatically"
→ Use: **final_extraction_comprehensive.json**

### "I need a structured reference for each prompt"
→ Use: **EXTRACTION_SUMMARY_REPORT.txt**

### "I'm looking for a specific compound or prompt"
→ Search: **UNIQUE_SMILES_LIST.txt** or **final_extraction_comprehensive.json**

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Total prompts analyzed | 13 |
| Prompts with final summaries | 11 ✓ |
| Prompts without summaries | 2 ✗ |
| Total compound entries | 127 |
| Total unique SMILES | 82 |
| SMILES in multiple prompts | 45 |
| Files with summary tables | 21 |
| Average compounds per prompt | 11.5 |

---

## Data Completeness

| Data Type | Coverage |
|-----------|----------|
| SMILES | 100% (127/127) |
| Docking Score | 95% (121/127) |
| Interacting Residues | 70% (89/127) |
| QED Score | 50% (63/127) |
| Molecular Weight | 46% (58/127) |

---

## Most Commonly Appearing Compounds

(Appearing in multiple prompts, indicating strong consensus)

1. **Dicaffeoylquinic acid variant** - 9 times (Prompts 7, 8, 9)
2. **Chlorogenic acid-like** - 4 times (Prompts 7, 8, 9)
3. **p-Coumaric acid** - Recommended by Prompt 10
4. **Caffeic acid** - Recommended by Prompt 10
5. Various aromatic nitro compounds - Early prompts (1-5)

---

## Design Progression Observed

**Stage 1 (Prompts 1-5): Synthetic Design**
- Nitro-aromatic compounds
- Focus on Lipinski properties

**Stage 2 (Prompts 7-9): Transition to Naturals**
- Plant-derived polyphenols
- Added residue interaction data

**Stage 3 (Prompts 10-13): Natural Product Optimization**
- Simplified natural compounds
- Complete binding information
- Rumen suitability focus

---

## How to Use the JSON File

### Python Example
```python
import json

with open('final_extraction_comprehensive.json', 'r') as f:
    data = json.load(f)

# Get all compounds from Prompt 11
prompt_11 = data['summary_by_prompt']['Prompt_11']
print(f"Prompt 11 has {prompt_11['total_compounds']} compounds")

# Get all unique SMILES
all_smiles = [c['smiles'] for c in data['all_unique_compounds']]

# Find SMILES appearing multiple times
frequent_smiles = [c for c in data['all_unique_compounds'] 
                   if len(c['found_in_prompts']) > 1]
```

### R Example
```r
library(jsonlite)
data <- fromJSON('final_extraction_comprehensive.json')

# Get statistics
total_unique <- data$total_statistics$total_unique_smiles
total_entries <- data$total_statistics$total_compound_entries

# Access prompt summary
prompts_summary <- data$summary_by_prompt
```

---

## Recommendations for Next Steps

1. **Review the consensus compounds** in UNIQUE_SMILES_LIST.txt
   - Focus on those appearing 3+ times

2. **Compare Prompt 10's recommendation** (p-Coumaric acid, Caffeic acid)
   - These are the most practical for rumen use
   - Simplest structures
   - Natural products

3. **Cross-reference with Prompt 11** (most comprehensive)
   - 35 compounds across 4 LLM models
   - Best representation of options

4. **Validate residue interactions**
   - 70% of entries have residue data
   - Cross-check docking scores across prompts

5. **Consider the design evolution**
   - Early synthetic compounds questioned for safety
   - Natural compounds increasingly favored
   - Latest prompts show strong consensus on polyphenols

---

## Notes

- **Prompt 3**: Empty directory - no data available
- **Prompt 6**: Chat log exists but contains no final summary section
- **Prompt 10**: Most focused on practical rumen applicability
- **Prompt 11**: Most comprehensive analysis (4 LLM models)
- **Prompts 12-13**: Iterative refinement of natural products

---

## File Locations

All files are located in:
```
/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent/
```

Individual files:
- `final_extraction_comprehensive.json`
- `EXTRACTION_FINDINGS.md`
- `EXTRACTION_SUMMARY_REPORT.txt`
- `UNIQUE_SMILES_LIST.txt`
- `EXTRACTION_README.txt`
- `EXTRACTION_FILES_INDEX.md` (this file)

---

**Last Updated:** 2026-06-30  
**Data Sources:** All chat log files from Prompts 1-13  
**Extraction Method:** Automated markdown table parsing with manual verification

