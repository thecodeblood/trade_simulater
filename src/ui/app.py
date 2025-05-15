import sys
import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                            QVBoxLayout, QHBoxLayout, QWidget, QStatusBar)
from PyQt6.QtCore import Qt, QTimer

from .orderbook_view import OrderbookView
from .trade_panel import TradePanel
from .dashboard import Dashboard
from .styles import apply_stylesheet

class TradeSimulatorApp(QMainWindow):
    def __init__(self, orderbook_manager=None, impact_model=None, slippage_model=None, fee_model=None):
        super().__init__()
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Store references to data sources and models
        self.orderbook_manager = orderbook_manager
        self.impact_model = impact_model
        self.slippage_model = slippage_model
        self.fee_model = fee_model
        
        # Initialize UI
        self.setWindowTitle("Trade Simulator")
        self.resize(1200, 800)
        
        # Apply custom stylesheet
        apply_stylesheet(self)
        
        # Create main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create UI components
        self.setup_ui()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Setup timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # Update every 100ms
    
    def setup_ui(self):
        # Create orderbook view tab
        self.orderbook_view = OrderbookView(self.orderbook_manager)
        self.tab_widget.addTab(self.orderbook_view, "Orderbook")
        
        # Create trading panel tab
        self.trade_panel = TradePanel(self.orderbook_manager)
        self.tab_widget.addTab(self.trade_panel, "Trading")
        
        # Create dashboard tab
        self.dashboard = Dashboard()
        self.tab_widget.addTab(self.dashboard, "Dashboard")
    
    # Add this method to the TradeSimulatorApp class
    def update_ui_with_orderbook_data(self):
        # Get latest orderbook data
        if self.orderbook_manager and self.orderbook_manager.get_current_orderbook():
            orderbook = self.orderbook_manager.get_current_orderbook()
            
            # Update dashboard statistics
            if hasattr(self, 'dashboard'):
                # Update processing time
                self.dashboard.update_latency_stat(orderbook.processing_time * 1000)  # ms
                
                # Update other metrics based on current simulation parameters
                if hasattr(self, 'trade_panel') and self.trade_panel.current_symbol:
                    symbol = self.trade_panel.current_symbol
                    quantity = self.trade_panel.get_current_quantity()
                    
                    # Calculate metrics
                    slippage = self.slippage_model.estimate_slippage(orderbook, quantity)
                    fees = self.fee_model.calculate_fees(quantity, orderbook.get_mid_price())
                    market_impact = self.impact_model.calculate_total_impact(quantity)
                    
                    # Update dashboard
                    self.dashboard.update_slippage_stat(slippage)
                    self.dashboard.update_fees_stat(fees)
                    self.dashboard.update_impact_stat(market_impact)
                    self.dashboard.update_total_cost_stat(slippage + fees + market_impact)
    
    # Add this method to fix the AttributeError
    def update_ui(self):
        # This method updates all UI components with latest data
        if hasattr(self, 'update_ui_with_orderbook_data'):
            self.update_ui_with_orderbook_data()
        
        # Update orderbook view if it exists
        if hasattr(self, 'orderbook_view'):
            self.orderbook_view.update()
    
    # Add a timer to periodically update the UI
    def setup_update_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui_with_orderbook_data)
        self.update_timer.start(100)  # Update every 100ms
    
    def closeEvent(self, event):
        # Clean up resources when closing
        self.update_timer.stop()
        if self.orderbook_manager:
            self.orderbook_manager.disconnect_all()
        self.logger.info("Application closed")
        event.accept()


def run_app(orderbook_manager=None):
    app = QApplication(sys.argv)
    window = TradeSimulatorApp(orderbook_manager)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()