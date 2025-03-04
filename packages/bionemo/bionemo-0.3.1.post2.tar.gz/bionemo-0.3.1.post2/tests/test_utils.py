import os

import pytest

from bionemo.api import BadRequestId, IncorrectParamsError


# TODO: Test what happens when given a bad UniProt ID ("Pgoaway", "badval", etc).
# TODO: Test what happens when given a bad PubChem ID ("Pgoaway", "badval", etc).
@pytest.mark.parametrize(
    "uniprotId,expected",
    [
        (
            "P00374",
            "MVGSLNCIVAVSQNMGIGKNGDLPWPPLRNEFRYFQRMTTTSSVEGKQNLVIMGKKTWFSIPEKNRPLKGRINLVLSRELKEPPQGAHFLSRSLDDALKLTEQPELANKVDMVWIVGGSSVYKEAMNHPGHLKLFVTRIMQDFESDTFFPEIDLEKYKLLPEYPGVLSDVQEEKGIKYKFEVYEKND",
        ),
        ("P00123", "YDAAAGKATYDASCAMCHKTGMMGAPKVGDKAAWAPHIAKGMNVMVANSIKGYKGTKGMMPAKGGNPKLTDAQVGNAVAYMVGQSK"),
        (
            "P31415",
            "MSATDRMGPRAVPGLRLALLLLLVLGTPKSGVQGQEGLDFPEYDGVDRVINVNAKNYKNVFKKYEVLALLYHEPPEDDKASQRQFEMEELILELAAQVLEDKGVGFGLVDSEKDAAVAKKLGLTEVDSMYVFKGDEVIEYDGEFSADTIVEFLLDVLEDPVELIEGERELQAFENIEDEIKLIGYFKSKDSEHYKAFEDAAEEFHPYIPFFATFDSKVAKKLTLKLNEIDFYEAFMEEPVTIPDKPNSEEEIVNFVEEHRRSTLRKLKPESMYETWEDDMDGIHIVAFAEEADPDGFEFLETLKAVAQDNTENPDLSIIWIDPDDFPLLVPYWEKTFDIDLSAPQIGVVNVTDADSVWMEMDDEEDLPSAEELEDWLEDVLEGEINTEDDDDDDDD",
        ),
    ],
)
def test_get_uniprot(make_python_client, uniprotId: str, expected: str):
    api = make_python_client()
    result = api.get_uniprot(uniprotId)
    assert result == expected


@pytest.mark.parametrize(
    "pubchem_cid,expected",
    [
        (
            "2224",
            "CCCCCC=CCC=CCC=CCC=CCCCC(=O)C(F)(F)F",
        ),
        (
            "1234",
            "CC(C)C(CCCN(C)CCC1=CC(=C(C=C1)OC)OC)(C#N)C2=CC(=C(C(=C2)OC)OC)OC",
        ),
    ],
)
def test_get_smiles(make_python_client, pubchem_cid: str, expected: str):
    # Run Test
    api = make_python_client()
    result = api.get_smiles(pubchem_cid)
    assert result == expected


def test_task_utils(make_python_client):
    """
    Test fetch_task_status(), delete_task() and cancel_task().  Each can take a correlation_id
    or a RequestId (which contains a correlation_id as a str).
    """
    api = make_python_client()
    protein_sequence = "MSFSGKYQLQSQENFEAFMKAIGLPEELIQKGKDIKGVSEIVQNGKHFKFTITAGSKVIQNEFTVGEECELETMTGEKVKTVVQLEGDNKLVTTFKNIKSVTELNGDIITNTMTLGDIVFKRISKRI"

    # Create a long-running task, immediately get it's status and then delete it (using correlation_id).
    rqstId = api.openfold_async(protein_sequence)
    task_status = api.fetch_task_status(rqstId.correlation_id)
    assert task_status in ["CREATED", "PROCESSING", "SUBMITTED"]
    _cancel_status = api.cancel_task(rqstId.correlation_id)
    # TODO: Check _cancel_status

    # Create a long-running task, get it's status and then delete it (using RequestId).
    rqstId = api.openfold_async(protein_sequence)
    task_status = api.fetch_task_status(rqstId)
    assert task_status in ["CREATED", "PROCESSING", "SUBMITTED"]
    _cancel_status = api.cancel_task(rqstId)
    # TODO: Check _cancel_status.  Again.

    # Create a long-running task, get it's status (using something bogus) and expect an exception.
    rqstId = api.openfold_async(protein_sequence)
    try:
        task_status = api.cancel_task(42)
    except BadRequestId:
        pass
    except Exception as somethingElse:
        assert False, f"Caught {type(somethingElse)}: {somethingElse}, was expecting a BadRequestId"


