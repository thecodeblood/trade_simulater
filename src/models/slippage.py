import numpy as np
import pandas as pd
import logging
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split


class SlippageEstimator:
    """
    Base class for slippage estimation models.
    
    Slippage is the difference between the expected price of a trade and the price
    at which the trade is actually executed. This class provides methods to estimate
    slippage based on various factors like order size, market volatility, and liquidity.
    """
    
    def __init__(self):
        """
        Initialize the slippage estimator.
        """
        self.logger = logging.getLogger('SlippageEstimator')
    
    def estimate(self, order_size, current_price, **kwargs):
        """
        Estimate slippage for a given order.
        
        Args:
            order_size (float): Size of the order in units
            current_price (float): Current price of the asset
            **kwargs: Additional parameters specific to the model
        
        Returns:
            float: Estimated slippage in currency units
        """
        raise NotImplementedError("Subclasses must implement this method")


class SimpleSlippageModel(SlippageEstimator):
    """
    A simple model for slippage estimation based on order size and price.
    
    This model uses a square-root formula commonly used in market impact models,
    where slippage is proportional to the square root of the order size relative
    to market volume.
    """
    
    def __init__(self, impact_factor=0.1, market_volume=None):
        """
        Initialize the simple slippage model.
        
        Args:
            impact_factor (float): Factor controlling the impact magnitude
            market_volume (float, optional): Typical market volume for normalization
        """
        super().__init__()
        self.impact_factor = impact_factor
        self.market_volume = market_volume
    
    def estimate(self, order_size, current_price, market_volume=None, volatility=None, **kwargs):
        """
        Estimate slippage using a simple square-root model.
        
        Args:
            order_size (float): Size of the order in units
            current_price (float): Current price of the asset
            market_volume (float, optional): Current market volume
            volatility (float, optional): Current market volatility
            **kwargs: Additional parameters
        
        Returns:
            float: Estimated slippage in currency units
        """
        # Use provided market volume or default
        volume = market_volume if market_volume is not None else self.market_volume
        
        # If no volume information is available, use a simple percentage model
        if volume is None:
            # Adjust impact factor based on volatility if provided
            adjusted_factor = self.impact_factor
            if volatility is not None:
                adjusted_factor *= (1 + volatility)
            
            # Simple percentage of price * sqrt(order_size)
            slippage = adjusted_factor * current_price * np.sqrt(order_size)
        else:
            # Square-root model normalized by market volume
            slippage = self.impact_factor * current_price * np.sqrt(order_size / volume)
        
        return slippage


class OrderbookSlippageModel(SlippageEstimator):
    """
    Slippage model based on orderbook data.
    
    This model uses the actual orderbook to calculate the expected slippage
    by simulating the execution of the order through the available liquidity.
    """
    
    def __init__(self, additional_factor=1.1):
        """
        Initialize the orderbook-based slippage model.
        
        Args:
            additional_factor (float): Factor to account for additional slippage
                                      beyond what's visible in the orderbook
        """
        super().__init__()
        self.additional_factor = additional_factor
    
    def estimate(self, order_size, current_price, orderbook=None, side='buy', **kwargs):
        """
        Estimate slippage using orderbook data.
        
        Args:
            order_size (float): Size of the order in units
            current_price (float): Current price of the asset (usually mid-price)
            orderbook (OrderBook): Orderbook instance with market depth data
            side (str): 'buy' or 'sell'
            **kwargs: Additional parameters
        
        Returns:
            float: Estimated slippage in currency units
        """
        if orderbook is None:
            self.logger.warning("No orderbook provided, falling back to simple model")
            simple_model = SimpleSlippageModel()
            return simple_model.estimate(order_size, current_price, **kwargs)
        
        try:
            # For buys, we look at the ask side; for sells, the bid side
            impact_side = 'ask' if side.lower() == 'buy' else 'bid'
            
            # Get the weighted average price for the order size
            executed_price = orderbook.get_price_for_volume(impact_side, order_size)
            
            if executed_price is None:
                # Not enough liquidity in the orderbook
                self.logger.warning(f"Not enough liquidity in orderbook for {order_size} units")
                # Fall back to simple model
                simple_model = SimpleSlippageModel()
                return simple_model.estimate(order_size, current_price, **kwargs)
            
            # Calculate slippage as the difference between executed price and current price
            if side.lower() == 'buy':
                slippage = executed_price - current_price
            else:  # sell
                slippage = current_price - executed_price
            
            # Apply additional factor to account for hidden costs
            slippage *= self.additional_factor
            
            # Ensure slippage is non-negative
            slippage = max(0, slippage)
            
            return slippage
            
        except Exception as e:
            self.logger.error(f"Error estimating slippage from orderbook: {e}")
            # Fall back to simple model
            simple_model = SimpleSlippageModel()
            return simple_model.estimate(order_size, current_price, **kwargs)


