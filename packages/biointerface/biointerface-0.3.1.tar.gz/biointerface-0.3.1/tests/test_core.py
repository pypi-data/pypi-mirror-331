"""Test core module of biointerface."""

import pytest
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBExceptions import PDBConstructionException
from PDBNucleicAcids.NucleicAcid import DoubleStrandNucleicAcid

# to be tested
from biointerface import Interface, build_interfaces


def get_test_structure():
    filepath = "tests/data/gattaca.cif"
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("gattaca", filepath)

    return structure


def test_extract_contacts():
    structure = get_test_structure()
    face = Interface(structure=structure, protein_chain_id="C")
    face.get_atomic_contacts()

    assert isinstance(face.contacts, list)
    assert all(len(contact) == 2 for contact in face.contacts)
    assert all(contact[0] != contact[1] for contact in face.contacts)


def test_get_atoms():
    structure = get_test_structure()
    face = Interface(structure=structure, protein_chain_id="C")
    atoms = face.get_protein_atoms()
    assert isinstance(atoms, list)
    assert all(
        hasattr(atom, "coord") for atom in atoms
    )  # Controlla se hanno coordinate

    atoms = face.get_dna_atoms()
    assert isinstance(atoms, list)
    assert all(
        hasattr(atom, "coord") for atom in atoms
    )  # Controlla se hanno coordinate


def test_get_residues():
    structure = get_test_structure()
    face = Interface(structure=structure, protein_chain_id="C")
    residues = face.get_aminoacids()
    assert isinstance(residues, list)
    assert all(
        hasattr(residue, "get_resname") for residue in residues
    )  # Devono avere nomi di residui

    residues = face.get_nucleotides()
    assert isinstance(residues, list)
    assert all(
        hasattr(residue, "get_resname") for residue in residues
    )  # Devono avere nomi di residui


def test_get_interface_data():
    structure = get_test_structure()
    face = Interface(structure=structure, protein_chain_id="C")
    df = face.get_interface_data()
    assert df is not None
    assert not df.empty
    assert set(
        ["prot_atom_name", "dna_atom_name", "euclidean_distance"]
    ).issubset(df.columns)


def test_get_bound_double_strands():
    structure = get_test_structure()
    face = Interface(structure=structure, protein_chain_id="C")
    dsna_list = face.get_bound_double_strands()
    assert isinstance(dsna_list, list)
    assert isinstance(dsna_list[0], DoubleStrandNucleicAcid)


def test_non_protein():
    structure = get_test_structure()

    # "A" is not a protein but a DNA chain
    # should raise an error
    with pytest.raises(PDBConstructionException):
        Interface(structure=structure, protein_chain_id="A")


def test_no_contacts():
    structure = get_test_structure()
    face = Interface(
        structure=structure, protein_chain_id="C", search_radius=1.0
    )

    assert len(face.contacts) == 0


def test_build_interfaces():
    structure = get_test_structure()
    face_list = build_interfaces(structure=structure, search_radius=5.0)

    assert isinstance(face_list, list)
    assert len(face_list) == 1
    assert isinstance(face_list[0], Interface)
