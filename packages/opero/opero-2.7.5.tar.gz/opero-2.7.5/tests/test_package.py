"""Test suite for opero."""


def test_version():
    """Verify package exposes version."""
    import opero

    assert opero.__version__
