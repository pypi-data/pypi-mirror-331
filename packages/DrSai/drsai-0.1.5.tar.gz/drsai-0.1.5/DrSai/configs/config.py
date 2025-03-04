# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os, sys
import yaml
from pathlib import Path
here = Path(__file__).parent


def load_configs(config_path=None, include_env=False):
    """
    Load the configuration from a YAML file and environment variables.

    :param config_path: The path to the YAML config file. Defaults to "./config.yaml".
    :return: Merged configuration from environment variables and YAML file.
    """
    # Copy environment variables to avoid modifying them directly
    config_path = config_path or os.path.join(here, "config.yaml")
    configs = dict(os.environ) if include_env else {}
    if config_path and not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    try:
        with open(config_path, "r") as file:
            yaml_data = yaml.safe_load(file)
        # Update configs with YAML data
        if yaml_data:
            configs.update(yaml_data)
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}. Using only environment variables.")

    return configs


def get_llm_config(configs):
    """
    Get the LLM configuration from the configs.

    :param configs: The configuration dictionary.
    :return: The LLM configuration.
    """
    llm_config = configs['llm_config']
    llm_config['config_list'] = configs.get('models_config_list', None)
    return llm_config




