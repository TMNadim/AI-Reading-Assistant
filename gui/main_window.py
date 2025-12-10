"""
AI Reading Assistant - Main Window Implementation
Provides the primary GUI interface for the reading assistant application.
"""

import sys
import os
from typing import Optional, Callable
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QFileDialog, QStatusBar, QMenuBar, QMenu,
    QToolBar, QTextEdit, QListWidget, QListWidgetItem, QProgressBar,
    QMessageBox, QComboBox, QSpinBox, QCheckBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont, QKeySequence, QColor
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6.QtCore import QPointF


class WorkerThread(QThread):
    """Worker thread for background processing."""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, task: Callable, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Execute the background task."""
        try:
            self.task(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for AI Reading Assistant."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Reading Assistant")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize application state
        self.current_document = None
        self.documents = []
        self.worker_thread = None
        self.analysis_results = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Apply styling
        self.apply_styles()
    
    def setup_ui(self):
        """Setup main user interface components."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left sidebar - Document list
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Documents"))
        
        self.document_list = QListWidget()
        self.document_list.itemSelectionChanged.connect(self.on_document_selected)
        left_layout.addWidget(self.document_list)
        
        # Document controls
        doc_controls = QHBoxLayout()
        self.load_btn = QPushButton("Load Document")
        self.load_btn.clicked.connect(self.load_document)
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_document)
        doc_controls.addWidget(self.load_btn)
        doc_controls.addWidget(self.remove_btn)
        left_layout.addLayout(doc_controls)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(250)
        
        # Center - Document viewer and controls
        center_layout = QVBoxLayout()
        
        # Document display
        center_layout.addWidget(QLabel("Document Content"))
        self.document_view = QTextEdit()
        self.document_view.setReadOnly(True)
        self.document_view.setFont(QFont("Courier", 10))
        center_layout.addWidget(self.document_view)
        
        # Analysis controls
        controls_group = QGroupBox("Analysis Settings")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("Analysis Type:"), 0, 0)
        self.analysis_type = QComboBox()
        self.analysis_type.addItems([
            "Summarization",
            "Key Points Extraction",
            "Readability Analysis",
            "Sentiment Analysis",
            "Named Entity Recognition",
            "Full Analysis"
        ])
        controls_layout.addWidget(self.analysis_type, 0, 1)
        
        controls_layout.addWidget(QLabel("Summary Length:"), 1, 0)
        self.summary_length = QSpinBox()
        self.summary_length.setRange(50, 500)
        self.summary_length.setValue(150)
        self.summary_length.setSuffix(" words")
        controls_layout.addWidget(self.summary_length, 1, 1)
        
        self.highlight_key_points = QCheckBox("Highlight Key Points")
        self.highlight_key_points.setChecked(True)
        controls_layout.addWidget(self.highlight_key_points, 2, 0)
        
        self.include_sentiment = QCheckBox("Include Sentiment Analysis")
        self.include_sentiment.setChecked(True)
        controls_layout.addWidget(self.include_sentiment, 2, 1)
        
        controls_group.setLayout(controls_layout)
        center_layout.addWidget(controls_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("Analyze Document")
        self.analyze_btn.setMinimumHeight(40)
        self.analyze_btn.clicked.connect(self.analyze_document)
        self.analyze_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        
        action_layout.addWidget(self.analyze_btn)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.clear_btn)
        center_layout.addLayout(action_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        center_layout.addWidget(self.progress_bar)
        
        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        
        # Right sidebar - Analysis results
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Analysis Results"))
        
        # Results tabs
        self.results_view = QTextEdit()
        self.results_view.setReadOnly(True)
        self.results_view.setFont(QFont("Segoe UI", 9))
        right_layout.addWidget(self.results_view)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setMinimumWidth(300)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(center_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(splitter)
    
    def setup_menu_bar(self):
        """Setup application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Document", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.load_document)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export Results", self)
        export_action.setShortcut(QKeySequence.StandardKey.Save)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        clear_action = QAction("&Clear All", self)
        clear_action.setShortcut(QKeySequence.StandardKey.Delete)
        clear_action.triggered.connect(self.clear_all)
        edit_menu.addAction(clear_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")
        
        analyze_action = QAction("&Analyze Document", self)
        analyze_action.setShortcut(Qt.KeyboardModifier.CtrlModifier | Qt.Key.Key_Return)
        analyze_action.triggered.connect(self.analyze_document)
        analysis_menu.addAction(analyze_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup application toolbar."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setObjectName("MainToolbar")
        toolbar.setIconSize(QSize(24, 24))
        
        # Load document button
        load_action = QAction("Load Document", self)
        load_action.triggered.connect(self.load_document)
        toolbar.addAction(load_action)
        
        toolbar.addSeparator()
        
        # Analyze button
        analyze_action = QAction("Analyze", self)
        analyze_action.triggered.connect(self.analyze_document)
        toolbar.addAction(analyze_action)
        
        # Export button
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_results)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Clear button
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_all)
        toolbar.addAction(clear_action)
    
    def setup_status_bar(self):
        """Setup status bar."""
        self.statusBar().showMessage("Ready")
    
    def setup_connections(self):
        """Setup signal/slot connections."""
        pass
    
    def apply_styles(self):
        """Apply application stylesheet."""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            color: #333;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 0.5em;
            padding-top: 0.5em;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 15px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0b7dda;
        }
        QPushButton:pressed {
            background-color: #0a5ea6;
        }
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
        }
        QListWidget {
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        QListWidget::item:selected {
            background-color: #2196F3;
            color: white;
        }
        QMenuBar {
            background-color: #f5f5f5;
        }
        QMenuBar::item:selected {
            background-color: #2196F3;
            color: white;
        }
        """
        self.setStyleSheet(stylesheet)
    
    def load_document(self):
        """Load a document from file system."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "Text Files (*.txt);;PDF Files (*.pdf);;Word Files (*.docx);;All Files (*)"
        )
        
        if file_path:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Add to documents list
                doc_name = Path(file_path).name
                self.documents.append({
                    'name': doc_name,
                    'path': file_path,
                    'content': content
                })
                
                # Add to list widget
                self.document_list.addItem(doc_name)
                
                # Select the newly added document
                self.document_list.setCurrentRow(len(self.documents) - 1)
                
                self.statusBar().showMessage(f"Loaded: {doc_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load document: {str(e)}")
                self.statusBar().showMessage("Error loading document")
    
    def on_document_selected(self):
        """Handle document selection from list."""
        current_row = self.document_list.currentRow()
        if current_row >= 0 and current_row < len(self.documents):
            self.current_document = self.documents[current_row]
            self.document_view.setText(self.current_document['content'][:2000] + "...")
            self.statusBar().showMessage(f"Selected: {self.current_document['name']}")
    
    def remove_document(self):
        """Remove selected document."""
        current_row = self.document_list.currentRow()
        if current_row >= 0:
            self.documents.pop(current_row)
            self.document_list.takeItem(current_row)
            self.document_view.clear()
            self.current_document = None
            self.statusBar().showMessage("Document removed")
    
    def analyze_document(self):
        """Analyze the current document."""
        if not self.current_document:
            QMessageBox.warning(self, "Warning", "Please load a document first.")
            return
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)
        self.statusBar().showMessage("Analyzing document...")
        
        # Simulate analysis process
        self.simulate_analysis()
    
    def simulate_analysis(self):
        """Simulate document analysis."""
        analysis_type = self.analysis_type.currentText()
        content = self.current_document['content']
        
        # Simulate analysis results
        results = {
            'type': analysis_type,
            'summary': self.generate_summary(content),
            'key_points': self.extract_key_points(content),
            'readability': self.analyze_readability(content),
            'sentiment': self.analyze_sentiment(content) if self.include_sentiment.isChecked() else None
        }
        
        self.analysis_results = results
        self.display_results(results)
        
        # Update progress
        self.progress_bar.setValue(100)
        self.analyze_btn.setEnabled(True)
        self.statusBar().showMessage("Analysis complete!")
        
        # Hide progress bar after 2 seconds
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
    
    def generate_summary(self, content: str) -> str:
        """Generate document summary."""
        sentences = content.split('.')
        summary_length = self.summary_length.value()
        words = 0
        summary_sentences = []
        
        for sentence in sentences:
            words += len(sentence.split())
            if words <= summary_length:
                summary_sentences.append(sentence.strip())
            else:
                break
        
        return ". ".join(summary_sentences) + "." if summary_sentences else "No summary available."
    
    def extract_key_points(self, content: str) -> list:
        """Extract key points from document."""
        sentences = content.split('.')
        key_points = []
        
        for i, sentence in enumerate(sentences[:5]):
            if sentence.strip():
                key_points.append(f"• {sentence.strip()}")
        
        return key_points if key_points else ["No key points found."]
    
    def analyze_readability(self, content: str) -> dict:
        """Analyze document readability."""
        words = len(content.split())
        sentences = len(content.split('.'))
        paragraphs = len(content.split('\n\n'))
        
        avg_word_length = sum(len(w) for w in content.split()) / max(words, 1)
        
        return {
            'word_count': words,
            'sentence_count': sentences,
            'paragraph_count': paragraphs,
            'avg_word_length': f"{avg_word_length:.2f}",
            'readability_score': "Easy" if avg_word_length < 5 else "Medium" if avg_word_length < 7 else "Hard"
        }
    
    def analyze_sentiment(self, content: str) -> dict:
        """Analyze document sentiment."""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'horrible']
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        if positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return {
            'sentiment': sentiment,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def display_results(self, results: dict):
        """Display analysis results in results view."""
        result_text = f"Analysis Type: {results['type']}\n"
        result_text += "=" * 50 + "\n\n"
        
        result_text += "SUMMARY:\n"
        result_text += "-" * 50 + "\n"
        result_text += f"{results['summary']}\n\n"
        
        if self.highlight_key_points.isChecked():
            result_text += "KEY POINTS:\n"
            result_text += "-" * 50 + "\n"
            for point in results['key_points']:
                result_text += f"{point}\n"
            result_text += "\n"
        
        result_text += "READABILITY ANALYSIS:\n"
        result_text += "-" * 50 + "\n"
        readability = results['readability']
        result_text += f"Word Count: {readability['word_count']}\n"
        result_text += f"Sentence Count: {readability['sentence_count']}\n"
        result_text += f"Paragraph Count: {readability['paragraph_count']}\n"
        result_text += f"Avg Word Length: {readability['avg_word_length']}\n"
        result_text += f"Readability Score: {readability['readability_score']}\n\n"
        
        if results['sentiment'] and self.include_sentiment.isChecked():
            result_text += "SENTIMENT ANALYSIS:\n"
            result_text += "-" * 50 + "\n"
            sentiment = results['sentiment']
            result_text += f"Overall Sentiment: {sentiment['sentiment']}\n"
            result_text += f"Positive Words: {sentiment['positive_words']}\n"
            result_text += f"Negative Words: {sentiment['negative_words']}\n"
        
        self.results_view.setText(result_text)
    
    def export_results(self):
        """Export analysis results to file."""
        if not self.analysis_results:
            QMessageBox.warning(self, "Warning", "No analysis results to export.")
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Export Results",
            "",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.results_view.toPlainText())
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
                self.statusBar().showMessage("Results exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")
    
    def clear_all(self):
        """Clear all data and results."""
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear all data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.documents.clear()
            self.document_list.clear()
            self.document_view.clear()
            self.results_view.clear()
            self.current_document = None
            self.analysis_results = {}
            self.statusBar().showMessage("All data cleared")
    
    def show_about_dialog(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About AI Reading Assistant",
            "AI Reading Assistant v1.0\n\n"
            "An intelligent document analysis tool powered by AI.\n\n"
            "Features:\n"
            "• Document Summarization\n"
            "• Key Point Extraction\n"
            "• Readability Analysis\n"
            "• Sentiment Analysis\n"
            "• Entity Recognition\n\n"
            "© 2025 AI Reading Assistant. All rights reserved."
        )
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.documents:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "You have unsaved documents. Do you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Application entry point."""
    app = __import__('PyQt6.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
