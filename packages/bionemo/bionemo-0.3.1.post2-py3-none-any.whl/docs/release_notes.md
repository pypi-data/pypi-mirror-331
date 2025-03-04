# Release notes - v0.3.0

## New Functionality
Support has been added for the following models and workflows.

### Molecular Generation models
* [MolMIM](https://arxiv.org/abs/2208.09016) is a small molecule generative model developed by Nvidia. API endpoints include 
  embeddings (`molmim_embeddings_sync`), decoding(`molmim_decode_sync`), and generation (`molmim_unguided_generate_(a)sync`).
* MoFlow support has been extended to allow embeddings (`moflow_embeddings_sync`) and decoding(`moflow_decode_sync`)

### Property guided Generation
MolMIM and MoFlow now support guided molecular generation. Models iteratively optimize from a seed molecule to provide 
novel molecules that score highly on molecular similarity to the seed, while optimizing the users choice of property, 
such as QED or logP score. These endpoints are provided via `{moflow/molmim}_guided_generate_{a}sync`.

### MSA
Multiple sequence alignment (MSA) is available via the Jackhhmer tool. See the documentation on `msa_{a}sync` endpoints.

## Breaking API changes
* Moflow `temperature` parameter has been renamed to `scaled_radius`.
* Openfold and Alphafold `relax_prediction` parameter now defaults to `True`.
* The API endpoints for molecular generation models now distinguish between unguided and guided generative sampling. The previous endpoints `megamolbart_{a}sync` and `moflow_{a}sync` are now `megamolbart_unguided_generate_{a}sync` and
  `moflow_unguided_generate_{a}sync`, respectively, to match their guided generation counterparts. The old endpoints are deprecated, and will be removed in a future release.
* Input and output of the molecule generate methods has been standardized between MoFlow, MolMIM, and MegaMolBART. Previously, `megamolbart_generate` accepted a list of SMILES strings.
  Now, all generate methods accept a single seed SMILES string. Output of molecular generation is now a dictionary of {"generated_molecules": List[smiles], "scores": np.ndarray}, where
  scores represents similarity score to the seed in the case of unguided generation, and the score of the selected oracle for guided generation.