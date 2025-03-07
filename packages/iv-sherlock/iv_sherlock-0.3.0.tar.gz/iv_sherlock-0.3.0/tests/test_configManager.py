import json
import os
import pytest
import tempfile
import toml
from iv_sherlock.config_manager import Config


@pytest.fixture
def custom_config():
    return {'report': {'source_path': '/tmp/iv_sherlock/data', 'out_path': '/tmp/iv_sherlock/data/tmp',
                       'default_encoding': 'ASCII', 'export_pdf': True}, 'cvss': {'score_mapping': ''}}


@pytest.fixture
def score_mapping_dict():
    return {'AV': {'N': 0.85, 'A': 0.62}, 'AC': {'L': 0.77, 'H': 0.44}, 'PR': {'N': 0.85, 'L': 0.62, 'H': 0.27},
            'UI': {'N': 0.85, 'R': 0.62}, 'S': {'U': 1.0, 'C': 1.08}, 'C': {'H': 0.56, 'L': 0.22, 'N': 0.0},
            'I': {'H': 0.56, 'L': 0.22, 'N': 0.0}, 'A': {'H': 0.56, 'L': 0.22, 'N': 0.0}}


@pytest.fixture
def score_mapping_str(score_mapping_dict):
    return json.dumps(score_mapping_dict)


@pytest.fixture
def default_config(score_mapping_str):
    return {
        'report': {'source_path': '/home/pliu/git/ImageVulnAnalyzer/src/iv_sherlock/data',
                   'out_path': '/home/pliu/git/ImageVulnAnalyzer/src/iv_sherlock/data/tmp',
                   'default_encoding': 'utf-8', 'export_pdf': False},
        'cvss': {
            'score_mapping': score_mapping_str }}


@pytest.fixture
def temp_config_files(custom_config):
    """Fixture to create temporary config files for testing."""
    temp_dir = tempfile.TemporaryDirectory()
    default_config_path = os.path.join(temp_dir.name, "default_config.toml")
    custom_config_path = os.path.join(temp_dir.name, "custom_config.toml")

    # Create a user config file with overridden values
    with open(custom_config_path, "w") as f:
        toml.dump(custom_config, f)

    yield temp_dir.name, default_config_path, custom_config_path

    temp_dir.cleanup()  # Cleanup after test


@pytest.fixture
def config(temp_config_files):
    """Fixture to initialize the Config instance with test files."""
    temp_dir, default_config_path, custom_config_path = temp_config_files
    config_instance = Config(custom_config_path)
    return config_instance

@pytest.fixture
def config_without_custom_input():
    config_instance = Config()
    return config_instance


def test_default_config_loading(config, default_config):
    """Test if default config values are loaded correctly."""
    expected_default_config = default_config
    print(config._default_config)
    assert config._default_config == expected_default_config


def test_custom_config_loading(config, custom_config):
    """Test if custom config values are loaded correctly."""
    expected_custom_config = custom_config
    print(config._custom_config)
    assert config._custom_config == expected_custom_config


def test_get_input_report_path(config):
    """Test if the input report path is correct."""
    expected_in_path = "/tmp/iv_sherlock/data"
    actual_in_path = config.get_input_report_path()
    print(actual_in_path)
    assert actual_in_path == expected_in_path


def test_get_output_report_path(config):
    """Test if the output report path is correct."""
    expected_out_path = "/tmp/iv_sherlock/data/tmp"
    actual_out_path = config.get_output_report_path()
    print(actual_out_path)
    assert actual_out_path == expected_out_path


def test_get_export_pdf(config):
    """Test if the value export pdf is correct."""
    expected_pdf_val = True
    actual_pdf = config.get_export_pdf()
    print(actual_pdf)
    assert actual_pdf == expected_pdf_val


def test_get_default_encoding(config):
    """Test if the value default encoding is correct."""
    expected_encoding = "ASCII"
    actual_encoding = config.get_default_encoding()
    print(actual_encoding)
    assert actual_encoding == expected_encoding


def test_get_cvss_vector_value_mapping(config,score_mapping_dict):
    """Test if the cvss vector value mapping is correct."""
    actual_cvss = config.get_cvss_vector_value_mapping()
    print(actual_cvss)
    assert actual_cvss == score_mapping_dict


def test_get_input_report_path_without_custom_input(config_without_custom_input):
    """Test if the input report path is correct. As no custom config, the default config is used"""
    expected_in_path = "/home/pliu/git/ImageVulnAnalyzer/src/iv_sherlock/data"
    actual_in_path = config_without_custom_input.get_input_report_path()
    print(actual_in_path)
    assert actual_in_path == expected_in_path


def test_get_output_report_path_without_custom_input(config_without_custom_input):
    """Test if the output report path is correct."""
    expected_out_path = "/home/pliu/git/ImageVulnAnalyzer/src/iv_sherlock/data/tmp"
    actual_out_path = config_without_custom_input.get_output_report_path()
    print(actual_out_path)
    assert actual_out_path == expected_out_path


def test_get_export_pdf_without_custom_input(config_without_custom_input):
    """Test if the value export pdf is correct."""
    expected_pdf_val = False
    actual_pdf = config_without_custom_input.get_export_pdf()
    assert actual_pdf == expected_pdf_val


def test_get_cvss_vector_value_mapping_without_custom_input(config_without_custom_input, score_mapping_dict):
    """Test if the value export pdf is correct."""
    expected_mapping = score_mapping_dict
    actual_mapping = config_without_custom_input.get_cvss_vector_value_mapping()
    print(actual_mapping)
    assert actual_mapping == expected_mapping



def test_get_default_encoding_without_custom_input(config_without_custom_input):
    """Test if the value default encoding is correct."""
    expected_encoding = "utf-8"
    actual_encoding = config_without_custom_input.get_default_encoding()
    print(actual_encoding)
    assert actual_encoding == expected_encoding


def test_get_cvss_vector_value_without_custom_input(config_without_custom_input,score_mapping_dict):
    """Test if the cvss vector value mapping is correct."""
    actual_cvss = config_without_custom_input.get_cvss_vector_value_mapping()
    print(actual_cvss)
    assert actual_cvss == score_mapping_dict

def test_singleton_behavior(temp_config_files):
    """Test that multiple instances reference the same config."""
    _,_,custom_config_path = temp_config_files
    # create config1 without a custom config
    config1 = Config()
    config1_expected_encoding = "utf-8"
    config1_actual_encoding = config1.get_default_encoding()
    assert config1_expected_encoding == config1_actual_encoding
    # create config2 with a custom config
    config2 = Config(custom_config_path)
    config2_expected_encoding = "ASCII"
    config2_actual_encoding = config2.get_default_encoding()
    assert config2_expected_encoding == config2_actual_encoding
    # as config1 and config2 point to the same object, so the value of config1 is updated too.
    config1_encoding_after_config2 = config1.get_default_encoding()
    assert config1_encoding_after_config2 == config2_expected_encoding
    assert config2_actual_encoding == config1_encoding_after_config2 # Singleton should share state

