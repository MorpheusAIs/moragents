import logging
import logging.config
import os

from configparser import ConfigParser
from typing import Any, Callable, TypeVar, Optional

BASE_DIR = "./config"


T = TypeVar("T")


class Config:
    """
    wrapper class for python ConfigParser class.  will check environment variables
    for config values before checking config file properties
    """

    _instance: Optional["Config"] = None
    _env_vars: dict[str, str]
    _conf: ConfigParser

    def __new__(cls) -> "Config":
        """Singleton like pattern"""
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Config object"""
        self._env_vars = dict(os.environ.copy())
        self._load()

    @classmethod
    def get_instance(cls) -> "Config":
        """Singleton like pattern"""
        if not cls._instance:
            cls._instance = Config()
        return cls._instance

    def _load(self) -> None:
        """Load config from config file and environment variables"""
        # load base config
        conf_parser = ConfigParser()
        base_config = f"{BASE_DIR}/config.ini"
        print(f"loading base config: {base_config}")
        with open(base_config, "r", encoding="utf-8") as handle:
            conf_parser.read_file(handle)

        # load env specific config
        env = os.environ.get("ENV")
        if not env:
            env = "dev"
        env_conf = f"{BASE_DIR}/config-{env.lower()}.ini"
        if os.path.isfile(env_conf):
            print(f"loading config: {env_conf}")
            with open(env_conf, "r", encoding="utf-8") as handle:
                conf_parser.read_file(handle)

        # load local config if set
        local_conf_file = os.environ.get("LOCAL_CONF")
        if not local_conf_file:
            local_conf_file = f"{BASE_DIR}/local.conf"
        if os.path.isfile(local_conf_file):
            print(f"loading additional config: {local_conf_file}")
            with open(local_conf_file, "r", encoding="utf-8") as handle:
                conf_parser.read_file(handle)

        self._conf = conf_parser
        self._app_config_init()

    def _app_config_init(self) -> None:
        """Initialize app config"""
        logging.config.fileConfig(f'{BASE_DIR}/{self.get("logging_config")}')

        # disable noisy loggers
        logging.getLogger("google.cloud.pubsub_v1").setLevel(logging.WARNING)

    def get(self, key: str, section: str = "default", type_conv: Callable[[str], T] = lambda x: x) -> T:
        """Get config value for key, section.  If not found in config file, check environment variables"""
        value = self._env_vars.get(key)

        if not value:
            value = self._conf[section][key]

        return type_conv(value)

    def get_bytes(self, key: str, section: str = "default") -> bytes:
        """Get config value for key, section and cast to bytes"""
        return self.get(key, section, lambda s: s.encode("utf-8"))

    def get_bool(self, key: str, section: str = "default") -> bool:
        """Get config value for key, section and cast to boolean"""
        return self.get(key, section, lambda s: s.lower() in ["true", "1"])

    def get_int(self, key: str, section: str = "default") -> int:
        """Get config value for key, section and cast to integer"""
        return self.get(key, section, int)

    def get_float(self, key: str, section: str = "default") -> float:
        """Get config value for key, section and cast to float"""
        return self.get(key, section, float)

    def get_list(self, key: str, section: str = "default", sep: str = ",") -> list[str]:
        """Get config value for key, section and cast to list"""
        value = self.get(key, section)
        if not isinstance(value, str):
            raise TypeError(f"Expected string value for {key}, got {type(value)}")
        str_list = value.strip()
        return [] if str_list == "" else [s.strip() for s in str_list.split(sep)]
