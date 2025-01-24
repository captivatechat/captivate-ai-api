
# Captivate API Documentation

This documentation provides an overview of the functions available in the `Captivate` model, used for managing sessions, actions, and metadata in the platform.

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
    TextMessageModel(text="Welcome to our platform!")
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
    ActionModel(id="navigate", payload={"url": "https://example.com"})
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

### 18. `get_user_input`

```python
def get_user_input(self) -> Optional[str]:
```
- **Description**: Returns the user_input if it exists, otherwise returns `None`.
- **Example**: 
```python
user_input = captivate_instance.get_user_input()
```

### 19. `get_files`

```python
def get_files(self) -> List[FileModel]:
```
- **Description**: Returns the user_input if it exists, otherwise returns `None`.
- **Example**: 
```python
files = captivate_instance.get_files()
if files:
    for file in files:
        print(file)
```

## Example Usage

```python
from your_module import Captivate, TextMessageModel

# Initialize a Captivate instance
captivate_instance = Captivate(session_id="12345", hasLivechat=True, metadata={})

# Set the conversation title
captivate_instance.set_conversation_title("Chat with customer support")

# Set the response with a text message
captivate_instance.set_response([
    TextMessageModel(text="Hello, how can I assist you today?")
])

# Retrieve the response as a JSON string
response_json = captivate_instance.get_response()
print(response_json)
```

## License

MIT License
