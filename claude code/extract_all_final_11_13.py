#!/usr/bin/env python3
"""Extract ALL final recommendations from prompts 11-13 chat log files."""

import re
from pathlib import Path
from collections import defaultdict

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

# Known compounds to exclude
known_smiles = {
    'C=CC[S@](=O)C[C@@H](C(=O)O)N',  # Alliin
    'C1=CC(=C(C=C1C[C@H](C(=O)O)OC(=O)/C=C/C2=CC(=C(C=C2)O)O)O)O',  # Rosmarinic Acid
    'C1=CC(=CC=C1/C=C/C(=O)O)O',  # p-coumaric acid
    'C1=CC=C(C(=C1)/C=C/C(=O)O)O',  # o-coumaric acid
    'C1=CC(=CC(=C1)O)/C=C/C(=O)O',  # m-coumaric acid
    'C(Br)(Br)Br',  # Bromoform
    'CC1=CCC(CC1)C(=C)C',  # Limonene
    'CC1=C[C@H]2C[C@@H](C1)C2(C)C',  # a-pinene
    'COC1=C(C=CC(=C1)CC=C)O',  # Eugenol
    'CC1=CC=C(C=C1)C(C)C',  # p-cymene
    'CC(=CCC/C(=C/C=O)/C)C',  # Citral
    'CC[C@H](C)C(=O)O[C@H]1C[C@H](C=C2[C@H]1[C@H]([C@H](C=C2)C)CC[C@@H]3C[C@H](CC(=O)O3)O)C',  # Lovastatin
    'CCCCCCCCCC(=O)O',  # Capric Acid
    # Additional natural compounds that are well-known
    'CC(C)=CCC(C)=CCC(C)O',  # Geraniol
    'C1=CC(=CC=C1C=CC)O',  # p-Coumaryl alcohol
    'NC(C(=O)O)CCS',  # Homocysteine
    'NC(C(=O)O)CS',  # Cysteine
}

print("Extracting ALL final recommendations from Prompts 11-13 chat files...\n")

compounds_dict = defaultdict(list)

# Process each prompt
for prompt_num in [11, 12, 13]:
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        print(f"Prompt {prompt_num}: Directory not found")
        continue

    chat_files = sorted([f for f in prompt_dir.iterdir()
                        if f.is_file() and not f.name.startswith('.') and 'docking' not in f.name])

    print(f"Processing Prompt {prompt_num}:")

    for chat_file in chat_files:
        try:
            with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for final recommendation/summary tables
            # Search for sections with headers like "Final", "Recommendation", "Summary"
            sections = []

            # Find all markdown tables
            table_pattern = r'\|[^\|]*\|[^\|]*\|[^\|]*\|'
            tables = re.finditer(table_pattern, content)

            last_pos = 0
            for table_match in tables:
                # Check if this table is in a final section
                preceding_text = content[max(0, table_match.start()-500):table_match.start()]

                if any(keyword in preceding_text.lower() for keyword in
                       ['final', 'recommendation', 'summary', 'best', 'selected', 'top candidate']):
                    sections.append((table_match.start(), table_match.end()))

            # Extract tables from final sections
            found_compounds = 0
            for section_start, _ in sections:
                # Get the table section (up to next section or end)
                table_end = min(content.find('\n\n', section_start) + 100, section_start + 3000)
                table_text = content[section_start:table_end]

                # Extract table rows
                rows = table_text.split('\n')

                for row in rows:
                    if not row.startswith('|') or '---' in row:
                        continue

                    cells = [c.strip() for c in row.split('|')[1:-1]]
                    if len(cells) < 2:
                        continue

                    # Try to find SMILES in the row
                    smiles = None
                    name = ""
                    docking = None
                    residues = ""
                    qed = ""
                    np_score = ""
                    sas_score = ""
                    mw = ""
                    logp = ""
                    avail = ""

                    for i, cell in enumerate(cells):
                        cell_clean = cell.replace('`', '').replace('**', '').strip()

                        # Detect SMILES (rough heuristic)
                        if any(c in cell_clean for c in ['C1', 'c1', '[C@', '[C@@', 'C(', 'CC', 'O=']) and len(cell_clean) > 10:
                            if 'C' in cell_clean and any(c in cell_clean for c in ['=', '[', '(', '/']):
                                smiles = cell_clean

                        # Detect docking score (starts with - or −)
                        elif any(s in cell_clean for s in ['-', '−']) and any(c.isdigit() for c in cell_clean):
                            try:
                                docking = float(cell_clean.replace('−', '-').replace('**', ''))
                            except:
                                pass

                        # Other properties
                        if 'residue' in cells[0].lower() if i == 0 else 'residue' in row.lower():
                            residues = cell_clean
                        if 'QED' in cells[0] if i == 0 else False:
                            qed = cell_clean
                        if 'NP' in cells[0] if i == 0 else False:
                            np_score = cell_clean
                        if 'SAS' in cells[0] if i == 0 else False:
                            sas_score = cell_clean
                        if 'MW' in cells[0] if i == 0 else False:
                            mw = cell_clean
                        if 'LogP' in cells[0] if i == 0 else False:
                            logp = cell_clean

                    # If we found a SMILES, store it
                    if smiles and len(smiles) > 10:
                        if smiles not in known_smiles:
                            compounds_dict[smiles].append({
                                'Prompt': prompt_num,
                                'Docking_Score': docking,
                                'Binding_Residues': residues,
                                'QED': qed,
                                'NP_Score': np_score,
                                'SAS_Score': sas_score,
                                'MW': mw,
                                'LogP': logp,
                                'Availability': avail,
                            })
                            found_compounds += 1

            if found_compounds > 0:
                print(f"  ✓ {chat_file.name}: {found_compounds} compounds")
            else:
                print(f"  - {chat_file.name}: no compounds found")

        except Exception as e:
            print(f"  ✗ {chat_file.name}: {str(e)[:50]}")

