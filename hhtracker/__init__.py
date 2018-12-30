import os
import yaml
from addict import Dict


def _load_config():
    configfile = os.environ.get("HHTRACKER_CONFIG") or "config.yml"
    return Dict(yaml.load(open(configfile)))


config = _load_config()
