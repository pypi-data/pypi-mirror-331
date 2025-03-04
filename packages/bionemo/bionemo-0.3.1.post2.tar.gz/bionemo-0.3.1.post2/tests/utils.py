import os


def get_test_file_path(file):
    """Returns absolute paths to test data."""
    print(os.path.join(os.path.dirname(__file__), file))
    return os.path.join(os.path.dirname(__file__), file)
