from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
                             QGroupBox, QHBoxLayout, QMessageBox, QTabWidget, 
                             QTextEdit, QSpinBox, QComboBox, QProgressBar, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout,
                             QCheckBox, QFileDialog, QSplitter)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from utils import resource_path
import network_utils
import os
from PIL import Image
from io import BytesIO

class NetworkWorker(QThread):
    finished = pyqtSignal(object, str)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        
    def run(self):
        try:
            if self.operation == "generate_qr":
                self.status.emit("正在生成二维码...")
                result, error = network_utils.generate_qr_code(**self.kwargs)
            elif self.operation == "test_urls":
                self.status.emit("正在测试URL...")
                result, error = network_utils.test_urls_batch(**self.kwargs)
            elif self.operation == "scan_ports":
                self.status.emit("正在扫描端口...")
                result, error = network_utils.scan_ports(**self.kwargs)
            elif self.operation == "ping_host":
                self.status.emit("正在ping主机...")
                result, error = network_utils.ping_host(**self.kwargs)
            elif self.operation == "trace_route":
                self.status.emit("正在跟踪路由...")
                result, error = network_utils.trace_route(**self.kwargs)
            elif self.operation == "check_internet":
                self.status.emit("正在检查网络连接...")
                result, error = network_utils.check_internet_connection()
            elif self.operation == "get_network_info":
                self.status.emit("正在获取网络信息...")
                result, error = network_utils.get_network_info()
            elif self.operation == "start_server":
                self.status.emit("正在启动HTTP服务器...")
                server = network_utils.SimpleHTTPServer(**self.kwargs)
                result, error = server.start()
                # 保存服务器引用以便后续停止
                self.server = server
            else:
                result, error = None, "未知操作"
                
            self.finished.emit(result, error or "")
        except Exception as e:
            self.finished.emit(None, str(e))

