import httpx
from pydantic import BaseModel, model_validator, Field
from typing import Optional, Dict, Any, List, Union
import json
import asyncio
import redis.asyncio as redis
from datetime import datetime, timezone


# Session Model
class Session(BaseModel):
    session_id: str
    chat_history: List[Dict[str, Any]] = []  # Auto-filled chat history
    context: Dict[str, Any] = {}  # Auto-filled context
    conversation_title: str = "Untitled"


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
    type: str = "files"  # e.g., "file"
    files: List[FileModel]  # List of files


class UserModel(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None


class ChannelMetadataModel(BaseModel):
    user: Optional[UserModel] = None
    channelMetadata: Dict[str, Any] = (
        {}
    )  # This will allow dynamic properties at this level
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
        self.set_custom("title", title_data)  # this is to support old version
        self.set_custom("conversation_title", title)

    def get_conversation_title(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the 'title' from metadata.
        """
        return self.get_custom("conversation_title")


class InternalMetadataModel(BaseModel):
    channelMetadata: ChannelMetadataModel


class MetadataModel(BaseModel):
    internal: InternalMetadataModel


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
    outgoing_action: Optional[List[ActionModel]] = (
        None  # Optional actions to taken such as redirecting user to website
    )
    hasLivechat: bool  # Whether there is live chat available


class Captivate(BaseModel):
    session_id: str
    user_input: Optional[str] = None  # Can be null
    files: Optional[List[Dict[str, Any]]] = None  # Optional list of file objects
    metadata: MetadataModel  # Updated metadata
    incoming_action: Optional[List[ActionModel]] = None
    hasLivechat: bool
    response: Optional[CaptivateResponseModel] = None
    session: Optional[Session] = None  # Session storage (either in-memory or Redis)
    memory_mode: bool = (
        False  # True = Use in-memory session, False = Don't track session
    )
    redis_url: str = None
    redis_client: Optional[Any] = None
    llm: Optional[Any] = None
    longterm_context_tracking: bool = False
    generate_conversation_title: bool = False

    """Constants"""
    # API URLs as constants
    DEV_URL: str = Field(
        default="https://channel.dev.captivat.io/api/channel/sendMessage", exclude=True
    )
    PROD_URL: str = Field(
        default="https://channel.prod.captivat.io/api/channel/sendMessage", exclude=True
    )

    DEV_URL_V2: str = Field(
        default="https://channel.dev.captivat.io/api/channel/v2/sendMessage",
        exclude=True,
    )
    PROD_URL_V2: str = Field(
        default="https://channel.prod.captivat.io/api/channel/v2/sendMessage",
        exclude=True,
    )

    """Flags for class safeguards"""
    # Prevent session_id and hasLivechat from being changed once set
    _session_id_set = False
    _hasLivechat_set = False
    _has_responded: bool = False  # Flag to ensure `set_response` is called only once

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

    @classmethod
    async def create(
        cls,
        data_dict,
        memory_enabled=False,
        redis_url=None,
        llm=None,
        longterm_context=False,
        generate_conversation_title=False,
    ):
        instance = cls(**data_dict)

        if memory_enabled and redis_url:
            await instance._create_memory(redis_url)
            if llm:
                instance.enable_llm_features(
                    llm=llm,
                    longterm_context_tracking=longterm_context,
                    generate_conversation_title=generate_conversation_title,
                )
                if generate_conversation_title:
                    await instance._generate_conversation_title()

        await instance._load_or_create_session()

        return instance

    def enable_llm_features(
        self,
        llm: Any,
        longterm_context_tracking: bool = False,
        generate_conversation_title: bool = False,
    ) -> None:
        """
        Enable LLM-based features such as conversation title generation and long-term context tracking.

        Parameters:
        - `llm`: Any LangChain LLM object (e.g., OpenAI, HuggingFace, etc.).
        - `longterm_context_tracking`: Enables memory-based context tracking.
        - `generate_conversation_title`: Enables automatic title generation for new conversations.

        Requires memory mode to be enabled.
        """
        if not self.memory_mode:
            raise ValueError(
                "Memory mode must be enabled before enabling LLM features."
            )

        self.llm = llm
        self.longterm_context_tracking = longterm_context_tracking
        self.generate_conversation_title = generate_conversation_title

    async def _create_memory(self, redis_url: str):
        """Enable memory mode with Redis and load/create the session."""
        self.memory_mode = True
        self.redis_url = redis_url
        self.redis_client = await redis.Redis.from_url(
            self.redis_url, decode_responses=True
        )

    async def _load_or_create_session(self):
        """Load session or create a new one and append the user input."""
        if self.memory_mode and self.redis_client:
            session_data = await self.redis_client.get(f"session:{self.session_id}")
            if session_data:
                # Parse and load the session
                session_dict = json.loads(session_data)
                self.session = Session(
                    **session_dict
                )  # Create a Session model instance
            else:
                # Create a new session if not found
                self.session = Session(
                    session_id=self.session_id,
                    chat_history=[],
                    conversation_title=self.get_conversation_title(),
                )

            # If user input exists, append it to the session's chat history
            if self.user_input:
                self.session.chat_history.append(
                    {
                        "role": "user",
                        "message": self.user_input,
                        "timestamp": datetime.now(
                            timezone.utc
                        ).isoformat(),  # Add timestamp in ISO format
                    }
                )

            # Extract context if LLM features are enabled
            if self.llm and self.longterm_context_tracking:
                extracted_context = await self.extract_context()
                self.session.context.update(extracted_context)

            # Save session back to Redis
            await self.save_session()

    async def _generate_conversation_title(self) -> None:
        """Generates a conversation title using the LLM."""
        if not self.llm or not self.generate_conversation_title:
            return None

        # Skip title generation for default messages of Captivate chat
        if not self.user_input or self.user_input.strip().upper() == "START CHAT":
            return  # Do nothing if input is empty or "START CHAT"

        session_key = f"session:{self.session_id}"

        # Check if title is already stored in session
        if self.memory_mode and self.redis_client:

            session_data = await self.redis_client.get(session_key)

            if session_data:
                session_data = json.loads(
                    session_data
                )  # Convert JSON string to dictionary
                existing_title = session_data.get("conversation_title")

                if existing_title:
                    print("Title exists")
                    self.set_conversation_title(existing_title)
                    return  # Skip generation if it exists

        prompt = f"""
        You are an Agent tasked to generate a concise title for a conversation based on the user's message. The title should be brief and short, with a maximum of 5 words.  Return the title as a JSON object with the key "title".  For example:

        ```json
        {{"title": "Concise Conversation Title"}}
        Message: {self.user_input}
        """

        try:
            title_response = self.llm.invoke(prompt)
            response_content = title_response.content.strip()
            title_json = json.loads(response_content)

            title = title_json.get("title")

            if title:
                self.set_conversation_title(title)

            else:
                print("LLM response did not contain 'title' key:", response_content)
                self.set_conversation_title("Untitled Conversation")
        except Exception as e:
            print(f"Error generating title: {e}")
            return None

    async def extract_context(self) -> Dict[str, Any]:
        """Extract important context from user input & previous bot message using LLM."""
        if not self.llm:
            return {}

        last_bot_message = next(
            (
                msg["message"]
                for msg in reversed(self.session.chat_history)
                if msg["role"] == "bot"
            ),
            None,
        )

        prompt = (
            """You are an Agent for keeping memory context. 
            Extract and store important context about this chat. Only user context is needed ignore Bot context
            Your OUTPUT will be strictly in JSON. Use flat structure and avoid using nested objects
            Make sure to lower case property names\n"""
            f"Bot: {last_bot_message if last_bot_message else 'N/A'}\n"
            f"User: {self.user_input}\n"
        )

        extracted_text = self.llm.invoke(prompt)
        try:
            return json.loads(extracted_text.content)
        except json.JSONDecodeError:
            return {"error": "Failed to extract structured context"}

    async def save_session(self):
        """Asynchronously save the updated session to Redis."""
        if self.memory_mode and self.redis_client and self.session:
            await self.redis_client.set(
                f"session:{self.session_id}", json.dumps(self.session.model_dump())
            )

    async def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Retrieve the chat history from Redis.
        """
        if not self.memory_mode or not self.redis_client:
            raise ValueError("Memory mode is not enabled. Call `enable_memory` first.")

        session_data = await self.redis_client.get(f"session:{self.session_id}")
        if session_data:
            session_dict = json.loads(session_data)
            return session_dict.get("chat_history", [])
        return []  # Return an empty history if no data is found

    async def save_bot_message_to_history(self, bot_message: str) -> None:
        """
        Save the bot's message to the session's chat history asynchronously.
        """
        if self.session is not None:
            # Append the bot message to the chat history
            self.session.chat_history.append(
                {
                    "role": "bot",
                    "message": bot_message,
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),  # Add timestamp in ISO format
                }
            )
            # Save session asynchronously
            await self.save_session()
        else:
            print("Session not loaded or created.")

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

    async def set_response(
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
        Method to set the response messages in Captivate instance. This method can only be
        called once per instance. This is to ensure we avoid bad practices of overwriting responses in the library
        Instead all response set from the controller are considered final and ready for take-off
        """
        # Ensure that the response is only set once
        if self._has_responded:
            print(
                f"Warning: Response has already been set for session {self.session_id}. Subsequent calls will be ignored."
            )
            return  # Return early if already responded, preventing further changes

        # Mark that the response has been set
        self._has_responded = True

        # Ensure the response object exists
        if not self.response:
            self.response = CaptivateResponseModel(
                session_id=self.session_id,
                metadata=self.metadata,
                hasLivechat=self.hasLivechat,
            )

        # Set the response_messages
        self.response.response = response

        # If memory_mode is enabled and we have a session, treat the entire response as a bot message
        if self.memory_mode and self.session:
            # You can directly treat the response as the bot's message in this case
            bot_message = response  # the entire response object is a bot message
            # Save the bot's message asynchronously without blocking the function execution
            await self.save_bot_message_to_history(bot_message)

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

    async def async_send_message_v1(
        self, environment: str = "dev"
    ) -> Dict[str, Any]:  # DEPRECATED WILL NOT BE MAINTAINED
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

        action_data = [
            msg.model_dump() for msg in (self.response.outgoing_action) or []
        ]

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
