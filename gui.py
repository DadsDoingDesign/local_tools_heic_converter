#!/usr/bin/env python3
"""
Local Tools: HEIC Converter - GUI Application
A modern, user-friendly desktop application for converting HEIC/HEIF images to JPG or PNG format.

This module provides a graphical user interface built with PyQt6 for easy batch conversion
of HEIC/HEIF images while maintaining high quality and providing progress feedback.

Author: Denis Dukhvalov
Created with: Windsurf Editor
License: MIT
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, 
                           QProgressBar, QFileDialog, QScrollArea, QFrame,
                           QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PIL import Image
from pillow_heif import register_heif_opener
import darkdetect
from qt_material import apply_stylesheet

# Register HEIF opener
register_heif_opener()

class FileConversionWorker(QThread):
    progress = pyqtSignal(str, int, str)  # file_path, progress, status
    finished = pyqtSignal()
    conversion_count = pyqtSignal(int, int)  # completed, total
    output_folder = pyqtSignal(str)  # Signal to emit the output folder path

    def __init__(self, files, output_format, create_subfolder):
        super().__init__()
        self.files = files
        self.output_format = output_format
        self.create_subfolder = create_subfolder
        self.running = True
        self.completed = 0
        self.total = len(files)
        self.last_output_dir = None

    def run(self):
        for file_path in self.files:
            if not self.running:
                break

            try:
                # Update progress at start
                self.progress.emit(file_path, 0, "🔄 Starting...")
                
                # Check file type and compatibility
                input_ext = os.path.splitext(file_path)[1].lower()
                if not self._is_compatible(input_ext, self.output_format):
                    self.progress.emit(file_path, 100, f"⚠️ Warning: Converting from {input_ext} to {self.output_format} may result in quality loss")
                    continue

                # Create output directory
                output_dir = os.path.dirname(file_path)
                if self.create_subfolder:
                    output_dir = os.path.join(output_dir, f"converted_{self.output_format.lower()}")
                    os.makedirs(output_dir, exist_ok=True)
                
                self.last_output_dir = output_dir

                # Convert file
                output_path = os.path.join(
                    output_dir,
                    f"{os.path.splitext(os.path.basename(file_path))[0]}.{self.output_format.lower()}"
                )

                # Open and convert the image
                with Image.open(file_path) as img:
                    # Convert to RGB mode (removing alpha channel if present)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        img = img.convert('RGB')
                    
                    # Progress update
                    self.progress.emit(file_path, 50, "🔄 Converting...")
                    
                    # Save with appropriate quality
                    if self.output_format.lower() == 'jpg':
                        img.save(output_path, quality=95, optimize=True)
                    else:
                        img.save(output_path, optimize=True)

                self.completed += 1
                self.conversion_count.emit(self.completed, self.total)
                self.progress.emit(file_path, 100, "✅ Converted")

            except Exception as e:
                self.progress.emit(file_path, 100, f"❌ Error: {str(e)}")

        if self.last_output_dir:
            self.output_folder.emit(self.last_output_dir)
        self.finished.emit()

    def _is_compatible(self, input_ext, output_format):
        # List of supported input formats
        supported_formats = {
            '.jpg': ['jpg', 'png'],
            '.jpeg': ['jpg', 'png'],
            '.png': ['jpg', 'png'],
            '.heic': ['jpg', 'png'],
            '.bmp': ['jpg', 'png'],
            '.gif': ['jpg', 'png'],
            '.tiff': ['jpg', 'png'],
            '.webp': ['jpg', 'png']
        }
        
        return input_ext.lower() in supported_formats and output_format.lower() in supported_formats.get(input_ext.lower(), [])

    def stop(self):
        self.running = False

class FileListWidget(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setMinimumHeight(200)
        
        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setSpacing(5)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(container)
        
        # Dictionary to store progress bars
        self.progress_bars = {}

    def add_file(self, file_path):
        if file_path in self.progress_bars:
            return

        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)

        # File name label
        name_label = QLabel(os.path.basename(file_path))
        name_label.setMinimumWidth(200)
        layout.addWidget(name_label)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setTextVisible(False)
        progress_bar.setMinimumWidth(150)
        layout.addWidget(progress_bar)

        # Status label
        status_label = QLabel("🔄 Pending")
        status_label.setMinimumWidth(100)
        layout.addWidget(status_label)

        self.layout.addWidget(frame)
        self.progress_bars[file_path] = (progress_bar, status_label)

    def update_progress(self, file_path, progress, status):
        if file_path in self.progress_bars:
            progress_bar, status_label = self.progress_bars[file_path]
            progress_bar.setValue(progress)
            status_label.setText(status)

    def clear_list(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.progress_bars.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Tools: HEIC Converter")
        self.setMinimumSize(800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Status counter
        self.status_label = QLabel("Ready to convert")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Drag & Drop Area
        drop_area = QLabel("Drag & Drop Files Here\nor Click to Browse")
        drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_area.setMinimumHeight(100)
        drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed palette(mid);
                border-radius: 8px;
                padding: 20px;
            }
        """)
        drop_area.setAcceptDrops(True)
        drop_area.mousePressEvent = self.browse_files
        layout.addWidget(drop_area)

        # Options area
        options_layout = QHBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Output Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPG", "PNG"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)
        
        # Add spacer
        options_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Checkbox for creating subfolder
        self.subfolder_checkbox = QCheckBox("Create Subfolder")
        self.subfolder_checkbox.setChecked(True)
        options_layout.addWidget(self.subfolder_checkbox)
        
        # Checkbox for opening output folder
        self.open_folder_checkbox = QCheckBox("Open Output Folder")
        self.open_folder_checkbox.setChecked(True)
        options_layout.addWidget(self.open_folder_checkbox)
        
        layout.addLayout(options_layout)

        # File list
        self.file_list = FileListWidget()
        layout.addWidget(self.file_list)

        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button)

        # Initialize variables
        self.files_to_convert = []
        self.worker = None

        # Set up drag and drop
        self.setAcceptDrops(True)

        # Apply theme based on system preference
        self.apply_theme()

    def apply_theme(self):
        theme = 'dark_teal.xml' if darkdetect.isDark() else 'light_teal.xml'
        apply_stylesheet(self.app, theme=theme)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                if path.lower().endswith('.heic'):
                    files.append(path)
            elif os.path.isdir(path):
                for root, _, filenames in os.walk(path):
                    for filename in filenames:
                        if filename.lower().endswith('.heic'):
                            files.append(os.path.join(root, filename))
        
        if files:
            self.add_files(files)

    def browse_files(self, event=None):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select HEIC Files",
            "",
            "HEIC Files (*.heic);;All Files (*.*)"
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        for file in files:
            if file not in self.files_to_convert:
                self.files_to_convert.append(file)
                self.file_list.add_file(file)
        
        self.convert_button.setEnabled(bool(self.files_to_convert))
        self.update_status_label()

    def update_status_label(self):
        count = len(self.files_to_convert)
        self.status_label.setText(f"{count} file{'s' if count != 1 else ''} ready to convert")

    def start_conversion(self):
        if not self.files_to_convert:
            return

        self.convert_button.setEnabled(False)
        self.worker = FileConversionWorker(
            self.files_to_convert,
            self.format_combo.currentText(),
            self.subfolder_checkbox.isChecked()
        )
        self.worker.progress.connect(self.file_list.update_progress)
        self.worker.conversion_count.connect(self.update_conversion_count)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.output_folder.connect(self.open_output_folder)
        self.worker.start()

    def update_conversion_count(self, completed, total):
        self.status_label.setText(f"Converting: {completed}/{total} files completed")

    def conversion_finished(self):
        self.files_to_convert.clear()
        self.convert_button.setEnabled(False)
        self.status_label.setText("Conversion completed!")
        self.worker = None

    def open_output_folder(self, folder_path):
        if self.open_folder_checkbox.isChecked():
            os.startfile(folder_path)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.app = app  # Store reference to app for theme switching
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
