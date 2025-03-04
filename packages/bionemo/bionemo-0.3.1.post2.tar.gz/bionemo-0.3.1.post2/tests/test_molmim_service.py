import numpy as np
import pytest


@pytest.mark.parametrize(
    "smiles_list",
    [(["CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O", "C", "Clc1cc(Cl)cc(c1)c1nc2c(o1)cc(cc2)C(=O)O"]), (["C"])],
)
def test_molmim_embeddings(make_python_client, smiles_list):
    api = make_python_client()
    result = api.molmim_embeddings_sync(smiles_list)
    assert isinstance(result, list)
    assert len(result) == len(smiles_list)
    embedding_dimension = 512
    for i in result:
        assert isinstance(i, np.ndarray)
        assert i.dtype == np.float32
        assert i.shape == (embedding_dimension,)


def test_molmim_decode(make_python_client):
    api = make_python_client()
    num_embeddings = 3
    embedding_dimension = 512
    embeddings = [np.random.rand(embedding_dimension).astype(np.float32) for _ in range(num_embeddings)]
    result = api.molmim_decode_sync(embeddings)
    assert len(result) == num_embeddings
    for result in result:
        assert isinstance(result, str)


def test_molmim_decode_bad_input(make_python_client):
    api = make_python_client()
    embeddings = np.random.rand(5, 100)
    with pytest.raises(ValueError):
        api.molmim_decode_sync(embeddings)


def test_molmim_round_trip(make_python_client):
    api = make_python_client()
    smiles_list = ['COc1cc2c(cc1OC)C(=O)C(CC1CCN(Cc3ccccc3)CC1)C2', 'CC(=O)Oc1ccccc1C(=O)O']
    embeddings = api.molmim_embeddings_sync(smiles_list)
    result = api.molmim_decode_sync(embeddings)
    assert len(smiles_list) == len(result)
    # MolMIM reconstruction is not 100%, so we can't assert on
    for elem in result:
        assert isinstance(elem, str) and len(elem) > 0
