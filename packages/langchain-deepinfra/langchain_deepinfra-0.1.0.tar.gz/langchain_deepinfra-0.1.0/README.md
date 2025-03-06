# langchain-deepinfra

This package contains the LangChain integrations for [DeepInfra](https://deepinfra.com/) through their [APIs](https://deepinfra.com/docs).

## Installation and Setup

Install the LangChain partner package

```bash
pip install -U langchain-deepinfra
```

Get your DeepInfra api key from the [DeepInfra Dashboard](https://deepinfra.com/dash/api_keys) and set it as an environment variable (`DEEPINFRA_API_TOKEN`)

```bash
export DEEPINFRA_API_TOKEN=<api_key>
```

## Chat Completions

This package contains the `ChatDeepInfra` class, which is the recommended way to interface with DeepInfra chat models.

```python
from langchain_deepinfra import ChatDeepInfra

chat = ChatDeepInfra(model="meta-llama/Meta-Llama-3.1-8B-Instruct")
chat.invoke("Who is the first president of Indonesia?")
```

## Embeddings

`DeepInfraEmbeddings` class exposes the DeepInfra embedding API.

```python
from langchain_deepinfra import DeepInfraEmbeddings

embeddings = DeepInfraEmbeddings(model="BAAI/bge-base-en-v1.5")
embeddings.embed_query("Who is the first president of Indonesia?")
```

## LLM

`DeepInfra` class exposes the DeepInfra LLM API.

```python
from langchain_deepinfra import DeepInfra

llm = DeepInfra(model="meta-llama/Meta-Llama-3.1-8B-Instruct")
llm.invoke("Who is the first president of Indonesia?")
```
