#!/usr/bin/env python3
"""Extract from 'Final selection:' bullet lists in prompts 11-13 files."""

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
    'C/C=C/C1=CC(=C(C=C1)O)OC',  # Isoeugenol
}

print("Extracting from 'Final selection:' sections (SMILES primary)...\n")

compounds_dict = defaultdict(list)

for prompt_num in [11, 12, 13]:
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        continue

    chat_files = sorted([f for f in prompt_dir.iterdir()
                        if f.is_file() and not f.name.startswith('.') and 'docking' not in f.name])

    print(f"=== PROMPT {prompt_num} ===\n")

    for chat_file in chat_files:
        with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for "Final selection:" section
        if 'Final selection:' not in content:
            print(f"  {chat_file.name}: ❌ No 'Final selection:' section")
            continue

        # Extract text after "Final selection:"
        idx = content.rfind('Final selection:')  # Use rfind to get the LAST occurrence
        final_section = content[idx:idx+5000]

        # Extract SMILES in backticks with their context
        smiles_pattern = r'`([^`]+)`'
        matches = list(re.finditer(smiles_pattern, final_section[:2000]))  # Look in first 2000 chars

        if not matches:
            print(f"  {chat_file.name}: ⚠ Final section found but no SMILES in backticks")
            continue

        compounds_in_file = 0
        for match in matches:
            smiles = match.group(1).strip()

            # Validate SMILES
            if len(smiles) < 5 or not any(c in smiles for c in ['C', '=']):
                continue

            # Skip known compounds
            if smiles in known_smiles:
                continue

            # Get context around SMILES for metadata
            smiles_pos = match.start()
            context_before = final_section[max(0, smiles_pos-500):smiles_pos]
            context_after = final_section[smiles_pos:min(len(final_section), smiles_pos+500)]
            full_context = context_before + context_after

            # Extract docking score (look for pattern like "-7.4" or "Docking: -7.5")
            docking = None
            docking_match = re.search(r'[Dd]ocking:?\s*([-−][\d.]+)', full_context)
            if docking_match:
                try:
                    docking = float(docking_match.group(1).replace('−', '-'))
                except:
                    pass

            # Extract residues
            residues = ""
            residues_match = re.search(r'[Rr]esidues?:?\s*([^,\n.]+)', full_context)
            if residues_match:
                residues = residues_match.group(1).strip()[:100]

            # Extract other properties from context
            qed = ""
            qed_match = re.search(r'QED:?\s*([\d.]+)', full_context)
            if qed_match:
                qed = qed_match.group(1)

            np_score = ""
            np_match = re.search(r'NP:?\s*([\d.]+)', full_context)
            if np_match:
                np_score = np_match.group(1)

            sas_score = ""
            sas_match = re.search(r'SAS:?\s*([\d.]+)', full_context)
            if sas_match:
                sas_score = sas_match.group(1)

            mw = ""
            mw_match = re.search(r'MW:?\s*([\d.]+)', full_context)
            if mw_match:
                mw = mw_match.group(1)

            logp = ""
            logp_match = re.search(r'LogP:?\s*([-\d.]+)', full_context)
            if logp_match:
                logp = logp_match.group(1)

            # Check for commercial availability
            avail = ""
            if 'Commercially Available: Yes' in full_context or 'commercially available' in full_context.lower():
                avail = "Yes"
            elif 'Commercially Available: No' in full_context:
                avail = "No"

            # Store compound - SMILES is the key
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
            compounds_in_file += 1

        if compounds_in_file > 0:
            print(f"  {chat_file.name}: ✓ {compounds_in_file} compounds from final selection")
        else:
            print(f"  {chat_file.name}: ⚠ No valid SMILES extracted")

# Deduplicate and keep best data
final_compounds = []
for smiles, occurrences in compounds_dict.items():
    # Keep record with best docking score
    best = max(occurrences, key=lambda x: (
        0 if x["Docking_Score"] is None else 1,
        0 if x["Docking_Score"] is None else -x["Docking_Score"]
    ))
    best["SMILES"] = smiles
    best["Frequency"] = len(occurrences)
    final_compounds.append(best)

# Sort by docking score (best first)
final_compounds.sort(key=lambda x: (999 if x["Docking_Score"] is None else x["Docking_Score"]))

print(f"\n{'='*120}")
print(f"EXTRACTED: {len(final_compounds)} unique compounds from 'Final selection:' sections")
print(f"{'='*120}\n")

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
print(f"{'Rank':<5} {'Affinity':<10} {'Freq':<5} {'SMILES (first 65 chars)':<70} {'Residues':<20}")
print(f"{'-'*120}")

for rank, comp in enumerate(final_compounds, 1):
    aff = f"{comp['Docking_Score']:.1f}" if comp['Docking_Score'] else "?"
    freq = comp['Frequency']
    smiles_short = comp['SMILES'][:65]
    residues_short = comp['Binding_Residues'][:18] if comp['Binding_Residues'] else "-"
    print(f"{rank:<5} {aff:<10} {freq:<5} {smiles_short:<70} {residues_short:<20}")
