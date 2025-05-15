import logging
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QGridLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QComboBox, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QPainter, QPen


class StatisticsWidget(QFrame):
    """Widget for displaying trading statistics"""
    def __init__(self, title, value="--", prefix="", suffix=""):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.value_label = QLabel(f"{prefix}{value}{suffix}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
    
    def update_value(self, value, prefix="", suffix=""):
        self.value_label.setText(f"{prefix}{value}{suffix}")


class PerformanceChart(QFrame):
    """Simple bar chart for performance visualization"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        self.values = [0] * 10  # Store last 10 values
        self.colors = []  # Colors for each bar
    
    def update_data(self, new_value):
        # Shift values and add new one
        self.values = self.values[1:] + [new_value]
        
        # Update colors based on values (green for positive, red for negative)
        self.colors = [QColor(0, 128, 0) if v >= 0 else QColor(255, 0, 0) for v in self.values]
        
        # Trigger repaint
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(event.rect(), Qt.GlobalColor.white)
        
        # Get dimensions
        width = self.width()
        height = self.height()
        
        # Find min/max for scaling
        min_val = min(min(self.values), 0)  # Ensure we include zero
        max_val = max(max(self.values), 0)  # Ensure we include zero
        
        # Ensure we have a range to avoid division by zero
        value_range = max_val - min_val
        if value_range == 0:
            value_range = 1
        
        # Draw zero line
        zero_y = height - ((0 - min_val) / value_range * height)
        painter.setPen(QPen(Qt.GlobalColor.gray, 1))
        painter.drawLine(0, int(zero_y), width, int(zero_y))
        
        # Draw bars
        if self.values:
            bar_width = width / len(self.values)
            for i, value in enumerate(self.values):
                # Calculate bar height
                bar_height = (value - min_val) / value_range * height
                
                # Draw bar
                painter.fillRect(
                    int(i * bar_width), 
                    int(height - bar_height),
                    int(bar_width - 2),  # Leave small gap between bars
                    int(bar_height),
                    self.colors[i]
                )


class Dashboard(QWidget):
    def __init__(self, orderbook_manager=None):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.orderbook_manager = orderbook_manager
        self.current_symbol = None
        self.symbols = []
        
        # Trading statistics
        self.total_trades = 0
        self.total_volume = 0
        self.pnl = 0
        self.win_rate = 0
        
        # Initialize UI
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        layout.addLayout(controls_layout)
        
        # Symbol selector
        controls_layout.addWidget(QLabel("Symbol:"))
        self.symbol_combo = QComboBox()
        self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
        controls_layout.addWidget(self.symbol_combo)
        
        # Time period selector
        controls_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Today", "This Week", "This Month", "All Time"])
        self.period_combo.currentTextChanged.connect(self.update_data)
        controls_layout.addWidget(self.period_combo)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_data)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        
        # Statistics widgets
        stats_layout = QHBoxLayout()
        layout.addLayout(stats_layout)
        
        self.trades_widget = StatisticsWidget("Total Trades", "0")
        stats_layout.addWidget(self.trades_widget)
        
        self.volume_widget = StatisticsWidget("Total Volume", "0.00")
        stats_layout.addWidget(self.volume_widget)
        
        self.pnl_widget = StatisticsWidget("P&L", "0.00", prefix="$")
        stats_layout.addWidget(self.pnl_widget)
        
        self.win_rate_widget = StatisticsWidget("Win Rate", "0", suffix="%")
        stats_layout.addWidget(self.win_rate_widget)
        
        # Performance chart
        chart_group = QGroupBox("Performance")
        layout.addWidget(chart_group)
        chart_layout = QVBoxLayout(chart_group)
        
        self.performance_chart = PerformanceChart()
        chart_layout.addWidget(self.performance_chart)
        
        # Recent trades table
        trades_group = QGroupBox("Recent Trades")
        layout.addWidget(trades_group)
        trades_layout = QVBoxLayout(trades_group)
        
        self.trades_table = QTableWidget(0, 6)
        self.trades_table.setHorizontalHeaderLabels(
            ["Time", "Symbol", "Side", "Price", "Size", "P&L"]
        )
        self.trades_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        trades_layout.addWidget(self.trades_table)
        
        # Update available symbols if orderbook manager is provided
        if self.orderbook_manager:
            self.update_symbols()
        
        # Add some sample data for demonstration
        self.add_sample_data()
    
    def update_symbols(self):
        if not self.orderbook_manager:
            return
            
        # Get available symbols from orderbook manager
        self.symbols = list(self.orderbook_manager.orderbooks.keys())
        
        # Update combo box
        self.symbol_combo.clear()
        self.symbol_combo.addItems(["All"] + self.symbols)
        
        # Select "All" by default
        self.symbol_combo.setCurrentText("All")
    
    @pyqtSlot(str)
    def on_symbol_changed(self, symbol):
        self.current_symbol = None if symbol == "All" else symbol
        self.update_data()
    
    def update_data(self):
        # In a real application, this would fetch data from a database or trading system
        # For now, we'll just update the UI with the sample data
        
        # Update statistics widgets
        self.trades_widget.update_value(str(self.total_trades))
        self.volume_widget.update_value(f"{self.total_volume:.6f}")
        self.pnl_widget.update_value(f"{self.pnl:.2f}", prefix="$")
        self.win_rate_widget.update_value(str(self.win_rate), suffix="%")
        
        # Log the update
        self.logger.info(f"Dashboard updated for {self.current_symbol or 'All'} symbols")
    
    def add_sample_data(self):
        # Add sample statistics
        self.total_trades = 24
        self.total_volume = 3.45
        self.pnl = 127.50
        self.win_rate = 65
        
        # Update statistics widgets
        self.update_data()
        
        # Add sample performance data
        sample_performance = [15, -5, 22, -8, 30, 25, 10, -12, 18, 35]
        for value in sample_performance:
            self.performance_chart.update_data(value)
        
        # Add sample trades
        sample_trades = [
            {"time": "09:30:45", "symbol": "BTC-USDT", "side": "Buy", "price": 42150.25, "size": 0.25, "pnl": 18.75},
            {"time": "10:15:22", "symbol": "ETH-USDT", "side": "Sell", "price": 2250.50, "size": 1.5, "pnl": -12.30},
            {"time": "11:05:10", "symbol": "BTC-USDT", "side": "Buy", "price": 42200.00, "size": 0.15, "pnl": 7.50},
            {"time": "12:30:05", "symbol": "SOL-USDT", "side": "Sell", "price": 105.75, "size": 10.0, "pnl": 35.25},
            {"time": "13:45:30", "symbol": "ETH-USDT", "side": "Buy", "price": 2275.25, "size": 0.8, "pnl": 22.40},
        ]
        
        # Add to table
        self.trades_table.setRowCount(len(sample_trades))
        for i, trade in enumerate(sample_trades):
            time_item = QTableWidgetItem(trade["time"])
            symbol_item = QTableWidgetItem(trade["symbol"])
            side_item = QTableWidgetItem(trade["side"])
            price_item = QTableWidgetItem(f"{trade['price']:.2f}")
            size_item = QTableWidgetItem(f"{trade['size']:.6f}")
            pnl_item = QTableWidgetItem(f"${trade['pnl']:.2f}")
            
            # Color formatting
            if trade["side"] == "Buy":
                side_item.setForeground(QColor(0, 128, 0))  # Green for buy
            else:
                side_item.setForeground(QColor(255, 0, 0))  # Red for sell
                
            if trade["pnl"] >= 0:
                pnl_item.setForeground(QColor(0, 128, 0))  # Green for positive
            else:
                pnl_item.setForeground(QColor(255, 0, 0))  # Red for negative
            
            self.trades_table.setItem(i, 0, time_item)
            self.trades_table.setItem(i, 1, symbol_item)
            self.trades_table.setItem(i, 2, side_item)
            self.trades_table.setItem(i, 3, price_item)
            self.trades_table.setItem(i, 4, size_item)
            self.trades_table.setItem(i, 5, pnl_item)