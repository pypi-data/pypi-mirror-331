import pytest


MAGIC_MODEL_PARAMS = {
    "650m": {"embedding_size": 1280, "logits_size": 33},
    "3b": {"embedding_size": 2560, "logits_size": 33},
    "15b": {"embedding_size": 5120, "logits_size": 33},
}


@pytest.mark.parametrize(
    "protein_list, model_size",
    [
        (
            [
                "MRLLQLLFRASPATLLLVLCLQLGANKAQDNTRKIIIKNFDIPKSVRPNDEVTAVLAVQTELKECMVVKTYLISSIPLQGAFNYKYTACLCDDNPKTFYWDFYTNRTVQIAAVVDVIRELGICPDDAAVIPIKNNRFYTIEILKVE",
                "LKVE",
                "MGSASPGLSSVSPSHLLLPPDTVSRTGLEKAAAGAVGLERRDWSPSPPATPEQGLSAFYLSYFDMLYPEDSSWAAKAPGASSREEPPEEPEQCPVIDSQAPAGSLDLVPGGLTLEEHSLEQVQSMVVGEVLKDIETACKLLNITADPMDWSPSNVQKWLLWTEHQYRLPPMGKAFQELAGKELCAMSEEQFRQRSPLGGDVLHAHLDIWKSAAWMKERTSPGAIHYCASTSEESWTDSEVDSSCSGQPIHLWQFLKELLLKPHSYGRFIRWLNKEKGIFKIEDSAQVARLWGIRKNRPAMNYDKLSRSIRQYYKKGIIRKPDISQRLVYQFVHPI",
            ],
            "650m",
        ),
        (["MMMM"], "650m"),
        (
            [
                "MRLLQLLFRASPATLLLVLCLQLGANKAQDNTRKIIIKNFDIPKSVRPNDEVTAVLAVQTELKECMVVKTYLISSIPLQGAFNYKYTACLCDDNPKTFYWDFYTNRTVQIAAVVDVIRELGICPDDAAVIPIKNNRFYTIEILKVE",
                "LKVE",
                "MGSASPGLSSVSPSHLLLPPDTVSRTGLEKAAAGAVGLERRDWSPSPPATPEQGLSAFYLSYFDMLYPEDSSWAAKAPGASSREEPPEEPEQCPVIDSQAPAGSLDLVPGGLTLEEHSLEQVQSMVVGEVLKDIETACKLLNITADPMDWSPSNVQKWLLWTEHQYRLPPMGKAFQELAGKELCAMSEEQFRQRSPLGGDVLHAHLDIWKSAAWMKERTSPGAIHYCASTSEESWTDSEVDSSCSGQPIHLWQFLKELLLKPHSYGRFIRWLNKEKGIFKIEDSAQVARLWGIRKNRPAMNYDKLSRSIRQYYKKGIIRKPDISQRLVYQFVHPI",
            ],
            "3b",
        ),
        (["MMMM"], "3b"),
        (
            [
                "MRLLQLLFRASPATLLLVLCLQLGANKAQDNTRKIIIKNFDIPKSVRPNDEVTAVLAVQTELKECMVVKTYLISSIPLQGAFNYKYTACLCDDNPKTFYWDFYTNRTVQIAAVVDVIRELGICPDDAAVIPIKNNRFYTIEILKVE",
                "LKVE",
                "MGSASPGLSSVSPSHLLLPPDTVSRTGLEKAAAGAVGLERRDWSPSPPATPEQGLSAFYLSYFDMLYPEDSSWAAKAPGASSREEPPEEPEQCPVIDSQAPAGSLDLVPGGLTLEEHSLEQVQSMVVGEVLKDIETACKLLNITADPMDWSPSNVQKWLLWTEHQYRLPPMGKAFQELAGKELCAMSEEQFRQRSPLGGDVLHAHLDIWKSAAWMKERTSPGAIHYCASTSEESWTDSEVDSSCSGQPIHLWQFLKELLLKPHSYGRFIRWLNKEKGIFKIEDSAQVARLWGIRKNRPAMNYDKLSRSIRQYYKKGIIRKPDISQRLVYQFVHPI",
            ],
            "15b",
        ),
        (["MMMM"], "15b"),
    ],
)
def test_esm2(make_python_client, protein_list, model_size):
    api = make_python_client()
    result = api.esm2_sync(protein_list, model_size)
    assert len(result) == len(protein_list)
    for i, per_protein_response in enumerate(result):
        seq_length = len(protein_list[i])
        assert set(per_protein_response.keys()) == set(["embeddings", "logits", "tokens", "representations"])
        # Assert output matches magic values.
        assert per_protein_response["embeddings"].shape == (MAGIC_MODEL_PARAMS[model_size]["embedding_size"],)
        assert per_protein_response["logits"].shape == (seq_length, MAGIC_MODEL_PARAMS[model_size]["logits_size"])
        assert per_protein_response["tokens"].shape == (seq_length,)
        assert per_protein_response["representations"].shape == (
            seq_length,
            MAGIC_MODEL_PARAMS[model_size]["embedding_size"],
        )


def test_esm2_bad_model_name(make_python_client):
    api = make_python_client()
    with pytest.raises(ValueError):
        api.esm2_sync(['AAAA'], '40k')
