#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import MDAnalysis as mda
import pymol
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
from padelpy import padeldescriptor
import joblib
import csv
from rdkit.Chem import AllChem, SDWriter, SDMolSupplier
from pymol import cmd,stored
from vina import Vina
import os
import subprocess


# constants
docking_protein = "7te7_prepared.pdbqt"
prediction_model = "padel_model.joblib"
current_directory = os.getcwd()
file_paths = ["ligand_clean.sdf", "ligand.pdbqt"]


def delete_files_with_extension(directory, extensions):
    """
    Delete files with specified extensions in a directory.
    """
    for file in os.listdir(directory):
        if any(file.endswith(ext) for ext in extensions):
            os.remove(os.path.join(directory, file))

# Delete files in the working directory
current_directory = os.getcwd()
#delete_files_with_extension(current_directory, [".sdf", ".pdbqt"])
delete_files_with_extension(current_directory, [".sdf",".pdbqt"])


def prepare_ligand(input_sdf: str, output_pdbqt: str):
    # Read the input molecule
    mol = Chem.MolFromMolFile(input_sdf)
    if mol is None:
        raise ValueError(f"Invalid SDF file: {input_sdf}")
    
    # Generate 3D coordinates
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.UFFOptimizeMolecule(mol)

    # Save as pdbqt
    with open(output_pdbqt, 'w') as pdbqt_file:
        pdbqt_file.write(Chem.MolToPDBBlock(mol))

def calculate_lipinski_descriptors(smiles):
    """
    Calculate Lipinski descriptors: A set of molecular properties used to assess 
    the drug-likeness or pharmacokinetic profile of a chemical compound.

    Parameters
    ----------
    smiles : str
        An RDKit valid canonical SMILES or chemical structure of a compound.

    Returns
    -------
    str
        A formatted string of Lipinski descriptors.

    Raises
    ------
    ValueError
        If the input SMILES string is invalid.

    Example
    -------
    >>> calculate_lipinski_descriptors("Oc1ccc2c(c1)S[C@H](c1ccco1)[C@H](c1ccc(OCCN3CCCCC3)cc1)O2")
    'Molecular Weight: 385.50\\nLogP: 4.12\\nNumber of Hydrogen Bond Donors: 2\\n...'
    """

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        raise ValueError("Invalid SMILES string. Please provide a valid SMILES notation.")

    descriptors = {
        "Molecular Weight": Descriptors.MolWt(mol),
        "LogP": Descriptors.MolLogP(mol),
        "Num H Donors": Descriptors.NumHDonors(mol),
        "Num H Acceptors": Descriptors.NumHAcceptors(mol),
        "Num Rotatable Bonds": Descriptors.NumRotatableBonds(mol),
        "Carbon Count": sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 6),  # Carbon atomic number = 6
        "Oxygen Count": sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 8),  # Oxygen atomic number = 8
    }

    aliases = {
        "Molecular Weight": "Molecular Weight",
        "LogP": "LogP",
        "Num H Donors": "Number of Hydrogen Bond Donors",
        "Num H Acceptors": "Number of Hydrogen Bond Acceptors",
        "Num Rotatable Bonds": "Number of Rotatable Bonds",
        "Carbon Count": "Carbon Count",
        "Oxygen Count": "Oxygen Count",
    }

    formatted_descriptors = ""
    for key, value in descriptors.items():
        formatted_descriptors += f"{aliases[key]}: {value}\n"

    return formatted_descriptors




