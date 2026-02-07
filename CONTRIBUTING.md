# Contributing

Thanks for contributing to LLM Skills Runner.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt
```

## Running Tests

```bash
pytest
```

### Test Categories

- Contract tests: tests/contract/
- Integration tests: tests/integration/
- Unit tests: tests/unit/

## Code Quality

- Format code with your preferred formatter
- Run type checks with mypy (strict)

```bash
mypy src
```

## Pull Requests

- Keep changes focused and small
- Update documentation when behavior changes
- Ensure tests pass before submitting
