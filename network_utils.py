import socket
import threading
import time
import requests
import qrcode
from io import BytesIO
import http.server
import socketserver
from urllib.parse import urlparse
import json
import re

def generate_qr_code(text, error_correction='M', box_size=10, border=4):
    """生成二维码"""
    try:
        # 错误纠正级别映射
        error_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M, 
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=box_size,
            border=border,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # 生成PIL图像
        img = qr.make_image(fill_color="black", back_color="white")
        return img, None
        
    except Exception as e:
        return None, str(e)

def test_urls_batch(urls, timeout=5):
    """批量测试URL有效性"""
    try:
        results = []
        
        for url in urls:
            url = url.strip()
            if not url:
                continue
                
            # 确保URL有协议
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            try:
                response = requests.get(url, timeout=timeout, allow_redirects=True)
                status = response.status_code
                response_time = response.elapsed.total_seconds()
                final_url = response.url
                
                result = {
                    'original_url': url,
                    'final_url': final_url,
                    'status_code': status,
                    'status': 'success' if 200 <= status < 400 else 'error',
                    'response_time': round(response_time * 1000, 2),  # 毫秒
                    'error': None
                }
                
            except requests.RequestException as e:
                result = {
                    'original_url': url,
                    'final_url': url,
                    'status_code': None,
                    'status': 'failed',
                    'response_time': None,
                    'error': str(e)
                }
            
            results.append(result)
        
        return results, None
        
    except Exception as e:
        return None, str(e)

def scan_ports(host, start_port, end_port, timeout=1):
    """端口扫描"""
    try:
        open_ports = []
        closed_ports = []
        
        for port in range(start_port, end_port + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            try:
                result = sock.connect_ex((host, port))
                if result == 0:
                    # 尝试获取服务信息
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                    
                    open_ports.append({
                        'port': port,
                        'service': service,
                        'status': 'open'
                    })
                else:
                    closed_ports.append(port)
                    
            except Exception:
                closed_ports.append(port)
            finally:
                sock.close()
        
        return {
            'host': host,
            'open_ports': open_ports,
            'closed_count': len(closed_ports),
            'total_scanned': end_port - start_port + 1
        }, None
        
    except Exception as e:
        return None, str(e)

class SimpleHTTPServer:
    """简单HTTP服务器"""
    
    def __init__(self, directory, port=8000):
        self.directory = directory
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        try:
            from functools import partial

            # 使用 partial 绑定目录，避免全局 chdir，且不在 handler 中错误引用 self
            handler = partial(http.server.SimpleHTTPRequestHandler, directory=self.directory)

            class ReusableTCPServer(socketserver.TCPServer):
                allow_reuse_address = True

            self.server = ReusableTCPServer(("", self.port), handler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.running = True

            return f"http://localhost:{self.port}", None

        except Exception as e:
            return None, str(e)
    
    def stop(self):
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                self.running = False
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2)
            self.server = None
            self.server_thread = None
            return True, None
        except Exception as e:
            return False, str(e)

def ping_host(host, count=4):
    """Ping主机"""
    try:
        import subprocess
        import platform
        
        # 根据操作系统选择ping命令
        if platform.system().lower() == 'windows':
            cmd = ['ping', '-n', str(count), host]
        else:
            cmd = ['ping', '-c', str(count), host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        ping_result = {
            'host': host,
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }
        
        # 解析ping结果获取统计信息
        if ping_result['success']:
            output = result.stdout
            # 简单的统计解析（可以根据需要更详细）
            if 'packets transmitted' in output:
                ping_result['packet_loss'] = extract_packet_loss(output)
            elif '数据包' in output:  # 中文Windows
                ping_result['packet_loss'] = extract_packet_loss_zh(output)
        
        return ping_result, None
        
    except Exception as e:
        return None, str(e)

def extract_packet_loss(output):
    """从ping输出中提取丢包率"""
    try:
        # 匹配类似 "4 packets transmitted, 4 received, 0% packet loss"
        match = re.search(r'(\d+)% packet loss', output)
        if match:
            return int(match.group(1))
        return None
    except:
        return None

def extract_packet_loss_zh(output):
    """从中文ping输出中提取丢包率"""
    try:
        # 匹配中文Windows ping输出
        if '丢失' in output:
            match = re.search(r'丢失 = (\d+)', output)
            if match:
                lost = int(match.group(1))
                # 简单计算丢包率
                return (lost * 100) // 4  # 假设发送了4个包
        return 0
    except:
        return None

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 连接到一个远程地址来获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip, None
    except Exception as e:
        return None, str(e)

def check_internet_connection():
    """检查网络连接"""
    try:
        # 尝试连接到几个知名的DNS服务器
        test_hosts = [
            ("8.8.8.8", 53),      # Google DNS
            ("1.1.1.1", 53),      # Cloudflare DNS  
            ("114.114.114.114", 53) # 114 DNS
        ]
        
        for host, port in test_hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    return {'connected': True, 'host': host}, None
            except:
                continue
        
        return {'connected': False, 'host': None}, None
        
    except Exception as e:
        return None, str(e)

def trace_route(host, max_hops=30):
    """路由跟踪"""
    try:
        import subprocess
        import platform
        
        # 根据操作系统选择traceroute命令
        if platform.system().lower() == 'windows':
            cmd = ['tracert', '-h', str(max_hops), host]
        else:
            cmd = ['traceroute', '-m', str(max_hops), host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        return {
            'host': host,
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }, None
        
    except Exception as e:
        return None, str(e)

def get_network_info():
    """获取网络信息"""
    try:
        import psutil
        
        # 获取网络接口信息
        interfaces = {}
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            interface_info = {
                'addresses': [],
                'stats': None
            }
            
            for addr in interface_addresses:
                if addr.family == socket.AF_INET:  # IPv4
                    interface_info['addresses'].append({
                        'type': 'IPv4',
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                elif addr.family == socket.AF_INET6:  # IPv6
                    interface_info['addresses'].append({
                        'type': 'IPv6', 
                        'address': addr.address,
                        'netmask': addr.netmask
                    })
            
            # 获取接口统计信息
            try:
                stats = psutil.net_if_stats()[interface_name]
                interface_info['stats'] = {
                    'is_up': stats.isup,
                    'duplex': stats.duplex,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                }
            except:
                pass
            
            interfaces[interface_name] = interface_info
        
        # 获取网络IO统计
        net_io = psutil.net_io_counters()
        io_stats = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }
        
        return {
            'interfaces': interfaces,
            'io_stats': io_stats
        }, None
        
    except Exception as e:
        # 如果psutil不可用，返回基本信息
        try:
            local_ip, _ = get_local_ip()
            hostname = socket.gethostname()
            
            return {
                'basic_info': {
                    'hostname': hostname,
                    'local_ip': local_ip
                }
            }, None
        except Exception as e2:
            return None, str(e2)