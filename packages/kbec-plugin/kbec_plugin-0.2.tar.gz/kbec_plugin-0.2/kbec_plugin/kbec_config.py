import json
import os

from typing import Any

class KBecConfig:
    def __init__(self, config_path: str) -> None:
        self.plugin_name: str = None
        self.plugin_creator: str = None
        self.plugin_version: str = None
        self.plugin_url: str = None

        self.plugin_config_path: str = os.path.abspath(config_path)
        self.config_json_raw: dict[str: Any] = None

        self.load_config()

    def load_config(self) -> None:
        with open(self.plugin_config_path, "r") as config_file:
            self.config_json_raw = json.load(config_file)

        self.plugin_name = self.config_json_raw["plugin"]["name"]
        self.plugin_creator = self.config_json_raw["plugin"]["creator"]
        self.plugin_version = self.config_json_raw["plugin"]["version"]
        self.plugin_url = self.config_json_raw["plugin"]["url"]

    @property
    def plugin_info(self) -> str:
        return f"{self.plugin_name} {self.plugin_version}, created by {self.plugin_creator} ({self.plugin_url})"