import pytest
from src.data.orderbook import Orderbook

class TestOrderbook:
    def test_initialization(self):
        """Test orderbook initialization"""
        orderbook = Orderbook("BTC-USDT")
        assert orderbook.symbol == "BTC-USDT"
        assert len(orderbook.bids) == 0
        assert len(orderbook.asks) == 0
    
    def test_update_bids(self):
        """Test updating bids"""
        orderbook = Orderbook("BTC-USDT")
        orderbook.update_bids([[50000.0, 1.5], [49900.0, 2.3]])
        
        assert len(orderbook.bids) == 2
        assert 50000.0 in orderbook.bids
        assert orderbook.bids[50000.0] == 1.5
    
    def test_update_asks(self):
        """Test updating asks"""
        orderbook = Orderbook("BTC-USDT")
        orderbook.update_asks([[50100.0, 1.2], [50200.0, 2.5]])
        
        assert len(orderbook.asks) == 2
        assert 50100.0 in orderbook.asks
        assert orderbook.asks[50100.0] == 1.2
    
    def test_get_best_bid(self, mock_orderbook):
        """Test getting best bid price"""
        best_bid = mock_orderbook.get_best_bid()
        assert best_bid == 50000.0
    
    def test_get_best_ask(self, mock_orderbook):
        """Test getting best ask price"""
        best_ask = mock_orderbook.get_best_ask()
        assert best_ask == 50100.0
    
    def test_get_mid_price(self, mock_orderbook):
        """Test getting mid price"""
        mid_price = mock_orderbook.get_mid_price()
        assert mid_price == 50050.0
    
    def test_get_spread(self, mock_orderbook):
        """Test getting spread"""
        spread = mock_orderbook.get_spread()
        assert spread == 100.0
    
    def test_get_volume_at_price(self, mock_orderbook):
        """Test getting volume at price"""
        volume = mock_orderbook.get_volume_at_price(50000.0)
        assert volume == 1.5