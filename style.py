# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PyQt4 import QtGui, QtCore

# colors
BG_NORMAL = '#eef1f6'
BG_ALERT = '#fde2e2'
NAVY = '#1f2a44'
BLUE = '#3b6ef5'
GREEN = '#16a34a'
RED = '#dc2626'
GRAY = '#6b7280'

ROW_ALERT_BG = QtGui.QColor('#fecaca')
ROW_ALERT_FG = QtGui.QColor('#991b1b')
ROW_FG = QtGui.QColor('#1f2937')
OK_FG = QtGui.QColor(GREEN)
OVER_FG = QtGui.QColor(RED)
NOLOG_FG = QtGui.QColor('#9ca3af')

SHEET = '''
QFrame#root { background: %(bg)s; }

QLabel#title { color: %(navy)s; font-size: %(ft)dpx; font-weight: bold; }
QLabel#subtitle { color: %(gray)s; font-size: %(fs)dpx; }

QFrame#card { background: white; border: 1px solid #dde2ec;
              border-radius: 10px; }
QLabel#cardCaption { color: %(gray)s; font-size: %(fs)dpx; }
QLabel#cardValue { color: %(navy)s; font-size: %(fl)dpx;
                   font-weight: bold; }

QLabel#banner { background: %(red)s; color: white; font-size: %(fl)dpx;
                font-weight: bold; border-radius: 10px; padding: 8px; }

QTableWidget { background: white; alternate-background-color: #f6f8fc;
               border: 1px solid #dde2ec; border-radius: 10px;
               gridline-color: #edf0f5; font-size: %(fl)dpx; }
QHeaderView::section { background: %(navy)s; color: white; border: none;
                       padding: 8px; font-size: %(f)dpx;
                       font-weight: bold; }

QPushButton { font-size: %(f)dpx; padding: 8px 20px; border: none;
              border-radius: 8px; font-weight: bold; }
QPushButton#folder { background: %(blue)s; color: white; }
QPushButton#folder:hover { background: #2f5bd6; }
QPushButton#sound { background: #d1d5db; color: #374151; }
QPushButton#sound:checked { background: %(green)s; color: white; }

QLabel#status { color: %(st)s; font-size: %(f)dpx; font-weight: bold; }
'''


def make_icon():
    # navy box + 3 bars(packets) + red dot(alarm)
    pix = QtGui.QPixmap(64, 64)
    pix.fill(QtCore.Qt.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.Antialiasing)
    p.setPen(QtCore.Qt.NoPen)
    p.setBrush(QtGui.QColor(NAVY))
    p.drawRoundedRect(2, 2, 60, 60, 14, 14)
    p.setBrush(QtGui.QColor('#60a5fa'))
    for i, h in enumerate((14, 24, 32)):
        p.drawRoundedRect(12 + i * 15, 52 - h, 10, h, 3, 3)
    p.setBrush(QtGui.QColor(RED))
    p.drawEllipse(44, 6, 13, 13)
    p.end()
    return QtGui.QIcon(pix)


def build(size, alert, ok):
    # size: base font size(px), alert: over limit, ok: no error
    values = {
        'f': size,
        'fs': size - 3,
        'fl': size + 3,
        'ft': size + 10,
        'bg': BG_ALERT if alert else BG_NORMAL,
        'st': GREEN if ok else RED,
        'navy': NAVY, 'gray': GRAY, 'blue': BLUE,
        'green': GREEN, 'red': RED,
    }
    return SHEET % values
