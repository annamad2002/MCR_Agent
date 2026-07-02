#!/usr/bin/env python3
"""Simple extraction of final recommendations."""

import re
from pathlib import Path

base_dir = Path("/Users/annalevison/Library/CloudStorage/OneDrive-UniversityofReading/chem/ollama_prompts/Prompts/MCR_Agent")

final_smiles = {}  # smiles -> {prompt, model, compound}

for prompt_num in range(1, 14):
    prompt_dir = base_dir / str(prompt_num)
    if not prompt_dir.exists():
        continue

    chat_files = sorted([f for f in prompt_dir.iterdir() if f.is_file() and not f.name.startswith('.')])

    for chat_file in chat_files:
        if "docking" in chat_file.name:
            continue

        try:
            with open(chat_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Find "Final selection:" section
            final_idx = content.rfind("Final selection:")
            if final_idx == -1:
                continue

            final_section = content[final_idx:final_idx+5000]

            # Find table section (lines starting with |)
            lines = final_section.split('\n')
            in_table = False
            compound_col_idx = None
            smiles_col_idx = None

            for line in lines:
                if "| Compound |" in line or "| :--- |" in line:
                    in_table = True
                    # Find column indices
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    compound_col_idx = 0  # Usually first
                    smiles_col_idx = 1    # Usually second
                    continue

                if in_table and line.startswith('|'):
                    cells = [c.strip() for c in line.split('|')[1:-1]]

                    if len(cells) >= 2:
                        compound_name = cells[0].replace('**', '').replace('`', '').strip()
                        smiles = cells[1].replace('`', '').strip()

                        # Validate SMILES
                        if len(smiles) > 5 and any(c in smiles for c in ['C', 'N', 'O', 'S']):
                            model = chat_file.name.split(' - ')[1] if ' - ' in chat_file.name else chat_file.name
                            final_smiles[smiles] = {
                                'prompt': prompt_num,
                                'model': model,
                                'compound': compound_name
                            }
                            print(f"✓ P{prompt_num} {model:20} | {compound_name:40} | {smiles[:45]}")

        except Exception as e:
            print(f"✗ Error in {prompt_num}/{chat_file.name}: {str(e)[:50]}")

print(f"\n{'='*100}")
print(f"TOTAL UNIQUE FINAL RECOMMENDATIONS: {len(final_smiles)}")
print(f"{'='*100}")

# List them
for i, (smiles, info) in enumerate(sorted(final_smiles.items()), 1):
    print(f"{i:3}. P{info['prompt']} | {smiles}")
