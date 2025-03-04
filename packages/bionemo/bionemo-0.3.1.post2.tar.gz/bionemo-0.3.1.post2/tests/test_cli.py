import json
import os
from typing import Dict, List

import click
import pytest
from click.testing import CliRunner

from bionemo.cli.cli import CONFIG_DIR, CONFIG_FILE, cli

STAGING_ADDRESS = "https://stg.bionemo.ngc.nvidia.com/v1"
HOST_ADDRESS = os.getenv('HOST_ADDRESS', STAGING_ADDRESS)
API_KEY = os.environ['NGC_API_KEY_STAGING'] if HOST_ADDRESS == STAGING_ADDRESS else os.environ['NGC_API_KEY']

# Note: I might have to use the runner.isolated_filesystem here.
def setup_module():
    """Setup for the entire module."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": API_KEY, "host_address": HOST_ADDRESS}, f)


def teardown_module():
    """Teardown for the entire module."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    if os.path.exists(CONFIG_DIR):
        os.rmdir(CONFIG_DIR)


def test_config_set():
    runner = CliRunner()
    # Setting up config using the `config set` command
    result = runner.invoke(cli, ['config', 'set'], input="test_host\ntest_api_key\n")
    assert result.exit_code == 0
    assert 'Configuration saved.' in result.output

    # Assert the configuration file was created and has correct data
    assert os.path.exists(CONFIG_FILE)
    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)
    assert config_data == {'host_address': 'test_host', 'api_key': 'test_api_key'}


def test_config_show():
    runner = CliRunner()
    # Show config after it has been set
    result = runner.invoke(cli, ['config', 'show'])
    assert result.exit_code == 0
    assert 'test_host' in result.output
    assert 'test_api_key' in result.output


def test_config_get():
    runner = CliRunner()
    # Get individual config value
    result = runner.invoke(cli, ['config', 'get', 'host_address'])
    assert result.exit_code == 0
    assert 'test_host' in result.output


def test_bionemo_list_models():
    setup_module()
    runner = CliRunner()
    result = runner.invoke(cli, ['list_models'])
    assert result.exit_code == 0
    teardown_module()


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
def test_cli_get_smiles(pubchem_cid: str, expected: str):
    setup_module()
    runner = CliRunner()
    result = runner.invoke(cli, ['get_smiles', pubchem_cid])
    assert result.exit_code == 0
    assert result.output.strip() == expected


def test_cli_task_utils():
    """
    Test fetch_task_status(), delete_task() and cancel_task(). We use a correlation_id as a string
    to determine our status etc.
    """
    protein = "MSFSGKYQLQSQENFEAFMKAIGLPEELIQKGKDIKGVSEIVQNGKHFKFTITAGSKVIQNEFTVGEECELETMTGEKVKTVVQLEGDNKLVTTFKNIKSVTELNGDIITNTMTLGDIVFKRISKRI"
    setup_module()
    runner = CliRunner()
    result = runner.invoke(cli, ['openfold_async', protein])
    assert result.exit_code == 0

    # This is kinda hacky. Correlation_id looks like <model_name>:<uuid> so we just grab the uuid portion.
    correlation_id = result.output.strip().split(":")[-1]

    task_status = runner.invoke(cli, ['fetch_task_status', correlation_id])
    assert task_status.exit_code == 0
    assert task_status.output.strip() in ["CREATED", "PROCESSING"]

    cancel_status = runner.invoke(cli, ['cancel_task', correlation_id])
    teardown_module()


def test_bionemo_get_uniprot():
    uniprotId = "P00374"
    runner = CliRunner()
    result = runner.invoke(cli, ['get_uniprot', uniprotId])
    # TODO(@jomitchell): Finish test once uniprot gets updated
