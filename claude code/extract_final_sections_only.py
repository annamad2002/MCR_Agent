#!/usr/bin/env python3
"""Extract ONLY from explicit 'Final Selection/Recommendation' sections in prompts 11-13."""

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
    'CC(C)=CCC(C)=CCC(C)O',  # Geraniol
    'C1=CC(=CC=C1C=CC)O',  # p-Coumaryl alcohol
    'NC(C(=O)O)CCS',  # Homocysteine
    'NC(C(=O)O)CS',  # Cysteine
}

print("Extracting ONLY from 'Final Selection/Recommendation' sections...\n")

compounds_dict = defaultdict(list)

for prompt_num in [11, 12, 13]:
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        continue

    chat_files = sorted([f for f in prompt_dir.iterdir()
                        if f.is_file() and not f.name.startswith('.') and 'docking' not in f.name])

    print(f"\n=== PROMPT {prompt_num} ===\n")

    for chat_file in chat_files:
        with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for explicit final section markers
        final_markers = [
            'Final selection:',
            'Final Selection:',
            'FINAL SELECTION:',
            '### Final',
            '## Final',
            '### Recommended',
            '## Recommended',
            '### Ranking Final',
            'Final recommendation',
        ]

        final_section_start = -1
        for marker in final_markers:
            if marker.lower() in content.lower():
                # Find the actual position (case-insensitive)
                pos = content.lower().find(marker.lower())
                if pos > final_section_start:
                    final_section_start = pos

        if final_section_start == -1:
            print(f"  {chat_file.name}: ❌ No final section found")
            continue

        # Extract from final section onwards
        final_section = content[final_section_start:]

        # Find tables in the final section
        lines = final_section.split('\n')

        in_table = False
        smiles_col = -1
        name_col = -1
        docking_col = -1
        residues_col = -1
        qed_col = -1
        np_col = -1
        sas_col = -1
        mw_col = -1
        logp_col = -1
        avail_col = -1

        compounds_in_file = 0

        for line in lines[:200]:  # Check first 200 lines of final section
            if not line.startswith('|'):
                continue

            cells = [c.strip() for c in line.split('|')[1:-1]]

            # Header row detection
            if '---' in line or any(keyword in ' '.join(cells).lower() for keyword in ['smiles', 'compound', 'docking']):
                in_table = True
                # Map columns
                cells_lower = [c.lower() for c in cells]
                smiles_col = next((i for i, c in enumerate(cells_lower) if 'smiles' in c), -1)
                name_col = next((i for i, c in enumerate(cells_lower) if 'compound' in c or 'name' in c), -1)
                docking_col = next((i for i, c in enumerate(cells_lower) if 'docking' in c or 'score' in c), -1)
                residues_col = next((i for i, c in enumerate(cells_lower) if 'residue' in c), -1)
                qed_col = next((i for i, c in enumerate(cells_lower) if 'qed' in c), -1)
                np_col = next((i for i, c in enumerate(cells_lower) if 'np' in c), -1)
                sas_col = next((i for i, c in enumerate(cells_lower) if 'sas' in c), -1)
                mw_col = next((i for i, c in enumerate(cells_lower) if 'mw' in c or 'weight' in c), -1)
                logp_col = next((i for i, c in enumerate(cells_lower) if 'logp' in c), -1)
                avail_col = next((i for i, c in enumerate(cells_lower) if 'availab' in c), -1)
                continue

            # Data rows
            if in_table and len(cells) >= 2:
                # Get SMILES (prioritize backtick format)
                smiles = None
                if smiles_col >= 0 and smiles_col < len(cells):
                    smiles_raw = cells[smiles_col].replace('`', '').replace('**', '').strip()
                    if len(smiles_raw) > 10 and any(c in smiles_raw for c in ['C', '=', '[']):
                        smiles = smiles_raw

                if not smiles:
                    continue

                # Skip known compounds
                if smiles in known_smiles:
                    continue

                # Extract other data
                name = ""
                if name_col >= 0 and name_col < len(cells):
                    name = cells[name_col].replace('`', '').replace('**', '').strip()

                docking = None
                if docking_col >= 0 and docking_col < len(cells):
                    try:
                        docking = float(cells[docking_col].replace('−', '-').replace('**', '').strip())
                    except:
                        pass

                residues = ""
                if residues_col >= 0 and residues_col < len(cells):
                    residues = cells[residues_col].strip()

                qed = ""
                if qed_col >= 0 and qed_col < len(cells):
                    qed = cells[qed_col].strip()

                np_score = ""
                if np_col >= 0 and np_col < len(cells):
                    np_score = cells[np_col].strip()

                sas_score = ""
                if sas_col >= 0 and sas_col < len(cells):
                    sas_score = cells[sas_col].strip()

                mw = ""
                if mw_col >= 0 and mw_col < len(cells):
                    mw = cells[mw_col].strip()

                logp = ""
                if logp_col >= 0 and logp_col < len(cells):
                    logp = cells[logp_col].strip()

                avail = ""
                if avail_col >= 0 and avail_col < len(cells):
                    avail = cells[avail_col].strip()

                # Store by SMILES (SMILES is the key)
                compounds_dict[smiles].append({
                    'Prompt': prompt_num,
                    'Name': name,
                    'Docking_Score': docking,
                    'Binding_Residues': residues,
                    'QED': qed,
                    'NP_Score': np_score,
                    'SAS_Score': sas_score,
                    'MW': mw,
                    'LogP': logp,
                    'Availability': avail,
                })
                compounds_in_file += 1

        if compounds_in_file > 0:
            print(f"  {chat_file.name}: ✓ {compounds_in_file} compounds from final section")
        else:
            print(f"  {chat_file.name}: ⚠ Final section found but no compounds extracted")

