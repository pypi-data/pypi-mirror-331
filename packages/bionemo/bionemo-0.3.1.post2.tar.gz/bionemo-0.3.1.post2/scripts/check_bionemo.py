# Copyright (c) 2023-2024, NVIDIA CORPORATION.  All rights reserved.

import argparse
import json
import random
import time
import traceback
import uuid

import numpy as np

import bionemo
from bionemo.api import BionemoClient

# TODOs(trvachov):
# Replace print with logging.
# Always log verbose to file
# Or, replace everything with pytest -- need to understand gitlab hooks first.


class TestHelper:
    """
    Helper class to run python API tests.
    TODO: Replace everything with pytest
    """

    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

    def __init__(self, verbosity, expected_exceptions=[]):
        self.verbose = verbosity
        for item in expected_exceptions:
            if not issubclass(item, Exception):
                raise ValueError("Incorrect exception list: {}".format(expected_exceptions))
        self.expected_exceptions = expected_exceptions

    def print_test(self, test_target):
        print(TestHelper.BOLD + "Testing {} ...".format(test_target) + TestHelper.END, end=" ", flush=True)

    def print_success(self, time=None):
        if time is not None:
            print(TestHelper.BOLD + TestHelper.GREEN + "SUCCESS. {:.2f} seconds".format(time) + TestHelper.END)
        else:
            print(TestHelper.BOLD + TestHelper.GREEN + "SUCCESS." + TestHelper.END)

    def print_fail(self):
        if time is not None:
            print(TestHelper.BOLD + TestHelper.RED + "FAIL. {:.2f} seconds".format(time) + TestHelper.RED)
        else:
            print(TestHelper.BOLD + TestHelper.RED + "FAIL." + TestHelper.END)

    def expect_nonempty_response(self, response):
        """Checks that response is non-empty."""
        if type(response) == str:  # list models outputs a dict, all others a string
            try:
                response = json.loads(response)
            except json.decoder.JSONDecodeError:
                # Ad-hoc allowing PDB strings
                pass
        # numpy arrays can't be typecast into bool, so add special logic to handle this.
        if type(response) != np.ndarray and not response:
            raise ValueError("Empty response: {}".format(response))
        return True

    def expect_valid_correlation_id(self, request_id):
        """Checks that request_id.correlation_id is a correlation id."""
        if not request_id.model_name:
            raise ValueError("Expected non-empty (model name), in response.")
        # This will throw an error if invalid UUID
        uuid.UUID(request_id.correlation_id, version=4)
        # TODO: Should we cancel the submitted task?
        return True

    def check_function(self, assertion_function, function_under_test, *args_test, **kwargs_test):
        """Wrapper to run API test."""
        self.print_test(function_under_test.__name__ + " " + (str(kwargs_test) if kwargs_test else ""))
        response = None  # Initialize response to be returned as None in case
        # an exception is raised.
        if self.verbose:
            print("\nCalling: {}({},{})".format(function_under_test.__name__, args_test, kwargs_test))
            print("Asserting function: {}".format(assertion_function.__name__))
        try:
            start_time = time.time()
            response = function_under_test(*args_test, **kwargs_test)
            end_time = time.time()
            call_duration = end_time - start_time
            if self.verbose:
                print("Response:\n{}".format(response))

            if assertion_function(response):
                self.print_success(call_duration)
        except Exception as e:
            end_time = time.time()
            call_duration = end_time - start_time
            if type(e) in self.expected_exceptions:
                if self.verbose:
                    print("Caught expected exception: {}".format(traceback.format_exc()))
                self.print_success(call_duration)
            else:
                self.print_fail(call_duration)
                if self.verbose:
                    print(traceback.format_exc())
        return response


def make_random_protein(length):
    """Generates random protein string to avoid cache hits on server."""
    PROTEIN_ALPHABET = [
        'A',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'K',
        'L',
        'M',
        'N',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'V',
        'W',
        'Y',
    ]
    protein_string = random.choices(PROTEIN_ALPHABET, k=length)
    return "".join(protein_string)


