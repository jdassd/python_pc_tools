import requests
import semver
import os
import subprocess
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt

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

def download_and_install_update(release_info):
    """
    下载并安装更新。
    """
    asset = release_info['assets'][0] # 假设第一个asset是更新包
    download_url = asset['browser_download_url']
    file_name = asset['name']
    
    reply = QMessageBox.question(None, '发现新版本', 
                                 f"发现新版本 {release_info['tag_name']}。\n\n更新日志:\n{release_info['body']}\n\n是否立即下载并更新？",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                 QMessageBox.StandardButton.No)

    if reply == QMessageBox.StandardButton.Yes:
        progress_dialog = QProgressDialog("正在下载更新...", "取消", 0, 100)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()

        try:
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            download_path = os.path.join(os.getcwd(), file_name)
            
            with open(download_path, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if progress_dialog.wasCanceled():
                        return
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress = int((downloaded_size / total_size) * 100) if total_size > 0 else 0
                    progress_dialog.setValue(progress)
            
            progress_dialog.setValue(100)
            
            # 创建并执行更新脚本
            create_update_script(download_path)
            
        except requests.RequestException as e:
            QMessageBox.critical(None, "下载失败", f"下载更新失败: {e}")

def create_update_script(download_path):
    """
    创建并执行用于安装更新的批处理脚本。
    """
    script_content = f"""
@echo off
echo "正在准备更新，请稍候..."
timeout /t 5 /nobreak > NUL

echo "正在关闭当前应用..."
taskkill /f /im 工具箱.exe > NUL

echo "正在解压并替换文件..."
tar -xf "{download_path}" -C "."

echo "清理临时文件..."
del "{download_path}"

echo "更新完成，正在重启应用..."
start "" "main.exe"

del "%~f0"
"""
    script_path = os.path.join(os.getcwd(), "update.bat")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
        
    subprocess.Popen(f'cmd /c "{script_path}"', shell=True)
    QApplication.quit()
