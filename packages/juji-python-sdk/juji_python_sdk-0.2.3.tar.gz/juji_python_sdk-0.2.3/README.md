# Juji Python SDK

This is a Python SDK for [Juji Chatbot](https://juji.io) and [Juji Design](https://juji.ai/rep), using the [Juji API](https://juji.io/docs/api).

## Installation

```bash
pip install juji-python-sdk
```

## Usage
The Chatbot and Design SDKs are in the same package.

### Chatbot
```python
from juji_python_sdk import Chatbot

chatbot = Chatbot("<chatbot_url>")

participation = chatbot.start_chat()
```

#### Asynchronous message handling

```python
def handle_message(message: dict):
    if message["type"] == "normal":
        print(f"Juji: {message['text']}")
    elif message["type"] == "flowinfo":
        print(f"Juji is waiting for your response...")

participation.add_message_callback(handle_message)

time.sleep(10)

print("You: Hello, how are you?")
participation.send_chat_msg("Hello, how are you?")

time.sleep(10)

print("You: Bye!")
participation.end()
```

#### Synchronous message handling

```python
messages = participation.get_messages()
print(messages)

print("You: Hello, how are you?")
messages = participation.send_chat_msg("Hello, how are you?")
print(messages) 
```

### Design

```python
from juji_python_sdk import JujiDesign

design = JujiDesign("<juji_api_key>", "<juji_platform_url>")

brands = design.get_brands()

browser_key = uuid.uuid4()
design.add_faq(["Where can I buy some tomatoes?"], 
               ["We have the best tomatoes in the world!"], 
               "<engagement_id>", 
               browser_key)
``` 
Check out the [design_example.py](design_example.py) for a complete example.