class RegressionSlippageModel(SlippageEstimator):
    """
    Machine learning-based slippage estimation using regression models.
    
    This model uses historical trade data to train a regression model that
    predicts slippage based on various features like order size, volatility,
    spread, and market conditions.
    """
    
    def __init__(self, model_type='linear'):
        """
        Initialize the regression-based slippage model.
        
        Args:
            model_type (str): Type of regression model to use
                             ('linear', 'ridge', 'lasso', 'random_forest')
        """
        super().__init__()
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_names = None
    
    def _create_model(self):
        """
        Create the regression model based on the specified type.
        
        Returns:
            object: Scikit-learn model instance
        """
        if self.model_type == 'linear':
            return LinearRegression()
        elif self.model_type == 'ridge':
            return Ridge(alpha=1.0)
        elif self.model_type == 'lasso':
            return Lasso(alpha=0.1)
        elif self.model_type == 'random_forest':
            return RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            self.logger.warning(f"Unknown model type: {self.model_type}, using linear regression")
            return LinearRegression()
    
    def train(self, historical_data):
        """
        Train the regression model using historical trade data.
        
        Args:
            historical_data (DataFrame): DataFrame containing historical trades with features
                                        and actual slippage values
        
        Returns:
            float: Model score (R^2) on the test set
        """
        try:
            # Check if the required columns are present
            required_columns = ['order_size', 'volatility', 'spread', 'market_volume', 'slippage']
            missing_columns = [col for col in required_columns if col not in historical_data.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns in historical data: {missing_columns}")
                return 0.0
            
            # Extract features and target
            X = historical_data.drop('slippage', axis=1)
            y = historical_data['slippage']
            
            # Store feature names for prediction
            self.feature_names = X.columns.tolist()
            
            # Split data into training and test sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Create and fit the pipeline with scaling
            self.scaler = StandardScaler()
            self.model = self._create_model()
            
            # Fit the scaler
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            # Train the model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate the model
            X_test_scaled = self.scaler.transform(X_test)
            score = self.model.score(X_test_scaled, y_test)
            
            self.logger.info(f"Trained {self.model_type} regression model with R^2 score: {score:.4f}")
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error training regression model: {e}")
            return 0.0
    
    def estimate(self, order_size, current_price, **kwargs):
        """
        Estimate slippage using the trained regression model.
        
        Args:
            order_size (float): Size of the order in units
            current_price (float): Current price of the asset
            **kwargs: Additional features for the model (e.g., volatility, spread, market_volume)
        
        Returns:
            float: Estimated slippage in currency units
        """
        if self.model is None:
            self.logger.warning("Model not trained, falling back to simple model")
            simple_model = SimpleSlippageModel()
            return simple_model.estimate(order_size, current_price, **kwargs)
        
        try:
            # Create feature vector
            features = {'order_size': order_size}
            
            # Add additional features from kwargs
            for feature in self.feature_names:
                if feature != 'order_size' and feature in kwargs:
                    features[feature] = kwargs[feature]
                elif feature != 'order_size':
                    # If a required feature is missing, use a default value or log warning
                    self.logger.warning(f"Missing feature: {feature}, using default value")
                    features[feature] = 0.0
            
            # Convert to DataFrame with correct column order
            X = pd.DataFrame([features])[self.feature_names]
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict slippage
            slippage_prediction = self.model.predict(X_scaled)[0]
            
            # Convert to absolute value and scale by current price if needed
            slippage = abs(slippage_prediction)
            
            # If the model was trained on percentage slippage, convert to currency units
            if slippage < 0.1:  # Heuristic to detect if prediction is in percentage
                slippage *= current_price
            
            return slippage
            
        except Exception as e:
            self.logger.error(f"Error predicting slippage with regression model: {e}")
            # Fall back to simple model
            simple_model = SimpleSlippageModel()
            return simple_model.estimate(order_size, current_price, **kwargs)


class SlippageModelFactory:
    """
    Factory class to create appropriate slippage models based on available data.
    """
    
    @staticmethod
    def create_model(model_type='auto', **kwargs):
        """
        Create a slippage model based on the specified type and available data.
        
        Args:
            model_type (str): Type of model to create
                             ('simple', 'orderbook', 'regression', 'auto')
            **kwargs: Additional parameters for the specific model
        
        Returns:
            SlippageEstimator: Instance of a slippage estimation model
        """
        if model_type == 'simple':
            return SimpleSlippageModel(**kwargs)
        elif model_type == 'orderbook':
            return OrderbookSlippageModel(**kwargs)
        elif model_type == 'regression':
            return RegressionSlippageModel(**kwargs)
        elif model_type == 'auto':
            # Determine the best model based on available data
            if 'historical_data' in kwargs and len(kwargs['historical_data']) > 100:
                # If we have enough historical data, use regression model
                model = RegressionSlippageModel(**kwargs)
                if 'historical_data' in kwargs:
                    model.train(kwargs['historical_data'])
                return model
            elif 'orderbook' in kwargs and kwargs['orderbook'] is not None:
                # If we have orderbook data, use orderbook model
                return OrderbookSlippageModel(**kwargs)
            else:
                # Fall back to simple model
                return SimpleSlippageModel(**kwargs)
        else:
            logging.warning(f"Unknown model type: {model_type}, using simple model")
            return SimpleSlippageModel(**kwargs)