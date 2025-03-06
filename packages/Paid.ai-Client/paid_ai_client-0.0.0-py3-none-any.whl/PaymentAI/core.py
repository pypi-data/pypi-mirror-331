import requests
import logging
import threading
import json
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, List

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Generic type for the data field
T = TypeVar('T')

@dataclass
class Signal(Generic[T]):
    """
    Represents a signal event to be sent to the AgentPaid API.
    """
    event_name: str
    agent_id: str
    customer_id: str
    data: T


class PaidClient:
    """
    Client for the AgentPaid API.
    Collects signals and flushes them to the API periodically or when the buffer is full.
    """

    def __init__(self, api_key: str, api_url: str = 'https://api.agentpaid.io'):
        """
        Initialize the client with an API key and optional API URL.
        
        Args:
            api_key: The API key for authentication
            api_url: The base URL for the API (defaults to 'https://api.agentpaid.io')
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.signals: List[Signal[Any]] = []
        
        # Start the periodic flush timer
        self._start_timer()
        
        logger.info(f"ApClient initialized with endpoint: {self.api_url}")

    def _start_timer(self):
        """Start a timer to flush signals every 30 seconds"""
        self.timer = threading.Timer(30.0, self._timer_callback)
        self.timer.daemon = True  # Allow the program to exit even if timer is running
        self.timer.start()
        
    def _timer_callback(self):
        """Callback for the timer to flush signals and restart the timer"""
        try:
            self.flush()
        except Exception as e:
            logger.error(f"Error during automatic flush: {str(e)}")
        finally:
            self._start_timer()  # Restart the timer
            
    def flush(self):
        """
        Send all collected signals to the API and clear the buffer.
        """
        if not self.signals:
            logger.debug("No signals to flush")
            return
        
        url = f"{self.api_url}/api/entries/bulk"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        body = {
            "transactions": [vars(signal) for signal in self.signals]
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Successfully flushed {len(self.signals)} signals")
            self.signals = []
        except requests.RequestException as e:
            logger.error(f"Failed to flush signals: {str(e)}")
            raise RuntimeError(f"Failed to flush signals: {str(e)}")
    
    def record_usage(self, agent_id: str, external_user_id: str, signal_name: str, data: Any):
        """
        Record a usage signal.
        
        Args:
            agent_id: The ID of the agent
            external_user_id: The external user ID (customer)
            signal_name: The name of the signal event
            data: The data to include with the signal
        """
        signal = Signal(
            event_name=signal_name,
            agent_id=agent_id,
            customer_id=external_user_id,
            data=data
        )
        
        self.signals.append(signal)
        logger.debug(f"Recorded signal: {signal_name} for agent {agent_id}")
        
        # If buffer reaches 100 signals, flush immediately
        if len(self.signals) >= 100:
            logger.info("Signal buffer reached 100, flushing")
            self.flush()
    
    def __del__(self):
        """
        Cleanup method to flush remaining signals when the object is garbage collected.
        """
        try:
            # Cancel the timer
            if hasattr(self, 'timer'):
                self.timer.cancel()
            
            # Flush any remaining signals
            if self.signals:
                logger.info("Flushing signals during cleanup")
                self.flush()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")