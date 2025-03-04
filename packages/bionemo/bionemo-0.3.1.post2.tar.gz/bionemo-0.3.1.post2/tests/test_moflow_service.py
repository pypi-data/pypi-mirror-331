import numpy as np
import pytest


@pytest.mark.parametrize(
    "smiles_list",
    [(["CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O", "C", "Clc1cc(Cl)cc(c1)c1nc2c(o1)cc(cc2)C(=O)O"]), (["C"])],
)
def test_moflow_embeddings(make_python_client, smiles_list):
    api = make_python_client()
    result = api.moflow_embeddings_sync(smiles_list)
    assert isinstance(result, list)
    assert len(result) == len(smiles_list)
    embedding_dimension = 6800
    for i in result:
        assert isinstance(i, np.ndarray)
        assert i.dtype == np.float32
        assert i.shape == (embedding_dimension,)


def test_moflow_decode(make_python_client):
    api = make_python_client()
    num_embeddings = 3
    embedding_dimension = 6800
    embeddings = [np.random.rand(embedding_dimension).astype(np.float32) for _ in range(num_embeddings)]
    result = api.moflow_decode_sync(embeddings)
    assert len(result) == num_embeddings
    for result in result:
        assert isinstance(result, str)


def test_moflow_decode_bad_input(make_python_client):
    api = make_python_client()
    embeddings = np.random.rand(5, 100)
    with pytest.raises(ValueError):
        api.moflow_decode_sync(embeddings)
