import pytest
from src.models.market_impact import AlmgrenChrissModel

class TestAlmgrenChrissModel:
    def test_initialization(self):
        """Test model initialization"""
        model = AlmgrenChrissModel()
        assert model is not None
    
    def test_calculate_temporary_impact(self):
        """Test calculation of temporary market impact"""
        model = AlmgrenChrissModel()
        impact = model.calculate_temporary_impact(
            volume=10.0,
            sigma=0.01,
            daily_volume=1000.0,
            participation_rate=0.1
        )
        assert impact > 0
    
    def test_calculate_permanent_impact(self):
        """Test calculation of permanent market impact"""
        model = AlmgrenChrissModel()
        impact = model.calculate_permanent_impact(
            volume=10.0,
            sigma=0.01,
            daily_volume=1000.0
        )
        assert impact > 0
    
    def test_estimate_market_impact(self, mock_orderbook):
        """Test estimation of market impact using orderbook"""
        model = AlmgrenChrissModel()
        impact = model.estimate_market_impact(
            orderbook=mock_orderbook,
            side="buy",
            volume=1.0,
            price=50000.0
        )
        assert impact > 0