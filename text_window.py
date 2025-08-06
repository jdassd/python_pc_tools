from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTextEdit, 
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QFileDialog, QMessageBox, QCheckBox, QTabWidget, 
                             QGridLayout, QSpinBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QScrollArea)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import pyqtSignal, QThread, pyqtSlot
from utils import resource_path
import text_utils
import os

class TextProcessingWorker(QThread):
    finished = pyqtSignal(object, str)
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        
    def run(self):
        try:
            if self.operation == "process_file":
                result, error = text_utils.process_text_file(**self.kwargs)
            elif self.operation == "merge_files":
                result, error = text_utils.merge_text_files(**self.kwargs)
            else:
                result, error = None, "未知操作"
                
            self.finished.emit(result, error or "")
        except Exception as e:
            self.finished.emit(None, str(e))

class TextWindow(QWidget):
    operation_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("文本处理工具")
        self.setGeometry(200, 200, 900, 700)
        self.setWindowIcon(QIcon(resource_path("文本.png")))
        
        self.current_files = []
        self.worker = None
        
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 编码转换标签页
        self.setup_encoding_tab()
        
        # 查找替换标签页
        self.setup_find_replace_tab()
        
        # 文本分割合并标签页
        self.setup_split_merge_tab()
        
        # 文本分析标签页
        self.setup_analysis_tab()

    def setup_encoding_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout(file_group)
        
        self.encoding_file_label = QLabel("未选择文件")
        select_file_btn = QPushButton("选择文件")
        select_file_btn.clicked.connect(self.select_encoding_file)
        
        file_layout.addWidget(QLabel("文件:"))
        file_layout.addWidget(self.encoding_file_label, 1)
        file_layout.addWidget(select_file_btn)
        layout.addWidget(file_group)
        
        # 编码设置组
        encoding_group = QGroupBox("编码转换设置")
        encoding_layout = QGridLayout(encoding_group)
        
        self.source_encoding = QComboBox()
        self.source_encoding.addItems(["自动检测", "UTF-8", "GBK", "GB2312", "ASCII", "UTF-16"])
        self.target_encoding = QComboBox()
        self.target_encoding.addItems(["UTF-8", "GBK", "GB2312", "ASCII", "UTF-16"])
        
        encoding_layout.addWidget(QLabel("源编码:"), 0, 0)
        encoding_layout.addWidget(self.source_encoding, 0, 1)
        encoding_layout.addWidget(QLabel("目标编码:"), 1, 0)
        encoding_layout.addWidget(self.target_encoding, 1, 1)
        
        layout.addWidget(encoding_group)
        
        # 转换按钮
        convert_btn = QPushButton("开始转换")
        convert_btn.clicked.connect(self.convert_encoding)
        layout.addWidget(convert_btn)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "编码转换")

    def setup_find_replace_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout(file_group)
        
        self.replace_file_label = QLabel("未选择文件")
        select_file_btn = QPushButton("选择文件")
        select_file_btn.clicked.connect(self.select_replace_file)
        
        file_layout.addWidget(QLabel("文件:"))
        file_layout.addWidget(self.replace_file_label, 1)
        file_layout.addWidget(select_file_btn)
        layout.addWidget(file_group)
        
        # 替换规则组
        rules_group = QGroupBox("替换规则")
        rules_layout = QVBoxLayout(rules_group)
        
        # 替换选项
        options_layout = QHBoxLayout()
        self.use_regex = QCheckBox("使用正则表达式")
        self.case_sensitive = QCheckBox("区分大小写")
        self.case_sensitive.setChecked(True)
        
        options_layout.addWidget(self.use_regex)
        options_layout.addWidget(self.case_sensitive)
        options_layout.addStretch()
        rules_layout.addLayout(options_layout)
        
        # 替换规则表格
        self.replace_table = QTableWidget(1, 2)
        self.replace_table.setHorizontalHeaderLabels(["查找", "替换"])
        self.replace_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        rules_layout.addWidget(self.replace_table)
        
        # 表格操作按钮
        table_btn_layout = QHBoxLayout()
        add_rule_btn = QPushButton("添加规则")
        remove_rule_btn = QPushButton("删除规则")
        add_rule_btn.clicked.connect(self.add_replace_rule)
        remove_rule_btn.clicked.connect(self.remove_replace_rule)
        
        table_btn_layout.addWidget(add_rule_btn)
        table_btn_layout.addWidget(remove_rule_btn)
        table_btn_layout.addStretch()
        rules_layout.addLayout(table_btn_layout)
        
        layout.addWidget(rules_group)
        
        # 执行按钮
        execute_btn = QPushButton("执行替换")
        execute_btn.clicked.connect(self.execute_find_replace)
        layout.addWidget(execute_btn)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "查找替换")

    def setup_split_merge_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文本分割组
        split_group = QGroupBox("文本分割")
        split_layout = QGridLayout(split_group)
        
        self.split_file_label = QLabel("未选择文件")
        select_split_file_btn = QPushButton("选择文件")
        select_split_file_btn.clicked.connect(self.select_split_file)
        
        split_layout.addWidget(QLabel("文件:"), 0, 0)
        split_layout.addWidget(self.split_file_label, 0, 1)
        split_layout.addWidget(select_split_file_btn, 0, 2)
        
        self.split_method = QComboBox()
        self.split_method.addItems(["按行数分割", "按字符数分割", "按分隔符分割"])
        self.split_method.currentTextChanged.connect(self.on_split_method_changed)
        
        split_layout.addWidget(QLabel("分割方式:"), 1, 0)
        split_layout.addWidget(self.split_method, 1, 1)
        
        self.split_value_input = QLineEdit()
        self.split_value_input.setPlaceholderText("请输入分割值")
        split_layout.addWidget(QLabel("分割值:"), 2, 0)
        split_layout.addWidget(self.split_value_input, 2, 1)
        
        split_btn = QPushButton("开始分割")
        split_btn.clicked.connect(self.split_text_file)
        split_layout.addWidget(split_btn, 3, 0, 1, 3)
        
        layout.addWidget(split_group)
        
        # 文本合并组
        merge_group = QGroupBox("文本合并")
        merge_layout = QVBoxLayout(merge_group)
        
        # 文件列表
        files_layout = QHBoxLayout()
        self.merge_files_list = QTextEdit()
        self.merge_files_list.setMaximumHeight(100)
        self.merge_files_list.setPlaceholderText("已选择的文件将在这里显示...")
        
        select_merge_files_btn = QPushButton("选择文件")
        select_merge_files_btn.clicked.connect(self.select_merge_files)
        
        files_layout.addWidget(self.merge_files_list, 1)
        files_layout.addWidget(select_merge_files_btn)
        merge_layout.addLayout(files_layout)
        
        # 分隔符设置
        separator_layout = QHBoxLayout()
        self.separator_input = QLineEdit()
        self.separator_input.setText("\\n")
        self.separator_input.setPlaceholderText("文件间分隔符")
        
        separator_layout.addWidget(QLabel("分隔符:"))
        separator_layout.addWidget(self.separator_input)
        merge_layout.addLayout(separator_layout)
        
        # 合并按钮
        merge_btn = QPushButton("开始合并")
        merge_btn.clicked.connect(self.merge_text_files)
        merge_layout.addWidget(merge_btn)
        
        layout.addWidget(merge_group)
        layout.addStretch()
        self.tab_widget.addTab(tab, "分割合并")

    def setup_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout(file_group)
        
        self.analysis_file_label = QLabel("未选择文件")
        select_file_btn = QPushButton("选择文件")
        select_file_btn.clicked.connect(self.select_analysis_file)
        
        file_layout.addWidget(QLabel("文件:"))
        file_layout.addWidget(self.analysis_file_label, 1)
        file_layout.addWidget(select_file_btn)
        layout.addWidget(file_group)
        
        # 分析按钮
        analyze_btn = QPushButton("开始分析")
        analyze_btn.clicked.connect(self.analyze_text_file)
        layout.addWidget(analyze_btn)
        
        # 分析结果显示
        self.analysis_result = QTextEdit()
        self.analysis_result.setReadOnly(True)
        layout.addWidget(self.analysis_result)
        
        self.tab_widget.addTab(tab, "文本分析")

    def select_encoding_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文本文件", "", 
            "文本文件 (*.txt *.log *.csv *.py *.js *.html *.xml);;所有文件 (*)"
        )
        if file_path:
            self.encoding_file_path = file_path
            self.encoding_file_label.setText(os.path.basename(file_path))

    def select_replace_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文本文件", "", 
            "文本文件 (*.txt *.log *.csv *.py *.js *.html *.xml);;所有文件 (*)"
        )
        if file_path:
            self.replace_file_path = file_path
            self.replace_file_label.setText(os.path.basename(file_path))

    def select_split_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文本文件", "", 
            "文本文件 (*.txt *.log *.csv);;所有文件 (*)"
        )
        if file_path:
            self.split_file_path = file_path
            self.split_file_label.setText(os.path.basename(file_path))

    def select_merge_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择要合并的文本文件", "", 
            "文本文件 (*.txt *.log *.csv);;所有文件 (*)"
        )
        if file_paths:
            self.merge_file_paths = file_paths
            file_names = [os.path.basename(f) for f in file_paths]
            self.merge_files_list.setText('\n'.join(file_names))

    def select_analysis_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文本文件", "", 
            "文本文件 (*.txt *.log *.csv);;所有文件 (*)"
        )
        if file_path:
            self.analysis_file_path = file_path
            self.analysis_file_label.setText(os.path.basename(file_path))

    def add_replace_rule(self):
        row_count = self.replace_table.rowCount()
        self.replace_table.insertRow(row_count)

    def remove_replace_rule(self):
        current_row = self.replace_table.currentRow()
        if current_row >= 0:
            self.replace_table.removeRow(current_row)

    def on_split_method_changed(self, method):
        if method == "按行数分割":
            self.split_value_input.setPlaceholderText("请输入每份文件的行数")
        elif method == "按字符数分割":
            self.split_value_input.setPlaceholderText("请输入每份文件的字符数")
        elif method == "按分隔符分割":
            self.split_value_input.setPlaceholderText("请输入分隔符")

    def convert_encoding(self):
        if not hasattr(self, 'encoding_file_path'):
            QMessageBox.warning(self, "错误", "请先选择文件")
            return
        
        source_enc = self.source_encoding.currentText()
        if source_enc == "自动检测":
            source_enc = None
        
        target_enc = self.target_encoding.currentText()
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存转换后的文件", 
            f"{os.path.splitext(self.encoding_file_path)[0]}_{target_enc}.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if not output_path:
            return
        
        self.worker = TextProcessingWorker(
            "process_file",
            file_path=self.encoding_file_path,
            operation="convert_encoding",
            target_encoding=target_enc,
            output_path=output_path
        )
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def execute_find_replace(self):
        if not hasattr(self, 'replace_file_path'):
            QMessageBox.warning(self, "错误", "请先选择文件")
            return
        
        # 获取替换规则
        find_replace_pairs = []
        for row in range(self.replace_table.rowCount()):
            find_item = self.replace_table.item(row, 0)
            replace_item = self.replace_table.item(row, 1)
            
            if find_item and find_item.text():
                find_text = find_item.text()
                replace_text = replace_item.text() if replace_item else ""
                find_replace_pairs.append((find_text, replace_text))
        
        if not find_replace_pairs:
            QMessageBox.warning(self, "错误", "请至少添加一条替换规则")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存替换后的文件", 
            f"{os.path.splitext(self.replace_file_path)[0]}_replaced.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if not output_path:
            return
        
        self.worker = TextProcessingWorker(
            "process_file",
            file_path=self.replace_file_path,
            operation="find_replace",
            find_replace_pairs=find_replace_pairs,
            use_regex=self.use_regex.isChecked(),
            case_sensitive=self.case_sensitive.isChecked(),
            output_path=output_path
        )
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def split_text_file(self):
        if not hasattr(self, 'split_file_path'):
            QMessageBox.warning(self, "错误", "请先选择文件")
            return
        
        split_method_map = {
            "按行数分割": "lines",
            "按字符数分割": "chars", 
            "按分隔符分割": "delimiter"
        }
        
        method = split_method_map[self.split_method.currentText()]
        value = self.split_value_input.text().strip()
        
        if not value:
            QMessageBox.warning(self, "错误", "请输入分割值")
            return
        
        self.worker = TextProcessingWorker(
            "process_file",
            file_path=self.split_file_path,
            operation="split",
            split_method=method,
            split_value=value
        )
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def merge_text_files(self):
        if not hasattr(self, 'merge_file_paths'):
            QMessageBox.warning(self, "错误", "请先选择要合并的文件")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存合并后的文件", "merged_text.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if not output_path:
            return
        
        # 处理分隔符中的转义字符
        separator = self.separator_input.text().replace('\\n', '\n').replace('\\t', '\t')
        
        self.worker = TextProcessingWorker(
            "merge_files",
            file_paths=self.merge_file_paths,
            output_path=output_path,
            separator=separator
        )
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def analyze_text_file(self):
        if not hasattr(self, 'analysis_file_path'):
            QMessageBox.warning(self, "错误", "请先选择文件")
            return
        
        self.worker = TextProcessingWorker(
            "process_file",
            file_path=self.analysis_file_path,
            operation="analyze"
        )
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.start()

    @pyqtSlot(object, str)
    def on_operation_finished(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"操作失败: {error}")
        else:
            if isinstance(result, list):
                QMessageBox.information(self, "成功", f"操作完成！生成了 {len(result)} 个文件")
            else:
                QMessageBox.information(self, "成功", f"操作完成！\n输出文件: {result}")
            self.operation_successful.emit()

    @pyqtSlot(object, str)  
    def on_analysis_finished(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"分析失败: {error}")
        else:
            # 格式化分析结果显示
            analysis_text = f"""文本分析结果:
================================================
基本统计:
- 总字符数: {result['char_count']}
- 不含空格字符数: {result['char_count_no_spaces']}
- 单词数: {result['word_count']}
- 行数: {result['line_count']}
- 段落数: {result['paragraph_count']}
- 句子数: {result['sentence_count']}

平均统计:
- 平均每句单词数: {result['avg_words_per_sentence']}
- 平均每词字符数: {result['avg_chars_per_word']}

最常用字符 (前10个):
{chr(10).join([f"'{char}': {count}次" for char, count in result['most_common_chars']])}

最常用单词 (前10个):
{chr(10).join([f"'{word}': {count}次" for word, count in result['most_common_words']])}
"""
            self.analysis_result.setText(analysis_text)
            self.operation_successful.emit()