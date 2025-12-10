import os
import pytest
from src.config import Config

@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
    monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
    monkeypatch.delenv("ZOTERO_LIBRARY_TYPE", raising=False)
    monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
    monkeypatch.delenv("EMAIL", raising=False)

def test_config_defaults(clean_env):
    config = Config()
    assert config.ZOTERO_LIBRARY_ID == ""
    assert config.ZOTERO_API_KEY == ""
    assert config.ZOTERO_LIBRARY_TYPE == "group"
    assert config.SEMANTIC_SCHOLAR_API_KEY == ""
    assert config.EMAIL == ""

def test_config_from_env(monkeypatch):
    monkeypatch.setenv("ZOTERO_LIBRARY_ID", "12345")
    monkeypatch.setenv("ZOTERO_API_KEY", "key123")
    monkeypatch.setenv("ZOTERO_LIBRARY_TYPE", "user")
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "semkey")
    monkeypatch.setenv("EMAIL", "test@example.com")

    config = Config()
    assert config.ZOTERO_LIBRARY_ID == "12345"
    assert config.ZOTERO_API_KEY == "key123"
    assert config.ZOTERO_LIBRARY_TYPE == "user"
    assert config.SEMANTIC_SCHOLAR_API_KEY == "semkey"
    assert config.EMAIL == "test@example.com"

def test_validate_success(monkeypatch):
    monkeypatch.setenv("ZOTERO_LIBRARY_ID", "12345")
    monkeypatch.setenv("ZOTERO_API_KEY", "key123")
    monkeypatch.setenv("EMAIL", "test@example.com")

    config = Config()
    # Should not raise exception
    config.validate()

def test_validate_missing_library_id(monkeypatch):
    monkeypatch.setenv("ZOTERO_API_KEY", "key123")
    monkeypatch.setenv("EMAIL", "test@example.com")

    config = Config()
    with pytest.raises(ValueError, match="ZOTERO_LIBRARY_ID is missing"):
        config.validate()

def test_validate_missing_api_key(monkeypatch):
    monkeypatch.setenv("ZOTERO_LIBRARY_ID", "12345")
    monkeypatch.setenv("EMAIL", "test@example.com")

    config = Config()
    with pytest.raises(ValueError, match="ZOTERO_API_KEY is missing"):
        config.validate()

def test_validate_missing_email(monkeypatch):
    monkeypatch.setenv("ZOTERO_LIBRARY_ID", "12345")
    monkeypatch.setenv("ZOTERO_API_KEY", "key123")

    config = Config()
    with pytest.raises(ValueError, match="EMAIL is missing"):
        config.validate()

def test_validate_multiple_missing(monkeypatch):
    config = Config()
    with pytest.raises(ValueError) as excinfo:
        config.validate()
    msg = str(excinfo.value)
    assert "ZOTERO_LIBRARY_ID is missing" in msg
    assert "ZOTERO_API_KEY is missing" in msg
    assert "EMAIL is missing" in msg
