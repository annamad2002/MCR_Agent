#!/usr/bin/env python3
"""Replace missing images with "Image not found" labels."""

import os
from pathlib import Path
import re

# Get list of existing images
img_dir = Path("molecule_images")
existing_images = set()
if img_dir.exists():
    for img_file in img_dir.glob("*.png"):
        num = int(img_file.stem.split("_")[1])
        existing_images.add(num)

print(f"Found {len(existing_images)} existing images: {sorted(existing_images)}")

# Read the markdown file
md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    content = f.read()

# Find all image references and check if they exist
pattern = r'!\[Molecule\]\(molecule_images/molecule_(\d+)\.png\)'
matches = re.finditer(pattern, content)

missing_count = 0
for match in matches:
    img_num = int(match.group(1))
    if img_num not in existing_images:
        missing_count += 1

print(f"Found {missing_count} references to missing images")

# Replace missing image references with "Image not found"
def replace_missing_images(match):
    img_num = int(match.group(1))
    if img_num not in existing_images:
        return "Image not found"
    else:
        return match.group(0)

updated_content = re.sub(pattern, replace_missing_images, content)

# Write the updated markdown
with open(md_file, 'w') as f:
    f.write(updated_content)

print(f"✓ Updated markdown file")
print(f"✓ {missing_count} missing images labeled as 'Image not found'")
print(f"✓ {len(existing_images)} images are properly referenced")
