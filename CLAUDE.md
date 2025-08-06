# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based multi-functional desktop application (多功能工具箱) that provides file processing tools for PDF, image, audio, and video files, plus mouse automation features. The application uses a modular window-based architecture with separate utility modules for each tool category.

## Key Commands

### Development & Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Build executable
pyinstaller main.spec
```

## Architecture

### Core Application Structure
- **main.py**: Main entry point with adaptive grid layout and tool launcher
- **utils.py**: Resource path utilities for PyInstaller compatibility
- **styles.qss**: Qt stylesheet for application theming

### Window Modules (UI Layer)
Each tool has a dedicated window module:
- `pdf_window.py` - PDF processing interface
- `image_window.py` - Image editing interface  
- `audio_window.py` - Audio manipulation interface
- `video_window.py` - Video processing interface
- `mouse_window.py` - Mouse automation controls

### Utility Modules (Business Logic)
Each tool type has corresponding utility functions:
- `pdf_utils.py` - PDF operations (convert, merge, split, compress)
- `image_utils.py` - Image processing (format conversion, compression, cropping, watermarks)
- `audio_utils.py` - Audio manipulation (format conversion, editing, volume control)
- `video_utils.py` - Video processing (format conversion, editing, compression)
- `mouse_utils.py` - Mouse automation and hotkey handling
- `zip_utils.py` - Archive file operations

### Application Management
- **update_manager.py**: GitHub release checking and auto-update functionality
- **main.spec**: PyInstaller configuration including resource bundling

## Key Libraries & Dependencies

- **PyQt6**: GUI framework
- **PyMuPDF, pdf2docx, python-docx**: PDF processing
- **Pillow**: Image manipulation  
- **pydub**: Audio processing
- **moviepy**: Video processing
- **pynput**: Mouse/keyboard automation
- **requests, semver**: Update management

## Development Notes

### Resource Handling
- Uses `resource_path()` from utils.py for PyInstaller compatibility
- Icon resources are bundled in main.spec
- All file paths must be handled through resource_path() for distribution

### UI Architecture
- Main window uses adaptive grid layout that adjusts based on window size
- Custom `AdaptiveToolButton` class provides responsive tool buttons
- Statistics tracking for usage counters across different tool types
- Thread-based update checking on startup

### Signal/Slot Pattern
- Each tool window emits `operation_successful` signals
- Main window connects to these signals to update usage statistics
- Update checking uses threaded worker with progress signals

### Version Management
- Current version defined as `__version__` in main.py
- Update checking compares against GitHub releases using semver
- Auto-update functionality downloads and installs new versions

## Code Conventions

- Chinese language used for UI text and comments
- Object names use camelCase for Qt stylesheet targeting
- Module separation: window classes handle UI, utils handle business logic
- Error handling with try/catch blocks and user-friendly message dialogs