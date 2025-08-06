from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget,
                             QFileDialog, QMessageBox, QProgressBar, QComboBox, 
                             QCheckBox, QSpinBox, QGroupBox, QGridLayout, QListWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from utils import resource_path
import data_utils
import os
import json
from pathlib import Path
import pandas as pd

class DataWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)
    data_ready = pyqtSignal(object)  # 传递分析结果数据
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "analyze_csv":
                result = data_utils.analyze_csv_file(
                    self.kwargs['file_path'],
                    self.kwargs.get('sample_rows', 1000)
                )
                self.data_ready.emit(result)
                self.finished.emit("CSV分析完成")
            
            elif self.operation == "clean_csv":
                result = data_utils.clean_csv_data(
                    self.kwargs['input_path'],
                    self.kwargs['output_path'],
                    self.kwargs['operations']
                )
                self.finished.emit(f"数据清理完成，从{result['original_shape']}变为{result['cleaned_shape']}")
            
            elif self.operation == "generate_report":
                result = data_utils.generate_data_report(
                    self.kwargs['file_path'],
                    self.kwargs['output_dir']
                )
                self.finished.emit(f"报告生成完成: {result['report_path']}")
            
            elif self.operation == "merge_csv":
                result = data_utils.merge_multiple_csv(
                    self.kwargs['file_paths'],
                    self.kwargs['output_path'],
                    self.kwargs['merge_type']
                )
                self.finished.emit(f"合并完成: {result['merged_rows']}行, {result['merged_columns']}列")
            
            elif self.operation == "split_csv":
                result = data_utils.split_csv_by_column(
                    self.kwargs['input_path'],
                    self.kwargs['output_dir'],
                    self.kwargs['split_column']
                )
                self.finished.emit(f"拆分完成，生成{len(result)}个文件")
            
            elif self.operation == "analyze_log":
                patterns = self.kwargs.get('patterns')
                result = data_utils.analyze_log_file(
                    self.kwargs['log_file_path'],
                    patterns
                )
                self.data_ready.emit(result)
                self.finished.emit("日志分析完成")
            
            elif self.operation == "convert_format":
                result = data_utils.convert_data_format(
                    self.kwargs['input_file'],
                    self.kwargs['output_file'],
                    self.kwargs['input_format'],
                    self.kwargs['output_format']
                )
                self.finished.emit(f"格式转换完成: {result}")
            
            elif self.operation == "create_pivot":
                result = data_utils.create_pivot_table(
                    self.kwargs['input_file'],
                    self.kwargs['output_file'],
                    self.kwargs['index_col'],
                    self.kwargs['columns_col'],
                    self.kwargs['values_col'],
                    self.kwargs.get('agg_func', 'sum')
                )
                self.finished.emit(f"透视表创建完成: {result['rows']}行, {result['columns']}列")
                
        except Exception as e:
            self.error.emit(str(e))

