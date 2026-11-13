# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import socket
import datetime
import paramiko
from logparser import file_name


def fetch_logs(cfg):
    # download today(or yesterday) log of each name. return error msg
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    msg = ''
    try:
        ssh.connect(cfg['HOST'], port=cfg['PORT'], username=cfg['USER'],
                    password=cfg['PASSWORD'], timeout=5)
        sftp = ssh.open_sftp()
        sftp.get_channel().settimeout(30)  # no data 30s -> socket.timeout
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        missing = []
        for name, _ in cfg['NAMES']:
            ok = False
            for day in (today, yesterday):
                fn = file_name(day, name)
                remote = cfg['REMOTE_DIR'].rstrip('/') + '/' + fn
                local = os.path.join(cfg['LOCAL_DIR'], fn)
                try:
                    sftp.stat(remote)  # check exists (get makes empty file)
                except socket.timeout:  # timeout is IOError too, raise it
                    raise
                except IOError:
                    continue
                tmp = local + '.tmp'  # keep old file if download fails
                sftp.get(remote, tmp)
                if os.path.exists(local):
                    os.remove(local)
                os.rename(tmp, local)
                ok = True
                break
            if not ok:
                missing.append(name)
        sftp.close()
        if missing:
            msg = 'No remote log: ' + ', '.join(missing)
    except Exception as e:
        msg = 'SSH error: %r' % e
    finally:
        ssh.close()
    return msg
