import json
import time
import logging
import websocket
from threading import Thread

class OrderbookWebSocketClient:
    def __init__(self, url, symbol, on_message_callback=None, on_error_callback=None):
        """
        Initialize the WebSocket client for orderbook data.
        
        Args:
            url (str): WebSocket endpoint URL
            symbol (str): Trading symbol (e.g., 'BTC-USDT')
            on_message_callback (callable): Callback for processing messages
            on_error_callback (callable): Callback for handling errors
        """
        self.url = url
        self.symbol = symbol
        self.on_message_callback = on_message_callback
        self.on_error_callback = on_error_callback
        self.ws = None
        self.thread = None
        self.running = False
        self.last_update_time = 0
        self.latency = 0
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('OrderbookWebSocketClient')
    
    def on_message(self, ws, message):
        """
        Handle incoming WebSocket messages.
        
        Args:
            ws: WebSocket connection
            message (str): Message received from WebSocket
        """
        try:
            # Measure latency
            receive_time = time.time()
            self.latency = receive_time - self.last_update_time
            self.last_update_time = receive_time
            
            # Parse message
            data = json.loads(message)
            
            # Call the callback if provided
            if self.on_message_callback:
                self.on_message_callback(data)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            if self.on_error_callback:
                self.on_error_callback(e)
    
    def on_error(self, ws, error):
        """
        Handle WebSocket errors.
        
        Args:
            ws: WebSocket connection
            error: Error object
        """
        self.logger.error(f"WebSocket error: {error}")
        if self.on_error_callback:
            self.on_error_callback(error)
    
    def on_close(self, ws, close_status_code, close_msg):
        """
        Handle WebSocket connection close.
        
        Args:
            ws: WebSocket connection
            close_status_code: Status code for connection close
            close_msg: Close message
        """
        self.logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        self.running = False
    
    def on_open(self, ws):
        """
        Handle WebSocket connection open.
        
        Args:
            ws: WebSocket connection
        """
        self.logger.info(f"WebSocket connection established for {self.symbol}")
        self.running = True
        self.last_update_time = time.time()
    
    def connect(self):
        """
        Establish WebSocket connection and start processing in a separate thread.
        """
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()
        
        self.logger.info(f"Started WebSocket client for {self.symbol}")
    
    def disconnect(self):
        """
        Disconnect from WebSocket.
        """
        if self.ws:
            self.ws.close()
            self.running = False
            self.logger.info(f"Disconnected WebSocket client for {self.symbol}")
    
    def get_latency(self):
        """
        Get the current latency in milliseconds.
        
        Returns:
            float: Latency in milliseconds
        """
        return self.latency * 1000  # Convert to milliseconds