import requests
import semver
import os
import subprocess
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread

GITHUB_REPO = "jdassd/python_pc_tools"  # 需要替换为实际的仓库地址

def check_for_updates(current_version):
    """
    检查GitHub上是否有新版本。
    """
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        latest_release = response.json()
        latest_version = latest_release["tag_name"].lstrip('v')
        
        if semver.compare(latest_version, current_version) > 0:
            return latest_release
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"检查更新失败: {e}")
    return None

class UpdateDownloader(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, download_url, file_name):
        super().__init__()
        self.download_url = download_url
        self.file_name = file_name
        self._is_canceled = False

    def run(self):
        try:
            response = requests.get(self.download_url, stream=True, timeout=60)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            download_path = os.path.join(os.getcwd(), self.file_name)
            
            with open(download_path, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if self._is_canceled:
                        return
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress_value = int((downloaded_size / total_size) * 100) if total_size > 0 else 0
                    self.progress.emit(progress_value)
            
            if not self._is_canceled:
                self.finished.emit(download_path)

        except requests.RequestException as e:
            if not self._is_canceled:
                self.error.emit(f"下载更新失败: {e}")
    
    def cancel(self):
        self._is_canceled = True

def download_and_install_update(release_info, parent=None):
    """
    下载并安装更新（支持压缩包与安装器）。
    """
    assets = release_info.get('assets', [])
    if not assets:
        QMessageBox.information(parent, "无可用更新包", "发布版本未提供可下载的更新资产。")
        return

    # 优先选择压缩包，其次安装器，最后回退第一个资产
    selected = None
    for a in assets:
        name = a.get('name', '').lower()
        if name.endswith(('.zip', '.tar.gz', '.tar', '.tgz')):
            selected = a
            break
    if not selected:
        for a in assets:
            name = a.get('name', '').lower()
            if name.endswith('.exe'):
                selected = a
                break
    if not selected:
        selected = assets[0]

    download_url = selected['browser_download_url']
    file_name = selected['name']

    reply = QMessageBox.question(
        parent,
        '发现新版本',
        f"发现新版本 {release_info.get('tag_name', '')}。\n\n更新日志:\n{release_info.get('body', '')}\n\n是否立即下载并更新？",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
        progress_dialog = QProgressDialog("正在下载更新...", "取消", 0, 100, parent)
        progress_dialog.setWindowTitle("多功能工具箱")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)

        thread = QThread()
        downloader = UpdateDownloader(download_url, file_name)
        downloader.moveToThread(thread)

        def on_finish(path):
            progress_dialog.setValue(100)
            progress_dialog.close()
            thread.quit()
            create_update_script(path)

        def on_error(msg):
            QMessageBox.critical(parent, "下载失败", msg)
            progress_dialog.close()
            thread.quit()

        def on_cancel():
            downloader.cancel()
            progress_dialog.close()
            thread.quit()

        downloader.progress.connect(progress_dialog.setValue)
        downloader.finished.connect(on_finish)
        downloader.error.connect(on_error)
        progress_dialog.canceled.connect(on_cancel)

        thread.started.connect(downloader.run)
        thread.finished.connect(downloader.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()
        progress_dialog.exec()

def create_update_script(download_path):
    """
    创建并执行用于安装更新的批处理脚本：
    - 压缩包：解压替换后重启应用
    - 安装器(.exe)：直接启动安装器
    """
    lower = download_path.lower()
    is_archive = lower.endswith(('.zip', '.tar', '.tgz')) or lower.endswith('.tar.gz')
    is_installer = lower.endswith('.exe')

    if is_installer:
        script_content = f"""
@echo off
chcp 65001 > NUL
echo 正在准备安装，请稍候...
timeout /t 2 /nobreak > NUL

echo 正在关闭当前应用...
taskkill /f /im 工具箱.exe > NUL

echo 正在启动安装程序...
start "" "{download_path}"

echo 安装程序已启动，本程序将退出。
del "%~f0"
"""
    else:
        # 归档包使用 tar 解压（Windows 10+ 内置 bsdtar 兼容 zip/tar）
        script_content = f"""
@echo off
chcp 65001 > NUL
echo 正在准备更新，请稍候...
timeout /t 2 /nobreak > NUL

echo 正在关闭当前应用...
taskkill /f /im 工具箱.exe > NUL

echo 正在解压并替换文件...
tar -xf "{download_path}" -C "."

echo 清理临时文件...
del "{download_path}"

echo 更新完成，正在重启应用...
start "" "工具箱.exe"

del "%~f0"
"""

    script_path = os.path.join(os.getcwd(), "update.bat")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    subprocess.Popen(f'cmd /c "{script_path}"', shell=True)
    QApplication.quit()
