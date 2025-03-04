"""
CareCopy: 一个用于复制和比较文件和目录的敏捷工具软件
A simple file copy and comparison tool that allows to copy files and directories, compare files and directories, and estimate the time it will take to copy files.
version: 1.0
"""

import os
import sys
import time
import hashlib
import shutil
from pathlib import Path
from datetime import timedelta

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                              QLineEdit, QFileDialog, QCheckBox, QVBoxLayout, 
                              QHBoxLayout, QWidget, QProgressBar, QMessageBox,
                              QTextEdit, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QSize


class CopyWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished_signal = Signal()
    error_signal = Signal(str)
    
    def __init__(self, source, destination, verify=False, continue_on_error=True):
        super().__init__()
        self.source = source
        self.destination = destination
        self.verify = verify
        self.continue_on_error = continue_on_error
        self.running = True
        self.total_files = 0
        self.copied_files = 0
        
    def run(self):
        try:
            if os.path.isfile(self.source):
                self.total_files = 1
                self._copy_file(self.source, self.destination)
            else:
                # Count total files first
                self.status.emit("Counting files...")
                self.total_files = sum(len(files) for _, _, files in os.walk(self.source))
                self.status.emit(f"Found {self.total_files} files")
                
                # Create destination if it doesn't exist
                os.makedirs(self.destination, exist_ok=True)
                
                # Copy files
                for root, dirs, files in os.walk(self.source):
                    if not self.running:
                        return
                    
                    # Create relative path structure in destination
                    rel_path = os.path.relpath(root, self.source)
                    dest_path = os.path.join(self.destination, rel_path)
                    os.makedirs(dest_path, exist_ok=True)
                    
                    for file in files:
                        if not self.running:
                            return
                        
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(dest_path, file)
                        
                        try:
                            self._copy_file(src_file, dst_file)
                        except Exception as e:
                            if self.continue_on_error:
                                self.error_signal.emit(f"Error copying {src_file}: {str(e)}")
                                continue
                            else:
                                raise
                        
            self.status.emit("Copy completed")
            self.finished_signal.emit()
            
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")
    
    def _copy_file(self, src, dst):
        filename = os.path.basename(src)
        self.status.emit(f"Copying {filename}...")
        
        # Copy the file
        shutil.copy2(src, dst)
        
        # Verify if needed
        if self.verify:
            self.status.emit(f"Verifying {filename}...")
            src_hash = self._get_file_hash(src)
            dst_hash = self._get_file_hash(dst)
            
            if src_hash != dst_hash:
                raise Exception(f"Verification failed for {filename}")
        
        self.copied_files += 1
        progress = int((self.copied_files / self.total_files) * 100)
        self.progress.emit(progress)
    
    def _get_file_hash(self, filepath):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def stop(self):
        self.running = False


class CompareWorker(QThread):
    result_signal = Signal(str)
    finished_signal = Signal()
    
    def __init__(self, source, destination):
        super().__init__()
        self.source = source
        self.destination = destination
    
    def run(self):
        try:
            if os.path.isfile(self.source):
                # Compare single file
                if not os.path.exists(self.destination):
                    self.result_signal.emit(f"Target file doesn't exist: {self.destination}")
                elif self._files_identical(self.source, self.destination):
                    self.result_signal.emit("Files are identical")
                else:
                    self.result_signal.emit("Files are different")
            else:
                # Compare directories
                results = []
                source_files = self._get_file_list(self.source)
                
                if os.path.isfile(self.destination):
                    self.result_signal.emit("Can't compare directory with file")
                    self.finished_signal.emit()
                    return
                
                dest_files = self._get_file_list(self.destination)
                
                # Files only in source
                only_in_source = source_files - dest_files
                if only_in_source:
                    results.append("Files only in source:")
                    for f in sorted(only_in_source):
                        results.append(f"  {f}")
                
                # Files only in destination
                only_in_dest = dest_files - source_files
                if only_in_dest:
                    results.append("Files only in destination:")
                    for f in sorted(only_in_dest):
                        results.append(f"  {f}")
                
                # Common files that might differ
                common = source_files & dest_files
                different = []
                
                for rel_path in sorted(common):
                    src_file = os.path.join(self.source, rel_path)
                    dst_file = os.path.join(self.destination, rel_path)
                    
                    if not self._files_identical(src_file, dst_file):
                        different.append(rel_path)
                
                if different:
                    results.append("Modified files:")
                    for f in different:
                        results.append(f"  {f}")
                
                if not only_in_source and not only_in_dest and not different:
                    results.append("Directories are identical")
                
                self.result_signal.emit("\n".join(results))
            
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit(f"Error during comparison: {str(e)}")
            self.finished_signal.emit()
    
    def _get_file_list(self, directory):
        """Get set of relative paths for all files in directory"""
        result = set()
        base_path = Path(directory)
        
        for root, _, files in os.walk(directory):
            rel_root = Path(root).relative_to(base_path)
            for file in files:
                if rel_root == Path('.'):
                    result.add(file)
                else:
                    result.add(str(rel_root / file))
        
        return result
    
    def _files_identical(self, file1, file2):
        """Check if two files have the same size and content"""
        # Quick check: compare file sizes first
        if os.path.getsize(file1) != os.path.getsize(file2):
            return False
        
        # Compare file content
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            chunk_size = 8192
            while True:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                if chunk1 != chunk2:
                    return False
                if not chunk1:  # EOF
                    return True


