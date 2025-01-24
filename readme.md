# Captivate AI & LLM API

## Overview
This API is developed by CaptivateChat to handle its API formats.This flexible messaging and metadata management system built using Pydantic models, designed to handle complex communication scenarios with robust type checking and validation.

## Key Components

### Models
- `Captivate`: Primary model managing conversation state
- `CaptivateResponseModel`: Handles response messages and metadata
- `ActionModel`: Manages actions with flexible payload handling
- `ChannelMetadataModel`: Stores dynamic channel and conversation metadata

### Features
- Dynamic metadata handling
- Immutable session and chat properties
- Flexible message type support
- Custom metadata manipulation
- Conversation title management

You can install through:

```bash
pip install captivate-ai-api
```


## Captivate Payload

Here's the JSON payload you will send in the POST request:

```json
{
    "session_id": "lance_catcher_test_69c35e3e-7ff4-484e-8e36-792a62567b79",
    "endpoint": "action",
    "user_input": "hi man",
    "incoming_action": [
        {
            "id": "sendEmail",
            "payload": {
                "email": "delvallelance@gmail.com",
                "message": "You are fired"
            }
        }
    ],
    "metadata": {
        "internal": {
            "channelMetadata": {
                "course_id": "abc",
                "channelMetadata": {
                    "channel": "custom-channel",
                    "channelData": {}
                },
                "user": {
                    "firstName": "Lance",
                    "lastName": "safa",
                    "email": "asdaf@gmail.com"
                },
                "phoneNumber": null,
                "custom": {
                    "mode": "non-dbfred",
                    "title": {
                        "type": "title",
                        "title": "\"Latest Updates on EU Regulations\""
                    }
                }
            }
        }
    },
    "hasLivechat": false
}
```
## Usage Example

```python
from captivate_ai_api import Captivate, UserModel, TextMessageModel



@app.post("/chat")
async def handle_chat(data: CaptivateRequestModel):
    try:
        # Create Captivate instance using the request data
        captivate = Captivate(**data.dict())
        captivate.set_conversation_title('Lord of the rings')

        # Prepare messages
        messages = [
            TextMessageModel(text="Welcome to our platform!"),
            ButtonMessageModel(buttons={"title": "Learn More", "action": "navigate"}),
            TableMessageModel(table="<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"),
            CardMessageModel(
                text="Special Offer",
                description="Get 20% off your next purchase.",
                image_url="https://example.com/offer.png",
                link="https://example.com/deals"
            ),
            HtmlMessageModel(html="<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"),
            FileModel(type="application/pdf", url="https://example.com/manual.pdf", filename="UserManual.pdf"),
            BaseMessageModel(type="alert", RootModel={"priority": "high", "message": "System maintenance scheduled."})
        ]
        
        # Set the response messages
        captivate.set_response(messages)

        # Outgoing actions Both 'payload' & 'data' works for backwards compatibliity. Moving forward it is recommended to use 'data'
        outgoing_actions = [
            ActionModel(id="navigate", payload={"url": "https://example.com"}),
            ActionModel(id="submit", data={"form_id": "1234"})
        ] 
        captivate.set_outgoing_action(outgoing_actions)

        return captivate.get_response() #Returns data to captivate platform in the correct format





```

# Expected Response from `/chat` Endpoint

When you send the POST request to the `/chat` endpoint, the response will look as follows:

```json
{
    "messages": [
        {
            "type": "text",
            "text": "Welcome to our platform!"
        },
        {
            "type": "button",
            "buttons": {
                "title": "Learn More",
                "action": "navigate"
            }
        },
        {
            "type": "table",
            "table": "<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"
        },
        {
            "type": "card",
            "text": "Special Offer",
            "description": "Get 20% off your next purchase.",
            "image_url": "https://example.com/offer.png",
            "link": "https://example.com/deals"
        },
        {
            "type": "html",
            "html": "<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"
        },
        {
            "type": "application/pdf",
            "url": "https://example.com/manual.pdf",
            "filename": "UserManual.pdf"
        },
        {
            "type": "alert",
            "RootModel": {
                "priority": "high",
                "message": "System maintenance scheduled."
            }
        }
    ],
    "session_id": "lance_catcher_test_69c35e3e-7ff4-484e-8e36-792a62567b79",
    "metadata": {
        "internal": {
            "channelMetadata": {
                "user": {
                    "firstName": "Lance",
                    "lastName": "safa",
                    "email": "asdaf@gmail.com"
                },
                "channelMetadata": {
                    "channel": "custom-channel",
                    "channelData": {}
                },
                "custom": {
                    "mode": "non-dbfred",
                    "title": {
                        "type": "title",
                        "title": "Lord of the rings"
                    }
                },
                "conversationCreatedAt": null,
                "conversationUpdatedAt": null
            }
        }
    },
    "outgoing_action": [
        {
            "id": "navigate",
            "payload": {
                "url": "https://example.com"
            },
            "data": {
                "url": "https://example.com"
            }
        },
        {
            "id": "submit",
            "payload": {
                "form_id": "1234"
            },
            "data": {
                "form_id": "1234"
            }
        }
    ],
    "hasLivechat": false
}
```

