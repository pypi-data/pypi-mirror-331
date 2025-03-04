import time
from collections import deque

class KeyBase:
    def __init__(self, key, client, idx):
        """Initialize a tracker for API requests and token usage."""
        self.request_log = deque()  # Stores (timestamp, token_count)
        self.key = key
        self.client = client(api_key=key)
        self.idx = idx

class Key(KeyBase):
    def __init__(self, key, client, idx):
        super().__init__(key, client, idx)
    
    def log_request(self, token_count):
        """Log an API request with token usage and clean up old entries."""
        current_time = time.time()
        self.request_log.append((current_time, token_count))
        
        # Remove requests older than 60 seconds
        self._cleanup_old_requests()

    def _cleanup_old_requests(self):
        """Remove requests older than 60 seconds."""
        current_time = time.time()
        while self.request_log and self.request_log[0][0] < current_time - 60:
            self.request_log.popleft()

    def get_rpm(self):
        """Return the number of requests in the last 60 seconds."""
        self._cleanup_old_requests()
        return len(self.request_log)

    def get_tpm(self):
        """Return the number of tokens used in the last 60 seconds."""
        self._cleanup_old_requests()
        return sum(tokens for _, tokens in self.request_log)

class AsyncKey(KeyBase):
    def __init__(self, key, client, idx):
        super().__init__(key, client, idx)

    async def get_rpm(self):
        """Return the number of requests in the last 60 seconds."""
        await self._cleanup_old_requests()
        return len(self.request_log)

    async def get_tpm(self):
        """Return the number of tokens used in the last 60 seconds."""
        await self._cleanup_old_requests()
        return sum(tokens for _, tokens in self.request_log)
    
    async def log_request(self, token_count):
        current_time = time.time()
        self.request_log.append((current_time, token_count))
        await self._cleanup_old_requests()
    
    async def _cleanup_old_requests(self):
        current_time = time.time()
        while self.request_log and self.request_log[0][0] < current_time - 60:
            self.request_log.popleft()