import pytest
from src.models.market_impact import AlmgrenChrissModel
from src.models.slippage import SlippageModelFactory
from src.models.fees import ExchangeFeeCalculator

class TestDataModelIntegration:
    def test_market_impact_with_orderbook(self, mock_orderbook):
        """Test market impact model with orderbook data"""
        model = AlmgrenChrissModel()
        impact = model.estimate_market_impact(
            orderbook=mock_orderbook,
            side="buy",
            volume=1.0,
            price=50000.0
        )
        assert impact > 0
    
    def test_slippage_with_orderbook(self, mock_orderbook):
        """Test slippage model with orderbook data"""
        model = SlippageModelFactory.create("orderbook")
        slippage = model.estimate_slippage(
            orderbook=mock_orderbook,
            side="buy",
            volume=1.0,
            price=50000.0
        )
        assert slippage >= 0
    
    def test_total_transaction_cost(self, mock_orderbook):
        """Test calculation of total transaction cost"""
        impact_model = AlmgrenChrissModel()
        slippage_model = SlippageModelFactory.create("orderbook")
        fee_model = ExchangeFeeCalculator()
        
        # Calculate individual components
        impact = impact_model.estimate_market_impact(
            orderbook=mock_orderbook,
            side="buy",
            volume=1.0,
            price=50000.0
        )
        
        slippage = slippage_model.estimate_slippage(
            orderbook=mock_orderbook,
            side="buy",
            volume=1.0,
            price=50000.0
        )
        
        fee = fee_model.calculate_fee(
            exchange="okx",
            fee_type="taker",
            volume=1.0,
            price=50000.0
        )
        
        # Total cost should be the sum of all components
        total_cost = impact + slippage + fee
        assert total_cost > 0