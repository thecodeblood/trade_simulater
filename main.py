import asyncio
import sys
import json
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEventLoop
from src.data.orderbook import OrderBookManager
from src.ui.app import TradeSimulatorApp
from src.models.market_impact import AlmgrenChrissModel
from src.models.slippage import SlippageModelFactory
from src.models.fees import ExchangeFeeCalculator
from src.utils.performance import PerformanceMonitor

# Define models at the global scope
impact_model = None
slippage_model = None
fee_model = None

async def main():
    # Initialize models (these will be used later in the appropriate components)
    # Adjust parameters to avoid the warning
    global impact_model, slippage_model, fee_model
    
    impact_model_params = {
        'lambda_temp': 1e-6,
        'gamma': 0.1,
        'sigma': 0.3,
        'eta': 5e-7,  # Increased from default 2.5e-7
        'epsilon': 0.01,
        'tau': 1.0
    }
    impact_model = AlmgrenChrissModel(params=impact_model_params)
    slippage_model = SlippageModelFactory.create_model("auto")
    fee_model = ExchangeFeeCalculator()
    
    # Initialize the orderbook manager
    orderbook_manager = OrderBookManager()
    
    # Connect to WebSocket and start processing data
    await orderbook_manager.connect("wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP")
    
    # Return the orderbook manager for the UI to use
    return orderbook_manager

# Modify the run_qt_app function
def run_qt_app(orderbook_manager):
    # This function runs in the main thread
    app = QApplication(sys.argv)
    simulator = TradeSimulatorApp(
        orderbook_manager=orderbook_manager,
        impact_model=impact_model,  # Pass the models
        slippage_model=slippage_model,
        fee_model=fee_model
    )
    simulator.show()
    return app.exec()

if __name__ == "__main__":
    # Run the async part first to set up the orderbook manager
    orderbook_manager = asyncio.run(main())
    
    # Then run the Qt application in the main thread
    sys.exit(run_qt_app(orderbook_manager))

# Add to imports
from src.utils.performance import PerformanceMonitor

# Add to TradeSimulatorApp initialization
self.performance_monitor = PerformanceMonitor()

# Modify OrderBookManager to record processing times
def on_orderbook_update(self, orderbook):
    # Existing code...
    
    # Record performance metrics
    if hasattr(self.app, 'performance_monitor'):
        self.app.performance_monitor.record_processing_time(orderbook.processing_time * 1000)
        self.app.performance_monitor.record_memory_usage()