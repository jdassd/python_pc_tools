import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog, QGridLayout,
                             QMessageBox, QHBoxLayout, QFrame)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QSize

from pdf_window import PDFWindow
from image_window import ImageWindow
from audio_window import AudioWindow
from video_window import VideoWindow
from update_manager import check_for_updates, download_and_install_update
from threading import Thread
from utils import resource_path
# from zip_utils import crack_zip_password

__version__ = "1.0.0"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"多功能工具箱 v{__version__}")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(resource_path('工具箱.png')))

        self.pdf_count = 0
        self.image_count = 0
        self.audio_count = 0
        self.video_count = 0

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        title_label = QLabel("多功能工具箱")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label = QLabel("一站式文件处理工具, 支持PDF、图片、音频、视频格式转换和编辑")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addWidget(header_frame)

        # Tools Grid
        tools_grid = QGridLayout()
        tools_grid.setSpacing(20)
        main_layout.addLayout(tools_grid)

        tools_grid.addWidget(self.create_tool_button("PDF工具", "PDF转Word、合并、分割、\n压缩等操作", resource_path("pdf.png"), self.open_pdf_tools), 0, 0)
        tools_grid.addWidget(self.create_tool_button("图片工具", "图片格式转换、压缩、裁剪、\n水印等", resource_path("图片.png"), self.open_image_tools), 0, 1)
        tools_grid.addWidget(self.create_tool_button("音频工具", "音频格式转换、剪辑、音量\n调节等", resource_path("音乐.png"), self.open_audio_tools), 1, 0)
        tools_grid.addWidget(self.create_tool_button("视频工具", "视频格式转换、剪辑、压缩\n等操作", resource_path("视频.png"), self.open_video_tools), 1, 1)

        # Stats
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)
        main_layout.addWidget(stats_frame)

        self.pdf_count_widget = self.create_stat_label("0", "PDF处理次数")
        self.image_count_widget = self.create_stat_label("0", "图片处理次数")
        self.audio_count_widget = self.create_stat_label("0", "音频处理次数")
        self.video_count_widget = self.create_stat_label("0", "视频处理次数")

        stats_layout.addWidget(self.pdf_count_widget)
        stats_layout.addWidget(self.image_count_widget)
        stats_layout.addWidget(self.audio_count_widget)
        stats_layout.addWidget(self.video_count_widget)

        main_layout.addStretch()

        self.check_for_updates_on_startup()

    def check_for_updates_on_startup(self):
        def check():
            latest_release = check_for_updates(__version__)
            if latest_release:
                self.show_update_dialog(latest_release)

        # 在后台线程中运行更新检查
        update_thread = Thread(target=check, daemon=True)
        update_thread.start()

    def show_update_dialog(self, release_info):
        download_and_install_update(release_info)

    def create_tool_button(self, title, description, icon_path, on_click):
        button = QPushButton()
        button.setObjectName("toolButton")
        button_layout = QVBoxLayout(button)
        
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(QSize(48, 48), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("toolTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel(description)
        desc_label.setObjectName("toolDesc")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout.addWidget(icon_label)
        button_layout.addWidget(title_label)
        button_layout.addWidget(desc_label)
        button_layout.setStretch(0, 1)
        button_layout.setStretch(1, 0)
        button_layout.setStretch(2, 0)

        button.clicked.connect(on_click)
        return button

    def create_stat_label(self, count, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        
        count_label = QLabel(count)
        count_label.setObjectName("statCount")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel(text)
        text_label.setObjectName("statText")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(count_label)
        layout.addWidget(text_label)
        return widget

    def open_pdf_tools(self):
        self.pdf_window = PDFWindow()
        self.pdf_window.operation_successful.connect(self.increment_pdf_count)
        self.pdf_window.show()

    def open_image_tools(self):
        self.image_window = ImageWindow()
        self.image_window.operation_successful.connect(self.increment_image_count)
        self.image_window.show()

    def open_audio_tools(self):
        self.audio_window = AudioWindow()
        self.audio_window.operation_successful.connect(self.increment_audio_count)
        self.audio_window.show()

    def open_video_tools(self):
        self.video_window = VideoWindow()
        self.video_window.operation_successful.connect(self.increment_video_count)
        self.video_window.show()

    def increment_pdf_count(self):
        self.pdf_count += 1
        self.pdf_count_widget.findChild(QLabel, "statCount").setText(str(self.pdf_count))

    def increment_image_count(self):
        self.image_count += 1
        self.image_count_widget.findChild(QLabel, "statCount").setText(str(self.image_count))

    def increment_audio_count(self):
        self.audio_count += 1
        self.audio_count_widget.findChild(QLabel, "statCount").setText(str(self.audio_count))

    def increment_video_count(self):
        self.video_count += 1
        self.video_count_widget.findChild(QLabel, "statCount").setText(str(self.video_count))

    def show_message(self, message, title="提示"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open(resource_path("styles.qss"), "r") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())