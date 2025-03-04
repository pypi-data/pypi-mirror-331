import pytest


@pytest.mark.parametrize(
    "sequence, databases, algorithm, format_, e_value, bit_score, iterations, timeout",
    [
        (
            "SATTPPGDLEQPELEARVKEIIEVDGYQFRDLNDNGELDPYEDWRLPTPERVADLVGQMSLVEKSGLMLINTLNAACDPQTGEFGVLPAQADNYINTQHMHRFVFRNVVDVRAEGVECTGTGTPVVSPAEAATFTNAVQEMSEATRLGIPSLFKSNARNHIDPDARVGINEAAGAFSAFPKEAGIAAAALGEQARRTGEATTGDMSVVADFADVMGEEWASIGLRGMYGYMADLSTEPRWYRTHETFTEDAYLAAEIMETLVQTLQGEELTDNGLALSPQTRVALTLKHFPGGGPQELGLDPHYAFGKAQVYPAGRFEEHFLPFQAAIDAGVSSIMPYYGVPVDVPVVGGEPGETYPHTGFAFSDSIVNGLLRDQLGFTGYVNSDTGIINDRAWGLEGNTVPERVAAAINGGTDTLSGFSDVSVITDLYEADLISEERIDLAAERLLEPLFDMGLFENPYVDPDVATATVGADDHRAVGLDLQRKSLVLLQNEETDEGPVLPLKEGGDVYILGDFTEETVESYGYEVTNGNVAEGEERPSAAGSDYVLISMTAKTNAGDYVSDDPSLGLNPDHGTNPSVIIGDDGEPLPGLDGQSLWGAADVCVHKEGHEENPSCTDNRLRFGGAYPWESSILDFTGMEAAESWEVVPSLETIQEVMAEVEDPSKVILHVYFRQPYVLDEESGLRDAGAILAGFGMTDTALMDVLTGAYAPQGKLPFALAGTREAIIEQDSDRPGYDETEDGALYPFGYGLTYEDDTEE",
            ['mgnify', 'smallbfd', 'uniref90'],
            'jackhmmer',
            'a3m',
            0.0001,
            None,
            1,
            None,
        ),
        (
            "MGDTAVNVGSAAGTGANTTNTTTQAPQNKPYFTYNNEIIGEATQSNPLGNVVRTTISFKSDDKVSDLISTISKAVQFHKNNSASGENVTINENDFINQLKANGVTVKTVQPSNKNEKAYEAIDKVPSTSFNITLSATGDNNQTATIQIPMVPQGLEHHHHHH",
            ['mgnify', 'smallbfd', 'uniref90'],
            'jackhmmer',
            'a3m',
            0.0001,
            None,
            1,
            None,
        ),
    ],
)
def test_msa_jackhmmer(
    make_python_client, sequence, databases, algorithm, format_, e_value, bit_score, iterations, timeout
):
    # Run Test
    api = make_python_client()
    result = api.msa_sync(sequence, databases, algorithm, format_, e_value, bit_score, iterations, timeout)
    # Assertions
    assert len(result) == len(databases)

    for res in result:
        assert 'database' in res and res['database'] in databases
        assert 'format' in res and res['format'] == format_
        assert 'alignment' in res and isinstance(res['alignment'], str)


def test_msa_invalid_algorithm(make_python_client):
    api = make_python_client()
    with pytest.raises(ValueError):
        api.msa_async("AAAAA", databases=["mgnify"], algorithm="random")
