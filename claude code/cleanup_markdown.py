#!/usr/bin/env python3
"""Clean up markdown by removing duplicate images and "Image not found" when image exists."""

import re
from pathlib import Path

md_file = Path("SMILES_List_Master.md")
with open(md_file, 'r') as f:
    lines = f.readlines()

cleaned_lines = []

for line in lines:
    # Skip header and separator rows
    if not line.startswith('|') or 'Rank' in line or '---' in line:
        cleaned_lines.append(line)
        continue

    # For data rows, clean up the image column
    if line.startswith('|') and re.match(r'\|\s*\d+\s*\|', line):
        # Split by pipes
        cells = [c.strip() for c in line.split('|')[1:-1]]  # Remove first and last empty

        if len(cells) >= 8:
            # Get the image cells (last 1-2 cells may be images)
            # Find all image references in the row
            images = re.findall(r'!\[Molecule\]\([^)]+\)', line)

            if images:
                # Keep only the best/latest image
                best_image = images[-1]  # Take the last one (PubChem images are better)

                # Remove all image references and "Image not found" from the line
                clean_line = line
                for img in images:
                    clean_line = clean_line.replace(img, '')
                clean_line = clean_line.replace('Image not found', '')

                # Remove extra pipes and spaces
                clean_line = re.sub(r'\|\s*\|', '|', clean_line)
                clean_line = re.sub(r'\s+\|', ' |', clean_line)

                # Add back the single best image
                clean_line = clean_line.rstrip('|') + f' | {best_image} |\n'
                cleaned_lines.append(clean_line)
            else:
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    else:
        cleaned_lines.append(line)

# Write cleaned markdown
with open(md_file, 'w') as f:
    f.writelines(cleaned_lines)

print("✓ Cleaned up markdown file")

# Count final images
with open(md_file, 'r') as f:
    content = f.read()

image_count = len(re.findall(r'!\[Molecule\]', content))
print(f"✓ Total images in markdown: {image_count}")
