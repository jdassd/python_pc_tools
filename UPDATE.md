# 如何发布新版本并触发自动更新

本指南将说明如何通过创建 GitHub Release 来发布新版本的应用程序，并让客户端的自动更新功能正确检测和下载。

## 发布流程

### 1. 更新应用程序版本号

在发布新版本之前，最重要的一步是更新代码中的版本号。

-   打开 `main.py` 文件。
-   找到 `__version__` 变量。
-   将其更新为新的版本号（例如，从 `"1.0.0"` 更新到 `"1.1.0"`）。请遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

```python
# main.py
__version__ = "1.1.0" 
```

### 2. 打包应用程序

使用 PyInstaller 将您的应用程序打包成可执行文件。

-   在项目根目录下运行打包命令：
    ```bash
    pyinstaller main.spec
    ```
-   打包成功后，所有需要分发的文件将位于 `dist/main` 目录中。

### 3. 创建更新压缩包

自动更新机制需要一个包含所有应用程序文件的压缩包。

-   将 `dist/main` 目录下的 **所有内容** 压缩成一个文件。
-   推荐使用 `.zip` 或 `.tar.gz` 格式。
-   例如，您可以将压缩包命名为 `update-v1.1.0.zip`。

### 4. 在 GitHub 上创建 Release

这是让自动更新功能生效的关键步骤。

1.  **导航到 Releases 页面**:
    -   在您的 GitHub 仓库主页，点击右侧的 "Releases" 链接。

2.  **创建新 Release**:
    -   点击 "Draft a new release" 按钮。

3.  **填写 Release 信息**:
    -   **Tag version**: 这是最重要的字段。输入一个与您在 `main.py` 中设置的版本号完全匹配的标签，建议以 `v` 开头，例如 `v1.1.0`。`update_manager.py` 中的代码会自动去除 `v` 前缀进行比较。
    -   **Release title**: 为您的版本取一个清晰的标题，例如 `Version 1.1.0`。
    -   **Describe this release**: 在这里填写详细的更新日志。这些内容将直接显示在客户端的更新提示对话框中，所以请写得清晰明了。

4.  **上传更新包**:
    -   在 "Attach binaries by dropping them here or selecting them" 区域，上传您在第 3 步中创建的压缩包（例如 `update-v1.1.0.zip`）。

5.  **发布 Release**:
    -   检查所有信息无误后，点击 "Publish release" 按钮。

完成以上步骤后，当用户打开旧版本的应用程序时，它会自动检测到这个新的 Release，并提示用户进行更新。