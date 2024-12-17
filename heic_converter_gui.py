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

class DropArea(QLabel):
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setText("Drag & Drop Files Here\nor Click to Browse")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed palette(mid);
                border-radius: 8px;
                padding: 20px;
            }
        """)
        self.setAcceptDrops(True)
        self.mousePressEvent = self.browse_files

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.files_dropped.emit(files)

    def browse_files(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "Image Files (*.heic *.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp)"
        )
        self.files_dropped.emit(files)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Image Converter")
        self.setMinimumSize(800, 600)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Drag & Drop Area (topmost)
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.handle_dropped_files)
        layout.addWidget(self.drop_area)

        # Settings row (horizontal layout)
        settings_layout = QHBoxLayout()
        
        # Left side - Format selection and checkboxes
        left_settings = QHBoxLayout()
        
        # Output format selection
        format_label = QLabel("Output Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPG", "PNG"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                color: white;
                padding: 5px;
                min-width: 80px;
            }
            QComboBox QAbstractItemView {
                color: white;
                background-color: #2b2b2b;
                selection-background-color: #404040;
            }
        """)
        left_settings.addWidget(format_label)
        left_settings.addWidget(self.format_combo)
        
        # Checkboxes
        self.subfolder_check = QCheckBox("Create Subfolder")
        self.auto_open_check = QCheckBox("Auto-open when done")
        left_settings.addWidget(self.subfolder_check)
        left_settings.addWidget(self.auto_open_check)
        
        # Add left settings to main settings layout
        settings_layout.addLayout(left_settings)
        
        # Add stretch to push status label to the right
        settings_layout.addStretch()
        
        # Status counter (right-aligned)
        self.status_label = QLabel("0 files detected")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 5px 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        settings_layout.addWidget(self.status_label)
        
        # Add settings layout to main layout
        layout.addLayout(settings_layout)

        # File List
        self.file_list = FileListWidget()
        layout.addWidget(self.file_list)

        # Buttons row
        button_layout = QHBoxLayout()
        
        button_style = """
            QPushButton {
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:disabled {
                background-color: transparent;
                border: 1px solid #666666;
                color: #666666;
            }
        """
        
        self.convert_button = QPushButton("Convert")
        self.convert_button.setEnabled(False)  # Disabled by default
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setStyleSheet(button_style)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_files)
        self.clear_button.setEnabled(False)  # Disabled by default
        self.clear_button.setStyleSheet(button_style)
        
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)

        # Main widget
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Initialize variables
        self.files = []
        self.worker = None
        
        # Set up drag & drop
        self.setAcceptDrops(True)

    def handle_dropped_files(self, files):
        self.files.extend(files)
        for file in files:
            self.file_list.add_file(file)
        self.convert_button.setEnabled(len(self.files) > 0)
        self.clear_button.setEnabled(len(self.files) > 0)
        self.update_status()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.add_files(files)

    def browse_files(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "Image Files (*.heic *.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp)"
        )
        self.add_files(files)

    def add_files(self, new_files):
        for file in new_files:
            if file not in self.files:
                self.files.append(file)
                self.file_list.add_file(file)
        
        self.convert_button.setEnabled(bool(self.files))
        self.update_status()

    def clear_files(self):
        self.files.clear()
        self.file_list.clear_list()
        self.convert_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.status_label.setText("0 files detected")

    def start_conversion(self):
        if not self.files:
            return

        self.worker = FileConversionWorker(
            self.files,
            self.format_combo.currentText(),
            self.subfolder_check.isChecked()
        )
        self.worker.progress.connect(self.file_list.update_progress)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.conversion_count.connect(self.update_conversion_count)
        self.worker.output_folder.connect(self.open_output_folder)
        
        self.convert_button.setText("Stop")
        self.convert_button.clicked.disconnect()
        self.convert_button.clicked.connect(self.stop_conversion)
        self.clear_button.setEnabled(False)
        
        self.worker.start()

    def stop_conversion(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.conversion_finished()

    def conversion_finished(self):
        self.convert_button.setText("Convert")
        self.convert_button.clicked.disconnect()
        self.convert_button.clicked.connect(self.start_conversion)
        self.clear_button.setEnabled(True)
        self.worker = None

    def update_conversion_count(self, completed, total):
        self.status_label.setText(f"{completed}/{total} files converted")

    def update_status(self):
        count = len(self.files)
        if count == 0:
            self.status_label.setText("0 files detected")
        else:
            self.status_label.setText(f"{count} file{'s' if count != 1 else ''} detected")

    def open_output_folder(self, folder_path):
        if self.auto_open_check.isChecked():
            try:
                os.startfile(folder_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open output folder: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Apply theme based on system
    if darkdetect.isDark():
        apply_stylesheet(app, theme='dark_teal.xml')
    else:
        apply_stylesheet(app, theme='light_teal.xml')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
