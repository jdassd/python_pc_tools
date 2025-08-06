from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget,
                             QFileDialog, QMessageBox, QProgressBar, QComboBox, 
                             QCheckBox, QSpinBox, QGroupBox, QGridLayout, QListWidget,
                             QSlider, QColorDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap
from utils import resource_path
import media_utils
import os
import time
from pathlib import Path

class MediaWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "screenshot":
                region = self.kwargs.get('region')
                delay = self.kwargs.get('delay', 0)
                result = media_utils.capture_screen(
                    self.kwargs['save_path'],
                    region,
                    delay
                )
                self.finished.emit(f"截图保存到: {result}")
            
            elif self.operation == "create_gif":
                result = media_utils.create_gif_from_images(
                    self.kwargs['image_paths'],
                    self.kwargs['output_path'],
                    self.kwargs.get('duration', 500),
                    self.kwargs.get('loop', 0)
                )
                self.finished.emit(f"GIF创建完成: {result}")
            
            elif self.operation == "optimize_gif":
                result = media_utils.optimize_gif(
                    self.kwargs['input_path'],
                    self.kwargs['output_path'],
                    self.kwargs.get('max_colors', 256),
                    self.kwargs.get('resize_ratio', 1.0)
                )
                self.finished.emit(f"GIF优化完成: {result}")
            
            elif self.operation == "generate_barcode":
                result = media_utils.generate_barcode(
                    self.kwargs['data'],
                    self.kwargs['barcode_type'],
                    self.kwargs['output_path'],
                    **self.kwargs.get('options', {})
                )
                self.finished.emit(f"条形码生成完成: {result}")
            
            elif self.operation == "create_collage":
                result = media_utils.create_image_collage(
                    self.kwargs['image_paths'],
                    self.kwargs['output_path'],
                    self.kwargs.get('layout', 'grid'),
                    self.kwargs.get('spacing', 10),
                    self.kwargs.get('background_color', 'white')
                )
                self.finished.emit(f"图片拼贴完成: {result}")
            
            elif self.operation == "create_gallery":
                result = media_utils.create_thumbnail_gallery(
                    self.kwargs['image_directory'],
                    self.kwargs['output_path'],
                    self.kwargs.get('thumbnail_size', (150, 150)),
                    self.kwargs.get('columns', 5),
                    self.kwargs.get('spacing', 10),
                    self.kwargs.get('background_color', 'white'),
                    self.kwargs.get('show_filenames', True)
                )
                self.finished.emit(f"缩略图画廊创建完成: {result}")
            
            elif self.operation == "extract_gif_frames":
                result = media_utils.extract_frames_from_gif(
                    self.kwargs['gif_path'],
                    self.kwargs['output_directory'],
                    self.kwargs.get('frame_format', 'png')
                )
                self.finished.emit(f"GIF帧提取完成，提取了{len(result)}帧")
            
            elif self.operation == "batch_resize":
                result = media_utils.resize_image_batch(
                    self.kwargs['input_directory'],
                    self.kwargs['output_directory'],
                    self.kwargs['new_size'],
                    self.kwargs.get('maintain_aspect', True),
                    self.kwargs.get('quality', 95)
                )
                self.finished.emit(f"批量调整尺寸完成，处理了{len(result)}个文件")
            
            elif self.operation == "add_watermark":
                result = media_utils.create_image_watermark(
                    self.kwargs['image_path'],
                    self.kwargs['watermark_text'],
                    self.kwargs['output_path'],
                    self.kwargs.get('position', 'bottom-right'),
                    self.kwargs.get('opacity', 128),
                    self.kwargs.get('font_size', 36)
                )
                self.finished.emit(f"水印添加完成: {result}")
                
        except Exception as e:
            self.error.emit(str(e))

