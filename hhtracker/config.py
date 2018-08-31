import yaml
from addict import Dict


config = Dict(yaml.load(open("./config.yml")))
