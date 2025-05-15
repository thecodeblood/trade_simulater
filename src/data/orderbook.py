import asyncio
import logging
import time
from collections import defaultdict
from .websocket_client import OrderbookWebSocketClient

class OrderBook:
    def __init__(self, symbol):
        """
        Initialize an orderbook for a specific trading symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., 'BTC-USDT')
        """
        self.symbol = symbol
        self.asks = {}  # Price -> Quantity mapping for asks
        self.bids = {}  # Price -> Quantity mapping for bids
        self.timestamp = 0
        self.last_update_time = 0
        self.processing_time = 0
        
        # Configure logging
        self.logger = logging.getLogger(f'OrderBook-{symbol}')
    
    def update(self, data):
        """
        Update the orderbook with new data.
        
        Args:
            data (dict): Orderbook data with asks and bids
        
        Returns:
            float: Processing time in milliseconds
        """
        start_time = time.time()
        
        try:
            # Update timestamp
            if 'timestamp' in data:
                self.timestamp = data['timestamp']
            
            # Update asks
            if 'asks' in data:
                for price_str, quantity_str in data['asks']:
                    price = float(price_str)
                    quantity = float(quantity_str)
                    
                    if quantity > 0:
                        self.asks[price] = quantity
                    else:
                        # Remove price level if quantity is 0
                        if price in self.asks:
                            del self.asks[price]
            
            # Update bids
            if 'bids' in data:
                for price_str, quantity_str in data['bids']:
                    price = float(price_str)
                    quantity = float(quantity_str)
                    
                    if quantity > 0:
                        self.bids[price] = quantity
                    else:
                        # Remove price level if quantity is 0
                        if price in self.bids:
                            del self.bids[price]
            
            self.last_update_time = time.time()
            self.processing_time = self.last_update_time - start_time
            
            return self.processing_time * 1000  # Convert to milliseconds
            
        except Exception as e:
            self.logger.error(f"Error updating orderbook: {e}")
            return 0
    
    def get_best_ask(self):
        """
        Get the best (lowest) ask price and quantity.
        
        Returns:
            tuple: (price, quantity) or (None, None) if no asks
        """
        if not self.asks:
            return None, None
        
        best_price = min(self.asks.keys())
        return best_price, self.asks[best_price]
    
    def get_best_bid(self):
        """
        Get the best (highest) bid price and quantity.
        
        Returns:
            tuple: (price, quantity) or (None, None) if no bids
        """
        if not self.bids:
            return None, None
        
        best_price = max(self.bids.keys())
        return best_price, self.bids[best_price]
    
    def get_spread(self):
        """
        Calculate the spread between best ask and best bid.
        
        Returns:
            float: Spread or None if either ask or bid is missing
        """
        best_ask, _ = self.get_best_ask()
        best_bid, _ = self.get_best_bid()
        
        if best_ask is None or best_bid is None:
            return None
        
        return best_ask - best_bid
    
    def get_mid_price(self):
        """
        Calculate the mid price between best ask and best bid.
        
        Returns:
            float: Mid price or None if either ask or bid is missing
        """
        best_ask, _ = self.get_best_ask()
        best_bid, _ = self.get_best_bid()
        
        if best_ask is None or best_bid is None:
            return None
        
        return (best_ask + best_bid) / 2
    
    def get_volume_at_price(self, side, price):
        """
        Get the volume available at a specific price level.
        
        Args:
            side (str): 'ask' or 'bid'
            price (float): Price level
        
        Returns:
            float: Volume at the specified price or 0 if not available
        """
        if side.lower() == 'ask':
            return self.asks.get(price, 0)
        elif side.lower() == 'bid':
            return self.bids.get(price, 0)
        else:
            return 0
    
    def get_volume_up_to_price(self, side, price):
        """
        Calculate the cumulative volume up to a specific price level.
        
        Args:
            side (str): 'ask' or 'bid'
            price (float): Price level
        
        Returns:
            float: Cumulative volume
        """
        volume = 0
        
        if side.lower() == 'ask':
            for p, q in self.asks.items():
                if p <= price:
                    volume += q
        elif side.lower() == 'bid':
            for p, q in self.bids.items():
                if p >= price:
                    volume += q
        
        return volume
    
    def get_price_for_volume(self, side, volume):
        """
        Calculate the price needed to execute a specific volume.
        
        Args:
            side (str): 'ask' or 'bid'
            volume (float): Volume to execute
        
        Returns:
            float: Weighted average price or None if not enough liquidity
        """
        remaining_volume = volume
        total_cost = 0
        
        if side.lower() == 'ask':
            # Sort asks by price (ascending)
            sorted_prices = sorted(self.asks.keys())
            
            for price in sorted_prices:
                available_volume = self.asks[price]
                
                if remaining_volume <= available_volume:
                    # We can fulfill the remaining volume at this price
                    total_cost += remaining_volume * price
                    remaining_volume = 0
                    break
                else:
                    # Take all available volume at this price and continue
                    total_cost += available_volume * price
                    remaining_volume -= available_volume
        
        elif side.lower() == 'bid':
            # Sort bids by price (descending)
            sorted_prices = sorted(self.bids.keys(), reverse=True)
            
            for price in sorted_prices:
                available_volume = self.bids[price]
                
                if remaining_volume <= available_volume:
                    # We can fulfill the remaining volume at this price
                    total_cost += remaining_volume * price
                    remaining_volume = 0
                    break
                else:
                    # Take all available volume at this price and continue
                    total_cost += available_volume * price
                    remaining_volume -= available_volume
        
        if remaining_volume > 0:
            # Not enough liquidity to fulfill the requested volume
            return None
        
        return total_cost / volume  # Weighted average price


