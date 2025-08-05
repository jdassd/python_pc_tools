from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit,
                             QGridLayout, QGroupBox, QFileDialog, QMessageBox,
                             QComboBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal
from video_utils import convert_video_format, cut_video, compress_video
from utils import resource_path

class VideoWindow(QWidget):
    operation_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频工具")
        self.setGeometry(200, 200, 500, 600)
        self.setWindowIcon(QIcon(resource_path("工具箱.png")))

        main_layout = QVBoxLayout(self)

        # Convert Video Group
        convert_group = QGroupBox("格式转换")
        convert_layout = QGridLayout(convert_group)
        self.convert_input = QLineEdit()
        self.convert_input.setPlaceholderText("选择一个视频文件")
        convert_layout.addWidget(self.convert_input, 0, 0, 1, 2)
        convert_btn = QPushButton("选择文件")
        convert_btn.setObjectName("selectFileButton")
        convert_btn.clicked.connect(lambda: self.select_file(self.convert_input))
        convert_layout.addWidget(convert_btn, 0, 2)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["libx264", "mpeg4"])
        convert_layout.addWidget(self.format_combo, 1, 0)
        convert_run_btn = QPushButton("转换")
        convert_run_btn.clicked.connect(self.run_convert_video)
        convert_layout.addWidget(convert_run_btn, 1, 1, 1, 2)
        main_layout.addWidget(convert_group)

        # Cut Video Group
        cut_group = QGroupBox("剪辑视频")
        cut_layout = QGridLayout(cut_group)
        self.cut_input = QLineEdit()
        self.cut_input.setPlaceholderText("选择一个视频文件")
        cut_layout.addWidget(self.cut_input, 0, 0, 1, 2)
        cut_btn = QPushButton("选择文件")
        cut_btn.setObjectName("selectFileButton")
        cut_btn.clicked.connect(lambda: self.select_file(self.cut_input))
        cut_layout.addWidget(cut_btn, 0, 2)
        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("开始时间 (s)")
        cut_layout.addWidget(self.start_time_input, 1, 0)
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("结束时间 (s)")
        cut_layout.addWidget(self.end_time_input, 1, 1)
        cut_run_btn = QPushButton("剪辑")
        cut_run_btn.clicked.connect(self.run_cut_video)
        cut_layout.addWidget(cut_run_btn, 1, 2)
        main_layout.addWidget(cut_group)

        # Compress Video Group
        compress_group = QGroupBox("压缩视频")
        compress_layout = QGridLayout(compress_group)
        self.compress_input = QLineEdit()
        self.compress_input.setPlaceholderText("选择一个视频文件")
        compress_layout.addWidget(self.compress_input, 0, 0, 1, 2)
        compress_btn = QPushButton("选择文件")
        compress_btn.setObjectName("selectFileButton")
        compress_btn.clicked.connect(lambda: self.select_file(self.compress_input))
        compress_layout.addWidget(compress_btn, 0, 2)
        self.bitrate_input = QLineEdit()
        self.bitrate_input.setPlaceholderText("比特率 (e.g., 500k, 1M)")
        compress_layout.addWidget(self.bitrate_input, 1, 0, 1, 2)
        compress_run_btn = QPushButton("压缩")
        compress_run_btn.clicked.connect(self.run_compress_video)
        compress_layout.addWidget(compress_run_btn, 1, 2)
        main_layout.addWidget(compress_group)

        main_layout.addStretch()

    def select_file(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_name:
            line_edit.setText(file_name)

    def run_convert_video(self):
        input_path = self.convert_input.text()
        if not input_path: return
        codec = self.format_combo.currentText()
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件")
        if output_path:
            result = convert_video_format(input_path, output_path, codec)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_cut_video(self):
        input_path = self.cut_input.text()
        if not input_path: return
        try:
            start_time = int(self.start_time_input.text())
            end_time = int(self.end_time_input.text())
        except ValueError:
            self.show_message("请输入有效的开始和结束时间。", "错误")
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件")
        if output_path:
            result = cut_video(input_path, output_path, start_time, end_time)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_compress_video(self):
        input_path = self.compress_input.text()
        if not input_path: return
        bitrate = self.bitrate_input.text()
        if not bitrate:
            self.show_message("请输入比特率。", "错误")
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件")
        if output_path:
            result = compress_video(input_path, output_path, bitrate)
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