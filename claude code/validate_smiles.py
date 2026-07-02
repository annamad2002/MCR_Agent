#!/usr/bin/env python3
"""
Validate SMILES_List_Master.csv by extracting final recommendations from chat logs
and comparing them against the master list.
"""

import os
import re
import json
import csv
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

def extract_smiles_from_table(text):
    """Extract SMILES from markdown tables in text."""
    smiles_list = []

    # Look for markdown table patterns with SMILES column
    # Pattern: | compound | SMILES | ... with backticks around SMILES
    lines = text.split('\n')

    in_table = False
    smiles_col_idx = -1

    for line in lines:
        if '|' not in line:
            in_table = False
            continue

        parts = [p.strip() for p in line.split('|')]

        # Skip empty parts at start and end
        parts = [p for p in parts if p]

        # Check if this is a header row with SMILES
        if not in_table and 'SMILES' in line.upper():
            in_table = True
            # Find index of SMILES column
            for idx, part in enumerate(parts):
                if 'SMILES' in part.upper():
                    smiles_col_idx = idx
                    break
            continue

        # Skip separator rows (all dashes)
        if all(c in '-' for c in line.replace('|', '').strip()):
            continue

        # Extract SMILES from data rows
        if in_table and smiles_col_idx >= 0 and len(parts) > smiles_col_idx:
            smiles_str = parts[smiles_col_idx]
            # Remove backticks if present
            smiles_str = smiles_str.strip('`')

            # Only add if it looks like a valid SMILES (starts with C, N, O, S, [, etc)
            if smiles_str and smiles_str[0] in 'CNOS[(' and not smiles_str.startswith('SMILES'):
                smiles_list.append(smiles_str)

    return smiles_list

def parse_final_selection_table(content):
    """Extract all final recommendation SMILES from content."""
    all_smiles = []

    # Look for the "Content:" section that marks the final summary/recommendations
    # This contains the "Recommended Compounds" or similar heading with SMILES in backticks
    if 'Content:' not in content:
        return all_smiles

    # Find the last "Content:" section (it might appear multiple times)
    last_content_idx = content.rfind('Content:')
    if last_content_idx < 0:
        return all_smiles

    # Get everything after the last "Content:"
    content_section = content[last_content_idx:]

    # The content section usually ends with a separator line (--------) or end of file
    end_idx = len(content_section)
    dash_idx = content_section.find('--------')
    if dash_idx > 0:
        end_idx = dash_idx

    content_section = content_section[:end_idx]

    # Extract SMILES from backticks
    # Pattern: `SMILES_HERE`
    smiles_pattern = r'`([^`]+)`'

    found_smiles = []
    for match in re.finditer(smiles_pattern, content_section):
        potential_smiles = match.group(1).strip()

        # Validate it looks like SMILES
        # SMILES start with C, N, O, S, [, or ( and contain organic chemistry chars
        if potential_smiles and len(potential_smiles) > 1:
            # Check if it looks like a SMILES string (common patterns)
            if potential_smiles[0] in 'CNOSPBclnos[(' and ' ' not in potential_smiles:
                # Make sure it's not a header or label
                if potential_smiles.lower() != 'smiles' and not any(stop in potential_smiles for stop in ['http', 'www']):
                    found_smiles.append(potential_smiles)

    # Remove duplicates while preserving order
    seen = set()
    unique_smiles = []
    for s in found_smiles:
        if s not in seen:
            seen.add(s)
            unique_smiles.append(s)

    return unique_smiles

def extract_model_from_filename(filename):
    """Extract model name from chat log filename."""
    # Files are like "12 - gemma", "12 - gemma - 2", etc.
    parts = filename.split(' - ')
    if len(parts) >= 2:
        model = parts[1]
        return model
    return "unknown"

def process_prompt_directory(prompt_num):
    """Process all chat logs in a single prompt directory."""
    prompt_dir = BASE_DIR / str(prompt_num)

    if not prompt_dir.exists():
        return []

    results = []

    # Find all chat log files (could have .md extension or no extension)
    for file_path in sorted(prompt_dir.iterdir()):
        if not file_path.is_file():
            continue

        filename = file_path.name

        # Skip docking results, hidden files, etc.
        if (filename.startswith('.') or 'docking' in filename.lower() or
            filename.endswith('.csv') or filename.endswith('.ini')):
            continue

        # Check if it's a chat log file (starts with prompt number)
        if not filename.startswith(str(prompt_num)):
            continue

        # Read the file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Extract final selection SMILES
            smiles_list = parse_final_selection_table(content)

            if smiles_list:  # Only process if we found something
                model = extract_model_from_filename(filename)

                for smiles in smiles_list:
                    results.append({
                        'prompt': prompt_num,
                        'model': model,
                        'filename': filename,
                        'smiles': smiles
                    })

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return results

def load_master_csv():
    """Load the master SMILES CSV."""
    smiles_map = {}  # smiles -> {rank, model, prompt, etc}

    csv_path = BASE_DIR / "SMILES_List_Master.csv"

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Detect delimiter
            first_line = f.readline()
            f.seek(0)

            delimiter = '\t' if '\t' in first_line else ','

            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                if row.get('SMILES'):
                    smiles = row['SMILES'].strip()
                    smiles_map[smiles] = row
    except Exception as e:
        print(f"Error loading master CSV: {e}")

    return smiles_map

