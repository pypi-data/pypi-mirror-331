import numpy as np
import pytest


@pytest.mark.parametrize(
    "smiles_list",
    [(["CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O", "C", "Clc1cc(Cl)cc(c1)c1nc2c(o1)cc(cc2)C(=O)O"]), (["C"])],
)
def test_megamolbart_embeddings(make_python_client, smiles_list):
    # Run Test
    api = make_python_client()
    result = api.megamolbart_embeddings_sync(smiles_list)
    assert type(result) == list
    assert len(result) == len(smiles_list)
    EMBEDDING_DIMENSION = 512
    for i in result:
        assert type(i) == np.ndarray
        assert i.dtype == np.float32
        assert i.shape == (EMBEDDING_DIMENSION,)