def test_task_order(make_python_client):
    api = make_python_client()

    ordered_req_ids = [api.esmfold_async('AAAAA').correlation_id for _ in range(5)]
    # The task API should reverse this order, with the most recent first
    ordered_req_ids.reverse()

    # This should just be 5, but with parallel tests, another call could inject itself, so we give a buffer to be safe.
    fetched_tasks = api.fetch_tasks(100)
    matching_ids = [task['correlation_id'] for task in fetched_tasks if task['correlation_id'] in ordered_req_ids]

    # We have a different problem if this fails, so separate out the check even though this is usually extraneous,
    # for debugging purposes.
    assert len(matching_ids) == len(ordered_req_ids)
    # Now check for content
    assert matching_ids == ordered_req_ids


def test_verify_key(make_python_client):
    """
    Test verify_key().  First we test with the NGC_API_KEY as set in the environment (which should work),
    then we alter that value and test again.  The 2nd test should fail.
    """

    api = make_python_client()
    assert api.verify_key(), "Key was bad but it should've been good."

    old_key = os.getenv("NGC_API_KEY")
    api = make_python_client()
    # If the API key is incorrect during construction, an error should be raised.
    # Below is a test to check the rare case that construction succeeded with a correct API
    # key, but then API keys were changed mid-session. We emulate this change by modifying the
    # API key to something in correct after construction:
    api.api_key = "wrong_api_key"
    api.headers["Authorization"] = api.api_key
    assert not api.verify_key(), "Key was good but it should've been bad."
    os.environ["NGC_API_KEY"] = old_key  # Restore the old key, just in case.


def test_fetch_tasks(make_python_client):
    """
    Test fetch_tasks().  The default is to fetch 10 tasks (the 10 most recent), but a smaller
    or larger number may be specified.
    """

    api = make_python_client()
    # Make sure we have a bunch of tasks.  They have to be async tasks - the
    # sync ones just return the results.
    prot = "MSFSGKYQLQSQENFEAFMKAIGLPEELIQKGKDIKGVSEIVQNGKHFKFTITAGSKVIQNEFTVGEECELETMTGEKVKTVVQLEGDNKLVTTFKNIKSVTELNGDIITNTMTLGDIVFKRISKRI"
    test_tasks = []
    for i in range(15):
        test_tasks.append(api.esmfold_async(prot))

    tasks = api.fetch_tasks()
    assert len(tasks) == 10, f"Expected 10 tasks, got {len(tasks)}"

    tasks = api.fetch_tasks(5)
    assert len(tasks) == 5, f"Expected 5 tasks, got {len(tasks)}"

    tasks = api.fetch_tasks(15)
    assert len(tasks) == 15, f"Expected 15 tasks, got {len(tasks)}"

    try:
        _ = api.fetch_tasks(-1)
    except IncorrectParamsError:
        pass
    except Exception as somethingElse:
        assert False, f"Asked for -1 tasks, raised {somethingElse} instead of  IncorrectParamsError"

    # Clean up.
    for task in test_tasks:
        api.delete_task(task)
