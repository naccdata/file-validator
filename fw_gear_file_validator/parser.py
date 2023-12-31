"""Parser module to parse gear config.json."""

from pathlib import Path
from typing import Tuple, Union

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_file_validator.utils import FwReference

level_dict = {"Validate File Contents": "file", "Validate Flywheel Objects": "flywheel"}
SUPPORTED_FILE_EXTENSIONS = {".json": "json"}
SUPPORTED_FLYWHEEL_MIMETYPES = {"application/json": "json"}


def parse_config(
    context: GearToolkitContext,
) -> Tuple[bool, str, Path, FwReference, dict]:
    """Parses necessary items out of the context object"""

    debug = context.config.get("debug")
    tag = context.config.get("tag")
    add_parents = context.config.get("add_parents")
    schema_file_path = Path(context.get_input_path("validation_schema"))

    validation_level = level_dict[context.config.get("validation_level")]

    if validation_level == "file":
        if not context.get_input_filename("input_file"):
            raise ValueError("No input file provided for validation_level 'file'")
        if add_parents:
            raise ValueError(
                "Cannot attach flywheel parents to file-content validation"
            )

    file_name = None
    file_type = None
    file_path = None
    if context.get_input("input_file"):
        file_name = context.get_input_filename("input_file")
        file_type = identify_file_type(context.get_input("input_file"))
        if validation_level == "file":
            file_path = Path(context.get_input_path("input_file"))

    if validation_level == "flywheel":
        file_path = None

    fw_ref = FwReference(
        cont_id=context.destination["id"],
        cont_type=context.destination["type"],
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        _client=context.client,
    )

    loader_config = {"add_parents": add_parents}

    return debug, tag, schema_file_path, fw_ref, loader_config


def get_fw_type_info(input_file: dict) -> (str, str):
    """Gets a mimetype from a flywheel config input file object, and extracts the local path of that file."""
    mime = input_file.get("object", {}).get("mimetype")
    path = input_file.get("location", {}).get("name")
    return mime, path


def get_ext(input_file: Union[Path, str]) -> Union[str, None]:
    """Extracts the extension from a string or Path"""
    if isinstance(input_file, str):
        input_file = Path(input_file)
    if not isinstance(input_file, Path):
        return None
    return input_file.suffix


def validate_filetype(ext: str, mime: str) -> Union[str, None]:
    """Ensures detected filetype is supported and errors if not"""
    input_file_type = None
    if ext:
        input_file_type = SUPPORTED_FILE_EXTENSIONS.get(ext)
    elif mime:
        input_file_type = SUPPORTED_FLYWHEEL_MIMETYPES.get(mime)
    if input_file_type is None:
        raise TypeError(f"file type {mime},{ext} is not supported")

    return input_file_type


def identify_file_type(input_file: Union[dict, str, Path]) -> str:
    """Given a flywheel config input file object, identify a valid file type if possible"""
    # see if the input file object has a value
    if not input_file:
        return ""

    # Order is done this way, because IF it's a flywheel file, it's possible that the
    # MIMEtype may not be populated correctly or recognized, however the file may still
    # have a valid extension, which we want to extract from the flywheel object
    mime = None
    if isinstance(input_file, dict):
        mime, input_file = get_fw_type_info(input_file)
    ext = get_ext(input_file)
    input_file_type = validate_filetype(ext, mime)

    return input_file_type
