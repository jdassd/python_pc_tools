# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PyQt6-based multi-functional desktop application (多功能工具箱) that provides 13 comprehensive tool categories: PDF processing, image editing, audio/video manipulation, mouse automation, text processing, system utilities, network tools, encryption/decryption, developer tools, office productivity, media enhancement, and data analysis. The application uses a modular window-based architecture with separate utility modules for each tool category.

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
- **main.py**: Main entry point with adaptive grid layout and tool launcher (supports 13 tool categories with auto-adjusting rows)
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
- `crypto_window.py` - Encryption/decryption tools interface
- `dev_window.py` - Developer tools interface
- `office_window.py` - Office productivity tools interface
- `media_window.py` - Media enhancement tools interface
- `data_window.py` - Data analysis tools interface

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
- `crypto_utils.py` - Encryption/decryption operations (AES file encryption, hash calculation, password generation)
- `dev_utils.py` - Developer utilities (JSON/XML formatting, encoding/decoding, regex testing, color tools)
- `office_utils.py` - Office productivity (Excel processing, file monitoring, clipboard management, directory analysis)
- `media_utils.py` - Media enhancement (screenshot tools, GIF creation, barcode generation, image collages)
- `data_utils.py` - Data analysis (CSV analysis, data cleaning, log analysis, pivot tables)
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

### Encryption & Security
- **cryptography**: File and text encryption using AES and RSA

### Data Processing & Analysis
- **pandas**: Data manipulation and analysis for CSV/Excel files
- **numpy**: Numerical computing support
- **matplotlib & seaborn**: Data visualization and chart generation
- **openpyxl**: Excel file reading and writing

### Office & Productivity
- **watchdog**: File system monitoring
- **pyperclip**: Clipboard operations
- **python-barcode[images]**: Barcode generation with image support

## Complete Feature Set

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

### Encryption & Decryption Tools
- **File Encryption/Decryption**: AES encryption with password protection
- **Text Encryption/Decryption**: Secure text encoding and decoding
- **Hash Calculation**: MD5, SHA1, SHA256, SHA512 file and text hashing
- **Password Generator**: Customizable random password generation

### Developer Tools
- **JSON/XML Processing**: Format, validate, minify JSON and XML
- **Encoding/Decoding**: URL, Base64, HTML encoding and decoding
- **Regex Testing**: Test and replace with regular expressions
- **Color Tools**: RGB/HEX/HSL conversion, palette generation

### Office Productivity Tools
- **Excel Processing**: Merge, split, convert, and clean Excel files
- **Advanced Batch Rename**: Sequence, date, regex, and case-based renaming
- **File Monitoring**: Real-time directory change monitoring
- **Clipboard Management**: History tracking and content management
- **Directory Analysis**: File structure and storage analysis

### Media Enhancement Tools
- **Screenshot Tools**: Full screen, region, delayed, and annotated screenshots
- **GIF Creation**: From images, optimization, and frame extraction
- **Barcode Generation**: Multiple barcode formats with customization
- **Image Processing**: Collages, galleries, batch resizing, watermarks

### Data Analysis Tools
- **CSV Analysis**: Comprehensive data profiling with quality reports
- **Data Cleaning**: Remove duplicates, fill missing values, standardize formats
- **Data Conversion**: Multi-format conversion (CSV/Excel/JSON/HTML)
- **Log Analysis**: Pattern matching and log file insights
- **Data Pivot Tables**: Create pivot tables with custom aggregations

## Development Notes

### UI Architecture
- Main window with adaptive grid layout supporting 13 tool categories (auto-adjusts from 2 to 4 rows)
- Scrollable statistics bar for all tool usage counters
- Each tool uses tabbed interface for multiple functions
- Threaded operations prevent UI blocking during long processes
- Progress tracking and status updates for user feedback

### Threading Pattern
- Worker classes for all tools (TextProcessingWorker, SystemWorker, NetworkWorker, CryptoWorker, DataWorker, MediaWorker, OfficeWorker) handle background operations
- PyQt signals/slots for thread communication
- Status updates and progress reporting during operations
- Thread-safe data processing for large files

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
- Current version: v1.0.9 defined as `__version__` in main.py
- Update checking compares against GitHub releases using semver
- Auto-update functionality downloads and installs new versions

### New Tool Integration
- All new tools follow the same architectural pattern
- Consistent signal/slot communication for usage tracking
- Modular design allows easy addition of future tools

## Code Conventions

- Chinese language used for UI text and user-facing messages
- Object names use camelCase for Qt stylesheet targeting
- Module separation: window classes handle UI, utils handle business logic
- Error handling with try/catch blocks and user-friendly message dialogs
- Consistent file structure: each tool has window.py and utils.py pair
- Thread-safe operations for all long-running processes
- PyInstaller-optimized: All dependencies are pure Python libraries for easy single-file distribution
- Version v1.0.9 includes 13 comprehensive tool categories