import pytest
from utils import get_test_file_path


def amino_sequence_pdb_validator(amino_sequence, pdb_string):
    """Validates a PDB file against an amino acid sequence.

    Args:
        amino_sequence (str): The amino acid sequence in the protein alphabet.
        pdb_string (str): a PDB file loaded into a string.

    Returns:
        (bool): True if the PDB file contains amino acid metadata in the same order
                as in the amino acid sequence
    """
    ALPHABET_TO_PDB_METADATA_MAP = {
        "A": "ALA",
        "C": "CYS",
        "D": "ASP",
        "E": "GLU",
        "F": "PHE",
        "G": "GLY",
        "H": "HIS",
        "I": "ILE",
        "K": "LYS",
        "L": "LEU",
        "M": "MET",
        "N": "ASN",
        "P": "PRO",
        "Q": "GLN",
        "R": "ARG",
        "S": "SER",
        "T": "THR",
        "V": "VAL",
        "W": "TRP",
        "Y": "TYR",
    }
    # Parse PDB file. Note, there are libraries to do this, but here we implement a light
    # weight parser to avoid bringing heavy deps into this repository.
    pdb_rows = pdb_string.splitlines()
    current_amino_acid_index = None
    protein_seq_from_pdb = []
    # PDB file format is a fixed-column width format, so we parse based on
    # column number rather than tab/space delimieters:
    RESIDUE_NAME_COLS = (17, 20)
    RESIDUE_ID_COLS = (22, 26)
    for row in pdb_rows:
        if len(row) < RESIDUE_ID_COLS[1]:
            continue
        amino_acid_name = row[RESIDUE_NAME_COLS[0] : RESIDUE_NAME_COLS[1]].strip()
        if amino_acid_name not in ALPHABET_TO_PDB_METADATA_MAP.values():
            continue
        amino_acid_index = int(row[RESIDUE_ID_COLS[0] : RESIDUE_ID_COLS[1]].strip())
        if amino_acid_index != current_amino_acid_index:
            protein_seq_from_pdb.append(amino_acid_name)
            current_amino_acid_index = amino_acid_index

    input_sequence = [ALPHABET_TO_PDB_METADATA_MAP[x] for x in amino_sequence]
    return input_sequence == protein_seq_from_pdb


@pytest.mark.parametrize(
    "folding_api_function, protein_sequence, msas, use_msa, relax_prediction, timeout",
    [
        ("esmfold_sync", "AAACCCCDDDDEEEEFGHIKLMNPQRSTVWY", None, None, None, None),
        (
            "openfold_sync",
            "AAACCCCDDDDEEEEFGHIKLMNPQRSTVWY",
            get_test_file_path("test_data/hhblits_full_9237707.a3m"),
            True,
            True,
            None,
        ),
        (
            "openfold_sync",
            "AAACCCCDDDDEEEEFGHIKLMNPQRSTVWY",
            [
                get_test_file_path("test_data/hhblits_full_9237707.a3m"),
                get_test_file_path("test_data/hhblits_full_9237707_dupl.a3m"),
            ],
            True,
            True,
            None,
        ),
        ("openfold_sync", "AAACCCCDDDDEEEEFGHIKLMNPQRSTVWY", None, True, True, None),
        (
            "alphafold2_sync",
            "AAACCCCDDDDEEEEFGHIKLMNPQRSTVWY",
            None,  # TODO: Bug in alphafold service prevents us from using the MSA file.
            True,
            True,
            1800,
        ),
    ],
)
def test_folding(make_python_client, folding_api_function, protein_sequence, msas, use_msa, relax_prediction, timeout):
    # Run Test
    api = make_python_client()
    function_to_call = getattr(api, folding_api_function)
    # TODO: Present folding API in a more unified way
    if folding_api_function == "esmfold_sync":
        result = function_to_call(protein_sequence, timeout)
    else:
        result = function_to_call(protein_sequence, msas, use_msa, relax_prediction, timeout)
    assert amino_sequence_pdb_validator(protein_sequence, result)