# Deduplicate and keep best data
final_compounds = []
for smiles, occurrences in compounds_dict.items():
    # Keep record with best docking score and most complete data
    best = max(occurrences, key=lambda x: (
        0 if x["Docking_Score"] is None else 1,  # Has docking score
        0 if x["Binding_Residues"] == "" else 1,  # Has residues
        0 if x["Docking_Score"] is None else -x["Docking_Score"]  # Best affinity
    ))
    best["SMILES"] = smiles
    best["Frequency"] = len(occurrences)
    final_compounds.append(best)

# Sort by docking score
final_compounds.sort(key=lambda x: (999 if x["Docking_Score"] is None else x["Docking_Score"]))

print(f"\n{'='*100}")
print(f"RESULTS: {len(final_compounds)} unique compounds from final sections only")
print(f"{'='*100}\n")

# Write CSV
output_csv = base_dir / "Final_Recommendations_11_13_SMILES_Primary.csv"
with open(output_csv, 'w') as f:
    header = "Rank,SMILES,Docking_Score,Binding_Residues,Frequency,Commercial_Availability,QED,NP_Score,SAS_Score,MW,LogP,Prompt\n"
    f.write(header)

    for rank, comp in enumerate(final_compounds, 1):
        residues = comp['Binding_Residues'].replace('"', '""')
        avail = comp['Availability'].replace('"', '""')
        f.write(f'{rank},"{comp["SMILES"]}",{comp["Docking_Score"] if comp["Docking_Score"] else ""},"{residues}",{comp["Frequency"]},"{avail}",{comp["QED"]},{comp["NP_Score"]},{comp["SAS_Score"]},{comp["MW"]},{comp["LogP"]},{comp["Prompt"]}\n')

print(f"✓ CSV saved: {output_csv}\n")

# Display results
print(f"{'Rank':<5} {'Affinity':<10} {'Freq':<5} {'SMILES (first 60 chars)':<65} {'Avail':<15}")
print(f"{'-'*100}")

for rank, comp in enumerate(final_compounds, 1):
    aff = f"{comp['Docking_Score']:.1f}" if comp['Docking_Score'] else "?"
    freq = comp['Frequency']
    smiles_short = comp['SMILES'][:60]
    avail = comp['Availability'][:13] if comp['Availability'] else "Unknown"
    print(f"{rank:<5} {aff:<10} {freq:<5} {smiles_short:<65} {avail:<15}")
