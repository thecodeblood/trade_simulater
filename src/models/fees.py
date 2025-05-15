import logging
import numpy as np
from enum import Enum
from abc import ABC, abstractmethod


class FeeType(Enum):
    """Enum representing different types of fees in cryptocurrency trading."""
    MAKER = 'maker'  # Fee for adding liquidity to the order book
    TAKER = 'taker'  # Fee for removing liquidity from the order book
    DEPOSIT = 'deposit'  # Fee for depositing funds
    WITHDRAWAL = 'withdrawal'  # Fee for withdrawing funds
    NETWORK = 'network'  # Blockchain network fee (gas fee)


class FeeStructure(Enum):
    """Enum representing different fee calculation structures."""
    FLAT = 'flat'  # Fixed fee regardless of trade size
    PERCENTAGE = 'percentage'  # Fee as a percentage of trade value
    TIERED = 'tiered'  # Fee based on trading volume tiers


class FeeCalculator(ABC):
    """Abstract base class for fee calculators.
    
    This class defines the interface for all fee calculator implementations.
    Different exchanges may have different fee structures, so this allows
    for flexible implementation of various fee models.
    """
    
    def __init__(self):
        """Initialize the fee calculator."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def calculate_fee(self, order_size, price, fee_type=FeeType.TAKER, **kwargs):
        """Calculate the fee for a given order.
        
        Args:
            order_size (float): Size of the order in base currency units
            price (float): Price per unit in quote currency
            fee_type (FeeType): Type of fee to calculate (maker, taker, etc.)
            **kwargs: Additional parameters specific to the fee structure
        
        Returns:
            float: Calculated fee in quote currency
        """
        pass


class PercentageFeeCalculator(FeeCalculator):
    """Fee calculator using percentage-based fee structure.
    
    This is the most common fee structure in cryptocurrency exchanges,
    where fees are calculated as a percentage of the total trade value.
    """
    
    def __init__(self, maker_fee=0.001, taker_fee=0.002, deposit_fee=0.0, withdrawal_fee=0.0005):
        """Initialize the percentage fee calculator.
        
        Args:
            maker_fee (float): Maker fee as a decimal (e.g., 0.001 for 0.1%)
            taker_fee (float): Taker fee as a decimal (e.g., 0.002 for 0.2%)
            deposit_fee (float): Deposit fee as a decimal
            withdrawal_fee (float): Withdrawal fee as a decimal
        """
        super().__init__()
        self.fee_rates = {
            FeeType.MAKER: maker_fee,
            FeeType.TAKER: taker_fee,
            FeeType.DEPOSIT: deposit_fee,
            FeeType.WITHDRAWAL: withdrawal_fee,
            FeeType.NETWORK: 0.0  # Network fees are typically not percentage-based
        }
    
    def calculate_fee(self, order_size, price, fee_type=FeeType.TAKER, **kwargs):
        """Calculate the fee for a given order using percentage-based structure.
        
        Args:
            order_size (float): Size of the order in base currency units
            price (float): Price per unit in quote currency
            fee_type (FeeType): Type of fee to calculate
            **kwargs: Additional parameters
        
        Returns:
            float: Calculated fee in quote currency
        """
        if not isinstance(fee_type, FeeType):
            try:
                fee_type = FeeType(fee_type)
            except ValueError:
                self.logger.warning(f"Invalid fee type: {fee_type}, using TAKER as default")
                fee_type = FeeType.TAKER
        
        # For network fees, use the provided value or a default
        if fee_type == FeeType.NETWORK:
            return kwargs.get('network_fee', 0.0)
        
        # Calculate the total trade value
        trade_value = order_size * price
        
        # Apply the appropriate fee rate
        fee_rate = self.fee_rates.get(fee_type, self.fee_rates[FeeType.TAKER])
        
        # Calculate the fee
        fee = trade_value * fee_rate
        
        return fee


class TieredFeeCalculator(FeeCalculator):
    """Fee calculator using tiered fee structure based on trading volume.
    
    Many exchanges offer reduced fees for users with higher trading volumes.
    This calculator implements a tiered fee structure where the fee rate
    decreases as the trading volume increases.
    """
    
    def __init__(self, maker_tiers=None, taker_tiers=None):
        """Initialize the tiered fee calculator.
        
        Args:
            maker_tiers (list): List of tuples (volume_threshold, fee_rate) for maker fees
            taker_tiers (list): List of tuples (volume_threshold, fee_rate) for taker fees
        """
        super().__init__()
        
        # Default tiers if none provided
        self.maker_tiers = maker_tiers or [
            (0, 0.001),       # 0.1% for volume < 50,000
            (50000, 0.0008),  # 0.08% for volume >= 50,000
            (100000, 0.0006), # 0.06% for volume >= 100,000
            (500000, 0.0004), # 0.04% for volume >= 500,000
            (1000000, 0.0002) # 0.02% for volume >= 1,000,000
        ]
        
        self.taker_tiers = taker_tiers or [
            (0, 0.002),       # 0.2% for volume < 50,000
            (50000, 0.0018),  # 0.18% for volume >= 50,000
            (100000, 0.0016), # 0.16% for volume >= 100,000
            (500000, 0.0014), # 0.14% for volume >= 500,000
            (1000000, 0.0012) # 0.12% for volume >= 1,000,000
        ]
    
    def _get_fee_rate(self, volume, tiers):
        """Get the fee rate for a given volume based on tiers.
        
        Args:
            volume (float): Trading volume
            tiers (list): List of tuples (volume_threshold, fee_rate)
        
        Returns:
            float: Fee rate as a decimal
        """
        # Sort tiers by volume threshold in descending order
        sorted_tiers = sorted(tiers, key=lambda x: x[0], reverse=True)
        
        # Find the applicable tier
        for threshold, rate in sorted_tiers:
            if volume >= threshold:
                return rate
        
        # If no tier matches (should not happen with proper setup)
        return sorted_tiers[-1][1]
    
    def calculate_fee(self, order_size, price, fee_type=FeeType.TAKER, **kwargs):
        """Calculate the fee for a given order using tiered fee structure.
        
        Args:
            order_size (float): Size of the order in base currency units
            price (float): Price per unit in quote currency
            fee_type (FeeType): Type of fee to calculate
            **kwargs: Additional parameters including 'trading_volume' for tier determination
        
        Returns:
            float: Calculated fee in quote currency
        """
        if not isinstance(fee_type, FeeType):
            try:
                fee_type = FeeType(fee_type)
            except ValueError:
                self.logger.warning(f"Invalid fee type: {fee_type}, using TAKER as default")
                fee_type = FeeType.TAKER
        
        # Calculate the total trade value
        trade_value = order_size * price
        
        # Get the user's trading volume (30-day or as specified)
        trading_volume = kwargs.get('trading_volume', 0.0)
        
        # Determine the fee rate based on the fee type and trading volume
        if fee_type == FeeType.MAKER:
            fee_rate = self._get_fee_rate(trading_volume, self.maker_tiers)
        elif fee_type == FeeType.TAKER:
            fee_rate = self._get_fee_rate(trading_volume, self.taker_tiers)
        elif fee_type == FeeType.NETWORK:
            return kwargs.get('network_fee', 0.0)
        else:
            # For other fee types, use a flat rate or calculate differently
            fee_rate = kwargs.get('fee_rate', 0.001)
        
        # Calculate the fee
        fee = trade_value * fee_rate
        
        return fee


class FlatFeeCalculator(FeeCalculator):
    """Fee calculator using flat fee structure.
    
    Some exchanges charge a fixed fee per transaction, regardless of the trade size.
    This calculator implements a flat fee structure.
    """
    
    def __init__(self, maker_fee=1.0, taker_fee=2.0, deposit_fee=0.0, withdrawal_fee=5.0):
        """Initialize the flat fee calculator.
        
        Args:
            maker_fee (float): Flat maker fee in quote currency
            taker_fee (float): Flat taker fee in quote currency
            deposit_fee (float): Flat deposit fee in quote currency
            withdrawal_fee (float): Flat withdrawal fee in quote currency
        """
        super().__init__()
        self.fee_rates = {
            FeeType.MAKER: maker_fee,
            FeeType.TAKER: taker_fee,
            FeeType.DEPOSIT: deposit_fee,
            FeeType.WITHDRAWAL: withdrawal_fee,
            FeeType.NETWORK: 0.0  # Network fees are handled separately
        }
    
    def calculate_fee(self, order_size, price, fee_type=FeeType.TAKER, **kwargs):
        """Calculate the fee for a given order using flat fee structure.
        
        Args:
            order_size (float): Size of the order in base currency units
            price (float): Price per unit in quote currency
            fee_type (FeeType): Type of fee to calculate
            **kwargs: Additional parameters
        
        Returns:
            float: Calculated fee in quote currency
        """
        if not isinstance(fee_type, FeeType):
            try:
                fee_type = FeeType(fee_type)
            except ValueError:
                self.logger.warning(f"Invalid fee type: {fee_type}, using TAKER as default")
                fee_type = FeeType.TAKER
        
        # For network fees, use the provided value or a default
        if fee_type == FeeType.NETWORK:
            return kwargs.get('network_fee', 0.0)
        
        # Return the flat fee for the specified fee type
        return self.fee_rates.get(fee_type, self.fee_rates[FeeType.TAKER])


class ExchangeFeeCalculator:
    """Factory class for creating and managing exchange-specific fee calculators.
    
    This class provides a unified interface for calculating fees across different
    exchanges, each with their own fee structures and rates.
    """
    
    def __init__(self):
        """Initialize the exchange fee calculator factory."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.exchange_calculators = {}
        self.default_calculator = PercentageFeeCalculator()
    
    def register_exchange(self, exchange_name, calculator):
        """Register a fee calculator for a specific exchange.
        
        Args:
            exchange_name (str): Name of the exchange
            calculator (FeeCalculator): Fee calculator instance for the exchange
        """
        self.exchange_calculators[exchange_name.lower()] = calculator
    
    def get_calculator(self, exchange_name=None):
        """Get the fee calculator for a specific exchange.
        
        Args:
            exchange_name (str, optional): Name of the exchange
        
        Returns:
            FeeCalculator: Fee calculator instance for the exchange
        """
        if exchange_name is None:
            return self.default_calculator
        
        calculator = self.exchange_calculators.get(exchange_name.lower())
        if calculator is None:
            self.logger.warning(f"No fee calculator registered for exchange: {exchange_name}, using default")
            return self.default_calculator
        
        return calculator
    
    def calculate_fee(self, order_size, price, exchange_name=None, fee_type=FeeType.TAKER, **kwargs):
        """Calculate the fee for a given order on a specific exchange.
        
        Args:
            order_size (float): Size of the order in base currency units
            price (float): Price per unit in quote currency
            exchange_name (str, optional): Name of the exchange
            fee_type (FeeType): Type of fee to calculate
            **kwargs: Additional parameters specific to the fee structure
        
        Returns:
            float: Calculated fee in quote currency
        """
        calculator = self.get_calculator(exchange_name)
        return calculator.calculate_fee(order_size, price, fee_type, **kwargs)


