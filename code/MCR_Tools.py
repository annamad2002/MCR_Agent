from rdkit import RDLogger
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdFMCS
from rdkit.Chem.Lipinski import RotatableBondSmarts
from rdkit.Chem import AllChem, Draw, QED
from rdkit.Chem import RDConfig
from pdbfixer import PDBFixer
from openmm import *
from openmm.app import *
from openmm.unit import *
import sys, os
import random
from datetime import datetime
import subprocess
import zipfile
import nglview as nv
import MDAnalysis as mda
import prolif as plf
from MDAnalysis.analysis import distances
import pandas as pd
import numpy as np
import oddt
import re
import pubchempy as pcp
sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
sys.path.append(os.path.join(RDConfig.RDContribDir, 'NP_Score'))
import sascorer, npscorer
from oddt.interactions import (hbonds, hydrophobic_contacts, pi_stacking, 
                                pi_cation, halogenbonds, salt_bridges)

def quick_run(SMILES: str, mol_id: int = 0):

  '''
    Accepts SMILES string for molecule, and binds to Methyl-coezyme M reductase binding site. Returns ligand docking score.
    args:
      SMILES: SMILES string for the molecule.
    returns:
      score: ligand docking score.
  '''
  try:
    pH = 7.0
    FFtype = "MMFF94"

    if FFtype == "MMFF94":
        charge_method = 'mmff94'
    else:
        charge_method = 'gasteiger'

    print("Optimizing the ligand structure...", end='')
    if SMILES == "":
        ligandfile = files.upload()
        ligandfile_name = next(iter(ligandfile))
        subprocess.run(f'obabel {ligandfile_name} -O ligand.sdf -p{pH} --ff {FFtype} --partialcharge {charge_method} --best --minimize --steps 100000 --sd', shell=True)
    else:
        subprocess.run(f'obabel -:"{SMILES}" -O ligand.sdf -p{pH} --gen3d --ff {FFtype} --partialcharge {charge_method} --best --minimize --steps 150000 --sd', shell=True)

    mol = Chem.rdmolfiles.SDMolSupplier("ligand.sdf")[0]
    Chem.rdmolops.SanitizeMol(mol)


    n_rot_bonds = Chem.rdMolDescriptors.CalcNumRotatableBonds(mol)
    n_amide_bonds = Chem.rdMolDescriptors.CalcNumAmideBonds(mol)

    select_fix = ''


    rot_atom_pairs = mol.GetSubstructMatches(RotatableBondSmarts)
    rot_bonds = list(set([mol.GetBondBetweenAtoms(*ap).GetIdx() for ap in rot_atom_pairs]))

    Chem.rdDepictor.Compute2DCoords(mol)


    def update_rotatable_bond(change):
        new_input = change.new
        if new_input.endswith(','):
            return
        if new_input == '':
            fix_bonds_idx = []
        else:
            fix_bonds_idx = [int(s) for s in new_input.split(',')]
        bond_colors = recolor_bonds(fix_bonds_idx)
        d.ClearDrawing()
        Chem.Draw.rdMolDraw2D.PrepareAndDrawMolecule(d, mol, legend='Rotable in red, Fixed in blue',
                                                    highlightBonds=rot_bonds, highlightBondColors=bond_colors)
        rot_bond_count = 0
        for bond in rot_bonds:
            if bond not in fix_bonds_idx:
                rot_bond_count += 1

    SMILES = Chem.rdmolfiles.MolToSmiles(mol)
    rotable = ""

    if select_fix == '':
        fix_bonds_idx = []
    else:
        fix_bonds_idx = [int(s) for s in select_fix.split(',')]

    for i in fix_bonds_idx:
        bond = mol.GetBondWithIdx(i)
        a1 = bond.GetBeginAtom().GetIdx()+1 # RDKit은 0부터 셈
        a2 = bond.GetEndAtom().GetIdx()+1
        rotable = rotable + ' -r "'+SMILES+'" -b '+str(a1)+" "+str(a2)

    subprocess.run(f'mk_prepare_ligand.py -i ligand.sdf -o ligand.pdbqt{rotable}', shell=True)

    if os.path.exists('ligand.pdbqt'):
        print('ligand PDBQT file has been generated.')
    else:
        print('Failed to generate ligand PDBQT file.')

    flexFlag = False
    blind_docking = False

    center_x = "0.53"
    center_y = "-0.044"
    center_z = "-26.454"
    len_x = "28"
    len_y = "28"
    len_z = "28"

    number_reps = 1

    best_scores = []
    for run_number in range(1,number_reps+1,1):

        output = f"ligand{mol_id}_out_{run_number}.pdbqt"

        exhaustiveness = 32


        if flexFlag:
            rigid = "receptor = MCR_Agent/data/receptor.pdbqt\n"
            flex_rec = "flex = MCR_Agent/data/receptor_flex.pdbqt\n"
        else:
            rigid = "receptor = MCR_Agent/data/receptor.pdbqt\n"
            flex_rec = ""

        with open('config', 'w') as f:
            f.write(rigid)
            f.write("ligand = ligand.pdbqt\n")
            f.write("center_x = "+str(center_x)+'\n')
            f.write("center_y = "+str(center_y)+'\n')
            f.write("center_z = "+str(center_z)+'\n')
            f.write("size_x = "+str(len_x)+'\n')
            f.write("size_y = "+str(len_y)+'\n')
            f.write("size_z = "+str(len_z)+'\n')
            f.write("num_modes = 10\n")
            f.write("out = "+output+'\n')
            f.write(f"log = docking_log{mol_id}_{run_number}.txt\n")
            f.write("exhaustiveness = "+str(exhaustiveness)+'\n')
            f.write(flex_rec)

        if blind_docking:
            p = subprocess.Popen('/content/qvina/bin/qvina-w --config config', shell=True, bufsize=0, stdout=subprocess.PIPE, encoding='utf-8')
        else:
            p = subprocess.Popen('/content/qvina/bin/qvina2.1 --config config', shell=True, bufsize=0, stdout=subprocess.PIPE, encoding='utf-8')

        while p.poll() == None:
            out = p.stdout.read(1)
            print(out, end='')

        docking_file = f"docking_log{mol_id}_{run_number}.txt"
        df = open(docking_file, 'r')
        lines = df.readlines()
        df.close()

        for line in lines:
          parts = line.split()
          if len(parts) >1:
            if parts[0] == "1":
              best_scores.append(parts[1])

        for score in best_scores:
          print(score)

    zip_path = 'docking_results.zip'
    mode = 'a' if os.path.exists(zip_path) else 'w'
    with zipfile.ZipFile(zip_path, mode) as zf:
      if os.path.exists(docking_file):
          zf.write(docking_file)
      if os.path.exists(output):
          zf.write(output)
    score = best_scores[0]
    return score, output

  except Exception as e:
        fail_msg = f"Molecule {mol_id} ({SMILES}) FAILED: {e}"
        print(fail_msg)
        with open('failed_molecules.txt', 'a') as f:
            f.write(fail_msg + '\n')
        return None

