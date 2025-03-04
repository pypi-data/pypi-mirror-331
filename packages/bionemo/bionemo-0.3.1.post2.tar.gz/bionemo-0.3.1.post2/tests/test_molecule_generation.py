import pytest


def _check_molecule_result_validity(result, num_samples):
    assert set(result.keys()) == {"generated_molecules", "scores"}
    for key in result.keys():
        assert len(result[key]) == num_samples
    for item in result["generated_molecules"]:
        assert isinstance(item, str)
    for item in result["scores"]:
        assert isinstance(item, float)


@pytest.mark.parametrize("model", ("moflow_sync", "molmim_unguided_generate_sync", "megamolbart_sync"))
@pytest.mark.parametrize(
    "smiles, num_samples, timeout", [("CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O", 1, None), ("c1ccccc1", 10, 1000)]
)
def test_unguided_generation_sync(make_python_client, model, smiles, num_samples, timeout):
    # Run Test
    api = make_python_client()
    endpoint = getattr(api, model)
    # TODO Test non-1 radii when server allows.
    result = endpoint(smiles, num_samples=num_samples, scaled_radius=1, timeout=timeout)
    # Assertions
    _check_molecule_result_validity(result, num_samples)


@pytest.mark.parametrize("model", ("moflow_async", "molmim_unguided_generate_async", "megamolbart_async"))
@pytest.mark.parametrize(
    "smiles, num_samples, timeout", [("CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O", 1, None), ("c1ccccc1", 10, 1000)]
)
def test_unguided_generation_async(make_python_client, model, smiles, num_samples, timeout):
    # Run Test
    api = make_python_client()
    endpoint = getattr(api, model)
    req = endpoint(smiles, num_samples=num_samples, scaled_radius=1, timeout=timeout)
    result = api.fetch_result(req)
    # Assertions
    _check_molecule_result_validity(result, num_samples)


@pytest.mark.parametrize("model", ("moflow_guided_generate_sync", "molmim_guided_generate_sync"))
@pytest.mark.parametrize(
    "smiles, property_name, iterations, num_samples, min_similarity",
    [("CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O", "QED", 3, 5, 0.0), ("C", "plogP", 10, 20, 0.5)],
)
def test_guided_generation_sync(
    make_python_client, model, smiles, property_name, iterations, num_samples, min_similarity
):
    # Run Test
    api = make_python_client()
    endpoint = getattr(api, model)
    result = endpoint(smiles, property_name, iterations, num_samples=num_samples, min_similarity=min_similarity)
    # Assertions
    _check_molecule_result_validity(result, num_samples)


@pytest.mark.parametrize("model", ("moflow_guided_generate_async", "molmim_guided_generate_async"))
@pytest.mark.parametrize(
    "smiles, property_name, iterations, num_samples, min_similarity",
    [("CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O", "QED", 3, 5, 0.0), ("C", "plogP", 10, 20, 0.5)],
)
def test_guided_generation_async(
    make_python_client, model, smiles, property_name, iterations, num_samples, min_similarity
):
    # Run Test
    api = make_python_client()
    endpoint = getattr(api, model)
    req = endpoint(smiles, property_name, iterations, num_samples=num_samples, min_similarity=min_similarity)
    result = api.fetch_result(req)
    # Assertions
    _check_molecule_result_validity(result, num_samples)
