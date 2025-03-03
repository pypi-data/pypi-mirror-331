from .key import Key

class KeyHandler:
    def __init__(self, api_keys, client):
        self.keys = [Key(key, client, i) for i, key in enumerate(api_keys)]
        #self.clients = [client(api_key=key.key) for key in keys]

        self.metrics = {
            "tpm": lambda key: key.get_tpm(),
            "rps": lambda key: key.get_rpm(),
            "tpd": lambda key: key.get_tpm(),
            "rpd": lambda key: key.get_rpm(),
        }

    def request(self, *args, **kwargs):
        key = self.get_lazy_key()
        response = key.client.chat.completions.create(*args, **kwargs)
        tokens = response.usage.total_tokens
        key.log_request(tokens)
        print(f"Used key {key.key} with {tokens} tokens.")
        return response
    
    def get_lazy_key(self, metric="tpm"):
        
        assert metric in self.metrics.keys(), f"Availabel metrics: {list(self.metrics.keys())}."
        assert metric not in ["tpd", "rpd"], f"Method \"{metric}\" is not yet implemented."
        
        key = min(self.keys, key=self.metrics[metric])
        
        return key

class AsyncKeyHandler(KeyHandler):
    async def request(self, *args, **kwargs):
        key = await self.get_lazy_key()  # Async call to get a key
        response = await key.client.chat.completions.create(*args, **kwargs)  # Awaiting async call
        tokens = response.usage.total_tokens
        await key.log_request(tokens)
        print(f"Used key {key.key} with {tokens} tokens.")
        return response
    
    async def get_lazy_key(self, metric="tpm"):
        assert metric in self.metrics.keys(), f"Availabel metrics: {list(self.metrics.keys())}."
        assert metric not in ["tpd", "rpd"], f"Method \"{metric}\" is not yet implemented."
        
        key = min(self.keys, key=self.metrics[metric])
        
        return key