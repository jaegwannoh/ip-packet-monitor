# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import io
import os
import datetime

TIME_FMT = '%Y%m%d %H:%M:%S'


def file_name(day, name):
    return '%s_%s_log.txt' % (day.strftime('%Y-%m-%d'), name)


def find_local(local_dir, name):
    # today file first, if not exists use yesterday file
    today = datetime.date.today()
    for day in (today, today - datetime.timedelta(days=1)):
        path = os.path.join(local_dir, file_name(day, name))
        if os.path.exists(path):
            return path
    return None


def read_log(path):
    rows = []
    f = io.open(path, 'r', encoding='utf-8', errors='ignore')
    for line in f:
        parts = line.strip().split(',')
        if len(parts) < 3:
            continue
        try:
            t = datetime.datetime.strptime(parts[0].strip(), TIME_FMT)
            n = int(parts[2].strip())
        except ValueError:
            continue
        rows.append((t, n))
    f.close()
    rows.sort(key=lambda r: r[0])  # sort by time only, keep file order
    return rows


def calc(rows):
    # return (last_hour, total, last_time) or None
    if not rows:
        return None
    last_time, total = rows[-1]
    start = last_time - datetime.timedelta(hours=1)
    hour = 0
    for i in range(1, len(rows)):
        t, n = rows[i]
        if t <= start:
            continue
        prev = rows[i - 1][1]
        if n >= prev:
            hour += n - prev
        else:
            hour += n  # reset
    return hour, total, last_time
