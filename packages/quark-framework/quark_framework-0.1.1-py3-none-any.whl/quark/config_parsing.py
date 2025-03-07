import yaml
# from dataclasses import dataclass

from quark.modules.Core import Core

# @dataclass(frozen=True)
# class Config:
#     # List of benchmarking piplines consisting of tuples of core modules with their respective configurations
#     pipelines: list[list[tuple[Core, dict]]]

def parse_config_file(path: str) -> list[list[tuple[Core, dict]]]:
    # List of benchmarking piplines consisting of tuples of core modules with their respective configurations
    with open(path, 'r') as file:
        return yaml.safe_load(file)