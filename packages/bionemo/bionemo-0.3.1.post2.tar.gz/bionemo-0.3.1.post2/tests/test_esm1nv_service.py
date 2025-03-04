import numpy as np
import pytest


@pytest.mark.parametrize(
    "protein_list",
    [
        (
            [
                "MRLLQLLFRASPATLLLVLCLQLGANKAQDNTRKIIIKNFDIPKSVRPNDEVTAVLAVQTELKECMVVKTYLISSIPLQGAFNYKYTACLCDDNPKTFYWDFYTNRTVQIAAVVDVIRELGICPDDAAVIPIKNNRFYTIEILKVE",
                "LKVE",
                "MGSASPGLSSVSPSHLLLPPDTVSRTGLEKAAAGAVGLERRDWSPSPPATPEQGLSAFYLSYFDMLYPEDSSWAAKAPGASSREEPPEEPEQCPVIDSQAPAGSLDLVPGGLTLEEHSLEQVQSMVVGEVLKDIETACKLLNITADPMDWSPSNVQKWLLWTEHQYRLPPMGKAFQELAGKELCAMSEEQFRQRSPLGGDVLHAHLDIWKSAAWMKERTSPGAIHYCASTSEESWTDSEVDSSCSGQPIHLWQFLKELLLKPHSYGRFIRWLNKEKGIFKIEDSAQVARLWGIRKNRPAMNYDKLSRSIRQYYKKGIIRKPDISQRLVYQFVHPI",
            ]
        ),
        (["MMMM"]),
    ],
)
def test_esm1nv(make_python_client, protein_list):
    api = make_python_client()
    result = api.esm1nv_sync(protein_list)
    assert type(result) == list
    assert len(result) == len(protein_list)
    EMBEDDING_DIMENSION = 768
    for i in result:
        assert type(i) == np.ndarray
        assert i.dtype == np.float32
        assert i.shape == (EMBEDDING_DIMENSION,)