print(f"\n{'='*80}")
print(f"Total unique compounds found: {len(compounds_dict)}")
print(f"{'='*80}\n")

# If we found no compounds with the table method, try a simpler text search
if len(compounds_dict) == 0:
    print("Retrying with direct text search...\n")

    for prompt_num in [11, 12, 13]:
        prompt_dir = base_dir / str(prompt_num)
        chat_files = sorted([f for f in prompt_dir.iterdir()
                            if f.is_file() and not f.name.startswith('.') and 'docking' not in f.name])

        for chat_file in chat_files:
            with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Find all SMILES-like strings
            smiles_pattern = r'[A-Z0-9\[\]\@\#=\-\\/\(\)C]+(?:[a-z0-9\[\]\@\#=\-\\/\(\)C]*[A-Z0-9\[\]\@\#=\-\\/\(\)C])'

            # Look for SMILES in code blocks or backticks
            backtick_pattern = r'`([^`]+)`'
            matches = re.finditer(backtick_pattern, content)

            for match in matches:
                potential_smiles = match.group(1).strip()
                if len(potential_smiles) > 10 and any(c in potential_smiles for c in ['C', '=', '[']):
                    # Try to extract docking score nearby
                    pos = match.start()
                    context = content[max(0, pos-200):min(len(content), pos+200)]

                    docking = None
                    docking_search = re.search(r'[-−](\d+\.?\d*)', context)
                    if docking_search:
                        try:
                            docking = float(docking_search.group(0).replace('−', '-'))
                        except:
                            pass

                    if potential_smiles not in known_smiles:
                        compounds_dict[potential_smiles].append({
                            'Prompt': prompt_num,
                            'Docking_Score': docking,
                            'Binding_Residues': '',
                            'QED': '',
                            'NP_Score': '',
                            'SAS_Score': '',
                            'MW': '',
                            'LogP': '',
                            'Availability': '',
                        })

print(f"Found {len(compounds_dict)} unique compounds after retry")

# Build final list
final_compounds = []
for smiles, occurrences in compounds_dict.items():
    # Keep best docking score
    best = max(occurrences, key=lambda x: -999 if x["Docking_Score"] is None else -x["Docking_Score"])
    best["SMILES"] = smiles
    best["Frequency"] = len(occurrences)
    final_compounds.append(best)

# Sort by docking score
final_compounds.sort(key=lambda x: (999 if x["Docking_Score"] is None else x["Docking_Score"]))

# Write CSV
output_csv = base_dir / "Prompts_11_13_All_Final_Recommendations.csv"
with open(output_csv, 'w') as f:
    header = "Rank,SMILES,Docking_Score,Binding_Residues,Frequency,Commercial_Availability,QED,NP_Score,SAS_Score,MW,LogP,Prompt\n"
    f.write(header)

    for rank, comp in enumerate(final_compounds, 1):
        residues = comp['Binding_Residues'].replace('"', '""')
        avail = comp['Availability'].replace('"', '""')
        f.write(f'{rank},"{comp["SMILES"]}",{comp["Docking_Score"] if comp["Docking_Score"] else ""},"{residues}",{comp["Frequency"]},"{avail}",{comp["QED"]},{comp["NP_Score"]},{comp["SAS_Score"]},{comp["MW"]},{comp["LogP"]},{comp["Prompt"]}\n')

print(f"\n✓ CSV saved: {output_csv}")
print(f"✓ Total unique compounds: {len(final_compounds)}")
