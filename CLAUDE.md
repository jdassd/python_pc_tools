# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based multi-functional desktop application (多功能工具箱) that provides comprehensive file processing tools for PDF, image, audio, video files, plus text processing, system utilities, network tools, and mouse automation features. The application uses a modular window-based architecture with separate utility modules for each tool category.

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
- **main.py**: Main entry point with adaptive grid layout and tool launcher (supports up to 8 tool categories)
- **utils.py**: Resource path utilities for PyInstaller compatibility
- **styles.qss**: Qt stylesheet for application theming

### Window Modules (UI Layer)
Each tool category has a dedicated window module:
- `pdf_window.py` - PDF processing interface
- `image_window.py` - Image editing interface  
- `audio_window.py` - Audio manipulation interface
- `video_window.py` - Video processing interface
- `mouse_window.py` - Mouse automation controls
- `text_window.py` - Text processing and analysis interface
- `system_window.py` - System utilities interface
- `network_window.py` - Network tools interface

### Utility Modules (Business Logic)
Each tool type has corresponding utility functions:
- `pdf_utils.py` - PDF operations (convert, merge, split, compress)
- `image_utils.py` - Enhanced image processing (format conversion, compression, cropping, watermarks, EXIF reading, batch processing, filters, rotation/flip, image concatenation)
- `audio_utils.py` - Audio manipulation (format conversion, editing, volume control)
- `video_utils.py` - Video processing (format conversion, editing, compression)
- `mouse_utils.py` - Mouse automation and hotkey handling with dynamic coordinate support
- `text_utils.py` - Text processing (encoding conversion, find/replace, split/merge, analysis)
- `system_utils.py` - System utilities (duplicate file finder, batch rename, directory comparison, system cleanup)
- `network_utils.py` - Network tools (QR code generation, URL testing, port scanning, HTTP server, network diagnostics)
- `zip_utils.py` - Archive file operations

### Application Management
- **update_manager.py**: GitHub release checking and auto-update functionality
- **main.spec**: PyInstaller configuration including resource bundling

## Key Libraries & Dependencies

### Core Framework
- **PyQt6**: GUI framework with tabbed interfaces and threaded operations

### File Processing
- **PyMuPDF, pdf2docx, python-docx**: PDF processing
- **Pillow**: Enhanced image manipulation with EXIF support
- **pydub**: Audio processing
- **moviepy**: Video processing

### System & Network
- **psutil**: System information and process management
- **requests**: HTTP requests for URL testing and updates
- **qrcode[pil]**: QR code generation with PIL support
- **pynput**: Mouse/keyboard automation
- **semver**: Version comparison for updates

## New Features Added

### Text Processing Tools
- **Encoding Conversion**: Convert between UTF-8, GBK, GB2312, ASCII, UTF-16
- **Batch Find/Replace**: Support for regex and case-sensitive operations
- **Text Split/Merge**: Split by lines, characters, or delimiters; merge multiple files
- **Text Analysis**: Character/word count, frequency analysis, statistics

### System Tools
- **Duplicate File Finder**: MD5-based duplicate detection with subdirectory support
- **Batch File Rename**: Pattern-based and sequence-based renaming
- **Directory Comparison**: Compare files and content between directories
- **System Cleanup**: Empty folder removal and temp file cleaning

### Network Tools
- **QR Code Generator**: Customizable QR codes with different error correction levels
- **URL Batch Testing**: Test multiple URLs with response time and status tracking
- **Port Scanner**: Scan port ranges with service identification
- **HTTP File Server**: Share directories via built-in HTTP server
- **Network Diagnostics**: Ping, traceroute, network info, connection testing

### Enhanced Image Tools
- **EXIF Information Reader**: Extract and display image metadata
- **Batch Image Renaming**: Rename by creation time or custom patterns
- **Image Rotation/Flip**: 90°/180°/270° rotation and horizontal/vertical flipping
- **Image Concatenation**: Horizontal/vertical image stitching with spacing
- **Property Adjustment**: Brightness, contrast, saturation, sharpness controls
- **Filter Application**: Blur, sharpen, edge detection, grayscale, invert, emboss
- **Batch Processing**: Apply operations to entire directories

## Development Notes

### UI Architecture
- Main window expanded to 3-row grid layout for 8 tool categories
- Each tool uses tabbed interface for multiple functions
- Threaded operations prevent UI blocking during long processes
- Progress tracking and status updates for user feedback

### Threading Pattern
- Worker classes (TextProcessingWorker, SystemWorker, NetworkWorker) handle background operations
- PyQt signals/slots for thread communication
- Status updates and progress reporting during operations

### Resource Handling
- Uses `resource_path()` from utils.py for PyInstaller compatibility
- Icon resources bundled in main.spec
- All file paths handled through resource_path() for distribution

### Error Handling
- Comprehensive try/catch blocks with user-friendly error messages
- Graceful degradation when optional dependencies unavailable
- Input validation and file existence checks

### Signal/Slot Pattern
- Each tool window emits `operation_successful` signals
- Main window connects to these signals to update usage statistics
- Consistent pattern across all tool modules

### Version Management
- Current version defined as `__version__` in main.py
- Update checking compares against GitHub releases using semver
- Auto-update functionality downloads and installs new versions

## Code Conventions

- Chinese language used for UI text and user-facing messages
- Object names use camelCase for Qt stylesheet targeting
- Module separation: window classes handle UI, utils handle business logic
- Error handling with try/catch blocks and user-friendly message dialogs
- Consistent file structure: each tool has window.py and utils.py pair
- Thread-safe operations for all long-running processes