def pubchem(smile, n_results: int = 50):

  '''
    Searches PubChem for compounds similar to novel compound.
    args:
      n_results: number of similar compounds to retrieve.
      smile: SMILES string for the molecule.
    returns:
      out_string: SMILES strings of the similar compounds.
  '''

  novel_compound = smile
  novel_mol = Chem.MolFromSmiles(novel_compound)

  results = pcp.get_compounds(identifier=str(novel_compound), namespace="smiles", searchtype="similarity",listkey_count=n_results)
  sub_smiles = []
  for compound in results:
    sub_smiles.append(compound.smiles)

  out_string = '\n'.join(sub_smiles)

  return out_string

def lipinski(smiles_list: list[str] = ['c1ccccc1']):
  '''
    A tool to calculate QED and other lipinski properties of a molecule.

      Args:
        smiles_list: the input smiles strings

      Returns:
        total_lipinski_string: a string of the QED and other lipinski properties of the molecules,
                      including Molecular Weight, LogP, HBA, HBD, Polar Surface Area,
                      Rotatable Bonds, Aromatic Rings and Undesireable Moieties.
  '''
  print("lipinski tool")
  print('===================================================')

  total_lipinski_string = ''

  for smiles in smiles_list:
    for ion in ['.[Na+]', '.[K+]', '.[Cl-]', '.[Br-]', '[Na+].', '[K+].', '[Cl-].', '[Br-].']:
        smiles = smiles.replace(ion, '')
    lipinski_list = []
    try:
        mol = Chem.MolFromSmiles(smiles)
        qed = Chem.QED.default(mol)

        p = Chem.QED.properties(mol)
        mw = p[0]
        logP = p[1]
        hba = p[2]
        hbd = p[3]
        psa = p[4]
        rb = p[5]
        ar = p[6]
        um = p[7]

        lipinski_list.append(qed)
        lipinski_list.append(mw)
        lipinski_list.append(logP)
        lipinski_list.append(hba)
        lipinski_list.append(hbd)
        lipinski_list.append(psa)
        lipinski_list.append(rb)
        lipinski_list.append(ar)
        lipinski_list.append(um)

        total_lipinski_string += f"Properties of SMILES: {smiles}: QED: {qed:.3f}\n"
        total_lipinski_string += f"Molecular Weight: {mw:.3f}, LogP: {logP:.3f}\n"
        total_lipinski_string += f"Hydrogen bond acceptors: {hba}, Hydrogen bond donors: {hbd}\n" 
        total_lipinski_string += f"Polar Surface Area: {psa:.3f}, Rotatable Bonds: {rb}\n" 
        total_lipinski_string += f"Aromatic Rings: {ar}, Undesireable moieties: {um}\n"
        total_lipinski_string += "===================================================\n"    
    except:
        total_lipinski_string += f"SMILES: {smiles}, Could not get properties\n"
  
  return total_lipinski_string

