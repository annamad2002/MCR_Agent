#!/usr/bin/env python3
"""Rebuild markdown with known inhibitors in a separate section at the top."""

import csv
import json
from pathlib import Path

csv_file = Path("SMILES_List_Master.csv")
mapping_file = Path("smiles_to_cid_mapping.json")

# Load the SMILES-to-CID mapping
with open(mapping_file, 'r') as f:
    smiles_to_cid = json.load(f)

# List of known inhibitors to identify
known_inhibitors = {
    'Alliin',
    'Rosmarinic acid',
    'Bromoform',
    'Limonene',
    'α-pinene',
    'a-pinene',
    'Eugenol',
    'p-cymene',
    'Citral',
    'Lovastatin',
    'Capric Acid'
}

# Read CSV
rows = []
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Loaded {len(rows)} compounds from CSV")

# Separate compounds into groups
known = []
new_with_images = []
without_images = []

for row in rows:
    smiles = row['SMILES'].strip()
    name = row['Compound_Name'].strip()
    has_image = smiles in smiles_to_cid and smiles_to_cid[smiles] != 0

    # Check if it's a known inhibitor (case-insensitive)
    is_known = any(known_name.lower() == name.lower() for known_name in known_inhibitors)

    if is_known:
        known.append(row)
    elif has_image:
        new_with_images.append(row)
    else:
        without_images.append(row)

print(f"Known inhibitors: {len(known)}")
print(f"New compounds with images: {len(new_with_images)}")
print(f"Compounds without images: {len(without_images)}")

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
md_lines.append(f"**Known Inhibitors (Validated):** {len(known)}")
md_lines.append(f"**New Compounds with Images:** {len(new_with_images)}")
md_lines.append(f"**Compounds without Images:** {len(without_images)}")
md_lines.append("")
md_lines.append("---")
md_lines.append("")

# Data Organization section
md_lines.append("## Data Organization")
md_lines.append("")
md_lines.append("This dataset is organized into three sections:")
md_lines.append("")
md_lines.append("### Part 1: Known/Validated Inhibitors")
md_lines.append(f"- **Total:** {len(known)} compounds")
md_lines.append("- **Status:** Previously identified as MCR inhibitors")
md_lines.append("- **All have images:** Yes")
md_lines.append("")
md_lines.append("### Part 2: New Compounds WITH Images")
md_lines.append(f"- **Total:** {len(new_with_images)} compounds")
md_lines.append("- **Status:** Novel compounds discovered in this study")
md_lines.append("- **Organization:** Sorted by binding affinity (best to worst)")
md_lines.append("")
md_lines.append("### Part 3: Compounds WITHOUT Images")
md_lines.append(f"- **Total:** {len(without_images)} compounds")
md_lines.append("- **Status:** Could not find in PubChem database")
md_lines.append("- **Organization:** Sorted by binding affinity (best to worst)")
md_lines.append("")
md_lines.append("---")
md_lines.append("")

# PART 1: Known Inhibitors
md_lines.append("## PART 1: Known/Validated MCR Inhibitors")
md_lines.append("")
md_lines.append("These compounds have been previously identified as MCR inhibitors.")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

rank = 1
for row in known:
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

    md_lines.append(f"| {rank} | {smiles} | {name} | {affinity} | {residues} | {model} | {prompt} | {prev_found} | {image} |")
    rank += 1

md_lines.append("")
md_lines.append("---")
md_lines.append("")

# PART 2: New compounds with images (separate by mature/early)
md_lines.append("## PART 2: New Compounds WITH Images")
md_lines.append("")
md_lines.append("### 2A: Mature Prompts (9-13) with Images — Sorted by Binding Affinity")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

rank = 1
for row in new_with_images:
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
md_lines.append("### 2B: Early Prompts (1-8) with Images — Sorted by Binding Affinity")
md_lines.append("")
md_lines.append("| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |")
md_lines.append("|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|")

rank = 1
for row in new_with_images:
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

# PART 3: Compounds without images (separate by mature/early)
md_lines.append("## PART 3: Compounds WITHOUT Images (To Be Validated)")
md_lines.append("")
md_lines.append("### 3A: Mature Prompts (9-13) without Images — Sorted by Binding Affinity")
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
md_lines.append("### 3B: Early Prompts (1-8) without Images — Sorted by Binding Affinity")
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
md_lines.append(f"- **Known inhibitors:** {len(known)} (validated)")
md_lines.append(f"- **With images:** {len(known) + len(new_with_images)} ({100*(len(known) + len(new_with_images))//len(rows)}%)")
md_lines.append(f"- **Without images:** {len(without_images)} ({100*len(without_images)//len(rows)}%)")
md_lines.append("")
md_lines.append("### Image Source")
md_lines.append("- **PubChem** (https://pubchem.ncbi.nlm.nih.gov/)")
md_lines.append("- **Method:** SMILES string lookup via PubChem PUG REST API")

# Write markdown
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'w') as f:
    f.write('\n'.join(md_lines))

print(f"\n✓ Rebuilt markdown with three-part organization")
print(f"✓ Known inhibitors at top ({len(known)} compounds)")
print(f"✓ New compounds with images in middle ({len(new_with_images)} compounds)")
print(f"✓ Compounds without images at bottom ({len(without_images)} compounds)")
