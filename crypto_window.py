from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget,
                             QFileDialog, QMessageBox, QProgressBar, QComboBox, 
                             QCheckBox, QSpinBox, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from utils import resource_path
import crypto_utils
import os

class CryptoWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "encrypt_file":
                result = crypto_utils.encrypt_file(
                    self.kwargs['file_path'],
                    self.kwargs['password'],
                    self.kwargs.get('output_path')
                )
                self.finished.emit(f"文件加密完成: {result}")
            elif self.operation == "decrypt_file":
                result = crypto_utils.decrypt_file(
                    self.kwargs['file_path'],
                    self.kwargs['password'],
                    self.kwargs.get('output_path')
                )
                self.finished.emit(f"文件解密完成: {result}")
            elif self.operation == "calculate_hash":
                result = crypto_utils.calculate_file_hash(
                    self.kwargs['file_path'],
                    self.kwargs['algorithm']
                )
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class CryptoWindow(QMainWindow):
    operation_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("加密解密工具")
        self.setGeometry(200, 200, 800, 600)
        self.setWindowIcon(QIcon(resource_path("加密.png")))
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 文件加密解密选项卡
        self.file_crypto_tab = self.create_file_crypto_tab()
        self.tab_widget.addTab(self.file_crypto_tab, "文件加密解密")
        
        # 文本加密解密选项卡
        self.text_crypto_tab = self.create_text_crypto_tab()
        self.tab_widget.addTab(self.text_crypto_tab, "文本加密解密")
        
        # 哈希计算选项卡
        self.hash_tab = self.create_hash_tab()
        self.tab_widget.addTab(self.hash_tab, "哈希计算")
        
        # 密码生成选项卡
        self.password_tab = self.create_password_tab()
        self.tab_widget.addTab(self.password_tab, "密码生成器")
        
    def create_file_crypto_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件选择
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("选择要加密/解密的文件...")
        file_layout.addWidget(self.file_path_input)
        
        file_btn_layout = QHBoxLayout()
        self.select_file_btn = QPushButton("选择文件")
        self.select_file_btn.clicked.connect(self.select_file)
        file_btn_layout.addWidget(self.select_file_btn)
        file_btn_layout.addStretch()
        file_layout.addLayout(file_btn_layout)
        
        layout.addWidget(file_group)
        
        # 密码设置
        password_group = QGroupBox("密码设置")
        password_layout = QVBoxLayout(password_group)
        
        self.file_password_input = QLineEdit()
        self.file_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.file_password_input.setPlaceholderText("输入加密/解密密码...")
        password_layout.addWidget(self.file_password_input)
        
        layout.addWidget(password_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.encrypt_file_btn = QPushButton("加密文件")
        self.encrypt_file_btn.clicked.connect(self.encrypt_file)
        self.decrypt_file_btn = QPushButton("解密文件")
        self.decrypt_file_btn.clicked.connect(self.decrypt_file)
        
        btn_layout.addWidget(self.encrypt_file_btn)
        btn_layout.addWidget(self.decrypt_file_btn)
        layout.addLayout(btn_layout)
        
        # 进度条
        self.file_progress = QProgressBar()
        self.file_progress.setVisible(False)
        layout.addWidget(self.file_progress)
        
        layout.addStretch()
        return widget
    
    def create_text_crypto_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入文本
        input_group = QGroupBox("输入文本")
        input_layout = QVBoxLayout(input_group)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("输入要加密/解密的文本...")
        input_layout.addWidget(self.text_input)
        
        layout.addWidget(input_group)
        
        # 密码设置
        password_group = QGroupBox("密码设置")
        password_layout = QVBoxLayout(password_group)
        
        self.text_password_input = QLineEdit()
        self.text_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.text_password_input.setPlaceholderText("输入加密/解密密码...")
        password_layout.addWidget(self.text_password_input)
        
        layout.addWidget(password_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.encrypt_text_btn = QPushButton("加密文本")
        self.encrypt_text_btn.clicked.connect(self.encrypt_text)
        self.decrypt_text_btn = QPushButton("解密文本")
        self.decrypt_text_btn.clicked.connect(self.decrypt_text)
        
        btn_layout.addWidget(self.encrypt_text_btn)
        btn_layout.addWidget(self.decrypt_text_btn)
        layout.addLayout(btn_layout)
        
        # 输出文本
        output_group = QGroupBox("输出结果")
        output_layout = QVBoxLayout(output_group)
        
        self.text_output = QTextEdit()
        self.text_output.setPlaceholderText("加密/解密结果将显示在这里...")
        self.text_output.setReadOnly(True)
        output_layout.addWidget(self.text_output)
        
        layout.addWidget(output_group)
        
        return widget
    
    def create_hash_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入选择
        input_group = QGroupBox("输入选择")
        input_layout = QVBoxLayout(input_group)
        
        # 文件哈希
        file_hash_layout = QHBoxLayout()
        self.hash_file_path = QLineEdit()
        self.hash_file_path.setPlaceholderText("选择要计算哈希的文件...")
        self.select_hash_file_btn = QPushButton("选择文件")
        self.select_hash_file_btn.clicked.connect(self.select_hash_file)
        
        file_hash_layout.addWidget(self.hash_file_path)
        file_hash_layout.addWidget(self.select_hash_file_btn)
        input_layout.addLayout(file_hash_layout)
        
        # 文本哈希
        self.hash_text_input = QTextEdit()
        self.hash_text_input.setPlaceholderText("或者输入要计算哈希的文本...")
        self.hash_text_input.setMaximumHeight(100)
        input_layout.addWidget(self.hash_text_input)
        
        layout.addWidget(input_group)
        
        # 哈希算法选择
        algorithm_group = QGroupBox("哈希算法")
        algorithm_layout = QHBoxLayout(algorithm_group)
        
        self.hash_algorithm = QComboBox()
        self.hash_algorithm.addItems(["MD5", "SHA1", "SHA256", "SHA512"])
        self.hash_algorithm.setCurrentText("MD5")
        
        self.calculate_hash_btn = QPushButton("计算哈希")
        self.calculate_hash_btn.clicked.connect(self.calculate_hash)
        
        algorithm_layout.addWidget(QLabel("算法:"))
        algorithm_layout.addWidget(self.hash_algorithm)
        algorithm_layout.addWidget(self.calculate_hash_btn)
        algorithm_layout.addStretch()
        
        layout.addWidget(algorithm_group)
        
        # 哈希结果
        result_group = QGroupBox("哈希结果")
        result_layout = QVBoxLayout(result_group)
        
        self.hash_result = QTextEdit()
        self.hash_result.setPlaceholderText("哈希值将显示在这里...")
        self.hash_result.setReadOnly(True)
        self.hash_result.setMaximumHeight(100)
        result_layout.addWidget(self.hash_result)
        
        layout.addWidget(result_group)
        
        layout.addStretch()
        return widget
    
    def create_password_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 密码设置
        settings_group = QGroupBox("密码设置")
        settings_layout = QGridLayout(settings_group)
        
        # 密码长度
        settings_layout.addWidget(QLabel("密码长度:"), 0, 0)
        self.password_length = QSpinBox()
        self.password_length.setRange(1, 128)
        self.password_length.setValue(12)
        settings_layout.addWidget(self.password_length, 0, 1)
        
        # 字符类型选择
        self.use_uppercase = QCheckBox("大写字母 (A-Z)")
        self.use_uppercase.setChecked(True)
        settings_layout.addWidget(self.use_uppercase, 1, 0, 1, 2)
        
        self.use_lowercase = QCheckBox("小写字母 (a-z)")
        self.use_lowercase.setChecked(True)
        settings_layout.addWidget(self.use_lowercase, 2, 0, 1, 2)
        
        self.use_digits = QCheckBox("数字 (0-9)")
        self.use_digits.setChecked(True)
        settings_layout.addWidget(self.use_digits, 3, 0, 1, 2)
        
        self.use_symbols = QCheckBox("特殊符号 (!@#$%^&*等)")
        self.use_symbols.setChecked(True)
        settings_layout.addWidget(self.use_symbols, 4, 0, 1, 2)
        
        layout.addWidget(settings_group)
        
        # 生成按钮
        generate_layout = QHBoxLayout()
        self.generate_password_btn = QPushButton("生成密码")
        self.generate_password_btn.clicked.connect(self.generate_password)
        generate_layout.addWidget(self.generate_password_btn)
        generate_layout.addStretch()
        layout.addLayout(generate_layout)
        
        # 生成的密码
        result_group = QGroupBox("生成的密码")
        result_layout = QVBoxLayout(result_group)
        
        self.generated_passwords = QTextEdit()
        self.generated_passwords.setPlaceholderText("生成的密码将显示在这里...")
        self.generated_passwords.setReadOnly(True)
        result_layout.addWidget(self.generated_passwords)
        
        layout.addWidget(result_group)
        
        return widget
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
        if file_path:
            self.file_path_input.setText(file_path)
    
    def select_hash_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*)")
        if file_path:
            self.hash_file_path.setText(file_path)
    
    def encrypt_file(self):
        file_path = self.file_path_input.text()
        password = self.file_password_input.text()
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", "请选择有效的文件")
            return
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
        
        self.file_progress.setVisible(True)
        self.file_progress.setRange(0, 0)
        
        self.crypto_worker = CryptoWorker("encrypt_file", file_path=file_path, password=password)
        self.crypto_worker.finished.connect(self.on_crypto_finished)
        self.crypto_worker.error.connect(self.on_crypto_error)
        self.crypto_worker.start()
    
    def decrypt_file(self):
        file_path = self.file_path_input.text()
        password = self.file_password_input.text()
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", "请选择有效的文件")
            return
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
        
        self.file_progress.setVisible(True)
        self.file_progress.setRange(0, 0)
        
        self.crypto_worker = CryptoWorker("decrypt_file", file_path=file_path, password=password)
        self.crypto_worker.finished.connect(self.on_crypto_finished)
        self.crypto_worker.error.connect(self.on_crypto_error)
        self.crypto_worker.start()
    
    def encrypt_text(self):
        text = self.text_input.toPlainText()
        password = self.text_password_input.text()
        
        if not text:
            QMessageBox.warning(self, "警告", "请输入要加密的文本")
            return
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
        
        try:
            encrypted_text = crypto_utils.encrypt_text(text, password)
            self.text_output.setPlainText(encrypted_text)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加密失败: {str(e)}")
    
    def decrypt_text(self):
        text = self.text_input.toPlainText()
        password = self.text_password_input.text()
        
        if not text:
            QMessageBox.warning(self, "警告", "请输入要解密的文本")
            return
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
        
        try:
            decrypted_text = crypto_utils.decrypt_text(text, password)
            self.text_output.setPlainText(decrypted_text)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解密失败: {str(e)}")
    
    def calculate_hash(self):
        file_path = self.hash_file_path.text()
        text = self.hash_text_input.toPlainText()
        algorithm = self.hash_algorithm.currentText()
        
        if file_path and os.path.exists(file_path):
            self.crypto_worker = CryptoWorker("calculate_hash", file_path=file_path, algorithm=algorithm)
            self.crypto_worker.finished.connect(self.on_hash_finished)
            self.crypto_worker.error.connect(self.on_crypto_error)
            self.crypto_worker.start()
        elif text:
            try:
                hash_value = crypto_utils.calculate_text_hash(text, algorithm)
                self.hash_result.setPlainText(f"{algorithm}: {hash_value}")
                self.operation_successful.emit()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"计算哈希失败: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "请选择文件或输入文本")
    
    def generate_password(self):
        length = self.password_length.value()
        use_uppercase = self.use_uppercase.isChecked()
        use_lowercase = self.use_lowercase.isChecked()
        use_digits = self.use_digits.isChecked()
        use_symbols = self.use_symbols.isChecked()
        
        try:
            password = crypto_utils.generate_password(
                length, use_uppercase, use_lowercase, use_digits, use_symbols
            )
            current_text = self.generated_passwords.toPlainText()
            if current_text:
                new_text = current_text + "\n" + password
            else:
                new_text = password
            self.generated_passwords.setPlainText(new_text)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成密码失败: {str(e)}")
    
    def on_crypto_finished(self, result):
        self.file_progress.setVisible(False)
        QMessageBox.information(self, "完成", result)
        self.operation_successful.emit()
    
    def on_hash_finished(self, result):
        algorithm = self.hash_algorithm.currentText()
        self.hash_result.setPlainText(f"{algorithm}: {result}")
        self.operation_successful.emit()
    
    def on_crypto_error(self, error):
        self.file_progress.setVisible(False)
        QMessageBox.critical(self, "错误", error)