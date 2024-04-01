import logging
import typing as t
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import flywheel
import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils.datatypes import Container
from fw_gear_file_validator.validator import null

PARENT_ORDER = [
    "group",
    "project",
    "subject",
    "session",
    "acquisition",
    "analysis",
    "file",
]

log = logging.getLogger()

N_TRIES = 5
SLEEP_TIME = 5


@dataclass
class FwReference:
    """A reference to a flywheel object (being a container or a gear input file).

    Host a set of methods to facilitate the loading of the object in its specific
    context (gear input file, flywheel container or flywheel file).

    Attributes:
        id: str, the id of the container
        object: flywheel object, the flywheel object
        type: str, the type of the container
        parents: dict, the parents of the container
        name: str, the name of the container
        is_file: bool, True if the object is a file, False otherwise
        ref: dict, the reference to the object, basically the parent dictionary plus the object itself.
        _client: flywheel.Client, the flywheel client

    Properties (cached):
        parent_type: str, container type of the object's parent
        parent_id: str: The container ID of the object's parent
        my_object: the full flywheel object.


    """

    id: str = None
    input_object: t.Union[
        flywheel.ContainerReference,
        flywheel.FileReference,
        flywheel.JobFileInput,
        dict,
    ] = None
    type: str = None
    parents: dict = None
    name: str = None
    file_type: str = None
    ref: dict = None
    _client: flywheel.Client = None
    contents: str = None

    @classmethod
    def init_from_gear_input(
        cls,
        fw_client: flywheel.Client,
        gear_input: t.Union[dict, flywheel.models.JobFileInput],
        content: str = None,
    ):
        """
        Initialize a flywheel reference object from a gear input file
        Args:
            fw_client: a flywheel client
            gear_input: a JobFileInput
            content: "file" or "flywheel", indicating if the desire is to load a file's content,
                or the flywheel object.

        Returns:
            FwReference

        """

        if "label" in gear_input:
            raise ValueError("Only files are valid FwReference Inputs")

        file_object = fw_client.get_file(gear_input.get("object", {}).get("file_id"))
        return cls(
            input_object=gear_input,
            id=file_object["file_id"],
            type="file",
            name=file_object.name,
            file_type=file_object.type,
            _client=fw_client,
            parents=dict(file_object.parents),
            contents=content,
        )

    def __post_init__(self) -> None:
        self.path_is_valid()
        self.parents = {k: v for k, v in self.parents.items() if v}  # remove None's
        self.ref = {**self.parents, self.type: self.id}

    def path_is_valid(self) -> bool:
        """Returns True if the file path is valid, raise exception otherwise."""
        if self.file_path and not self.file_path.exists():
            raise ValueError(f"File {self.file_path} does not exist")
        return True

    @cached_property
    def file_path(self) -> t.Union[Path, None]:
        """If present returns the file path"""
        if self.input_object and "location" in self.input_object:
            path = Path(self.input_object["location"]["path"])
        else:
            path = None
        return path

    @cached_property
    def parent_type(self) -> str:
        """Returns the type of the parent."""
        for p in PARENT_ORDER[::-1]:
            if p in self.parents and self.parents[p] is not None:
                return p

    @cached_property
    def parent_id(self) -> str:
        """Returns the id of the parent."""
        for p in PARENT_ORDER[::-1]:
            if p in self.parents and self.parents[p] is not None:
                return self.parents[p]

    @property
    def loc(self) -> t.Union[Path, dict]:
        """Returns location of the object."""
        if self.contents == "file":
            if self.file_path:
                return self.file_path
            return Path("")
        elif self.contents == "flywheel":
            return self.hierarchy_objects

    @property
    def client(self) -> flywheel.Client:
        """Returns the Flywheel client."""
        if not self._client:
            raise ValueError("Client not set. Use set_client() to set the client.")
        return self._client

    def set_client(self, client: flywheel.Client):
        """Sets the Flywheel client as attribute."""
        self._client = client

    def get_lookup_path(self, level: str = None) -> str:
        """Returns the Flywheel path of the Flywheel object."""
        hierarchy_parts = []
        for k in PARENT_ORDER:
            if k in self.hierarchy_objects:
                if k == "file":
                    hierarchy_parts.append(self.hierarchy_objects[k].get("name"))
                else:
                    hierarchy_parts.append(self.hierarchy_objects[k].get("label"))
            if k == level:
                break
        return "fw://" + "/".join(hierarchy_parts)

    @cached_property
    def fw_object(self) -> Container:
        """Returns the container for the provided Flywheel reference."""
        return self.get_level_object(self.type)

    @cached_property
    def hierarchy_objects(self):
        hierarchy = {}
        for level in self.ref.keys():
            fw_object = self.get_level_object(level)
            if fw_object is None:
                continue
            hierarchy[level] = fw_object
        return hierarchy

    def get_level_object(self, level) -> t.Union[dict, Container, flywheel.Group, None]:
        """Returns all the parent containers."""
        if level not in self.ref.keys():
            return None
        if level == "group":
            return flywheel.Group(label=self.parents['group'])

        p_id = self.ref[level]
        getter = getattr(self.client, f"get_{level}")
        fw_object = getter(p_id)
        return fw_object


