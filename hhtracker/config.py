import yaml
from addict import Dict


def read_config():
    cfg = Dict(yaml.load(open("./config.yml")))
    for key in cfg.keys():
        val = getattr(cfg, key)
        globals()[key] = val


read_config()
del globals()["read_config"]
