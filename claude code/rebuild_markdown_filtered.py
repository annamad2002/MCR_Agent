#!/usr/bin/env python3
"""Rebuild markdown with images first, then non-images at the bottom."""

import csv
import json
from pathlib import Path

csv_file = Path("SMILES_List_Master.csv")
mapping_file = Path("smiles_to_cid_mapping.json")

# Load the SMILES-to-CID mapping
with open(mapping_file, 'r') as f:
    smiles_to_cid = json.load(f)

# Read CSV
rows = []
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Loaded {len(rows)} compounds from CSV")

# Separate compounds with and without images
with_images = []
without_images = []

for row in rows:
    smiles = row['SMILES'].strip()
    has_image = smiles in smiles_to_cid and smiles_to_cid[smiles] != 0

    if has_image:
        with_images.append(row)
    else:
        without_images.append(row)

print(f"With images: {len(with_images)}")
print(f"Without images: {len(without_images)}")

# Count by prompt for each group
mature_with = sum(1 for r in with_images if int(r['Prompt']) >= 9)
early_with = sum(1 for r in with_images if int(r['Prompt']) < 9)
mature_without = sum(1 for r in without_images if int(r['Prompt']) >= 9)
early_without = sum(1 for r in without_images if int(r['Prompt']) < 9)

print(f"  With images - Mature: {mature_with}, Early: {early_with}")
print(f"  Without images - Mature: {mature_without}, Early: {early_without}")

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
md_lines.append(f"**Compounds with Images:** {len(with_images)}")
md_lines.append(f"**Compounds without Images:** {len(without_images)}")
md_lines.append("")
md_lines.append("---")
md_lines.append("")

# Data Organization section
md_lines.append("## Data Organization")
md_lines.append("")
md_lines.append("This dataset is organized by image availability, then by binding affinity:")
md_lines.append("")
md_lines.append("### Part A: Compounds WITH Images")
md_lines.append(f"- **Total:** {len(with_images)} compounds")
md_lines.append(f"- **Mature prompts (9-13):** {mature_with} compounds")
md_lines.append(f"- **Early prompts (1-8):** {early_with} compounds")
md_lines.append("- **Organization:** Sorted by binding affinity (best to worst)")
md_lines.append("")
md_lines.append("### Part B: Compounds WITHOUT Images")
md_lines.append(f"- **Total:** {len(without_images)} compounds")
md_lines.append(f"- **Mature prompts (9-13):** {mature_without} compounds")
md_lines.append(f"- **Early prompts (1-8):** {early_without} compounds")
md_lines.append("- **Organization:** Sorted by binding affinity (best to worst)")
md_lines.append("- **Note:** Includes compounds with 'PubChem CID: None' designation")
md_lines.append("")
md_lines.append("---")
md_lines.append("")

# Part A: Compounds WITH images (mature first, then early)
md_lines.append("## PART A: Compounds WITH Images")
md_lines.append("")
md_lines.append("### A1: Mature Prompts (9-13) with Images — Sorted by Binding Affinity")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

rank = 1
for row in with_images:
    if int(row['Prompt']) >= 9:
        smiles = row['SMILES'].strip()
        name = row['Compound_Name']
        affinity = row['Binding_Affinity_kcal_mol']
        residues = row['Binding_Residues']
        model = row['Model']
        prompt = row['Prompt']
        prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

        cid = smiles_to_cid[smiles]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"

        md_lines.append(f"| {rank} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} | {image} |")
        rank += 1

md_lines.append("")
md_lines.append("### A2: Early Prompts (1-8) with Images — Sorted by Binding Affinity")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

rank = 1
for row in with_images:
    if int(row['Prompt']) < 9:
        smiles = row['SMILES'].strip()
        name = row['Compound_Name']
        affinity = row['Binding_Affinity_kcal_mol']
        residues = row['Binding_Residues']
        model = row['Model']
        prompt = row['Prompt']
        prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

        cid = smiles_to_cid[smiles]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"

        md_lines.append(f"| {rank} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} | {image} |")
        rank += 1

md_lines.append("")
md_lines.append("---")
md_lines.append("")

# Part B: Compounds WITHOUT images (mature first, then early)
md_lines.append("## PART B: Compounds WITHOUT Images (To Be Validated)")
md_lines.append("")
md_lines.append("### B1: Mature Prompts (9-13) without Images — Sorted by Binding Affinity")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|")

rank = 1
for row in without_images:
    if int(row['Prompt']) >= 9:
        smiles = row['SMILES'].strip()
        name = row['Compound_Name']
        affinity = row['Binding_Affinity_kcal_mol']
        residues = row['Binding_Residues']
        model = row['Model']
        prompt = row['Prompt']
        prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

        md_lines.append(f"| {rank} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} |")
        rank += 1

md_lines.append("")
md_lines.append("### B2: Early Prompts (1-8) without Images — Sorted by Binding Affinity")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|")

rank = 1
for row in without_images:
    if int(row['Prompt']) < 9:
        smiles = row['SMILES'].strip()
        name = row['Compound_Name']
        affinity = row['Binding_Affinity_kcal_mol']
        residues = row['Binding_Residues']
        model = row['Model']
        prompt = row['Prompt']
        prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

        md_lines.append(f"| {rank} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} |")
        rank += 1

md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## Summary Statistics")
md_lines.append("")
md_lines.append(f"- **Total compounds:** {len(rows)}")
md_lines.append(f"- **With images:** {len(with_images)} ({100*len(with_images)//len(rows)}%)")
md_lines.append(f"- **Without images:** {len(without_images)} ({100*len(without_images)//len(rows)}%)")
md_lines.append("")
md_lines.append("### Image Source")
md_lines.append("- **PubChem** (https://pubchem.ncbi.nlm.nih.gov/)")
md_lines.append("- **Method:** SMILES string lookup via PubChem PUG REST API")

# Write markdown
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'w') as f:
    f.write('\n'.join(md_lines))

print(f"\n✓ Rebuilt markdown with filtered organization")
print(f"✓ Images at top ({len(with_images)} compounds)")
print(f"✓ Non-images at bottom ({len(without_images)} compounds)")
