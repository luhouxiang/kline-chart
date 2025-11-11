#! -*- coding: utf-8 -*-
import os
from pathlib import Path
import yaml


conf = dict()


def load_yaml(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


# Resolve config path relative to this module so imports work when the CWD varies.
HERE = Path(__file__).resolve().parent.parent
DEFAULT_CONF = HERE.parent.joinpath('etc', 'config.yaml')
if DEFAULT_CONF.exists():
    conf = load_yaml(str(DEFAULT_CONF))
else:
    # Fallback to given relative path for backward compatibility
    conf = load_yaml(os.path.join(HERE, '..', 'etc', 'config.yaml'))