class MediaWindow(QMainWindow):
    operation_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("媒体增强工具")
        self.setGeometry(200, 200, 1000, 700)
        self.setWindowIcon(QIcon(resource_path("媒体.png")))
        
        self.screenshot_timer = QTimer()
        self.screenshot_timer.setSingleShot(True)
        self.screenshot_timer.timeout.connect(self.take_delayed_screenshot)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 屏幕截图选项卡
        self.screenshot_tab = self.create_screenshot_tab()
        self.tab_widget.addTab(self.screenshot_tab, "屏幕截图")
        
        # GIF制作选项卡
        self.gif_tab = self.create_gif_tab()
        self.tab_widget.addTab(self.gif_tab, "GIF制作")
        
        # 条形码生成选项卡
        self.barcode_tab = self.create_barcode_tab()
        self.tab_widget.addTab(self.barcode_tab, "条形码生成")
        
        # 图片处理选项卡
        self.image_tab = self.create_image_tab()
        self.tab_widget.addTab(self.image_tab, "图片处理")
        
    def create_screenshot_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 截图类型选择
        type_group = QGroupBox("截图类型")
        type_layout = QVBoxLayout(type_group)
        
        self.screenshot_type = QComboBox()
        self.screenshot_type.addItems(["全屏截图", "区域截图"])
        self.screenshot_type.currentTextChanged.connect(self.on_screenshot_type_changed)
        type_layout.addWidget(self.screenshot_type)
        
        # 区域设置（默认隐藏）
        self.region_widget = QWidget()
        region_layout = QGridLayout(self.region_widget)
        
        region_layout.addWidget(QLabel("X坐标:"), 0, 0)
        self.region_x = QSpinBox()
        self.region_x.setRange(0, 9999)
        region_layout.addWidget(self.region_x, 0, 1)
        
        region_layout.addWidget(QLabel("Y坐标:"), 0, 2)
        self.region_y = QSpinBox()
        self.region_y.setRange(0, 9999)
        region_layout.addWidget(self.region_y, 0, 3)
        
        region_layout.addWidget(QLabel("宽度:"), 1, 0)
        self.region_width = QSpinBox()
        self.region_width.setRange(1, 9999)
        self.region_width.setValue(800)
        region_layout.addWidget(self.region_width, 1, 1)
        
        region_layout.addWidget(QLabel("高度:"), 1, 2)
        self.region_height = QSpinBox()
        self.region_height.setRange(1, 9999)
        self.region_height.setValue(600)
        region_layout.addWidget(self.region_height, 1, 3)
        
        self.region_widget.setVisible(False)
        type_layout.addWidget(self.region_widget)
        
        layout.addWidget(type_group)
        
        # 截图设置
        settings_group = QGroupBox("截图设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("延时(秒):"), 0, 0)
        self.screenshot_delay = QSpinBox()
        self.screenshot_delay.setRange(0, 60)
        settings_layout.addWidget(self.screenshot_delay, 0, 1)
        
        settings_layout.addWidget(QLabel("保存路径:"), 1, 0)
        self.screenshot_path = QLineEdit()
        self.screenshot_path.setPlaceholderText("选择保存路径...")
        settings_layout.addWidget(self.screenshot_path, 1, 1)
        
        self.select_screenshot_path_btn = QPushButton("选择路径")
        self.select_screenshot_path_btn.clicked.connect(self.select_screenshot_path)
        settings_layout.addWidget(self.select_screenshot_path_btn, 1, 2)
        
        layout.addWidget(settings_group)
        
        # 截图按钮
        screenshot_btn = QPushButton("开始截图")
        screenshot_btn.clicked.connect(self.take_screenshot)
        layout.addWidget(screenshot_btn)
        
        # 标注功能
        annotation_group = QGroupBox("截图标注")
        annotation_layout = QVBoxLayout(annotation_group)
        
        # 当前截图显示
        self.screenshot_preview = QLabel()
        self.screenshot_preview.setMinimumHeight(200)
        self.screenshot_preview.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.screenshot_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_preview.setText("截图预览将显示在这里")
        annotation_layout.addWidget(self.screenshot_preview)
        
        # 标注工具（简化版）
        annotation_btn_layout = QHBoxLayout()
        self.add_text_btn = QPushButton("添加文本")
        self.add_rect_btn = QPushButton("添加矩形")
        self.save_annotated_btn = QPushButton("保存标注")
        
        annotation_btn_layout.addWidget(self.add_text_btn)
        annotation_btn_layout.addWidget(self.add_rect_btn)
        annotation_btn_layout.addWidget(self.save_annotated_btn)
        annotation_btn_layout.addStretch()
        
        annotation_layout.addLayout(annotation_btn_layout)
        
        layout.addWidget(annotation_group)
        
        layout.addStretch()
        return widget
    
    def create_gif_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # GIF创建
        create_group = QGroupBox("从图片创建GIF")
        create_layout = QVBoxLayout(create_group)
        
        # 图片选择
        self.gif_images_list = QListWidget()
        create_layout.addWidget(self.gif_images_list)
        
        images_btn_layout = QHBoxLayout()
        self.add_gif_images_btn = QPushButton("添加图片")
        self.add_gif_images_btn.clicked.connect(self.add_gif_images)
        self.remove_gif_images_btn = QPushButton("移除选中")
        self.remove_gif_images_btn.clicked.connect(self.remove_gif_images)
        self.clear_gif_images_btn = QPushButton("清空列表")
        self.clear_gif_images_btn.clicked.connect(self.clear_gif_images)
        
        images_btn_layout.addWidget(self.add_gif_images_btn)
        images_btn_layout.addWidget(self.remove_gif_images_btn)
        images_btn_layout.addWidget(self.clear_gif_images_btn)
        images_btn_layout.addStretch()
        create_layout.addLayout(images_btn_layout)
        
        # GIF设置
        gif_settings_layout = QGridLayout()
        
        gif_settings_layout.addWidget(QLabel("帧持续时间(毫秒):"), 0, 0)
        self.gif_duration = QSpinBox()
        self.gif_duration.setRange(10, 10000)
        self.gif_duration.setValue(500)
        gif_settings_layout.addWidget(self.gif_duration, 0, 1)
        
        gif_settings_layout.addWidget(QLabel("循环次数:"), 0, 2)
        self.gif_loop = QSpinBox()
        self.gif_loop.setRange(0, 100)
        self.gif_loop.setValue(0)  # 0表示无限循环
        gif_settings_layout.addWidget(self.gif_loop, 0, 3)
        
        gif_settings_layout.addWidget(QLabel("输出路径:"), 1, 0)
        self.gif_output_path = QLineEdit()
        self.gif_output_path.setPlaceholderText("选择GIF保存路径...")
        gif_settings_layout.addWidget(self.gif_output_path, 1, 1, 1, 2)
        
        self.select_gif_output_btn = QPushButton("选择路径")
        self.select_gif_output_btn.clicked.connect(self.select_gif_output)
        gif_settings_layout.addWidget(self.select_gif_output_btn, 1, 3)
        
        create_layout.addLayout(gif_settings_layout)
        
        # 创建GIF按钮
        self.create_gif_btn = QPushButton("创建GIF")
        self.create_gif_btn.clicked.connect(self.create_gif)
        create_layout.addWidget(self.create_gif_btn)
        
        layout.addWidget(create_group)
        
        # GIF优化
        optimize_group = QGroupBox("GIF优化")
        optimize_layout = QGridLayout(optimize_group)
        
        optimize_layout.addWidget(QLabel("输入GIF:"), 0, 0)
        self.optimize_input_path = QLineEdit()
        self.optimize_input_path.setPlaceholderText("选择要优化的GIF...")
        optimize_layout.addWidget(self.optimize_input_path, 0, 1)
        
        self.select_optimize_input_btn = QPushButton("选择GIF")
        self.select_optimize_input_btn.clicked.connect(self.select_optimize_input)
        optimize_layout.addWidget(self.select_optimize_input_btn, 0, 2)
        
        optimize_layout.addWidget(QLabel("最大颜色数:"), 1, 0)
        self.max_colors = QSpinBox()
        self.max_colors.setRange(8, 256)
        self.max_colors.setValue(256)
        optimize_layout.addWidget(self.max_colors, 1, 1)
        
        optimize_layout.addWidget(QLabel("缩放比例:"), 1, 2)
        self.resize_ratio = QComboBox()
        self.resize_ratio.addItems(["1.0", "0.8", "0.6", "0.5", "0.4"])
        optimize_layout.addWidget(self.resize_ratio, 1, 3)
        
        optimize_layout.addWidget(QLabel("输出路径:"), 2, 0)
        self.optimize_output_path = QLineEdit()
        self.optimize_output_path.setPlaceholderText("选择优化后保存路径...")
        optimize_layout.addWidget(self.optimize_output_path, 2, 1)
        
        self.select_optimize_output_btn = QPushButton("选择路径")
        self.select_optimize_output_btn.clicked.connect(self.select_optimize_output)
        optimize_layout.addWidget(self.select_optimize_output_btn, 2, 2)
        
        self.optimize_gif_btn = QPushButton("优化GIF")
        self.optimize_gif_btn.clicked.connect(self.optimize_gif)
        optimize_layout.addWidget(self.optimize_gif_btn, 3, 0, 1, 4)
        
        layout.addWidget(optimize_group)
        
        # GIF帧提取
        extract_group = QGroupBox("GIF帧提取")
        extract_layout = QGridLayout(extract_group)
        
        extract_layout.addWidget(QLabel("GIF文件:"), 0, 0)
        self.extract_gif_path = QLineEdit()
        self.extract_gif_path.setPlaceholderText("选择GIF文件...")
        extract_layout.addWidget(self.extract_gif_path, 0, 1)
        
        self.select_extract_gif_btn = QPushButton("选择GIF")
        self.select_extract_gif_btn.clicked.connect(self.select_extract_gif)
        extract_layout.addWidget(self.select_extract_gif_btn, 0, 2)
        
        extract_layout.addWidget(QLabel("输出目录:"), 1, 0)
        self.extract_output_dir = QLineEdit()
        self.extract_output_dir.setPlaceholderText("选择输出目录...")
        extract_layout.addWidget(self.extract_output_dir, 1, 1)
        
        self.select_extract_output_btn = QPushButton("选择目录")
        self.select_extract_output_btn.clicked.connect(self.select_extract_output)
        extract_layout.addWidget(self.select_extract_output_btn, 1, 2)
        
        extract_layout.addWidget(QLabel("帧格式:"), 2, 0)
        self.frame_format = QComboBox()
        self.frame_format.addItems(["png", "jpg", "bmp"])
        extract_layout.addWidget(self.frame_format, 2, 1)
        
        self.extract_frames_btn = QPushButton("提取帧")
        self.extract_frames_btn.clicked.connect(self.extract_gif_frames)
        extract_layout.addWidget(self.extract_frames_btn, 3, 0, 1, 3)
        
        layout.addWidget(extract_group)
        
        layout.addStretch()
        return widget
    
    def create_barcode_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 条形码设置
        settings_group = QGroupBox("条形码设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("条形码类型:"), 0, 0)
        self.barcode_type = QComboBox()
        self.barcode_type.addItems(["Code128", "Code39", "EAN13", "EAN8", "UPC"])
        settings_layout.addWidget(self.barcode_type, 0, 1)
        
        settings_layout.addWidget(QLabel("数据内容:"), 1, 0)
        self.barcode_data = QLineEdit()
        self.barcode_data.setPlaceholderText("输入要编码的数据...")
        settings_layout.addWidget(self.barcode_data, 1, 1, 1, 2)
        
        layout.addWidget(settings_group)
        
        # 样式设置
        style_group = QGroupBox("样式设置")
        style_layout = QGridLayout(style_group)
        
        style_layout.addWidget(QLabel("模块宽度:"), 0, 0)
        self.module_width = QComboBox()
        self.module_width.addItems(["0.1", "0.2", "0.3", "0.4", "0.5"])
        self.module_width.setCurrentText("0.2")
        style_layout.addWidget(self.module_width, 0, 1)
        
        style_layout.addWidget(QLabel("模块高度:"), 0, 2)
        self.module_height = QSpinBox()
        self.module_height.setRange(5, 50)
        self.module_height.setValue(15)
        style_layout.addWidget(self.module_height, 0, 3)
        
        style_layout.addWidget(QLabel("字体大小:"), 1, 0)
        self.barcode_font_size = QSpinBox()
        self.barcode_font_size.setRange(6, 24)
        self.barcode_font_size.setValue(10)
        style_layout.addWidget(self.barcode_font_size, 1, 1)
        
        style_layout.addWidget(QLabel("文字距离:"), 1, 2)
        self.text_distance = QSpinBox()
        self.text_distance.setRange(1, 20)
        self.text_distance.setValue(5)
        style_layout.addWidget(self.text_distance, 1, 3)
        
        layout.addWidget(style_group)
        
        # 输出设置
        output_layout = QHBoxLayout()
        self.barcode_output_path = QLineEdit()
        self.barcode_output_path.setPlaceholderText("选择保存路径...")
        output_layout.addWidget(self.barcode_output_path)
        
        self.select_barcode_output_btn = QPushButton("选择路径")
        self.select_barcode_output_btn.clicked.connect(self.select_barcode_output)
        output_layout.addWidget(self.select_barcode_output_btn)
        
        layout.addLayout(output_layout)
        
        # 生成按钮
        self.generate_barcode_btn = QPushButton("生成条形码")
        self.generate_barcode_btn.clicked.connect(self.generate_barcode)
        layout.addWidget(self.generate_barcode_btn)
        
        # 预览
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.barcode_preview = QLabel()
        self.barcode_preview.setMinimumHeight(150)
        self.barcode_preview.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.barcode_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.barcode_preview.setText("条形码预览将显示在这里")
        preview_layout.addWidget(self.barcode_preview)
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
        return widget
    
    def create_image_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 选择操作类型
        operation_group = QGroupBox("操作选择")
        operation_layout = QHBoxLayout(operation_group)
        
        self.image_operation = QComboBox()
        self.image_operation.addItems([
            "图片拼贴",
            "缩略图画廊",
            "批量调整尺寸",
            "添加水印"
        ])
        self.image_operation.currentTextChanged.connect(self.on_image_operation_changed)
        
        operation_layout.addWidget(QLabel("操作类型:"))
        operation_layout.addWidget(self.image_operation)
        operation_layout.addStretch()
        
        layout.addWidget(operation_group)
        
        # 动态参数区域
        self.image_params_widget = QWidget()
        self.image_params_layout = QVBoxLayout(self.image_params_widget)
        layout.addWidget(self.image_params_widget)
        
        # 执行按钮
        btn_layout = QHBoxLayout()
        self.execute_image_btn = QPushButton("执行操作")
        self.execute_image_btn.clicked.connect(self.execute_image_operation)
        btn_layout.addWidget(self.execute_image_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 进度条
        self.image_progress = QProgressBar()
        self.image_progress.setVisible(False)
        layout.addWidget(self.image_progress)
        
        # 初始化界面
        self.on_image_operation_changed("图片拼贴")
        return widget
    
    def on_screenshot_type_changed(self, screenshot_type):
        if screenshot_type == "区域截图":
            self.region_widget.setVisible(True)
        else:
            self.region_widget.setVisible(False)
    
    def on_image_operation_changed(self, operation):
        # 清空现有控件
        for i in reversed(range(self.image_params_layout.count())):
            self.image_params_layout.itemAt(i).widget().setParent(None)
        
        if operation == "图片拼贴":
            self.create_collage_ui()
        elif operation == "缩略图画廊":
            self.create_gallery_ui()
        elif operation == "批量调整尺寸":
            self.create_batch_resize_ui()
        elif operation == "添加水印":
            self.create_watermark_ui()
    
    def create_collage_ui(self):
        # 图片选择
        images_group = QGroupBox("图片选择")
        images_layout = QVBoxLayout(images_group)
        
        self.collage_images_list = QListWidget()
        images_layout.addWidget(self.collage_images_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加图片")
        add_btn.clicked.connect(self.add_collage_images)
        remove_btn = QPushButton("移除选中")
        remove_btn.clicked.connect(self.remove_collage_images)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        images_layout.addLayout(btn_layout)
        
        self.image_params_layout.addWidget(images_group)
        
        # 拼贴设置
        settings_group = QGroupBox("拼贴设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("布局:"), 0, 0)
        self.collage_layout = QComboBox()
        self.collage_layout.addItems(["网格", "水平", "垂直"])
        settings_layout.addWidget(self.collage_layout, 0, 1)
        
        settings_layout.addWidget(QLabel("间距:"), 0, 2)
        self.collage_spacing = QSpinBox()
        self.collage_spacing.setRange(0, 100)
        self.collage_spacing.setValue(10)
        settings_layout.addWidget(self.collage_spacing, 0, 3)
        
        settings_layout.addWidget(QLabel("背景颜色:"), 1, 0)
        self.collage_bg_color = QPushButton("选择颜色")
        self.collage_bg_color.clicked.connect(self.select_collage_bg_color)
        self.collage_bg_color.setStyleSheet("background-color: white;")
        settings_layout.addWidget(self.collage_bg_color, 1, 1)
        
        # 输出路径
        settings_layout.addWidget(QLabel("输出路径:"), 2, 0)
        self.collage_output_path = QLineEdit()
        self.collage_output_path.setPlaceholderText("选择保存路径...")
        settings_layout.addWidget(self.collage_output_path, 2, 1, 1, 2)
        
        select_output_btn = QPushButton("选择路径")
        select_output_btn.clicked.connect(self.select_collage_output)
        settings_layout.addWidget(select_output_btn, 2, 3)
        
        self.image_params_layout.addWidget(settings_group)
    
    def create_gallery_ui(self):
        # 目录选择
        dir_layout = QHBoxLayout()
        self.gallery_input_dir = QLineEdit()
        self.gallery_input_dir.setPlaceholderText("选择图片目录...")
        select_dir_btn = QPushButton("选择目录")
        select_dir_btn.clicked.connect(self.select_gallery_input_dir)
        
        dir_layout.addWidget(self.gallery_input_dir)
        dir_layout.addWidget(select_dir_btn)
        self.image_params_layout.addLayout(dir_layout)
        
        # 画廊设置
        settings_group = QGroupBox("画廊设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("缩略图宽度:"), 0, 0)
        self.thumbnail_width = QSpinBox()
        self.thumbnail_width.setRange(50, 500)
        self.thumbnail_width.setValue(150)
        settings_layout.addWidget(self.thumbnail_width, 0, 1)
        
        settings_layout.addWidget(QLabel("缩略图高度:"), 0, 2)
        self.thumbnail_height = QSpinBox()
        self.thumbnail_height.setRange(50, 500)
        self.thumbnail_height.setValue(150)
        settings_layout.addWidget(self.thumbnail_height, 0, 3)
        
        settings_layout.addWidget(QLabel("列数:"), 1, 0)
        self.gallery_columns = QSpinBox()
        self.gallery_columns.setRange(1, 20)
        self.gallery_columns.setValue(5)
        settings_layout.addWidget(self.gallery_columns, 1, 1)
        
        self.show_filenames = QCheckBox("显示文件名")
        self.show_filenames.setChecked(True)
        settings_layout.addWidget(self.show_filenames, 1, 2, 1, 2)
        
        # 输出路径
        settings_layout.addWidget(QLabel("输出路径:"), 2, 0)
        self.gallery_output_path = QLineEdit()
        self.gallery_output_path.setPlaceholderText("选择保存路径...")
        settings_layout.addWidget(self.gallery_output_path, 2, 1, 1, 2)
        
        select_output_btn = QPushButton("选择路径")
        select_output_btn.clicked.connect(self.select_gallery_output)
        settings_layout.addWidget(select_output_btn, 2, 3)
        
        self.image_params_layout.addWidget(settings_group)
    
    def create_batch_resize_ui(self):
        # 输入输出目录
        dir_group = QGroupBox("目录设置")
        dir_layout = QGridLayout(dir_group)
        
        dir_layout.addWidget(QLabel("输入目录:"), 0, 0)
        self.resize_input_dir = QLineEdit()
        self.resize_input_dir.setPlaceholderText("选择输入目录...")
        dir_layout.addWidget(self.resize_input_dir, 0, 1)
        
        select_input_btn = QPushButton("选择目录")
        select_input_btn.clicked.connect(self.select_resize_input_dir)
        dir_layout.addWidget(select_input_btn, 0, 2)
        
        dir_layout.addWidget(QLabel("输出目录:"), 1, 0)
        self.resize_output_dir = QLineEdit()
        self.resize_output_dir.setPlaceholderText("选择输出目录...")
        dir_layout.addWidget(self.resize_output_dir, 1, 1)
        
        select_output_btn = QPushButton("选择目录")
        select_output_btn.clicked.connect(self.select_resize_output_dir)
        dir_layout.addWidget(select_output_btn, 1, 2)
        
        self.image_params_layout.addWidget(dir_group)
        
        # 尺寸设置
        size_group = QGroupBox("尺寸设置")
        size_layout = QGridLayout(size_group)
        
        size_layout.addWidget(QLabel("新宽度:"), 0, 0)
        self.new_width = QSpinBox()
        self.new_width.setRange(1, 9999)
        self.new_width.setValue(800)
        size_layout.addWidget(self.new_width, 0, 1)
        
        size_layout.addWidget(QLabel("新高度:"), 0, 2)
        self.new_height = QSpinBox()
        self.new_height.setRange(1, 9999)
        self.new_height.setValue(600)
        size_layout.addWidget(self.new_height, 0, 3)
        
        self.maintain_aspect = QCheckBox("保持宽高比")
        self.maintain_aspect.setChecked(True)
        size_layout.addWidget(self.maintain_aspect, 1, 0, 1, 2)
        
        size_layout.addWidget(QLabel("JPEG质量:"), 1, 2)
        self.jpeg_quality = QSpinBox()
        self.jpeg_quality.setRange(1, 100)
        self.jpeg_quality.setValue(95)
        size_layout.addWidget(self.jpeg_quality, 1, 3)
        
        self.image_params_layout.addWidget(size_group)
    
    def create_watermark_ui(self):
        # 图片选择
        image_layout = QHBoxLayout()
        self.watermark_image_path = QLineEdit()
        self.watermark_image_path.setPlaceholderText("选择图片...")
        select_image_btn = QPushButton("选择图片")
        select_image_btn.clicked.connect(self.select_watermark_image)
        
        image_layout.addWidget(self.watermark_image_path)
        image_layout.addWidget(select_image_btn)
        self.image_params_layout.addLayout(image_layout)
        
        # 水印设置
        watermark_group = QGroupBox("水印设置")
        watermark_layout = QGridLayout(watermark_group)
        
        watermark_layout.addWidget(QLabel("水印文字:"), 0, 0)
        self.watermark_text = QLineEdit()
        self.watermark_text.setPlaceholderText("输入水印文字...")
        watermark_layout.addWidget(self.watermark_text, 0, 1, 1, 3)
        
        watermark_layout.addWidget(QLabel("位置:"), 1, 0)
        self.watermark_position = QComboBox()
        self.watermark_position.addItems([
            "右下角", "左下角", "右上角", "左上角", "中心"
        ])
        watermark_layout.addWidget(self.watermark_position, 1, 1)
        
        watermark_layout.addWidget(QLabel("透明度:"), 1, 2)
        self.watermark_opacity = QSpinBox()
        self.watermark_opacity.setRange(0, 255)
        self.watermark_opacity.setValue(128)
        watermark_layout.addWidget(self.watermark_opacity, 1, 3)
        
        watermark_layout.addWidget(QLabel("字体大小:"), 2, 0)
        self.watermark_font_size = QSpinBox()
        self.watermark_font_size.setRange(12, 100)
        self.watermark_font_size.setValue(36)
        watermark_layout.addWidget(self.watermark_font_size, 2, 1)
        
        # 输出路径
        watermark_layout.addWidget(QLabel("输出路径:"), 3, 0)
        self.watermark_output_path = QLineEdit()
        self.watermark_output_path.setPlaceholderText("选择保存路径...")
        watermark_layout.addWidget(self.watermark_output_path, 3, 1, 1, 2)
        
        select_output_btn = QPushButton("选择路径")
        select_output_btn.clicked.connect(self.select_watermark_output)
        watermark_layout.addWidget(select_output_btn, 3, 3)
        
        self.image_params_layout.addWidget(watermark_group)
    
    # 事件处理方法
    def select_screenshot_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存截图", "", "PNG图片 (*.png);;JPEG图片 (*.jpg)"
        )
        if file_path:
            self.screenshot_path.setText(file_path)
    
    def take_screenshot(self):
        save_path = self.screenshot_path.text()
        if not save_path:
            QMessageBox.warning(self, "警告", "请设置保存路径")
            return
        
        delay = self.screenshot_delay.value()
        region = None
        
        if self.screenshot_type.currentText() == "区域截图":
            region = (
                self.region_x.value(),
                self.region_y.value(),
                self.region_width.value(),
                self.region_height.value()
            )
        
        if delay > 0:
            QMessageBox.information(self, "提示", f"将在{delay}秒后开始截图")
            self.screenshot_timer.start(delay * 1000)
            self.delayed_screenshot_params = (save_path, region)
        else:
            self.take_delayed_screenshot(save_path, region)
    
    def take_delayed_screenshot(self, save_path=None, region=None):
        if save_path is None:
            save_path, region = self.delayed_screenshot_params
        
        self.media_worker = MediaWorker(
            "screenshot",
            save_path=save_path,
            region=region,
            delay=0
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def add_gif_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        for file in files:
            self.gif_images_list.addItem(file)
    
    def remove_gif_images(self):
        current_row = self.gif_images_list.currentRow()
        if current_row >= 0:
            self.gif_images_list.takeItem(current_row)
    
    def clear_gif_images(self):
        self.gif_images_list.clear()
    
    def select_gif_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存GIF", "", "GIF文件 (*.gif)"
        )
        if file_path:
            self.gif_output_path.setText(file_path)
    
    def create_gif(self):
        image_paths = [self.gif_images_list.item(i).text() 
                      for i in range(self.gif_images_list.count())]
        output_path = self.gif_output_path.text()
        
        if not image_paths:
            QMessageBox.warning(self, "警告", "请添加图片")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请设置输出路径")
            return
        
        duration = self.gif_duration.value()
        loop = self.gif_loop.value()
        
        self.media_worker = MediaWorker(
            "create_gif",
            image_paths=image_paths,
            output_path=output_path,
            duration=duration,
            loop=loop
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def select_optimize_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择GIF", "", "GIF文件 (*.gif)"
        )
        if file_path:
            self.optimize_input_path.setText(file_path)
    
    def select_optimize_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存优化GIF", "", "GIF文件 (*.gif)"
        )
        if file_path:
            self.optimize_output_path.setText(file_path)
    
    def optimize_gif(self):
        input_path = self.optimize_input_path.text()
        output_path = self.optimize_output_path.text()
        
        if not input_path or not os.path.exists(input_path):
            QMessageBox.warning(self, "警告", "请选择有效的GIF文件")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请设置输出路径")
            return
        
        max_colors = self.max_colors.value()
        resize_ratio = float(self.resize_ratio.currentText())
        
        self.media_worker = MediaWorker(
            "optimize_gif",
            input_path=input_path,
            output_path=output_path,
            max_colors=max_colors,
            resize_ratio=resize_ratio
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def select_extract_gif(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择GIF", "", "GIF文件 (*.gif)"
        )
        if file_path:
            self.extract_gif_path.setText(file_path)
    
    def select_extract_output(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.extract_output_dir.setText(directory)
    
    def extract_gif_frames(self):
        gif_path = self.extract_gif_path.text()
        output_dir = self.extract_output_dir.text()
        
        if not gif_path or not os.path.exists(gif_path):
            QMessageBox.warning(self, "警告", "请选择有效的GIF文件")
            return
        
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        frame_format = self.frame_format.currentText()
        
        self.media_worker = MediaWorker(
            "extract_gif_frames",
            gif_path=gif_path,
            output_directory=output_dir,
            frame_format=frame_format
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def select_barcode_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存条形码", "", "PNG图片 (*.png)"
        )
        if file_path:
            self.barcode_output_path.setText(file_path)
    
    def generate_barcode(self):
        data = self.barcode_data.text()
        barcode_type = self.barcode_type.currentText().lower()
        output_path = self.barcode_output_path.text()
        
        if not data:
            QMessageBox.warning(self, "警告", "请输入数据内容")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请设置输出路径")
            return
        
        options = {
            'module_width': float(self.module_width.currentText()),
            'module_height': self.module_height.value(),
            'font_size': self.barcode_font_size.value(),
            'text_distance': self.text_distance.value(),
        }
        
        self.media_worker = MediaWorker(
            "generate_barcode",
            data=data,
            barcode_type=barcode_type,
            output_path=output_path,
            options=options
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def execute_image_operation(self):
        operation = self.image_operation.currentText()
        
        try:
            if operation == "图片拼贴":
                self.execute_collage()
            elif operation == "缩略图画廊":
                self.execute_gallery()
            elif operation == "批量调整尺寸":
                self.execute_batch_resize()
            elif operation == "添加水印":
                self.execute_watermark()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def execute_collage(self):
        image_paths = [self.collage_images_list.item(i).text() 
                      for i in range(self.collage_images_list.count())]
        output_path = self.collage_output_path.text()
        
        if not image_paths:
            QMessageBox.warning(self, "警告", "请添加图片")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请设置输出路径")
            return
        
        layout_map = {"网格": "grid", "水平": "horizontal", "垂直": "vertical"}
        layout = layout_map[self.collage_layout.currentText()]
        spacing = self.collage_spacing.value()
        
        self.image_progress.setVisible(True)
        self.image_progress.setRange(0, 0)
        
        self.media_worker = MediaWorker(
            "create_collage",
            image_paths=image_paths,
            output_path=output_path,
            layout=layout,
            spacing=spacing,
            background_color='white'
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def execute_gallery(self):
        input_dir = self.gallery_input_dir.text()
        output_path = self.gallery_output_path.text()
        
        if not input_dir or not os.path.exists(input_dir):
            QMessageBox.warning(self, "警告", "请选择有效的输入目录")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请设置输出路径")
            return
        
        thumbnail_size = (self.thumbnail_width.value(), self.thumbnail_height.value())
        columns = self.gallery_columns.value()
        show_filenames = self.show_filenames.isChecked()
        
        self.image_progress.setVisible(True)
        self.image_progress.setRange(0, 0)
        
        self.media_worker = MediaWorker(
            "create_gallery",
            image_directory=input_dir,
            output_path=output_path,
            thumbnail_size=thumbnail_size,
            columns=columns,
            show_filenames=show_filenames
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def execute_batch_resize(self):
        input_dir = self.resize_input_dir.text()
        output_dir = self.resize_output_dir.text()
        
        if not input_dir or not os.path.exists(input_dir):
            QMessageBox.warning(self, "警告", "请选择有效的输入目录")
            return
        
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        new_size = (self.new_width.value(), self.new_height.value())
        maintain_aspect = self.maintain_aspect.isChecked()
        quality = self.jpeg_quality.value()
        
        self.image_progress.setVisible(True)
        self.image_progress.setRange(0, 0)
        
        self.media_worker = MediaWorker(
            "batch_resize",
            input_directory=input_dir,
            output_directory=output_dir,
            new_size=new_size,
            maintain_aspect=maintain_aspect,
            quality=quality
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    def execute_watermark(self):
        image_path = self.watermark_image_path.text()
        watermark_text = self.watermark_text.text()
        output_path = self.watermark_output_path.text()
        
        if not image_path or not os.path.exists(image_path):
            QMessageBox.warning(self, "警告", "请选择有效的图片")
            return
        
        if not watermark_text:
            QMessageBox.warning(self, "警告", "请输入水印文字")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请设置输出路径")
            return
        
        position_map = {
            "右下角": "bottom-right",
            "左下角": "bottom-left", 
            "右上角": "top-right",
            "左上角": "top-left",
            "中心": "center"
        }
        position = position_map[self.watermark_position.currentText()]
        opacity = self.watermark_opacity.value()
        font_size = self.watermark_font_size.value()
        
        self.image_progress.setVisible(True)
        self.image_progress.setRange(0, 0)
        
        self.media_worker = MediaWorker(
            "add_watermark",
            image_path=image_path,
            watermark_text=watermark_text,
            output_path=output_path,
            position=position,
            opacity=opacity,
            font_size=font_size
        )
        self.media_worker.finished.connect(self.on_media_finished)
        self.media_worker.error.connect(self.on_media_error)
        self.media_worker.start()
    
    # 辅助方法
    def add_collage_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        for file in files:
            self.collage_images_list.addItem(file)
    
    def remove_collage_images(self):
        current_row = self.collage_images_list.currentRow()
        if current_row >= 0:
            self.collage_images_list.takeItem(current_row)
    
    def select_collage_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.collage_bg_color.setStyleSheet(f"background-color: {color.name()};")
    
    def select_collage_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存拼贴图", "", "图片文件 (*.png *.jpg)"
        )
        if file_path:
            self.collage_output_path.setText(file_path)
    
    def select_gallery_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择图片目录")
        if directory:
            self.gallery_input_dir.setText(directory)
    
    def select_gallery_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存画廊", "", "图片文件 (*.png *.jpg)"
        )
        if file_path:
            self.gallery_output_path.setText(file_path)
    
    def select_resize_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输入目录")
        if directory:
            self.resize_input_dir.setText(directory)
    
    def select_resize_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.resize_output_dir.setText(directory)
    
    def select_watermark_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.watermark_image_path.setText(file_path)
    
    def select_watermark_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存水印图", "", "图片文件 (*.png *.jpg)"
        )
        if file_path:
            self.watermark_output_path.setText(file_path)
    
    def on_media_finished(self, message):
        self.image_progress.setVisible(False)
        QMessageBox.information(self, "完成", message)
        self.operation_successful.emit()
    
    def on_media_error(self, error):
        self.image_progress.setVisible(False)
        QMessageBox.critical(self, "错误", error)