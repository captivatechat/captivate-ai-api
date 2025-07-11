import httpx
from pydantic import BaseModel, EmailStr, model_validator, Field, RootModel
from typing import Optional, Dict, Any, List, Union
import requests
import io

# Predefined message types
class TextMessageModel(BaseModel):
    type: str = "text"
    text: str  # Text content


class ButtonMessageModel(BaseModel):
    type: str = "button"
    buttons: Dict[str, Any]  # Button structure (e.g., title, options)


class TableMessageModel(BaseModel):
    type: str = "table"
    table: str  # HTML formatted table

class CardMessageModel(BaseModel):
    text: str
    description: str
    image_url: str
    link: str

class CardCollectionModel(BaseModel):
    type: str = "cards"
    cards: List[CardMessageModel]


class HtmlMessageModel(BaseModel):
    type: str = "html"
    html: str  # HTML content



class FileModel(BaseModel):
    type: str  # MIME type, e.g., application/pdf
    url: Optional[str] = None  # URL can be null
    filename: Optional[str] = None  # Filename can be null

    @model_validator(mode="after")
    def check_url_or_filename(self):
        if not self.url and not self.filename:
            raise ValueError(
                "At least one of 'url' or 'filename' must be provided in FileModel."
            )
        return self

class FileCollectionModel(BaseModel):
    type: str = 'files'  # e.g., "file"
    files: List[FileModel]  # List of files
    
    
