import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog, QGridLayout,
                             QMessageBox, QHBoxLayout, QFrame, QSizePolicy)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QSize, QObject, pyqtSignal, QThread

from pdf_window import PDFWindow
from image_window import ImageWindow
from audio_window import AudioWindow
from video_window import VideoWindow
from mouse_window import MouseWindow
from text_window import TextWindow
from system_window import SystemWindow
from network_window import NetworkWindow
from crypto_window import CryptoWindow
from dev_window import DevWindow
from office_window import OfficeWindow
from media_window import MediaWindow
from data_window import DataWindow
from update_manager import check_for_updates, download_and_install_update
from utils import resource_path
from data_manager import DataManager
# from zip_utils import crack_zip_password

__version__ = "1.0.9"

class AdaptiveToolButton(QPushButton):
    def __init__(self, title, description, icon_path, parent=None):
        super().__init__(parent)
        self.setObjectName("toolButton")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.icon_path = icon_path
        self.title_text = title
        self.description_text = description

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(self.title_text)
        self.title_label.setObjectName("toolTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.desc_label = QLabel(self.description_text)
        self.desc_label.setObjectName("toolDesc")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setWordWrap(True)

        layout.addWidget(self.icon_label, 2)
        layout.addWidget(self.title_label, 1)
        layout.addWidget(self.desc_label, 1)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        button_height = self.height()
        
        # --- Icon Resizing ---
        icon_size = int(button_height * 0.3) # Icon takes up 30% of the button height
        pixmap = QPixmap(self.icon_path)
        self.icon_label.setPixmap(pixmap.scaled(QSize(icon_size, icon_size), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # --- Font Resizing ---
        title_font_size = max(int(button_height * 0.08), 10) # 减小标题字体比例，最小10px
        desc_font_size = max(int(button_height * 0.06), 8) # 减小描述字体比例，最小8px

        title_font = self.title_label.font()
        title_font.setPixelSize(title_font_size)
        self.title_label.setFont(title_font)

        desc_font = self.desc_label.font()
        desc_font.setPixelSize(desc_font_size)
        self.desc_label.setFont(desc_font)

class UpdateCheckWorker(QObject):
    update_found = pyqtSignal(dict)

    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version

    def run(self):
        """Checks for updates and emits a signal if a new version is found."""
        latest_release = check_for_updates(self.current_version)
        if latest_release:
            self.update_found.emit(latest_release)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"多功能工具箱 v{__version__}")
        self.setMinimumSize(600, 700) # 设置一个合理的最小尺寸
        self.setWindowIcon(QIcon(resource_path('工具箱.png')))

        # 初始化数据管理器
        self.data_manager = DataManager()
        
        # 从持久化存储加载使用次数
        counts = self.data_manager.get_all_counts()
        self.pdf_count = counts.get('pdf_count', 0)
        self.image_count = counts.get('image_count', 0)
        self.audio_count = counts.get('audio_count', 0)
        self.video_count = counts.get('video_count', 0)
        self.mouse_count = counts.get('mouse_count', 0)
        self.text_count = counts.get('text_count', 0)
        self.system_count = counts.get('system_count', 0)
        self.network_count = counts.get('network_count', 0)
        self.crypto_count = counts.get('crypto_count', 0)
        self.dev_count = counts.get('dev_count', 0)
        self.office_count = counts.get('office_count', 0)
        self.media_count = counts.get('media_count', 0)
        self.data_count = counts.get('data_count', 0)

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
        subtitle_label = QLabel("多功能工具箱, 提供文件处理、加密解密、开发工具、数据分析等全方位功能")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addWidget(header_frame)

        # Tools Grid
        self.tools_grid = QGridLayout()
        self.tools_grid.setSpacing(20)
        main_layout.addLayout(self.tools_grid, 1)

        self.setup_tools_grid()

        # Stats

        self.pdf_count_widget = self.create_stat_label(str(self.pdf_count), "PDF处理次数")
        self.image_count_widget = self.create_stat_label(str(self.image_count), "图片处理次数")
        self.audio_count_widget = self.create_stat_label(str(self.audio_count), "音频处理次数")
        self.video_count_widget = self.create_stat_label(str(self.video_count), "视频处理次数")
        self.mouse_count_widget = self.create_stat_label(str(self.mouse_count), "鼠标点击次数")
        self.text_count_widget = self.create_stat_label(str(self.text_count), "文本处理次数")
        self.system_count_widget = self.create_stat_label(str(self.system_count), "系统工具次数")
        self.network_count_widget = self.create_stat_label(str(self.network_count), "网络工具次数")
        self.crypto_count_widget = self.create_stat_label(str(getattr(self, 'crypto_count', 0)), "加密解密次数")
        self.dev_count_widget = self.create_stat_label(str(getattr(self, 'dev_count', 0)), "开发工具次数")
        self.office_count_widget = self.create_stat_label(str(getattr(self, 'office_count', 0)), "办公效率次数")
        self.media_count_widget = self.create_stat_label(str(getattr(self, 'media_count', 0)), "媒体增强次数")
        self.data_count_widget = self.create_stat_label(str(getattr(self, 'data_count', 0)), "数据分析次数")

        # 使用固定高度的统计展示区域，支持换行布局
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        # stats_frame.setFixedHeight(120)  # 移除固定高度，使其自适应
        
        # 使用网格布局来显示统计数据，支持两行显示
        stats_grid_layout = QGridLayout(stats_frame)
        stats_grid_layout.setSpacing(15)
        stats_grid_layout.setContentsMargins(15, 15, 15, 15)
        
        # 统计项列表
        stats_items = [
            (self.pdf_count_widget, "PDF处理次数"),
            (self.image_count_widget, "图片处理次数"),
            (self.audio_count_widget, "音频处理次数"),
            (self.video_count_widget, "视频处理次数"),
            (self.mouse_count_widget, "鼠标点击次数"),
            (self.text_count_widget, "文本处理次数"),
            (self.system_count_widget, "系统工具次数"),
            (self.network_count_widget, "网络工具次数"),
            (self.crypto_count_widget, "加密解密次数"),
            (self.dev_count_widget, "开发工具次数"),
            (self.office_count_widget, "办公效率次数"),
            (self.media_count_widget, "媒体增强次数"),
            (self.data_count_widget, "数据分析次数")
        ]
        
        # 分两行显示：第一行7个，第二行6个
        cols_per_row = 7
        for idx, (widget, _) in enumerate(stats_items):
            row = idx // cols_per_row
            col = idx % cols_per_row
            
            # 如果是第二行且只有6个元素，居中显示
            stats_grid_layout.addWidget(widget, row, col)

        # 为第二行添加伸缩因子，使其居中
        if len(stats_items) > cols_per_row:
            remaining_items = len(stats_items) % cols_per_row
            if remaining_items > 0:
                # 添加前置和后置伸缩因子
                stats_grid_layout.setColumnStretch(cols_per_row - 1, 1) # 确保最后一列有伸缩
                stats_grid_layout.setColumnStretch(0, 1)
        
        main_layout.addWidget(stats_frame)

        main_layout.addStretch()

        self.check_for_updates_on_startup()

    def setup_tools_grid(self):
        tools = [
            ("PDF工具", "PDF转Word、合并、分割、\n压缩等操作", resource_path("pdf.png"), self.open_pdf_tools),
            ("图片工具", "图片格式转换、压缩、裁剪、\n水印等", resource_path("图片.png"), self.open_image_tools),
            ("音频工具", "音频格式转换、剪辑、音量\n调节等", resource_path("音乐.png"), self.open_audio_tools),
            ("视频工具", "视频格式转换、剪辑、压缩\n等操作", resource_path("视频.png"), self.open_video_tools),
            ("鼠标工具", "模拟鼠标点击，支持\n自定义坐标和频率", resource_path("鼠标.png"), self.open_mouse_tools),
            ("文本工具", "文本编码转换、查找替换、\n分割合并、统计分析", resource_path("文本.png"), self.open_text_tools),
            ("系统工具", "文件重命名、重复文件查找、\n目录比较、系统清理", resource_path("系统.png"), self.open_system_tools),
            ("网络工具", "二维码生成、URL测试、\n端口扫描、HTTP服务器", resource_path("网络.png"), self.open_network_tools),
            ("加密解密", "文件加密解密、哈希计算、\n密码生成器", resource_path("加密.png"), self.open_crypto_tools),
            ("开发工具", "JSON/XML格式化、URL编码、\n正则表达式、颜色工具", resource_path("开发.png"), self.open_dev_tools),
            ("办公效率", "Excel处理、批量重命名、\n文件监控、剪贴板管理", resource_path("办公.png"), self.open_office_tools),
            ("媒体增强", "屏幕截图、GIF制作、\n条形码生成、图片拼贴", resource_path("媒体.png"), self.open_media_tools),
            ("数据分析", "CSV分析、数据清理、\n日志分析、数据透视", resource_path("数据.png"), self.open_data_tools)
        ]

        # Clear existing widgets
        for i in reversed(range(self.tools_grid.count())):
            self.tools_grid.itemAt(i).widget().setParent(None)

        num_tools = len(tools)
        # 固定4列布局，根据工具数量计算行数
        num_columns = 4
        num_rows = (num_tools + num_columns - 1) // num_columns  # 向上取整计算需要的行数
        
        for i in range(num_columns):
            self.tools_grid.setColumnStretch(i, 1)
        for i in range(num_rows):
            self.tools_grid.setRowStretch(i, 1)

        for idx, (title, desc, icon, callback) in enumerate(tools):
            row = idx // num_columns  # 按行优先排列
            col = idx % num_columns
            button = self.create_tool_button(title, desc, icon, callback)
            self.tools_grid.addWidget(button, row, col)


    def check_for_updates_on_startup(self):
        self.update_thread = QThread()
        self.update_worker = UpdateCheckWorker(__version__)
        self.update_worker.moveToThread(self.update_thread)

        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.update_found.connect(self.show_update_dialog)
        
        # Clean up the thread when the worker is done
        self.update_worker.update_found.connect(self.update_thread.quit)
        self.update_thread.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)

        self.update_thread.start()

    def show_update_dialog(self, release_info):
        download_and_install_update(release_info, self)

    def create_tool_button(self, title, description, icon_path, on_click):
        button = AdaptiveToolButton(title, description, icon_path)
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

    def open_mouse_tools(self):
        self.mouse_window = MouseWindow()
        self.mouse_window.operation_successful.connect(self.increment_mouse_count)
        self.mouse_window.show()

    def increment_pdf_count(self):
        self.pdf_count = self.data_manager.increment_tool_count('pdf_count')
        self.pdf_count_widget.findChild(QLabel, "statCount").setText(str(self.pdf_count))

    def increment_image_count(self):
        self.image_count = self.data_manager.increment_tool_count('image_count')
        self.image_count_widget.findChild(QLabel, "statCount").setText(str(self.image_count))

    def increment_audio_count(self):
        self.audio_count = self.data_manager.increment_tool_count('audio_count')
        self.audio_count_widget.findChild(QLabel, "statCount").setText(str(self.audio_count))

    def increment_video_count(self):
        self.video_count = self.data_manager.increment_tool_count('video_count')
        self.video_count_widget.findChild(QLabel, "statCount").setText(str(self.video_count))

    def open_text_tools(self):
        self.text_window = TextWindow()
        self.text_window.operation_successful.connect(self.increment_text_count)
        self.text_window.show()

    def open_system_tools(self):
        self.system_window = SystemWindow()
        self.system_window.operation_successful.connect(self.increment_system_count)
        self.system_window.show()

    def open_network_tools(self):
        self.network_window = NetworkWindow()
        self.network_window.operation_successful.connect(self.increment_network_count)
        self.network_window.show()

    def increment_text_count(self):
        self.text_count = self.data_manager.increment_tool_count('text_count')
        self.text_count_widget.findChild(QLabel, "statCount").setText(str(self.text_count))

    def increment_system_count(self):
        self.system_count = self.data_manager.increment_tool_count('system_count')
        self.system_count_widget.findChild(QLabel, "statCount").setText(str(self.system_count))

    def increment_network_count(self):
        self.network_count = self.data_manager.increment_tool_count('network_count')
        self.network_count_widget.findChild(QLabel, "statCount").setText(str(self.network_count))

    def increment_mouse_count(self):
        self.mouse_count = self.data_manager.increment_tool_count('mouse_count')
        self.mouse_count_widget.findChild(QLabel, "statCount").setText(str(self.mouse_count))
    
    def open_crypto_tools(self):
        self.crypto_window = CryptoWindow()
        self.crypto_window.operation_successful.connect(self.increment_crypto_count)
        self.crypto_window.show()
    
    def open_dev_tools(self):
        self.dev_window = DevWindow()
        self.dev_window.operation_successful.connect(self.increment_dev_count)
        self.dev_window.show()
    
    def open_office_tools(self):
        self.office_window = OfficeWindow()
        self.office_window.operation_successful.connect(self.increment_office_count)
        self.office_window.show()
    
    def open_media_tools(self):
        self.media_window = MediaWindow()
        self.media_window.operation_successful.connect(self.increment_media_count)
        self.media_window.show()
    
    def open_data_tools(self):
        self.data_window = DataWindow()
        self.data_window.operation_successful.connect(self.increment_data_count)
        self.data_window.show()
    
    def increment_crypto_count(self):
        self.crypto_count = self.data_manager.increment_tool_count('crypto_count')
        self.crypto_count_widget.findChild(QLabel, "statCount").setText(str(self.crypto_count))
    
    def increment_dev_count(self):
        self.dev_count = self.data_manager.increment_tool_count('dev_count')
        self.dev_count_widget.findChild(QLabel, "statCount").setText(str(self.dev_count))
    
    def increment_office_count(self):
        self.office_count = self.data_manager.increment_tool_count('office_count')
        self.office_count_widget.findChild(QLabel, "statCount").setText(str(self.office_count))
    
    def increment_media_count(self):
        self.media_count = self.data_manager.increment_tool_count('media_count')
        self.media_count_widget.findChild(QLabel, "statCount").setText(str(self.media_count))
    
    def increment_data_count(self):
        self.data_count = self.data_manager.increment_tool_count('data_count')
        self.data_count_widget.findChild(QLabel, "statCount").setText(str(self.data_count))

    def show_message(self, message, title="提示"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open(resource_path("styles.qss"), "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())