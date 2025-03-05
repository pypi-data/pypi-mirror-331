import tomli
from appdirs import *

class Cfg:
    def __init__(self):
        appname = "cdm"
        cfg_dir = user_config_dir(appname)
        cfg_file = cfg_dir + "/frontend.toml"

        with open(cfg_file, mode="rb") as fp:
            self._cfg = tomli.load(fp)

    def get_cdm_addr(self):
        return self._cfg["cdm"]
