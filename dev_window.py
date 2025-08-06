from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget,
                             QMessageBox, QComboBox, QGroupBox, QGridLayout,
                             QCheckBox, QSpinBox, QColorDialog, QListWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor
from utils import resource_path
import dev_utils
import re

class DevWindow(QMainWindow):
    operation_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("开发者工具")
        self.setGeometry(200, 200, 900, 700)
        self.setWindowIcon(QIcon(resource_path("开发.png")))
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # JSON/XML格式化选项卡
        self.format_tab = self.create_format_tab()
        self.tab_widget.addTab(self.format_tab, "JSON/XML格式化")
        
        # URL/Base64编码选项卡
        self.encode_tab = self.create_encode_tab()
        self.tab_widget.addTab(self.encode_tab, "URL/Base64编码")
        
        # 正则表达式选项卡
        self.regex_tab = self.create_regex_tab()
        self.tab_widget.addTab(self.regex_tab, "正则表达式")
        
        # 颜色工具选项卡
        self.color_tab = self.create_color_tab()
        self.tab_widget.addTab(self.color_tab, "颜色工具")
        
    def create_format_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入区域
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        
        self.format_input = QTextEdit()
        self.format_input.setPlaceholderText("粘贴JSON或XML代码...")
        input_layout.addWidget(self.format_input)
        
        layout.addWidget(input_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.format_json_btn = QPushButton("格式化JSON")
        self.format_json_btn.clicked.connect(self.format_json)
        self.minify_json_btn = QPushButton("压缩JSON")
        self.minify_json_btn.clicked.connect(self.minify_json)
        self.validate_json_btn = QPushButton("验证JSON")
        self.validate_json_btn.clicked.connect(self.validate_json)
        
        self.format_xml_btn = QPushButton("格式化XML")
        self.format_xml_btn.clicked.connect(self.format_xml)
        self.minify_xml_btn = QPushButton("压缩XML")
        self.minify_xml_btn.clicked.connect(self.minify_xml)
        self.validate_xml_btn = QPushButton("验证XML")
        self.validate_xml_btn.clicked.connect(self.validate_xml)
        
        btn_layout.addWidget(self.format_json_btn)
        btn_layout.addWidget(self.minify_json_btn)
        btn_layout.addWidget(self.validate_json_btn)
        btn_layout.addWidget(self.format_xml_btn)
        btn_layout.addWidget(self.minify_xml_btn)
        btn_layout.addWidget(self.validate_xml_btn)
        
        layout.addLayout(btn_layout)
        
        # 输出区域
        output_group = QGroupBox("输出")
        output_layout = QVBoxLayout(output_group)
        
        self.format_output = QTextEdit()
        self.format_output.setPlaceholderText("格式化结果将显示在这里...")
        self.format_output.setReadOnly(True)
        output_layout.addWidget(self.format_output)
        
        layout.addWidget(output_group)
        
        return widget
    
    def create_encode_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入区域
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        
        self.encode_input = QTextEdit()
        self.encode_input.setPlaceholderText("输入要编码/解码的文本...")
        input_layout.addWidget(self.encode_input)
        
        layout.addWidget(input_group)
        
        # 操作按钮
        btn_layout = QGridLayout()
        
        self.url_encode_btn = QPushButton("URL编码")
        self.url_encode_btn.clicked.connect(self.url_encode)
        self.url_decode_btn = QPushButton("URL解码")
        self.url_decode_btn.clicked.connect(self.url_decode)
        
        self.base64_encode_btn = QPushButton("Base64编码")
        self.base64_encode_btn.clicked.connect(self.base64_encode)
        self.base64_decode_btn = QPushButton("Base64解码")
        self.base64_decode_btn.clicked.connect(self.base64_decode)
        
        self.html_encode_btn = QPushButton("HTML编码")
        self.html_encode_btn.clicked.connect(self.html_encode)
        self.html_decode_btn = QPushButton("HTML解码")
        self.html_decode_btn.clicked.connect(self.html_decode)
        
        btn_layout.addWidget(self.url_encode_btn, 0, 0)
        btn_layout.addWidget(self.url_decode_btn, 0, 1)
        btn_layout.addWidget(self.base64_encode_btn, 1, 0)
        btn_layout.addWidget(self.base64_decode_btn, 1, 1)
        btn_layout.addWidget(self.html_encode_btn, 2, 0)
        btn_layout.addWidget(self.html_decode_btn, 2, 1)
        
        layout.addLayout(btn_layout)
        
        # 输出区域
        output_group = QGroupBox("输出")
        output_layout = QVBoxLayout(output_group)
        
        self.encode_output = QTextEdit()
        self.encode_output.setPlaceholderText("编码/解码结果将显示在这里...")
        self.encode_output.setReadOnly(True)
        output_layout.addWidget(self.encode_output)
        
        layout.addWidget(output_group)
        
        return widget
    
    def create_regex_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 正则表达式输入
        regex_group = QGroupBox("正则表达式")
        regex_layout = QVBoxLayout(regex_group)
        
        self.regex_pattern = QLineEdit()
        self.regex_pattern.setPlaceholderText("输入正则表达式...")
        regex_layout.addWidget(self.regex_pattern)
        
        # 标志选项
        flags_layout = QHBoxLayout()
        self.ignore_case = QCheckBox("忽略大小写 (i)")
        self.multiline = QCheckBox("多行模式 (m)")
        self.dotall = QCheckBox("单行模式 (s)")
        
        flags_layout.addWidget(self.ignore_case)
        flags_layout.addWidget(self.multiline)
        flags_layout.addWidget(self.dotall)
        flags_layout.addStretch()
        regex_layout.addLayout(flags_layout)
        
        layout.addWidget(regex_group)
        
        # 测试文本
        text_group = QGroupBox("测试文本")
        text_layout = QVBoxLayout(text_group)
        
        self.regex_text = QTextEdit()
        self.regex_text.setPlaceholderText("输入要测试的文本...")
        text_layout.addWidget(self.regex_text)
        
        layout.addWidget(text_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.test_regex_btn = QPushButton("测试匹配")
        self.test_regex_btn.clicked.connect(self.test_regex)
        
        btn_layout.addWidget(self.test_regex_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 替换功能
        replace_group = QGroupBox("替换")
        replace_layout = QVBoxLayout(replace_group)
        
        self.replacement_text = QLineEdit()
        self.replacement_text.setPlaceholderText("替换为...")
        replace_layout.addWidget(self.replacement_text)
        
        self.replace_btn = QPushButton("执行替换")
        self.replace_btn.clicked.connect(self.regex_replace)
        replace_layout.addWidget(self.replace_btn)
        
        layout.addWidget(replace_group)
        
        # 结果显示
        result_group = QGroupBox("匹配结果")
        result_layout = QVBoxLayout(result_group)
        
        self.regex_result = QTextEdit()
        self.regex_result.setPlaceholderText("匹配结果将显示在这里...")
        self.regex_result.setReadOnly(True)
        result_layout.addWidget(self.regex_result)
        
        layout.addWidget(result_group)
        
        return widget
    
    def create_color_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 颜色输入
        input_group = QGroupBox("颜色输入")
        input_layout = QGridLayout(input_group)
        
        # 十六进制输入
        input_layout.addWidget(QLabel("十六进制:"), 0, 0)
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#FF0000")
        self.hex_input.textChanged.connect(self.on_hex_changed)
        input_layout.addWidget(self.hex_input, 0, 1)
        
        # RGB输入
        input_layout.addWidget(QLabel("R:"), 1, 0)
        self.r_input = QSpinBox()
        self.r_input.setRange(0, 255)
        self.r_input.valueChanged.connect(self.on_rgb_changed)
        input_layout.addWidget(self.r_input, 1, 1)
        
        input_layout.addWidget(QLabel("G:"), 1, 2)
        self.g_input = QSpinBox()
        self.g_input.setRange(0, 255)
        self.g_input.valueChanged.connect(self.on_rgb_changed)
        input_layout.addWidget(self.g_input, 1, 3)
        
        input_layout.addWidget(QLabel("B:"), 1, 4)
        self.b_input = QSpinBox()
        self.b_input.setRange(0, 255)
        self.b_input.valueChanged.connect(self.on_rgb_changed)
        input_layout.addWidget(self.b_input, 1, 5)
        
        # 颜色选择器
        self.color_picker_btn = QPushButton("选择颜色")
        self.color_picker_btn.clicked.connect(self.open_color_picker)
        input_layout.addWidget(self.color_picker_btn, 2, 0, 1, 2)
        
        # 颜色预览
        self.color_preview = QLabel()
        self.color_preview.setMinimumHeight(50)
        self.color_preview.setStyleSheet("border: 1px solid #ccc; background-color: #ffffff;")
        input_layout.addWidget(self.color_preview, 2, 2, 1, 4)
        
        layout.addWidget(input_group)
        
        # 颜色信息显示
        info_group = QGroupBox("颜色信息")
        info_layout = QGridLayout(info_group)
        
        info_layout.addWidget(QLabel("HSL:"), 0, 0)
        self.hsl_label = QLabel("0, 0%, 0%")
        info_layout.addWidget(self.hsl_label, 0, 1)
        
        layout.addWidget(info_group)
        
        # 调色板生成
        palette_group = QGroupBox("调色板生成")
        palette_layout = QVBoxLayout(palette_group)
        
        palette_btn_layout = QHBoxLayout()
        self.generate_palette_btn = QPushButton("生成调色板")
        self.generate_palette_btn.clicked.connect(self.generate_palette)
        
        self.palette_count = QSpinBox()
        self.palette_count.setRange(3, 10)
        self.palette_count.setValue(5)
        
        palette_btn_layout.addWidget(self.generate_palette_btn)
        palette_btn_layout.addWidget(QLabel("颜色数量:"))
        palette_btn_layout.addWidget(self.palette_count)
        palette_btn_layout.addStretch()
        
        palette_layout.addLayout(palette_btn_layout)
        
        # 调色板显示
        self.palette_list = QListWidget()
        self.palette_list.setMaximumHeight(150)
        palette_layout.addWidget(self.palette_list)
        
        layout.addWidget(palette_group)
        
        layout.addStretch()
        return widget
    
    def format_json(self):
        text = self.format_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入JSON文本")
            return
        
        try:
            formatted = dev_utils.format_json(text)
            self.format_output.setPlainText(formatted)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def minify_json(self):
        text = self.format_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入JSON文本")
            return
        
        try:
            minified = dev_utils.minify_json(text)
            self.format_output.setPlainText(minified)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def validate_json(self):
        text = self.format_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入JSON文本")
            return
        
        is_valid, message = dev_utils.validate_json(text)
        if is_valid:
            QMessageBox.information(self, "验证结果", message)
        else:
            QMessageBox.warning(self, "验证结果", message)
        self.operation_successful.emit()
    
    def format_xml(self):
        text = self.format_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入XML文本")
            return
        
        try:
            formatted = dev_utils.format_xml(text)
            self.format_output.setPlainText(formatted)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def minify_xml(self):
        text = self.format_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入XML文本")
            return
        
        try:
            minified = dev_utils.minify_xml(text)
            self.format_output.setPlainText(minified)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def validate_xml(self):
        text = self.format_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入XML文本")
            return
        
        is_valid, message = dev_utils.validate_xml(text)
        if is_valid:
            QMessageBox.information(self, "验证结果", message)
        else:
            QMessageBox.warning(self, "验证结果", message)
        self.operation_successful.emit()
    
    def url_encode(self):
        text = self.encode_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本")
            return
        
        try:
            encoded = dev_utils.url_encode(text)
            self.encode_output.setPlainText(encoded)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def url_decode(self):
        text = self.encode_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本")
            return
        
        try:
            decoded = dev_utils.url_decode(text)
            self.encode_output.setPlainText(decoded)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def base64_encode(self):
        text = self.encode_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本")
            return
        
        try:
            encoded = dev_utils.base64_encode(text)
            self.encode_output.setPlainText(encoded)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def base64_decode(self):
        text = self.encode_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本")
            return
        
        try:
            decoded = dev_utils.base64_decode(text)
            self.encode_output.setPlainText(decoded)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def html_encode(self):
        text = self.encode_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本")
            return
        
        try:
            encoded = dev_utils.html_encode(text)
            self.encode_output.setPlainText(encoded)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def html_decode(self):
        text = self.encode_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本")
            return
        
        try:
            decoded = dev_utils.html_decode(text)
            self.encode_output.setPlainText(decoded)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def test_regex(self):
        pattern = self.regex_pattern.text()
        text = self.regex_text.toPlainText()
        
        if not pattern:
            QMessageBox.warning(self, "警告", "请输入正则表达式")
            return
        
        if not text:
            QMessageBox.warning(self, "警告", "请输入测试文本")
            return
        
        flags = 0
        if self.ignore_case.isChecked():
            flags |= re.IGNORECASE
        if self.multiline.isChecked():
            flags |= re.MULTILINE
        if self.dotall.isChecked():
            flags |= re.DOTALL
        
        try:
            result = dev_utils.test_regex(pattern, text, flags)
            
            output = f"匹配数量: {result['match_count']}\n\n"
            if result['matches']:
                output += "匹配项:\n"
                for i, match in enumerate(result['matches'], 1):
                    output += f"{i}. {match}\n"
                
                output += "\n匹配详情:\n"
                for i, detail in enumerate(result['match_details'], 1):
                    output += f"{i}. 位置 {detail['start']}-{detail['end']}: {detail['match']}\n"
                    if detail['groups']:
                        output += f"   分组: {detail['groups']}\n"
            else:
                output += "没有找到匹配项"
            
            self.regex_result.setPlainText(output)
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def regex_replace(self):
        pattern = self.regex_pattern.text()
        text = self.regex_text.toPlainText()
        replacement = self.replacement_text.text()
        
        if not pattern:
            QMessageBox.warning(self, "警告", "请输入正则表达式")
            return
        
        if not text:
            QMessageBox.warning(self, "警告", "请输入测试文本")
            return
        
        flags = 0
        if self.ignore_case.isChecked():
            flags |= re.IGNORECASE
        if self.multiline.isChecked():
            flags |= re.MULTILINE
        if self.dotall.isChecked():
            flags |= re.DOTALL
        
        try:
            result = dev_utils.regex_replace(pattern, replacement, text, flags)
            self.regex_result.setPlainText(f"替换结果:\n{result}")
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def on_hex_changed(self):
        hex_color = self.hex_input.text()
        if len(hex_color) == 7 and hex_color.startswith('#'):
            try:
                r, g, b = dev_utils.hex_to_rgb(hex_color)
                self.r_input.blockSignals(True)
                self.g_input.blockSignals(True)
                self.b_input.blockSignals(True)
                
                self.r_input.setValue(r)
                self.g_input.setValue(g)
                self.b_input.setValue(b)
                
                self.r_input.blockSignals(False)
                self.g_input.blockSignals(False)
                self.b_input.blockSignals(False)
                
                self.update_color_display(r, g, b)
            except:
                pass
    
    def on_rgb_changed(self):
        r = self.r_input.value()
        g = self.g_input.value()
        b = self.b_input.value()
        
        hex_color = dev_utils.rgb_to_hex(r, g, b)
        self.hex_input.blockSignals(True)
        self.hex_input.setText(hex_color)
        self.hex_input.blockSignals(False)
        
        self.update_color_display(r, g, b)
    
    def update_color_display(self, r, g, b):
        # 更新颜色预览
        self.color_preview.setStyleSheet(
            f"border: 1px solid #ccc; background-color: rgb({r}, {g}, {b});"
        )
        
        # 更新HSL显示
        h, s, l = dev_utils.rgb_to_hsl(r, g, b)
        self.hsl_label.setText(f"{h}°, {s}%, {l}%")
    
    def open_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            
            self.r_input.setValue(r)
            self.g_input.setValue(g)
            self.b_input.setValue(b)
            
            hex_color = dev_utils.rgb_to_hex(r, g, b)
            self.hex_input.setText(hex_color)
            
            self.update_color_display(r, g, b)
    
    def generate_palette(self):
        hex_color = self.hex_input.text()
        count = self.palette_count.value()
        
        if not hex_color or not hex_color.startswith('#'):
            QMessageBox.warning(self, "警告", "请输入有效的十六进制颜色")
            return
        
        try:
            palette = dev_utils.generate_color_palette(hex_color, count)
            
            self.palette_list.clear()
            for color in palette:
                r, g, b = dev_utils.hex_to_rgb(color)
                item_widget = QLabel(f"{color} | RGB({r}, {g}, {b})")
                item_widget.setStyleSheet(f"background-color: {color}; padding: 5px; margin: 2px;")
                
                from PyQt6.QtWidgets import QListWidgetItem
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.palette_list.addItem(item)
                self.palette_list.setItemWidget(item, item_widget)
            
            self.operation_successful.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))