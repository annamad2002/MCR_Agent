#!/usr/bin/env python3
"""Rebuild markdown Part 2 with literature findings column."""

import csv
import json
from pathlib import Path

# Load literature findings
lit_file = Path("mcr_compound_details.json")
literature_data = {}

if lit_file.exists():
    with open(lit_file, 'r') as f:
        data = json.load(f)
        compound_db = data.get("compound_database", {})
        for rank_key, compound_info in compound_db.items():
            name = compound_info.get("compound_name", "").strip()
            status = compound_info.get("literature_status", "No literature found")
            mechanism = compound_info.get("mechanism", "")
            notes = compound_info.get("structural_notes", "")

            # Build summary
            summary = status
            if mechanism:
                summary += f" - {mechanism}"
            if notes and "No literature" not in status:
                summary += f". {notes}"

            literature_data[name] = summary

print(f"Loaded literature data for {len(literature_data)} compounds")

# Read the current markdown
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    content = f.read()

# Read CSV for compound list
csv_file = Path("SMILES_List_Master.csv")
rows = []
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Separate into groups
known_names = {
    'Lovastatin', 'Capric Acid', 'Citral', 'Eugenol',
    'Limonene', 'p-cymene', 'Bromoform'
}

known = []
new_with_images = []

for row in rows:
    name = row['Compound_Name'].strip()
    is_known = any(known_name.lower() == name.lower() for known_name in known_names)

    if is_known:
        known.append(row)
    else:
        # Check if it has an image
        smiles = row['SMILES'].strip()
        # We'll check this later from the mapping
        new_with_images.append(row)

print(f"Known: {len(known)}, New with images: {len(new_with_images)}")

# Now rebuild just Part 2 with the literature column
# Split the current markdown
parts = content.split("## PART 2: New Compounds WITH Images")

if len(parts) != 2:
    print("Error: Could not find Part 2 in markdown")
    exit(1)

header_part = parts[0]
rest = parts[1]

# Find where Part 2 ends (look for "## PART 3")
if "## PART 3:" in rest:
    part2_content = rest.split("## PART 3:")[0]
    part3_onwards = "## PART 3:" + rest.split("## PART 3:")[1]
else:
    part2_content = rest
    part3_onwards = ""

# Build new Part 2
new_part2 = "## PART 2: New Compounds WITH Images\n"

# Separate mature and early
mature = [r for r in new_with_images if int(r['Prompt']) >= 9]
early = [r for r in new_with_images if int(r['Prompt']) < 9]

# Load SMILES mapping
mapping_file = Path("smiles_to_cid_mapping.json")
with open(mapping_file, 'r') as f:
    smiles_to_cid = json.load(f)

# 2A: Mature
new_part2 += "\n### 2A: Mature Prompts (9-13) with Images — Sorted by Binding Affinity\n\n"
new_part2 += "| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Model | Prompt | Image | Literature/MCR Data |\n"
new_part2 += "|------|--------|---------------|---------------------------|-------|--------|--------|---------------------|\n"

rank = 1
for row in mature:
    smiles = row['SMILES'].strip()
    name = row['Compound_Name']
    affinity = row['Binding_Affinity_kcal_mol']
    model = row['Model']
    prompt = row['Prompt']

    # Get image
    if smiles in smiles_to_cid and smiles_to_cid[smiles] != 0:
        cid = smiles_to_cid[smiles]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"
    else:
        image = "No image"

    # Get literature data
    lit_info = literature_data.get(name, "No literature found")
    # Truncate to 100 chars for readability
    if len(lit_info) > 100:
        lit_info = lit_info[:97] + "..."

    new_part2 += f"| {rank} | {smiles} | {name} | {affinity} | {model} | {prompt} | {image} | {lit_info} |\n"
    rank += 1

# 2B: Early
new_part2 += "\n### 2B: Early Prompts (1-8) with Images — Sorted by Binding Affinity\n\n"
new_part2 += "| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Model | Prompt | Image | Literature/MCR Data |\n"
new_part2 += "|------|--------|---------------|---------------------------|-------|--------|--------|---------------------|\n"

rank = 1
for row in early:
    smiles = row['SMILES'].strip()
    name = row['Compound_Name']
    affinity = row['Binding_Affinity_kcal_mol']
    model = row['Model']
    prompt = row['Prompt']

    # Get image
    if smiles in smiles_to_cid and smiles_to_cid[smiles] != 0:
        cid = smiles_to_cid[smiles]
        image = f"![Molecule](pubchem_images/pubchem_{cid}.png)"
    else:
        image = "No image"

    # Get literature data
    lit_info = literature_data.get(name, "No literature found")
    # Truncate to 100 chars
    if len(lit_info) > 100:
        lit_info = lit_info[:97] + "..."

    new_part2 += f"| {rank} | {smiles} | {name} | {affinity} | {model} | {prompt} | {image} | {lit_info} |\n"
    rank += 1

new_part2 += "\n"

# Reconstruct full markdown
new_content = header_part + new_part2 + "\n---\n\n" + part3_onwards

# Write back
with open(md_file, 'w') as f:
    f.write(new_content)

print("✓ Updated Part 2 with literature column")