class OrderBookManager:
    def __init__(self):
        """
        Initialize the orderbook manager to handle multiple orderbooks.
        """
        self.orderbooks = {}
        self.websocket_clients = {}
        self.logger = logging.getLogger('OrderBookManager')
    
    async def connect(self, url, symbol=None):
        """
        Connect to a WebSocket endpoint and start processing orderbook data.
        
        Args:
            url (str): WebSocket endpoint URL
            symbol (str, optional): Trading symbol. If None, extracted from URL.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Extract symbol from URL if not provided
            if symbol is None:
                # Example URL: wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP
                parts = url.split('/')
                symbol = parts[-1]  # Get the last part of the URL
            
            # Create orderbook if it doesn't exist
            if symbol not in self.orderbooks:
                self.orderbooks[symbol] = OrderBook(symbol)
            
            # Create and connect WebSocket client
            client = OrderbookWebSocketClient(
                url=url,
                symbol=symbol,
                on_message_callback=lambda data: self._process_message(symbol, data),
                on_error_callback=lambda error: self.logger.error(f"WebSocket error for {symbol}: {error}")
            )
            
            client.connect()
            self.websocket_clients[symbol] = client
            
            # Wait for initial data
            await asyncio.sleep(2)  # Give some time for initial data to arrive
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to {url}: {e}")
            return False
    
    def _process_message(self, symbol, data):
        """
        Process incoming WebSocket messages and update the orderbook.
        
        Args:
            symbol (str): Trading symbol
            data (dict): Message data
        """
        if symbol in self.orderbooks:
            processing_time = self.orderbooks[symbol].update(data)
            self.logger.debug(f"Updated orderbook for {symbol}. Processing time: {processing_time:.2f}ms")
    
    def get_orderbook(self, symbol):
        """
        Get the orderbook for a specific symbol.
        
        Args:
            symbol (str): Trading symbol
        
        Returns:
            OrderBook: Orderbook instance or None if not found
        """
        return self.orderbooks.get(symbol)
    
    def get_current_orderbook(self):
        """
        Get the orderbook for the currently selected symbol.
        
        Returns:
            OrderBook: Current orderbook instance or None if not found
        """
        # This assumes that the current symbol is stored somewhere accessible
        # You might need to modify this to get the current symbol from the appropriate place
        if hasattr(self, 'current_symbol') and self.current_symbol:
            return self.get_orderbook(self.current_symbol)
        return None
    
    def disconnect_all(self):
        """
        Disconnect all WebSocket clients.
        """
        for symbol, client in self.websocket_clients.items():
            client.disconnect()
            self.logger.info(f"Disconnected WebSocket client for {symbol}")
        
        self.websocket_clients = {}