class UserModel(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None


class ChannelMetadataModel(BaseModel):
    user: Optional[UserModel] = None
    channelMetadata: Dict[str, Any] = {} # This will allow dynamic properties at this level
    custom: Dict[str, Any] = {}  # Custom dynamic properties
    conversationCreatedAt: Optional[str] = None  # ISO8601 format for dates
    conversationUpdatedAt: Optional[str] = None  # ISO8601 format for dates

    def set_custom(self, key: str, value: Any):
        """
        Set or update a key-value pair in the custom object.
        """
        self.custom[key] = value

    def get_custom(self, key: str) -> Optional[Any]:
        """
        Retrieve a value by key from the custom object.
        """
        return self.custom.get(key)

    def remove_custom(self, key: str):
        """
        Remove a key-value pair from the custom object.
        """
        if key in self.custom:
            del self.custom[key]

    def set_conversation_title(self, title: str):
        """
        Set a conversation title in the custom object with the specified format.
        """
        title_data = {
            "type": "title",
            "title": title,
        }
        self.set_custom("title", title_data) #this is to support old version
        self.set_custom("conversation_title", title)

    def get_conversation_title(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the 'title' from metadata.
        """
        return self.get_custom("conversation_title")
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves value from any top-level or nested attribute if present.
        """
        if key in self.custom:
            return self.custom.get(key, default)
        if key in self.channelMetadata:
            return self.channelMetadata.get(key, default)
        return getattr(self, key, default)


class InternalMetadataModel(BaseModel):
    channelMetadata: ChannelMetadataModel
    def get(self, attr: str, default: Any = None) -> Any:
            """
            Simulates a dictionary-style get for known top-level attributes.
            """
            return getattr(self, attr, default)

class MetadataModel(BaseModel):
    internal: InternalMetadataModel
    def get(self, attr: str, default: Any = None) -> Any:
        return getattr(self, attr, default)

class ActionModel(BaseModel):
    id: str = Field(alias="action")  # Supports both 'id' and 'action' as input keys
    payload: Optional[Dict[str, Any]] = None  # Existing field
    data: Optional[Dict[str, Any]] = None  # New field for migration

    def model_post_init(self, __context: Any) -> None:
        # Ensure `payload` and `data` are synchronized
        if self.payload and self.data and self.payload != self.data:
            raise ValueError("`payload` and `data` must be identical during migration.")
        unified_value = self.payload or self.data
        object.__setattr__(self, "payload", unified_value)
        object.__setattr__(self, "data", unified_value)


    class Config:
        populate_by_name = (
            True  # Allows using both 'id' and 'action', 'payload', and 'data' as input
        )


class CaptivateResponseModel(BaseModel):
    response: List[
        Union[
            TextMessageModel,
            FileCollectionModel,
            ButtonMessageModel,
            TableMessageModel,
            CardCollectionModel,
            HtmlMessageModel,
            dict,
        ]
    ] = []  # List of responses Default to an empty list
    session_id: str  # Session ID to identify the conversation
    metadata: MetadataModel  # Updated metadata
    outgoing_action: Optional[List[ActionModel]] = None  # Optional actions to taken such as redirecting user to website
    hasLivechat: bool  # Whether there is live chat available


class Captivate(BaseModel):
    session_id: str
    user_input: Optional[str] = None  # Can be null
    files: Optional[List[Dict[str, Any]]] = None  # Optional list of file objects
    metadata: MetadataModel  # Updated metadata
    incoming_action: Optional[List[ActionModel]] = None
    hasLivechat: bool
    response: Optional[CaptivateResponseModel] = None


    # API URLs as constants
    DEV_URL: str = Field(default="https://channel.dev.captivat.io/api/channel/sendMessage", exclude=True)
    PROD_URL: str = Field(default="https://channel.prod.captivat.io/api/channel/sendMessage", exclude=True)
    
    DEV_URL_V2: str = Field(default="https://channel.dev.captivat.io/api/channel/v2/sendMessage", exclude=True)
    PROD_URL_V2: str = Field(default="https://channel.prod.captivat.io/api/channel/v2/sendMessage", exclude=True)
    # Prevent session_id and hasLivechat from being changed once set
    _session_id_set = False
    _hasLivechat_set = False

    @model_validator(mode="before")
    def check_immutable_fields(cls, values):
        """
        Ensures that session_id and hasLivechat cannot be modified after being set.
        """
        if "_session_id_set" in values:
            if values.get("session_id") != values.get("session_id", None):
                raise ValueError("session_id cannot be modified after it is set.")

        if "_hasLivechat_set" in values:
            if values.get("hasLivechat") != values.get("hasLivechat", None):
                raise ValueError("hasLivechat cannot be modified after it is set.")

        return values

    @model_validator(mode="after")
    def set_response_metadata(self):
        # Ensure the response is populated and update its metadata
        if self.response is None:
            self.response = CaptivateResponseModel(
                session_id=self.session_id,
                metadata=self.metadata,
                hasLivechat=self.hasLivechat,
            )

        # Sync session_id and hasLivechat from Captivate to response
        if self.session_id != self.response.session_id:
            self.response.session_id = self.session_id
        if self.hasLivechat != self.response.hasLivechat:
            self.response.hasLivechat = self.hasLivechat

        # Update metadata if it's been changed
        if self.metadata != self.response.metadata:
            self.response.metadata = self.metadata

        return self

    @model_validator(mode="after")
    def copy_to_response(self):
        """
        Automatically copies session_id, hasLivechat, and metadata to the response if not explicitly set.
        """
        if self.response:
            self.response.session_id = self.session_id
            self.response.hasLivechat = self.hasLivechat
            self.response.metadata = self.metadata

        return self

    def get_session_id(self) -> str:
        """
        Returns the value of 'session_id'.
        """
        return self.session_id

    def get_user_input(self) -> Optional[str]:
        """
        Returns the value of 'user_input'.
        """
        return self.user_input

    # Proxy method to set the conversation title
    def set_conversation_title(self, title: str):
        self.metadata.internal.channelMetadata.set_conversation_title(title)

    # Proxy method to get the conversation title
    def get_conversation_title(self) -> Optional[str]:
        return self.metadata.internal.channelMetadata.get_conversation_title()

    # Proxy method for custom object manipulation
    def set_metadata(self, key: str, value: Any):
        """Set a key-value pair in the custom metadata."""
        self.metadata.internal.channelMetadata.set_custom(key, value)

    def get_metadata(self, key: str) -> Optional[Any]:
        """Retrieve the value for a given key in the custom metadata."""
        return self.metadata.internal.channelMetadata.get_custom(key)

    def remove_metadata(self, key: str) -> bool:
        """Remove a key from the custom metadata."""
        return self.metadata.internal.channelMetadata.remove_custom(key)

        # Function to get channel from metadata

    def get_channel(self) -> Optional[str]:
        return self.metadata.internal.channelMetadata.channelMetadata.get("channel")

    # Function to get user from metadata
    def get_user(self) -> Optional[UserModel]:
        return self.metadata.internal.channelMetadata.user

    # Function to set the user in metadata
    def set_user(self, user: UserModel) -> None:
        self.metadata.internal.channelMetadata.user = user

    def get_created_at(self) -> Optional[str]:
        # Return the conversationCreatedAt if it exists
        return self.metadata.internal.channelMetadata.conversationCreatedAt

    def get_updated_at(self) -> Optional[str]:
        # Return the conversationUpdatedAt if it exists
        return self.metadata.internal.channelMetadata.conversationUpdatedAt

    def get_has_livechat(self) -> bool:
        """
        Returns the value of 'hasLivechat'.
        """
        return self.hasLivechat

    def set_response(
        self,
        response: List[
            Union[
                TextMessageModel,
                FileModel,
                ButtonMessageModel,
                TableMessageModel,
                CardMessageModel,
                HtmlMessageModel,
                dict,
            ]
        ],
    ) -> None:
        """
        Method to set the response messages in Captivate instance.
        """
        # Ensure the response object exists
        if not self.response:
            self.response = CaptivateResponseModel(
                session_id=self.session_id,
                metadata=self.metadata,
                hasLivechat=self.hasLivechat,
            )

        # Set the response_messages
        self.response.response = response

    def get_incoming_action(self) -> Optional[List[ActionModel]]:
        """
        Retrieves the incoming actions from the response object, if present.
        """
        if not self.response or self.incoming_action is None:
            return None
        return self.incoming_action

    def set_outgoing_action(self, actions: List[ActionModel]) -> None:
        """
        Sets the outgoing actions in the response object.
        """
        if not self.response:
            self.response = CaptivateResponseModel(
                session_id=self.session_id,
                metadata=self.metadata,
                hasLivechat=self.hasLivechat,
            )
        self.response.outgoing_action = actions
        
    def escalate_to_human(self) -> None:
        """
        Sets an outgoing action to escalate the conversation to a human agent.
        """
        escalate_action = ActionModel(id="escalateToHuman")
        self.set_outgoing_action([escalate_action])
        
    def escalate_to_agent_router(self, reason: Optional[str] = None, intent: Optional[str] = None, recommended_agents: Optional[str] = None) -> None:
        """
        Sets an outgoing action to escalate the conversation to an agent router.
        
        Args:
            reason (str, optional): The reason for escalation.
            intent (str, optional): The user's intent.
            recommended_agents (str, optional): String of agent IDs to recommend.
        """
        payload = {}
        if reason:
            payload["reason"] = reason
        if intent:
            payload["intent"] = intent
        if recommended_agents:
            payload["recommended_agents"] = recommended_agents
            
        escalate_action = ActionModel(id="escalate_to_agent_router", payload=payload if payload else None)
        self.set_outgoing_action([escalate_action])
        
    def escalate_to_agent(self, agent_id: str, reason: Optional[str] = None) -> None:
        """
        Sets an outgoing action to force redirect the conversation to a specific agent.
        
        Args:
            agent_id (str): The ID of the agent to redirect to.
            reason (str, optional): The reason for the force redirection.
        """
        payload = {"agent_id": agent_id}
        if reason:
            payload["reason"] = reason
            
        escalate_action = ActionModel(id="escalate_to_agent", payload=payload)
        self.set_outgoing_action([escalate_action])
        
    def get_response(self) -> Optional[str]:
        """
        Returns the CaptivateResponseModel as a JSON string if it exists, otherwise returns None.
        """
        if self.response:
            return self.response.model_dump()  # Convert the response to a JSON string
        return None
    
    def get_files(self) -> Optional[List[Dict[str, Any]]]:
        """
        Returns the list of files associated with the Captivate instance.
        """
        return self.files

    def get_user_input(self) -> Optional[str]:
        """
        Returns the value of 'user_input' from the Captivate instance.
        """
        return self.user_input
    
    async def async_send_message_v1(self, environment: str = "dev") -> Dict[str, Any]: #DEPRECATED WILL NOT BE MAINTAINED
        """
        Asynchronously sends the CaptivateResponseModel to the API endpoint based on the environment. DEP

        Args:
            environment (str): The environment to use ('dev' or 'prod'). Defaults to 'dev'.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        if not self.response:
            raise ValueError("Response is not set. Cannot send an empty response.")

        # Determine the API URL based on the environment
        if environment == "prod":
            api_url = self.PROD_URL
        else:
            api_url = self.DEV_URL

         # Extract `channel` from metadata
        channel = self.get_channel()
        if not channel:
            raise ValueError("Channel information is missing in metadata.")
        
        # Convert the response message models into dictionaries
        message_data = []
    
        # Iterate through response and serialize models or dicts accordingly
        for message in self.response.response:
            if isinstance(message, BaseModel):
                # For Pydantic models, call .model_dump() to serialize
                message_data.append(message.model_dump())
            elif isinstance(message, dict):
                # For dictionaries, serialize directly
                message_data.append(message)
                
        action_data =  [msg.model_dump() for msg in (self.response.outgoing_action) or[]]

        # Prepare the payload dynamically
        message = {}

        if message_data:
            message["messages"] = message_data

        if action_data:
            message["actions"] = action_data

        payload = {
            "idChat": self.session_id,
            "channel": channel,
            }

        if message:  # Only add the "message" key if it's not empty
            payload["message"] = message


        
        print(payload)
        # Perform the async POST request
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload)

        # Raise an error if the request failed
        response.raise_for_status()
        return response
    
    
    async def async_send_message(self, environment: str = "dev") -> Dict[str, Any]:
        """
        Asynchronously sends the CaptivateResponseModel to the API endpoint based on the environment.

        Args:
            environment (str): The environment to use ('dev' or 'prod'). Defaults to 'dev'.

        Returns:
        Dict[str, Any]: The response from the API.
        """
        if not self.response:
            raise ValueError("Response is not set. Cannot send an empty response.")

        # Determine the API URL based on the environment
        api_url = self.PROD_URL_V2 if environment == "prod" else self.DEV_URL_V2

        # Convert the response to a dictionary
        payload = self.response.model_dump()

        # Send the request
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload)

        # Raise an error if the request failed
        response.raise_for_status()

        return response.json()  # Return the response as a JSON dictionary
    
    async def download_file_to_memory(self, file_info: Dict[str, Any]) -> io.BytesIO:
        """
        Downloads a file from the given dictionary and stores it in memory.

        Args:
            file_info (Dict[str, Any]): Dictionary containing the file details.
                Expected keys: 'url' (str), 'type' (str), 'filename' (str).

        Returns:
            io.BytesIO: In-memory file stream.
        """
        if "url" not in file_info:
            raise ValueError("Missing 'url' key in file_info dictionary.")

        response = requests.get(file_info["url"], stream=True)
        response.raise_for_status()  # Raise an error for failed requests

        return io.BytesIO(response.content)  # Store the file in-memory
    
