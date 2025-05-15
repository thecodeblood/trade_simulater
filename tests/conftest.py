import pytest
import asyncio
from unittest.mock import MagicMock, patch
from src.data.orderbook import OrderBookManager, Orderbook

@pytest.fixture
def sample_orderbook_data():
    """Sample orderbook data for testing"""
    return {
        "bids": [
            ["50000.0", "1.5"],
            ["49900.0", "2.3"],
            ["49800.0", "3.1"],
        ],
        "asks": [
            ["50100.0", "1.2"],
            ["50200.0", "2.5"],
            ["50300.0", "3.0"],
        ]
    }

@pytest.fixture
def mock_orderbook():
    """Create a mock orderbook with sample data"""
    orderbook = Orderbook("BTC-USDT")
    orderbook.update_bids([[50000.0, 1.5], [49900.0, 2.3], [49800.0, 3.1]])
    orderbook.update_asks([[50100.0, 1.2], [50200.0, 2.5], [50300.0, 3.0]])
    return orderbook

@pytest.fixture
def mock_orderbook_manager():
    """Create a mock orderbook manager"""
    manager = MagicMock(spec=OrderBookManager)
    orderbook = mock_orderbook()
    manager.get_orderbook.return_value = orderbook
    manager.get_symbols.return_value = ["BTC-USDT"]
    return manager

@pytest.fixture
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()