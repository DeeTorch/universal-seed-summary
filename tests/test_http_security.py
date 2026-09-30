import pytest
from uss_engine.clients._http import post_json

def test_post_json_rejects_file_scheme():
    with pytest.raises(ValueError, match="URL scheme 'file' is not allowed"):
        post_json(url="file:///etc/passwd", payload={"test": 123})

def test_post_json_rejects_ftp_scheme():
    with pytest.raises(ValueError, match="URL scheme 'ftp' is not allowed"):
        post_json(url="ftp://example.com/file", payload={"test": 123})

def test_post_json_rejects_empty_scheme():
    with pytest.raises(ValueError, match="URL scheme '' is not allowed"):
        post_json(url="example.com/api", payload={"test": 123})