def add_tags_metadata(
    context: flywheel_gear_toolkit.GearToolkitContext,
    fw_ref: FwReference,
    valid,
    tag,
):
    state = "PASS" if valid else "FAIL"

    log.debug("tagging file")
    input_filename = context.get_input_filename("input_file")
    file_ = fw_ref.fw_object
    fail_tag = f"{tag}-FAIL"
    pass_tag = f"{tag}-PASS"
    tag = f"{tag}-{state}"
    input_object = context.get_input("input_file")
    tags = file_.tags
    if state == "PASS" and fail_tag in tags:
        tags.remove(fail_tag)
        context.metadata.update_file(input_filename, tags=tags)
    elif state == "FAIL" and pass_tag in tags:
        tags.remove(pass_tag)
        context.metadata.update_file(input_filename, tags=tags)

    context.metadata.add_file_tags(input_object, str(tag))


def cast_csv_val(val: t.Any, cast_types: [type]):
    """Attempt to cast a type.  Return original value if unsuccessful

    Args:
        val: the value to cast
        cast_type: the type to cast it to

    Returns:
        cast_type(val) | val

    """
    # Earlier in the code we enforce that the ONLY accepted double type is null and something else.
    # So in theory at this point we only have a list of length one or two, where one element is null.
    # But it WOULD be nice to kinda automate this...

    # So here is a first stab with no assumptions on the incoming data:
    # If we're only attempting one cast:
    if len(cast_types) == 1:
        return cast_one(val, cast_types[0])

    # If we have multiple casts, and "null" is one of them, and it's possible to cast, return that.
    if null in cast_types:
        try:
            return null(val)
        except ValueError:
            # Remove null so we dont mess with it in the future
            cast_types.remove(null)

    # If there were only two, "null" and some other value, just try to cast it, whatever
    if len(cast_types) == 1:
        return cast_one(val, cast_types[0])

    # If we have more than one element AND "null" is not present, see if each element is castable to the desired type:
    castable = []
    for i, cast_type in enumerate(cast_types):
        try:
            cast_type(val)
            castable.append(i)
        except ValueError:
            pass

    if len(castable) > 1:
        raise ValueError(f"Value {val} can be cast to multiple types {[cast_types[c] for c in castable]}, please specify")
    if not any(castable):
        # If nothing works return the value, the validator will catch it
        return val
    # If we're here, there should be only one.  Phew
    return cast_types[castable[0]](val)


def cast_one(val, cast_type: type):
    try:
        return cast_type(val)
    except ValueError:
        return val


def get_loader_type(fw_ref):
    if fw_ref.contents == "flywheel":
        return fw_ref.contents
    return fw_ref.file_type
