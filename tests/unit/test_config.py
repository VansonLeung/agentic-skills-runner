from pathlib import Path
from unittest.mock import patch

import pytest

from skills_runner.config import Configuration
from skills_runner.exceptions import ConfigError


def test_from_env_missing_api_key(monkeypatch):
    with patch('skills_runner.config.load_dotenv'):
        monkeypatch.delenv("LLM_API_KEY", raising=False)
        monkeypatch.setenv("LLM_API_BASE_URL", "https://api.example.com")
        monkeypatch.setenv("LLM_MODEL_NAME", "gpt-4")

        with pytest.raises(ConfigError, match="LLM_API_KEY is required"):
            Configuration.from_env()


def test_from_env_missing_base_url(monkeypatch):
    with patch('skills_runner.config.load_dotenv'):
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        monkeypatch.delenv("LLM_API_BASE_URL", raising=False)
        monkeypatch.setenv("LLM_MODEL_NAME", "gpt-4")

        with pytest.raises(ConfigError, match="LLM_API_BASE_URL is required"):
            Configuration.from_env()


def test_from_env_missing_model_name(monkeypatch):
    with patch('skills_runner.config.load_dotenv'):
        monkeypatch.setenv("LLM_API_KEY", "test-key")
        monkeypatch.setenv("LLM_API_BASE_URL", "https://api.example.com")
        monkeypatch.delenv("LLM_MODEL_NAME", raising=False)

        with pytest.raises(ConfigError, match="LLM_MODEL_NAME is required"):
            Configuration.from_env()


def test_from_env_invalid_timeout(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_API_BASE_URL", "https://api.example.com")
    monkeypatch.setenv("LLM_MODEL_NAME", "gpt-4")
    monkeypatch.setenv("SKILLS_FOLDER_PATH", str(tmp_path))
    monkeypatch.setenv("SCRIPT_TIMEOUT_SECONDS", "0")

    with pytest.raises(ConfigError, match="SCRIPT_TIMEOUT_SECONDS must be a positive integer"):
        Configuration.from_env()


def test_from_env_creates_skills_folder(monkeypatch, tmp_path):
    skills_path = tmp_path / "skills"
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_API_BASE_URL", "https://api.example.com")
    monkeypatch.setenv("LLM_MODEL_NAME", "gpt-4")
    monkeypatch.setenv("SKILLS_FOLDER_PATH", str(skills_path))
    monkeypatch.setenv("SCRIPT_TIMEOUT_SECONDS", "30")

    config = Configuration.from_env()

    assert config.skills_folder == skills_path
    assert skills_path.exists()
    assert skills_path.is_dir()
