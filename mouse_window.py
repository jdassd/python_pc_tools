from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit,
                             QGridLayout, QGroupBox, QRadioButton,
                             QComboBox, QLabel, QHBoxLayout)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, QTimer
from utils import resource_path
from mouse_utils import Clicker, HotkeyListener
from pynput.mouse import Button as MouseButton
from pynput.mouse import Controller
import sys

class MouseWindow(QWidget):
    update_status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("鼠标模拟点击工具")
        self.setGeometry(200, 200, 400, 450)
        self.setWindowIcon(QIcon(resource_path("鼠标.png")))

        self.clicker_thread = None
        self.mouse_controller = Controller()

        main_layout = QVBoxLayout(self)

        # Mode Selection Group
        mode_group = QGroupBox("模式选择")
        mode_layout = QHBoxLayout(mode_group)
        self.manual_mode_radio = QRadioButton("手动设置坐标")
        self.auto_mode_radio = QRadioButton("自动获取坐标")
        self.manual_mode_radio.setChecked(True)
        mode_layout.addWidget(self.manual_mode_radio)
        mode_layout.addWidget(self.auto_mode_radio)
        main_layout.addWidget(mode_group)

        # Coordinates Group
        coords_group = QGroupBox("坐标设置")
        coords_layout = QGridLayout(coords_group)
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("X")
        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Y")
        coords_layout.addWidget(QLabel("X:"), 0, 0)
        coords_layout.addWidget(self.x_input, 0, 1)
        coords_layout.addWidget(QLabel("Y:"), 1, 0)
        coords_layout.addWidget(self.y_input, 1, 1)
        main_layout.addWidget(coords_group)

        # Click Settings Group
        settings_group = QGroupBox("点击设置")
        settings_layout = QGridLayout(settings_group)

        settings_layout.addWidget(QLabel("点击频率:"), 0, 0)
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["0.001秒/次", "0.01秒/次", "0.1秒/次", "1秒/次", "5秒/次", "20秒/次", "自定义"])
        self.frequency_combo.currentIndexChanged.connect(self.toggle_custom_frequency)
        settings_layout.addWidget(self.frequency_combo, 0, 1)
        
        self.custom_frequency_input = QLineEdit()
        self.custom_frequency_input.setPlaceholderText("秒/次 (eg: 0.5)")
        self.custom_frequency_input.setVisible(False)
        settings_layout.addWidget(self.custom_frequency_input, 1, 1)

        settings_layout.addWidget(QLabel("鼠标按键:"), 2, 0)
        self.mouse_button_combo = QComboBox()
        self.mouse_button_combo.addItems(["左键", "右键"])
        settings_layout.addWidget(self.mouse_button_combo, 2, 1)
        main_layout.addWidget(settings_group)

        # Hotkey Info
        hotkey_group = QGroupBox("热键")
        hotkey_layout = QVBoxLayout(hotkey_group)
        hotkey_layout.addWidget(QLabel("按 'F6' 启动点击"))
        hotkey_layout.addWidget(QLabel("按 'F7' 停止点击"))
        main_layout.addWidget(hotkey_group)


        # Action Buttons
        action_layout = QHBoxLayout()
        self.start_button = QPushButton("启动 (F6)")
        self.stop_button = QPushButton("停止 (F7)")
        self.stop_button.setEnabled(False)
        action_layout.addWidget(self.start_button)
        action_layout.addWidget(self.stop_button)
        main_layout.addLayout(action_layout)

        self.status_label = QLabel("状态: 已停止")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch()

        self.start_button.clicked.connect(self.start_clicker)
        self.stop_button.clicked.connect(self.stop_clicker)
        self.manual_mode_radio.toggled.connect(self.toggle_mode)

        self.hotkey_listener = HotkeyListener(self.start_clicker, self.stop_clicker)
        self.hotkey_listener.start()
        
        self.update_status_signal.connect(self.status_label.setText)

    def toggle_custom_frequency(self, index):
        if self.frequency_combo.itemText(index) == "自定义":
            self.custom_frequency_input.setVisible(True)
        else:
            self.custom_frequency_input.setVisible(False)

    def toggle_mode(self, checked):
        if checked:
            self.x_input.setEnabled(True)
            self.y_input.setEnabled(True)
        else:
            self.x_input.setEnabled(False)
            self.y_input.setEnabled(False)

    def start_clicker(self):
        if self.clicker_thread and self.clicker_thread.is_alive():
            return

        try:
            # Get Frequency
            freq_text = self.frequency_combo.currentText()
            if freq_text == "自定义":
                interval = float(self.custom_frequency_input.text())
                if interval < 0.001:
                    raise ValueError("自定义间隔不能小于0.001")
            else:
                interval = float(freq_text.split('秒'))
        except ValueError as e:
            self.update_status_signal.emit(f"错误: 无效的频率 - {e}")
            return

        # Get Mouse Button
        button = MouseButton.left if self.mouse_button_combo.currentText() == "左键" else MouseButton.right

        # Get Coordinates
        x, y = None, None
        if self.manual_mode_radio.isChecked():
            try:
                x = int(self.x_input.text())
                y = int(self.y_input.text())
            except ValueError:
                self.update_status_signal.emit("错误: 无效的坐标")
                return
        else: # Auto mode
            x, y = self.mouse_controller.position


        self.clicker_thread = Clicker(interval, button, x, y)
        self.clicker_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.update_status_signal.emit("状态: 运行中...")

    def stop_clicker(self):
        if self.clicker_thread and self.clicker_thread.is_alive():
            self.clicker_thread.stop()
            self.clicker_thread.join() # Wait for thread to finish
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_status_signal.emit("状态: 已停止")

    def closeEvent(self, event):
        self.stop_clicker()
        # The HotkeyListener is a daemon thread, so it will exit when the main program exits.
        # No need to explicitly stop it unless it's holding resources.
        super().closeEvent(event)
