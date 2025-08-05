# 如何通过 GitHub Actions 自动发布新版本

本指南将说明如何通过推送一个新的 Git 标签来自动触发 GitHub Actions，从而完成应用程序的构建、打包和发布。

## 自动化发布流程

新的发布流程完全自动化，您只需要在本地完成版本更新和标签推送即可。

### 1. 更新应用程序版本号

在发布新版本之前，请先更新代码中的版本号。

-   打开 `main.py` 文件。
-   找到 `__version__` 变量。
-   将其更新为新的版本号（例如，从 `"1.1.0"` 更新到 `"1.2.0"`）。请遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

```python
# main.py
__version__ = "1.2.0" 
```

### 2. 提交并推送 Git 标签

这是触发自动化发布流程的关键步骤。

1.  **提交代码变更**:
    ```bash
    git add main.py
    git commit -m "Bump version to 1.2.0"
    ```

2.  **创建新的 Git 标签**:
    -   标签名必须以 `v` 开头，并与您在 `main.py` 中设置的版本号匹配。
    ```bash
    git tag v1.2.0
    ```

3.  **推送标签到 GitHub**:
    -   这将触发在 `.github/workflows/release.yml` 中定义的 GitHub Action。
    ```bash
    git push origin v1.2.0
    ```

### 3. 自动化处理流程

当您推送新标签后，GitHub Actions 将自动完成以下所有任务：

-   **构建应用**: 在 Windows 环境下使用 PyInstaller 打包您的应用程序。
-   **创建压缩包**: 将所有构建好的文件压缩成一个 `.tar.gz` 文件。
-   **创建 Release**: 自动在 GitHub 上创建一个新的 Release。
    -   Release 的标题和标签将根据您的 Git 标签自动生成。
    -   **重要**: 您仍然需要手动编辑这个自动创建的 Release，为其添加详细的更新日志。客户端的更新提示框会直接显示这些内容。
-   **上传附件**: 将生成的压缩包上传到 Release 作为附件。

完成以上步骤后，客户端的自动更新功能将能够检测到新版本，并提示用户进行更新。

### 4. 本地手动打包

使用命令
```
python -m PyInstaller main.spec
```