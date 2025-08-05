# 多功能工具箱

一站式文件处理工具，支持PDF、图片、音频、视频格式转换和编辑。

![alt text](image.png)

![alt text](image-1.png)

## 功能特性

### PDF工具
- PDF转Word转换
- PDF合并与分割
- PDF压缩
- 其他PDF操作

### 图片工具
- 图片格式转换
- 图片压缩
- 图片裁剪
- 添加水印

### 音频工具
- 音频格式转换
- 音频剪辑
- 音量调节

### 视频工具
- 视频格式转换
- 视频剪辑
- 视频压缩

## 环境要求

- Python 3.7+
- PyQt6

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 打包为可执行文件

```bash
pyinstaller main.spec
```

## 技术栈

- **界面框架**: PyQt6
- **PDF处理**: PyMuPDF, pdf2docx, python-docx
- **图片处理**: Pillow
- **音频处理**: pydub
- **视频处理**: moviepy
- **更新管理**: requests, semver

## 项目结构

```
pc_tools_gemini/
├── main.py              # 主程序入口
├── pdf_window.py        # PDF工具窗口
├── image_window.py      # 图片工具窗口
├── audio_window.py      # 音频工具窗口
├── video_window.py      # 视频工具窗口
├── pdf_utils.py         # PDF处理工具
├── image_utils.py       # 图片处理工具
├── audio_utils.py       # 音频处理工具
├── video_utils.py       # 视频处理工具
├── zip_utils.py         # 压缩文件工具
├── update_manager.py    # 更新管理器
├── styles.qss          # 界面样式
├── requirements.txt     # 项目依赖
└── *.png               # 界面图标
```

## 版本信息

当前版本: v1.0.0