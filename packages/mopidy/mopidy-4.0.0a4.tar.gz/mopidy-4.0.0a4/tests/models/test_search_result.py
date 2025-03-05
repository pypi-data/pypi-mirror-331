import pydantic
import pytest

from mopidy.models import Album, Artist, SearchResult, Track


def test_uri():
    uri = "an_uri"
    result = SearchResult(uri=uri)
    assert result.uri == uri
    with pytest.raises(pydantic.ValidationError):
        result.uri = None


def test_tracks():
    tracks = [Track(), Track(), Track()]
    result = SearchResult(tracks=tracks)
    assert list(result.tracks) == tracks
    with pytest.raises(pydantic.ValidationError):
        result.tracks = None


def test_artists():
    artists = [Artist(), Artist(), Artist()]
    result = SearchResult(artists=artists)
    assert list(result.artists) == artists
    with pytest.raises(pydantic.ValidationError):
        result.artists = None


def test_albums():
    albums = [Album(), Album(), Album()]
    result = SearchResult(albums=albums)
    assert list(result.albums) == albums
    with pytest.raises(pydantic.ValidationError):
        result.albums = None


def test_invalid_kwarg():
    with pytest.raises(pydantic.ValidationError):
        SearchResult(foo="baz")


def test_repr_without_results():
    assert (
        repr(SearchResult(uri="uri"))
        == "SearchResult(uri='uri', tracks=(), artists=(), albums=())"
    )


def test_serialize_without_results():
    assert SearchResult(uri="uri").serialize() == {
        "__model__": "SearchResult",
        "uri": "uri",
        "albums": [],
        "artists": [],
        "tracks": [],
    }
