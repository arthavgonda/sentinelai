import asyncio
import time
from typing import Dict, Callable, Any, Optional
from datetime import datetime, timedelta
from config import settings
import logging

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, name: str, threshold: int = None, timeout: int = None):
        self.name = name
        self.threshold = threshold or settings.CIRCUIT_BREAKER_THRESHOLD
        self.timeout = timeout or settings.CIRCUIT_BREAKER_TIMEOUT
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"
        self.lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        async with self.lock:
            if self.state == "open":
                if self._should_attempt_reset():
                    self.state = "half_open"
                    logger.info(f"Circuit breaker {self.name} entering half-open state")
                else:
                    raise Exception(f"Circuit breaker {self.name} is open")
            elif self.state == "half_open":
                pass
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        async with self.lock:
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
                logger.info(f"Circuit breaker {self.name} closed after successful call")
            elif self.state == "closed":
                self.failure_count = 0
    
    async def _on_failure(self):
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.threshold:
                self.state = "open"
                logger.warning(f"Circuit breaker {self.name} opened after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
    
    def reset(self):
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

class CircuitBreakerManager:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def get_breaker(self, name: str) -> CircuitBreaker:
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(name)
        return self.breakers[name]
    
    def reset_breaker(self, name: str):
        if name in self.breakers:
            self.breakers[name].reset()

circuit_breaker_manager = CircuitBreakerManager()

