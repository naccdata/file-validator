import logging
import typing as t

from flywheel_gear_toolkit import GearToolkitContext
from jsonschema.exceptions import ValidationError

from fw_gear_file_validator.utils import PARENT_ORDER, FwReference

log = logging.getLogger(__name__)


def validator_error_to_standard(schema_error):
    return {
        "type": "error",  # For now, jsonValidaor can only produce errors.
        "code": str(schema_error.validator),
        "location": ""
        if schema_error.schema_path == [""]
        else {"key_path": ".".join(list(schema_error.schema_path)[:-1])},
        "value": str(schema_error.instance),
        "expected": str(schema_error.schema),
        "message": schema_error.message,
    }


def make_empty_file_error():
    return ValidationError(
        **{
            "validator": "EmptyFile",
            "schema_path": [""],
            "instance": "",
            "schema": "",
            "message": "The File Is Empty",
            "path": "",
        }
    )


def make_missing_header_error():
    return ValidationError(
        **{
            "validator": "MissingHeader",
            "schema_path": [""],
            "instance": "",
            "schema": "",
            "message": "The file is missing a header, or the header is not recognized.",
            "path": "",
        }
    )


def make_incorrect_header_error(column_name):
    return ValidationError(
        **{
            "validator": "IncorrectColumnName",
            "schema_path": [""],
            "instance": "",
            "schema": "",
            "message": f"The file has an unspecified column: {column_name}",
            "path": "",
        }
    )


def add_flywheel_location_to_errors(fw_ref: FwReference, packaged_errors: list):
    """Takes a set of packaged errors and adds flywheel hierarchy info to them."""
    hierarchy = fw_ref.hierarchy_objects
    fw_url = fw_ref.get_lookup_path()
    if fw_ref.contents == "file":
        for e in packaged_errors:
            e["flywheel_path"] = fw_url
            e["container_id"] = hierarchy["file"]["file_id"]
    else:
        for e in packaged_errors:
            location = e["location"].split(".")[0]
            if location not in PARENT_ORDER:
                raise ValueError(
                    f"Value {location} not valid flywheel hierarchy location"
                )
            e["flywheel_path"] = fw_ref.get_lookup_path(level=location)
            id_loc = "file_id" if location == "file" else "id"
            e["container_id"] = hierarchy[location][id_loc]

    return packaged_errors


def save_errors_metadata(
    errors: t.List[t.Dict], input_file: FwReference, gtk_context: GearToolkitContext
):
    """Saves the packaged errors to file metadata."""
    if not errors:
        state = "PASS"
        meta_dict = {}
    else:
        state = "FAIL"
        meta_dict = {"data": errors}

    gtk_context.metadata.add_qc_result(
        input_file.name, "validation", state=state, **meta_dict
    )