def predict_pIC50(smiles):
    """Prediction model is based on RandomForest regression constructed using a collection of all known cannonical SMILES that interact with Oestrogen Receptor alpha protein stored in the ChEMBL database.

    Params
    ------
    smiles: string: An rdkit valid canonical SMILES or chemical structure a compound.

    Usage
    -----
    from MLDockKit import predict_pIC50

    predict_pIC50("Oc1ccc2c(c1)S[C@H](c1ccco1)[C@H](c1ccc(OCCN3CCCCC3)cc1)O2")
    """
    # Get the directory of the currently executing script

    script_dir = os.path.dirname(__file__)

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("You entered an invalid SMILES string")

    # Convert SMILES to molecule object
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)

    # Write the molecule to an SDF file
    sdf_file = os.path.join(script_dir, "molecule.smi")
    data = [[smiles + "\t" + "Compound_name"]]
    with open(sdf_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

    # Process the fingerprints
    padeldescriptor(
        mol_dir=sdf_file,
        d_file=os.path.join(script_dir, "descriptors.csv"),
        detectaromaticity=True,
        standardizenitro=True,
        standardizetautomers=True,
        removesalt=True,
        fingerprints=True,
    )
    data = pd.read_csv(os.path.join(script_dir, "descriptors.csv"))
    X = data.drop(columns=["Name"])

    # Specify the path to the "padel_model.joblib" file
    prediction_model = os.path.join(script_dir, "padel_model.joblib")
    loaded_model = joblib.load(prediction_model)
    y_pred = loaded_model.predict(X)
    predicted_value = y_pred[0]
    predicted_value = format(predicted_value, ".2f")
    return f"Predicted pIC50: {predicted_value}"

def prot_lig_docking(smiles):
    """
    Docking procedure is performed by Autodock Vina on the Oestrogen Receptor alpha protein, pdb_id: 5gs4.
    
    Params
    ------
    smiles: string, an rdkit valid canonical SMILES or chemical structure a compound.
    
    Returns
    ------
    str: Docking score or an error message.
    """
    # Get the directory of the currently executing script
    script_dir = os.path.dirname(__file__)
    current_directory = os.getcwd()

    # Convert SMILES to a molecule
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "Error: Invalid SMILES string"

    # Add hydrogens and generate 3D coordinates
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)

    # Save the ligand to an SDF file
    sdf_file = os.path.join(current_directory, "ligand_initial.sdf")
    writer = SDWriter(sdf_file)
    writer.write(mol)
    writer.close()

    # Prepare ligand using meeko
    ligand_pdbqt = os.path.join(current_directory, "ligand_prepared.pdbqt")
    subprocess.run([
        "obabel", sdf_file, 
        "-O", ligand_pdbqt, 
        "--gen3D", 
        "--addhydrogens", 
        "--partialcharge", 
        "--ff", "mmff94"
        ], check=True)

    # Load the docking protein
    docking_protein = os.path.join(script_dir, "7te7_prepared.pdbqt")
    original_protein = os.path.join(script_dir, "7te7_original.pdb")
    original_structure = mda.Universe(original_protein)
    ligand_mda = original_structure.select_atoms("resname I0V")

    # Get the center of the ligand as the "pocket center"
    pocket_center = ligand_mda.center_of_geometry()
    ligand_box = ligand_mda.positions.max(axis=0) - ligand_mda.positions.min(axis=0) + 5

    ## convert ligand_box to list
    pocket_center = pocket_center.tolist()
    ligand_box = ligand_box.tolist() 

    # Initialize Vina
    v = Vina(sf_name="vina")
    v.set_receptor(docking_protein)
    v.set_ligand_from_file(ligand_pdbqt)
    v.compute_vina_maps(center=pocket_center, box_size=ligand_box)

    # Perform docking
    v.dock(exhaustiveness=10, n_poses=10)

    # Save docking results
    vina_out_file = os.path.join(current_directory, "ligand_docked.pdbqt")
    sdf_file = os.path.join(current_directory, "ligand_docked.sdf")
    v.write_poses(vina_out_file, n_poses=10, overwrite=True)

    # Process docking results
    try:
        docking_score = v.score()  # Extract docking score
        return f"Docking score: {docking_score[0]:.3f} kcal/mol"
    except Exception as e:
        return f"Error during docking: {str(e)}"