def calculate_SAS_and_NP(smiles_list: list[str]):
  '''Calculate SAS and NP scores for a list of SMILES strings. SAS score is a measure
  of synthetic accessibility, and a value of 1 indicates that the molecule is easy to synthesize,
  while a value of 10 indicates that it is difficult to synthesize.
  NP score is a measure of natural product-likeness, and a higher score indicates that the
  molecule is more similar to natural products; the score runs from -5 to 5, with higher scores
  indicating greater similarity to natural products.

  Args:
      smiles_list (list[str]): A list of SMILES strings representing the molecules to be scored.

  Returns:
      list[tuple[float, float]]: A list of tuples containing the SAS and NP scores for each molecule.
  '''
  fscore = npscorer.readNPModel()

  out_string = '| SMILES | SAS Score | NP Score |\n'
  out_string += '|---------|-----------|----------|\n'
  for smiles in smiles_list:
      mol = Chem.MolFromSmiles(smiles)
      if mol is not None:
          sas_score = sascorer.calculateScore(mol)
          np_score = npscorer.scoreMol(mol, fscore)
          out_string += f'| {smiles} | {sas_score:.2f} | {np_score:.2f} |\n'
      else:
          out_string += f'| {smiles} | {"Invalid SMILES"} | {"Invalid SMILES"} |\n'
  return out_string

def dock_and_get_interacting_residues(smiles: str):
  '''
    docks a molecule to the target and returns the interacting residues. If the docking fails, returns an empty list.

    Args:
        smiles (str): the SMILES string of the molecule to dock and get interacting residues for
    Returns:
        output_string (str): a string containing the interacting residues and types of interactions.
  '''

  score, output = quick_run(smiles)

  if output is None:
    return "Docking failed. No interacting residues found."

  replace_string = f"obabel -ipdbqt {output} -osdf -O {output.replace('pdbqt','sdf')}"
  subprocess.run(replace_string, shell=True)
  ligand_file = output.replace('pdbqt', 'sdf')
  protein_file = 'MCR_Agent/data/receptor.pdb'

  pro = next(oddt.toolkit.readfile('pdb',protein_file))
  lig = next(oddt.toolkit.readfile('sdf',ligand_file))
  pro.protein = True

  contacts_results = find_contacts(pro, lig)

  return contacts_results

def find_contacts(pro, lig):

  int_types = ['hbonds', 'hydrophobic_contacts', 'pi_stacking', 'pi_cation', 'halogenbonds', 'salt_bridges']
  int_functions = [hbonds, hydrophobic_contacts, pi_stacking, pi_cation, halogenbonds, salt_bridges]

  output_string = '## Contacts between the ligand and proteins residues -------------------------'
  interacting_residues = []

  for int_type, int_function in zip(int_types, int_functions):
    output_string += f'\n\n{int_type.upper()} interactions:\n'
    if int_type == 'pi_stacking':
      pro_atoms, lig_atoms, strict_parallel, strict_perpendicular = int_function(pro, lig)
    elif int_type == 'salt_bridges' or int_type == 'hydrophobic_contacts':
      pro_atoms, lig_atoms = int_function(pro, lig)
    elif int_type == 'halogenbonds' or int_type == 'pi_cation':
      pro_atoms, lig_atoms, strict = int_function(pro, lig, tolerance=30)
    else:
      pro_atoms, lig_atoms, strict = int_function(pro, lig)

    if int_type not in ['pi_stacking']:
      assert len(pro_atoms) == len(lig_atoms)
      atoms = []
      residues = []
      for atom, res in zip(lig_atoms, pro_atoms):
        atom_name = str(atom['atomtype']).split('.')[0]
        atom_number = str(atom['id'])
        res_name = str(res['resname'])
        res_number = str(res['resnum'])
        res_id = res_name+res_number
        output_string += f'Atom {atom_name}-{atom_number} forms a {int_type} with {res_id}\n'
        atoms.append(atom_number)
        residues.append(res_id)

      atoms = list(set(atoms))
      residues = list(set(residues))
      interacting_residues.append(residues)

    if int_type == 'pi_stacking':
      residues = []
      for res in pro_atoms:
        res_name = str(res['resname'])
        res_number = str(res['resnum'])
        res_id = res_name+res_number
        output_string += f'{res_id} forms pi-stacking interactions with the Ligand\n'
        residues.append(res_id)
        para = strict_parallel.sum()
        perp = strict_perpendicular.sum()

      residues = list(set(residues))
      interacting_residues.append(residues)

      try:
        output_string += f'The total number of parallel interactions are {para}\n'
        output_string += f'The total number of perpendicular interactions are {perp}\n'
      except:
        pass

  interacting_residues = [item for sublist in interacting_residues for item in sublist]
  interacting_residues = list(set(interacting_residues))
  interacting_residues.sort()

  output_string += f"List of all interacting residues:\n {', '.join(interacting_residues)}"

  return output_string

