import pytest

from . import DATADIR


@pytest.fixture
def filecontents(request):
    """Return the contents of a file (via indirect parametrization)."""
    params = request.param
    with open(DATADIR.joinpath(params["filename"])) as fp:
        contents = fp.read()
    return contents
