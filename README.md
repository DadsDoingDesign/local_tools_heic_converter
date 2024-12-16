# Local Tools: HEIC Converter

A modern, user-friendly desktop application for converting HEIC/HEIF images to JPG or PNG format. Built with Python and PyQt6, this tool provides an intuitive interface for batch converting images while maintaining high quality.

![Local Tools HEIC Converter Screenshot](docs/screenshot.png)

## Features

- 🖼️ Modern, intuitive graphical user interface
- 📁 Drag & drop support for files and folders
- 🔄 Batch conversion of multiple files
- 📊 Individual progress tracking for each file
- 🎨 Choice of JPG or PNG output format
- 📂 Optional subfolder creation for converted files
- 🌓 Automatic dark/light mode support
- 🎯 High-quality conversion (95% quality for JPG)
- ⚡ Optimized output files
- ❌ Comprehensive error handling and status reporting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dadsdoingdesign/local_tools_heic_converter.git
cd local_tools_heic_converter
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Version (Recommended)
```bash
python -m local_tools_heic_converter.gui
```

1. Launch the application
2. Drag & drop HEIC files into the window, or click to browse
3. Select your desired output format (JPG or PNG)
4. Choose whether to create a subfolder for converted files
5. Click "Convert" to start the process
6. Monitor progress for each file
7. Access converted files in the output folder (opens automatically when complete)

### Command Line Version
```bash
python -m local_tools_heic_converter.cli path/to/directory
```

Additional command-line options:
- `--format png` - Convert to PNG instead of JPG
- `--output path/to/output` - Specify output directory

## Development

### Project Structure
```
local_tools_heic_converter/
├── local_tools_heic_converter/
│   ├── __init__.py
│   ├── gui.py           # Main GUI application
│   └── cli.py           # Command-line interface
├── requirements.txt      # Python dependencies
├── docs/                # Documentation
│   └── screenshot.png   # Application screenshot
└── README.md           # Project documentation
```

### Requirements
- Python 3.8+
- PyQt6
- Pillow
- pillow-heif
- darkdetect
- qt-material

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- HEIC support provided by [pillow-heif](https://github.com/bigcat88/pillow_heif)
- Material design theme by [qt-material](https://github.com/UN-GCPDS/qt-material)
- Created with [Windsurf Editor](https://www.codeium.com/windsurf)

## Authors

- **Denis Dukhvalov** - [dadsdoingdesign](https://github.com/dadsdoingdesign)
- Created with [Windsurf Editor](https://www.codeium.com/windsurf)
