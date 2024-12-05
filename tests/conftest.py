import pytest

from . import get_filecontents


@pytest.fixture
def filecontents(request):
    """Return the contents of a file (via indirect parametrization)."""
    return get_filecontents(request.param["filename"])
