import pydantic
import pytest

from mopidy.models import Image


def test_uri():
    uri = "an_uri"
    image = Image(uri=uri)
    assert image.uri == uri
    with pytest.raises(pydantic.ValidationError):
        image.uri = None


def test_width():
    image = Image(uri="uri", width=100)
    assert image.width == 100
    with pytest.raises(pydantic.ValidationError):
        image.width = None


def test_height():
    image = Image(uri="uri", height=100)
    assert image.height == 100
    with pytest.raises(pydantic.ValidationError):
        image.height = None


def test_invalid_kwarg():
    with pytest.raises(pydantic.ValidationError):
        Image(uri="uri", foo="baz")