def check_api(NGC_KEY, random_protein=False, verbose=False, expected_exceptions=[]):
    """Main script to check API calls that wait for a response."""
    api = BionemoClient(api_key=NGC_KEY, api_host="https://stg.bionemo.ngc.nvidia.com/v1")

    test_smi = "CN(C)CCC1=CNC2=C1C(=CC=C2)OP(=O)(O)O"
    if random_protein:
        test_protein_seq = make_random_protein(3)
    else:
        test_protein_seq = "MSLK"
    diffdock_ligand_file = './test_data/6a87_ligand.sdf'
    diffdock_protein_file = './test_data/6a87_protein_processed.pdb'
    tester = TestHelper(verbose, expected_exceptions)
    print("test_protein_seq: {}".format(test_protein_seq))

    print("\nTesting async calls.")
    tester.check_function(tester.expect_valid_correlation_id, api.esmfold_async, test_protein_seq)
    tester.check_function(tester.expect_valid_correlation_id, api.alphafold2_async, test_protein_seq)
    tester.check_function(
        tester.expect_valid_correlation_id, api.diffdock_async, diffdock_ligand_file, diffdock_protein_file
    )
    tester.check_function(tester.expect_valid_correlation_id, api.megamolbart_async, [test_smi], num_samples=1)
    tester.check_function(tester.expect_valid_correlation_id, api.openfold_async, test_protein_seq)
    tester.check_function(tester.expect_valid_correlation_id, api.msa_async, test_protein_seq, ['mgnify'])
    tester.check_function(tester.expect_valid_correlation_id, api.protgpt2_async)
    print("\nTesting task interaction")
    task_list = tester.check_function(tester.expect_nonempty_response, api.fetch_tasks)
    if task_list:
        # Test task status on first task in list
        tester.check_function(tester.expect_nonempty_response, api.fetch_task_status, task_list[0])

        print("\nAttempting to cancel all pending tasks.")
        for task in api.fetch_tasks():
            if task.status not in ['DONE', 'CANCELLED', 'ERROR']:
                print(
                    "Cancelling: {} {}. Result: {}".format(task.model_name, task.correlation_id, api.cancel_task(task))
                )
    else:
        print(TestHelper.BOLD + TestHelper.RED + "Listing tasks failed; skipping task cancellation." + TestHelper.END)
    # TODO: Test "delete task".
    print("\nTesting sync calls.")
    tester.check_function(tester.expect_nonempty_response, api.list_models)
    tester.check_function(tester.expect_nonempty_response, api.megamolbart_sync, [test_smi], num_samples=1)
    tester.check_function(tester.expect_nonempty_response, api.megamolbart_embeddings_sync, [test_smi])
    tester.check_function(tester.expect_nonempty_response, api.moflow_sync, test_smi, num_samples=1)
    tester.check_function(tester.expect_nonempty_response, api.openfold_sync, test_protein_seq)
    tester.check_function(tester.expect_nonempty_response, api.msa_sync, test_protein_seq, ['mgnify'])
    tester.check_function(tester.expect_nonempty_response, api.alphafold2_sync, test_protein_seq)
    tester.check_function(tester.expect_nonempty_response, api.esmfold_sync, test_protein_seq)
    tester.check_function(tester.expect_nonempty_response, api.protgpt2_sync)
    tester.check_function(tester.expect_nonempty_response, api.esm2_sync, [test_protein_seq], model='650m')
    tester.check_function(tester.expect_nonempty_response, api.esm2_sync, [test_protein_seq], model='3b')
    tester.check_function(tester.expect_nonempty_response, api.esm2_sync, [test_protein_seq], model='15b')
    tester.check_function(tester.expect_nonempty_response, api.esm1nv_sync, [test_protein_seq])
    tester.check_function(
        tester.expect_nonempty_response, api.diffdock_sync, diffdock_ligand_file, diffdock_protein_file
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to check python client functionality.')
    parser.add_argument('API_KEY', type=str, help='Staging NGC API Key.')
    parser.add_argument("-v", "--verbose", action="store_true", required=False, help='Prints responses and errors.')
    parser.add_argument(
        "-r",
        "--random_protein",
        action="store_true",
        required=False,
        help='Generate random protein for folding models.',
    )

    args = parser.parse_args()
    print("\n" + TestHelper.BOLD + TestHelper.YELLOW + "Checking unauthorized API calls:" + TestHelper.END)
    check_api("ASDF", verbose=args.verbose, expected_exceptions=[bionemoservice.error.AuthorizationError])
    print("\n" + TestHelper.BOLD + TestHelper.YELLOW + "Checking authorized API calls:" + TestHelper.END)
    check_api(args.API_KEY, random_protein=args.random_protein, verbose=args.verbose)