class DataWindow(QMainWindow):
    operation_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据分析工具")
        self.setGeometry(200, 200, 1200, 800)
        self.setWindowIcon(QIcon(resource_path("数据.png")))
        
        self.analysis_result = None
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # CSV分析选项卡
        self.csv_analysis_tab = self.create_csv_analysis_tab()
        self.tab_widget.addTab(self.csv_analysis_tab, "CSV分析")
        
        # 数据清理选项卡
        self.data_cleaning_tab = self.create_data_cleaning_tab()
        self.tab_widget.addTab(self.data_cleaning_tab, "数据清理")
        
        # 数据转换选项卡
        self.data_conversion_tab = self.create_data_conversion_tab()
        self.tab_widget.addTab(self.data_conversion_tab, "数据转换")
        
        # 日志分析选项卡
        self.log_analysis_tab = self.create_log_analysis_tab()
        self.tab_widget.addTab(self.log_analysis_tab, "日志分析")
        
        # 数据透视选项卡
        self.pivot_tab = self.create_pivot_tab()
        self.tab_widget.addTab(self.pivot_tab, "数据透视")
        
    def create_csv_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件选择
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout(file_group)
        
        self.csv_file_input = QLineEdit()
        self.csv_file_input.setPlaceholderText("选择CSV文件...")
        self.select_csv_btn = QPushButton("选择文件")
        self.select_csv_btn.clicked.connect(self.select_csv_file)
        
        file_layout.addWidget(self.csv_file_input)
        file_layout.addWidget(self.select_csv_btn)
        layout.addWidget(file_group)
        
        # 分析设置
        settings_group = QGroupBox("分析设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("样本行数:"), 0, 0)
        self.sample_rows = QSpinBox()
        self.sample_rows.setRange(100, 100000)
        self.sample_rows.setValue(1000)
        settings_layout.addWidget(self.sample_rows, 0, 1)
        
        self.analyze_csv_btn = QPushButton("开始分析")
        self.analyze_csv_btn.clicked.connect(self.analyze_csv)
        settings_layout.addWidget(self.analyze_csv_btn, 0, 2)
        
        self.generate_report_btn = QPushButton("生成报告")
        self.generate_report_btn.clicked.connect(self.generate_report)
        self.generate_report_btn.setEnabled(False)
        settings_layout.addWidget(self.generate_report_btn, 0, 3)
        
        layout.addWidget(settings_group)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 分析结果显示
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        self.basic_info_text = QTextEdit()
        self.basic_info_text.setMaximumHeight(150)
        self.basic_info_text.setReadOnly(True)
        basic_layout.addWidget(self.basic_info_text)
        left_layout.addWidget(basic_group)
        
        # 数据质量
        quality_group = QGroupBox("数据质量")
        quality_layout = QVBoxLayout(quality_group)
        self.quality_info_text = QTextEdit()
        self.quality_info_text.setMaximumHeight(150)
        self.quality_info_text.setReadOnly(True)
        quality_layout.addWidget(self.quality_info_text)
        left_layout.addWidget(quality_group)
        
        splitter.addWidget(left_widget)
        
        # 列信息表格
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        columns_group = QGroupBox("列信息")
        columns_layout = QVBoxLayout(columns_group)
        
        self.columns_table = QTableWidget()
        self.columns_table.setColumnCount(7)
        self.columns_table.setHorizontalHeaderLabels([
            "列名", "数据类型", "非空值", "空值", "缺失率", "唯一值", "内存使用"
        ])
        self.columns_table.horizontalHeader().setStretchLastSection(True)
        columns_layout.addWidget(self.columns_table)
        
        right_layout.addWidget(columns_group)
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        # 进度条
        self.csv_progress = QProgressBar()
        self.csv_progress.setVisible(False)
        layout.addWidget(self.csv_progress)
        
        return widget
    
    def create_data_cleaning_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入文件
        input_group = QGroupBox("输入文件")
        input_layout = QHBoxLayout(input_group)
        
        self.clean_input_file = QLineEdit()
        self.clean_input_file.setPlaceholderText("选择要清理的CSV文件...")
        self.select_clean_input_btn = QPushButton("选择文件")
        self.select_clean_input_btn.clicked.connect(self.select_clean_input)
        
        input_layout.addWidget(self.clean_input_file)
        input_layout.addWidget(self.select_clean_input_btn)
        layout.addWidget(input_group)
        
        # 清理选项
        options_group = QGroupBox("清理选项")
        options_layout = QVBoxLayout(options_group)
        
        self.remove_duplicates = QCheckBox("删除重复行")
        self.remove_empty_rows = QCheckBox("删除空行")
        self.remove_empty_columns = QCheckBox("删除空列")
        self.fill_missing_mean = QCheckBox("用均值填充数值缺失值")
        self.fill_missing_mode = QCheckBox("用众数填充文本缺失值")
        self.standardize_text = QCheckBox("标准化文本格式")
        self.convert_dates = QCheckBox("转换日期格式")
        
        options_layout.addWidget(self.remove_duplicates)
        options_layout.addWidget(self.remove_empty_rows)
        options_layout.addWidget(self.remove_empty_columns)
        options_layout.addWidget(self.fill_missing_mean)
        options_layout.addWidget(self.fill_missing_mode)
        options_layout.addWidget(self.standardize_text)
        options_layout.addWidget(self.convert_dates)
        
        layout.addWidget(options_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.clean_output_file = QLineEdit()
        self.clean_output_file.setPlaceholderText("选择输出文件...")
        self.select_clean_output_btn = QPushButton("选择输出")
        self.select_clean_output_btn.clicked.connect(self.select_clean_output)
        
        output_layout.addWidget(self.clean_output_file)
        output_layout.addWidget(self.select_clean_output_btn)
        layout.addLayout(output_layout)
        
        # 执行按钮
        self.clean_data_btn = QPushButton("开始清理")
        self.clean_data_btn.clicked.connect(self.clean_data)
        layout.addWidget(self.clean_data_btn)
        
        layout.addStretch()
        return widget
    
    def create_data_conversion_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 操作选择
        operation_group = QGroupBox("操作选择")
        operation_layout = QHBoxLayout(operation_group)
        
        self.conversion_operation = QComboBox()
        self.conversion_operation.addItems(["合并CSV文件", "拆分CSV文件", "格式转换"])
        self.conversion_operation.currentTextChanged.connect(self.on_conversion_operation_changed)
        
        operation_layout.addWidget(QLabel("操作类型:"))
        operation_layout.addWidget(self.conversion_operation)
        operation_layout.addStretch()
        
        layout.addWidget(operation_group)
        
        # 动态参数区域
        self.conversion_params_widget = QWidget()
        self.conversion_params_layout = QVBoxLayout(self.conversion_params_widget)
        layout.addWidget(self.conversion_params_widget)
        
        # 执行按钮
        btn_layout = QHBoxLayout()
        self.execute_conversion_btn = QPushButton("执行操作")
        self.execute_conversion_btn.clicked.connect(self.execute_conversion)
        btn_layout.addWidget(self.execute_conversion_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 进度条
        self.conversion_progress = QProgressBar()
        self.conversion_progress.setVisible(False)
        layout.addWidget(self.conversion_progress)
        
        layout.addStretch()
        
        # 初始化界面
        self.on_conversion_operation_changed("合并CSV文件")
        return widget
    
    def create_log_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日志文件选择
        file_layout = QHBoxLayout()
        self.log_file_input = QLineEdit()
        self.log_file_input.setPlaceholderText("选择日志文件...")
        self.select_log_btn = QPushButton("选择文件")
        self.select_log_btn.clicked.connect(self.select_log_file)
        
        file_layout.addWidget(self.log_file_input)
        file_layout.addWidget(self.select_log_btn)
        layout.addLayout(file_layout)
        
        # 分析模式
        patterns_group = QGroupBox("分析模式")
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.use_default_patterns = QCheckBox("使用默认模式 (ERROR, WARNING, INFO, IP, TIMESTAMP)")
        self.use_default_patterns.setChecked(True)
        self.use_default_patterns.toggled.connect(self.toggle_custom_patterns)
        patterns_layout.addWidget(self.use_default_patterns)
        
        # 自定义模式（默认隐藏）
        self.custom_patterns_widget = QWidget()
        custom_layout = QVBoxLayout(self.custom_patterns_widget)
        
        custom_layout.addWidget(QLabel("自定义正则表达式模式 (格式: 名称:模式，每行一个):"))
        self.custom_patterns_text = QTextEdit()
        self.custom_patterns_text.setPlaceholderText("例如:\nERROR:ERROR|Error|error\nWARN:WARNING|Warning|warning")
        self.custom_patterns_text.setMaximumHeight(100)
        custom_layout.addWidget(self.custom_patterns_text)
        
        self.custom_patterns_widget.setVisible(False)
        patterns_layout.addWidget(self.custom_patterns_widget)
        
        layout.addWidget(patterns_group)
        
        # 分析按钮
        self.analyze_log_btn = QPushButton("分析日志")
        self.analyze_log_btn.clicked.connect(self.analyze_log)
        layout.addWidget(self.analyze_log_btn)
        
        # 分析结果显示
        result_group = QGroupBox("分析结果")
        result_layout = QVBoxLayout(result_group)
        
        # 基本统计
        self.log_basic_info = QTextEdit()
        self.log_basic_info.setMaximumHeight(120)
        self.log_basic_info.setReadOnly(True)
        result_layout.addWidget(self.log_basic_info)
        
        # 模式匹配统计表格
        self.log_patterns_table = QTableWidget()
        self.log_patterns_table.setColumnCount(3)
        self.log_patterns_table.setHorizontalHeaderLabels(["模式", "匹配次数", "示例"])
        self.log_patterns_table.horizontalHeader().setStretchLastSection(True)
        result_layout.addWidget(self.log_patterns_table)
        
        layout.addWidget(result_group)
        
        return widget
    
    def create_pivot_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入文件
        file_layout = QHBoxLayout()
        self.pivot_input_file = QLineEdit()
        self.pivot_input_file.setPlaceholderText("选择CSV文件...")
        self.select_pivot_input_btn = QPushButton("选择文件")
        self.select_pivot_input_btn.clicked.connect(self.select_pivot_input)
        
        file_layout.addWidget(self.pivot_input_file)
        file_layout.addWidget(self.select_pivot_input_btn)
        layout.addLayout(file_layout)
        
        # 透视表设置
        settings_group = QGroupBox("透视表设置")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("行索引列:"), 0, 0)
        self.pivot_index_col = QLineEdit()
        self.pivot_index_col.setPlaceholderText("输入作为行索引的列名...")
        settings_layout.addWidget(self.pivot_index_col, 0, 1)
        
        settings_layout.addWidget(QLabel("列索引列:"), 1, 0)
        self.pivot_columns_col = QLineEdit()
        self.pivot_columns_col.setPlaceholderText("输入作为列索引的列名...")
        settings_layout.addWidget(self.pivot_columns_col, 1, 1)
        
        settings_layout.addWidget(QLabel("数值列:"), 2, 0)
        self.pivot_values_col = QLineEdit()
        self.pivot_values_col.setPlaceholderText("输入包含数值的列名...")
        settings_layout.addWidget(self.pivot_values_col, 2, 1)
        
        settings_layout.addWidget(QLabel("聚合函数:"), 3, 0)
        self.pivot_agg_func = QComboBox()
        self.pivot_agg_func.addItems(["sum", "mean", "count", "min", "max", "std"])
        settings_layout.addWidget(self.pivot_agg_func, 3, 1)
        
        layout.addWidget(settings_group)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.pivot_output_file = QLineEdit()
        self.pivot_output_file.setPlaceholderText("选择输出文件...")
        self.select_pivot_output_btn = QPushButton("选择输出")
        self.select_pivot_output_btn.clicked.connect(self.select_pivot_output)
        
        output_layout.addWidget(self.pivot_output_file)
        output_layout.addWidget(self.select_pivot_output_btn)
        layout.addLayout(output_layout)
        
        # 创建按钮
        self.create_pivot_btn = QPushButton("创建透视表")
        self.create_pivot_btn.clicked.connect(self.create_pivot_table)
        layout.addWidget(self.create_pivot_btn)
        
        layout.addStretch()
        return widget
    
    def on_conversion_operation_changed(self, operation):
        # 清空现有控件
        for i in reversed(range(self.conversion_params_layout.count())):
            self.conversion_params_layout.itemAt(i).widget().setParent(None)
        
        if operation == "合并CSV文件":
            self.create_merge_csv_ui()
        elif operation == "拆分CSV文件":
            self.create_split_csv_ui()
        elif operation == "格式转换":
            self.create_format_conversion_ui()
    
    def create_merge_csv_ui(self):
        # 文件列表
        files_group = QGroupBox("选择要合并的文件")
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
        
        self.conversion_params_layout.addWidget(files_group)
        
        # 合并选项
        options_layout = QHBoxLayout()
        self.merge_type = QComboBox()
        self.merge_type.addItems(["垂直合并(堆叠)", "水平合并(并排)"])
        
        options_layout.addWidget(QLabel("合并方式:"))
        options_layout.addWidget(self.merge_type)
        options_layout.addStretch()
        self.conversion_params_layout.addLayout(options_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.merge_output_file = QLineEdit()
        self.merge_output_file.setPlaceholderText("选择输出文件...")
        select_output_btn = QPushButton("选择输出")
        select_output_btn.clicked.connect(self.select_merge_output)
        
        output_layout.addWidget(self.merge_output_file)
        output_layout.addWidget(select_output_btn)
        self.conversion_params_layout.addLayout(output_layout)
    
    def create_split_csv_ui(self):
        # 输入文件
        input_layout = QHBoxLayout()
        self.split_input_file = QLineEdit()
        self.split_input_file.setPlaceholderText("选择要拆分的CSV文件...")
        select_input_btn = QPushButton("选择文件")
        select_input_btn.clicked.connect(self.select_split_input)
        
        input_layout.addWidget(self.split_input_file)
        input_layout.addWidget(select_input_btn)
        self.conversion_params_layout.addLayout(input_layout)
        
        # 拆分列
        col_layout = QHBoxLayout()
        self.split_column = QLineEdit()
        self.split_column.setPlaceholderText("输入拆分依据的列名...")
        
        col_layout.addWidget(QLabel("拆分列:"))
        col_layout.addWidget(self.split_column)
        col_layout.addStretch()
        self.conversion_params_layout.addLayout(col_layout)
        
        # 输出目录
        output_layout = QHBoxLayout()
        self.split_output_dir = QLineEdit()
        self.split_output_dir.setPlaceholderText("选择输出目录...")
        select_dir_btn = QPushButton("选择目录")
        select_dir_btn.clicked.connect(self.select_split_output_dir)
        
        output_layout.addWidget(self.split_output_dir)
        output_layout.addWidget(select_dir_btn)
        self.conversion_params_layout.addLayout(output_layout)
    
    def create_format_conversion_ui(self):
        # 输入文件
        input_layout = QHBoxLayout()
        self.format_input_file = QLineEdit()
        self.format_input_file.setPlaceholderText("选择输入文件...")
        select_input_btn = QPushButton("选择文件")
        select_input_btn.clicked.connect(self.select_format_input)
        
        input_layout.addWidget(self.format_input_file)
        input_layout.addWidget(select_input_btn)
        self.conversion_params_layout.addLayout(input_layout)
        
        # 格式选择
        format_layout = QGridLayout()
        
        format_layout.addWidget(QLabel("输入格式:"), 0, 0)
        self.input_format = QComboBox()
        self.input_format.addItems(["CSV", "Excel", "JSON"])
        format_layout.addWidget(self.input_format, 0, 1)
        
        format_layout.addWidget(QLabel("输出格式:"), 0, 2)
        self.output_format = QComboBox()
        self.output_format.addItems(["CSV", "Excel", "JSON", "HTML"])
        format_layout.addWidget(self.output_format, 0, 3)
        
        self.conversion_params_layout.addLayout(format_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        self.format_output_file = QLineEdit()
        self.format_output_file.setPlaceholderText("选择输出文件...")
        select_output_btn = QPushButton("选择输出")
        select_output_btn.clicked.connect(self.select_format_output)
        
        output_layout.addWidget(self.format_output_file)
        output_layout.addWidget(select_output_btn)
        self.conversion_params_layout.addLayout(output_layout)
    
    # 事件处理方法
    def select_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv)"
        )
        if file_path:
            self.csv_file_input.setText(file_path)
    
    def analyze_csv(self):
        file_path = self.csv_file_input.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", "请选择有效的CSV文件")
            return
        
        sample_rows = self.sample_rows.value()
        
        self.csv_progress.setVisible(True)
        self.csv_progress.setRange(0, 0)
        
        self.data_worker = DataWorker("analyze_csv", file_path=file_path, sample_rows=sample_rows)
        self.data_worker.data_ready.connect(self.display_csv_analysis)
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def display_csv_analysis(self, analysis):
        self.analysis_result = analysis
        
        # 显示基本信息
        basic_info = analysis['basic_info']
        basic_text = f"""文件信息:
• 行数: {basic_info['rows']:,}
• 列数: {basic_info['columns']}
• 文件大小: {basic_info['file_size'] / 1024 / 1024:.2f} MB
• 内存使用: {basic_info['memory_usage'] / 1024 / 1024:.2f} MB
• 编码格式: {basic_info['encoding']}"""
        
        self.basic_info_text.setPlainText(basic_text)
        
        # 显示数据质量信息
        missing_data = analysis['missing_data']
        total_missing = sum(info['ratio'] for info in missing_data.values())
        avg_missing = total_missing / len(missing_data) if missing_data else 0
        
        high_missing_cols = [col for col, info in missing_data.items() if info['ratio'] > 50]
        numeric_cols = [col for col, dtype in analysis['data_types'].items() if dtype == 'numeric']
        
        quality_text = f"""数据质量:
• 平均缺失率: {avg_missing:.1f}%
• 高缺失率列数 (>50%): {len(high_missing_cols)}
• 数值列数: {len(numeric_cols)}
• 文本列数: {len([col for col, dtype in analysis['data_types'].items() if dtype == 'text'])}
• 日期列数: {len([col for col, dtype in analysis['data_types'].items() if dtype == 'datetime'])}"""
        
        self.quality_info_text.setPlainText(quality_text)
        
        # 填充列信息表格
        columns_info = analysis['columns_info']
        self.columns_table.setRowCount(len(columns_info))
        
        for row, (col_name, info) in enumerate(columns_info.items()):
            missing_ratio = missing_data.get(col_name, {}).get('ratio', 0)
            
            self.columns_table.setItem(row, 0, QTableWidgetItem(col_name))
            self.columns_table.setItem(row, 1, QTableWidgetItem(info['dtype']))
            self.columns_table.setItem(row, 2, QTableWidgetItem(f"{info['non_null_count']:,}"))
            self.columns_table.setItem(row, 3, QTableWidgetItem(f"{info['null_count']:,}"))
            self.columns_table.setItem(row, 4, QTableWidgetItem(f"{missing_ratio:.1f}%"))
            self.columns_table.setItem(row, 5, QTableWidgetItem(f"{info['unique_count']:,}"))
            self.columns_table.setItem(row, 6, QTableWidgetItem(f"{info['memory_usage'] / 1024:.1f} KB"))
        
        self.columns_table.resizeColumnsToContents()
        
        # 启用报告生成按钮
        self.generate_report_btn.setEnabled(True)
    
    def generate_report(self):
        if not self.analysis_result:
            QMessageBox.warning(self, "警告", "请先进行CSV分析")
            return
        
        file_path = self.csv_file_input.text()
        output_dir = QFileDialog.getExistingDirectory(self, "选择报告输出目录")
        
        if not output_dir:
            return
        
        self.csv_progress.setVisible(True)
        self.csv_progress.setRange(0, 0)
        
        self.data_worker = DataWorker("generate_report", file_path=file_path, output_dir=output_dir)
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def select_clean_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv)"
        )
        if file_path:
            self.clean_input_file.setText(file_path)
    
    def select_clean_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存清理后的文件", "", "CSV文件 (*.csv)"
        )
        if file_path:
            self.clean_output_file.setText(file_path)
    
    def clean_data(self):
        input_file = self.clean_input_file.text()
        output_file = self.clean_output_file.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请选择有效的输入文件")
            return
        
        if not output_file:
            QMessageBox.warning(self, "警告", "请选择输出文件")
            return
        
        operations = []
        if self.remove_duplicates.isChecked():
            operations.append('remove_duplicates')
        if self.remove_empty_rows.isChecked():
            operations.append('remove_empty_rows')
        if self.remove_empty_columns.isChecked():
            operations.append('remove_empty_columns')
        if self.fill_missing_mean.isChecked():
            operations.append('fill_missing_mean')
        if self.fill_missing_mode.isChecked():
            operations.append('fill_missing_mode')
        if self.standardize_text.isChecked():
            operations.append('standardize_text')
        if self.convert_dates.isChecked():
            operations.append('convert_dates')
        
        if not operations:
            QMessageBox.warning(self, "警告", "请至少选择一项清理操作")
            return
        
        self.data_worker = DataWorker(
            "clean_csv",
            input_path=input_file,
            output_path=output_file,
            operations=operations
        )
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def execute_conversion(self):
        operation = self.conversion_operation.currentText()
        
        try:
            if operation == "合并CSV文件":
                self.execute_merge_csv()
            elif operation == "拆分CSV文件":
                self.execute_split_csv()
            elif operation == "格式转换":
                self.execute_format_conversion()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def execute_merge_csv(self):
        file_paths = [self.merge_files_list.item(i).text() 
                     for i in range(self.merge_files_list.count())]
        output_path = self.merge_output_file.text()
        merge_type = "vertical" if self.merge_type.currentText() == "垂直合并(堆叠)" else "horizontal"
        
        if not file_paths:
            QMessageBox.warning(self, "警告", "请添加要合并的文件")
            return
        
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择输出文件")
            return
        
        self.conversion_progress.setVisible(True)
        self.conversion_progress.setRange(0, 0)
        
        self.data_worker = DataWorker(
            "merge_csv",
            file_paths=file_paths,
            output_path=output_path,
            merge_type=merge_type
        )
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def execute_split_csv(self):
        input_file = self.split_input_file.text()
        output_dir = self.split_output_dir.text()
        split_column = self.split_column.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请选择有效的输入文件")
            return
        
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        if not split_column:
            QMessageBox.warning(self, "警告", "请输入拆分列名")
            return
        
        self.conversion_progress.setVisible(True)
        self.conversion_progress.setRange(0, 0)
        
        self.data_worker = DataWorker(
            "split_csv",
            input_path=input_file,
            output_dir=output_dir,
            split_column=split_column
        )
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def execute_format_conversion(self):
        input_file = self.format_input_file.text()
        output_file = self.format_output_file.text()
        input_format = self.input_format.currentText()
        output_format = self.output_format.currentText()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请选择有效的输入文件")
            return
        
        if not output_file:
            QMessageBox.warning(self, "警告", "请选择输出文件")
            return
        
        self.conversion_progress.setVisible(True)
        self.conversion_progress.setRange(0, 0)
        
        self.data_worker = DataWorker(
            "convert_format",
            input_file=input_file,
            output_file=output_file,
            input_format=input_format,
            output_format=output_format
        )
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def select_log_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择日志文件", "", "日志文件 (*.log *.txt);;所有文件 (*)"
        )
        if file_path:
            self.log_file_input.setText(file_path)
    
    def toggle_custom_patterns(self, checked):
        self.custom_patterns_widget.setVisible(not checked)
    
    def analyze_log(self):
        log_file = self.log_file_input.text()
        if not log_file or not os.path.exists(log_file):
            QMessageBox.warning(self, "警告", "请选择有效的日志文件")
            return
        
        patterns = None
        if not self.use_default_patterns.isChecked():
            # 解析自定义模式
            custom_text = self.custom_patterns_text.toPlainText().strip()
            if custom_text:
                patterns = {}
                for line in custom_text.split('\n'):
                    if ':' in line:
                        name, pattern = line.split(':', 1)
                        patterns[name.strip()] = pattern.strip()
        
        self.data_worker = DataWorker(
            "analyze_log",
            log_file_path=log_file,
            patterns=patterns
        )
        self.data_worker.data_ready.connect(self.display_log_analysis)
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    def display_log_analysis(self, analysis):
        # 显示基本信息
        basic_text = f"""日志文件信息:
• 总行数: {analysis['total_lines']:,}
• 文件大小: {analysis['file_size'] / 1024 / 1024:.2f} MB
• 时间戳数量: {analysis.get('time_range', {}).get('count', 0):,}"""
        
        if 'time_range' in analysis and analysis['time_range']['count'] > 0:
            basic_text += f"""
• 时间范围: {analysis['time_range']['first']} - {analysis['time_range']['last']}"""
        
        self.log_basic_info.setPlainText(basic_text)
        
        # 填充模式匹配表格
        pattern_counts = analysis['pattern_counts']
        line_samples = analysis['line_samples']
        
        self.log_patterns_table.setRowCount(len(pattern_counts))
        
        for row, (pattern_name, count) in enumerate(pattern_counts.items()):
            self.log_patterns_table.setItem(row, 0, QTableWidgetItem(pattern_name))
            self.log_patterns_table.setItem(row, 1, QTableWidgetItem(f"{count:,}"))
            
            # 显示示例
            samples = line_samples.get(pattern_name, [])
            if samples:
                example = samples[0]['content'][:100] + "..." if len(samples[0]['content']) > 100 else samples[0]['content']
                self.log_patterns_table.setItem(row, 2, QTableWidgetItem(example))
            else:
                self.log_patterns_table.setItem(row, 2, QTableWidgetItem("无匹配"))
        
        self.log_patterns_table.resizeColumnsToContents()
    
    def select_pivot_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv)"
        )
        if file_path:
            self.pivot_input_file.setText(file_path)
    
    def select_pivot_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存透视表", "", "CSV文件 (*.csv)"
        )
        if file_path:
            self.pivot_output_file.setText(file_path)
    
    def create_pivot_table(self):
        input_file = self.pivot_input_file.text()
        output_file = self.pivot_output_file.text()
        index_col = self.pivot_index_col.text()
        columns_col = self.pivot_columns_col.text()
        values_col = self.pivot_values_col.text()
        agg_func = self.pivot_agg_func.currentText()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请选择有效的输入文件")
            return
        
        if not output_file:
            QMessageBox.warning(self, "警告", "请选择输出文件")
            return
        
        if not all([index_col, columns_col, values_col]):
            QMessageBox.warning(self, "警告", "请填写所有列名")
            return
        
        self.data_worker = DataWorker(
            "create_pivot",
            input_file=input_file,
            output_file=output_file,
            index_col=index_col,
            columns_col=columns_col,
            values_col=values_col,
            agg_func=agg_func
        )
        self.data_worker.finished.connect(self.on_data_finished)
        self.data_worker.error.connect(self.on_data_error)
        self.data_worker.start()
    
    # 辅助方法
    def add_merge_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择CSV文件", "", "CSV文件 (*.csv)"
        )
        for file in files:
            self.merge_files_list.addItem(file)
    
    def remove_merge_files(self):
        current_row = self.merge_files_list.currentRow()
        if current_row >= 0:
            self.merge_files_list.takeItem(current_row)
    
    def select_merge_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存合并文件", "", "CSV文件 (*.csv)"
        )
        if file_path:
            self.merge_output_file.setText(file_path)
    
    def select_split_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv)"
        )
        if file_path:
            self.split_input_file.setText(file_path)
    
    def select_split_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.split_output_dir.setText(directory)
    
    def select_format_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择输入文件", "", "所有文件 (*)"
        )
        if file_path:
            self.format_input_file.setText(file_path)
    
    def select_format_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存输出文件", "", "所有文件 (*)"
        )
        if file_path:
            self.format_output_file.setText(file_path)
    
    def on_data_finished(self, message):
        self.csv_progress.setVisible(False)
        self.conversion_progress.setVisible(False)
        QMessageBox.information(self, "完成", message)
        self.operation_successful.emit()
    
    def on_data_error(self, error):
        self.csv_progress.setVisible(False)
        self.conversion_progress.setVisible(False)
        QMessageBox.critical(self, "错误", error)