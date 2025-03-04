import asyncio
from .key import Key, AsyncKey

class KeyHandlerBase:
    def __init__(self, api_keys, client, verbose=False, metric="tpm"):
        self.verbose = verbose
        self.metric = metric
        self.metrics = {
            "tpm": lambda key: key.get_tpm(),
            "rps": lambda key: key.get_rpm(),
            "tpd": lambda key: key.get_tpm(),
            "rpd": lambda key: key.get_rpm(),
        }

class KeyHandler(KeyHandlerBase):
    def __init__(self, api_keys, client, **kwargs):
        super().__init__(api_keys, client, **kwargs)
        self.keys = [Key(key, client, i) for i, key in enumerate(api_keys)]

    def request(self, *args, **kwargs):
        key = self.get_lazy_key()
        response = key.client.chat.completions.create(*args, **kwargs)
        tokens = response.usage.total_tokens
        key.log_request(tokens)
        if self.verbose:
            print(f"Used key {key.key} with {tokens} tokens.")
        return response
    
    def get_lazy_key(self, metric="tpm"):
        
        assert metric in self.metrics.keys(), f"Availabel metrics: {list(self.metrics.keys())}."
        assert metric not in ["tpd", "rpd"], f"Method \"{metric}\" is not yet implemented."
        
        key = min(self.keys, key=self.metrics[metric])
        
        return key

class AsyncKeyHandler(KeyHandler):
    def __init__(self, api_keys, client, **kwargs):
        super().__init__(api_keys, client, **kwargs)
        self.keys = [AsyncKey(key, client, i) for i, key in enumerate(api_keys)]

    async def request(self, *args, **kwargs):
        key = await self.get_lazy_key()  # Async call to get a key
        response = await key.client.chat.completions.create(*args, **kwargs)  # Awaiting async call
        tokens = response.usage.total_tokens
        await key.log_request(tokens)
        if self.verbose:
            print(f"Used key {key.idx} for {tokens} tokens.")
        return response
    
    async def get_lazy_key(self, metric="tpm"):
        assert metric in self.metrics.keys(), f"Availabel metrics: {list(self.metrics.keys())}."
        assert metric not in ["tpd", "rpd"], f"Method \"{metric}\" is not yet implemented."
        
        tasks = [self.metrics[metric](key) for key in self.keys]
        metric_values = await asyncio.gather(*tasks)
        key = min(zip(self.keys, metric_values), key=lambda x: x[1])[0]
        
        return key