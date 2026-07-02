#!/usr/bin/env python3
"""Generate molecule images from SMILES strings and embed them in markdown."""

import os
import re
import csv
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Draw, AllChem

# Create directory for images
img_dir = Path("molecule_images")
img_dir.mkdir(exist_ok=True)

# Read the markdown file
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    content = f.read()

# Extract SMILES from the markdown tables
# Pattern to match table rows with SMILES
pattern = r'\|\s*\d+\s*\|\s*([A-Z0-9\[\]\@\#=\-\/\\()]+)\s*\|'
smiles_list = re.findall(pattern, content)

print(f"Found {len(smiles_list)} SMILES strings")

# Generate images
generated_images = {}
failed_smiles = []

for i, smiles in enumerate(smiles_list, 1):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"  ✗ Failed to parse SMILES {i}: {smiles[:50]}...")
            failed_smiles.append(smiles)
            continue

        # Generate 2D coordinates
        AllChem.Compute2DCoords(mol)

        # Generate image
        img_path = img_dir / f"molecule_{i}.png"
        img = Draw.MolToImage(mol, size=(200, 200))
        img.save(img_path)

        generated_images[smiles] = f"molecule_images/molecule_{i}.png"

        if i % 20 == 0:
            print(f"  ✓ Generated {i} images...")

    except Exception as e:
        print(f"  ✗ Error generating image for SMILES {i}: {str(e)[:60]}")
        failed_smiles.append(smiles)

print(f"\n✓ Successfully generated {len(generated_images)} images")
if failed_smiles:
    print(f"✗ Failed to generate images for {len(failed_smiles)} SMILES")

# Now update the markdown file to include images
# We'll modify the table to add an image column

def update_markdown_table(content, generated_images):
    """Update markdown tables to include molecule images."""

    lines = content.split('\n')
    output_lines = []
    in_table = False
    header_updated = False
    smiles_to_img = {}

    # Build the mapping
    for smiles, img_path in generated_images.items():
        smiles_to_img[smiles] = img_path

    for i, line in enumerate(lines):
        # Detect table start (header line with pipe characters)
        if '| Rank |' in line or '| Compound |' in line:
            in_table = True
            header_updated = False

        if in_table and '| Rank |' in line and not header_updated:
            # Add Image column to header
            if 'Image' not in line:
                line = line.rstrip('|') + ' Image |'
                header_updated = True

        elif in_table and line.startswith('|---'):
            # Add separator for image column
            if '---|' not in line or line.count('---') < 8:  # Check if we need to add
                line = line.rstrip('|') + ' --- |'

        elif in_table and line.startswith('|') and '|' in line:
            # Check if this is a data row (contains SMILES pattern)
            if re.search(r'\|\s*\d+\s*\|', line):
                # Find the SMILES in this line
                match = re.search(r'\|\s*\d+\s*\|\s*([A-Z0-9\[\]\@\#=\-\/\\()]+)', line)
                if match:
                    smiles = match.group(1).strip()
                    if smiles in smiles_to_img:
                        img_path = smiles_to_img[smiles]
                        # Add image reference to end of line
                        line = line.rstrip() + f' ![Molecule]({img_path}) |'
                    else:
                        # No image, add empty cell
                        line = line.rstrip() + ' |'

        elif in_table and line.strip() == '':
            in_table = False

        output_lines.append(line)

    return '\n'.join(output_lines)

# Update the markdown
updated_content = update_markdown_table(content, generated_images)

# Write updated markdown
with open(md_file, 'w') as f:
    f.write(updated_content)

print(f"\n✓ Updated {md_file}")
print(f"✓ Images saved to {img_dir}/")