class EstimateWorker(QThread):
    estimated_signal = Signal(str)
    
    def __init__(self, source):
        super().__init__()
        self.source = source
    
    def run(self):
        try:
            total_size = 0
            file_count = 0
            
            if os.path.isfile(self.source):
                total_size = os.path.getsize(self.source)
                file_count = 1
            else:
                for root, _, files in os.walk(self.source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            # Rough estimate: 100MB/s copy speed
            estimated_time = total_size / (100 * 1024 * 1024)
            size_readable = self._format_size(total_size)
            
            time_str = str(timedelta(seconds=int(estimated_time)))
            self.estimated_signal.emit(f"Files: {file_count}\nSize: {size_readable}\nEstimated time: {time_str}")
            
        except Exception as e:
            self.estimated_signal.emit(f"Error estimating: {str(e)}")
    
    def _format_size(self, size_bytes):
        """Format file size in a human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.2f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"


class CareCopyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Care Copy: A simple tool to copy and compare files and directories.")
        self.setMinimumSize(700, 500)
        
        # Main layout setup
        main_layout = QVBoxLayout()
        
        # Source selection section
        source_layout = QHBoxLayout()
        source_label = QLabel("Source:")
        self.source_edit = QLineEdit()
        source_browse_file_btn = QPushButton("File...")
        source_browse_file_btn.clicked.connect(self._browse_source_file)
        source_browse_dir_btn = QPushButton("Directory...")
        source_browse_dir_btn.clicked.connect(self._browse_source_dir)
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit, 1)
        source_layout.addWidget(source_browse_file_btn)
        source_layout.addWidget(source_browse_dir_btn)
        main_layout.addLayout(source_layout)
        
        # Destination selection section
        dest_layout = QHBoxLayout()
        dest_label = QLabel("Destination:")
        self.dest_edit = QLineEdit()
        dest_browse_btn = QPushButton("Browse...")
        dest_browse_btn.clicked.connect(self._browse_destination)
        dest_layout.addWidget(dest_label)
        dest_layout.addWidget(self.dest_edit, 1)
        dest_layout.addWidget(dest_browse_btn)
        main_layout.addLayout(dest_layout)
        
        # Options section
        options_layout = QHBoxLayout()
        self.continue_cb = QCheckBox("Continue on error")
        self.continue_cb.setChecked(True)
        self.verify_cb = QCheckBox("Verify copied files")
        self.estimate_cb = QCheckBox("Estimate time")
        options_layout.addWidget(self.continue_cb)
        options_layout.addWidget(self.verify_cb)
        options_layout.addWidget(self.estimate_cb)
        main_layout.addLayout(options_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self._start_copy)
        self.compare_btn = QPushButton("Compare")
        self.compare_btn.clicked.connect(self._compare)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel)
        self.cancel_btn.setEnabled(False)
        
        self.estimate_btn = QPushButton("Estimate")
        self.estimate_btn.clicked.connect(self._estimate)
        
        action_layout.addWidget(self.copy_btn)
        action_layout.addWidget(self.compare_btn)
        action_layout.addWidget(self.estimate_btn)
        action_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(action_layout)
        
        # Progress section
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        main_layout.addLayout(progress_layout)
        
        # Log area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        main_layout.addWidget(self.log_text, 1)
        
        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Worker thread references
        self.copy_worker = None
        self.compare_worker = None
        self.estimate_worker = None
    
    def _browse_source_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Source File")
        if path:
            self.source_edit.setText(path)
    
    def _browse_source_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if path:
            self.source_edit.setText(path)
    
    def _browse_destination(self):
        path = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if path:
            self.dest_edit.setText(path)
    
    def _start_copy(self):
        source = self.source_edit.text()
        destination = self.dest_edit.text()
        
        if not source or not os.path.exists(source):
            QMessageBox.warning(self, "Error", "Invalid source path")
            return
        
        if not destination:
            QMessageBox.warning(self, "Error", "Invalid destination path")
            return
        
        # Adjust destination if source is a file
        if os.path.isfile(source) and os.path.isdir(destination):
            destination = os.path.join(destination, os.path.basename(source))
        
        # Configure and start worker
        self.copy_worker = CopyWorker(
            source,
            destination,
            verify=self.verify_cb.isChecked(),
            continue_on_error=self.continue_cb.isChecked()
        )
        self.copy_worker.progress.connect(self.progress_bar.setValue)
        self.copy_worker.status.connect(self._update_status)
        self.copy_worker.error_signal.connect(self._log_error)
        self.copy_worker.finished_signal.connect(self._copy_finished)
        
        # Update UI
        self.copy_btn.setEnabled(False)
        self.compare_btn.setEnabled(False)
        self.estimate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Start the worker
        self.log_text.append("Starting copy operation...")
        self.copy_worker.start()
    
    def _compare(self):
        source = self.source_edit.text()
        destination = self.dest_edit.text()
        
        if not source or not os.path.exists(source):
            QMessageBox.warning(self, "Error", "Invalid source path")
            return
        
        if not destination or not os.path.exists(destination):
            QMessageBox.warning(self, "Error", "Invalid destination path")
            return
        
        # Configure and start worker
        self.compare_worker = CompareWorker(source, destination)
        self.compare_worker.result_signal.connect(self._display_compare_result)
        self.compare_worker.finished_signal.connect(self._compare_finished)
        
        # Update UI
        self.copy_btn.setEnabled(False)
        self.compare_btn.setEnabled(False)
        self.estimate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Start the worker
        self.log_text.append("Starting comparison...")
        self._update_status("Comparing...")
        self.compare_worker.start()
    
    def _estimate(self):
        source = self.source_edit.text()
        
        if not source or not os.path.exists(source):
            QMessageBox.warning(self, "Error", "Invalid source path")
            return
        
        # Configure and start worker
        self.estimate_worker = EstimateWorker(source)
        self.estimate_worker.estimated_signal.connect(self._display_estimate)
        
        # Update UI
        self.copy_btn.setEnabled(False)
        self.compare_btn.setEnabled(False)
        self.estimate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Start the worker
        self.log_text.append("Estimating...")
        self._update_status("Calculating estimates...")
        self.estimate_worker.start()
    
    def _cancel(self):
        if self.copy_worker and self.copy_worker.isRunning():
            self.copy_worker.stop()
            self.copy_worker.wait()
            self._update_status("Copy operation cancelled")
            self.log_text.append("Copy operation cancelled")
        
        self._reset_ui()
    
    def _update_status(self, message):
        self.status_label.setText(message)
    
    def _log_error(self, error_msg):
        self.log_text.append(f"<span style='color: red;'>{error_msg}</span>")
    
    def _copy_finished(self):
        self.log_text.append("Copy operation completed")
        self._reset_ui()
    
    def _compare_finished(self):
        self._reset_ui()
    
    def _display_compare_result(self, result):
        self.log_text.append("--- Comparison Results ---")
        self.log_text.append(result)
        self.log_text.append("-------------------------")
    
    def _display_estimate(self, estimate):
        self.log_text.append("--- Estimate ---")
        self.log_text.append(estimate)
        self.log_text.append("---------------")
        self._reset_ui()
    
    def _reset_ui(self):
        self.copy_btn.setEnabled(True)
        self.compare_btn.setEnabled(True)
        self.estimate_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._update_status("Ready")


def main():
    app = QApplication(sys.argv)
    window = CareCopyApp()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CareCopyApp()
    window.show()
    sys.exit(app.exec())