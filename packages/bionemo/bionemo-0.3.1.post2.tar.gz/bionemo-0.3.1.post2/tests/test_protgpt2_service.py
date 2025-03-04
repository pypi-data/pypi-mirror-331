import pytest


@pytest.mark.parametrize(
    "max_length, top_k, repetition_penalty, num_return_sequences, percent_to_keep, timeout",
    [(200, 400, 1.1, 100, 0.5, None), (200, 400, 1.3, 2000, 0.99, None)],
)
def test_protgpt2(
    make_python_client, max_length, top_k, repetition_penalty, num_return_sequences, percent_to_keep, timeout
):
    # Run Test
    api = make_python_client()
    result = api.protgpt2_sync(
        max_length,
        top_k,
        repetition_penalty,
        num_return_sequences,
        percent_to_keep,
        timeout=None,
    )

    assert set(result.keys()) == set(["generated_sequences", "perplexities"])
    assert len(result["generated_sequences"]) == num_return_sequences
    assert len(result["perplexities"]) == num_return_sequences
