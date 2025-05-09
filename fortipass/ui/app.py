#!/usr/bin/env python3
# FortiPass - Main UI Application

import os
import sys
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QProgressBar, QFrame, QGridLayout, QCheckBox,
                            QSpinBox, QComboBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon

from fortipass.core.password_analyzer import PasswordAnalyzer
from fortipass.ui.widgets import StrengthMeter, HeatmapWidget, FeedbackWidget
from fortipass.utils.report_generator import ReportGenerator

class FortiPassApp:
    """Main FortiPass application class."""
    
    def __init__(self):
        """Initialize the FortiPass application."""
        self.app = QApplication(sys.argv)
        self.window = FortiPassWindow()
        
    def run(self):
        """Run the application main loop."""
        self.window.show()
        return self.app.exec_()

class FortiPassWindow(QMainWindow):
    """Main window for FortiPass application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("FortiPass - Professional Password Strength Visualizer")
        self.setMinimumSize(800, 600)
        
        # Initialize the password analyzer with default wordlist
        wordlist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    "data", "common_passwords.txt")
        self.analyzer = PasswordAnalyzer(wordlist_path if os.path.exists(wordlist_path) else None)
        
        # Initialize UI components
        self.init_ui()
        
        # Set up timer for delayed analysis (for better UX)
        self.analysis_timer = QTimer()
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.timeout.connect(self.analyze_password)
        
        # Initial analysis
        self.analyze_password()
    
    def init_ui(self):
        """Initialize the user interface components."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title and description
        title_label = QLabel("FortiPass")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel("Professional Password Strength Visualizer")
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Password input section
        input_frame = QFrame()
        input_frame.setFrameShape(QFrame.StyledPanel)
        input_layout = QVBoxLayout(input_frame)
        
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password to analyze")
        self.password_input.textChanged.connect(self.on_password_changed)
        
        self.show_password_btn = QPushButton("Show")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input, 1)
        password_layout.addWidget(self.show_password_btn)
        
        input_layout.addLayout(password_layout)
        
        # Strength meter
        meter_layout = QHBoxLayout()
        meter_label = QLabel("Strength:")
        meter_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.strength_meter = StrengthMeter()
        
        self.strength_label = QLabel("N/A")
        self.strength_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.strength_label.setMinimumWidth(100)
        
        meter_layout.addWidget(meter_label)
        meter_layout.addWidget(self.strength_meter, 1)
        meter_layout.addWidget(self.strength_label)
        
        input_layout.addLayout(meter_layout)
        
        # Visualization section
        viz_frame = QFrame()
        viz_frame.setFrameShape(QFrame.StyledPanel)
        viz_layout = QVBoxLayout(viz_frame)
        
        viz_title = QLabel("Password Analysis")
        viz_title.setFont(QFont("Arial", 12, QFont.Bold))
        viz_title.setAlignment(Qt.AlignCenter)
        
        # Heatmap visualization
        self.heatmap = HeatmapWidget()
        
        # Feedback widget
        self.feedback_widget = FeedbackWidget()
        
        # Metrics grid
        metrics_layout = QGridLayout()
        
        # Row 0
        metrics_layout.addWidget(QLabel("Length:"), 0, 0)
        self.length_label = QLabel("0")
        metrics_layout.addWidget(self.length_label, 0, 1)
        
        metrics_layout.addWidget(QLabel("Entropy:"), 0, 2)
        self.entropy_label = QLabel("0.0")
        metrics_layout.addWidget(self.entropy_label, 0, 3)
        
        # Row 1
        metrics_layout.addWidget(QLabel("Character Classes:"), 1, 0)
        self.diversity_label = QLabel("0/4")
        metrics_layout.addWidget(self.diversity_label, 1, 1)
        
        metrics_layout.addWidget(QLabel("Crack Time:"), 1, 2)
        self.crack_time_label = QLabel("Instant")
        metrics_layout.addWidget(self.crack_time_label, 1, 3)
        
        viz_layout.addWidget(viz_title)
        viz_layout.addWidget(self.heatmap)
        viz_layout.addLayout(metrics_layout)
        viz_layout.addWidget(self.feedback_widget)
        
        # Tools section
        tools_frame = QFrame()
        tools_frame.setFrameShape(QFrame.StyledPanel)
        tools_layout = QHBoxLayout(tools_frame)
        
        # Password generator
        generator_layout = QVBoxLayout()
        generator_title = QLabel("Password Generator")
        generator_title.setFont(QFont("Arial", 10, QFont.Bold))
        
        generator_options_layout = QGridLayout()
        
        generator_options_layout.addWidget(QLabel("Length:"), 0, 0)
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)
        generator_options_layout.addWidget(self.length_spin, 0, 1)
        
        self.uppercase_check = QCheckBox("Uppercase (A-Z)")
        self.uppercase_check.setChecked(True)
        generator_options_layout.addWidget(self.uppercase_check, 1, 0, 1, 2)
        
        self.digits_check = QCheckBox("Digits (0-9)")
        self.digits_check.setChecked(True)
        generator_options_layout.addWidget(self.digits_check, 2, 0, 1, 2)
        
        self.symbols_check = QCheckBox("Symbols (!@#$...)")
        self.symbols_check.setChecked(True)
        generator_options_layout.addWidget(self.symbols_check, 3, 0, 1, 2)
        
        generate_btn = QPushButton("Generate Password")
        generate_btn.clicked.connect(self.generate_password)
        
        generator_layout.addWidget(generator_title)
        generator_layout.addLayout(generator_options_layout)
        generator_layout.addWidget(generate_btn)
        
        # Export section
        export_layout = QVBoxLayout()
        export_title = QLabel("Export Report")
        export_title.setFont(QFont("Arial", 10, QFont.Bold))
        
        export_options_layout = QGridLayout()
        
        export_options_layout.addWidget(QLabel("Format:"), 0, 0)
        self.export_format = QComboBox()
        self.export_format.addItems(["PDF", "JSON"])
        export_options_layout.addWidget(self.export_format, 0, 1)
        
        export_btn = QPushButton("Export Analysis")
        export_btn.clicked.connect(self.export_report)
        
        export_layout.addWidget(export_title)
        export_layout.addLayout(export_options_layout)
        export_layout.addWidget(export_btn)
        
        # Add to tools layout
        tools_layout.addLayout(generator_layout)
        tools_layout.addLayout(export_layout)
        
        # Add all sections to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addWidget(input_frame)
        main_layout.addWidget(viz_frame, 1)  # Give this section more space
        main_layout.addWidget(tools_frame)
    
    def on_password_changed(self):
        """Handle password input changes."""
        # Reset the timer to delay analysis for better UX
        self.analysis_timer.start(300)  # 300ms delay
    
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("Show")
    
    def analyze_password(self):
        """Analyze the current password and update UI."""
        password = self.password_input.text()
        
        # Get analysis results
        results = self.analyzer.analyze(password)
        
        # Update UI with results
        self.update_ui_with_results(results)
    
    def update_ui_with_results(self, results: Dict[str, Any]):
        """Update UI components with analysis results."""
        # Update strength meter
        self.strength_meter.set_strength(results["strength_score"])
        self.strength_label.setText(results["strength_category"])
        
        # Set color based on strength
        if results["strength_score"] < 20:
            color = "#FF4136"  # Red
        elif results["strength_score"] < 40:
            color = "#FF851B"  # Orange
        elif results["strength_score"] < 60:
            color = "#FFDC00"  # Yellow
        elif results["strength_score"] < 80:
            color = "#2ECC40"  # Light green
        else:
            color = "#01FF70"  # Bright green
            
        self.strength_label.setStyleSheet(f"color: {color};")
        
        # Update metrics
        self.length_label.setText(str(results["length"]))
        self.entropy_label.setText(f"{results['entropy']:.2f}")
        self.diversity_label.setText(f"{results['char_diversity']}/4")
        self.crack_time_label.setText(results["crack_time"])
        
        # Update heatmap visualization
        self.heatmap.set_password(results["password"] if "password" in results else self.password_input.text())
        self.heatmap.set_analysis_results(results)
        
        # Update feedback
        self.feedback_widget.set_feedback(results["feedback"])
        self.feedback_widget.set_patterns(results["patterns"])
    
    def generate_password(self):
        """Generate a strong password based on selected options."""
        length = self.length_spin.value()
        include_uppercase = self.uppercase_check.isChecked()
        include_digits = self.digits_check.isChecked()
        include_symbols = self.symbols_check.isChecked()
        
        password = self.analyzer.generate_strong_password(
            length, include_uppercase, include_digits, include_symbols
        )
        
        self.password_input.setText(password)
        self.analyze_password()
    
    def export_report(self):
        """Export password analysis report."""
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Export Failed", "No password to analyze.")
            return
            
        # Get analysis results
        results = self.analyzer.analyze(password)
        
        # Create report generator
        report_gen = ReportGenerator()
        
        # Get export format
        export_format = self.export_format.currentText().lower()
        
        # Get save path from user
        file_filter = "PDF Files (*.pdf)" if export_format == "pdf" else "JSON Files (*.json)"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "", file_filter
        )
        
        if not save_path:
            return  # User canceled
        
        try:
            # Generate and save report
            if export_format == "pdf":
                report_gen.export_pdf(results, save_path)
            else:
                report_gen.export_json(results, save_path)
                
            QMessageBox.information(self, "Export Successful", 
                                   f"Report exported successfully to {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                               f"Failed to export report: {str(e)}") 