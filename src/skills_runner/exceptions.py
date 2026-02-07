class SkillsRunnerError(Exception):
    """Base exception for skills runner errors."""


class ConfigError(SkillsRunnerError):
    """Raised when configuration is invalid or missing."""


class SkillNotFoundError(SkillsRunnerError):
    """Raised when a requested skill does not exist."""


class ToolExecutionError(SkillsRunnerError):
    """Raised when a tool fails to execute."""
