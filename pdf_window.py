from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit,
                             QGridLayout, QGroupBox, QFileDialog, QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal

from pdf_utils import pdf_to_images, merge_pdfs, split_pdf, pdf_to_word

class PDFWindow(QWidget):
    operation_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 工具")
        self.setGeometry(200, 200, 500, 600)
        self.setWindowIcon(QIcon("工具箱.png"))

        main_layout = QVBoxLayout(self)

        # PDF to Word Group
        pdf_to_word_group = QGroupBox("PDF转Word")
        pdf_to_word_layout = QGridLayout(pdf_to_word_group)
        self.pdf_to_word_input = QLineEdit()
        self.pdf_to_word_input.setPlaceholderText("选择一个PDF文件")
        pdf_to_word_layout.addWidget(self.pdf_to_word_input, 0, 0, 1, 2)
        pdf_to_word_btn = QPushButton("选择文件")
        pdf_to_word_btn.setObjectName("selectFileButton")
        pdf_to_word_btn.clicked.connect(lambda: self.select_file(self.pdf_to_word_input))
        pdf_to_word_layout.addWidget(pdf_to_word_btn, 0, 2)
        pdf_to_word_run_btn = QPushButton("转换")
        pdf_to_word_run_btn.clicked.connect(self.run_pdf_to_word)
        pdf_to_word_layout.addWidget(pdf_to_word_run_btn, 0, 3)
        main_layout.addWidget(pdf_to_word_group)

        # PDF to Image Group
        pdf_to_img_group = QGroupBox("PDF转图片")
        pdf_to_img_layout = QGridLayout(pdf_to_img_group)
        self.pdf_to_img_input = QLineEdit()
        self.pdf_to_img_input.setPlaceholderText("选择一个PDF文件")
        pdf_to_img_layout.addWidget(self.pdf_to_img_input, 0, 0, 1, 2)
        pdf_to_img_btn = QPushButton("选择文件")
        pdf_to_img_btn.setObjectName("selectFileButton")
        pdf_to_img_btn.clicked.connect(lambda: self.select_file(self.pdf_to_img_input))
        pdf_to_img_layout.addWidget(pdf_to_img_btn, 0, 2)
        pdf_to_img_run_btn = QPushButton("转换")
        pdf_to_img_run_btn.clicked.connect(self.run_pdf_to_images)
        pdf_to_img_layout.addWidget(pdf_to_img_run_btn, 0, 3)
        main_layout.addWidget(pdf_to_img_group)

        # Merge PDFs Group
        merge_pdfs_group = QGroupBox("合并PDF")
        merge_pdfs_layout = QGridLayout(merge_pdfs_group)
        self.merge_pdfs_input = QLineEdit()
        self.merge_pdfs_input.setPlaceholderText("选择多个PDF文件")
        merge_pdfs_layout.addWidget(self.merge_pdfs_input, 0, 0, 1, 2)
        merge_pdfs_btn = QPushButton("选择文件")
        merge_pdfs_btn.setObjectName("selectFileButton")
        merge_pdfs_btn.clicked.connect(lambda: self.select_files(self.merge_pdfs_input))
        merge_pdfs_layout.addWidget(merge_pdfs_btn, 0, 2)
        merge_pdfs_run_btn = QPushButton("合并")
        merge_pdfs_run_btn.clicked.connect(self.run_merge_pdfs)
        merge_pdfs_layout.addWidget(merge_pdfs_run_btn, 0, 3)
        main_layout.addWidget(merge_pdfs_group)

        # Split PDF Group
        split_pdf_group = QGroupBox("分割PDF")
        split_pdf_layout = QGridLayout(split_pdf_group)
        self.split_pdf_input = QLineEdit()
        self.split_pdf_input.setPlaceholderText("选择一个PDF文件")
        split_pdf_layout.addWidget(self.split_pdf_input, 0, 0, 1, 2)
        split_pdf_btn = QPushButton("选择文件")
        split_pdf_btn.setObjectName("selectFileButton")
        split_pdf_btn.clicked.connect(lambda: self.select_file(self.split_pdf_input))
        split_pdf_layout.addWidget(split_pdf_btn, 0, 2)
        self.split_ranges_input = QLineEdit()
        self.split_ranges_input.setPlaceholderText("例如: 1-5,6-10")
        split_pdf_layout.addWidget(self.split_ranges_input, 1, 0, 1, 2)
        split_pdf_run_btn = QPushButton("分割")
        split_pdf_run_btn.clicked.connect(self.run_split_pdf)
        split_pdf_layout.addWidget(split_pdf_run_btn, 1, 2)
        main_layout.addWidget(split_pdf_group)

        main_layout.addStretch()

    def select_file(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_name:
            line_edit.setText(file_name)

    def select_files(self, line_edit):
        file_names, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        if file_names:
            line_edit.setText(",".join(file_names))

    def select_folder(self, line_edit):
        folder_name = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_name:
            line_edit.setText(folder_name)

    def run_pdf_to_word(self):
        pdf_path = self.pdf_to_word_input.text()
        if not pdf_path: return
        output_path, _ = QFileDialog.getSaveFileName(self, "保存Word文件", "", "Word Documents (*.docx)")
        if output_path:
            result = pdf_to_word(pdf_path, output_path)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_pdf_to_images(self):
        pdf_path = self.pdf_to_img_input.text()
        if not pdf_path: return
        output_folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if output_folder:
            result = pdf_to_images(pdf_path, output_folder)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_merge_pdfs(self):
        pdf_files = self.merge_pdfs_input.text().split(',')
        if not pdf_files or not pdf_files[0]: return
        output_path, _ = QFileDialog.getSaveFileName(self, "保存合并后的PDF", "", "PDF Files (*.pdf)")
        if output_path:
            result = merge_pdfs(pdf_files, output_path)
            self.show_message(result)
            if "Successfully" in result:
                self.operation_successful.emit()

    def run_split_pdf(self):
        pdf_path = self.split_pdf_input.text()
        ranges_str = self.split_ranges_input.text()
        if not pdf_path or not ranges_str: return
        
        try:
            ranges = [tuple(map(int, r.split('-'))) for r in ranges_str.split(',')]
        except:
            self.show_message("范围格式错误，请使用 '1-5,6-10' 格式。", "错误")
            return

        output_folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if output_folder:
            result = split_pdf(pdf_path, ranges, output_folder)
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