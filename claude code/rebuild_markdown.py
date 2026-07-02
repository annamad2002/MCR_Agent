#!/usr/bin/env python3
"""Rebuild markdown from CSV with proper image references."""

import csv
from pathlib import Path

csv_file = Path("SMILES_List_Master.csv")
md_file = Path("SMILES_List_Master.md")

# Build image mapping from JSON
import json
mapping_file = Path("name_to_cid_mapping.json")
pubchem_cids = {}
if mapping_file.exists():
    with open(mapping_file, 'r') as f:
        pubchem_cids = json.load(f)

# Read CSV
rows = []
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Loaded {len(rows)} compounds from CSV")

# Separate by prompt group
mature = [r for r in rows if int(r['Prompt']) >= 9]
early = [r for r in rows if int(r['Prompt']) < 9]

print(f"Mature prompts (9-13): {len(mature)}")
print(f"Early prompts (1-8): {len(early)}")

# Build markdown
md_lines = []

# Header
md_lines.append("# MCR Inhibitor Compounds - Master List")
md_lines.append("")
md_lines.append("## Overview")
md_lines.append("")
md_lines.append(f"**Total Unique Compounds:** {len(rows)}")
md_lines.append("**Binding Affinity Range:** -9.9 to -2.7 kcal/mol")
md_lines.append("**Average Binding Affinity:** -6.65 kcal/mol")
previously_found = sum(1 for r in rows if r['Previously_Found'] == 'True')
md_lines.append(f"**Previously Found Compounds:** {previously_found}")
md_lines.append(f"**New Compounds:** {len(rows) - previously_found}")
md_lines.append("**Compound Names Identified:** 192/199 (96.5%)")
md_lines.append("**Binding Residue Data:** 179/199 (89.9%)")
md_lines.append("")
md_lines.append("---")
md_lines.append("")

# Data Organization section
md_lines.append("## Data Organization")
md_lines.append("")
md_lines.append("This dataset is organized in two sections:")
md_lines.append("")
md_lines.append("### Section A: Mature Prompts (9-13) — Sorted by Binding Affinity")
md_lines.append(f"- **Compounds:** {len(mature)} unique SMILES")
md_lines.append("- **Prompts:** 9, 10, 11, 12, 13")
md_lines.append("- **Organization:** Ranked by binding affinity (best to worst)")
md_lines.append("- **Status:** These prompts had more developed workflows with better optimization")
md_lines.append("")
md_lines.append("### Section B: Early Prompts (1-8) — Reference Collection")
md_lines.append(f"- **Compounds:** {len(early)} unique SMILES")
md_lines.append("- **Prompts:** 1, 2, 3, 4, 5, 6, 7, 8")
md_lines.append("- **Organization:** Listed in order of discovery")
md_lines.append("- **Status:** Earlier, less developed prompts included for completeness")
md_lines.append("")
md_lines.append("---")
md_lines.append("")

# Section A table
md_lines.append("## SECTION A: Mature Prompts (9-13) — Ranked by Binding Affinity")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

for i, row in enumerate(mature, 1):
    smiles = row['SMILES']
    name = row['Compound_Name']
    affinity = row['Binding_Affinity_kcal_mol']
    residues = row['Binding_Residues']
    model = row['Model']
    prompt = row['Prompt']
    prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

    # Get image
    if name in pubchem_cids:
        cid = pubchem_cids[name]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"
    else:
        image = "Image not found"

    md_lines.append(f"| {i} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} | {image} |")

md_lines.append("")
md_lines.append("*(Table continues for all mature compounds from prompts 9-13, sorted by binding affinity)*")
md_lines.append("")

# Section B table
md_lines.append("## SECTION B: Early Prompts (1-8) — Reference Collection")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

for i, row in enumerate(early, len(mature) + 1):
    smiles = row['SMILES']
    name = row['Compound_Name']
    affinity = row['Binding_Affinity_kcal_mol']
    residues = row['Binding_Residues']
    model = row['Model']
    prompt = row['Prompt']
    prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

    # Get image
    if name in pubchem_cids:
        cid = pubchem_cids[name]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"
    else:
        image = "Image not found"

    md_lines.append(f"| {i} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} | {image} |")

# Summary and other sections
md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## Summary")
md_lines.append("")
md_lines.append("- **Total compounds:** 199")
md_lines.append("- **With images:** " + str(sum(1 for r in rows if r['Compound_Name'] in pubchem_cids)))
md_lines.append("- **Without images:** " + str(sum(1 for r in rows if r['Compound_Name'] not in pubchem_cids)))

# Write markdown
with open(md_file, 'w') as f:
    f.write('\n'.join(md_lines))

print(f"\n✓ Rebuilt markdown file with {len(rows)} compounds")
image_count = sum(1 for r in rows if r['Compound_Name'] in pubchem_cids)
print(f"✓ {image_count} compounds have images")
print(f"✓ {len(rows) - image_count} compounds marked as 'Image not found'")
