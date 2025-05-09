#!/usr/bin/env python3
# FortiPass - Report Generator Utility

import os
import json
import datetime
from typing import Dict, Any, List

class ReportGenerator:
    """Utility for generating password analysis reports in various formats."""
    
    def __init__(self):
        """Initialize the report generator."""
        pass
    
    def export_json(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Export password analysis results as JSON.
        
        Args:
            results: Password analysis results
            output_path: Path to save the JSON file
        """
        # Create a copy of results to avoid modifying the original
        report_data = dict(results)
        
        # Add metadata
        report_data["metadata"] = {
            "generated_at": datetime.datetime.now().isoformat(),
            "generator": "FortiPass Password Strength Visualizer",
            "version": "1.0.0"
        }
        
        # Remove password from the report for security
        if "password" in report_data:
            del report_data["password"]
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
    
    def export_pdf(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Export password analysis results as PDF.
        
        Args:
            results: Password analysis results
            output_path: Path to save the PDF file
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics.charts.barcharts import VerticalBarChart
        except ImportError:
            raise ImportError("ReportLab is required for PDF export. Install with 'pip install reportlab'.")
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = styles["Heading1"]
        subtitle_style = styles["Heading2"]
        normal_style = styles["Normal"]
        
        # Content elements
        elements = []
        
        # Title
        elements.append(Paragraph("Password Strength Analysis Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Metadata
        elements.append(Paragraph("Report Details", subtitle_style))
        elements.append(Spacer(1, 6))
        
        now = datetime.datetime.now()
        elements.append(Paragraph(f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Paragraph("Tool: FortiPass Password Strength Visualizer", normal_style))
        elements.append(Spacer(1, 12))
        
        # Summary
        elements.append(Paragraph("Summary", subtitle_style))
        elements.append(Spacer(1, 6))
        
        # Create summary table
        summary_data = [
            ["Metric", "Value"],
            ["Strength Score", f"{results['strength_score']}/100"],
            ["Strength Category", results["strength_category"]],
            ["Password Length", str(results["length"])],
            ["Entropy", f"{results['entropy']:.2f}"],
            ["Character Classes", f"{results['char_diversity']}/4"],
            ["Estimated Crack Time", results["crack_time"]]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 300])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 12))
        
        # Character class details
        elements.append(Paragraph("Character Classes", subtitle_style))
        elements.append(Spacer(1, 6))
        
        char_class_data = [
            ["Character Class", "Present"],
            ["Lowercase Letters", "Yes" if results["has_lowercase"] else "No"],
            ["Uppercase Letters", "Yes" if results["has_uppercase"] else "No"],
            ["Digits", "Yes" if results["has_digits"] else "No"],
            ["Special Characters", "Yes" if results["has_symbols"] else "No"]
        ]
        
        char_class_table = Table(char_class_data, colWidths=[200, 300])
        char_class_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(char_class_table)
        elements.append(Spacer(1, 12))
        
        # Detected patterns
        if "patterns" in results and results["patterns"]:
            elements.append(Paragraph("Detected Patterns", subtitle_style))
            elements.append(Spacer(1, 6))
            
            patterns_data = [["Pattern Type", "Description", "Severity"]]
            for pattern in results["patterns"]:
                patterns_data.append([
                    pattern["type"].replace("_", " ").title(),
                    pattern["description"],
                    pattern.get("severity", "low").title()
                ])
            
            patterns_table = Table(patterns_data, colWidths=[150, 250, 100])
            patterns_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (2, 0), 12),
                ('BOTTOMPADDING', (0, 0), (2, 0), 12),
                ('BACKGROUND', (0, 1), (2, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(patterns_table)
            elements.append(Spacer(1, 12))
        
        # Feedback and suggestions
        elements.append(Paragraph("Feedback & Suggestions", subtitle_style))
        elements.append(Spacer(1, 6))
        
        for feedback in results["feedback"]:
            elements.append(Paragraph(f"• {feedback}", normal_style))
            elements.append(Spacer(1, 3))
        
        elements.append(Spacer(1, 12))
        
        # NIST guidelines
        elements.append(Paragraph("NIST SP 800-63B Guidelines", subtitle_style))
        elements.append(Spacer(1, 6))
        
        nist_guidelines = [
            "Minimum of 8 characters in length",
            "Support passwords at least 64 characters in length",
            "Support all ASCII characters including spaces",
            "Screen passwords against commonly used, expected, or compromised values",
            "No composition rules requiring specific character types",
            "No password hints or knowledge-based security questions",
            "No periodic password resets without reason"
        ]
        
        for guideline in nist_guidelines:
            elements.append(Paragraph(f"• {guideline}", normal_style))
            elements.append(Spacer(1, 3))
        
        # Build the PDF
        doc.build(elements) 