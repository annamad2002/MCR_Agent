#!/usr/bin/env python3
"""Extract final recommendations from prompt chat logs and rebuild CSV."""

import os
import re
from pathlib import Path
from collections import defaultdict

# Directory containing all prompts
base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Store final recommendations
final_recommendations = []
issues = []

# Go through each prompt directory (1-13)
for prompt_num in range(1, 14):
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        print(f"Prompt {prompt_num}: Directory not found")
        continue

    print(f"\n=== Prompt {prompt_num} ===")

    # List all chat log files
    chat_files = [f for f in prompt_dir.iterdir() if f.is_file() and not f.name.startswith('.')]

    if not chat_files:
        print(f"No chat files found in {prompt_num}/")
        continue

    for chat_file in sorted(chat_files):
        # Skip docking results directories
        if chat_file.is_dir() or "docking" in chat_file.name:
            continue

        # Extract model name from filename
        filename = chat_file.name
        print(f"\nProcessing: {filename}")

        try:
            with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for "Final selection:" section
            if "Final selection:" not in content:
                print(f"  ⚠ No 'Final selection:' found")
                continue

            # Find the final selection section
            final_section = content[content.find("Final selection:"):]

            # Extract SMILES from the table
            # Look for SMILES in the format: | SMILES | ... |
            smiles_pattern = r'\|\s*([A-Z0-9\[\]\@\#=\-\\/\(\)C]+)\s*\|'
            smiles_matches = re.findall(smiles_pattern, final_section[:2000])  # Look in first 2000 chars of final section

            if not smiles_matches:
                print(f"  ⚠ No SMILES found in final selection")
                continue

            # First match in final selection table is usually the SMILES column header, skip it
            for smiles in smiles_matches[1:]:  # Skip header
                if len(smiles) > 5:  # Valid SMILES are usually longer
                    # Extract compound name if available
                    compound_name = extract_compound_name(content, smiles)

                    final_recommendations.append({
                        'prompt': prompt_num,
                        'model': extract_model_name(filename),
                        'smiles': smiles,
                        'compound_name': compound_name
                    })
                    print(f"  ✓ {smiles[:50]}... ({compound_name})")

        except Exception as e:
            issues.append(f"Error reading {prompt_num}/{filename}: {str(e)}")
            print(f"  ✗ Error: {str(e)}")

print(f"\n\n=== SUMMARY ===")
print(f"Total final recommendations found: {len(final_recommendations)}")
print(f"Unique SMILES: {len(set(r['smiles'] for r in final_recommendations))}")
print(f"Issues encountered: {len(issues)}")

if issues:
    print("\nIssues:")
    for issue in issues[:10]:
        print(f"  - {issue}")

# Write to validation CSV
output_file = base_dir / "SMILES_Final_Recommendations_ONLY.csv"
with open(output_file, 'w') as f:
    f.write("Prompt,Model,SMILES,Compound_Name\n")
    for rec in sorted(final_recommendations, key=lambda x: (x['prompt'], x['model'])):
        # Escape quotes in compound name
        name = rec['compound_name'].replace('"', '""') if rec['compound_name'] else ""
        f.write(f'{rec["prompt"]},"{rec["model"]}","{rec["smiles"]}","{name}"\n')

print(f"\n✓ Validation file saved: {output_file}")

def extract_compound_name(content, smiles):
    """Try to extract compound name for this SMILES."""
    # Look for compound name near the SMILES in the content
    idx = content.find(smiles)
    if idx > 0:
        snippet = content[max(0, idx-500):idx+500]
        # Look for common patterns like "Name: ..." or similar
        name_patterns = [
            r'Compound[:\s]+([^,\|]+)',
            r'Name[:\s]+([^,\|]+)',
            r'\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, snippet)
            if match and match.group(1):
                return match.group(1).strip()[:100]
    return ""

def extract_model_name(filename):
    """Extract model name from chat file name."""
    # Examples: "12 - gemma", "12 - gemma - 2"
    if " - " in filename:
        parts = filename.split(" - ")
        return " - ".join(parts[1:]).strip()
    return filename

print(f"\nNext steps:")
print(f"1. Review {output_file} to ensure all SMILES are correct")
print(f"2. Compare with SMILES_List_Master.csv to identify discrepancies")
print(f"3. Rebuild master CSV with only validated final recommendations")
