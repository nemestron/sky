import pytest
import tempfile
import shutil
import os

@pytest.fixture
def temp_workspace():
    """Provides a temporary directory for isolated testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create required subdirectories
    os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "frames"), exist_ok=True)
    
    yield temp_dir
    shutil.rmtree(temp_dir)