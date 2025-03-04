import json
import pathlib

import pytest

from bionemo.api.task_tracker import load_log_file

existing_log_contents = """{"timestamp": 1685119822.7358055, "request": {"corr_id": "f46552f2-1cc3-4560-af07-04fbf4d9ab6f", "model": "diffdock", "status": "UNKNOWN"}}
{"timestamp": 1685119824.1137993, "request": {"corr_id": "f46552f2-1cc3-4560-af07-04fbf4d9ab6f", "model": "diffdock", "status": "PROCESSING"}}
{"timestamp": 1685119830.7241743, "request": {"corr_id": "f46552f2-1cc3-4560-af07-04fbf4d9ab6f", "model": "diffdock", "status": "DONE"}}
"""


@pytest.mark.parametrize("existing_file,append", [(False, False), (True, False), (True, True)])
def test_logging(make_python_client, tmpdir, existing_file, append):
    # Log file setup
    file: pathlib.Path = tmpdir / "test_log.json"
    file_path = str(file)

    want_first_entries = [json.loads(line) for line in existing_log_contents.splitlines()]
    if existing_file:
        file.write_text(existing_log_contents, "utf-8")

    api = make_python_client(file_path=file_path, append=append)
    smiles = "CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O"
    api.moflow_unguided_generate_sync(smiles, num_samples=3)
    api.megamolbart_unguided_generate_sync(smiles, num_samples=3)

    entries = load_log_file(file_path)
    if existing_file and append:
        assert entries[:3] == want_first_entries
        entries = entries[3:]
    else:
        # Check that we didn't append
        assert entries[0] != want_first_entries[0]

    # What we expect - 2 different correlation IDs, at least one "DONE" entry for a moflow and megamolbart log each.
    found_corr_ids = set()
    found_models = set()
    found_models_done = set()

    want_models = {"moflow", "megamolbart"}

    for entry in entries:
        found_corr_ids.add(entry["request"]["corr_id"])
        found_models.add(entry["request"]["model"])
        if entry["request"]["status"] == "DONE":
            found_models_done.add(entry["request"]["model"])

    assert len(found_corr_ids) == 2
    assert found_models == want_models
    assert found_models_done == want_models
