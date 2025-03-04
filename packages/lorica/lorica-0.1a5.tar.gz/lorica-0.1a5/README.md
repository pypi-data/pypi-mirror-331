# Lorica Package

## Introduction
This package provides functionality for interaction with Lorica Cybersecurity products. The following capabilities are currently offered:
- OHTTP encapsulation for secure interaction with Lorica AI deployment.

## Lorica AI OHTTP Encapsulation using Requests Session
To encapsulate requests and responses through a `requests.Session`, simply replace the object construction with `lorica.ohttp.Session`:
```python
import lorica.ohttp
import json

# Create lorica.ohttp.Session that inherits from requests.Session.
session = lorica.ohttp.Session()

deployment_url = "DEPLOYMENT_URL"
lorica_api_key = "LORICA_API_KEY"

# Use session like a request.Session including response streaming support.
stream = True
resp = session.post(
    f"{deployment_url}/v1/chat/completions",
    headers={"Authorization": f"Bearer {lorica_api_key}"},
    json={
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "where does the sun rise from?"},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": stream,
    },
    stream=stream
)
resp.raise_for_status()
if stream:
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue

        data = line[len("data: "):].strip()
        if data == "[DONE]":
            break

        chunk = json.loads(data)
        print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
else:
    print(resp.json()["choices"][0]["message"]["content"])
```

## Lorica AI OHTTP Encapsulation using HTTPX Transport
To encapsulate requests and responses through a `httpx.Transport`, simply replace the object construction with `lorica.ohttp.Transport`:
```python
import lorica.ohttp
import httpx
import json

# Initialize httpx client with the lorica.ohttp.Transport that inherits from httpx.Transport
httpx_client = httpx.Client(transport=lorica.ohttp.Transport())

deployment_url = "DEPLOYMENT_URL"
lorica_api_key = "LORICA_API_KEY"

# Use client as normal including chunked-encoding response support.
method = "POST"
url = deployment_url + "/v1/chat/completions"
stream = True
data = {
    "model": "meta-llama/Llama-3.2-3B-Instruct",
    "messages": [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "where does the sun rise from?"},
    ],
    "temperature": 0.7,
    "max_tokens": 1024,
    "stream": stream,
}
headers = {"Authorization": f"Bearer {lorica_api_key}"}
if stream:
    with httpx_client.stream(method, url, json=data, headers=headers) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line or not line.startswith("data: "):
                continue

            data = line[len("data: "):].strip()
            if data == "[DONE]":
                break

            chunk = json.loads(data)
            print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
else:
    resp = httpx_client.post(url, json=data, headers=headers, timeout=30)
    resp.raise_for_status()
    print(resp.json()["choices"][0]["message"]["content"])
```

## Lorica AI OHTTP Encapsulation using OpenAI Client
This is also applicable to clients that utilize `httpx` for their HTTP communication, for example `openai` client:
```python
import lorica.ohttp
import httpx
import openai

# Initialize httpx client with lorica.ohttp.Transport that inherits from httpx.Transport
httpx_client = httpx.Client(transport=lorica.ohttp.Transport())
deployment_url = "DEPLOYMENT_URL"
lorica_api_key = "LORICA_API_KEY"

# Configure OpenAI client with httpx client
client = openai.OpenAI(
    api_key=lorica_api_key,
    http_client=httpx_client,
    base_url=deployment_url + "/v1")

# Use OpenAI SDK as normal for example llama chat (including stream capability)
stream = True
completion = client.chat.completions.create(
    model="meta-llama/Llama-3.2-3B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "where does the sun rise from?"},
    ],
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024,
    stream=stream,
)
if stream:
    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
else:
    print(completion.choices[0].message.content)
```