# Example usage and setup for common exchanges
def create_default_exchange_calculators():
    """Create and configure fee calculators for common exchanges.
    
    Returns:
        ExchangeFeeCalculator: Configured exchange fee calculator instance
    """
    factory = ExchangeFeeCalculator()
    
    # Register calculators for common exchanges with their fee structures
    # OKX
    okx_calculator = TieredFeeCalculator(
        maker_tiers=[
            (0, 0.0008),       # 0.08% for volume < 5,000,000
            (5000000, 0.0006),  # 0.06% for volume >= 5,000,000
            (10000000, 0.0004), # 0.04% for volume >= 10,000,000
            (20000000, 0.0002), # 0.02% for volume >= 20,000,000
        ],
        taker_tiers=[
            (0, 0.001),        # 0.1% for volume < 5,000,000
            (5000000, 0.0008),  # 0.08% for volume >= 5,000,000
            (10000000, 0.0006), # 0.06% for volume >= 10,000,000
            (20000000, 0.0004), # 0.04% for volume >= 20,000,000
        ]
    )
    factory.register_exchange('okx', okx_calculator)
    
    # Binance
    binance_calculator = TieredFeeCalculator(
        maker_tiers=[
            (0, 0.001),        # 0.1% for volume < 1,000,000
            (1000000, 0.0009),  # 0.09% for volume >= 1,000,000
            (5000000, 0.0008),  # 0.08% for volume >= 5,000,000
            (10000000, 0.0007), # 0.07% for volume >= 10,000,000
        ],
        taker_tiers=[
            (0, 0.001),        # 0.1% for volume < 1,000,000
            (1000000, 0.0009),  # 0.09% for volume >= 1,000,000
            (5000000, 0.0008),  # 0.08% for volume >= 5,000,000
            (10000000, 0.0007), # 0.07% for volume >= 10,000,000
        ]
    )
    factory.register_exchange('binance', binance_calculator)
    
    # Coinbase Pro
    coinbase_calculator = TieredFeeCalculator(
        maker_tiers=[
            (0, 0.005),        # 0.5% for volume < 10,000
            (10000, 0.0035),    # 0.35% for volume >= 10,000
            (50000, 0.0025),    # 0.25% for volume >= 50,000
            (100000, 0.002),    # 0.2% for volume >= 100,000
        ],
        taker_tiers=[
            (0, 0.006),        # 0.6% for volume < 10,000
            (10000, 0.004),     # 0.4% for volume >= 10,000
            (50000, 0.0025),    # 0.25% for volume >= 50,000
            (100000, 0.002),    # 0.2% for volume >= 100,000
        ]
    )
    factory.register_exchange('coinbase', coinbase_calculator)
    
    return factory


# Create a global instance for easy access
exchange_fee_calculator = create_default_exchange_calculators()


def calculate_total_cost(order_size, price, exchange_name=None, fee_type=FeeType.TAKER, **kwargs):
    """Calculate the total cost of a trade including fees.
    
    Args:
        order_size (float): Size of the order in base currency units
        price (float): Price per unit in quote currency
        exchange_name (str, optional): Name of the exchange
        fee_type (FeeType): Type of fee to calculate
        **kwargs: Additional parameters specific to the fee structure
    
    Returns:
        tuple: (total_cost, fee) in quote currency
    """
    # Calculate the base cost of the trade
    base_cost = order_size * price
    
    # Calculate the fee
    fee = exchange_fee_calculator.calculate_fee(
        order_size, price, exchange_name, fee_type, **kwargs
    )
    
    # Calculate the total cost (base cost + fee for buys, base cost - fee for sells)
    is_buy = kwargs.get('is_buy', True)
    if is_buy:
        total_cost = base_cost + fee
    else:
        total_cost = base_cost - fee
    
    return total_cost, fee