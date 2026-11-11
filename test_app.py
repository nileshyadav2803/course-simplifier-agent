"""
Tests for app.py – no real API calls are made.
Run with:  pytest tests/
"""

import os
import sys

import pytest

# Make sure the project root is on sys.path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Test 1: load_env() raises a clear EnvironmentError when variables are missing
# ---------------------------------------------------------------------------

def test_load_env_raises_on_missing_values(monkeypatch):
    """load_env() must raise EnvironmentError listing every missing variable."""
    # Remove all three variables from the environment
    monkeypatch.delenv("WATSONX_API_KEY", raising=False)
    monkeypatch.delenv("WATSONX_PROJECT_ID", raising=False)
    monkeypatch.delenv("WATSONX_URL", raising=False)

    import app  # noqa: PLC0415 (import inside function is intentional)

    # Patch load_dotenv so it cannot read a real .env file from disk,
    # ensuring only the cleared environment above is seen by load_env().
    monkeypatch.setattr(app, "load_dotenv", lambda: None)

    with pytest.raises(EnvironmentError) as exc_info:
        app.load_env()

    error_message = str(exc_info.value)
    assert "WATSONX_API_KEY" in error_message
    assert "WATSONX_PROJECT_ID" in error_message
    assert "WATSONX_URL" in error_message


# ---------------------------------------------------------------------------
# Test 2: SYSTEM_MESSAGE is loaded correctly from app.py
# ---------------------------------------------------------------------------

def test_system_message_is_loaded():
    """SYSTEM_MESSAGE must contain the key phrases from app.json."""
    import app  # noqa: PLC0415

    assert "Course Content Simplification Agent" in app.SYSTEM_MESSAGE
    assert "Beginner" in app.SYSTEM_MESSAGE
    assert "Intermediate" in app.SYSTEM_MESSAGE
    assert "Expert" in app.SYSTEM_MESSAGE
    # The instruction not to add extra information must be present
    assert "Do not add information" in app.SYSTEM_MESSAGE


# ---------------------------------------------------------------------------
# Test 3: build_prompt() prepends the level to the user text
# ---------------------------------------------------------------------------

def test_build_prompt_prepends_level():
    """build_prompt() must produce '<Level>: <user text>' so the model sees the level."""
    import app  # noqa: PLC0415

    for level in ["Beginner", "Intermediate", "Expert"]:
        result = app.build_prompt(level, "Neural networks process data in layers.")
        assert result.startswith(f"{level}:"), (
            f"Expected prompt to start with '{level}:', got: {result!r}"
        )
        assert "Neural networks" in result