def visualize_dock_results(
    presentation='cartoon',
    label_residues=True,
    show_iAA=True,
    viewport_size=(1200, 900)
):
    """Visualizes a docking result in PyMOL, keeping only interacting residues.

    Parameters:
    - presentation (str): How to display the receptor (default: 'cartoon').
    - label_residues (bool): Option to label residues (default: True).
    - show_iAA (bool): Option to show interacting amino acids only (default: True).
    - viewport_size (tuple): Size of the PyMOL viewport (default: (1200, 900)).
    """

    script_dir = os.path.dirname(__file__)
    current_directory = os.getcwd()
    receptor_file = os.path.join(script_dir, "7te7_H_no_HOHandI0V.pdb")
    ligand_file = os.path.join(current_directory, "ligand_docked.pdbqt")


    # Ensure required files are available
    if not os.path.exists(receptor_file) or not os.path.exists(ligand_file):
        raise ValueError("Both receptor_file and ligand_file must exist.")

    pymol.finish_launching()

    # Load receptor and ligand
    pymol.cmd.load(receptor_file, "receptor")
    pymol.cmd.load(ligand_file, "ligand")

    # Remove water molecules
    pymol.cmd.remove("resn HOH")

    # Show ligand
    pymol.cmd.show("sticks", "ligand")
    pymol.cmd.color("magenta", "ligand")
    pymol.cmd.set("stick_radius", 0.3, "ligand")


    # Select interacting residues (within 5Å of the ligand)
    pymol.cmd.select("interacting_residues", "byres receptor within 5 of ligand")
    pymol.cmd.show("sticks", "interacting_residues")
    pymol.cmd.color("red", "interacting_residues")  # Highlight interacting residues


    if show_iAA:
        # Hide everything except interacting residues and ligand
        pymol.cmd.hide("everything")
        
        # Show only interacting residues
        pymol.cmd.show("sticks", "interacting_residues")
        pymol.cmd.color("palegreen", "interacting_residues")
        
        # Ensure the ligand remains visible
        pymol.cmd.show("sticks", "ligand")
        pymol.cmd.color("magenta", "ligand")

    else:
        pymol.cmd.dss("receptor")  # Assign secondary structure if missing
        pymol.cmd.show(presentation, "receptor")

        # Define hydrophobic (non-polar) and hydrophilic (polar/charged) residues
        hydrophobic_residues = "ALA+VAL+LEU+ILE+PHE+PRO+MET+TRP"
        hydrophilic_residues = "ARG+LYS+ASP+GLU+HIS+SER+THR+ASN+GLN+TYR+CYS"

        # Color hydrophobic residues in green
        pymol.cmd.color("palegreen", f"receptor and resn {hydrophobic_residues}")

        # Color hydrophilic residues in blue
        pymol.cmd.color("lightblue", f"receptor and resn {hydrophilic_residues}")

        # Color neutral residues (if needed) in white
        pymol.cmd.color("grey70", "receptor and not (resn " + hydrophobic_residues + "+" + hydrophilic_residues + ")")   

    # Label residues
    if label_residues:
        # Clear previous selections
        pymol.cmd.deselect()

        # Store unique interacting residues
        stored.residues = []
        pymol.cmd.iterate("interacting_residues and name CA", 
                          "stored.residues.append((resi, resn))")

        # Ensure residues were found
        if stored.residues:
            for resi, resn in set(stored.residues):
                pymol.cmd.label(f"resi {resi} and name CA", f'"{resn}-{resi}"')
        else:
            print("No interacting residues found for labeling.")

        # Set viewport and zoom
        pymol.cmd.viewport(*viewport_size)
        pymol.cmd.zoom("ligand")  


def MLDockKit(smiles, output_file="MLDockKit_output.txt", presentation='cartoon', label_residues=True, show_iAA=True):
    """
    Perform the entire molecular modeling pipeline:
    1. Calculate Lipinski descriptors
    2. Predict pIC50
    3. Perform protein-ligand docking
    4. Visualize docking results

    Params:
    smiles (str): SMILES string for ligand.
    output_file (str): File path for saving output.
    presentation (str): How to display the receptor [[e.g., 'surface', 'sticks', 'spheres', 'cartoon', etc.] (default: 'cartoon')].
    label_residues (bool): Option to label residues (default: True).
    show_iAA (bool): Option to show interacting amino acids only (default: True).

    Returns:
    str: Summary of the pipeline execution.
    """
    try:
        with open(output_file, "w") as f:
            f.write("." * 200 + "\n")
            # Calculate Lipinski descriptors
            lipinski_descriptors = calculate_lipinski_descriptors(smiles)
            f.write("Lipinski Descriptors"+ "\n")
            f.write(str(lipinski_descriptors))
            f.write("\n" + "." * 200 + "\n")
            print("\n" +'###Computation of Lipinsky descriptors complete'+"\n")
            
            # Predict pIC50
            pIC50_prediction = predict_pIC50(smiles)
            f.write(pIC50_prediction + "\n")
            f.write("\n" + "." * 200 + "\n")
            print('###Prediction of pIC50 complete'+"\n")

            # Perform protein-ligand docking
            docking_result = prot_lig_docking(smiles)
            f.write(docking_result + "\n")
            f.write("\n" + "." * 200 + "\n")
            print("\n" + '###Docking process complete'+"\n")
            print("##MLDockKit output is saved to " + output_file + "and image rendered in pymol"+"\n")

            # Delete files in the script directory
            script_dir = os.path.dirname(__file__)
            delete_files_with_extension(script_dir, [".smi", ".csv"])

        # Visualize docking results, passing the user-defined parameters
        visualize_dock_results(
            presentation=presentation,
            label_residues=label_residues,
            show_iAA=show_iAA
        )
        
    except Exception as e:
        return f"Error occurred: {str(e)}"
