from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


def apply_stylesheet(widget):
    """
    Apply a custom stylesheet to the application or widget
    """
    # Set the application style
    widget.setStyle(QApplication.style())
    
    # Define colors
    # primary_color variable removed as it was unused
    secondary_color = "#3498db"  # Bright blue
    background_color = "#f5f5f5"  # Light gray
    text_color = "#000000"  # Black
    accent_color = "#e74c3c"  # Red
    
    # Create a custom palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(background_color))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(text_color))
    palette.setColor(QPalette.ColorRole.Base, QColor("white"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(background_color))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("white"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(text_color))
    palette.setColor(QPalette.ColorRole.Text, QColor(text_color))
    palette.setColor(QPalette.ColorRole.Button, QColor(background_color))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(text_color))
    palette.setColor(QPalette.ColorRole.Link, QColor(secondary_color))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(secondary_color))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))
    
    # Apply the palette
    widget.setPalette(palette)
    
    # Apply stylesheet
    widget.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e6e6e6;
            border: 1px solid #cccccc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            margin-right: 2px;
            color: #000000; /* Ensure text is black in all tabs */
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 1px solid white;
            color: #000000; /* Explicitly set text color for selected tabs */
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #f0f0f0;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px; /* Increased padding */
            min-width: 100px; /* Wider buttons */
            font-weight: bold; /* Make text bold */
        }
        
        QPushButton:hover {
            background-color: #2980b9;
            /* Remove the transition property */
        }
        transition: background-color 0.3s; /* Smooth transition */
        }
        
        QPushButton:pressed {
            background-color: #1c6ea4;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
            background-color: white;
            color: #000000; /* Add explicit text color */
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #3498db;
        }
        
        /* Add these new styles for QComboBox dropdown */
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #cccccc;
            border-left-style: solid;
        }
        
        QComboBox::item {
            color: #000000; /* Text color for dropdown items */
        }
        
        QComboBox::item:selected {
            background-color: #3498db;
            color: white; /* Text color for selected dropdown items */
        }
        
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            margin-top: 12px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 3px;
            color: #000000; /* Add explicit text color for group box titles */
            background-color: white; /* Match the background color */
        }
        
        QLabel {
            color: #000000; /* Add explicit text color for all labels */
        }
        
        QRadioButton {
            color: #000000; /* Ensure radio button text is black initially */
        }
        
        QRadioButton:checked {
            color: #000000; /* Ensure radio button text remains black when selected */
        }
        
        QComboBox {
            color: #000000; /* Ensure dropdown text is visible */
        }
        
        QComboBox QAbstractItemView {
            background-color: white;
            color: #000000; /* Ensure dropdown items are visible */
            selection-background-color: #3498db;
            selection-color: white;
        }
        
        QTableWidget {
            border: 1px solid #cccccc;
            gridline-color: #e6e6e6;
            selection-background-color: #3498db;
            selection-color: white;
        }
        
        QHeaderView::section {
            background-color: #e6e6e6;
            border: 1px solid #cccccc;
            padding: 4px;
            font-weight: bold;
        }
        
        QStatusBar {
            background-color: #2c3e50;
            color: white;
        }
    """)