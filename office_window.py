from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget,
                             QFileDialog, QMessageBox, QProgressBar, QComboBox, 
                             QCheckBox, QSpinBox, QGroupBox, QGridLayout, QListWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
from utils import resource_path
import office_utils
import os
import shutil
from pathlib import Path
import pandas as pd

class OfficeWorker(QThread):
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
            if self.operation == "merge_excel":
                result = office_utils.merge_excel_files(
                    self.kwargs['file_paths'],
                    self.kwargs['output_path'],
                    self.kwargs['merge_type']
                )
                self.finished.emit(f"Excel文件合并完成: {result}")
            
            elif self.operation == "split_excel":
                result = office_utils.split_excel_file(
                    self.kwargs['file_path'],
                    self.kwargs['output_dir'],
                    self.kwargs.get('split_column'),
                    self.kwargs.get('rows_per_file', 1000)
                )
                self.finished.emit(f"Excel文件拆分完成，生成了{len(result)}个文件")
            
            elif self.operation == "batch_rename":
                result = office_utils.batch_rename_advanced(
                    self.kwargs['directory'],
                    self.kwargs['pattern_type'],
                    self.kwargs['pattern_data']
                )
                self.finished.emit(f"批量重命名完成，处理了{len(result)}个文件")
            
            elif self.operation == "convert_format":
                result = office_utils.convert_file_format(
                    self.kwargs['input_file'],
                    self.kwargs['output_file'],
                    self.kwargs['format_type']
                )
                self.finished.emit(f"格式转换完成: {result}")
            
            elif self.operation == "clean_excel":
                result = office_utils.clean_excel_data(
                    self.kwargs['input_file'],
                    self.kwargs['output_file'],
                    self.kwargs['operations']
                )
                self.finished.emit(f"Excel数据清理完成: {result}")
            
            elif self.operation == "analyze_directory":
                result = office_utils.analyze_directory_structure(
                    self.kwargs['directory']
                )
                self.finished.emit("目录分析完成")
                # 通过信号传递结果数据
                self.kwargs['callback'](result)
                
        except Exception as e:
            self.error.emit(str(e))

