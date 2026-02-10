from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import logging
import os

from dotenv import load_dotenv

from .exceptions import ConfigError


@dataclass(frozen=True)
class Configuration:
    """Configuration loaded from environment variables and .env file."""
    api_key: str
    api_base_url: str
    model_name: str
    model_names: tuple
    skills_folder: Path
    timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Configuration":
        """Load configuration values from environment variables."""
        load_dotenv()

        api_key = os.getenv("LLM_API_KEY", "").strip()
        api_base_url = os.getenv("LLM_API_BASE_URL", "").strip()
        model_name = os.getenv("LLM_MODEL_NAME", "").strip()
        model_names_raw = os.getenv("LLM_MODEL_NAMES", "").strip()
        skills_folder_raw = os.getenv("SKILLS_FOLDER_PATH", "./skills").strip()
        timeout_raw = os.getenv("SCRIPT_TIMEOUT_SECONDS", "30").strip()

        if not api_key:
            logging.warning("LLM_API_KEY is not set; requests may fail if the provider requires one")
        if not api_base_url:
            raise ConfigError("LLM_API_BASE_URL is required")
        # Parse model list: LLM_MODEL_NAMES takes priority, falls back to LLM_MODEL_NAME
        if model_names_raw:
            model_names = tuple(m.strip() for m in model_names_raw.split(",") if m.strip())
        elif model_name:
            model_names = (model_name,)
        else:
            model_names = ()

        if not model_names:
            raise ConfigError("LLM_MODEL_NAME or LLM_MODEL_NAMES is required")

        # Default model is the first in the list
        if not model_name:
            model_name = model_names[0]

        skills_folder = Path(skills_folder_raw)
        timeout_seconds = _parse_positive_int(timeout_raw, "SCRIPT_TIMEOUT_SECONDS")

        _ensure_skills_folder(skills_folder)

        return cls(
            api_key=api_key,
            api_base_url=api_base_url,
            model_name=model_name,
            model_names=model_names,
            skills_folder=skills_folder,
            timeout_seconds=timeout_seconds,
        )


def _parse_positive_int(value: str, env_name: str) -> int:
    """Parse and validate a positive integer from environment."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigError(f"{env_name} must be a positive integer") from exc

    if parsed <= 0:
        raise ConfigError(f"{env_name} must be a positive integer")

    return parsed


def _ensure_skills_folder(path: Path) -> None:
    """Ensure the skills folder exists and is a directory."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"Unable to create skills folder at: {path}") from exc

    if not path.is_dir():
        raise ConfigError(f"Skills folder path is not a directory: {path}")


def setup_logging(log_file: Optional[Path] = None) -> None:
    """Configure basic logging to stdout or a file."""
    handlers = None
    if log_file is not None:
        handlers = [logging.FileHandler(log_file)]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )
