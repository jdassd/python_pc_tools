from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit,
                             QGridLayout, QGroupBox, QFileDialog, QMessageBox,
                             QComboBox, QLabel, QSlider)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from audio_utils import convert_audio_format, cut_audio, adjust_volume
from utils import resource_path

class AudioWindow(QWidget):
    operation_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("音频工具")
        self.setGeometry(200, 200, 500, 600)
        self.setWindowIcon(QIcon(resource_path("工具箱.png")))

        main_layout = QVBoxLayout(self)

        # Convert Audio Group
        convert_group = QGroupBox("格式转换")
        convert_layout = QGridLayout(convert_group)
        self.convert_input = QLineEdit()
        self.convert_input.setPlaceholderText("选择一个音频文件")
        convert_layout.addWidget(self.convert_input, 0, 0, 1, 2)
        convert_btn = QPushButton("选择文件")
        convert_btn.setObjectName("selectFileButton")
        convert_btn.clicked.connect(lambda: self.select_file(self.convert_input))
        convert_layout.addWidget(convert_btn, 0, 2)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "wav", "ogg", "flv"])
        convert_layout.addWidget(self.format_combo, 1, 0)
        convert_run_btn = QPushButton("转换")
        convert_run_btn.clicked.connect(self.run_convert_audio)
        convert_layout.addWidget(convert_run_btn, 1, 1, 1, 2)
        main_layout.addWidget(convert_group)

        # Cut Audio Group
        cut_group = QGroupBox("剪辑音频")
        cut_layout = QGridLayout(cut_group)
        self.cut_input = QLineEdit()
        self.cut_input.setPlaceholderText("选择一个音频文件")
        cut_layout.addWidget(self.cut_input, 0, 0, 1, 2)
        cut_btn = QPushButton("选择文件")
        cut_btn.setObjectName("selectFileButton")
        cut_btn.clicked.connect(lambda: self.select_file(self.cut_input))
        cut_layout.addWidget(cut_btn, 0, 2)
        self.start_ms_input = QLineEdit()
        self.start_ms_input.setPlaceholderText("开始时间 (ms)")
        cut_layout.addWidget(self.start_ms_input, 1, 0)
        self.end_ms_input = QLineEdit()
        self.end_ms_input.setPlaceholderText("结束时间 (ms)")
        cut_layout.addWidget(self.end_ms_input, 1, 1)
        cut_run_btn = QPushButton("剪辑")
        cut_run_btn.clicked.connect(self.run_cut_audio)
        cut_layout.addWidget(cut_run_btn, 1, 2)
        main_layout.addWidget(cut_group)

        # Adjust Volume Group
        volume_group = QGroupBox("音量调节")
        volume_layout = QGridLayout(volume_group)
        self.volume_input = QLineEdit()
        self.volume_input.setPlaceholderText("选择一个音频文件")
        volume_layout.addWidget(self.volume_input, 0, 0, 1, 2)
        volume_btn = QPushButton("选择文件")
        volume_btn.setObjectName("selectFileButton")
        volume_btn.clicked.connect(lambda: self.select_file(self.volume_input))
        volume_layout.addWidget(volume_btn, 0, 2)
        self.db_slider = QSlider(Qt.Orientation.Horizontal)
        self.db_slider.setRange(-20, 20)
        self.db_slider.setValue(0)
        volume_layout.addWidget(self.db_slider, 1, 0, 1, 2)
        self.db_label = QLabel("0 dB")
        volume_layout.addWidget(self.db_label, 1, 2)
        self.db_slider.valueChanged.connect(lambda v: self.db_label.setText(f"{v} dB"))
        volume_run_btn = QPushButton("调节")
        volume_run_btn.clicked.connect(self.run_adjust_volume)
        volume_layout.addWidget(volume_run_btn, 2, 0, 1, 3)
        main_layout.addWidget(volume_group)

        main_layout.addStretch()

    def select_file(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_name:
            line_edit.setText(file_name)

    def run_convert_audio(self):
        input_path = self.convert_input.text()
        if not input_path: return
        output_format = self.format_combo.currentText()
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", f"{output_format.upper()} Files (*.{output_format})")
        if output_path:
            result = convert_audio_format(input_path, output_path, output_format)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_cut_audio(self):
        input_path = self.cut_input.text()
        if not input_path: return
        try:
            start_ms = int(self.start_ms_input.text())
            end_ms = int(self.end_ms_input.text())
        except ValueError:
            self.show_message("请输入有效的开始和结束时间。", "错误")
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件")
        if output_path:
            result = cut_audio(input_path, output_path, start_ms, end_ms)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_adjust_volume(self):
        input_path = self.volume_input.text()
        if not input_path: return
        db = self.db_slider.value()
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件")
        if output_path:
            result = adjust_volume(input_path, output_path, db)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def show_message(self, message, title="提示"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()