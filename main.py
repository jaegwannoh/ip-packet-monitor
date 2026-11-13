# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import datetime
import ctypes
import winsound
from PyQt4 import QtGui, QtCore
import config
import fetcher
import logparser
import style

APP_ID = 'IPPacketMonitor.App.1'

HEADERS = ['이름', '최근 1시간 패킷', '기준값', '누적 패킷',
           '마지막 기록 시각', '상태']


class MainWindow(QtGui.QWidget):
    def __init__(self, cfg):
        super(MainWindow, self).__init__()
        self.cfg = cfg
        self.sound_on = True
        self.alert = False
        self.ok = True
        self.font_size = 14
        self.setWindowTitle('IP Packet Monitor')
        self.resize(1000, 520)
        self.setMinimumSize(700, 380)

        # root frame (background color)
        self.root = QtGui.QFrame()
        self.root.setObjectName('root')
        outer = QtGui.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.root)

        layout = QtGui.QVBoxLayout(self.root)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # title
        title = QtGui.QLabel('IP Packet Monitor')
        title.setObjectName('title')
        subtitle = QtGui.QLabel('IP 패킷 출현량 모니터링')
        subtitle.setObjectName('subtitle')
        top = QtGui.QHBoxLayout()
        top.addWidget(title)
        top.addStretch()
        top.addWidget(subtitle, 0, QtCore.Qt.AlignBottom)
        layout.addLayout(top)

        # info cards
        cards = QtGui.QHBoxLayout()
        cards.setSpacing(12)
        self.ip_value = self.add_card(cards, '감시 IP')
        self.interval_value = self.add_card(cards, '확인 주기')
        self.count_value = self.add_card(cards, '감시 대상')
        self.time_value = self.add_card(cards, '마지막 확인')
        layout.addLayout(cards)

        # alert banner
        self.banner = QtGui.QLabel()
        self.banner.setObjectName('banner')
        self.banner.setAlignment(QtCore.Qt.AlignCenter)
        self.banner.hide()
        layout.addWidget(self.banner)

        # table
        self.table = QtGui.QTableWidget(len(cfg['NAMES']), len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.table.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        layout.addWidget(self.table, 1)

        # bottom buttons
        self.folder_btn = QtGui.QPushButton('로그 폴더 열기')
        self.folder_btn.setObjectName('folder')
        self.sound_btn = QtGui.QPushButton()
        self.sound_btn.setObjectName('sound')
        self.sound_btn.setCheckable(True)
        self.sound_btn.setChecked(True)
        for btn in (self.folder_btn, self.sound_btn):
            btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.status_label = QtGui.QLabel()
        self.status_label.setObjectName('status')
        self.folder_btn.clicked.connect(self.open_folder)
        self.sound_btn.clicked.connect(self.toggle_sound)

        bottom = QtGui.QHBoxLayout()
        bottom.addWidget(self.folder_btn)
        bottom.addWidget(self.sound_btn)
        bottom.addStretch()
        bottom.addWidget(self.status_label)
        layout.addLayout(bottom)

        self.ip_value.setText(cfg['MONITOR_IP'])
        self.interval_value.setText('%d초' % cfg['INTERVAL'])
        self.count_value.setText('%d개' % len(cfg['NAMES']))
        self.update_sound_btn()
        self.apply_style()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check)
        self.timer.start(cfg['INTERVAL'] * 1000)
        QtCore.QTimer.singleShot(100, self.check)

        self.beep_timer = QtCore.QTimer(self)
        self.beep_timer.timeout.connect(self.beep)

    def add_card(self, box, caption):
        card = QtGui.QFrame()
        card.setObjectName('card')
        v = QtGui.QVBoxLayout(card)
        v.setContentsMargins(16, 10, 16, 10)
        v.setSpacing(2)
        cap = QtGui.QLabel(caption)
        cap.setObjectName('cardCaption')
        value = QtGui.QLabel('-')
        value.setObjectName('cardValue')
        v.addWidget(cap)
        v.addWidget(value)
        box.addWidget(card)
        return value

    def apply_style(self):
        self.root.setStyleSheet(
            style.build(self.font_size, self.alert, self.ok))

    def check(self):
        msg = fetcher.fetch_logs(self.cfg)
        over_names = []
        for row, (name, limit) in enumerate(self.cfg['NAMES']):
            path = logparser.find_local(self.cfg['LOCAL_DIR'], name)
            result = None
            if path:
                try:
                    result = logparser.calc(logparser.read_log(path))
                except Exception as e:
                    msg = 'Read error (%s): %r' % (name, e)
            over = False
            limit_text = '없음' if limit is None else limit
            if result is None:
                values = [name, '-', limit_text, '-', '-', '로그 없음']
            else:
                hour, total, last = result
                over = limit is not None and hour >= limit
                state = '● 경고' if over else '● 정상'
                values = [name, hour, limit_text, total,
                          last.strftime('%Y%m%d - %H:%M'), state]
            if over:
                over_names.append(name)
            self.set_row(row, values, over, result is not None)

        self.alert = len(over_names) > 0
        self.ok = not msg
        if self.alert:
            self.banner.setText('경고  기준값 이상: ' + ', '.join(over_names))
            self.banner.show()
        else:
            self.banner.hide()
        now = datetime.datetime.now().strftime('%H:%M:%S')
        self.time_value.setText(now)
        self.status_label.setText('● ' + (msg if msg else '정상'))
        self.apply_style()

        self.update_beep()

    def beep(self):
        try:
            winsound.Beep(1000, 300)
        except RuntimeError:  # no sound device
            pass

    def update_beep(self):
        if self.alert and self.sound_on:
            if not self.beep_timer.isActive():
                self.beep()
                self.beep_timer.start(1000)
        else:
            self.beep_timer.stop()

    def set_row(self, row, values, over, has_log):
        last_col = len(values) - 1
        for col, value in enumerate(values):
            item = QtGui.QTableWidgetItem('%s' % value)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            if over:
                item.setBackground(QtGui.QBrush(style.ROW_ALERT_BG))
                item.setForeground(QtGui.QBrush(style.ROW_ALERT_FG))
            else:
                item.setForeground(QtGui.QBrush(style.ROW_FG))
            if not has_log:
                item.setForeground(QtGui.QBrush(style.NOLOG_FG))
            elif col == last_col:
                color = style.OVER_FG if over else style.OK_FG
                item.setForeground(QtGui.QBrush(color))
            self.table.setItem(row, col, item)

    def open_folder(self):
        os.startfile(self.cfg['LOCAL_DIR'])

    def toggle_sound(self):
        self.sound_on = self.sound_btn.isChecked()
        self.update_sound_btn()
        self.update_beep()

    def update_sound_btn(self):
        self.sound_btn.setText('소리 ON' if self.sound_on else '소리 OFF')

    def resizeEvent(self, event):
        size = max(12, min(self.width() // 70, self.height() // 34))
        if size != self.font_size:
            self.font_size = size
            self.apply_style()
        super(MainWindow, self).resizeEvent(event)


def main():
    # taskbar: show as own program, not python.exe
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        pass
    app = QtGui.QApplication(sys.argv)
    app.setFont(QtGui.QFont('Malgun Gothic', 10))
    app.setWindowIcon(style.make_icon())
    try:
        cfg = config.load_config(os.path.join(config.BASE_DIR, 'config.txt'))
    except Exception as e:
        QtGui.QMessageBox.critical(None, 'Error', '설정 파일 오류: %r' % e)
        return
    win = MainWindow(cfg)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
