from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit,
                             QGridLayout, QGroupBox, QFileDialog, QMessageBox,
                             QComboBox, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal
from image_utils import (convert_image_format, resize_image,
                         crop_image, add_watermark)
from utils import resource_path

class ImageWindow(QWidget):
    operation_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片工具")
        self.setGeometry(200, 200, 500, 600)
        self.setWindowIcon(QIcon(resource_path("工具箱.png")))

        main_layout = QVBoxLayout(self)

        # Convert Image Group
        convert_group = QGroupBox("格式转换")
        convert_layout = QGridLayout(convert_group)
        self.convert_input = QLineEdit()
        self.convert_input.setPlaceholderText("选择一个图片文件")
        convert_layout.addWidget(self.convert_input, 0, 0, 1, 2)
        convert_btn = QPushButton("选择文件")
        convert_btn.setObjectName("selectFileButton")
        convert_btn.clicked.connect(lambda: self.select_file(self.convert_input))
        convert_layout.addWidget(convert_btn, 0, 2)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "BMP", "GIF", "TIFF"])
        convert_layout.addWidget(self.format_combo, 1, 0)
        convert_run_btn = QPushButton("转换")
        convert_run_btn.clicked.connect(self.run_convert_image)
        convert_layout.addWidget(convert_run_btn, 1, 1, 1, 2)
        main_layout.addWidget(convert_group)

        # Resize Image Group
        resize_group = QGroupBox("调整大小")
        resize_layout = QGridLayout(resize_group)
        self.resize_input = QLineEdit()
        self.resize_input.setPlaceholderText("选择一个图片文件")
        resize_layout.addWidget(self.resize_input, 0, 0, 1, 2)
        resize_btn = QPushButton("选择文件")
        resize_btn.setObjectName("selectFileButton")
        resize_btn.clicked.connect(lambda: self.select_file(self.resize_input))
        resize_layout.addWidget(resize_btn, 0, 2)
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("宽度")
        resize_layout.addWidget(self.width_input, 1, 0)
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("高度")
        resize_layout.addWidget(self.height_input, 1, 1)
        resize_run_btn = QPushButton("调整")
        resize_run_btn.clicked.connect(self.run_resize_image)
        resize_layout.addWidget(resize_run_btn, 1, 2)
        main_layout.addWidget(resize_group)

        # Crop Image Group
        crop_group = QGroupBox("裁剪图片")
        crop_layout = QGridLayout(crop_group)
        self.crop_input = QLineEdit()
        self.crop_input.setPlaceholderText("选择一个图片文件")
        crop_layout.addWidget(self.crop_input, 0, 0, 1, 2)
        crop_btn = QPushButton("选择文件")
        crop_btn.setObjectName("selectFileButton")
        crop_btn.clicked.connect(lambda: self.select_file(self.crop_input))
        crop_layout.addWidget(crop_btn, 0, 2)
        self.crop_x = QLineEdit()
        self.crop_x.setPlaceholderText("X")
        crop_layout.addWidget(self.crop_x, 1, 0)
        self.crop_y = QLineEdit()
        self.crop_y.setPlaceholderText("Y")
        crop_layout.addWidget(self.crop_y, 1, 1)
        self.crop_w = QLineEdit()
        self.crop_w.setPlaceholderText("宽度")
        crop_layout.addWidget(self.crop_w, 2, 0)
        self.crop_h = QLineEdit()
        self.crop_h.setPlaceholderText("高度")
        crop_layout.addWidget(self.crop_h, 2, 1)
        crop_run_btn = QPushButton("裁剪")
        crop_run_btn.clicked.connect(self.run_crop_image)
        crop_layout.addWidget(crop_run_btn, 2, 2)
        main_layout.addWidget(crop_group)
        
        main_layout.addStretch()

    def select_file(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_name:
            line_edit.setText(file_name)

    def run_convert_image(self):
        input_path = self.convert_input.text()
        if not input_path: return
        output_format = self.format_combo.currentText()
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", f"{output_format} Files (*.{output_format.lower()})")
        if output_path:
            result = convert_image_format(input_path, output_path, output_format)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_resize_image(self):
        input_path = self.resize_input.text()
        if not input_path: return
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
        except ValueError:
            self.show_message("请输入有效的宽度和高度。", "错误")
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件")
        if output_path:
            result = resize_image(input_path, output_path, (width, height))
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_crop_image(self):
        input_path = self.crop_input.text()
        if not input_path: return
        try:
            x = int(self.crop_x.text())
            y = int(self.crop_y.text())
            w = int(self.crop_w.text())
            h = int(self.crop_h.text())
        except ValueError:
            self.show_message("请输入有效的裁剪参数。", "错误")
            return
        output_path, _ = QFileDialog.getSaveFileName(self, "保存文件")
        if output_path:
            result = crop_image(input_path, output_path, (x, y, x + w, y + h))
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