## Functions Overview

### 1. `get_session_id`

```python
def get_session_id(self) -> str:
```
- **Description**: Returns the value of `session_id`.
- **Example**: 
```python
session_id = captivate_instance.get_session_id()
```

### 2. `get_user_input`

```python
def get_user_input(self) -> Optional[str]:
```
- **Description**: Returns the value of `user_input`.
- **Example**: 
```python
user_input = captivate_instance.get_user_input()
```

### 3. `set_conversation_title`

```python
def set_conversation_title(self, title: str):
```
- **Description**: Sets the conversation title in the custom metadata.
- **Example**: 
```python
captivate_instance.set_conversation_title("New Conversation Title")
```

### 4. `get_conversation_title`

```python
def get_conversation_title(self) -> Optional[str]:
```
- **Description**: Retrieves the conversation title from the custom metadata.
- **Example**: 
```python
conversation_title = captivate_instance.get_conversation_title()
```

### 5. `set_metadata`

```python
def set_metadata(self, key: str, value: Any):
```
- **Description**: Sets a key-value pair in the custom metadata.
- **Example**: 
```python
captivate_instance.set_metadata("custom_key", "custom_value")
```

### 6. `get_metadata`

```python
def get_metadata(self, key: str) -> Optional[Any]:
```
- **Description**: Retrieves the value for a given key in the custom metadata.
- **Example**: 
```python
metadata_value = captivate_instance.get_metadata("custom_key")
```

### 7. `remove_metadata`

```python
def remove_metadata(self, key: str) -> bool:
```
- **Description**: Removes a key from the custom metadata.
- **Example**: 
```python
captivate_instance.remove_metadata("custom_key")
```

### 8. `get_channel`

```python
def get_channel(self) -> Optional[str]:
```
- **Description**: Retrieves the channel from the metadata.
- **Example**: 
```python
channel = captivate_instance.get_channel()
```

### 9. `get_user`

```python
def get_user(self) -> Optional[UserModel]:
```
- **Description**: Retrieves the user from the metadata.
- **Example**: 
```python
user = captivate_instance.get_user()
```

### 10. `set_user`

```python
def set_user(self, user: UserModel) -> None:
```
- **Description**: Sets the user in the metadata.
- **Example**: 
```python
captivate_instance.set_user(UserModel(firstName="John", lastName="Doe"))
```

### 11. `get_created_at`

```python
def get_created_at(self) -> Optional[str]:
```
- **Description**: Returns the `conversationCreatedAt` timestamp from the metadata.
- **Example**: 
```python
created_at = captivate_instance.get_created_at()
```

### 12. `get_updated_at`

```python
def get_updated_at(self) -> Optional[str]:
```
- **Description**: Returns the `conversationUpdatedAt` timestamp from the metadata.
- **Example**: 
```python
updated_at = captivate_instance.get_updated_at()
```

### 13. `get_has_livechat`

```python
def get_has_livechat(self) -> bool:
```
- **Description**: Returns the value of `hasLivechat`.
- **Example**: 
```python
has_livechat = captivate_instance.get_has_livechat()
```

### 14. `set_response`

```python
def set_response(self, messages: List[Union[TextMessageModel, FileModel, ButtonMessageModel, TableMessageModel, CardMessageModel, HtmlMessageModel, BaseMessageModel]]) -> None:
```
- **Description**: Sets the response messages in the `Captivate` instance.
- **Example**: 
```python
captivate_instance.set_response([
            TextMessageModel(text="Welcome to our platform!"),
            ButtonMessageModel(buttons={"title": "Learn More", "action": "navigate"}),
            TableMessageModel(table="<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"),
            CardMessageModel(
                text="Special Offer",
                description="Get 20% off your next purchase.",
                image_url="https://example.com/offer.png",
                link="https://example.com/deals"
                ),
            HtmlMessageModel(html="<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"),
            FileModel(type="application/pdf", url="https://example.com/manual.pdf", filename="UserManual.pdf"),
            BaseMessageModel(type="alert", RootModel={"priority": "high", "message": "System maintenance scheduled."})
            ])
```

### 15. `get_incoming_action`

```python
def get_incoming_action(self) -> Optional[List[ActionModel]]:
```
- **Description**: Retrieves the incoming actions from the response object, if present.
- **Example**: 
```python
incoming_actions = captivate_instance.get_incoming_action()
```

### 16. `set_outgoing_action`

```python
def set_outgoing_action(self, actions: List[ActionModel]) -> None:
```
- **Description**: Sets the outgoing actions in the response object.
- **Example**: 
```python
captivate_instance.set_outgoing_action([
    ActionModel(id="navigate", data={"url": "https://example.com"})
])
```

### 17. `get_response`

```python
def get_response(self) -> Optional[str]:
```
- **Description**: Returns the `CaptivateResponseModel` as a JSON string if it exists, otherwise returns `None`.
- **Example**: 
```python
response_json = captivate_instance.get_response()
```




