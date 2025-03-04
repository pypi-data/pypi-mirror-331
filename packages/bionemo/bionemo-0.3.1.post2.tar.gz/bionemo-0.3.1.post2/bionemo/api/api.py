# Copyright (c) 2023-2024, NVIDIA CORPORATION.  All rights reserved.
"""
This is the BioNemoService Python Client module.

It contains the class BionemoClient, which is a python interface to the BioNemo Service.
The BioNemo Service is an inference-as-a-service developed by NVIDIA for deployment of
AI models in the biology and chemistry domains.
"""
import copy
import http
import io
import json
import os
import sys
import threading
import time
import warnings

from typing import Any, Callable, Dict, List, Optional, Set, Union

import h5py as h5
import numpy as np
import requests


from bionemo.api.error import ApiKeyNotSetError, BadRequestId, IncorrectParamsError
from bionemo.api.request_id import RequestId
from bionemo.api.response_handler import ResponseHandler
from bionemo.api.task_tracker import log_request_status, set_request_log_file
from bionemo.api.version import __version__

if sys.version_info.minor < 8:
    from typing_extensions import Literal
else:
    from typing import Literal

MAX_CONNECTION_RETRIES = 3
REQUESTS_TIMEOUT_SECS = 1200

# used by generate_future and generate_multiple only
MAX_CONCURRENT_HTTP_REQUESTS = 3
DEFAULT_BINARY_DATA_TYPE = "npz"

# make sure all sessions on single thread to minimize TCP reconnections
_thread_context = threading.local()
_thread_context.connection_lifetime = 0


def mark_cli(func: Callable) -> Callable:
    """Marks a function to be part of the commandline interface.

    If a function is decorated with @mark_cli then it will be part of the Command-line Interface.

    To read about the commandline interface (CLI) see `bionemo/cli/readme.md`

    Args:
        func : function to mark.
    """
    func.is_decorated = True
    return func


def create_session():
    """Create session so that TCP connection does not reset, reducing handshake latency.

    Returns:
        requests.Session: a requests Session instance
    """
    session = requests.Session()
    session.mount(
        "https://",
        requests.adapters.HTTPAdapter(max_retries=MAX_CONNECTION_RETRIES),  # noqa missing import
    )
    return session


def get_session() -> requests.Session:
    """Construct a persistent request session if necessary and return.

    Restarts the session if 5 minutes have passed since the last invocation. If ~10 minutes passes, the
    connection to the server tends to break, leaving the client hanging.
    """
    SESSION_RESTART_INTERVAL_SECONDS: int = 300
    current_time: float = time.time()

    session_exists: bool = hasattr(_thread_context, "session") and hasattr(_thread_context, "connection_lifetime")

    # The short circuit here is important, if the session doesn't exist neither does connection lifetime.
    should_create_session: bool = (
        not session_exists or current_time - _thread_context.connection_lifetime > SESSION_RESTART_INTERVAL_SECONDS
    )

    if should_create_session:
        _thread_context.session = create_session()

    _thread_context.connection_lifetime = current_time
    return _thread_context.session


