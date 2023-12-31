from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flywheel import Acquisition, FileEntry, Group, Project, Session, Subject

from fw_gear_file_validator import utils

PARENT_ORDER = utils.PARENT_ORDER
FwReference = utils.FwReference

BASE_DIR = d = Path(__file__).resolve().parents[1]
BASE_DIR = BASE_DIR / "tests"
test_config = BASE_DIR / "assets" / "config.json"


def test_is_valid():
    with pytest.raises(ValueError):
        ref = FwReference(file_path=Path("does/not/exist.txt"))

    ref = FwReference(file_path=Path(test_config))
    assert ref.is_valid()

    with pytest.raises(ValueError):
        ref = FwReference(cont_type="none")

    for parent in PARENT_ORDER:
        ref = FwReference(cont_type=parent)
        assert ref.is_valid()


def test_loc():
    ref = FwReference(file_path=Path(test_config))
    assert ref.loc() == Path(test_config)

    ref = FwReference(cont_type="subject")
    assert ref.loc() == ref


def test_validate_file_contents():
    ref = FwReference(file_path=Path(test_config))
    assert ref.validate_file_contents()

    ref = FwReference(cont_type="subject")
    assert ref.validate_file_contents() is False


def test_client():
    client = MagicMock
    ref = FwReference(file_path=Path(test_config))
    with pytest.raises(ValueError):
        ref.client

    ref = FwReference(file_path=Path(test_config), _client=client)
    assert ref.client == client


def test_container():
    ses_id = "63ceeda12bae5aafaf66306e"
    file_name = "json_classifier.yaml"
    file_type = "json"

    client = MagicMock()

    ref = FwReference(
        cont_type="session",
        cont_id=ses_id,
        _client=client,
    )
    ref.container
    client.get_session.assert_called_once()
    client.get_session().get_file.assert_not_called()

    client = MagicMock()
    ref = FwReference(
        cont_type="session",
        cont_id=ses_id,
        _client=client,
        file_name=file_name,
        file_type=file_type,
    )

    ref.container
    client.get_session().get_file.assert_called_once()


def test_parents():
    ses_id = "63ceeda12bae5aafaf66306e"
    file_id = "6442edd40e732989de85e54d"
    file_name = "json_classifier.yaml"
    file_type = "json"

    client = MagicMock()
    ref = FwReference(cont_type="session", cont_id=ses_id, _client=client)
    parents = ref.parents

    client.get_session.assert_called_once()
    client.get_session().get_file.assert_not_called()
    client.get_session().parents.items.assert_called_once()

    client = MagicMock()
    ref = FwReference(
        cont_type="session",
        cont_id=ses_id,
        _client=client,
        file_name=file_name,
        file_type=file_type,
    )

    parents = ref.parents
    client.get_session().get_file.assert_called_once()
    client.get_session().get_file().parents.items.assert_called_once()


def test_all():
    acq_id = "63ceedbd866bff5a5fc6082e"
    file_name = "test_json_form.json"
    file_type = "json"

    client = MagicMock()
    ref = FwReference(cont_type="acquisition", cont_id=acq_id, _client=client)

    a = ref.all

    client.get_acquisition.assert_called_once()
    client.get_acquisition().parents.items.assert_called_once()
    client.get_acquisition().get_file.assert_not_called()

    client = MagicMock()

    ref = FwReference(
        cont_type="acquisition",
        cont_id=acq_id,
        _client=client,
        file_name=file_name,
        file_type=file_type,
    )

    b = ref.all
    client.get_acquisition.assert_called_once()
    client.get_acquisition().get_file.assert_called_once()
    client.get_acquisition().get_file().parents.items.assert_called_once()


def test_get_lookup_path():
    fw_ref = FwReference(
        cont_id="test_container_id",
        cont_type="acquisition",
        file_name="test_file_name.ext",
        file_path=None,
        file_type="test_file_type",
        _client=None,
    )

    group = Group()
    group.label = "test_group"
    project = Project()
    project.label = "test_project"
    subject = Subject()
    subject.label = "test_subject"
    session = Session()
    session.label = "test_session"
    acquisition = Acquisition()
    acquisition.label = "test_acquisition"
    file = FileEntry()
    file.name = "test_file_name.ext"

    parent_dict = {
        "group": group,
        "project": project,
        "subject": subject,
        "session": session,
        "acquisition": acquisition,
        "file": file,
    }

    fw_ref.__dict__["container"] = file
    fw_ref.__dict__["parents"] = parent_dict

    url = f"fw://{group.label}/{project.label}/{subject.label}/{session.label}/{acquisition.label}/{file.name}"
    assert fw_ref.get_lookup_path() == url

    url = f"fw://{group.label}/{project.label}/{subject.label}/{session.label}/{acquisition.label}"
    assert fw_ref.get_lookup_path(level="acquisition") == url

    url = f"fw://{group.label}/{project.label}/{subject.label}/{session.label}"
    assert fw_ref.get_lookup_path(level="session") == url

    url = f"fw://{group.label}/{project.label}/{subject.label}"
    assert fw_ref.get_lookup_path(level="subject") == url

    url = f"fw://{group.label}/{project.label}"
    assert fw_ref.get_lookup_path(level="project") == url

    url = f"fw://{group.label}"
    assert fw_ref.get_lookup_path(level="group") == url


def test_container_retrys():
    utils.SLEEP_TIME = 0.1

    my_client = MagicMock()
    my_client.get_session = MagicMock(return_value=None)
    fw_ref = FwReference(
        cont_id="test_container_id",
        cont_type="session",
        file_name="test_file_name.ext",
        file_path=None,
        file_type="test_file_type",
        _client=my_client,
    )

    with pytest.raises(ValueError) as e_info:
        fw_ref.container

    assert my_client.get_session.call_count == utils.N_TRIES


def test_parent_retrys():
    utils.SLEEP_TIME = 0.1

    my_client = MagicMock()
    session = Session()
    session.label = "test_session"
    session.parents = {
        "group": "gid",
        "project": "pid",
        "subject": "sid",
        "session": None,
        "acquisition": None,
    }

    my_client.get_session = MagicMock(return_value=session)
    my_client.get_subject = MagicMock(return_value=None)
    my_client.get_project = MagicMock(return_value=None)
    my_client.get_group = MagicMock(return_value=None)

    fw_ref = FwReference(
        cont_id="test_container_id",
        cont_type="session",
        file_name=None,
        file_path=None,
        file_type=None,
        _client=my_client,
    )

    with pytest.raises(ValueError) as e_info:
        fw_ref.parents

    assert my_client.get_group.call_count == utils.N_TRIES