def main():
    """Main validation process."""
    print("Starting SMILES validation...")
    print("=" * 80)

    # Extract final recommendations from all prompts
    all_final_recommendations = []

    for prompt_num in range(1, 14):
        print(f"\nProcessing Prompt {prompt_num}...")
        results = process_prompt_directory(prompt_num)
        print(f"  Found {len(results)} final recommendation SMILES")
        all_final_recommendations.extend(results)

    print(f"\nTotal final recommendations found: {len(all_final_recommendations)}")

    # Load master CSV
    master_map = load_master_csv()
    print(f"Total SMILES in master CSV: {len(master_map)}")

    # Get unique SMILES from final recommendations
    final_smiles_set = set(r['smiles'] for r in all_final_recommendations)
    print(f"Unique SMILES in final recommendations: {len(final_smiles_set)}")

    # Find discrepancies
    master_smiles_set = set(master_map.keys())

    # Missing SMILES (in final recommendations but not in CSV)
    missing_in_csv = final_smiles_set - master_smiles_set

    # Extra SMILES (in CSV but not from final recommendations)
    extra_in_csv = master_smiles_set - final_smiles_set

    print(f"\nMissing in CSV (in final recs but not CSV): {len(missing_in_csv)}")
    print(f"Extra in CSV (in CSV but not final recs): {len(extra_in_csv)}")

    # Save results
    output_dir = BASE_DIR

    # 1. Save all final recommendations
    with open(output_dir / "final_recommendations_validated.json", 'w') as f:
        json.dump(all_final_recommendations, f, indent=2)

    # 2. Create validation report
    report = []
    report.append("SMILES VALIDATION REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated: {open(BASE_DIR / 'SMILES_List_Master.csv').readline()}")
    report.append(f"\nTotal final recommendations found: {len(all_final_recommendations)}")
    report.append(f"Unique SMILES in final recommendations: {len(final_smiles_set)}")
    report.append(f"Total SMILES in master CSV: {len(master_map)}")
    report.append(f"\nDISCREPANCIES:")
    report.append(f"Missing in CSV (in final recs but not CSV): {len(missing_in_csv)}")
    report.append(f"Extra in CSV (in CSV but not from final recs): {len(extra_in_csv)}")

    if missing_in_csv:
        report.append(f"\n\nMISSING SMILES (need to be added to CSV):")
        report.append("-" * 80)
        # Group by prompt
        missing_by_prompt = defaultdict(list)
        for rec in all_final_recommendations:
            if rec['smiles'] in missing_in_csv:
                missing_by_prompt[rec['prompt']].append(rec)

        for prompt in sorted(missing_by_prompt.keys()):
            report.append(f"\nPrompt {prompt}:")
            for rec in missing_by_prompt[prompt]:
                report.append(f"  Model: {rec['model']}")
                report.append(f"  SMILES: {rec['smiles']}")

    if extra_in_csv:
        report.append(f"\n\nEXTRA SMILES (should be removed or verified):")
        report.append("-" * 80)
        for smiles in sorted(extra_in_csv):
            csv_row = master_map[smiles]
            report.append(f"SMILES: {smiles}")
            report.append(f"  Rank: {csv_row.get('Rank', 'N/A')}")
            report.append(f"  Model: {csv_row.get('Model', 'N/A')}")
            report.append(f"  Prompt: {csv_row.get('Prompt', 'N/A')}")

    # Save report
    with open(output_dir / "validation_report.txt", 'w') as f:
        f.write('\n'.join(report))

    # 3. Create CSV of corrections needed
    corrections = []
    all_fieldnames = set()

    for smiles in sorted(missing_in_csv):
        # Find which prompts/models have this SMILES
        sources = [r for r in all_final_recommendations if r['smiles'] == smiles]
        for src in sources:
            row = {
                'action': 'ADD',
                'smiles': smiles,
                'model': src['model'],
                'prompt': src['prompt']
            }
            corrections.append(row)
            all_fieldnames.update(row.keys())

    for smiles in sorted(extra_in_csv):
        csv_row = master_map[smiles]
        row = {
            'action': 'REMOVE/VERIFY',
            'smiles': smiles,
            'current_model': csv_row.get('Model', 'N/A'),
            'current_prompt': csv_row.get('Prompt', 'N/A'),
            'rank': csv_row.get('Rank', 'N/A')
        }
        corrections.append(row)
        all_fieldnames.update(row.keys())

    with open(output_dir / "smiles_corrections_needed.csv", 'w', newline='') as f:
        if corrections:
            fieldnames = sorted(all_fieldnames)
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(corrections)

    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Files created:")
    print(f"  - final_recommendations_validated.json")
    print(f"  - validation_report.txt")
    print(f"  - smiles_corrections_needed.csv")
    print("\n" + report[0])
    print('\n'.join(report[1:20]))  # Print first part of report

if __name__ == "__main__":
    main()