class BionemoClient:
    """
    A python client to request inference from the BioNemoService.

    Some models (like MegaMolBART) are synchronous and return an immediate result.  Others
    (like MoFlow) are asynchronous i.e. they return a value that can be used to find the
    result once it's ready.

    This class provides a MODEL_sync() call for all supported models, as well
    as a MODEL_async() call for each asynchronous model.  When the caller
    is ready to retrieve the results of an asynchronous call it should call the
    fetch_result() method, passing it the value returned by the MODEL()_async call.
    """

    def __init__(
        self,
        api_key=None,
        org_id=None,
        api_host=None,
        timeout_secs=REQUESTS_TIMEOUT_SECS,
        do_logging=False,
        log_file_path=None,
        log_file_append=True,
    ):
        """Construct an client instance.

        Args:
            api_key (str): The user API key necessary to access the service.
            org_id (str): The organization ID of the user.
            api_host (str): The URL to the backend service API.
            timeout_secs (int): The timeout duration for all requests in seconds. Defaults to 1200 seconds.
            do_logging (bool, Optional): Set to True to enable logging. Defaults to False.
            log_file_path (str, Optional): If logging is enabled this specifies the location of the log file.
                If logging is enabled but log_file_path is not set a tempfile will be used.
            log_file_append (bool): If logging is enabled and log_file_append is True then the log file
                will be appended to.  If logging is enabled and log_file_append is False then the log file
                will be overwritten.  Defaults to True.

        Raises:
            error.ApiKeyNotSetError: if no API key is set.

        If specified, the log file will contain a timestamp and the request information: correlation ID,
        action performed, name of the model and status of the request.

        Note that not all calls result in a log entry - get_smiles(), get_uniprot() and list_models() do
        not log anything.  fetch_tasks() will log the status of all existing tasks, in addition to returning
        task status.
        """
        self.api_key = api_key if api_key is not None else os.getenv("NGC_API_KEY")
        if not self.api_key:
            raise ApiKeyNotSetError(
                "API KEY is not set. Please pass api_key when instantiating BionemoClient"
                " or do'export NGC_API_KEY=<your_ngc_api_key>'"
            )

        self.org_id = org_id if org_id is not None else os.getenv("NGC_ORG_ID")
        # TODO: Understand whether ORG ID use will be necessary in production.
        # if not self.org_id:
        #     warnings.warn(
        #         "ORG ID is not set. If you have one and would like to set it, please pass org_id"
        #         " when instantiating BionemoClient do 'export NGC_ORG_ID=<your_ngc_org_id>'"
        #     )

        self.api_host = api_host if api_host is not None else "https://api.bionemo.ngc.nvidia.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"python-client:{__version__}",
        }
        if self.org_id:
            self.headers["Organization-ID"] = self.org_id
        self.timeout_secs = timeout_secs

        # Don't check this until after self.api_key and self.api_host have been set.
        # Here we call list_models as a proxy for key verification. If this fails,
        # list_models will raise an exception with the correct response from the server.
        self.list_models()
        set_request_log_file(do_logging, file_path=log_file_path, append=log_file_append)

    @mark_cli
    def verify_key(self):
        """Verify the API key.

        Returns:
            bool: True if the API_KEY passed to the constructor is valid, False otherwise.
        """
        try:
            # Why list_models()? It's fast, doesn't require any parameters and doesn't change the state
            # of the users data on the server.
            _ = self.list_models()
            return True
        except Exception:  # noqa
            return False

    @mark_cli
    def list_models(self):
        """List available models for inference.

        Returns:
            List: A list of available models and their API methods.
        """
        url = f"{self.api_host}/models"

        response = get_session().get(url, headers=self.headers, timeout=self.timeout_secs)
        ResponseHandler.handle_response(response)
        return response.json()["models"]

    @mark_cli
    def get_uniprot(self, uniprot_id: str):
        """Get amino acid sequence by UniProt ID.

         Args:
            uniprot_id (str): A UniProt protein ID.

        Returns:
            str: The corresponding amino acid sequence.

        """
        headers = self._setup_headers()
        url = f"{self.api_host}/uniprot/{uniprot_id}"
        response = get_session().get(
            url,
            headers=headers,
            timeout=self.timeout_secs,
            stream=False,
        )

        ResponseHandler.handle_response(response)
        return json.loads(response.content)

    @mark_cli
    def get_smiles(self, pubchem_cid: str):
        """Get SMILES from PubChem CID.

         Args:
            pubchem_cid (str): A PubChem CID.

        Returns:
            str: The corresponding SMILES string.

        """
        headers = self._setup_headers()
        url = f"{self.api_host}/pubchem/{pubchem_cid}"
        response = get_session().get(
            url,
            headers=headers,
            timeout=self.timeout_secs,
            stream=False,
        )
        ResponseHandler.handle_response(response)
        return json.loads(response.content)

    def _setup_headers(self, return_type=None):
        """Copy self.headers, add logging & return type settings as needed.

        Args:
            return_type (str): The expected return type from the request

        Returns:
            Dict: Header for HTML request.
        """
        headers = copy.copy(self.headers)
        if return_type == "stream":
            headers["x-stream"] = "true"
        return headers

    def _wait_for_response(
        self,
        py_request_id: RequestId,
    ):
        """Wait for a response from the model, polling periodically.

        The async BioNeMo calls require that you poll a particular URL for the response.
        Construct that URL from the request ID (model:correlation_id) and wait for it
        to return something.

        Args:
            py_request_id (RequestId): Everything we know about this request.

        Returns:
            Dict: The loaded JSON request response

        Raises:
            ValueError: If the model response is anything other than status 200 (OK) or
                        if the task was cancelled or had an inference error.
            requests.Timeout: If the service doesn't respond in time.
        """
        correlation_id = py_request_id.correlation_id
        url = f"{self.api_host}/task/{correlation_id}"

        starting_time = time.time()
        headers = self._setup_headers()
        tmo = py_request_id.timeout if py_request_id.timeout else self.timeout_secs
        while True:
            response = get_session().get(url, headers=headers)
            if response.ok:
                status_result = json.loads(response.content)
            else:
                raise ValueError(
                    f"Error in fetching request {url}. Status code: {response.status_code}"
                    f"\nResponse: {response.content}"
                )
            log_request_status(
                py_request_id.correlation_id,
                "check_request_status",
                py_request_id.model_name,
                status_result["control_info"]["status"],
            )
            if status_result["control_info"]["status"] in ["DONE", "CANCEL", "ERROR"]:
                break
            time.sleep(5)  # waiting for the prediction from BioNeMo Server

            if time.time() - starting_time > tmo:
                raise requests.Timeout(f"Timed out waiting for response for {py_request_id.correlation_id}")

        if status_result["control_info"]["status"] in ["CANCEL", "ERROR"]:
            raise ValueError(
                "No output from task with correlation id {} due to task state: {}"
                "\n Detailed response: {}".format(
                    status_result["control_info"]["correlation_id"],
                    status_result["control_info"]["status"],
                    status_result["response"],
                )
            )
        return status_result

    @staticmethod
    def _process_response(
        response,
        return_type=None,
    ):
        """Process a raw response.

        Args:
            response (requests.models.Response): A requests response.
            return_type (str): The expected payload type in the response.

        Returns:
            Dict (JSON): A post-processed response
        """
        if return_type == "stream":
            ResponseHandler.handle_response(response, stream=True)
            return response.iter_lines()
        if return_type in ["async", "future"]:
            return response
        if return_type == "text":
            ResponseHandler.handle_response(response)
            return ResponseHandler.post_process_generate_response(response, True)
        ResponseHandler.handle_response(response)
        return ResponseHandler.post_process_generate_response(response, False)

    def _submit_request(
        self,
        model_name: str,
        url: str,
        data,
        files,
        timeout=None,
    ):
        """Construct and post() the request.

        Args:
            model_name (str): the name of the requested inference model
            url (str): the API endpoint to which the request will be sent
            data (Dict(JSON)): the data payload
            files (Dict(JSON)): the files payload, if any
            timeout (int): the timeout duration in seconds. A timeout results in a
                requests.exceptions.Timeout exception raised.
        """
        headers = self._setup_headers()

        response = get_session().post(
            url,
            headers=headers,
            json=data,
            timeout=self.timeout_secs,
            stream=False,
            files=files,
            allow_redirects=False,
        )
        processed_response = BionemoClient._process_response(response)
        # status is unknown at this point.
        log_request_status(processed_response["correlation_id"], "request_inference", model_name, "UNKNOWN")
        return RequestId(model_name, processed_response["correlation_id"], timeout)

    #
    # Syncronous (blocking) calls.
    #
    @mark_cli
    def megamolbart_embeddings_sync(
        self,
        smis: List[str],
    ):
        """Request MegaMolBart embeddings inference, wait for the response.

        MegaMolBart is a generative model developed by NVIDIA to produce novel small molecules given
        an input seed molecule.
        https://github.com/NVIDIA/MegaMolBART

        This function will request embeddings for the input SMILES from MegaMolBart.
        Approximate inference duration: < 0.1 second.

        Args:
            smis (List[str]): List of SMILES strings for which embeddings will be generated.
                              Each string may be 1 to 510 characters.

        Returns:
            List[numpy.ndarray]: A list of embeddings, one for each input.
        """
        url = f"{self.api_host}/molecule/megamolbart/embeddings"
        data = {
            "smis": smis,
            "format": DEFAULT_BINARY_DATA_TYPE,
        }
        headers = self._setup_headers()

        response = get_session().post(
            url,
            headers=headers,
            json=data,
            timeout=self.timeout_secs,
            stream=False,
        )

        ResponseHandler.handle_response(response)
        response_list = BionemoClient._decode_embedding_response(response.content, DEFAULT_BINARY_DATA_TYPE)

        return [x["embeddings"] for x in response_list]

    @mark_cli
    def molmim_embeddings_sync(
        self,
        smis: List[str],
    ) -> List[np.ndarray]:
        """Request MolMIM embeddings inference, wait for the response.

        MolMIM is a generative model developed by NVIDIA to produce novel small molecules given
        an input seed molecule.
        https://arxiv.org/abs/2208.09016

        This function will request embeddings for the input SMILES from MolMIM.
        Approximate inference duration: < 0.1 second.

        The dimensionality of MolMIM latent space is 512.

        Args:
            smis (List[str]): List of SMILES strings for which embeddings will be generated.
                              Each string may be 1 to 510 characters.

        Returns:
            List[numpy.ndarray]: A list of embeddings, one for each input. Each array has size 512
        """
        url = f"{self.api_host}/molecule/molmim/embeddings"
        data = {
            "smis": smis,
            "format": DEFAULT_BINARY_DATA_TYPE,
        }
        headers = self._setup_headers()

        response = get_session().post(
            url,
            headers=headers,
            json=data,
            timeout=self.timeout_secs,
            stream=False,
        )

        ResponseHandler.handle_response(response)

        parsed_response = BionemoClient._decode_embedding_response(response.content, DEFAULT_BINARY_DATA_TYPE)[0][
            'embeddings'
        ]

        return [parsed_response[i, :] for i in range(parsed_response.shape[0])]

    def molmim_decode_sync(self, embeddings: List[np.ndarray]) -> List[str]:
        """Request MolMIM decoding of embeddings, wait for the response.

        MolMIM is a generative model developed by NVIDIA to produce novel small molecules given
        an input seed molecule.
        https://arxiv.org/abs/2208.09016

        This function will decode latent space embeddings into smiles strings. It is possible for decoding to fail
        to generate a valid smiles string - in these cases, an empty string is returned.

        The dimensionality of MolMIM latent space is 512, so each embedding must be that size.

        Args: embeddings (List[np.ndarray]): List of embeddings, where each embedding has size 512 to match the
            latent space of MolMIM.

        Returns:
            List[str]: List of SMILES strings with length equal to the number of embeddings.
        """
        molmim_latent_space_ndims = 512
        url = f"{self.api_host}/molecule/molmim/decoder"

        headers = self._setup_headers()

        for i, embedding in enumerate(embeddings):
            if embedding.size != molmim_latent_space_ndims:
                raise ValueError(
                    f"embedding {i} of {len(embeddings)} has size {embedding.size}, must be {molmim_latent_space_ndims}"
                )
        stacked_embeddings = np.expand_dims(
            np.vstack([embedding.flatten() for embedding in embeddings]).astype(np.float32), axis=0
        )
        with io.BytesIO() as buffer:
            np.savez(buffer, embeddings=stacked_embeddings)  # noqa numpy typing mismatch
            buffer.seek(0)

            response = get_session().post(
                url,
                headers=headers,
                files={"embeddings": ("embeddings.npz", buffer)},
                timeout=self.timeout_secs,
                stream=False,
            )

        ResponseHandler.handle_response(response)
        return json.loads(response.content.decode())

    def _guided_mol_generate_dispatch(
        self,
        model: str,
        smi: str,
        property_name: str,
        iterations: int,
        algorithm: str = "CMA-ES",
        num_samples: int = 20,
        particles: int = 20,
        min_similarity: float = 0.7,
        timeout=None,
    ):
        url = f"{self.api_host}/molecule/{model}/generate"

        scoring_algorithms: Set[str] = {"logP", "plogP", "QED"}
        if property_name not in scoring_algorithms:
            raise ValueError(f"Got property name {property_name}, must be one of {scoring_algorithms}")
        if particles < num_samples:
            raise ValueError(f"particles({particles}) must be greater or equal to num_samples({num_samples})")

        request_id = self._submit_request(
            model,
            url,
            data={
                "algorithm": algorithm,
                "smi": smi,
                "iterations": iterations,
                "property_name": property_name,
                "particles": particles,
                "minimize": False,
                "min_similarity": min_similarity,
                "source": "api",
                "num_samples": num_samples,
            },
            files=None,
            timeout=timeout if timeout is not None else self.timeout_secs,
        )
        return request_id

    def molmim_guided_generate_async(
        self,
        smi: str,
        property_name: str,
        iterations: int,
        algorithm: str = "CMA-ES",
        num_samples: int = 20,
        particles: int = 20,
        min_similarity: float = 0.7,
        timeout=None,
    ) -> RequestId:
        """Request MolMIM guided molecule generation based on a desired property.

        This endpoint uses the CMA-ES algorithm to iteratively query MolMIM to provide generated molecules selected
        for high scores on a given property. The properties currently supported are QED score and penalized logP

        Args:
            smi: Seed smiles, for which new candidates will be generated.
            property_name: Scoring function - one of ("plogp", or "QED")
            iterations: Number of iterations of optimization to perform
            algorithm: "CMA-ES" is currently the only option
            num_samples: Number of candidates to generate
            particles: Number of molecules to generate each intermediate step. Must be at least 20 and >= num_samples
            min_similarity: Scores will be penalized for molecules that do not hit this similarity threshold.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.
        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        return self._guided_mol_generate_dispatch(
            'molmim', smi, property_name, iterations, algorithm, num_samples, particles, min_similarity, timeout
        )

    def molmim_guided_generate_sync(
        self,
        smi: str,
        property_name: str,
        iterations: int,
        algorithm: str = "CMA-ES",
        num_samples: int = 20,
        particles: int = 20,
        min_similarity: float = 0.7,
        timeout: Optional[int] = None,
    ) -> Dict[str, List]:
        """Request MolMIM guided molecule generation based on a desired property and wait for result.

        This endpoint uses the CMA-ES algorithm to iteratively query MolMIM to provide generated molecules selected
        for high scores on a given property. The properties currently supported are QED score and penalized logP


        Args:
            smi: Seed smiles, for which new candidates will be generated.
            property_name: Scoring function - one of ("plogp", or "QED")
            iterations: Number of iterations of optimization to perform
            algorithm: "CMA-ES" is currently the only option
            num_samples: Number of candidates to generate
            particles: Number of molecules to generate each intermediate step. Must be at least 20 and >= num_samples
            min_similarity: Scores will be penalized for molecules that do not hit this similarity threshold.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.
        Returns:
            Dict[List]: A dictionary containing MolMIM output for the input seed.
                The dictionary has keys "generated_molecules" and "scores". Each key contains
                a list of length num_samples. The scores are the score of the property selected.
        """

        py_request_id = self._guided_mol_generate_dispatch(
            'molmim', smi, property_name, iterations, algorithm, num_samples, particles, min_similarity, timeout
        )
        return self._wait_for_generation(py_request_id)

    def molmim_unguided_generate_async(
        self, smi: str, num_samples: int, scaled_radius: float = 1.0, timeout: Optional[int] = None
    ):
        """Request MolMIM generation inference without waiting for inference results.

        Approximate inference duration: ~1 second.

        Args:
            smi (str): SMILES molecule sequence. 1 - 512 characters.
            num_samples (int): Number of sampled molecules to be returned as SMILES.
                Minimum value of 1.
            scaled_radius (float): Adjust to control the structural output of MolMIM
                generated molecules. Higher values generate more diverse
                molecules, while lower values generate more similar compounds to the seed.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        data = {"smi": f"{smi}", "num_samples": num_samples, "scaled_radius": scaled_radius, "algorithm": "none"}
        url = f"{self.api_host}/molecule/molmim/generate"
        return self._submit_request("molmim", url, data, None, timeout=timeout)

    def molmim_unguided_generate_sync(
        self, smi: str, num_samples: int, scaled_radius: float = 1.0, timeout: Optional[int] = None
    ):
        """Request MolMIM unguided generation inference, wait for result.

        Approximate inference duration: ~1 second.

        Args:
            smi (str): SMILES molecule sequence. 1 - 512 characters.
            num_samples (int): Number of sampled molecules to be returned as SMILES.
                Minimum value of 1.
            scaled_radius (float): Adjust to control the structural output of MolMIM
                generated molecules. Higher values generate more diverse
                molecules, while lower values generate more similar compounds to the seed.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.
        Returns:
            Dict[List]: A dictionary containing MolMIM output for the input seed.
                The dictionary has keys "generated_molecules" and "scores". Each key contains
                a list of length num_samples. The scores are tanimoto similarity to the seed molecule.
        """
        py_request_id = self.molmim_unguided_generate_async(smi, num_samples, scaled_radius, timeout)
        return self._wait_for_generation(py_request_id)

    def esm2_sync(
        self,
        sequences: List[str],
        model: Literal["650m", "3b", "15b"] = "650m",
    ):
        """Request ESM2 inference, wait for the response.

        Evolutionary Scale Modeling 2 (ESM2) is a protein-to-embedding generator developed
        by Facebook AI Research.
        https://github.com/facebookresearch/esm

        Approximate inference time: <1 second.

        Args:
            sequences (List[str]): List of strings in the protein alphabet for which embeddings
                                   will be generated. Each string should be 1 to 1024 characters.
            model (str): Which ESM 2 model size to use. Options are {"650m", "3b", "15b"}

        Returns:
            List[Dict[numpy.array]]: A list of outputs corresponding to the input list.
                Each list entry is a dict that contains following keys:
                'representation', 'tokens', 'logits' and 'embeddings', all of which contain
                a numpy array. Each item in the output list corresponds to the input list item.
        """
        valid_models: Set[str] = {"650m", "3b", "15b"}
        if model not in valid_models:
            raise ValueError(f"Invalid model {model}. Options are {valid_models}")

        url = f"{self.api_host}/protein-embedding/esm2-{model.lower()}/embeddings"
        data = {
            "sequence": sequences,
            "format": DEFAULT_BINARY_DATA_TYPE,
        }
        headers = self._setup_headers()

        response = get_session().post(
            url,
            headers=headers,
            json=data,
            timeout=self.timeout_secs,
            stream=False,
        )
        ResponseHandler.handle_response(response)
        response_data = BionemoClient._decode_embedding_response(response.content, DEFAULT_BINARY_DATA_TYPE)
        #
        # For esm2, there is padding in the tokens that needs to be removed.
        # For each padded index in "tokens", we must also remove the corresponding
        # indexes in all other arrays.
        # TODO(trvachov): fetch padding values from API rather than hard-coding 0,1,2)
        for response in response_data:
            keep_index_list = [i for i, token in enumerate(response["tokens"]) if token not in [0, 1, 2]]
            response["tokens"] = response["tokens"][keep_index_list]
            response["logits"] = response["logits"][keep_index_list]
            response["representations"] = response["representations"][keep_index_list]
        return response_data

    @mark_cli
    def esm1nv_sync(
        self,
        sequences: List[str],
    ):
        """Request ESM1nv inference, wait for response.

        ESM1nv is an embedding generation model developed by NVIDIA, based on prior work
        by Facebook AI Research's ESM-1b model.

        Approximate infernece time: <0.1 second.

        Args:
            sequences (List[str]): List of strings in the protein alphabet for which embeddings
                                   will be generated. Each string should be 1 to 512 characters.

        Returns:
            List[numpy.ndarray]: A list of embeddings, one for each input.
        """
        url = f"{self.api_host}/protein-embedding/esm1nv/embeddings"
        data = {
            "sequence": sequences,
            "format": DEFAULT_BINARY_DATA_TYPE,
        }
        headers = self._setup_headers()

        response = get_session().post(
            url,
            headers=headers,
            json=data,
            timeout=self.timeout_secs,
            stream=False,
        )

        ResponseHandler.handle_response(response)
        response_list = BionemoClient._decode_embedding_response(response.content, DEFAULT_BINARY_DATA_TYPE)
        return [x["embeddings"] for x in response_list]

    #
    # Asynchronous calls.  Calling
    #
    #     task_id = MODEL_async(...)
    #
    # will return a value that uniquely identifies that request.  Call
    #
    #     fetch_task_status(task_id)
    #
    # to see if the task is ready.  Once it's ready, call
    #
    #     results = fetch_result(task_id)
    #
    # to retrieve the results.
    #
    # Note, the BionemoClient keeps track of asynchronous tasks using a "correlation_id", which
    # is a UUID e.g. 285bc36c-00a9-40eb-acdf-62ecaf2c378b
    #
    # In this python API, we defined a "py_request_id" which is a combination of everything we
    # know about a request: model name, correlation id, call-specific timeout (if used) and
    # status (if known).  The correlation ID is a UUID, the model name is used in identifying
    # how to unwrap the JSON response of certain models.
    @mark_cli
    def fetch_result(self, py_request_id: RequestId):
        """Get inference results from request id.

        Given a request ID (modelname:correlation_id) get the
        results from the server and dispatch them to the appropriate parser, returning
        the parsed result.

        Args:
            py_request_id (RequestId): Everything we know about this request.

        Returns:
            (multiple types): The result of the model, which is a different type for each model.

        Raises:
            ValueError: If py_request_id is invalid.
        """
        model = py_request_id.model_name

        # Wait for results to become available.
        start_time = time.time()
        while self.fetch_task_status(py_request_id) in ["CREATED", "PROCESSING", "SUBMITTED"]:
            if time.time() - start_time > self.timeout_secs:
                raise requests.Timeout(f"Timed out waiting for results from {py_request_id}")
            time.sleep(1)

        # Get the results, farm out parsing, return results.
        # TODO: Could use a dispatch table here.
        if model == "alphafold2":
            return self._wait_for_alphafold2(py_request_id)
        if model == "diffdock":
            return self._wait_for_diffdock(py_request_id)
        if model == "esmfold":
            return self._wait_for_esmfold(py_request_id)
        if model == "openfold":
            return self._wait_for_openfold(py_request_id)
        if model == 'msa':
            return self._wait_for_msa(py_request_id)
        if model == "protgpt2":
            return self._wait_for_simple_response(py_request_id)
        if model in {"moflow", "molmim", "megamolbart"}:
            return self._wait_for_generation(py_request_id)

        raise ValueError("Unsupported model " + model)

    def moflow_embeddings_sync(
        self,
        smis: List[str],
    ) -> List[np.ndarray]:
        """Request MoFlow embeddings inference, wait for the response.


        This function will request embeddings for the input SMILES from MoFlow.
        Approximate inference duration: < 0.1 second.

        The dimensionality of MoFlow latent space is 6800.

        Args:
            smis (List[str]): List of SMILES strings for which embeddings will be generated.
                              Each string may be 1 to 512 characters.

        Returns:
            List[numpy.ndarray]: A list of embeddings, one for each input. Each array has size 512
        """
        url = f"{self.api_host}/molecule/moflow/embeddings"
        data = {
            "smis": smis,
            "format": DEFAULT_BINARY_DATA_TYPE,
        }
        headers = self._setup_headers()

        response = get_session().post(
            url,
            headers=headers,
            json=data,
            timeout=self.timeout_secs,
            stream=False,
        )

        ResponseHandler.handle_response(response)

        parsed_response = BionemoClient._decode_embedding_response(response.content, DEFAULT_BINARY_DATA_TYPE)[0][
            'embeddings'
        ]

        return [parsed_response[i, :] for i in range(parsed_response.shape[0])]

    def moflow_decode_sync(self, embeddings: List[np.ndarray]) -> List[str]:
        """Request MoFlow decoding of embeddings, wait for the response.

        This function will decode latent space embeddings into smiles strings. It is possible for decoding to fail
        to generate a valid smiles string - in these cases, an empty string is returned.

        The dimensionality of MoFlow latent space is 6800, so each embedding must be that size.

        Args: embeddings (List[np.ndarray]): List of embeddings, where each embedding has size 512 to match the
            latent space of MoFlow.

        Returns:
            List[str]: List of SMILES strings with length equal to the number of embeddings.
        """
        moflow_latent_space_ndims: int = 6800
        url = f"{self.api_host}/molecule/moflow/decoder"

        headers = self._setup_headers()

        for i, embedding in enumerate(embeddings):
            if embedding.size != moflow_latent_space_ndims:
                raise ValueError(
                    f"embedding {i} of {len(embeddings)} has size {embedding.size}, must be {moflow_latent_space_ndims}"
                )
        stacked_embeddings = np.expand_dims(
            np.vstack([embedding.flatten() for embedding in embeddings]).astype(np.float32), axis=0
        )

        with io.BytesIO() as buffer:
            np.savez(buffer, embeddings=stacked_embeddings)  # noqa numpy typing mismatch
            buffer.seek(0)

            response = get_session().post(
                url,
                headers=headers,
                files={"embeddings": ("embeddings.npz", buffer)},
                timeout=self.timeout_secs,
                stream=False,
            )
        ResponseHandler.handle_response(response)
        return json.loads(response.content.decode())

    def moflow_unguided_generate_async(
        self,
        smi: str,
        num_samples: int = 1,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        """Request MoFlow generation inference without waiting for inference results.

        MoFlow is a generative model developed at Cornell University to produce novel molecules given an input seed
        molecule.
        https://arxiv.org/abs/2006.10137
        https://github.com/calvin-zcx/moflow

        Approximate inference duration: <1 second.

        Args:
            smi (str): SMILES molecule sequence. 1 - 512 characters.
            num_samples (int): Number of sampled molecules to be returned as SMILES.
                Minimum value of 1.
            scaled_radius (float): Adjust to control the structural output of MoFlow
                generated molecules. Higher values generate more complex and diverse
                molecules, while lower values generate more chemical valid compounds. Minimum value
                of 0.2.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        data = {
            "smi": f"{smi}",
            "num_samples": num_samples,
            "scaled_radius": scaled_radius,
            "algorithm": "none",
            "source": "api",
        }
        url = f"{self.api_host}/molecule/moflow/generate"
        return self._submit_request("moflow", url, data, None, timeout)

    def _wait_for_generation(self, py_request_id: RequestId) -> Dict[str, List]:
        """Wait for results from a call to molmim or moflow, parse results.

        Args:
            py_request_id (RequestId): Everything we know about this request.

        Returns:
            Dict[List]: A dict with keys "generated_molecules" and "scores".
                        Each key contains a list of length num_samples.
        """
        status_result = self._wait_for_response(py_request_id)
        #
        # Convert
        #  [
        #      {'generated_molecules':'abc', 'similarity':.9},
        #      {'generated_molecules':'xyz', 'similarity':.8},
        #      etc...
        #  ]
        # to
        #  {
        #      'generated_molecules':['abc', 'xyz'],
        #      'similarity':[.9, .8]
        #  }
        result = json.loads(status_result["response"])['samples']
        inverted: Dict[str, Any] = {"generated_molecules": [], "scores": []}
        for item in result:
            inverted["generated_molecules"].append(item["sample"])
            inverted["scores"].append(item["score"])
        return inverted

    def moflow_unguided_generate_sync(
        self,
        smi: str,
        num_samples: int = 1,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        """Request MoFlow generation inference, wait for the response.

        MoFlow is a generative model developed at Cornell University to produce novel molecules
        given an input seed molecule.
        https://arxiv.org/abs/2006.10137
        https://github.com/calvin-zcx/moflow

        Approximate inference duration: <1 second.

        Args:
            smi (str): SMILES molecule sequence. 1 - 512 characters.
            num_samples (int): Number of sampled molecules to be returned as SMILES.
                Minimum value of 1.
            scaled_radius (float): Adjust to control the structural output of MoFlow
                generated molecules. Higher values generate more complex and diverse
                molecules, while lower values generate more chemical valid compounds. Minimum value
                of 0.2.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            Dict[List]: A dictionary containing moflow output for the input seed.
                The dictionary has keys "generated_molecules" and "scores". Each key contains
                a list of length num_samples. The scores are tanimoto similarity to the seed molecule.
        """
        py_request_id = self.moflow_unguided_generate_async(smi, num_samples, scaled_radius, timeout)
        return self._wait_for_generation(py_request_id)

    def moflow_guided_generate_async(
        self,
        smi: str,
        property_name: str,
        iterations: int,
        algorithm: str = "CMA-ES",
        num_samples: int = 20,
        particles: int = 20,
        min_similarity: float = 0.7,
        timeout: Optional[int] = None,
    ):
        """Request MoFlow guided molecule generation based on a desired property.

        This endpoint uses the CMA-ES algorithm to iteratively query MoFlow to provide generated molecules selected
        for high scores on a given property. The properties currently supported are QED score and penalized logP

        Args:
            smi: Seed smiles, for which new candidates will be generated.
            property_name: Scoring function - one of ("plogp", or "QED")
            iterations: Number of iterations of optimization to perform
            algorithm: "CMA-ES"
            num_samples: Number of candidates to generate
            particles: Number of molecules to generate each intermediate step. Must be at least 20 and >= num_samples
            min_similarity: Scores will be penalized for molecules that do not hit this similarity threshold.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.
        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        return self._guided_mol_generate_dispatch(
            'moflow', smi, property_name, iterations, algorithm, num_samples, particles, min_similarity, timeout
        )

    def moflow_guided_generate_sync(
        self,
        smi: str,
        property_name: str,
        iterations: int,
        algorithm: str = "CMA-ES",
        num_samples: int = 20,
        particles: int = 20,
        min_similarity: float = 0.7,
        timeout: Optional[int] = None,
    ):
        """Request MoFlow guided molecule generation based on a desired property.

        This endpoint uses the CMA-ES algorithm to iteratively query MoFlow to provide generated molecules selected
        for high scores on a given property. The properties currently supported QED score and penalized logP

        Args:
            smi: Seed smiles, for which new candidates will be generated.
            property_name: Scoring function - one of ("plogp", or "QED")
            iterations: Number of iterations of optimization to perform
            algorithm: "CMA-ES"
            num_samples: Number of candidates to generate
            particles: Number of molecules to generate each intermediate step. Must be at least 20 and >= num_samples
            min_similarity: Scores will be penalized for molecules that do not hit this similarity threshold.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.
        Returns:
            Dict[List]: A dictionary containing moflow output for the input seed.
                The dictionary has keys "generated_molecules" and "scores". Each key contains
                a list of length num_samples.
        """
        py_request_id = self.moflow_guided_generate_async(
            smi, property_name, iterations, algorithm, num_samples, particles, min_similarity, timeout
        )
        return self._wait_for_generation(py_request_id)

    def moflow_sync(
        self,
        smi: str,
        num_samples: int = 1,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        warnings.warn(
            "moflow_sync is deprecated and will be removed in a future release. Please use "
            "moflow_unguided_generate_sync",
            FutureWarning,
        )
        return self.moflow_unguided_generate_sync(smi, num_samples, scaled_radius, timeout)

    moflow_sync.__doc__ = moflow_sync.__doc__

    def moflow_async(
        self,
        smi: str,
        num_samples: int = 1,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        warnings.warn(
            "moflow_async is deprecated and will be removed in a future release. Please use "
            "moflow_unguided_generate_async",
            FutureWarning,
        )
        return self.moflow_unguided_generate_async(smi, num_samples, scaled_radius, timeout)

    moflow_async.__doc__ = moflow_unguided_generate_async.__doc__

    def megamolbart_unguided_generate_async(
        self,
        smi: str,
        num_samples: int = 10,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        """Request MegaMolBart inference without waiting for inference results.

        MegaMolBart is a generative model developed by NVIDIA to produce novel small molecules given
        an input seed molecule.
        https://github.com/NVIDIA/MegaMolBART

        Approximate inference duration: 10-60 seconds.

        Args:
            smi (str): SMILES string to use as a seed in novel molecule generation. 1 - 512 characters.
            num_samples (int): The number of molecules to generate per seed molecule.
                Minimum value of 1.
            scaled_radius (float): The radius in feature-space from which new molecules
                will be sampled. Minimum value of 1.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        url = f"{self.api_host}/molecule/megamolbart/generate"
        data = {
            "smi": smi,
            "num_samples": num_samples,
            "scaled_radius": scaled_radius,
        }
        return self._submit_request("megamolbart", url, data, None, timeout)

    def megamolbart_unguided_generate_sync(
        self,
        smi: str,
        num_samples: int = 10,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        """Request MegaMolBart inference, wait for the response.

        MegaMolBart is a generative model developed by NVIDIA to produce novel small molecules given
        an input seed molecule.
        https://github.com/NVIDIA/MegaMolBART

        Approximate inference duration: 10-60 seconds.

        Args:
            smi (str): SMILES string to use as a seed in novel molecule generation. 1 - 512 characters.
            num_samples (int): The number of molecules to generate per seed molecule.
                Minimum value of 1.
            scaled_radius (float): The radius in feature-space from which new molecules
                will be sampled. Minimum value of 1.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            Dict[List]: A dictionary containing MegaMolBart output for the input seed.
                The dictionary has keys "generated_molecules" and "scores". Each key contains
                a list of length num_samples. The scores are tanimoto similarity to the seed molecule.
        """
        rqst_id = self.megamolbart_unguided_generate_async(smi, num_samples, scaled_radius, timeout)
        return self._wait_for_generation(rqst_id)

    def megamolbart_sync(
        self,
        smi: str,
        num_samples: int = 10,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        warnings.warn(
            "megamolbart_sync is deprecated and will be removed in a future release. Please use "
            "megamolbart_unguided_generate_sync",
            FutureWarning,
        )
        return self.megamolbart_unguided_generate_sync(smi, num_samples, scaled_radius, timeout)

    megamolbart_sync.__doc__ = megamolbart_unguided_generate_sync.__doc__

    def megamolbart_async(
        self,
        smi: str,
        num_samples: int = 10,
        scaled_radius: float = 1.0,
        timeout=None,
    ):
        warnings.warn(
            "megamolbart_async is deprecated and will be removed in a future release. Please use "
            "megamolbart_unguided_generate_async",
            FutureWarning,
        )
        return self.megamolbart_unguided_generate_async(smi, num_samples, scaled_radius, timeout)

    megamolbart_async.__doc__ = megamolbart_unguided_generate_async.__doc__

    @mark_cli
    def msa_async(
        self,
        sequence: str,
        databases: List[str],
        algorithm: str = "jackhmmer",
        output_format: str = "a3m",
        e_value: float = 0.0001,
        bit_score: Optional[float] = None,
        iterations: int = 1,
        timeout=None,
    ):
        """Request MSA alignment without waiting for inference results.

        Currently we support Jackhmmer for alignments. See http://hmmer.org/ for more information.

        Approximate inference duration: 2-15 minutes.

        Args:
            sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 2000 characters.
            databases (List[str]): List of databases to search. Currently supported:
                mgnify | smallbfd | uniref90 | uniref100 | uniref50
            algorithm (str): Algorithm to use. Currently only "jackhmmer" is supported
            output_format (str): Alignment format. "a3m" and "sto" are supported.
            e_value (float): e-value. See jackhmmer docs for more details
            bit_score (Optional[float]): bit score. See jackhmmer docs for more details
            iterations (int): iterations. See jackhmmer docs for more details
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        supported_algorithms = {"jackhmmer"}
        if algorithm not in supported_algorithms:
            raise ValueError(f"Unsupported algorithm {algorithm}, options are {supported_algorithms}")

        url = f"{self.api_host}/msa-calculation/{algorithm}/align"
        data = {
            'sequence': sequence,
            'databases': databases,
            'format': output_format,
            'e_value': e_value,
            'iterations': iterations,
            'source': 'api',
        }

        if bit_score is not None:
            data['bit_score'] = bit_score

        return self._submit_request('msa', url, data, None, timeout=timeout)

    def _wait_for_msa(
        self,
        py_request_id: RequestId,
    ):
        """Wait for results from a call to msa_async, parse results.

        Args:
            py_request_id (RequestId): a string wih the format 'modelname:correlation_id'

        Returns:
            str: A list of dictionaries containing alignment data and metadata
        """
        status_result = self._wait_for_response(py_request_id)
        return json.loads(status_result["response"])["alignments"]

    @mark_cli
    def msa_sync(
        self,
        sequence: str,
        databases: List[str],
        algorithm: str = "jackhmmer",
        output_format: str = "a3m",
        e_value: float = 0.0001,
        bit_score: Optional[float] = None,
        iterations: int = 1,
        timeout=None,
    ):
        """Request MSA alignment, wait for the response.

        Currently we support Jackhmmer for alignments. See http://hmmer.org/ for more information.

        Approximate inference duration: 2-15 minutes.

        Args:
            sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 2000 characters.
            databases (List[str]): List of databases to search. Currently supported:
                mgnify | smallbfd | uniref90 | uniref100 | uniref50
            algorithm (str): Algorithm to use. Currently only "jackhmmer" is supported
            output_format (str): Alignment format. "a3m" and "sto" are supported.
            e_value (float): e-value. See jackhmmer docs for more details
            bit_score (Optional[float]): bit score. See jackhmmer docs for more details
            iterations (int): iterations. See jackhmmer docs for more details
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            str: A list of dictionaries containing alignment data and metadata
        """
        rqst_id = self.msa_async(
            sequence, databases, algorithm, output_format, e_value, bit_score, iterations, timeout
        )
        return self._wait_for_msa(rqst_id)

    @mark_cli
    def openfold_async(
        self,
        protein_sequence: str,
        msas: Optional[Union[str, List[str]]] = None,  # File names from which MSAs are read.
        use_msa: bool = True,
        relax_prediction: bool = True,
        timeout=None,
    ):
        """Request OpenFold inference without waiting for inference results.

        OpenFold is an open source protein structure prediction model, similar in
        feature-set and performance to AlphaFold2.
        https://github.com/aqlaboratory/openfold

        Approximate inference duration: 2-10 minutes.

        Args:
            protein_sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 2000 characters.
            msas (Optional[Union[str, List[str]]]): Paths to multi-sequence alignment (MSA) files in .a3m format.
                If use_msa=True, these files will be uploaded and used during
                protein folding.
            use_msa (bool): If True, the specified msas file will be uploaded and
                used as input to the folding model. If False, MSAs will
                be auto-generated, however this typically yields less
                accurate results.
            relax_prediction (bool): If True, a geometry-relaxation step will be
                applied to the folded output. This is performed
                with a short molecular dynamics simulation.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        url = f"{self.api_host}/protein-structure/openfold/predict"
        data = {}
        if isinstance(msas, str):
            msas = [msas]

        files = [
            ("sequence", (None, protein_sequence)),
        ]

        if msas is None:
            files.append(('msas', None))
        else:
            for msa in msas:
                files.append(('msas', (msa, open(msa, "rb"))))

        files.extend(
            [
                ("use_msa", (None, str(use_msa).lower())),
                ("relax_prediction", (None, str(relax_prediction).lower())),
            ]
        )
        return self._submit_request("openfold", url, data, files, timeout)

    def _wait_for_openfold(
        self,
        py_request_id: RequestId,
    ):
        """Wait for results from a call to openfold_async, parse results.

        Args:
            py_request_id (RequestId): a string wih the format 'modelname:correlation_id'

        Returns:
            str: A string representing the folded protein geometry in Protein Data Bank (PDB) format.
        """
        status_result = self._wait_for_response(py_request_id)
        return json.loads(status_result["response"])["pdbs"][0]

    @mark_cli
    def openfold_sync(
        self,
        protein_sequence: str,
        msas: Optional[Union[str, List[str]]] = None,  # Paths to MSA files.
        use_msa: bool = True,
        relax_prediction: bool = True,
        timeout=None,
    ):
        """Request OpenFold inference, wait for the response.

        OpenFold is an open source protein structure prediction model, similar in
        feature-set and performance to AlphaFold2.
        https://github.com/aqlaboratory/openfold

        Approximate inference duration: 2-10 minutes.

        Args:
            protein_sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 2000 characters.
            msas (Optional[Union[str, List[str]]]): Paths to multi-sequence alignment (MSA) files in .a3m format.
                If use_msa=True, these files will be uploaded and used during
                protein folding.
            use_msa (bool): If True, the specified msas file will be uploaded and
                used as input to the folding model. If False, MSAs will
                be auto-generated, however this typically yields less
                accurate results.
            relax_prediction (bool): If True, a geometry-relaxation step will be
                applied to the folded output. This is performed
                with a short molecular dynamics simulation.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            str: A string representing the folded protein geometry in Protein Data Bank (PDB) format.
        """
        rqst_id = self.openfold_async(protein_sequence, msas, use_msa, relax_prediction, timeout)
        return self._wait_for_openfold(rqst_id)

    @mark_cli
    def alphafold2_async(
        self,
        protein_sequence: Union[str, List[str]],
        msas: Optional[Union[str, List[str]]] = None,
        relax_prediction: bool = True,
        model_preset: str = 'monomer',
        timeout=None,
    ):
        """Request AlphaFold2 inference, without waiting for inference results.

        AlphaFold2 is the second generation protein folding model developed by
        DeepMind.
        https://www.nature.com/articles/s41586-021-03819-2
        https://github.com/deepmind/alphafold

        Approximate inference duration: 5-30 minutes.

        Args:
            protein_sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 3000 characters.
            msas (Optional[Union[str, List[str]]]): Paths to multi-sequence alignment (MSA) files in .a3m format.
                If use_msa=True, these files will be uploaded and used during
                protein folding.
            use_msa (bool): If True, the specified msas file will be uploaded and
                used as input to the folding model. If False, MSAs will
                be auto-generated, however this typically yields less
                accurate results.
            relax_prediction (bool): If True, a geometry-relaxation step will be
                applied to the folded output. This is performed
                with a short molecular dynamics simulation.
            model_preset (str): Choose between 'monomer' or 'multimer'. If 'multimer'
                is selected, 'msas' must not be set and 'protein_sequence' must be a list
                of sequences, min 2 max 6.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        url = f"{self.api_host}/protein-structure/alphafold2/predict"
        data = {}

        if isinstance(protein_sequence, str):
            protein_sequence = [protein_sequence]
        files = [
            ("sequence", (None, seq)) for seq in protein_sequence
        ]

        if isinstance(msas, str):
            msas = [msas]
        if msas is None:
            files.append(('msas', None))
        else:
            for msa in msas:
                files.append(('msas', (msa, open(msa, 'rb'))))

        files.extend(
            [
                ("relax_prediction", (None, str(relax_prediction).lower())),
                ("model_preset", (None, model_preset)),
            ]
        )
        return self._submit_request("alphafold2", url, data, files, timeout)

    def _wait_for_alphafold2(
        self,
        py_request_id: RequestId,
    ):
        """Wait for results from a call to alphafold2_async, parse results.

        Args:
            py_request_id (RequestId): Everything we know about this request.

        Returns:
            str: A string representing the folded protein geometry in Protein Data Bank (PDB) format.
        """
        status_result = self._wait_for_response(py_request_id)
        return json.loads(status_result["response"])["pdbs"][0]

    @mark_cli
    def alphafold2_sync(
        self,
        protein_sequence: str,
        msas: Optional[Union[str, List[str]]] = None,  # Paths to MSA files.
        use_msa: bool = True,
        relax_prediction: bool = True,
        timeout=None,
    ):
        """Request AlphaFold2 inference, wait for the response.

        AlphaFold2 is the second generation protein folding model developed by
        DeepMind.
        https://www.nature.com/articles/s41586-021-03819-2
        https://github.com/deepmind/alphafold

        Approximate inference duration: 5-30 minutes.

        Args:
            protein_sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 3000 characters.
            msas (Optional[Union[str, List[str]]]): Paths to multi-sequence alignment (MSA) files in .a3m format.
                If use_msa=True, these files will be uploaded and used during
                protein folding.
            use_msa (bool): If True, the specified msas file will be uploaded and
                used as input to the folding model. If False, MSAs will
                be auto-generated, however this typically yields less
                accurate results.
            relax_prediction (bool): If True, a geometry-relaxation step will be
                applied to the folded output. This is performed
                with a short molecular dynamics simulation.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            str: A string representing the folded protein geometry in Protein Data Bank (PDB) format.
        """
        rqst_id = self.alphafold2_async(protein_sequence, msas, use_msa, relax_prediction, timeout)
        return self._wait_for_alphafold2(rqst_id)

    @mark_cli
    def esmfold_async(
        self,
        protein_sequence: str,
        timeout=None,
    ):
        """Request ESMFold inference, without waiting for inference results.

        Evolutionary Scale Modeling (ESM) Fold is a protein structure predictor developed
        by Facebook AI Research.
        https://github.com/facebookresearch/esm#esmfold

        Approximate inference time: 5-10 seconds.

        Args:
            protein_sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 1024 characters.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        url = f"{self.api_host}/protein-structure/esmfold/predict-no-aln"
        data = {
            "sequence": f"{protein_sequence}",
        }
        return self._submit_request("esmfold", url, data, None, timeout)

    def _wait_for_esmfold(
        self,
        py_request_id: RequestId,
    ):
        """Wait for results from a call to esmfold_async, parse results.

        Args:
            py_request_id (RequestId): Everything we know about this request.

        Returns:
            str: A string representing the folded protein geometry in Protein Data Bank (PDB) format.
        """
        status_result = self._wait_for_response(py_request_id)
        return json.loads(status_result["response"])["pdbs"][0]

    @mark_cli
    def esmfold_sync(
        self,
        protein_sequence: str,
        timeout=None,
    ):
        """Request ESMFold inference, wait for the response.

        Evolutionary Scale Modeling (ESM) Fold is a protein structure predictor developed
        by Facebook AI Research.
        https://github.com/facebookresearch/esm#esmfold

        Approximate inference time: 5-10 seconds.

        Args:
            protein_sequence (str): A string represeting a protein using the
                protein alphabet. 1 to 1024 characters.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            str: A strig representing the folded protein geometry in Protein Data Bank (PDB) format.
        """
        rqst_id = self.esmfold_async(protein_sequence, timeout)
        return self._wait_for_esmfold(rqst_id)

    @mark_cli
    def protgpt2_async(
        self,
        max_length: int = 150,
        top_k: int = 950,
        repetition_penalty: float = 1.2,
        num_return_sequences: int = 10,
        percent_to_keep: float = 0.1,
        timeout=None,
    ):
        """Request ProtGPT2 inference, without waiting for inference results.

        ProtGPT2 is a protein sequence generator developed by the University of Bayreuth.
        https://www.nature.com/articles/s41467-022-32007-7
        https://huggingface.co/nferruz/ProtGPT2

        Approximate inference time: 5-120 seconds.

        Args:
            max_length (int): Maximum number of tokens to generate. As tokens comprise an average of 3 to 4
                amino acids, the resulting protein sequences will be longer than max_length in terms of number
                of amino acids.
            top_k (int): Sampling of the k most probable tokens from the vocabulary as a decoding mechanism.
            repetition_penalty (float): Penalty to avoid repeats when random sampling at decoding.
                Recommended range is 1.1 to 1.3.
            num_return_sequences (int): Number of protein sequences to be returned in the API’s response.
            percent_to_keep (float, 0-1): The API's response contains only the sequences with the
                top percent_to_keep perplexities. If this value is < 1.0, sequences will be
                generated iteratively until num_return_sequences and percent_to_keep are satisfied.
                This can result in longer runtimes. A value of 1.0 means bypassing this perplexity filter
                and hence a faster response.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        url = f"{self.api_host}/protein-sequence/protgpt2/generate"
        data = {
            "max_length": max_length,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "num_return_sequences": num_return_sequences,
            "percent_to_keep": percent_to_keep,
        }
        return self._submit_request("protgpt2", url, data, None, timeout)

    def _wait_for_simple_response(self, py_request_id: RequestId):
        """Wait for results from the service, parse results.

        This function just loads the returned json object and returns the response.
        protgpt2 and diffdock use this kind of simple output unwrapping.

        Args:
            py_request_id (RequestId): Everything we know about this request.

        Returns:
            dict: A dictionary containing generated amino acid sequences and their perplexities.
        """
        status_result = self._wait_for_response(py_request_id)
        return json.loads(status_result["response"])

    @mark_cli
    def protgpt2_sync(
        self,
        max_length: int = 150,
        top_k: int = 950,
        repetition_penalty: float = 1.2,
        num_return_sequences: int = 10,
        percent_to_keep: float = 0.1,
        timeout=None,
    ):
        """Request ProtGPT2 inference, wait for the response.

        ProtGPT2 is a protein sequence generator developed by the University of Bayreuth.
        https://www.nature.com/articles/s41467-022-32007-7
        https://huggingface.co/nferruz/ProtGPT2

        Approximate inference time: 5-120 seconds.

        Args:
            max_length (int): Maximum number of tokens to generate. As tokens comprise an average of 3 to 4
                amino acids, the resulting protein sequences will be longer than max_length in terms of number
                of amino acids.
            top_k (int): Sampling of the k most probable tokens from the vocabulary as a decoding mechanism.
            repetition_penalty (float): Penalty to avoid repeats when random sampling at decoding.
                Recommended range is 1.1 to 1.3.
            num_return_sequences (int): Number of protein sequences to be returned in the API’s response.
            percent_to_keep (float, 0-1): The API's response contains only the sequences with the
                top percent_to_keep perplexities. If this value is < 1.0, sequences will be
                generated iteratively until num_return_sequences and percent_to_keep are satisfied.
                This can result in longer runtimes. A value of 1.0 means bypassing this perplexity filter
                and hence a faster response.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            Dict: A dictionary containing generated amino acid sequences and their perplexities.
        """
        rqst_id = self.protgpt2_async(
            max_length,
            top_k,
            repetition_penalty,
            num_return_sequences,
            percent_to_keep,
            timeout,
        )
        # For protgpt2 and diffdock, we just load the reponse.
        return self._wait_for_simple_response(rqst_id)

    @mark_cli
    def diffdock_async(
        self,
        ligand_file: str,
        protein_file: str,
        poses_to_generate: int = 20,
        diffusion_time_divisions: int = 20,
        diffusion_steps: int = 18,
        save_diffusion_trajectory: bool = False,
        timeout=None,
    ):
        """Request DiffDock inference without waiting for inference results.

        DiffDock performs ligand-protein docking, generating multiple possible
        poses and their confidence values. The model was developed at MIT.
        https://github.com/gcorso/DiffDock

        Approximate inference time: 5-30 seconds.

        Args:
            ligand_file (str): Path to small molecule/ligand file containing geometry in
                Structure-Data file (SD File) format. Maximum filesize is 5 MB.
            protein_file (str): Path to protein geometry in Protein Databank (PDB) format.
                Maximum filesize is 10 MB.
            poses_to_generate (int): number of docking poses to generate. Value range 1-100.
            diffusion_time_divisions (int): The number of discrete time divisions in the
                diffusion process. Value range 1-100.
            diffusion_steps (int): The number of steps to take along the discrete time
                divisions. This must be no greater than diffusion_time_divisions. Value range
                1-100.
            save_diffusion_trajectory (bool): If True, the inference output will contain a
                key entry "visualizations_files" that contains a string with a continuous
                list of PDB atom coordinates, depicting the reverse ligand diffusion during
                inference.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            RequestId: An object used to track the inference request.
                The RequestId contains the model name, correlation ID and other information related
                to this request. It can be used to interact with the task at a later time.
        """
        url = f"{self.api_host}/molecular-docking/diffdock/generate"
        self._setup_headers()
        data = {}
        files = {
            "ligand_file_bytes": open(ligand_file, "rb"),
            "protein_file_bytes": open(protein_file, "rb"),
            "poses_to_generate": (None, poses_to_generate),
            "diffusion_time_divisions": (None, diffusion_time_divisions),
            "diffusion_steps": (None, diffusion_steps),
            "save_diffusion_trajectory": (None, str(save_diffusion_trajectory).lower()),
        }
        return self._submit_request("diffdock", url, data, files, timeout)

    def _wait_for_diffdock(
        self,
        py_request_id: RequestId,
    ):
        """Wait for results from a call to diffdock_async, parse results.

        Args:
            py_request_id (RequestId): Everything we know about this request.

        Returns:
            dict: A dictionary containing lists of docked positions and confidences.
        """
        status_result = self._wait_for_response(py_request_id)
        return json.loads(status_result["response"])

    @mark_cli
    def diffdock_sync(
        self,
        ligand_file: str,
        protein_file: str,
        poses_to_generate: int = 20,
        diffusion_time_divisions: int = 20,
        diffusion_steps: int = 18,
        save_diffusion_trajectory: bool = False,
        timeout=None,
    ):
        """Request DiffDock inference, wait for the response.

        DiffDock performs ligand-protein docking, generating multiple possible
        poses and their confidence values. The model was developed at MIT.
        https://github.com/gcorso/DiffDock

        Approximate inference time: 5-30 seconds.

        Args:
            ligand_file (str): Path to small molecule/ligand file containing geometry in
                Structure-Data file (SD File) format. Maximum filesize is 5 MB.
            protein_file (str): Path to protein geometry in Protein Databank (PDB) format.
                Maximum filesize is 10 MB.
            poses_to_generate (int): number of docking poses to generate. Value range 1-100.
            diffusion_time_divisions (int): The number of discrete time divisions in the
                diffusion process. Value range 1-100.
            diffusion_steps (int): The number of steps to take along the discrete time
                divisions. This must be no greater than diffusion_time_divisions. Value range
                1-100.
            save_diffusion_trajectory (bool): If True, the inference output will contain a
                key entry "visualizations_files" that contains a string with a continuous
                list of PDB atom coordinates, depicting the reverse ligand diffusion during
                inference.
            timeout (int): The timeout duration in seconds. If None, the default timeout
                set during construction will be used. A timeout results in a
                requests.exceptions.Timeout exception.

        Returns:
            Dict: A dictionary containing lists of docked positions and confidences.
        """
        rqst_id = self.diffdock_async(
            ligand_file,
            protein_file,
            poses_to_generate,
            diffusion_time_divisions,
            diffusion_steps,
            save_diffusion_trajectory,
            timeout,
        )
        return self._wait_for_simple_response(rqst_id)

    #
    # Utilities
    #
    @mark_cli
    def fetch_tasks(self, number_of_tasks: int = 10):
        """Get all available information for the 'N' most recent tasks.

        Args:
            number_of_tasks (int): Number of tasks to retrieve.

        Returns:
            List[Dict] : A list of tasks recently submitted by the user, each with a dict of
                         details about the task status.
        """
        if number_of_tasks <= 0:
            raise IncorrectParamsError(
                status_code=http.HTTPStatus.BAD_REQUEST,
                reason=f"Number of tasks was {number_of_tasks}, it must be > 0",
                decoded_content="",
            )

        url = f"{self.api_host}/tasks?source=api&limit={number_of_tasks}"
        headers = self._setup_headers()
        response = get_session().get(url, headers=headers)
        ResponseHandler.handle_response(response)
        tasks = json.loads(response.content)["tasks"]
        return tasks

    @mark_cli
    def fetch_task_status(self, py_request_id: Union[str, RequestId]):
        """Get information for a specific task.

        Args:
            py_request_id (str or RequestId): The inference task of interest.

        Returns:
            str: A string representing the task state, one of 'DONE', 'CREATED', 'PROCESSING', 'SUBMITTED', 'ERROR'
        """
        url = self._form_url(py_request_id, "task")
        headers = self._setup_headers()
        response = get_session().get(url, headers=headers)
        ResponseHandler.handle_response(response)
        content = json.loads(response.content)["control_info"]["status"]
        if isinstance(py_request_id, RequestId):
            py_request_id.status = content
        return content

    @mark_cli
    def delete_task(self, py_request_id: Union[str, RequestId]):
        """Delete the given task.

        Args:
            py_request_id (str or RequestId): The inference task of interest.

        Returns:
            str: a status confirmation the task was deleted.
        """
        url = self._form_url(py_request_id, "task")
        headers = self._setup_headers()
        response = get_session().delete(url, headers=headers)
        ResponseHandler.handle_response(response)
        return json.loads(response.content)

    @mark_cli
    def cancel_task(self, py_request_id: Union[str, RequestId]):
        """Cancel a task.

        Args:
            py_request_id (str or RequestId): The correlation_id.

        Returns:
            str: a status confirmation the task was cancelled.
        """
        url = self._form_url(py_request_id, "cancel")
        headers = self._setup_headers()
        response = get_session().put(url, headers=headers)
        return json.loads(response.content)

    def _form_url(self, py_request_id: Union[str, RequestId], endpoint: str):
        """Form a 'task manipulation' URL.
        Args:
            py_request_id (str or RequestId): The correlation ID.
            endpoint: What we need to talk to.
        """
        if not endpoint.isalpha():
            raise Exception(f"Invalid endpoint ->{endpoint}<-")
        if isinstance(py_request_id, RequestId):
            url = f"{self.api_host}/{endpoint}/{py_request_id.correlation_id}"
        elif isinstance(py_request_id, str):
            url = f"{self.api_host}/{endpoint}/{py_request_id}"
        else:
            raise BadRequestId(type(py_request_id))
        return url

    @staticmethod
    def _decode_embedding_response(byte_data, data_format=Literal["npz", "h5"]):
        """Decode a binary model output.

        Given a binary zip file in byte_data whose entries are numpy arrays,
        extract its contents & return a map from each 'filename' to the corresponding
        NumPy array.

        Args:
            byte_data (bytes (build-in python): embedding byte data to decode
            data_format (str): what data type is represented in the byte data

        Returns:
            List[Dict[np.array]] The decoded payload.
                A dict is used for the various properties that may be returned (e.g. "embeddings",
                "tokens"...), and List in which each entry is an embeddings (np.array). A List of dicts is
                used rather than a 2D np.array because
                    a) To clearly indicate that the first index relates to different
                       input/output pairs
                    b) To allow variable length responses per array, which we need to
                       de-pad ESM2.

        Raises:
            ValueError: If `data_format` is not supported.
        """
        file_like_obj = io.BytesIO(byte_data)
        if data_format == "npz":
            payload = np.load(file_like_obj)
        elif data_format == "h5":
            payload = h5.File(file_like_obj)
        else:
            raise ValueError(f"Unsupported response data format: {data_format}")
        # Get any value. There is an assumption all values are arrays of equal length.
        length = len(next(iter(payload.values())))
        # Return a list-of-dicts
        result_list = [{key: payload[key][i] for key in payload.keys()} for i in range(length)]
        return result_list
