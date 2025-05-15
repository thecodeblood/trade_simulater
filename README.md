# Cryptocurrency Trading Simulator

A sophisticated trading simulator that implements advanced market models for cryptocurrency trading, featuring real-time orderbook visualization, trade execution simulation, and performance monitoring.

## Features

- **Real-time Orderbook Visualization**: Live display of market depth and price levels
- **Advanced Market Models**:
  - Almgren-Chriss Market Impact Model
  - Multiple Slippage Estimation Models
  - Dynamic Fee Calculation System
- **Performance Monitoring**: Real-time tracking of system performance metrics
- **Interactive Trading Interface**: User-friendly trade panel for order execution

## Architecture

### Core Components

- **Data Layer** (`src/data/`)
  - WebSocket client for real-time market data
  - Orderbook management system

- **Models** (`src/models/`)
  - Market impact calculation
  - Slippage estimation
  - Fee calculation

- **User Interface** (`src/ui/`)
  - Main application window
  - Orderbook visualization
  - Trading panel
  - Performance dashboard

- **Utilities** (`src/utils/`)
  - Performance monitoring
  - System metrics collection

## Installation

1. Clone the repository
```bash
   git clone <repository-url>
   cd Trader

2. Create and activate a virtual environment
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
3. Install dependencies
```bash
   pip install -r requirements.txt
``` 

## Usage
1. Run the application
```bash
   python src/main.py
```
2. Interact with the trading simulator through the user interface.
- Real-time orderbook display
- Trading interface
- Performance metrics dashboard

## Documentation
For detailed information on each component and its usage, please refer to the respective sections in the documentation.
- Market Impact Model
- Slippage Models
- Fee Calculation
- Performance Monitoring

## Testing
To run the test suite, use the following command:
```bash
   python -m pytest tests/ 
```

## Project Structure
```
src/
├── data/
│   ├── websocket_client.py
│   └── orderbook.py
├── models/
│   ├── market_impact.py
│   ├── slippage.py
│   └── fee.py
├── ui/
│   ├── main_window.py
│   ├── orderbook_widget.py
│   ├── trade_panel.py
│   └── performance_dashboard.py
├── utils/
│   ├── performance_monitor.py
│   └── system_metrics.py
└── main.py
```

## Contributing
- Fork the repository
- Create a feature branch
- Commit your changes
- Push to the branch
- Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

