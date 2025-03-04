
(definitely not ai generated generic project description that will be updated in the future)

Lazy Key is a Python-based utility designed to efficiently manage multiple API keys while ensuring optimal usage and load balancing. Built with asyncio, the system dynamically selects the best available key based on predefined rate-limiting metrics such as tokens per minute (TPM) and requests per second (RPS).

**Key Features**\
✅ Asynchronous API Requests – Uses asyncio to handle API calls concurrently, improving performance.\
✅ Smart Key Selection – Dynamically picks the API key with the lowest usage based on live metrics.\
✅ Rate Limit Awareness – Supports selection methods like TPM and RPS to maximize key efficiency.\
✅ Parallel Metric Evaluation – Uses asyncio.gather() to fetch usage data from all keys simultaneously.\
✅ Flexible and Scalable – Easily extendable to support additional rate-limiting strategies and APIs such as OpenAI, Groq, or any custom online LLM API.\

# Quickstart

Sync version
```python
from lazykey import KeyHandler
from groq import Groq

api_keys = ["API_KEY_1", "API_KEY_2"]
client = Groq

api = KeyHandler(api_keys, client)

completion = api.request(
    messages=[
        {
            "role": "user",
            "content": "Cats or dogs?",
        }
    ],
    model="llama-3.3-70b-versatile",
)
```

Async version:
```python
from lazykey import AsyncKeyHandler
from groq import AsyncGroq

api_keys = ["API_KEY_1", "API_KEY_2"]
client = AsyncGroq

api = AsyncKeyHandler(api_keys, client)

completion = await api.request(
    messages=[
        {
            "role": "user",
            "content": "Cats or dogs?",
        }
    ],
    model="llama-3.3-70b-versatile",
)
```