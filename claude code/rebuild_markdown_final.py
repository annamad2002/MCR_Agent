#!/usr/bin/env python3
"""Rebuild markdown with complete SMILES-to-CID mapping."""

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

# Separate by prompt group
mature = [r for r in rows if int(r['Prompt']) >= 9]
early = [r for r in rows if int(r['Prompt']) < 9]

print(f"Mature prompts (9-13): {len(mature)}")
print(f"Early prompts (1-8): {len(early)}")

# Count how many have images
image_count = 0
for row in rows:
    smiles = row['SMILES'].strip()
    if smiles in smiles_to_cid and smiles_to_cid[smiles] != 0:
        image_count += 1

print(f"Compounds with images: {image_count}")

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
md_lines.append(f"**Compounds with Images:** {image_count}")
md_lines.append(f"**Compounds without Images:** {len(rows) - image_count}")
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
    smiles = row['SMILES'].strip()
    name = row['Compound_Name']
    affinity = row['Binding_Affinity_kcal_mol']
    residues = row['Binding_Residues']
    model = row['Model']
    prompt = row['Prompt']
    prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

    # Get image
    if smiles in smiles_to_cid and smiles_to_cid[smiles] != 0:
        cid = smiles_to_cid[smiles]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"
    else:
        image = "Image not found"

    md_lines.append(f"| {i} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} | {image} |")

md_lines.append("")

# Section B table
md_lines.append("## SECTION B: Early Prompts (1-8) — Reference Collection")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

for i, row in enumerate(early, len(mature) + 1):
    smiles = row['SMILES'].strip()
    name = row['Compound_Name']
    affinity = row['Binding_Affinity_kcal_mol']
    residues = row['Binding_Residues']
    model = row['Model']
    prompt = row['Prompt']
    prev_found = "✓ Yes" if row['Previously_Found'] == 'True' else "No"

    # Get image
    if smiles in smiles_to_cid and smiles_to_cid[smiles] != 0:
        cid = smiles_to_cid[smiles]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"
    else:
        image = "Image not found"

    md_lines.append(f"| {i} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} | {image} |")

md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## Image Availability")
md_lines.append("")
md_lines.append(f"- **Images found:** {image_count}/{len(rows)} ({100*image_count//len(rows)}%)")
md_lines.append(f"- **Source:** PubChem (https://pubchem.ncbi.nlm.nih.gov/)")
md_lines.append("- **Method:** SMILES string lookup via PubChem PUG REST API")

# Write markdown
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'w') as f:
    f.write('\n'.join(md_lines))

print(f"\n✓ Rebuilt markdown with {image_count} images")
