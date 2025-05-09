#!/usr/bin/env python3
# FortiPass - Custom UI Widgets

from typing import Dict, List, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QSizePolicy, QScrollArea,
                            QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont, QBrush

class StrengthMeter(QProgressBar):
    """Custom progress bar for password strength visualization."""
    
    def __init__(self, parent=None):
        """Initialize the strength meter."""
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(False)
        self.setMinimumHeight(20)
        self.setMaximumHeight(20)
    
    def set_strength(self, value: int):
        """Set the strength value and update the color."""
        self.setValue(value)
        
        # Set color gradient based on strength
        if value < 20:
            self.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF4136, stop:1 #FF4136);
                    border-radius: 5px;
                }
            """)
        elif value < 40:
            self.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF4136, stop:1 #FF851B);
                    border-radius: 5px;
                }
            """)
        elif value < 60:
            self.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF851B, stop:1 #FFDC00);
                    border-radius: 5px;
                }
            """)
        elif value < 80:
            self.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFDC00, stop:1 #2ECC40);
                    border-radius: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ECC40, stop:1 #01FF70);
                    border-radius: 5px;
                }
            """)


class HeatmapWidget(QWidget):
    """Widget for visualizing password strength as a heatmap."""
    
    def __init__(self, parent=None):
        """Initialize the heatmap widget."""
        super().__init__(parent)
        self.password = ""
        self.analysis_results = None
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def set_password(self, password: str):
        """Set the password to visualize."""
        self.password = password
        self.update()
    
    def set_analysis_results(self, results: Dict[str, Any]):
        """Set the analysis results for visualization."""
        self.analysis_results = results
        self.update()
    
    def paintEvent(self, event):
        """Paint the heatmap visualization."""
        if not self.password:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate character cell width
        width = self.width()
        height = self.height()
        
        # Ensure minimum height
        if height < 40:
            height = 40
        
        # Calculate character cell dimensions
        char_count = len(self.password)
        if char_count == 0:
            return
            
        cell_width = min(width / char_count, 40)  # Max width of 40px per character
        cell_height = height - 20  # Leave room for character labels
        
        # Draw each character cell
        x_offset = (width - (cell_width * char_count)) / 2  # Center the heatmap
        
        for i, char in enumerate(self.password):
            # Calculate character strength (simplified)
            char_strength = self._calculate_char_strength(i, char)
            
            # Determine color based on strength
            color = self._get_strength_color(char_strength)
            
            # Draw character cell
            rect = QRectF(x_offset + (i * cell_width), 0, cell_width, cell_height)
            painter.fillRect(rect, color)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(rect)
            
            # Draw character
            painter.setPen(Qt.black)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, char)
            
            # Draw strength value
            strength_rect = QRectF(x_offset + (i * cell_width), cell_height, cell_width, 20)
            painter.drawText(strength_rect, Qt.AlignCenter, f"{int(char_strength)}")
    
    def _calculate_char_strength(self, index: int, char: str) -> float:
        """Calculate the strength contribution of a single character."""
        if not self.analysis_results:
            return 50  # Default medium strength
            
        # Base strength from character type
        base_strength = 0
        if char.islower():
            base_strength = 40
        elif char.isupper():
            base_strength = 60
        elif char.isdigit():
            base_strength = 50
        else:  # Symbol
            base_strength = 80
            
        # Adjust for patterns
        if self.analysis_results and "patterns" in self.analysis_results:
            for pattern in self.analysis_results["patterns"]:
                # This is a simplified approach - in a real implementation,
                # we would need to know which characters are part of which patterns
                if pattern["type"] == "repeated_chars" and index > 0 and char == self.password[index-1]:
                    base_strength -= 20
                elif pattern["type"] == "sequential_chars":
                    # Check if this might be part of a sequence
                    if index > 0 and ord(char) == ord(self.password[index-1]) + 1:
                        base_strength -= 15
                        
        # Ensure strength is within bounds
        return max(0, min(100, base_strength))
    
    def _get_strength_color(self, strength: float) -> QColor:
        """Get color based on strength value."""
        if strength < 20:
            return QColor("#FF4136")  # Red
        elif strength < 40:
            return QColor("#FF851B")  # Orange
        elif strength < 60:
            return QColor("#FFDC00")  # Yellow
        elif strength < 80:
            return QColor("#2ECC40")  # Light green
        else:
            return QColor("#01FF70")  # Bright green


class FeedbackWidget(QWidget):
    """Widget for displaying password feedback and suggestions."""
    
    def __init__(self, parent=None):
        """Initialize the feedback widget."""
        super().__init__(parent)
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Feedback section
        feedback_title = QLabel("Feedback & Suggestions")
        feedback_title.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.feedback_area = QScrollArea()
        self.feedback_area.setWidgetResizable(True)
        self.feedback_area.setFrameShape(QFrame.NoFrame)
        self.feedback_area.setMinimumHeight(80)
        self.feedback_area.setMaximumHeight(120)
        
        self.feedback_content = QWidget()
        self.feedback_layout = QVBoxLayout(self.feedback_content)
        self.feedback_layout.setAlignment(Qt.AlignTop)
        self.feedback_area.setWidget(self.feedback_content)
        
        # Patterns section
        patterns_title = QLabel("Detected Patterns")
        patterns_title.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.patterns_area = QScrollArea()
        self.patterns_area.setWidgetResizable(True)
        self.patterns_area.setFrameShape(QFrame.NoFrame)
        self.patterns_area.setMinimumHeight(60)
        self.patterns_area.setMaximumHeight(100)
        
        self.patterns_content = QWidget()
        self.patterns_layout = QVBoxLayout(self.patterns_content)
        self.patterns_layout.setAlignment(Qt.AlignTop)
        self.patterns_area.setWidget(self.patterns_content)
        
        # Add to main layout
        layout.addWidget(feedback_title)
        layout.addWidget(self.feedback_area)
        layout.addWidget(patterns_title)
        layout.addWidget(self.patterns_area)
    
    def set_feedback(self, feedback: List[str]):
        """Set the feedback messages."""
        # Clear previous feedback
        self._clear_layout(self.feedback_layout)
        
        # Add new feedback
        for message in feedback:
            label = QLabel(message)
            label.setWordWrap(True)
            self.feedback_layout.addWidget(label)
            
        # Add empty widget if no feedback
        if not feedback:
            label = QLabel("No feedback available.")
            label.setWordWrap(True)
            self.feedback_layout.addWidget(label)
    
    def set_patterns(self, patterns: List[Dict[str, Any]]):
        """Set the detected patterns."""
        # Clear previous patterns
        self._clear_layout(self.patterns_layout)
        
        # Add new patterns
        for pattern in patterns:
            # Create pattern label with severity indicator
            severity = pattern.get("severity", "low")
            color = "#FF4136" if severity == "high" else "#FF851B" if severity == "medium" else "#FFDC00"
            
            label = QLabel(f"• {pattern['description']}")
            label.setStyleSheet(f"color: {color};")
            label.setWordWrap(True)
            self.patterns_layout.addWidget(label)
            
        # Add empty widget if no patterns
        if not patterns:
            label = QLabel("No patterns detected.")
            label.setWordWrap(True)
            self.patterns_layout.addWidget(label)
    
    def _clear_layout(self, layout):
        """Clear all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater() 