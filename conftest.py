import shutil
from pathlib import Path

import pytest


@pytest.fixture
def cleanup_test_files():
    test_file_path = Path(__file__).parent.resolve().joinpath('tmp_test_files')
    if test_file_path.exists():
        shutil.rmtree(test_file_path)
    test_file_path.mkdir()
    yield test_file_path
    shutil.rmtree(test_file_path)
