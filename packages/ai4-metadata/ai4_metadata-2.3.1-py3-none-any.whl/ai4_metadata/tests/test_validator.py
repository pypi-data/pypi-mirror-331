"""Unit tests for the validator module."""

import pathlib
import pytest

from ai4_metadata import exceptions
from ai4_metadata import utils
from ai4_metadata import validate


@pytest.fixture
def valid_schema_file():
    """Fixture for a valid schema file."""
    return pathlib.Path(__file__).parent / "../schemata/ai4-apps-v2.0.0.json"


@pytest.fixture
def invalid_schema_file():
    """Fixture for an invalid schema file."""
    return ""


@pytest.fixture
def valid_instance():
    """Fixture for a valid instance."""
    i = pathlib.Path(__file__).parent / "../../../instances/sample-v2.mods.json"
    return utils.load_json(i)


@pytest.fixture
def valid_instance_file():
    """Fixture for a valid instance."""
    return pathlib.Path(__file__).parent / "../../../instances/sample-v2.mods.json"


@pytest.fixture
def valid_yaml_instance():
    """Fixture for a valid instance."""
    i = pathlib.Path(__file__).parent / "../../../instances/sample-v2.mods.yaml"
    return utils.load_yaml(i)


@pytest.fixture
def valid_yaml_instance_file():
    """Fixture for a valid instance."""
    return pathlib.Path(__file__).parent / "../../../instances/sample-v2.mods.yaml"


@pytest.fixture
def invalid_instance():
    """Fixture for an invalid instance."""
    return {"foo": "bar"}


@pytest.fixture
def invalid_instance_file():
    """Fixture for an invalid instance."""
    return pathlib.Path(__file__).parent / "../../../instances/invalid.json"


@pytest.fixture
def not_found_instance_file():
    """Fixture for an invalid instance."""
    return pathlib.Path(__file__).parent / "foo/bar/baz/instance.json"


def test_validator(valid_schema_file, valid_instance_file):
    """Test the validator with a loaded JSON."""
    assert validate.validate(valid_instance_file, valid_schema_file) is None


def test_validator_file(valid_schema_file, valid_instance):
    """Test the validator with a JSON file."""
    assert validate.validate(valid_instance, valid_schema_file) is None


def test_validator_yaml(valid_schema_file, valid_yaml_instance):
    """Test the validator with a loaded YAML."""
    assert validate.validate(valid_yaml_instance, valid_schema_file) is None


def test_validator_yaml_file(valid_schema_file, valid_yaml_instance_file):
    """Test the validator with a YAML file."""
    assert validate.validate(valid_yaml_instance_file, valid_schema_file) is None


def test_validator_invalid_instance(valid_schema_file, invalid_instance):
    """Test the validator with an invalid instance."""
    with pytest.raises(exceptions.MetadataValidationError):
        validate.validate(invalid_instance, valid_schema_file)


def test_validator_invalid_instance_file(valid_schema_file, invalid_instance_file):
    """Test the validator with an invalid instance file."""
    with pytest.raises(exceptions.MetadataValidationError):
        validate.validate(invalid_instance_file, valid_schema_file)


def test_validator_not_found_instance_file(valid_schema_file, not_found_instance_file):
    """Test the validator with a not found instance file."""
    with pytest.raises(exceptions.FileNotFoundError):
        validate.validate(not_found_instance_file, valid_schema_file)


def test_validator_invalid_schema(invalid_schema_file, valid_instance):
    """Test the validator with an invalid schema."""
    with pytest.raises(exceptions.SchemaValidationError):
        validate.validate(valid_instance, invalid_schema_file)


def test_validator_invallid_all(invalid_schema_file, invalid_instance):
    """Test the validator with an invalid schema and instance."""
    with pytest.raises(exceptions.SchemaValidationError):
        validate.validate(invalid_instance, invalid_schema_file)
