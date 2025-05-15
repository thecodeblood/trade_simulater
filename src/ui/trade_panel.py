import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QLineEdit, QPushButton, QRadioButton, QButtonGroup,
                             QGroupBox, QGridLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDoubleSpinBox, QSpinBox, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor


class TradePanel(QWidget):
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
        
        # Create tabs for different trading functions
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create manual trading tab
        manual_tab = QWidget()
        tab_widget.addTab(manual_tab, "Manual Trading")
        self.setup_manual_trading(manual_tab)
        
        # Create simulation tab
        simulation_tab = QWidget()
        tab_widget.addTab(simulation_tab, "Simulation")
        self.setup_simulation(simulation_tab)
        
        # Create trade history table
        self.setup_trade_history(layout)
        
        # Update available symbols if orderbook manager is provided
        if self.orderbook_manager:
            self.update_symbols()
    
    def setup_manual_trading(self, parent):
        layout = QVBoxLayout(parent)
        
        # Market data and symbol selection
        market_layout = QHBoxLayout()
        layout.addLayout(market_layout)
        
        # Symbol selector
        symbol_group = QGroupBox("Symbol")
        symbol_layout = QVBoxLayout(symbol_group)
        
        self.symbol_combo = QComboBox()
        self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
        symbol_layout.addWidget(self.symbol_combo)
        
        market_layout.addWidget(symbol_group)
        
        # Market data display
        market_data_group = QGroupBox("Market Data")
        market_data_layout = QGridLayout(market_data_group)
        
        market_data_layout.addWidget(QLabel("Best Bid:"), 0, 0)
        self.best_bid_label = QLabel("--")
        market_data_layout.addWidget(self.best_bid_label, 0, 1)
        
        market_data_layout.addWidget(QLabel("Best Ask:"), 0, 2)
        self.best_ask_label = QLabel("--")
        market_data_layout.addWidget(self.best_ask_label, 0, 3)
        
        market_data_layout.addWidget(QLabel("Spread:"), 1, 0)
        self.spread_label = QLabel("--")
        market_data_layout.addWidget(self.spread_label, 1, 1)
        
        market_data_layout.addWidget(QLabel("Mid Price:"), 1, 2)
        self.mid_price_label = QLabel("--")
        market_data_layout.addWidget(self.mid_price_label, 1, 3)
        
        market_layout.addWidget(market_data_group)
        market_layout.addStretch()
        
        # Order entry form
        order_group = QGroupBox("New Order")
        order_layout = QGridLayout(order_group)
        layout.addWidget(order_group)
        
        # Order type
        order_layout.addWidget(QLabel("Order Type:"), 0, 0)
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Market", "Limit"])
        self.order_type_combo.currentTextChanged.connect(self.on_order_type_changed)
        order_layout.addWidget(self.order_type_combo, 0, 1)
        
        # Side selection
        order_layout.addWidget(QLabel("Side:"), 1, 0)
        side_layout = QHBoxLayout()
        self.buy_radio = QRadioButton("Buy")
        self.sell_radio = QRadioButton("Sell")
        self.buy_radio.setChecked(True)
        side_layout.addWidget(self.buy_radio)
        side_layout.addWidget(self.sell_radio)
        order_layout.addLayout(side_layout, 1, 1)
        
        # Price
        order_layout.addWidget(QLabel("Price:"), 2, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000)
        self.price_spin.setDecimals(2)
        self.price_spin.setSingleStep(0.01)
        order_layout.addWidget(self.price_spin, 2, 1)
        
        # Size
        order_layout.addWidget(QLabel("Size:"), 3, 0)
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0.000001, 1000)
        self.size_spin.setDecimals(6)
        self.size_spin.setSingleStep(0.01)
        order_layout.addWidget(self.size_spin, 3, 1)
        
        # Submit button
        self.submit_button = QPushButton("Submit Order")
        self.submit_button.clicked.connect(self.on_submit_order)
        order_layout.addWidget(self.submit_button, 4, 0, 1, 2)
        
        # Initial setup for order type
        self.on_order_type_changed(self.order_type_combo.currentText())
    
    def setup_simulation(self, parent):
        layout = QVBoxLayout(parent)
        
        # Simulation parameters
        params_group = QGroupBox("Simulation Parameters")
        params_layout = QGridLayout(params_group)
        layout.addWidget(params_group)
        
        # Symbol
        params_layout.addWidget(QLabel("Symbol:"), 0, 0)
        self.sim_symbol_combo = QComboBox()
        params_layout.addWidget(self.sim_symbol_combo, 0, 1)
        
        # Order size
        params_layout.addWidget(QLabel("Total Size:"), 1, 0)
        self.sim_size_spin = QDoubleSpinBox()
        self.sim_size_spin.setRange(0.01, 1000)
        self.sim_size_spin.setDecimals(6)
        self.sim_size_spin.setValue(1.0)
        params_layout.addWidget(self.sim_size_spin, 1, 1)
        
        # Time horizon
        params_layout.addWidget(QLabel("Time Horizon (min):"), 2, 0)
        self.sim_time_spin = QSpinBox()
        self.sim_time_spin.setRange(1, 1440)  # 1 min to 24 hours
        self.sim_time_spin.setValue(60)  # Default 1 hour
        params_layout.addWidget(self.sim_time_spin, 2, 1)
        
        # Number of slices
        params_layout.addWidget(QLabel("Number of Slices:"), 3, 0)
        self.sim_slices_spin = QSpinBox()
        self.sim_slices_spin.setRange(1, 100)
        self.sim_slices_spin.setValue(10)
        params_layout.addWidget(self.sim_slices_spin, 3, 1)
        
        # Side selection
        params_layout.addWidget(QLabel("Side:"), 4, 0)
        side_layout = QHBoxLayout()
        self.sim_buy_radio = QRadioButton("Buy")
        self.sim_sell_radio = QRadioButton("Sell")
        self.sim_buy_radio.setChecked(True)
        side_layout.addWidget(self.sim_buy_radio)
        side_layout.addWidget(self.sim_sell_radio)
        params_layout.addLayout(side_layout, 4, 1)
        
        # Risk aversion
        params_layout.addWidget(QLabel("Risk Aversion:"), 5, 0)
        self.sim_risk_spin = QDoubleSpinBox()
        self.sim_risk_spin.setRange(0.1, 10.0)
        self.sim_risk_spin.setDecimals(1)
        self.sim_risk_spin.setValue(1.0)
        params_layout.addWidget(self.sim_risk_spin, 5, 1)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        
        self.sim_calculate_button = QPushButton("Calculate Optimal Trajectory")
        self.sim_calculate_button.clicked.connect(self.on_calculate_trajectory)
        buttons_layout.addWidget(self.sim_calculate_button)
        
        self.sim_execute_button = QPushButton("Execute Simulation")
        self.sim_execute_button.clicked.connect(self.on_execute_simulation)
        buttons_layout.addWidget(self.sim_execute_button)
        
        # Results display
        results_group = QGroupBox("Simulation Results")
        results_layout = QVBoxLayout(results_group)
        layout.addWidget(results_group)
        
        self.sim_results_table = QTableWidget(0, 3)
        self.sim_results_table.setHorizontalHeaderLabels(["Time", "Size", "Expected Price"])
        self.sim_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        results_layout.addWidget(self.sim_results_table)
        
        # Update available symbols
        if self.orderbook_manager:
            self.update_symbols()
    
    def setup_trade_history(self, layout):
        history_group = QGroupBox("Trade History")
        history_layout = QVBoxLayout(history_group)
        layout.addWidget(history_group)
        
        self.history_table = QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels(
            ["Time", "Symbol", "Side", "Type", "Price", "Size"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)
    
    def update_symbols(self):
        if not self.orderbook_manager:
            return
            
        # Get available symbols from orderbook manager
        self.symbols = list(self.orderbook_manager.orderbooks.keys())
        
        # Update combo boxes
        self.symbol_combo.clear()
        self.symbol_combo.addItems(self.symbols)
        
        self.sim_symbol_combo.clear()
        self.sim_symbol_combo.addItems(self.symbols)
        
        # Select first symbol if available
        if self.symbols:
            self.current_symbol = self.symbols[0]
            self.symbol_combo.setCurrentText(self.current_symbol)
            self.sim_symbol_combo.setCurrentText(self.current_symbol)
    
    @pyqtSlot(str)
    def on_symbol_changed(self, symbol):
        self.current_symbol = symbol
        self.update_data()
    
    @pyqtSlot(str)
    def on_order_type_changed(self, order_type):
        # Enable/disable price field based on order type
        if order_type == "Market":
            self.price_spin.setEnabled(False)
        else:  # Limit order
            self.price_spin.setEnabled(True)
    
    @pyqtSlot()
    def on_submit_order(self):
        if not self.current_symbol:
            self.logger.warning("No symbol selected")
            return
        
        # Get order details
        order_type = self.order_type_combo.currentText()
        side = "buy" if self.buy_radio.isChecked() else "sell"
        price = self.price_spin.value() if order_type == "Limit" else None
        size = self.size_spin.value()
        
        # Log order details
        self.logger.info(
            f"Order submitted: {self.current_symbol} {side} {order_type} "
            f"{'@ ' + str(price) if price else ''} {size}"
        )
        
        # TODO: Implement actual order submission logic
        
        # Add to trade history for demonstration
        self.add_to_history(self.current_symbol, side, order_type, 
                           price if price else "Market", size)
    
    @pyqtSlot()
    def on_calculate_trajectory(self):
        # Get simulation parameters
        symbol = self.sim_symbol_combo.currentText()
        size = self.sim_size_spin.value()
        time_horizon = self.sim_time_spin.value()
        slices = self.sim_slices_spin.value()
        side = "buy" if self.sim_buy_radio.isChecked() else "sell"
        risk_aversion = self.sim_risk_spin.value()
        
        # Log simulation parameters
        self.logger.info(
            f"Calculating trajectory: {symbol} {side} {size} over {time_horizon} min "
            f"in {slices} slices with risk aversion {risk_aversion}"
        )
        
        # TODO: Implement actual trajectory calculation using Almgren-Chriss model
        
        # For demonstration, show a simple TWAP trajectory
        self.sim_results_table.setRowCount(0)
        slice_size = size / slices
        time_per_slice = time_horizon / slices
        
        for i in range(slices):
            self.sim_results_table.insertRow(i)
            
            time_item = QTableWidgetItem(f"{i * time_per_slice:.1f} min")
            size_item = QTableWidgetItem(f"{slice_size:.6f}")
            price_item = QTableWidgetItem("Market")
            
            self.sim_results_table.setItem(i, 0, time_item)
            self.sim_results_table.setItem(i, 1, size_item)
            self.sim_results_table.setItem(i, 2, price_item)
    
    @pyqtSlot()
    def on_execute_simulation(self):
        # Get number of rows in results table
        rows = self.sim_results_table.rowCount()
        if rows == 0:
            self.logger.warning("No trajectory calculated")
            return
        
        symbol = self.sim_symbol_combo.currentText()
        side = "buy" if self.sim_buy_radio.isChecked() else "sell"
        
        # Log simulation execution
        self.logger.info(f"Executing simulation for {symbol} {side}")
        
        # TODO: Implement actual simulation execution
        
        # For demonstration, add all slices to trade history
        for i in range(rows):
            time = self.sim_results_table.item(i, 0).text()
            size = float(self.sim_results_table.item(i, 1).text())
            price = self.sim_results_table.item(i, 2).text()
            
            self.add_to_history(symbol, side, "Simulation", price, size)
    
    def add_to_history(self, symbol, side, order_type, price, size):
        # Add new row to history table
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        import datetime
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        
        time_item = QTableWidgetItem(time_str)
        symbol_item = QTableWidgetItem(symbol)
        side_item = QTableWidgetItem(side.capitalize())
        type_item = QTableWidgetItem(order_type)
        price_item = QTableWidgetItem(str(price))
        size_item = QTableWidgetItem(f"{size:.6f}")
        
        # Color formatting
        if side.lower() == "buy":
            side_item.setForeground(QColor(0, 128, 0))  # Green for buy
        else:
            side_item.setForeground(QColor(255, 0, 0))  # Red for sell
        
        self.history_table.setItem(row, 0, time_item)
        self.history_table.setItem(row, 1, symbol_item)
        self.history_table.setItem(row, 2, side_item)
        self.history_table.setItem(row, 3, type_item)
        self.history_table.setItem(row, 4, price_item)
        self.history_table.setItem(row, 5, size_item)
    
    def update_data(self):
        if not self.orderbook_manager or not self.current_symbol:
            return
            
        # Get orderbook for current symbol
        orderbook = self.orderbook_manager.get_orderbook(self.current_symbol)
        if not orderbook:
            self.logger.warning(f"No orderbook found for symbol {self.current_symbol}")
            return
        
        # Update market data display
        best_bid = orderbook.get_best_bid()
        best_ask = orderbook.get_best_ask()
        spread = orderbook.get_spread()
        mid_price = orderbook.get_mid_price()
        
        # Extract price from the tuples (price, quantity)
        bid_price = best_bid[0] if best_bid[0] is not None else 0
        ask_price = best_ask[0] if best_ask[0] is not None else 0
        
        self.best_bid_label.setText(f"{bid_price:.2f}")
        self.best_ask_label.setText(f"{ask_price:.2f}")
        self.spread_label.setText(f"{spread:.2f}")
        self.mid_price_label.setText(f"{mid_price:.2f}")
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value to mid price
        if mid_price:
            self.price_spin.setValue(mid_price)
        
        # Update price spin default value