import json
import os
import tempfile
import toml
import pytest

from iv_sherlock.config_manager import Config
from iv_sherlock.report_generator import ReportGenerator


@pytest.fixture
def custom_config():
    custom_score = {"AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
                    "AC": {"L": 0.77, "H": 0.44},
                    "PR": {"N": 0.85, "L": 0.62, "H": 0.27},
                    "UI": {"N": 0.85, "R": 0.62},
                    "S": {"U": 1.0, "C": 1.08},
                    "C": {"H": 0.56, "L": 0.22, "N": 0.0},
                    "I": {"H": 0.56, "L": 0.22, "N": 0.0},
                    "A": {"H": 0.0, "L": 0.0, "N": 0.0}}
    custom_score_str = json.dumps(custom_score)
    data_dir = '/home/pliu/tmp/iv_sherlock/data'
    return {'report': {'source_path': f"{data_dir}", 'out_path': f'{data_dir}/tmp',
                       'default_encoding': 'utf-8', 'export_pdf': False},
            'cvss': {'score_mapping': f'{custom_score_str}'}}


@pytest.fixture
def temp_config_files(custom_config):
    """Fixture to create temporary config files for testing."""
    temp_dir = tempfile.TemporaryDirectory()

    custom_config_path = os.path.join(temp_dir.name, "custom_config.toml")

    # Create a user config file with overridden values
    with open(custom_config_path, "w") as f:
        toml.dump(custom_config, f)

    yield temp_dir.name, custom_config_path

    temp_dir.cleanup()  # Cleanup after test


@pytest.fixture
def report_generator(temp_config_files):
    temp_dir, custom_config_path = temp_config_files
    config = Config(custom_config_path)
    rg = ReportGenerator(config)
    return rg


def test_generate_reports_from_source_dir(report_generator):
    """This tests the report generation by using the given directory path. The directory contains the """
    report_generator.generate_reports_from_source_dir()
