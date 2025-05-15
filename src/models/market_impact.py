import numpy as np
import logging

class AlmgrenChrissModel:
    """
    Implementation of the Almgren-Chriss model for market impact estimation.
    
    The model divides market impact into two components:
    1. Temporary impact: Affects only the current trade and decays afterward
    2. Permanent impact: Persists in the market and affects all future trades
    
    The model helps determine the optimal trading trajectory to minimize
    the combination of market impact costs and volatility risk.
    """
    
    def __init__(self, params=None):
        """
        Initialize the Almgren-Chriss model with market parameters.
        
        Args:
            params (dict, optional): Model parameters including:
                - lambda_temp (float): Temporary market impact factor
                - gamma (float): Risk aversion parameter
                - sigma (float): Volatility of the asset
                - eta (float): Permanent market impact factor
                - epsilon (float): Fixed cost of trading (e.g., half spread)
                - tau (float): Time interval between trades
        """
        # Default parameters if none provided
        if params is None:
            params = {
                'lambda_temp': 1e-6,  # Temporary impact factor
                'gamma': 0.1,         # Risk aversion
                'sigma': 0.3,         # Volatility
                'eta': 2.5e-7,        # Permanent impact factor
                'epsilon': 0.01,      # Fixed trading cost
                'tau': 1.0            # Time interval
            }
        
        self.lambda_temp = params.get('lambda_temp', 1e-6)
        self.gamma = params.get('gamma', 0.1)
        self.sigma = params.get('sigma', 0.3)
        self.eta = params.get('eta', 2.5e-7)
        self.epsilon = params.get('epsilon', 0.01)
        self.tau = params.get('tau', 1.0)
        
        # Adjusted permanent impact parameter
        self.eta_tilde = self.eta - 0.5 * self.gamma * self.tau
        
        # Ensure model assumptions are valid
        if self.eta_tilde <= 0:
            logging.warning("Model assumption violated: Adjusted permanent impact must be positive")
            self.eta_tilde = 1e-8  # Set to small positive value
        
        # Calculate kappa parameter for optimal trajectory
        self.kappa_tilde_squared = (self.lambda_temp * self.sigma**2) / self.eta_tilde
        self.kappa = np.arccosh(0.5 * (self.kappa_tilde_squared * self.tau**2) + 1) / self.tau
        
        self.logger = logging.getLogger('AlmgrenChrissModel')
    
    def calculate_temporary_impact(self, trade_size, time_interval=None):
        """
        Calculate the temporary market impact for a given trade size.
        
        Args:
            trade_size (float): Size of the trade in units
            time_interval (float, optional): Time interval for the trade
                                            (defaults to self.tau)
        
        Returns:
            float: Temporary market impact cost
        """
        if time_interval is None:
            time_interval = self.tau
        
        # Trading rate (shares per unit time)
        trading_rate = trade_size / time_interval
        
        # Temporary impact formula: epsilon * sign(trade_size) + lambda * trading_rate
        # For simplicity, we use absolute value instead of sign function
        impact = self.epsilon * np.sign(trade_size) + self.lambda_temp * trading_rate
        
        return impact * abs(trade_size)  # Total cost = impact per share * shares
    
    def calculate_permanent_impact(self, trade_size, time_interval=None):
        """
        Calculate the permanent market impact for a given trade size.
        
        Args:
            trade_size (float): Size of the trade in units
            time_interval (float, optional): Time interval for the trade
                                            (defaults to self.tau)
        
        Returns:
            float: Permanent market impact (price change)
        """
        if time_interval is None:
            time_interval = self.tau
        
        # Trading rate (shares per unit time)
        trading_rate = trade_size / time_interval
        
        # Permanent impact formula: eta * trading_rate
        impact = self.eta * trading_rate
        
        return impact
    
    def optimal_trajectory(self, total_size, time_horizon, num_periods):
        """
        Calculate the optimal trading trajectory to minimize cost and risk.
        
        Args:
            total_size (float): Total position size to execute
            time_horizon (float): Total time for execution
            num_periods (int): Number of trading periods
        
        Returns:
            tuple: (holdings, trades) arrays with optimal trajectory
        """
        # Time interval between trades
        tau = time_horizon / num_periods
        
        # Initialize arrays for holdings and trades
        holdings = np.zeros(num_periods + 1)
        trades = np.zeros(num_periods)
        
        # Initial position
        holdings[0] = total_size
        
        # Calculate sinh and cosh terms for the formula
        sinh_term = np.sinh(self.kappa * np.arange(num_periods + 1) * tau)
        sinh_kappa_T = np.sinh(self.kappa * time_horizon)
        
        # Calculate optimal holdings at each time step
        for j in range(num_periods + 1):
            holdings[j] = total_size * sinh_term[num_periods - j] / sinh_kappa_T
        
        # Calculate trades at each time step (negative for sells)
        for j in range(num_periods):
            trades[j] = holdings[j] - holdings[j + 1]
        
        return holdings, trades
    
    def estimate_total_cost(self, trades, time_interval=None):
        """
        Estimate the total cost of executing a series of trades.
        
        Args:
            trades (array-like): Array of trade sizes
            time_interval (float, optional): Time interval for each trade
        
        Returns:
            dict: Dictionary with cost components:
                - temporary_impact: Cost due to temporary impact
                - permanent_impact: Cost due to permanent impact
                - volatility_risk: Cost due to volatility risk
                - total_cost: Sum of all costs
        """
        if time_interval is None:
            time_interval = self.tau
        
        # Initialize cost components
        temporary_impact = 0.0
        permanent_impact = 0.0
        volatility_risk = 0.0
        
        # Current holdings after each trade
        holdings = np.zeros(len(trades) + 1)
        holdings[0] = sum(trades)  # Initial position
        
        for i in range(len(trades)):
            # Update holdings
            holdings[i + 1] = holdings[i] - trades[i]
            
            # Calculate temporary impact cost
            temp_impact = self.calculate_temporary_impact(trades[i], time_interval)
            temporary_impact += temp_impact
            
            # Calculate permanent impact cost (affects all future trades)
            perm_impact = self.calculate_permanent_impact(trades[i], time_interval)
            permanent_impact += perm_impact * holdings[i + 1]  # Impact on remaining position
            
            # Calculate volatility risk cost
            volatility_risk += 0.5 * self.gamma * (self.sigma**2) * (holdings[i]**2) * time_interval
        
        # Total cost
        total_cost = temporary_impact + permanent_impact + volatility_risk
        
        return {
            'temporary_impact': temporary_impact,
            'permanent_impact': permanent_impact,
            'volatility_risk': volatility_risk,
            'total_cost': total_cost
        }
    
    def estimate_market_impact(self, order_size, current_price, orderbook, side='buy'):
        """
        Estimate market impact for a specific order using orderbook data.
        
        Args:
            order_size (float): Size of the order in units
            current_price (float): Current mid-price of the asset
            orderbook (OrderBook): Orderbook instance with market depth data
            side (str): 'buy' or 'sell'
        
        Returns:
            dict: Dictionary with impact estimates:
                - price_impact: Estimated price impact in currency units
                - relative_impact: Impact as percentage of current price
                - slippage: Estimated slippage cost
        """
        # Default to simple model if orderbook is None
        if orderbook is None:
            # Simple square-root model as fallback
            impact_factor = 0.1  # Default impact factor
            price_impact = impact_factor * current_price * np.sqrt(order_size)
            
            return {
                'price_impact': price_impact,
                'relative_impact': price_impact / current_price,
                'slippage': price_impact * order_size
            }
        
        try:
            # Use orderbook data to calculate a more accurate impact
            # For buys, we look at the ask side; for sells, the bid side
            impact_side = 'ask' if side.lower() == 'buy' else 'bid'
            
            # Get the weighted average price for the order size
            executed_price = orderbook.get_price_for_volume(impact_side, order_size)
            
            if executed_price is None:
                # Not enough liquidity in the orderbook
                self.logger.warning(f"Not enough liquidity in orderbook for {order_size} units")
                # Fall back to model-based estimate
                return self.estimate_market_impact(order_size, current_price, None, side)
            
            # Calculate price impact and slippage
            if side.lower() == 'buy':
                price_impact = executed_price - current_price
            else:  # sell
                price_impact = current_price - executed_price
            
            # Ensure price impact is non-negative
            price_impact = max(0, price_impact)
            
            return {
                'price_impact': price_impact,
                'relative_impact': price_impact / current_price,
                'slippage': price_impact * order_size
            }
            
        except Exception as e:
            self.logger.error(f"Error estimating market impact: {e}")
            # Fall back to model-based estimate
            return self.estimate_market_impact(order_size, current_price, None, side)