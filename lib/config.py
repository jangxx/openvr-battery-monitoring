import json
import os
from typing import Optional

from deepmerge.merger import Merger
from pydantic import BaseModel, field_validator
from appdirs import user_config_dir

CONFIG_DIR = user_config_dir("OpenVR Battery Monitoring", "jangxx")

DefaultConfigDict: dict = {
    "muted_devices": [],
    "update_interval": 10,
    "notifications": {
        "play_sound": True,
        "desktop": True,
        "ovrt": False,
    }
}

class ConfigNotificationsModel(BaseModel):
    play_sound: bool
    desktop: bool
    ovrt: bool

class ConfigModel(BaseModel):
    muted_devices: list[str]
    update_interval: int
    notifications: ConfigNotificationsModel

    @field_validator("update_interval")
    def validate_update_interval(cls, v):
        return max(v, 1)

ConfigMerger = Merger(
    [
        (list, ["append"]),
        (dict, ["merge"]),
        (set, ["union"]),
    ],
    ["override"],
    ["override_if_not_empty"]
)

class Config:
    _config_path = os.path.join(CONFIG_DIR, "config.json")
    _config: ConfigModel

    def __init__(self):
        config_dict = DefaultConfigDict

        if os.path.exists(self._config_path):
            with open(self._config_path, "r") as config_file:
                try:
                    config_file_content = json.load(config_file)
                    config_dict = ConfigMerger.merge(config_dict, config_file_content)
                except:
                    pass

        self._config = ConfigModel(**config_dict)

    def save(self):
        with open(self._config_path, "w+") as config_file:
            config_file.write(self._config.model_dump_json(indent=4))

    @property
    def data(self) -> ConfigModel:
        return self._config