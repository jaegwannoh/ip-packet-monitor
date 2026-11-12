# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import io
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = BASE_DIR.decode(sys.getfilesystemencoding())


def load_config(path):
    cfg = {'MONITOR_IP': '', 'HOST': '', 'PORT': '22', 'USER': '',
           'PASSWORD': '', 'REMOTE_DIR': '', 'LOCAL_DIR': 'logs',
           'INTERVAL': '60'}
    names = []

    f = io.open(path, 'r', encoding='utf-8-sig')
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip().upper()
        value = value.strip()
        if key == 'NAME':
            # NAME=web01,500 / NAME=web01 or NAME=web01,0 -> no limit
            parts = value.split(',')
            limit = None
            if len(parts) > 1 and parts[1].strip():
                limit = int(parts[1])
                if limit <= 0:
                    limit = None
            if parts[0].strip():
                names.append((parts[0].strip(), limit))
        else:
            cfg[key] = value
    f.close()

    cfg['PORT'] = int(cfg['PORT'])
    cfg['INTERVAL'] = max(1, int(cfg['INTERVAL']))
    cfg['NAMES'] = names

    local_dir = cfg['LOCAL_DIR']
    if not os.path.isabs(local_dir):
        local_dir = os.path.join(BASE_DIR, local_dir)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    cfg['LOCAL_DIR'] = local_dir
    return cfg
