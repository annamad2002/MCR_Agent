#!/usr/bin/env python3
"""
Collates SMILES, binding affinity, model, and prompt data from chat logs
into a single master CSV file with no duplicate SMILES entries.
"""

import os
import re
import pandas as pd
from pathlib import Path

# Base directory
base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

def extract_smiles_from_text(text):
    """Extract SMILES strings from text using regex pattern."""
    # SMILES pattern: alphanumeric and special characters: C,c,N,n,O,o,S,s,P,p,B,b, etc.
    # Followed by brackets, numbers, operators: ()-=+#/\@.
    smiles_pattern = r'[C-Sc-s0-9\[\]\(\)\-=+#/\\@\.]+'

    # More specific: look for valid SMILES starting with common elements or brackets
    # This regex looks for patterns that start with valid SMILES characters
    smiles_pattern = r'(?:^|[^a-zA-Z0-9])([C-Sc-s0-9\[\]\(\)\-=+#/\\@\.]+?)(?:[^a-zA-Z0-9\[\]]|$)'

    # Better approach: look for specific patterns
    # SMILES typically start with elements like C, c, N, n, O, o, P, p, S, s, B, b, or [
    # and end with numbers, ), or ]
    pattern = r'\b(?:[C-Sc-s0-9\[\]\(\)\-=+#/\\@\.]*[C-Sc-s0-9\]\)])\b'

    matches = re.findall(pattern, text)
    return matches

def extract_affinity_from_section(section_text):
    """Extract binding affinity (first mode affinity) from docking output section."""
    # Look for the affinity table format:
    # mode |   affinity | dist from best mode
    #      | (kcal/mol) | rmsd l.b.| rmsd u.b.
    # -----+------------+----------+----------
    #    1         -8.6      0.000      0.000

    lines = section_text.split('\n')
    affinity = None

    for line in lines:
        # Look for lines with mode number and affinity value
        # Pattern: whitespace, number (mode), whitespace, number with decimal (affinity)
        match = re.search(r'^\s*(\d+)\s+(-?\d+\.\d+)', line)
        if match:
            mode_num = int(match.group(1))
            aff_val = float(match.group(2))
            # We want the first mode (best affinity)
            if mode_num == 1:
                affinity = aff_val
                break

    return affinity

def parse_chat_log(filepath):
    """
    Parse a chat log file and extract SMILES, affinities, model name, and prompt number.
    Returns a list of dictionaries with extracted data.
    """
    data = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return data

    # Extract model name from filename
    filename = Path(filepath).name
    # Format: "13 - gemma" or "11 - devstral", etc.
    match = re.search(r'(\d+)\s*-\s*(.+?)$', filename)
    if match:
        prompt_num = int(match.group(1))
        model_name = match.group(2).strip()
    else:
        # If filename is just a number like "1.md"
        match = re.search(r'^(\d+)', filename)
        if match:
            prompt_num = int(match.group(1))
            model_name = "unknown"
        else:
            return data

    # Extract SMILES and their associated affinities
    # Look for patterns: "Calling quick_run with arguments {'SMILES': 'SMILES_STRING'..."
    # followed by docking output

    # Split by "Calling quick_run" to identify separate molecule runs
    sections = content.split('Calling quick_run')

    for section_idx, section in enumerate(sections):
        if section_idx == 0:
            # First section is before any quick_run calls
            continue

        # Extract SMILES from this section
        smiles_match = re.search(r"'SMILES':\s*'([^']+)'", section)
        if not smiles_match:
            continue

        smiles = smiles_match.group(1).strip()

        # Extract affinity from this section
        affinity = extract_affinity_from_section(section)

        # Only add if we found both SMILES and affinity
        if smiles and affinity is not None:
            data.append({
                'SMILES': smiles,
                'Binding_Affinity_kcal_mol': affinity,
                'Model': model_name,
                'Prompt': prompt_num
            })

    return data

def main():
    """Main function to collate all SMILES data from chat logs."""
    all_data = []

    # Walk through all numbered directories
    for i in range(1, 14):  # Prompts 1-13
        prompt_dir = base_dir / str(i)
        if not prompt_dir.exists():
            continue

        print(f"Processing prompt {i}...")

        # Find all chat log files in this directory
        for filepath in prompt_dir.iterdir():
            # Skip directories and .DS_Store
            if filepath.is_dir() or filepath.name == '.DS_Store':
                continue

            # Chat logs are files without extension or with generic names
            # They have names like "11 - gemma", "11 - devstral", etc. (no .md extension)
            # Skip known non-chat files
            if filepath.suffix in ['.json', '.xml', '.ipynb']:
                continue

            print(f"  Parsing {filepath.name}...")
            extracted = parse_chat_log(filepath)
            all_data.extend(extracted)

    # Create DataFrame
    df = pd.DataFrame(all_data)

    if df.empty:
        print("No data extracted!")
        return

    print(f"\nTotal entries before deduplication: {len(df)}")

    # Remove duplicate SMILES, keeping the first occurrence
    df = df.drop_duplicates(subset=['SMILES'], keep='first')

    print(f"Total entries after deduplication: {len(df)}")

    # Sort by binding affinity (lower is better)
    df = df.sort_values('Binding_Affinity_kcal_mol')

    # Save to CSV
    output_file = base_dir / "SMILES_List_Master.csv"
    df.to_csv(output_file, index=False)

    print(f"\nMaster SMILES list saved to: {output_file}")
    print(f"\nFirst few rows:")
    print(df.head(10))
    print(f"\nSummary statistics:")
    print(df.describe())

if __name__ == "__main__":
    main()
