import json
import tomllib  # Use 'import toml' if using Python < 3.11
from importlib import resources

from iv_sherlock.cve_evaluator import check_vector_score_mapping_validity


class Config:
    _instance = None  # Singleton instance

    def __new__(cls, custom_config_path: str = None):
        """
        Initiate a Config instance and ensure only one instance exists (Singleton).
        :param custom_config_path:
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # load the default config
            cls._instance._default_config = tomllib.loads(resources.read_text("iv_sherlock.conf", "config.toml"))
            # create custom config
            cls._instance._custom_config={}
        # if a custom config file is provided, load the custom config
        if custom_config_path:
            cls._instance._custom_config = cls.load_custom_config(custom_config_path)
        # merge the default and custom config
        cls._instance._config = cls.merge_dicts(cls._instance._default_config, cls._instance._custom_config)
        return cls._instance

    @staticmethod
    def load_custom_config(config_path:str):
        """
        Loads a TOML config file and return the corresponding config dictionary.
        :param config_path: Input config file path.
        :return:
        """
        custom_config = {}
        try:
            with open(config_path, "rb") as f:
                custom_config = tomllib.load(f)
        except FileNotFoundError:
            print(f"Warning: User config file {config_path} not found. Ignoring user config.")
        except Exception as e:
            print(f"Error loading config file {config_path}: {e}")
        return custom_config

    @staticmethod
    def merge_dicts(default_config: dict, custom_config: dict) -> dict:
        """
        Recursively merge two dictionaries, keeping default values if custom values are missing or empty.
        :param default_config: A dict contains the default values
        :param custom_config: A dict contains the custom values
        :return:
        """
        merged_config = default_config.copy()  # Start with default values

        for key, value in custom_config.items():
            # Recursively merge nested dicts
            if isinstance(value, dict) and key in merged_config:
                merged_config[key] = Config.merge_dicts(merged_config[key], value)
            # Ignore empty string values, keeping the default
            elif value is None or value == "" or value == " ":
                continue
            # Override with non-empty values
            else:
                merged_config[key] = value
        return merged_config

    def get_input_report_path(self)->str:
        return self._config["report"]["source_path"]

    def get_output_report_path(self)->str:
        return self._config["report"]["out_path"]

    def get_export_pdf(self)->bool:
        return self._config["report"]["export_pdf"]

    def get_default_encoding(self)->str:
        return self._config["report"]["default_encoding"]

    def get_cvss_vector_value_mapping(self)->dict:
        # use the custom score mapping string first
        custom_score_map_str:str = self._custom_config.get("cvss", {}).get("score_mapping")
        # if no custom score map is provided, use the default value
        if (custom_score_map_str is not None) and (custom_score_map_str.strip()!=""):
            # check the validity of the custom vector_map
            custom_score_map_dict = json.loads(custom_score_map_str)
            resu, comments = check_vector_score_mapping_validity(custom_score_map_dict)
            # if the custom vector score is valid, use the custom score mapping
            if resu:
                return custom_score_map_dict
            else:
                print("The provided cvss vector score mapping is invalid. Use the default value")
                return self.get_default_cvss_vector_value_mapping()
        else:
            print("Can't find cvss score mapping in the custom config file. Use the default value")
            return self.get_default_cvss_vector_value_mapping()


    def get_default_cvss_vector_value_mapping(self)->dict:
        """
        This method returns the default cvss vector score mapping.
        :return:
        """
        default_score_map_str = self._default_config["cvss"]["score_mapping"]
        return json.loads(default_score_map_str)

    @staticmethod
    def get_report_template_dir_path()->str:
        """
        This method returns the path to the output report template directory.
        :return: Path to the output report template directory
        """
        return str(resources.files("iv_sherlock") / "templates")






# Initialize the config singleton on first import
config = Config()
