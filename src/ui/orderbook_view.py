import logging
from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor


class OrderbookView(QWidget):
    def __init__(self, orderbook_manager=None):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.orderbook_manager = orderbook_manager
        self.current_symbol = None
        self.symbols = []
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        layout.addLayout(controls_layout)
        
        # Symbol selector
        self.symbol_label = QLabel("Symbol:")
        controls_layout.addWidget(self.symbol_label)
        
        self.symbol_combo = QComboBox()
        self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
        controls_layout.addWidget(self.symbol_combo)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_data)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        
        # Market data display
        self.market_data_layout = QHBoxLayout()
        layout.addLayout(self.market_data_layout)
        
        # Best bid/ask display
        self.price_info = QLabel("Best Bid: -- | Best Ask: -- | Spread: -- | Mid: --")
        self.price_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.price_info.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.market_data_layout.addWidget(self.price_info)
        
        # Orderbook tables layout
        tables_layout = QHBoxLayout()
        layout.addLayout(tables_layout)
        
        # Bids table
        self.bids_table = QTableWidget(0, 2)
        self.bids_table.setHorizontalHeaderLabels(["Price", "Size"])
        self.bids_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bids_table.verticalHeader().setVisible(False)
        self.bids_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tables_layout.addWidget(self.bids_table)
        
        # Asks table
        self.asks_table = QTableWidget(0, 2)
        self.asks_table.setHorizontalHeaderLabels(["Price", "Size"])
        self.asks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.asks_table.verticalHeader().setVisible(False)
        self.asks_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tables_layout.addWidget(self.asks_table)
        
        # Update available symbols if orderbook manager is provided
        if self.orderbook_manager:
            self.update_symbols()
    
    def update_symbols(self):
        if not self.orderbook_manager:
            return
            
        # Get available symbols from orderbook manager
        self.symbols = list(self.orderbook_manager.orderbooks.keys())
        
        # Update combo box
        self.symbol_combo.clear()
        self.symbol_combo.addItems(self.symbols)
        
        # Select first symbol if available
        if self.symbols:
            self.current_symbol = self.symbols[0]
            self.symbol_combo.setCurrentText(self.current_symbol)
    
    @pyqtSlot(str)
    def on_symbol_changed(self, symbol):
        self.current_symbol = symbol
        self.update_data()
    
    def update_data(self):
        if not self.orderbook_manager or not self.current_symbol:
            return
            
        # Get orderbook for current symbol
        orderbook = self.orderbook_manager.get_orderbook(self.current_symbol)
        if not orderbook:
            self.logger.warning(f"No orderbook found for symbol {self.current_symbol}")
            return
        
        # Update price info
        best_bid = orderbook.get_best_bid()
        best_ask = orderbook.get_best_ask()
        spread = orderbook.get_spread()
        mid_price = orderbook.get_mid_price()
        
        # Extract price from the tuples (price, quantity)
        bid_price = best_bid[0] if best_bid[0] is not None else 0
        ask_price = best_ask[0] if best_ask[0] is not None else 0
        
        self.price_info.setText(
            f"Best Bid: {bid_price:.2f} | Best Ask: {ask_price:.2f} | "
            f"Spread: {spread:.2f} | Mid: {mid_price:.2f}"
        )
        
        # Rest of the method remains unchanged
        # Update bids table
        self.bids_table.setRowCount(0)
        for i, (price, size) in enumerate(sorted(orderbook.bids.items(), reverse=True)):
            self.bids_table.insertRow(i)
            price_item = QTableWidgetItem(f"{price:.2f}")
            size_item = QTableWidgetItem(f"{size:.6f}")
            
            # Color formatting
            price_item.setForeground(QColor(0, 128, 0))  # Green for bids
            
            self.bids_table.setItem(i, 0, price_item)
            self.bids_table.setItem(i, 1, size_item)
        
        # Update asks table
        self.asks_table.setRowCount(0)
        for i, (price, size) in enumerate(sorted(orderbook.asks.items())):
            self.asks_table.insertRow(i)
            price_item = QTableWidgetItem(f"{price:.2f}")
            size_item = QTableWidgetItem(f"{size:.6f}")
            
            # Color formatting
            price_item.setForeground(QColor(255, 0, 0))  # Red for asks
            
            self.asks_table.setItem(i, 0, price_item)
            self.asks_table.setItem(i, 1, size_item)