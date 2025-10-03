"""Test validator.py changes."""

import pytest

from fw_gear_file_validator.validator import initialize_validator


def test_initialize_validator_flywheel_type():
    """Test that initialize_validator handles 'flywheel' file type."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema",
        "type": "object",
        "properties": {"test_field": {"type": "string"}},
    }

    validator = initialize_validator("flywheel", schema)

    assert validator is not None
    assert hasattr(validator, "validator")


def test_initialize_validator_json_type():
    """Test that initialize_validator still handles 'json' file type."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema",
        "type": "object",
        "properties": {"test_field": {"type": "string"}},
    }

    validator = initialize_validator("json", schema)

    assert validator is not None
    assert hasattr(validator, "validator")


def test_initialize_validator_csv_type():
    """Test that initialize_validator still handles 'csv' file type."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema",
        "type": "object",
        "properties": {"test_field": {"type": "string"}},
    }

    validator = initialize_validator("csv", schema)

    assert validator is not None
    assert hasattr(validator, "validator")


def test_initialize_validator_unsupported_type():
    """Test that initialize_validator raises ValueError for unsupported file type."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema",
        "type": "object",
        "properties": {"test_field": {"type": "string"}},
    }

    with pytest.raises(ValueError, match="file type unsupported Not supported"):
        initialize_validator("unsupported", schema)
