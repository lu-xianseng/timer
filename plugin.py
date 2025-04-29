import os, sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from src.command import run_cmd
from src.settings import RES_PATH
from src.log import _excepthook, logger
from src.styles import set_label_styles, set_button_styles

class ShutdownRestartApp(QWidget):
    def __init__(self):
        super().__init__()
        self.action = sys.argv[1]
        if not self.action in ['s', 'r']:
            exit(2)
        self.remaining_time = int(sys.argv[2])
        self.key = sys.argv[3]
        if self.key != 'TJhgy78uYH':
            exit(2)
        self.text = '关机' if self.action == 's' else '重启'
        self.initUI()
        self.start_countdown()

    def initUI(self):
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        icon_path = rf'{RES_PATH}\icon.ico'
        logger.debug(icon_path)
        self.setWindowIcon(QIcon(icon_path))
        layout = QVBoxLayout()

        self.label = QLabel(f"系统将在 {self.remaining_time} 秒后 {self.text}...", self)
        set_label_styles(self.label, font_size=12, color='red', bold=True)
        layout.addWidget(self.label)

        self.cancel_button = QPushButton('取消', self)
        set_button_styles(self.cancel_button, background_color='#EB4444', hover_color='#CC0000')
        self.cancel_button.clicked.connect(self.cancel_action)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)
        self.setWindowTitle("计划执行")
        self.setGeometry(100, 100, 300, 100)
        self.setFixedSize(self.width(), self.height())
        screen_geometry = QApplication.desktop().screenGeometry()
        window_width = self.width()
        window_height = self.height()
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.move(x, y)
        self.show()

    def start_countdown(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        lable_text = f"系统将会在{self.remaining_time}秒后{self.text}..."
        self.remaining_time -= 1
        if self.remaining_time > 0:
            self.label.setText(lable_text)
        else:
            self.timer.stop()
            if self.action == "s":
                logger.info('Shutdown now')
                run_cmd("shutdown /s /t 0")
            elif self.action == "r":
                logger.info('Reboot now')
                run_cmd("shutdown /r /t 0")
            self.close()

    def cancel_action(self):
        logger.info('Click cancel')
        self.close()


if __name__ == '__main__':
    sys.excepthook = _excepthook
    try:
        app = QApplication(sys.argv)
        ex = ShutdownRestartApp()
        sys.exit(app.exec_())
    except (IndexError, ValueError):
        ...
    