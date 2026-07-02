#!/usr/bin/env python3
"""Fix markdown tables by properly adding Image column."""

import re
from pathlib import Path
import csv

# Read the CSV to map SMILES to image numbers
csv_file = Path("SMILES_List_Master.csv")
smiles_to_image = {}

if csv_file.exists():
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        image_num = 1
        for row in reader:
            if 'SMILES' in row:
                smiles = row['SMILES'].strip()
                smiles_to_image[smiles] = image_num
                image_num += 1

print(f"Mapped {len(smiles_to_image)} SMILES to image numbers")

# Read the markdown file
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    lines = f.readlines()

# Process line by line
output_lines = []
in_table_section_a = False
in_table_section_b = False
table_header_fixed = False
image_col_added = False

for i, line in enumerate(lines):
    # Detect start of Section A table
    if "## SECTION A:" in line:
        in_table_section_a = True
        in_table_section_b = False
        table_header_fixed = False
        output_lines.append(line)
        continue

    # Detect start of Section B table
    if "## SECTION B:" in line:
        in_table_section_a = False
        in_table_section_b = True
        table_header_fixed = False
        output_lines.append(line)
        continue

    # Detect end of table
    if line.startswith("---") and not line.startswith("| "):
        in_table_section_a = False
        in_table_section_b = False
        table_header_fixed = False
        output_lines.append(line)
        continue

    # Fix header row
    if (in_table_section_a or in_table_section_b) and line.startswith("| Rank |") and not table_header_fixed:
        # Remove the corrupted Image header and add proper columns
        new_header = "| Rank | SMILES | Compound Name | Binding Affinity (kcal/mol) | Binding Residues | Model | Prompt | Previously Found | Image |\n"
        output_lines.append(new_header)
        table_header_fixed = True
        continue

    # Fix separator row
    if (in_table_section_a or in_table_section_b) and line.startswith("|---") and table_header_fixed and not image_col_added:
        new_sep = "|------|--------|---------------|---------------------------|------------------|-------|--------|------------------|--------|\n"
        output_lines.append(new_sep)
        image_col_added = True
        continue

    # Fix data rows - extract SMILES and add image
    if (in_table_section_a or in_table_section_b) and line.startswith("| ") and table_header_fixed and image_col_added:
        # Parse the row
        parts = [p.strip() for p in line.split('|')[1:-1]]  # Remove first empty and last empty parts

        if len(parts) >= 8 and parts[1]:  # Has SMILES in position 1
            smiles = parts[1].strip()

            # Remove any image reference from the row if it exists
            if " ![Molecule]" in smiles:
                smiles = smiles.split(" ![Molecule]")[0].strip()

            # Look up image number
            if smiles in smiles_to_image:
                img_num = smiles_to_image[smiles]
                # Reconstruct row with proper columns
                new_row = f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} | {parts[4]} | {parts[5]} | {parts[6]} | {parts[7]} | ![Molecule](molecule_images/molecule_{img_num}.png) |\n"
                output_lines.append(new_row)
            else:
                # Keep as is
                output_lines.append(line)
        else:
            output_lines.append(line)
        continue

    # Keep other lines as is
    output_lines.append(line)

# Write the fixed markdown
with open(md_file, 'w') as f:
    f.writelines(output_lines)

print(f"✓ Fixed markdown tables with Image column")