class NetworkWindow(QWidget):
    operation_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("网络工具")
        self.setGeometry(200, 200, 1000, 700)
        self.setWindowIcon(QIcon(resource_path("网络.png")))
        
        self.worker = None
        self.http_server = None
        
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 二维码生成标签页
        self.setup_qr_tab()
        
        # URL测试标签页
        self.setup_url_test_tab()
        
        # 端口扫描标签页
        self.setup_port_scan_tab()
        
        # HTTP服务器标签页
        self.setup_http_server_tab()
        
        # 网络诊断标签页
        self.setup_network_diag_tab()
        
        # 状态栏
        self.status_label = QLabel("就绪")
        main_layout.addWidget(self.status_label)

    def setup_qr_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文本输入组
        input_group = QGroupBox("二维码内容")
        input_layout = QVBoxLayout(input_group)
        
        self.qr_text_input = QTextEdit()
        self.qr_text_input.setPlaceholderText("输入要生成二维码的文本内容...")
        self.qr_text_input.setMaximumHeight(100)
        input_layout.addWidget(self.qr_text_input)
        
        layout.addWidget(input_group)
        
        # 设置组
        settings_group = QGroupBox("二维码设置")
        settings_layout = QGridLayout(settings_group)
        
        self.error_correction = QComboBox()
        self.error_correction.addItems(["L (7%)", "M (15%)", "Q (25%)", "H (30%)"])
        self.error_correction.setCurrentText("M (15%)")
        
        self.box_size = QSpinBox()
        self.box_size.setRange(1, 50)
        self.box_size.setValue(10)
        
        self.border_size = QSpinBox()
        self.border_size.setRange(1, 20)
        self.border_size.setValue(4)
        
        settings_layout.addWidget(QLabel("纠错级别:"), 0, 0)
        settings_layout.addWidget(self.error_correction, 0, 1)
        settings_layout.addWidget(QLabel("方块大小:"), 1, 0)
        settings_layout.addWidget(self.box_size, 1, 1)
        settings_layout.addWidget(QLabel("边框大小:"), 2, 0)
        settings_layout.addWidget(self.border_size, 2, 1)
        
        layout.addWidget(settings_group)
        
        # 生成和保存按钮
        btn_layout = QHBoxLayout()
        generate_qr_btn = QPushButton("生成二维码")
        save_qr_btn = QPushButton("保存二维码")
        save_qr_btn.setEnabled(False)
        
        generate_qr_btn.clicked.connect(self.generate_qr_code)
        save_qr_btn.clicked.connect(self.save_qr_code)
        
        btn_layout.addWidget(generate_qr_btn)
        btn_layout.addWidget(save_qr_btn)
        layout.addLayout(btn_layout)
        
        # 二维码预览
        self.qr_preview = QLabel()
        self.qr_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_preview.setStyleSheet("border: 1px solid gray; min-height: 200px;")
        self.qr_preview.setText("二维码预览将在这里显示")
        layout.addWidget(self.qr_preview)
        
        self.save_qr_btn = save_qr_btn
        self.current_qr_image = None
        
        self.tab_widget.addTab(tab, "二维码生成")

    def setup_url_test_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # URL输入组
        input_group = QGroupBox("URL列表")
        input_layout = QVBoxLayout(input_group)
        
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("输入要测试的URL，每行一个:\nhttp://www.example.com\nhttps://www.google.com")
        self.url_input.setMaximumHeight(120)
        input_layout.addWidget(self.url_input)
        
        # 设置
        settings_layout = QHBoxLayout()
        self.url_timeout = QSpinBox()
        self.url_timeout.setRange(1, 60)
        self.url_timeout.setValue(5)
        self.url_timeout.setSuffix(" 秒")
        
        settings_layout.addWidget(QLabel("超时时间:"))
        settings_layout.addWidget(self.url_timeout)
        settings_layout.addStretch()
        
        test_btn = QPushButton("开始测试")
        test_btn.clicked.connect(self.test_urls)
        settings_layout.addWidget(test_btn)
        
        input_layout.addLayout(settings_layout)
        layout.addWidget(input_group)
        
        # 结果表格
        self.url_result_table = QTableWidget()
        self.url_result_table.setColumnCount(5)
        self.url_result_table.setHorizontalHeaderLabels(["URL", "状态码", "响应时间", "最终URL", "错误"])
        self.url_result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.url_result_table)
        
        self.tab_widget.addTab(tab, "URL测试")

    def setup_port_scan_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 扫描设置组
        settings_group = QGroupBox("扫描设置")
        settings_layout = QGridLayout(settings_group)
        
        self.scan_host = QLineEdit()
        self.scan_host.setText("127.0.0.1")
        self.scan_host.setPlaceholderText("目标主机IP或域名")
        
        self.start_port = QSpinBox()
        self.start_port.setRange(1, 65535)
        self.start_port.setValue(1)
        
        self.end_port = QSpinBox()
        self.end_port.setRange(1, 65535)
        self.end_port.setValue(1000)
        
        self.scan_timeout = QSpinBox()
        self.scan_timeout.setRange(1, 10)
        self.scan_timeout.setValue(1)
        
        settings_layout.addWidget(QLabel("目标主机:"), 0, 0)
        settings_layout.addWidget(self.scan_host, 0, 1)
        settings_layout.addWidget(QLabel("起始端口:"), 1, 0)
        settings_layout.addWidget(self.start_port, 1, 1)
        settings_layout.addWidget(QLabel("结束端口:"), 2, 0)
        settings_layout.addWidget(self.end_port, 2, 1)
        settings_layout.addWidget(QLabel("超时(秒):"), 3, 0)
        settings_layout.addWidget(self.scan_timeout, 3, 1)
        
        scan_btn = QPushButton("开始扫描")
        scan_btn.clicked.connect(self.scan_ports)
        settings_layout.addWidget(scan_btn, 4, 0, 1, 2)
        
        layout.addWidget(settings_group)
        
        # 结果表格
        self.port_result_table = QTableWidget()
        self.port_result_table.setColumnCount(3)
        self.port_result_table.setHorizontalHeaderLabels(["端口", "状态", "服务"])
        self.port_result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.port_result_table)
        
        self.tab_widget.addTab(tab, "端口扫描")

    def setup_http_server_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 服务器设置组
        server_group = QGroupBox("HTTP服务器设置")
        server_layout = QGridLayout(server_group)
        
        self.server_dir_label = QLabel("未选择目录")
        select_dir_btn = QPushButton("选择目录")
        select_dir_btn.clicked.connect(self.select_server_directory)
        
        self.server_port = QSpinBox()
        self.server_port.setRange(1000, 65535)
        self.server_port.setValue(8000)
        
        server_layout.addWidget(QLabel("共享目录:"), 0, 0)
        server_layout.addWidget(self.server_dir_label, 0, 1)
        server_layout.addWidget(select_dir_btn, 0, 2)
        server_layout.addWidget(QLabel("端口:"), 1, 0)
        server_layout.addWidget(self.server_port, 1, 1)
        
        layout.addWidget(server_group)
        
        # 服务器控制
        control_layout = QHBoxLayout()
        self.start_server_btn = QPushButton("启动服务器")
        self.stop_server_btn = QPushButton("停止服务器")
        self.stop_server_btn.setEnabled(False)
        
        self.start_server_btn.clicked.connect(self.start_http_server)
        self.stop_server_btn.clicked.connect(self.stop_http_server)
        
        control_layout.addWidget(self.start_server_btn)
        control_layout.addWidget(self.stop_server_btn)
        layout.addLayout(control_layout)
        
        # 服务器状态
        self.server_status = QTextEdit()
        self.server_status.setReadOnly(True)
        self.server_status.setMaximumHeight(200)
        layout.addWidget(self.server_status)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "HTTP服务器")

    def setup_network_diag_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 诊断工具组
        tools_group = QGroupBox("网络诊断工具")
        tools_layout = QGridLayout(tools_group)
        
        self.diag_host = QLineEdit()
        self.diag_host.setText("www.baidu.com")
        self.diag_host.setPlaceholderText("目标主机")
        
        ping_btn = QPushButton("Ping测试")
        trace_btn = QPushButton("路由跟踪") 
        internet_btn = QPushButton("网络连接测试")
        netinfo_btn = QPushButton("获取网络信息")
        
        ping_btn.clicked.connect(self.ping_host)
        trace_btn.clicked.connect(self.trace_route)
        internet_btn.clicked.connect(self.check_internet)
        netinfo_btn.clicked.connect(self.get_network_info)
        
        tools_layout.addWidget(QLabel("目标主机:"), 0, 0)
        tools_layout.addWidget(self.diag_host, 0, 1, 1, 2)
        tools_layout.addWidget(ping_btn, 1, 0)
        tools_layout.addWidget(trace_btn, 1, 1)
        tools_layout.addWidget(internet_btn, 2, 0)
        tools_layout.addWidget(netinfo_btn, 2, 1)
        
        layout.addWidget(tools_group)
        
        # 结果显示
        self.diag_result = QTextEdit()
        self.diag_result.setReadOnly(True)
        layout.addWidget(self.diag_result)
        
        self.tab_widget.addTab(tab, "网络诊断")

    def generate_qr_code(self):
        text = self.qr_text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "错误", "请输入要生成二维码的内容")
            return
        
        # 获取纠错级别
        error_level = self.error_correction.currentText().split()[0]
        
        self.worker = NetworkWorker(
            "generate_qr",
            text=text,
            error_correction=error_level,
            box_size=self.box_size.value(),
            border=self.border_size.value()
        )
        self.worker.finished.connect(self.on_qr_generated)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def test_urls(self):
        url_text = self.url_input.toPlainText().strip()
        if not url_text:
            QMessageBox.warning(self, "错误", "请输入要测试的URL")
            return
        
        urls = [line.strip() for line in url_text.split('\n') if line.strip()]
        
        self.worker = NetworkWorker(
            "test_urls",
            urls=urls,
            timeout=self.url_timeout.value()
        )
        self.worker.finished.connect(self.on_urls_tested)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def scan_ports(self):
        host = self.scan_host.text().strip()
        if not host:
            QMessageBox.warning(self, "错误", "请输入目标主机")
            return
        
        start = self.start_port.value()
        end = self.end_port.value()
        
        if start > end:
            QMessageBox.warning(self, "错误", "起始端口不能大于结束端口")
            return
        
        if end - start > 10000:
            reply = QMessageBox.question(
                self, "确认扫描", 
                f"将扫描 {end - start + 1} 个端口，这可能需要较长时间。是否继续？"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.worker = NetworkWorker(
            "scan_ports",
            host=host,
            start_port=start,
            end_port=end,
            timeout=self.scan_timeout.value()
        )
        self.worker.finished.connect(self.on_ports_scanned)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def select_server_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择要共享的目录")
        if directory:
            self.server_directory = directory
            self.server_dir_label.setText(directory)

    def start_http_server(self):
        if not hasattr(self, 'server_directory'):
            QMessageBox.warning(self, "错误", "请先选择要共享的目录")
            return
        
        self.worker = NetworkWorker(
            "start_server",
            directory=self.server_directory,
            port=self.server_port.value()
        )
        self.worker.finished.connect(self.on_server_started)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def stop_http_server(self):
        if hasattr(self, 'http_server') and self.http_server:
            result, error = self.http_server.stop()
            if error:
                QMessageBox.critical(self, "错误", f"停止服务器失败: {error}")
            else:
                self.server_status.append("服务器已停止")
                self.start_server_btn.setEnabled(True)
                self.stop_server_btn.setEnabled(False)
                self.http_server = None

    def ping_host(self):
        host = self.diag_host.text().strip()
        if not host:
            QMessageBox.warning(self, "错误", "请输入目标主机")
            return
        
        self.worker = NetworkWorker("ping_host", host=host, count=4)
        self.worker.finished.connect(self.on_diag_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def trace_route(self):
        host = self.diag_host.text().strip()
        if not host:
            QMessageBox.warning(self, "错误", "请输入目标主机")
            return
        
        self.worker = NetworkWorker("trace_route", host=host)
        self.worker.finished.connect(self.on_diag_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def check_internet(self):
        self.worker = NetworkWorker("check_internet")
        self.worker.finished.connect(self.on_diag_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def get_network_info(self):
        self.worker = NetworkWorker("get_network_info")
        self.worker.finished.connect(self.on_diag_finished)
        self.worker.status.connect(self.status_label.setText)
        self.worker.start()

    def save_qr_code(self):
        if not self.current_qr_image:
            QMessageBox.warning(self, "错误", "没有可保存的二维码")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存二维码", "qrcode.png",
            "PNG文件 (*.png);;JPEG文件 (*.jpg);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self.current_qr_image.save(file_path)
                QMessageBox.information(self, "成功", f"二维码已保存到: {file_path}")
                self.operation_successful.emit()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    @pyqtSlot(object, str)
    def on_qr_generated(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"生成二维码失败: {error}")
        else:
            # 将PIL图像转换为QPixmap显示
            self.current_qr_image = result
            
            # 转换为字节流
            byte_array = BytesIO()
            result.save(byte_array, format='PNG')
            byte_array.seek(0)
            
            # 创建QPixmap并缩放显示
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array.getvalue())
            
            # 缩放以适应预览区域
            scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.qr_preview.setPixmap(scaled_pixmap)
            self.save_qr_btn.setEnabled(True)
            
            QMessageBox.information(self, "成功", "二维码生成完成!")
        
        self.status_label.setText("就绪")

    @pyqtSlot(object, str)
    def on_urls_tested(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"URL测试失败: {error}")
        else:
            # 清空表格并填充结果
            self.url_result_table.setRowCount(len(result))
            
            for i, url_result in enumerate(result):
                self.url_result_table.setItem(i, 0, QTableWidgetItem(url_result['original_url']))
                self.url_result_table.setItem(i, 1, QTableWidgetItem(str(url_result['status_code']) if url_result['status_code'] else "失败"))
                self.url_result_table.setItem(i, 2, QTableWidgetItem(f"{url_result['response_time']}ms" if url_result['response_time'] else "N/A"))
                self.url_result_table.setItem(i, 3, QTableWidgetItem(url_result['final_url']))
                self.url_result_table.setItem(i, 4, QTableWidgetItem(url_result['error'] or ""))
            
            success_count = len([r for r in result if r['status'] == 'success'])
            QMessageBox.information(self, "完成", f"测试完成! 成功: {success_count}/{len(result)}")
            self.operation_successful.emit()
        
        self.status_label.setText("就绪")

    @pyqtSlot(object, str)
    def on_ports_scanned(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"端口扫描失败: {error}")
        else:
            # 清空表格并填充结果
            open_ports = result['open_ports']
            self.port_result_table.setRowCount(len(open_ports))
            
            for i, port_info in enumerate(open_ports):
                self.port_result_table.setItem(i, 0, QTableWidgetItem(str(port_info['port'])))
                self.port_result_table.setItem(i, 1, QTableWidgetItem(port_info['status']))
                self.port_result_table.setItem(i, 2, QTableWidgetItem(port_info['service']))
            
            QMessageBox.information(
                self, "完成", 
                f"扫描完成!\n主机: {result['host']}\n开放端口: {len(open_ports)}\n扫描端口总数: {result['total_scanned']}"
            )
            self.operation_successful.emit()
        
        self.status_label.setText("就绪")

    @pyqtSlot(object, str)
    def on_server_started(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"启动服务器失败: {error}")
        else:
            self.http_server = self.worker.server
            self.server_status.append(f"服务器已启动: {result}")
            self.server_status.append(f"共享目录: {self.server_directory}")
            self.start_server_btn.setEnabled(False)
            self.stop_server_btn.setEnabled(True)
            
            QMessageBox.information(self, "成功", f"HTTP服务器已启动!\n访问地址: {result}")
            self.operation_successful.emit()
        
        self.status_label.setText("就绪")

    @pyqtSlot(object, str)
    def on_diag_finished(self, result, error):
        if error:
            QMessageBox.critical(self, "错误", f"网络诊断失败: {error}")
        else:
            # 格式化显示结果
            if 'host' in result and 'output' in result:
                # Ping或路由跟踪结果
                self.diag_result.append(f"=== {result.get('host', '')} ===")
                if result.get('success'):
                    self.diag_result.append(result['output'])
                    if 'packet_loss' in result and result['packet_loss'] is not None:
                        self.diag_result.append(f"丢包率: {result['packet_loss']}%")
                else:
                    self.diag_result.append(f"失败: {result.get('error', '未知错误')}")
            elif 'connected' in result:
                # 网络连接测试结果
                if result['connected']:
                    self.diag_result.append(f"✓ 网络连接正常 (通过 {result['host']})")
                else:
                    self.diag_result.append("✗ 网络连接异常")
            elif 'interfaces' in result or 'basic_info' in result:
                # 网络信息
                self.diag_result.append("=== 网络信息 ===")
                if 'interfaces' in result:
                    for name, info in result['interfaces'].items():
                        self.diag_result.append(f"\n接口: {name}")
                        for addr in info['addresses']:
                            self.diag_result.append(f"  {addr['type']}: {addr['address']}")
                        if info['stats'] and info['stats']['is_up']:
                            self.diag_result.append(f"  状态: 启用")
                            if info['stats']['speed'] > 0:
                                self.diag_result.append(f"  速度: {info['stats']['speed']} Mbps")
                elif 'basic_info' in result:
                    basic = result['basic_info']
                    self.diag_result.append(f"主机名: {basic['hostname']}")
                    self.diag_result.append(f"本地IP: {basic['local_ip']}")
            
            self.diag_result.append("")  # 添加空行
            self.operation_successful.emit()
        
        self.status_label.setText("就绪")