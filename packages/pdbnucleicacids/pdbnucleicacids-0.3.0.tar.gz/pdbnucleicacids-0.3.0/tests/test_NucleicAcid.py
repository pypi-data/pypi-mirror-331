"""Testing the NucleicAcid module from PDBNucleicAcids."""

# import pytest
from Bio.PDB.MMCIFParser import MMCIFParser

# to be tested
from PDBNucleicAcids.NucleicAcid import NABuilder
from PDBNucleicAcids.NucleicAcid import DSNABuilder


def get_test_structure():
    filepath = "tests/data/gattaca.cif"
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("gattaca", filepath)

    return structure


def test_NABuilder():
    """Test per verificare il comportamento con residuo non nucleico."""
    structure = get_test_structure()

    builder = NABuilder()
    na_list = builder.build_nucleic_acids(structure)
    assert na_list

    na = na_list[0]
    assert na.get_seq()
    assert na.get_atoms()
    assert na.get_na_type()


def test_DSNABuilder():
    """Test per verificare il comportamento con residuo non nucleico."""
    structure = get_test_structure()

    builder = DSNABuilder()
    dsna_list = builder.build_double_strands(structure)
    assert dsna_list

    dsna = dsna_list[0]
    assert dsna.get_atoms()
    assert dsna.get_i_strand()
    assert dsna.get_j_strand()
    assert dsna.get_na_complex_type()
    assert dsna.get_stagger_values()
    assert dsna.get_dataframe().iloc[0, 0]
