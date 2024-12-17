# HEIC to JPG/PNG Converter Pro

A modern, user-friendly tool to convert HEIC/HEIF images to JPG or PNG format.

## Features

- Modern, intuitive graphical user interface
- Drag & drop support for files
- Batch conversion of multiple files
- Progress tracking for each file
- Choice of JPG or PNG output format
- Optional subfolder creation for converted files
- Dark mode support (automatic based on system settings)
- High-quality conversion (95% quality for JPG)
- Error handling and status reporting

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Version (Recommended)
```bash
python heic_converter_gui.py
```

1. Launch the application
2. Drag & drop HEIC files into the window, or click to browse
3. Select your desired output format (JPG or PNG)
4. Choose whether to create a subfolder for converted files
5. Click "Convert" to start the process

### Command Line Version
```bash
python heic_converter.py path/to/directory
```

Additional command-line options:
- `--format png` - Convert to PNG instead of JPG
- `--output path/to/output` - Specify output directory

## Features

- Supports both single file and bulk conversion
- Converts to either JPG or PNG format
- Shows a progress bar for bulk conversions
- Maintains high image quality (95% quality for JPG)
- Provides error handling and conversion status
- Creates output directory if it doesn't exist
- Preserves original files