class OfficeWindow(QMainWindow):
    operation_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("办公效率工具")
        self.setGeometry(200, 200, 1000, 700)
        self.setWindowIcon(QIcon(resource_path("办公.png")))
        
        # 文件监控和剪贴板历史
        self.file_observer = None
        self.clipboard_history = office_utils.ClipboardHistory()
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Excel处理选项卡
        self.excel_tab = self.create_excel_tab()
        self.tab_widget.addTab(self.excel_tab, "Excel处理")
        
        # 批量重命名选项卡
        self.rename_tab = self.create_rename_tab()
        self.tab_widget.addTab(self.rename_tab, "批量重命名")
        
        # 文件监控选项卡
        self.monitor_tab = self.create_monitor_tab()
        self.tab_widget.addTab(self.monitor_tab, "文件监控")
        
        # 剪贴板管理选项卡
        self.clipboard_tab = self.create_clipboard_tab()
        self.tab_widget.addTab(self.clipboard_tab, "剪贴板管理")
        
        # 目录分析选项卡
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "目录分析")
        
    def create_excel_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Excel文件操作选择
        operation_group = QGroupBox("操作选择")
        operation_layout = QHBoxLayout(operation_group)
        
        self.excel_operation = QComboBox()
        self.excel_operation.addItems([
            "合并Excel文件",
            "拆分Excel文件", 
            "格式转换",
            "数据清理"
        ])
        self.excel_operation.currentTextChanged.connect(self.on_excel_operation_changed)
        
        operation_layout.addWidget(QLabel("操作类型:"))
        operation_layout.addWidget(self.excel_operation)
        operation_layout.addStretch()
        
        layout.addWidget(operation_group)
        
        # 动态参数区域
        self.excel_params_widget = QWidget()
        self.excel_params_layout = QVBoxLayout(self.excel_params_widget)
        layout.addWidget(self.excel_params_widget)
        
        # 执行按钮
        btn_layout = QHBoxLayout()
        self.execute_excel_btn = QPushButton("执行操作")
        self.execute_excel_btn.clicked.connect(self.execute_excel_operation)
        btn_layout.addWidget(self.execute_excel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 进度条
        self.excel_progress = QProgressBar()
        self.excel_progress.setVisible(False)
        layout.addWidget(self.excel_progress)
        
        layout.addStretch()
        
        # 初始化界面
        self.on_excel_operation_changed("合并Excel文件")
        return widget
    
    def create_rename_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 目录选择
        dir_group = QGroupBox("目录选择")
        dir_layout = QHBoxLayout(dir_group)
        
        self.rename_dir_input = QLineEdit()
        self.rename_dir_input.setPlaceholderText("选择要重命名的目录...")
        self.select_rename_dir_btn = QPushButton("选择目录")
        self.select_rename_dir_btn.clicked.connect(self.select_rename_directory)
        
        dir_layout.addWidget(self.rename_dir_input)
        dir_layout.addWidget(self.select_rename_dir_btn)
        layout.addWidget(dir_group)
        
        # 重命名模式
        mode_group = QGroupBox("重命名模式")
        mode_layout = QVBoxLayout(mode_group)
        
        self.rename_mode = QComboBox()
        self.rename_mode.addItems(["序号重命名", "时间重命名", "替换重命名", "大小写转换"])
        self.rename_mode.currentTextChanged.connect(self.on_rename_mode_changed)
        mode_layout.addWidget(self.rename_mode)
        
        # 动态参数区域
        self.rename_params_widget = QWidget()
        self.rename_params_layout = QVBoxLayout(self.rename_params_widget)
        mode_layout.addWidget(self.rename_params_widget)
        
        layout.addWidget(mode_group)
        
        # 预览和执行
        preview_layout = QHBoxLayout()
        self.preview_rename_btn = QPushButton("预览重命名")
        self.preview_rename_btn.clicked.connect(self.preview_rename)
        self.execute_rename_btn = QPushButton("执行重命名")
        self.execute_rename_btn.clicked.connect(self.execute_rename)
        
        preview_layout.addWidget(self.preview_rename_btn)
        preview_layout.addWidget(self.execute_rename_btn)
        preview_layout.addStretch()
        layout.addLayout(preview_layout)
        
        # 预览结果
        self.rename_preview = QTableWidget()
        self.rename_preview.setColumnCount(2)
        self.rename_preview.setHorizontalHeaderLabels(["原文件名", "新文件名"])
        self.rename_preview.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.rename_preview)
        
        # 初始化界面
        self.on_rename_mode_changed("序号重命名")
        return widget
    
    def create_monitor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 监控设置
        settings_group = QGroupBox("监控设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("监控目录:"), 0, 0)
        self.monitor_dir_input = QLineEdit()
        self.monitor_dir_input.setPlaceholderText("选择要监控的目录...")
        settings_layout.addWidget(self.monitor_dir_input, 0, 1)
        
        self.select_monitor_dir_btn = QPushButton("选择目录")
        self.select_monitor_dir_btn.clicked.connect(self.select_monitor_directory)
        settings_layout.addWidget(self.select_monitor_dir_btn, 0, 2)
        
        self.include_subdirs = QCheckBox("包含子目录")
        settings_layout.addWidget(self.include_subdirs, 1, 0, 1, 3)
        
        layout.addWidget(settings_group)
        
        # 监控控制
        control_layout = QHBoxLayout()
        self.start_monitor_btn = QPushButton("开始监控")
        self.start_monitor_btn.clicked.connect(self.start_monitor)
        self.stop_monitor_btn = QPushButton("停止监控")
        self.stop_monitor_btn.clicked.connect(self.stop_monitor)
        self.stop_monitor_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_monitor_btn)
        control_layout.addWidget(self.stop_monitor_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 监控日志
        log_group = QGroupBox("监控日志")
        log_layout = QVBoxLayout(log_group)
        
        self.monitor_log = QTextEdit()
        self.monitor_log.setReadOnly(True)
        self.monitor_log.setMaximumHeight(200)
        log_layout.addWidget(self.monitor_log)
        
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(lambda: self.monitor_log.clear())
        log_layout.addWidget(clear_log_btn)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        return widget
    
    def create_clipboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制面板
        control_group = QGroupBox("剪贴板监控")
        control_layout = QHBoxLayout(control_group)
        
        self.start_clipboard_btn = QPushButton("开始监控")
        self.start_clipboard_btn.clicked.connect(self.start_clipboard_monitor)
        self.stop_clipboard_btn = QPushButton("停止监控")
        self.stop_clipboard_btn.clicked.connect(self.stop_clipboard_monitor)
        self.stop_clipboard_btn.setEnabled(False)
        
        self.clear_history_btn = QPushButton("清空历史")
        self.clear_history_btn.clicked.connect(self.clear_clipboard_history)
        
        control_layout.addWidget(self.start_clipboard_btn)
        control_layout.addWidget(self.stop_clipboard_btn)
        control_layout.addWidget(self.clear_history_btn)
        control_layout.addStretch()
        
        layout.addWidget(control_group)
        
        # 历史记录表格
        history_group = QGroupBox("剪贴板历史")
        history_layout = QVBoxLayout(history_group)
        
        self.clipboard_table = QTableWidget()
        self.clipboard_table.setColumnCount(3)
        self.clipboard_table.setHorizontalHeaderLabels(["时间", "类型", "内容预览"])
        self.clipboard_table.horizontalHeader().setStretchLastSection(True)
        self.clipboard_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.clipboard_table.doubleClicked.connect(self.restore_clipboard_item)
        history_layout.addWidget(self.clipboard_table)
        
        layout.addWidget(history_group)
        
        # 定时刷新历史记录
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self.update_clipboard_display)
        
        return widget
    
    def create_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 目录选择
        dir_group = QGroupBox("目录选择")
        dir_layout = QHBoxLayout(dir_group)
        
        self.analysis_dir_input = QLineEdit()
        self.analysis_dir_input.setPlaceholderText("选择要分析的目录...")
        self.select_analysis_dir_btn = QPushButton("选择目录")
        self.select_analysis_dir_btn.clicked.connect(self.select_analysis_directory)
        
        dir_layout.addWidget(self.analysis_dir_input)
        dir_layout.addWidget(self.select_analysis_dir_btn)
        layout.addWidget(dir_group)
        
        # 分析按钮
        analyze_btn = QPushButton("开始分析")
        analyze_btn.clicked.connect(self.analyze_directory)
        layout.addWidget(analyze_btn)
        
        # 分析结果
        result_group = QGroupBox("分析结果")
        result_layout = QVBoxLayout(result_group)
        
        # 基本信息
        self.basic_info = QTextEdit()
        self.basic_info.setMaximumHeight(120)
        self.basic_info.setReadOnly(True)
        result_layout.addWidget(self.basic_info)
        
        # 文件类型统计表格
        self.file_types_table = QTableWidget()
        self.file_types_table.setColumnCount(3)
        self.file_types_table.setHorizontalHeaderLabels(["文件类型", "数量", "大小(MB)"])
        result_layout.addWidget(self.file_types_table)
        
        # 大文件列表
        large_files_label = QLabel("大文件列表 (>10MB):")
        result_layout.addWidget(large_files_label)
        
        self.large_files_table = QTableWidget()
        self.large_files_table.setColumnCount(2)
        self.large_files_table.setHorizontalHeaderLabels(["文件路径", "大小(MB)"])
        self.large_files_table.horizontalHeader().setStretchLastSection(True)
        result_layout.addWidget(self.large_files_table)
        
        layout.addWidget(result_group)
        
        return widget
    
    def on_excel_operation_changed(self, operation):
        # 清空现有控件
        for i in reversed(range(self.excel_params_layout.count())):
            self.excel_params_layout.itemAt(i).widget().setParent(None)
        
        if operation == "合并Excel文件":
            self.create_merge_excel_ui()
        elif operation == "拆分Excel文件":
            self.create_split_excel_ui()
        elif operation == "格式转换":
            self.create_convert_format_ui()
        elif operation == "数据清理":
            self.create_clean_excel_ui()
    
    def create_merge_excel_ui(self):
        # 文件选择
        files_group = QGroupBox("文件选择")
        files_layout = QVBoxLayout(files_group)
        
        self.merge_files_list = QListWidget()
        files_layout.addWidget(self.merge_files_list)
        
        btn_layout = QHBoxLayout()
        add_files_btn = QPushButton("添加文件")
        add_files_btn.clicked.connect(self.add_merge_files)
        remove_files_btn = QPushButton("移除选中")
        remove_files_btn.clicked.connect(self.remove_merge_files)
        
        btn_layout.addWidget(add_files_btn)
        btn_layout.addWidget(remove_files_btn)
        btn_layout.addStretch()
        files_layout.addLayout(btn_layout)
        
        self.excel_params_layout.addWidget(files_group)
        
        # 合并选项
        options_group = QGroupBox("合并选项")
        options_layout = QVBoxLayout(options_group)
        
        self.merge_type = QComboBox()
        self.merge_type.addItems(["合并为不同工作表", "合并为同一工作表"])
        options_layout.addWidget(self.merge_type)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.merge_output_input = QLineEdit()
        self.merge_output_input.setPlaceholderText("选择输出文件...")
        select_output_btn = QPushButton("选择输出")
        select_output_btn.clicked.connect(self.select_merge_output)
        
        output_layout.addWidget(self.merge_output_input)
        output_layout.addWidget(select_output_btn)
        options_layout.addLayout(output_layout)
        
        self.excel_params_layout.addWidget(options_group)
    
    def create_split_excel_ui(self):
        # 文件选择
        file_layout = QHBoxLayout()
        self.split_file_input = QLineEdit()
        self.split_file_input.setPlaceholderText("选择要拆分的Excel文件...")
        select_file_btn = QPushButton("选择文件")
        select_file_btn.clicked.connect(self.select_split_file)
        
        file_layout.addWidget(self.split_file_input)
        file_layout.addWidget(select_file_btn)
        self.excel_params_layout.addLayout(file_layout)
        
        # 拆分选项
        options_group = QGroupBox("拆分选项")
        options_layout = QGridLayout(options_group)
        
        self.split_mode = QComboBox()
        self.split_mode.addItems(["按行数拆分", "按列值拆分"])
        self.split_mode.currentTextChanged.connect(self.on_split_mode_changed)
        options_layout.addWidget(QLabel("拆分方式:"), 0, 0)
        options_layout.addWidget(self.split_mode, 0, 1)
        
        # 行数选项
        self.rows_per_file = QSpinBox()
        self.rows_per_file.setRange(1, 100000)
        self.rows_per_file.setValue(1000)
        options_layout.addWidget(QLabel("每文件行数:"), 1, 0)
        options_layout.addWidget(self.rows_per_file, 1, 1)
        
        # 列名选项
        self.split_column = QLineEdit()
        self.split_column.setPlaceholderText("输入列名...")
        self.split_column.setEnabled(False)
        options_layout.addWidget(QLabel("拆分列名:"), 2, 0)
        options_layout.addWidget(self.split_column, 2, 1)
        
        # 输出目录
        output_layout = QHBoxLayout()
        self.split_output_dir = QLineEdit()
        self.split_output_dir.setPlaceholderText("选择输出目录...")
        select_dir_btn = QPushButton("选择目录")
        select_dir_btn.clicked.connect(self.select_split_output_dir)
        
        output_layout.addWidget(self.split_output_dir)
        output_layout.addWidget(select_dir_btn)
        options_layout.addLayout(output_layout, 3, 0, 1, 2)
        
        self.excel_params_layout.addWidget(options_group)
    
    def create_convert_format_ui(self):
        # 输入文件
        input_layout = QHBoxLayout()
        self.convert_input_file = QLineEdit()
        self.convert_input_file.setPlaceholderText("选择输入文件...")
        select_input_btn = QPushButton("选择文件")
        select_input_btn.clicked.connect(self.select_convert_input)
        
        input_layout.addWidget(self.convert_input_file)
        input_layout.addWidget(select_input_btn)
        self.excel_params_layout.addLayout(input_layout)
        
        # 转换类型
        type_layout = QHBoxLayout()
        self.convert_type = QComboBox()
        self.convert_type.addItems([
            "Excel转CSV",
            "CSV转Excel", 
            "Excel转JSON",
            "JSON转Excel"
        ])
        
        type_layout.addWidget(QLabel("转换类型:"))
        type_layout.addWidget(self.convert_type)
        type_layout.addStretch()
        self.excel_params_layout.addLayout(type_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.convert_output_file = QLineEdit()
        self.convert_output_file.setPlaceholderText("选择输出文件...")
        select_output_btn = QPushButton("选择输出")
        select_output_btn.clicked.connect(self.select_convert_output)
        
        output_layout.addWidget(self.convert_output_file)
        output_layout.addWidget(select_output_btn)
        self.excel_params_layout.addLayout(output_layout)
    
    def create_clean_excel_ui(self):
        # 输入文件
        input_layout = QHBoxLayout()
        self.clean_input_file = QLineEdit()
        self.clean_input_file.setPlaceholderText("选择要清理的Excel文件...")
        select_input_btn = QPushButton("选择文件")
        select_input_btn.clicked.connect(self.select_clean_input)
        
        input_layout.addWidget(self.clean_input_file)
        input_layout.addWidget(select_input_btn)
        self.excel_params_layout.addLayout(input_layout)
        
        # 清理选项
        options_group = QGroupBox("清理选项")
        options_layout = QVBoxLayout(options_group)
        
        self.remove_duplicates = QCheckBox("删除重复行")
        self.remove_empty_rows = QCheckBox("删除空行")
        self.remove_empty_columns = QCheckBox("删除空列")
        self.trim_whitespace = QCheckBox("去除前后空格")
        self.standardize_case = QCheckBox("标准化大小写")
        
        options_layout.addWidget(self.remove_duplicates)
        options_layout.addWidget(self.remove_empty_rows)
        options_layout.addWidget(self.remove_empty_columns)
        options_layout.addWidget(self.trim_whitespace)
        options_layout.addWidget(self.standardize_case)
        
        self.excel_params_layout.addWidget(options_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.clean_output_file = QLineEdit()
        self.clean_output_file.setPlaceholderText("选择输出文件...")
        select_output_btn = QPushButton("选择输出")
        select_output_btn.clicked.connect(self.select_clean_output)
        
        output_layout.addWidget(self.clean_output_file)
        output_layout.addWidget(select_output_btn)
        self.excel_params_layout.addLayout(output_layout)
    
    def on_rename_mode_changed(self, mode):
        # 清空现有控件
        for i in reversed(range(self.rename_params_layout.count())):
            self.rename_params_layout.itemAt(i).widget().setParent(None)
        
        if mode == "序号重命名":
            self.create_sequence_rename_ui()
        elif mode == "时间重命名":
            self.create_date_rename_ui()
        elif mode == "替换重命名":
            self.create_replace_rename_ui()
        elif mode == "大小写转换":
            self.create_case_rename_ui()
    
    def create_sequence_rename_ui(self):
        grid = QGridLayout()
        
        grid.addWidget(QLabel("前缀:"), 0, 0)
        self.seq_prefix = QLineEdit()
        self.seq_prefix.setText("file")
        grid.addWidget(self.seq_prefix, 0, 1)
        
        grid.addWidget(QLabel("起始数字:"), 1, 0)
        self.seq_start = QSpinBox()
        self.seq_start.setRange(0, 9999)
        self.seq_start.setValue(1)
        grid.addWidget(self.seq_start, 1, 1)
        
        grid.addWidget(QLabel("数字位数:"), 2, 0)
        self.seq_digits = QSpinBox()
        self.seq_digits.setRange(1, 10)
        self.seq_digits.setValue(3)
        grid.addWidget(self.seq_digits, 2, 1)
        
        self.rename_params_layout.addLayout(grid)
    
    def create_date_rename_ui(self):
        grid = QGridLayout()
        
        grid.addWidget(QLabel("前缀:"), 0, 0)
        self.date_prefix = QLineEdit()
        grid.addWidget(self.date_prefix, 0, 1)
        
        grid.addWidget(QLabel("后缀:"), 1, 0)
        self.date_suffix = QLineEdit()
        grid.addWidget(self.date_suffix, 1, 1)
        
        grid.addWidget(QLabel("日期格式:"), 2, 0)
        self.date_format = QComboBox()
        self.date_format.addItems([
            "%Y%m%d_%H%M%S",
            "%Y-%m-%d_%H-%M-%S",
            "%Y%m%d",
            "%Y-%m-%d"
        ])
        grid.addWidget(self.date_format, 2, 1)
        
        self.rename_params_layout.addLayout(grid)
    
    def create_replace_rename_ui(self):
        grid = QGridLayout()
        
        grid.addWidget(QLabel("查找文本:"), 0, 0)
        self.replace_old = QLineEdit()
        grid.addWidget(self.replace_old, 0, 1)
        
        grid.addWidget(QLabel("替换为:"), 1, 0)
        self.replace_new = QLineEdit()
        grid.addWidget(self.replace_new, 1, 1)
        
        self.use_regex = QCheckBox("使用正则表达式")
        grid.addWidget(self.use_regex, 2, 0, 1, 2)
        
        self.rename_params_layout.addLayout(grid)
    
    def create_case_rename_ui(self):
        self.case_type = QComboBox()
        self.case_type.addItems(["小写", "大写", "首字母大写"])
        
        layout = QHBoxLayout()
        layout.addWidget(QLabel("转换类型:"))
        layout.addWidget(self.case_type)
        layout.addStretch()
        
        self.rename_params_layout.addLayout(layout)
    
    # 事件处理方法
    def select_rename_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            self.rename_dir_input.setText(directory)
    
    def select_monitor_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择监控目录")
        if directory:
            self.monitor_dir_input.setText(directory)
    
    def select_analysis_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择分析目录")
        if directory:
            self.analysis_dir_input.setText(directory)
    
    def add_merge_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        for file in files:
            self.merge_files_list.addItem(file)
    
    def remove_merge_files(self):
        current_row = self.merge_files_list.currentRow()
        if current_row >= 0:
            self.merge_files_list.takeItem(current_row)
    
    def select_merge_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存合并文件", "", "Excel文件 (*.xlsx)"
        )
        if file_path:
            self.merge_output_input.setText(file_path)
    
    def on_split_mode_changed(self, mode):
        if mode == "按列值拆分":
            self.split_column.setEnabled(True)
            self.rows_per_file.setEnabled(False)
        else:
            self.split_column.setEnabled(False)
            self.rows_per_file.setEnabled(True)
    
    def select_split_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.split_file_input.setText(file_path)
    
    def select_split_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.split_output_dir.setText(directory)
    
    def select_convert_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择输入文件", "", "所有文件 (*)"
        )
        if file_path:
            self.convert_input_file.setText(file_path)
    
    def select_convert_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存输出文件", "", "所有文件 (*)"
        )
        if file_path:
            self.convert_output_file.setText(file_path)
    
    def select_clean_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.clean_input_file.setText(file_path)
    
    def select_clean_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存清理文件", "", "Excel文件 (*.xlsx)"
        )
        if file_path:
            self.clean_output_file.setText(file_path)
    
    def execute_excel_operation(self):
        operation = self.excel_operation.currentText()
        
        try:
            if operation == "合并Excel文件":
                self.execute_merge_excel()
            elif operation == "拆分Excel文件":
                self.execute_split_excel()
            elif operation == "格式转换":
                self.execute_convert_format()
            elif operation == "数据清理":
                self.execute_clean_excel()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def execute_merge_excel(self):
        files = [self.merge_files_list.item(i).text() 
                for i in range(self.merge_files_list.count())]
        output_path = self.merge_output_input.text()
        merge_type = "sheets" if self.merge_type.currentText() == "合并为不同工作表" else "rows"
        
        if not files:
            QMessageBox.warning(self, "警告", "请添加要合并的文件")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择输出文件")
            return
        
        self.excel_progress.setVisible(True)
        self.excel_progress.setRange(0, 0)
        
        self.office_worker = OfficeWorker(
            "merge_excel",
            file_paths=files,
            output_path=output_path,
            merge_type=merge_type
        )
        self.office_worker.finished.connect(self.on_office_finished)
        self.office_worker.error.connect(self.on_office_error)
        self.office_worker.start()
    
    def execute_split_excel(self):
        file_path = self.split_file_input.text()
        output_dir = self.split_output_dir.text()
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", "请选择有效的Excel文件")
            return
        
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        split_column = None
        rows_per_file = 1000
        
        if self.split_mode.currentText() == "按列值拆分":
            split_column = self.split_column.text()
            if not split_column:
                QMessageBox.warning(self, "警告", "请输入拆分列名")
                return
        else:
            rows_per_file = self.rows_per_file.value()
        
        self.excel_progress.setVisible(True)
        self.excel_progress.setRange(0, 0)
        
        self.office_worker = OfficeWorker(
            "split_excel",
            file_path=file_path,
            output_dir=output_dir,
            split_column=split_column,
            rows_per_file=rows_per_file
        )
        self.office_worker.finished.connect(self.on_office_finished)
        self.office_worker.error.connect(self.on_office_error)
        self.office_worker.start()
    
    def execute_convert_format(self):
        input_file = self.convert_input_file.text()
        output_file = self.convert_output_file.text()
        convert_type_map = {
            "Excel转CSV": "excel_to_csv",
            "CSV转Excel": "csv_to_excel",
            "Excel转JSON": "excel_to_json",
            "JSON转Excel": "json_to_excel"
        }
        format_type = convert_type_map[self.convert_type.currentText()]
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请选择有效的输入文件")
            return
        
        if not output_file:
            QMessageBox.warning(self, "警告", "请选择输出文件")
            return
        
        self.excel_progress.setVisible(True)
        self.excel_progress.setRange(0, 0)
        
        self.office_worker = OfficeWorker(
            "convert_format",
            input_file=input_file,
            output_file=output_file,
            format_type=format_type
        )
        self.office_worker.finished.connect(self.on_office_finished)
        self.office_worker.error.connect(self.on_office_error)
        self.office_worker.start()
    
    def execute_clean_excel(self):
        input_file = self.clean_input_file.text()
        output_file = self.clean_output_file.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请选择有效的Excel文件")
            return
        
        if not output_file:
            QMessageBox.warning(self, "警告", "请选择输出文件")
            return
        
        operations = []
        if self.remove_duplicates.isChecked():
            operations.append("remove_duplicates")
        if self.remove_empty_rows.isChecked():
            operations.append("remove_empty_rows")
        if self.remove_empty_columns.isChecked():
            operations.append("remove_empty_columns")
        if self.trim_whitespace.isChecked():
            operations.append("trim_whitespace")
        if self.standardize_case.isChecked():
            operations.append("standardize_case")
        
        if not operations:
            QMessageBox.warning(self, "警告", "请至少选择一项清理操作")
            return
        
        self.excel_progress.setVisible(True)
        self.excel_progress.setRange(0, 0)
        
        self.office_worker = OfficeWorker(
            "clean_excel",
            input_file=input_file,
            output_file=output_file,
            operations=operations
        )
        self.office_worker.finished.connect(self.on_office_finished)
        self.office_worker.error.connect(self.on_office_error)
        self.office_worker.start()
    
    def preview_rename(self):
        directory = self.rename_dir_input.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self, "警告", "请选择有效的目录")
            return
        
        pattern_data = self.get_rename_pattern_data()
        if not pattern_data:
            return
        
        try:
            # 模拟重命名以获得预览
            files = [f for f in os.listdir(directory) 
                    if os.path.isfile(os.path.join(directory, f))]
            
            self.rename_preview.setRowCount(len(files))
            
            for i, filename in enumerate(files):
                old_name = filename
                # 这里应该调用重命名逻辑获取新名称
                # 为简化，直接显示原名称
                new_name = f"预览_{old_name}"  # 实际应该根据模式生成
                
                self.rename_preview.setItem(i, 0, QTableWidgetItem(old_name))
                self.rename_preview.setItem(i, 1, QTableWidgetItem(new_name))
                
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def execute_rename(self):
        directory = self.rename_dir_input.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self, "警告", "请选择有效的目录")
            return
        
        pattern_data = self.get_rename_pattern_data()
        if not pattern_data:
            return
        
        mode_map = {
            "序号重命名": "sequence",
            "时间重命名": "date",
            "替换重命名": "replace",
            "大小写转换": "case"
        }
        pattern_type = mode_map[self.rename_mode.currentText()]
        
        self.office_worker = OfficeWorker(
            "batch_rename",
            directory=directory,
            pattern_type=pattern_type,
            pattern_data=pattern_data
        )
        self.office_worker.finished.connect(self.on_office_finished)
        self.office_worker.error.connect(self.on_office_error)
        self.office_worker.start()
    
    def get_rename_pattern_data(self):
        mode = self.rename_mode.currentText()
        
        if mode == "序号重命名":
            return {
                'prefix': self.seq_prefix.text(),
                'start_num': self.seq_start.value(),
                'digits': self.seq_digits.value()
            }
        elif mode == "时间重命名":
            return {
                'prefix': self.date_prefix.text(),
                'suffix': self.date_suffix.text(),
                'date_format': self.date_format.currentText()
            }
        elif mode == "替换重命名":
            if not self.replace_old.text():
                QMessageBox.warning(self, "警告", "请输入查找文本")
                return None
            return {
                'old_text': self.replace_old.text(),
                'new_text': self.replace_new.text(),
                'use_regex': self.use_regex.isChecked()
            }
        elif mode == "大小写转换":
            case_map = {"小写": "lower", "大写": "upper", "首字母大写": "title"}
            return {
                'case_type': case_map[self.case_type.currentText()]
            }
        
        return {}
    
    def start_monitor(self):
        directory = self.monitor_dir_input.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self, "警告", "请选择有效的目录")
            return
        
        try:
            include_subdirs = self.include_subdirs.isChecked()
            self.file_observer = office_utils.monitor_directory(
                directory, self.on_file_event, include_subdirs
            )
            
            self.start_monitor_btn.setEnabled(False)
            self.stop_monitor_btn.setEnabled(True)
            self.monitor_log.append(f"开始监控目录: {directory}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def stop_monitor(self):
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            self.file_observer = None
            
            self.start_monitor_btn.setEnabled(True)
            self.stop_monitor_btn.setEnabled(False)
            self.monitor_log.append("监控已停止")
    
    def on_file_event(self, event_desc):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.monitor_log.append(f"[{timestamp}] {event_desc}")
    
    def start_clipboard_monitor(self):
        self.clipboard_history.start_monitoring(self.on_clipboard_change)
        self.start_clipboard_btn.setEnabled(False)
        self.stop_clipboard_btn.setEnabled(True)
        self.clipboard_timer.start(1000)  # 每秒更新一次显示
    
    def stop_clipboard_monitor(self):
        self.clipboard_history.stop_monitoring()
        self.start_clipboard_btn.setEnabled(True)
        self.stop_clipboard_btn.setEnabled(False)
        self.clipboard_timer.stop()
    
    def on_clipboard_change(self, content):
        # 剪贴板内容变化回调
        pass
    
    def update_clipboard_display(self):
        history = self.clipboard_history.get_history()
        self.clipboard_table.setRowCount(len(history))
        
        for i, item in enumerate(history):
            self.clipboard_table.setItem(i, 0, QTableWidgetItem(item['timestamp']))
            self.clipboard_table.setItem(i, 1, QTableWidgetItem(item['type']))
            
            # 内容预览（限制长度）
            preview = item['content'][:50] + "..." if len(item['content']) > 50 else item['content']
            preview = preview.replace('\n', ' ')
            self.clipboard_table.setItem(i, 2, QTableWidgetItem(preview))
    
    def restore_clipboard_item(self):
        current_row = self.clipboard_table.currentRow()
        if current_row >= 0:
            history = self.clipboard_history.get_history()
            if current_row < len(history):
                content = history[current_row]['content']
                import pyperclip
                pyperclip.copy(content)
                QMessageBox.information(self, "提示", "内容已复制到剪贴板")
    
    def clear_clipboard_history(self):
        self.clipboard_history.clear_history()
        self.clipboard_table.setRowCount(0)
    
    def analyze_directory(self):
        directory = self.analysis_dir_input.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self, "警告", "请选择有效的目录")
            return
        
        self.office_worker = OfficeWorker(
            "analyze_directory",
            directory=directory,
            callback=self.display_analysis_result
        )
        self.office_worker.finished.connect(self.on_office_finished)
        self.office_worker.error.connect(self.on_office_error)
        self.office_worker.start()
    
    def display_analysis_result(self, result):
        # 显示基本信息
        info_text = f"总大小: {result['total_size_mb']:.2f} MB\n"
        info_text += f"文件数量: {result['file_count']}\n"
        info_text += f"目录数量: {result['dir_count']}"
        self.basic_info.setPlainText(info_text)
        
        # 显示文件类型统计
        file_types = result['file_types']
        self.file_types_table.setRowCount(len(file_types))
        
        for i, (ext, data) in enumerate(file_types.items()):
            ext_display = ext if ext else "无扩展名"
            size_mb = data['size'] / (1024 * 1024)
            
            self.file_types_table.setItem(i, 0, QTableWidgetItem(ext_display))
            self.file_types_table.setItem(i, 1, QTableWidgetItem(str(data['count'])))
            self.file_types_table.setItem(i, 2, QTableWidgetItem(f"{size_mb:.2f}"))
        
        # 显示大文件列表
        large_files = result['large_files']
        self.large_files_table.setRowCount(len(large_files))
        
        for i, file_info in enumerate(large_files):
            self.large_files_table.setItem(i, 0, QTableWidgetItem(file_info['path']))
            self.large_files_table.setItem(i, 1, QTableWidgetItem(str(file_info['size_mb'])))
    
    def on_office_finished(self, message):
        self.excel_progress.setVisible(False)
        QMessageBox.information(self, "完成", message)
        self.operation_successful.emit()
    
    def on_office_error(self, error):
        self.excel_progress.setVisible(False)
        QMessageBox.critical(self, "错误", error)
    
    def closeEvent(self, event):
        # 清理资源
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        self.clipboard_history.stop_monitoring()
        event.accept()