import pytest
from utils import get_test_file_path


@pytest.mark.parametrize(
    "ligand_file, protein_file, poses_to_generate, diffusion_time_divisions, diffusion_steps, "
    "save_diffusion_trajectory, timeout",
    [
        ("test_data/6a87_ligand.sdf", "test_data/6a87_protein_processed.pdb", 10, 19, 16, True, None),
        ("test_data/6a87_ligand.sdf", "test_data/6a87_protein_processed.pdb", 3, 15, 11, True, None),
    ],
)
def test_diffdock(
    make_python_client,
    ligand_file,
    protein_file,
    poses_to_generate,
    diffusion_time_divisions,
    diffusion_steps,
    save_diffusion_trajectory,
    timeout,
):
    # Run Test
    api = make_python_client()
    result = api.diffdock_sync(
        get_test_file_path(ligand_file),
        get_test_file_path(protein_file),
        poses_to_generate,
        diffusion_time_divisions,
        diffusion_steps,
        save_diffusion_trajectory,
        timeout,
    )
    # Assertions
    assert set(result.keys()) == set(["docked_ligand_position_files", "visualizations_files", "pose_confidence"])
    for key in result.keys():
        if key == "visualizations_files" and not save_diffusion_trajectory:
            continue
        assert len(result[key]) == poses_to_generate
    for item in result["docked_ligand_position_files"]:
        assert type(item) == str
    for item in result["pose_confidence"]:
        assert type(item) == float
    if save_diffusion_trajectory:
        for item in result["visualizations_files"]:
            assert type(item) == str
            # The diffusion should have diffusion_time_divisions + 1 number of steps. This resulting string
            # contains each of the diffused poses
            # TODO: This should be split into a separate list rather than a continuous string
            # TODO: unclear how many poses there should be in this string
            # assert result['visualizations_files'][0].count("ENDMDL") == diffusion_time_divisions
