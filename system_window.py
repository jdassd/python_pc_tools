from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
                             QGroupBox, QHBoxLayout, QFileDialog, QMessageBox,
                             QTabWidget, QCheckBox, QSpinBox, QTextEdit, QProgressBar,
                             QTreeWidget, QTreeWidgetItem, QGridLayout, QComboBox,
                             QSplitter, QHeaderView)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from utils import resource_path
import system_utils
import os

class SystemWorker(QThread):
    finished = pyqtSignal(object, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        
    def run(self):
        try:
            if self.operation == "find_duplicates":
                self.status.emit("正在扫描文件...")
                result, error = system_utils.find_duplicate_files(**self.kwargs)
            elif self.operation == "batch_rename":
                self.status.emit("正在重命名文件...")
                result, error = system_utils.batch_rename_files(**self.kwargs)
            elif self.operation == "batch_rename_sequence":
                self.status.emit("正在按序列重命名...")
                result, error = system_utils.batch_rename_with_sequence(**self.kwargs)
            elif self.operation == "compare_dirs":
                self.status.emit("正在比较目录...")
                result, error = system_utils.compare_directories(**self.kwargs)
            elif self.operation == "find_empty_dirs":
                self.status.emit("正在查找空文件夹...")
                result, error = system_utils.find_empty_directories(**self.kwargs)
            elif self.operation == "clean_temp":
                self.status.emit("正在清理临时文件...")
                result, error = system_utils.clean_system_temp(**self.kwargs)
            elif self.operation == "dir_size":
                self.status.emit("正在计算目录大小...")
                result, error = system_utils.get_directory_size(**self.kwargs)
            else:
                result, error = None, "未知操作"
                
            self.finished.emit(result, error or "")
        except Exception as e:
            self.finished.emit(None, str(e))

class SystemWindow(QWidget):
    operation_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统工具")
        self.setGeometry(200, 200, 1000, 700)
        self.setWindowIcon(QIcon(resource_path("系统.png")))
        
        self.worker = None
        
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 文件重命名标签页
        self.setup_rename_tab()
        
        # 重复文件查找标签页
        self.setup_duplicate_tab()
        
        # 目录比较标签页
        self.setup_compare_tab()
        
        # 系统清理标签页
        self.setup_cleanup_tab()
        
        # 状态栏
        self.status_label = QLabel("就绪")
        main_layout.addWidget(self.status_label)

    def setup_rename_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 目录选择组
        dir_group = QGroupBox("目录选择")
        dir_layout = QHBoxLayout(dir_group)
        
        self.rename_dir_label = QLabel("未选择目录")
        select_dir_btn = QPushButton("选择目录")
        select_dir_btn.clicked.connect(self.select_rename_directory)
        
        dir_layout.addWidget(QLabel("目录:"))
        dir_layout.addWidget(self.rename_dir_label, 1)
        dir_layout.addWidget(select_dir_btn)
        layout.addWidget(dir_group)
        
        # 重命名方式选择
        method_group = QGroupBox("重命名方式")
        method_layout = QVBoxLayout(method_group)
        
        # 查找替换方式
        replace_frame = QWidget()
        replace_layout = QGridLayout(replace_frame)
        
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("要查找的文本")
        self.replace_input = QLineEdit() 
        self.replace_input.setPlaceholderText("替换为")
        
        self.use_regex_rename = QCheckBox("使用正则表达式")
        self.include_extension = QCheckBox("包含扩展名")
        
        replace_layout.addWidget(QLabel("查找:"), 0, 0)
        replace_layout.addWidget(self.find_input, 0, 1)
        replace_layout.addWidget(QLabel("替换:"), 1, 0)
        replace_layout.addWidget(self.replace_input, 1, 1)
        replace_layout.addWidget(self.use_regex_rename, 2, 0)
        replace_layout.addWidget(self.include_extension, 2, 1)
        
        method_layout.addWidget(QLabel("查找替换重命名:"))
        method_layout.addWidget(replace_frame)
        
        # 序列重命名方式
        sequence_frame = QWidget()
        sequence_layout = QGridLayout(sequence_frame)
        
        self.base_name_input = QLineEdit()
        self.base_name_input.setPlaceholderText("基础名称 (如: image)")
        self.start_num_input = QSpinBox()
        self.start_num_input.setMinimum(0)
        self.start_num_input.setMaximum(99999)
        self.start_num_input.setValue(1)
        self.padding_input = QSpinBox()
        self.padding_input.setMinimum(1)
        self.padding_input.setMaximum(10)
        self.padding_input.setValue(3)
        
        sequence_layout.addWidget(QLabel("基础名称:"), 0, 0)
        sequence_layout.addWidget(self.base_name_input, 0, 1)
        sequence_layout.addWidget(QLabel("起始编号:"), 1, 0)
        sequence_layout.addWidget(self.start_num_input, 1, 1)
        sequence_layout.addWidget(QLabel("补零位数:"), 2, 0)
        sequence_layout.addWidget(self.padding_input, 2, 1)
        
        method_layout.addWidget(QLabel("序列重命名:"))
        method_layout.addWidget(sequence_frame)
        
        layout.addWidget(method_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        replace_rename_btn = QPushButton("执行查找替换")
        sequence_rename_btn = QPushButton("执行序列重命名")
        
        replace_rename_btn.clicked.connect(self.execute_replace_rename)
        sequence_rename_btn.clicked.connect(self.execute_sequence_rename)
        
        btn_layout.addWidget(replace_rename_btn)
        btn_layout.addWidget(sequence_rename_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "文件重命名")

    def setup_duplicate_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 目录选择和选项
        top_layout = QHBoxLayout()
        
        dir_group = QGroupBox("扫描设置")
        dir_group_layout = QGridLayout(dir_group)
        
        self.duplicate_dir_label = QLabel("未选择目录")
        select_duplicate_dir_btn = QPushButton("选择目录")
        select_duplicate_dir_btn.clicked.connect(self.select_duplicate_directory)
        
        self.include_subdirs = QCheckBox("包含子目录")
        self.include_subdirs.setChecked(True)
        
        dir_group_layout.addWidget(QLabel("目录:"), 0, 0)
        dir_group_layout.addWidget(self.duplicate_dir_label, 0, 1)
        dir_group_layout.addWidget(select_duplicate_dir_btn, 0, 2)
        dir_group_layout.addWidget(self.include_subdirs, 1, 0, 1, 3)
        
        top_layout.addWidget(dir_group)
        
        scan_btn = QPushButton("开始扫描")
        scan_btn.clicked.connect(self.scan_duplicates)
        top_layout.addWidget(scan_btn)
        
        layout.addLayout(top_layout)
        
        # 结果显示
        self.duplicate_tree = QTreeWidget()
        self.duplicate_tree.setHeaderLabels(["文件", "大小", "路径"])
        self.duplicate_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.duplicate_tree)
        
        self.tab_widget.addTab(tab, "重复文件查找")

    def setup_compare_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 目录选择
        dirs_group = QGroupBox("选择要比较的目录")
        dirs_layout = QGridLayout(dirs_group)
        
        self.compare_dir1_label = QLabel("未选择目录1")
        self.compare_dir2_label = QLabel("未选择目录2")
        
        select_dir1_btn = QPushButton("选择目录1")
        select_dir2_btn = QPushButton("选择目录2")
        select_dir1_btn.clicked.connect(self.select_compare_dir1)
        select_dir2_btn.clicked.connect(self.select_compare_dir2)
        
        self.compare_content = QCheckBox("比较文件内容")
        
        dirs_layout.addWidget(QLabel("目录1:"), 0, 0)
        dirs_layout.addWidget(self.compare_dir1_label, 0, 1)
        dirs_layout.addWidget(select_dir1_btn, 0, 2)
        dirs_layout.addWidget(QLabel("目录2:"), 1, 0)
        dirs_layout.addWidget(self.compare_dir2_label, 1, 1)
        dirs_layout.addWidget(select_dir2_btn, 1, 2)
        dirs_layout.addWidget(self.compare_content, 2, 0, 1, 3)
        
        layout.addWidget(dirs_group)
        
        # 比较按钮
        compare_btn = QPushButton("开始比较")
        compare_btn.clicked.connect(self.compare_directories)
        layout.addWidget(compare_btn)
        
        # 结果显示
        self.compare_result = QTextEdit()
        self.compare_result.setReadOnly(True)
        layout.addWidget(self.compare_result)
        
        self.tab_widget.addTab(tab, "目录比较")

    def setup_cleanup_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 空文件夹清理
        empty_dirs_group = QGroupBox("空文件夹清理")
        empty_dirs_layout = QVBoxLayout(empty_dirs_group)
        
        dir_select_layout = QHBoxLayout()
        self.cleanup_dir_label = QLabel("未选择目录")
        select_cleanup_dir_btn = QPushButton("选择目录")
        select_cleanup_dir_btn.clicked.connect(self.select_cleanup_directory)
        
        dir_select_layout.addWidget(QLabel("目录:"))
        dir_select_layout.addWidget(self.cleanup_dir_label, 1)
        dir_select_layout.addWidget(select_cleanup_dir_btn)
        empty_dirs_layout.addLayout(dir_select_layout)
        
        empty_btn_layout = QHBoxLayout()
        find_empty_btn = QPushButton("查找空文件夹")
        remove_empty_btn = QPushButton("删除空文件夹")
        find_empty_btn.clicked.connect(lambda: self.find_empty_directories(False))
        remove_empty_btn.clicked.connect(lambda: self.find_empty_directories(True))
        
        empty_btn_layout.addWidget(find_empty_btn)
        empty_btn_layout.addWidget(remove_empty_btn)
        empty_dirs_layout.addLayout(empty_btn_layout)
        
        layout.addWidget(empty_dirs_group)
        
        # 临时文件清理
        temp_group = QGroupBox("临时文件清理")
        temp_layout = QVBoxLayout(temp_group)
        
        temp_info = QLabel("清理系统临时文件夹中的临时文件（超过1天未修改的文件）")
        temp_info.setWordWrap(True)
        temp_layout.addWidget(temp_info)
        
        temp_btn_layout = QHBoxLayout()
        preview_temp_btn = QPushButton("预览清理内容")
        clean_temp_btn = QPushButton("开始清理")
        preview_temp_btn.clicked.connect(lambda: self.clean_temp_files(True))
        clean_temp_btn.clicked.connect(lambda: self.clean_temp_files(False))
        
        temp_btn_layout.addWidget(preview_temp_btn)
        temp_btn_layout.addWidget(clean_temp_btn)
        temp_layout.addLayout(temp_btn_layout)
        
        layout.addWidget(temp_group)
        
        # 结果显示
        self.cleanup_result = QTextEdit()
        self.cleanup_result.setReadOnly(True)
        layout.addWidget(self.cleanup_result)
        
        self.tab_widget.addTab(tab, "系统清理")

    def select_rename_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择要重命名文件的目录")
        if directory:
            self.rename_directory = directory
            self.rename_dir_label.setText(directory)

    def select_duplicate_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择要扫描重复文件的目录")
        if directory:
            self.duplicate_directory = directory
            self.duplicate_dir_label.setText(directory)

    def select_compare_dir1(self):
        directory = QFileDialog.getExistingDirectory(self, "选择比较目录1")
        if directory:
            self.compare_directory1 = directory
            self.compare_dir1_label.setText(directory)

    def select_compare_dir2(self):
        directory = QFileDialog.getExistingDirectory(self, "选择比较目录2")
        if directory:
            self.compare_directory2 = directory
            self.compare_dir2_label.setText(directory)

    def select_cleanup_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择要清理的目录")
        if directory:
            self.cleanup_directory = directory
            self.cleanup_dir_label.setText(directory)

    def execute_replace_rename(self):
        if not hasattr(self, 'rename_directory'):
            QMessageBox.warning(self, "错误", "请先选择目录")
            return
        
        find_text = self.find_input.text().strip()
        replace_text = self.replace_input.text()
        
        if not find_text:
            QMessageBox.warning(self, "错误", "请输入要查找的文本")
            return
        
        self.worker = SystemWorker(
            "batch_rename",
            directory=self.rename_directory,
            pattern=find_text,
            replacement=replace_text,
            use_regex=self.use_regex_rename.isChecked(),
            include_extension=self.include_extension.isChecked()
        )
        self.worker.finished.connect(self.on_rename_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def execute_sequence_rename(self):
        if not hasattr(self, 'rename_directory'):
            QMessageBox.warning(self, "错误", "请先选择目录")
            return
        
        base_name = self.base_name_input.text().strip()
        if not base_name:
            QMessageBox.warning(self, "错误", "请输入基础名称")
            return
        
        self.worker = SystemWorker(
            "batch_rename_sequence",
            directory=self.rename_directory,
            base_name=base_name,
            start_num=self.start_num_input.value(),
            padding=self.padding_input.value()
        )
        self.worker.finished.connect(self.on_rename_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def scan_duplicates(self):
        if not hasattr(self, 'duplicate_directory'):
            QMessageBox.warning(self, "错误", "请先选择目录")
            return
        
        self.duplicate_tree.clear()
        
        self.worker = SystemWorker(
            "find_duplicates",
            directory=self.duplicate_directory,
            include_subdirs=self.include_subdirs.isChecked()
        )
        self.worker.finished.connect(self.on_duplicates_found)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def compare_directories(self):
        if not hasattr(self, 'compare_directory1') or not hasattr(self, 'compare_directory2'):
            QMessageBox.warning(self, "错误", "请先选择两个要比较的目录")
            return
        
        self.worker = SystemWorker(
            "compare_dirs",
            dir1=self.compare_directory1,
            dir2=self.compare_directory2,
            compare_content=self.compare_content.isChecked()
        )
        self.worker.finished.connect(self.on_compare_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def find_empty_directories(self, remove_empty):
        if not hasattr(self, 'cleanup_directory'):
            QMessageBox.warning(self, "错误", "请先选择目录")
            return
        
        if remove_empty:
            reply = QMessageBox.question(
                self, "确认删除", 
                "确定要删除所有空文件夹吗？此操作不可撤销。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.worker = SystemWorker(
            "find_empty_dirs",
            root_directory=self.cleanup_directory,
            remove_empty=remove_empty
        )
        self.worker.finished.connect(self.on_cleanup_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def clean_temp_files(self, dry_run):
        if not dry_run:
            reply = QMessageBox.question(
                self, "确认清理", 
                "确定要清理临时文件吗？此操作不可撤销。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.worker = SystemWorker(
            "clean_temp",
            dry_run=dry_run
        )
        self.worker.finished.connect(self.on_cleanup_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    @pyqtSlot(object, str)
    def on_rename_finished(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"重命名失败: {error}")
        else:
            renamed_files, errors = result
            message = f"成功重命名 {len(renamed_files)} 个文件"
            if errors:
                message += f"\n遇到 {len(errors)} 个错误"
            QMessageBox.information(self, "完成", message)
            self.operation_successful.emit()
        self.status_label.setText("就绪")

    @pyqtSlot(object, str)
    def on_duplicates_found(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"扫描失败: {error}")
        else:
            self.duplicate_tree.clear()
            total_duplicates = 0
            
            for hash_val, file_paths in result.items():
                if len(file_paths) > 1:
                    # 创建顶层项目
                    group_item = QTreeWidgetItem(self.duplicate_tree)
                    group_item.setText(0, f"重复组 ({len(file_paths)} 个文件)")
                    
                    total_duplicates += len(file_paths) - 1  # 减1是因为只有重复的算多余的
                    
                    # 添加每个重复文件
                    for file_path in file_paths:
                        file_item = QTreeWidgetItem(group_item)
                        file_item.setText(0, os.path.basename(file_path))
                        try:
                            size = os.path.getsize(file_path)
                            file_item.setText(1, system_utils.format_file_size(size))
                        except:
                            file_item.setText(1, "未知")
                        file_item.setText(2, file_path)
            
            self.duplicate_tree.expandAll()
            QMessageBox.information(self, "完成", f"找到 {total_duplicates} 个重复文件")
        
        self.status_label.setText("就绪")

    @pyqtSlot(object, str)
    def on_compare_finished(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"比较失败: {error}")
        else:
            compare_text = f"""目录比较结果:
================================================

仅在目录1中存在的文件 ({len(result['only_in_dir1'])} 个):
{chr(10).join(result['only_in_dir1']) if result['only_in_dir1'] else '无'}

仅在目录2中存在的文件 ({len(result['only_in_dir2'])} 个):
{chr(10).join(result['only_in_dir2']) if result['only_in_dir2'] else '无'}

两个目录中都存在的文件 ({len(result['common_files'])} 个):
{chr(10).join(result['common_files']) if result['common_files'] else '无'}
"""

            if 'same_content' in result:
                compare_text += f"""
内容相同的文件 ({len(result['same_content'])} 个):
{chr(10).join(result['same_content']) if result['same_content'] else '无'}

内容不同的文件 ({len(result['different_content'])} 个):
{chr(10).join(result['different_content']) if result['different_content'] else '无'}
"""
            
            self.compare_result.setText(compare_text)
            QMessageBox.information(self, "完成", "目录比较完成")
        
        self.status_label.setText("就绪")

    @pyqtSlot(object, str)
    def on_cleanup_finished(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"清理失败: {error}")
        else:
            if 'empty_dirs' in result:
                # 空文件夹清理结果
                cleanup_text = f"空文件夹清理结果:\n"
                cleanup_text += f"找到空文件夹: {len(result['empty_dirs'])} 个\n\n"
                
                if result['empty_dirs']:
                    cleanup_text += "空文件夹列表:\n"
                    cleanup_text += "\n".join(result['empty_dirs'])
                
                if 'removed_dirs' in result:
                    cleanup_text += f"\n\n已删除: {len(result['removed_dirs'])} 个"
                
            elif 'cleaned_files' in result:
                # 临时文件清理结果
                cleanup_text = f"临时文件清理结果:\n"
                cleanup_text += f"{'预览' if result['dry_run'] else '实际清理'}: {len(result['cleaned_files'])} 个项目\n"
                cleanup_text += f"节省空间: {system_utils.format_file_size(result['cleaned_size'])}\n"
                
                if result['errors']:
                    cleanup_text += f"\n遇到错误: {len(result['errors'])} 个\n"
                    cleanup_text += "\n".join(result['errors'][:10])  # 只显示前10个错误
                    if len(result['errors']) > 10:
                        cleanup_text += f"\n... 还有 {len(result['errors']) - 10} 个错误"
                
                if result['cleaned_files'][:10]:  # 显示前10个文件
                    cleanup_text += "\n\n清理的文件/文件夹 (显示前10个):\n"
                    cleanup_text += "\n".join(result['cleaned_files'][:10])
                    if len(result['cleaned_files']) > 10:
                        cleanup_text += f"\n... 还有 {len(result['cleaned_files']) - 10} 个项目"
            
            self.cleanup_result.setText(cleanup_text)
            QMessageBox.information(self, "完成", "清理操作完成")
            self.operation_successful.emit()
        
        self.status_label.setText("就绪")