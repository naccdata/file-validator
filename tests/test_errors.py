from pathlib import Path
from unittest.mock import MagicMock

import flywheel
from jsonschema.exceptions import ValidationError

from fw_gear_file_validator import errors, utils, validator

BASE_DIR = d = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_allOf = BASE_DIR / "assets" / "test_allOf_schema.json"


def test_save_errors_metadata():
    error_dict = [{"key1": "k1v1", "key2": "k2v1"}, {"key1": "k1v2", "key2": "k2v2"}]
    context = MagicMock()
    file_name = "test_file_name.ext"
    file_id = "test_container_id"
    file_type = "test_file_type"
    parent_dict = {}

    mock_client = MagicMock()

    file = flywheel.FileEntry(
        name=file_name, file_id=file_id, type=file_type, parents=parent_dict
    )
    mock_client.get_file.return_value = file
    fw_ref = utils.FwReference.init_from_gear_input(mock_client, file, "file")

    errors.save_errors_metadata(error_dict, fw_ref, context)
    context.metadata.add_qc_result.assert_called_with(
        file_name, "validation", state="FAIL", data=error_dict
    )


def test_validator_error_to_standard():
    test_validator = validator.JsonValidator(test_allOf)

    json_object_notrigger_noerror = {
        "required_key1": "aser",
        "required_key2": 3,
    }

    test_errors = list(
        test_validator.validator.iter_errors(json_object_notrigger_noerror)
    )

    assert test_errors == []
    json_object_notrigger_error = {
        "required_key1": "aser",
        "required_key2": 2,
    }
    test_errors = list(
        test_validator.validator.iter_errors(json_object_notrigger_error)
    )
    assert len(test_errors) == 1
    standard_error = errors.validator_error_to_standard(test_errors[0])
    assert standard_error["location"] == {"key_path": "allOf.0.then.conditional_key1"}
    assert standard_error["code"] == "required"


def test_file_error_required_property_fix():
    """Test that the required property error handling concatenates correctly."""

    validation_error = ValidationError(
        message="'missing_field' is a required property",
        schema_path=["properties", "test_field"],
        validator="required",
    )

    standard_error = errors.validator_error_to_standard(validation_error)

    assert standard_error["code"] == "required"
    assert standard_error["location"]["key_path"] == "properties.missing_field"
    assert standard_error["value"] == ""
    assert standard_error["expected"] == ""


def test_add_flywheel_location_to_errors_file_content():
    """Test adding flywheel location for file content validation."""
    mock_client = MagicMock()
    file_entry = flywheel.FileEntry(
        name="test.json", file_id="file123", type="json", parents={}
    )

    fw_ref = utils.FwReference.init_from_gear_input(mock_client, file_entry, "file")
    fw_ref.hierarchy_objects = {"file": {"file_id": "file123", "name": "test.json"}}

    errors_list = [{"location": {"key_path": "test.property"}, "message": "Test error"}]

    result = errors.add_flywheel_location_to_errors(fw_ref, errors_list)

    assert result[0]["container_id"] == "file123"
    assert "flywheel_path" in result[0]


def test_add_flywheel_location_to_errors_flywheel_metadata():
    """Test adding flywheel location for flywheel metadata validation."""
    mock_client = MagicMock()
    file_entry = flywheel.FileEntry(
        name="test.json",
        file_id="file123",
        type="json",
        parents={"acquisition": "acq123"},
    )

    fw_ref = utils.FwReference.init_from_gear_input(mock_client, file_entry, "flywheel")
    fw_ref.hierarchy_objects = {
        "file": {"file_id": "file123", "name": "test.json"},
        "acquisition": {"id": "acq123", "label": "test-acquisition"},
    }

    errors_list = [
        {
            "location": {"key_path": "properties.acquisition.properties.label"},
            "message": "Test error",
        }
    ]

    result = errors.add_flywheel_location_to_errors(fw_ref, errors_list)

    assert result[0]["container_id"] == "acq123"
    assert "flywheel_path" in result[0]
