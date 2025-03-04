import os
import json
import asyncio
import time
from typing import Dict, List, Optional, Union, Any, AsyncGenerator, Callable
from urllib.parse import urljoin

import httpx

from tiptree.exceptions import ActxAPIError
from tiptree.interface_models import (
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentSession,
    AgentSessionCreate,
    AgentSessionUpdate,
    AgentSessionWake,
    Message,
    MessageCreate,
    MessagePayload,
    UserKeyRead,
    APIResponse,
    MessageUpdate,
)


class TiptreeClient:
    """
    Client for interacting with the Tiptree Platform API v2.

    This client provides methods for all v2 API endpoints, organized into
    sections for agents, agent sessions, messages, and simple API interactions.

    All methods are available in both synchronous and asynchronous versions.
    Async methods are prefixed with 'async_'.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.tiptreesystems.com/platform",
        timeout: float = 60.0,
    ):
        """
        Initialize the Tiptree client.

        Args:
            base_url: Base URL of the Tiptree Platform API
            api_key: API key for authentication (optional)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("TIPTREE_API_KEY")
        self.timeout = timeout
        self.async_client = httpx.AsyncClient(timeout=timeout)
        self.sync_client = httpx.Client(timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def async_close(self):
        """Close the underlying async HTTP client."""
        await self.async_client.aclose()

    def close(self):
        """Close the underlying sync HTTP client."""
        self.sync_client.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests, including authentication if available."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get_url(self, path: str) -> str:
        """Construct a full URL from the base URL and path."""
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    async def _async_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Make an async HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response object

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = self._get_url(path)
        headers = self._get_headers()

        response = await self.async_client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
        )

        # Raise exception for error status codes
        response.raise_for_status()

        return response

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Make a synchronous HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response object

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = self._get_url(path)
        headers = self._get_headers()

        response = self.sync_client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
        )

        # Raise exception for error status codes
        response.raise_for_status()

        return response

    # *******************
    # *** ACTX Routes ***
    # *******************

    # Agent methods

    def list_agents(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Agent]:
        """
        List all agents with optional pagination and sorting (synchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Agent objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request("GET", "/api/v2/actx/agents", params=params)
        return [
            Agent.model_validate(agent).bind_client(self) for agent in response.json()
        ]

    async def async_list_agents(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Agent]:
        """
        List all agents with optional pagination and sorting (asynchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Agent objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET", "/api/v2/actx/agents", params=params
        )
        return [
            Agent.model_validate(agent).bind_client(self) for agent in response.json()
        ]

    def create_agent(self, agent_create: Optional[AgentCreate] = None) -> Agent:
        """
        Create a new agent (synchronous).

        Args:
            agent_create: Agent creation parameters

        Returns:
            Created Agent object
        """
        data = agent_create.model_dump() if agent_create else {}
        response = self._request("POST", "/api/v2/actx/agents", json_data=data)
        return Agent.model_validate(response.json()).bind_client(self)

    async def async_create_agent(
        self, agent_create: Optional[AgentCreate] = None
    ) -> Agent:
        """
        Create a new agent (asynchronous).

        Args:
            agent_create: Agent creation parameters

        Returns:
            Created Agent object
        """
        data = agent_create.model_dump() if agent_create else {}
        response = await self._async_request(
            "POST", "/api/v2/actx/agents", json_data=data
        )
        return Agent.model_validate(response.json()).bind_client(self)

    def get_agent(self, agent_id: str) -> Agent:
        """
        Get an agent by ID (synchronous).

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            Agent object
        """
        response = self._request("GET", f"/api/v2/actx/agents/{agent_id}")
        return Agent.model_validate(response.json()).bind_client(self)

    async def async_get_agent(self, agent_id: str) -> Agent:
        """
        Get an agent by ID (asynchronous).

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            Agent object
        """
        response = await self._async_request("GET", f"/api/v2/actx/agents/{agent_id}")
        return Agent.model_validate(response.json()).bind_client(self)

    def update_agent(self, agent_id: str, agent_update: AgentUpdate) -> Agent:
        """
        Update an existing agent (synchronous).

        Args:
            agent_id: ID of the agent to update
            agent_update: Agent update parameters

        Returns:
            Updated Agent object
        """
        response = self._request(
            "PATCH",
            f"/api/v2/actx/agents/{agent_id}",
            json_data=agent_update.model_dump(),
        )
        return Agent.model_validate(response.json()).bind_client(self)

    async def async_update_agent(
        self, agent_id: str, agent_update: AgentUpdate
    ) -> Agent:
        """
        Update an existing agent (asynchronous).

        Args:
            agent_id: ID of the agent to update
            agent_update: Agent update parameters

        Returns:
            Updated Agent object
        """
        response = await self._async_request(
            "PATCH",
            f"/api/v2/actx/agents/{agent_id}",
            json_data=agent_update.model_dump(),
        )
        return Agent.model_validate(response.json()).bind_client(self)

    # Agent Session methods

    def list_agent_sessions(
        self,
        agent_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[AgentSession]:
        """
        List all sessions for an agent with optional pagination and sorting (synchronous).

        Args:
            agent_id: ID of the agent
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request(
            "GET", f"/api/v2/actx/agents/{agent_id}/agent-sessions", params=params
        )
        return [
            AgentSession.model_validate(session).bind_client(self)
            for session in response.json()
        ]

    async def async_list_agent_sessions(
        self,
        agent_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[AgentSession]:
        """
        List all sessions for an agent with optional pagination and sorting (asynchronous).

        Args:
            agent_id: ID of the agent
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET", f"/api/v2/actx/agents/{agent_id}/agent-sessions", params=params
        )
        return [
            AgentSession.model_validate(session).bind_client(self)
            for session in response.json()
        ]

    def create_agent_session(
        self, agent_id: str, agent_session_create: Optional[AgentSessionCreate] = None
    ) -> AgentSession:
        """
        Create a new agent session (synchronous).

        Args:
            agent_id: ID of the agent
            agent_session_create: Session creation parameters

        Returns:
            Created AgentSession object
        """
        data = agent_session_create.model_dump() if agent_session_create else {}
        response = self._request(
            "POST", f"/api/v2/actx/agents/{agent_id}/agent-sessions", json_data=data
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    async def async_create_agent_session(
        self, agent_id: str, agent_session_create: Optional[AgentSessionCreate] = None
    ) -> AgentSession:
        """
        Create a new agent session (asynchronous).

        Args:
            agent_id: ID of the agent
            agent_session_create: Session creation parameters

        Returns:
            Created AgentSession object
        """
        data = agent_session_create.model_dump() if agent_session_create else {}
        response = await self._async_request(
            "POST", f"/api/v2/actx/agents/{agent_id}/agent-sessions", json_data=data
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    def get_agent_session(self, agent_session_id: str) -> AgentSession:
        """
        Get an agent session by ID (synchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        response = self._request(
            "GET", f"/api/v2/actx/agent-sessions/{agent_session_id}"
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    async def async_get_agent_session(self, agent_session_id: str) -> AgentSession:
        """
        Get an agent session by ID (asynchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        response = await self._async_request(
            "GET", f"/api/v2/actx/agent-sessions/{agent_session_id}"
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    def update_agent_session(
        self, agent_session_id: str, agent_session_update: AgentSessionUpdate
    ) -> AgentSession:
        """
        Update an existing agent session (synchronous).

        Args:
            agent_session_id: ID of the session to update
            agent_session_update: Session update parameters

        Returns:
            Updated AgentSession object
        """
        response = self._request(
            "PATCH",
            f"/api/v2/actx/agent-sessions/{agent_session_id}",
            json_data=agent_session_update.model_dump(exclude_unset=True),
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    async def async_update_agent_session(
        self, agent_session_id: str, agent_session_update: AgentSessionUpdate
    ) -> AgentSession:
        """
        Update an existing agent session (asynchronous).

        Args:
            agent_session_id: ID of the session to update
            agent_session_update: Session update parameters

        Returns:
            Updated AgentSession object
        """
        response = await self._async_request(
            "PATCH",
            f"/api/v2/actx/agent-sessions/{agent_session_id}",
            json_data=agent_session_update.model_dump(exclude_unset=True),
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    def wake_agent_session(self, agent_session_id: str) -> AgentSessionWake:
        """
        Wake an agent session (synchronous).

        Args:
            agent_session_id: ID of the session to wake

        Returns:
            AgentSessionWake response
        """
        response = self._request(
            "POST", f"/api/v2/actx/agent-sessions/{agent_session_id}/wake"
        )
        return AgentSessionWake.model_validate(response.json())

    async def async_wake_agent_session(self, agent_session_id: str) -> AgentSessionWake:
        """
        Wake an agent session (asynchronous).

        Args:
            agent_session_id: ID of the session to wake

        Returns:
            AgentSessionWake response
        """
        response = await self._async_request(
            "POST", f"/api/v2/actx/agent-sessions/{agent_session_id}/wake"
        )
        return AgentSessionWake.model_validate(response.json())

    # Message methods

    def list_messages(
        self,
        agent_session_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List[Message]:
        """
        List all messages for an agent session with optional pagination and filtering (synchronous).

        Args:
            agent_session_id: ID of the session
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "read": read,
            "sender": sender,
            "created_after": created_after,
            "created_before": created_before,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request(
            "GET",
            f"/api/v2/actx/agent-sessions/{agent_session_id}/messages",
            params=params,
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    async def async_list_messages(
        self,
        agent_session_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List[Message]:
        """
        List all messages for an agent session with optional pagination and filtering (asynchronous).

        Args:
            agent_session_id: ID of the session
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "read": read,
            "sender": sender,
            "created_after": created_after,
            "created_before": created_before,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET",
            f"/api/v2/actx/agent-sessions/{agent_session_id}/messages",
            params=params,
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    def send_message(
        self, agent_session_id: str, message: Union[MessageCreate, MessagePayload, str]
    ) -> Message:
        """
        Send a message to an agent session (synchronous).

        Args:
            agent_session_id: ID of the session
            message: Message to send (can be a MessageCreate, MessagePayload, or string)

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message, sender="user")
        elif isinstance(message, MessageCreate):
            message_data = message.payload
        else:  # MessagePayload
            message_data = message

        response = self._request(
            "POST",
            f"/api/v2/actx/agent-sessions/{agent_session_id}/messages",
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    async def async_send_message(
        self, session_id: str, message: Union[MessageCreate, MessagePayload, str]
    ) -> Message:
        """
        Send a message to an agent session (asynchronous).

        Args:
            session_id: ID of the session
            message: Message to send (can be a MessageCreate, MessagePayload, or string)

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message)
        elif isinstance(message, MessageCreate):
            message_data = message.payload
        else:  # MessagePayload
            message_data = message

        response = await self._async_request(
            "POST",
            f"/api/v2/actx/agent-sessions/{session_id}/messages",
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    def get_message(self, message_id: str) -> Message:
        """
        Get a message by ID (synchronous).

        Args:
            message_id: ID of the message to retrieve

        Returns:
            Message object
        """
        response = self._request("GET", f"/api/v2/actx/messages/{message_id}")
        return Message.model_validate(response.json()).bind_client(self)

    async def async_get_message(self, message_id: str) -> Message:
        """
        Get a message by ID (asynchronous).

        Args:
            message_id: ID of the message to retrieve

        Returns:
            Message object
        """
        response = await self._async_request(
            "GET", f"/api/v2/actx/messages/{message_id}"
        )
        return Message.model_validate(response.json()).bind_client(self)

    def update_message(self, message_id: str, message_update: MessageUpdate) -> Message:
        """
        Update a message by ID (synchronous).

        Currently supports marking messages as read.

        Args:
            message_id: ID of the message to update
            message_update: Update parameters (e.g., read status)

        Returns:
            Updated Message object
        """
        response = self._request(
            "PATCH",
            f"/api/v2/actx/messages/{message_id}",
            json_data=message_update.model_dump(exclude_unset=True),
        )
        return Message.model_validate(response.json()).bind_client(self)

    async def async_update_message(
        self, message_id: str, message_update: MessageUpdate
    ) -> Message:
        """
        Update a message by ID (asynchronous).

        Currently supports marking messages as read.

        Args:
            message_id: ID of the message to update
            message_update: Update parameters (e.g., read status)

        Returns:
            Updated Message object
        """
        response = await self._async_request(
            "PATCH",
            f"/api/v2/actx/messages/{message_id}",
            json_data=message_update.model_dump(exclude_unset=True),
        )
        return Message.model_validate(response.json()).bind_client(self)

    # *********************
    # *** Simple Routes ***
    # *********************

    def send_simple_message(
        self,
        user_key: str,
        message: Union[MessagePayload, str],
        wake_agent: bool = True,
    ) -> Message:
        """
        Send a message using the simple API (synchronous).

        Args:
            user_key: User key for identification
            message: Message to send (can be a MessagePayload or string)
            wake_agent: Whether to wake the agent

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message)
        else:  # MessagePayload
            message_data = message

        params = {"wake_agent": wake_agent}

        response = self._request(
            "POST",
            f"/api/v2/simple/user-keys/{user_key}/message",
            params=params,
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    async def async_send_simple_message(
        self,
        user_key: str,
        message: Union[MessagePayload, str],
        wake_agent: bool = True,
    ) -> Message:
        """
        Send a message using the simple API (asynchronous).

        Args:
            user_key: User key for identification
            message: Message to send (can be a MessagePayload or string)
            wake_agent: Whether to wake the agent

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message)
        else:  # MessagePayload
            message_data = message

        params = {"wake_agent": wake_agent}

        response = await self._async_request(
            "POST",
            f"/api/v2/simple/user-keys/{user_key}/message",
            params=params,
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    def get_simple_messages(
        self,
        user_key: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Message]:
        """
        Get messages using the simple API (synchronous).

        Args:
            user_key: User key for identification
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request(
            "GET", f"/api/v2/simple/user-keys/{user_key}/messages", params=params
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    async def async_get_simple_messages(
        self,
        user_key: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Message]:
        """
        Get messages using the simple API (asynchronous).

        Args:
            user_key: User key for identification
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET", f"/api/v2/simple/user-keys/{user_key}/messages", params=params
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    def get_user_key(self, user_key: str) -> UserKeyRead:
        """
        Get user key information (synchronous).

        Args:
            user_key: User key to retrieve

        Returns:
            UserKeyRead object
        """
        response = self._request("GET", f"/api/v2/simple/user-keys/{user_key}")
        return UserKeyRead.model_validate(response.json())

    async def async_get_user_key(self, user_key: str) -> UserKeyRead:
        """
        Get user key information (asynchronous).

        Args:
            user_key: User key to retrieve

        Returns:
            UserKeyRead object
        """
        response = await self._async_request(
            "GET", f"/api/v2/simple/user-keys/{user_key}"
        )
        return UserKeyRead.model_validate(response.json())

    # ************************
    # *** Streaming Routes ***
    # ************************

    async def async_stream_agent_session_events(
        self,
        agent_session_id: str,
        on_status: Optional[Callable[[bool, float], None]] = None,
        on_complete: Optional[Callable[[float], None]] = None,
        on_error: Optional[Callable[[str, float], None]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream events from an agent session using Server-Sent Events (asynchronous).

        This method returns an async generator that yields event data as dictionaries.
        You can also provide callback functions to handle specific event types.

        Args:
            agent_session_id: ID of the agent session to stream events from
            on_status: Optional callback for status events (is_awake, timestamp)
            on_complete: Optional callback for complete events (timestamp)
            on_error: Optional callback for error events (error_message, timestamp)

        Yields:
            Dict containing event type and data

        Example:
            ```python
            async for event in client.async_stream_agent_session_events(session_id):
                print(f"Event: {event['event']}, Data: {event['data']}")
            ```
        """
        url = self._get_url(
            f"/api/v2/actx/agent-sessions/{agent_session_id}/event-stream"
        )
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url, headers=headers) as response:
                response.raise_for_status()

                # Process the SSE stream
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk

                    # Process complete events in the buffer
                    while "\n\n" in buffer:
                        event_data, buffer = buffer.split("\n\n", 1)
                        lines = event_data.strip().split("\n")

                        event_type = "message"
                        data = ""

                        for line in lines:
                            if line.startswith("event:"):
                                event_type = line[6:].strip()
                            elif line.startswith("data:"):
                                data = line[5:].strip()

                        # Parse data if it's not empty and not a heartbeat
                        if data and event_type != "heartbeat":
                            try:
                                parsed_data = json.loads(data)
                            except json.JSONDecodeError:
                                parsed_data = data
                        else:
                            parsed_data = None

                        event = {"event": event_type, "data": parsed_data}

                        # Call appropriate callback if provided
                        if event_type == "status" and on_status and parsed_data:
                            on_status(
                                parsed_data.get("is_awake"),
                                parsed_data.get("timestamp"),
                            )
                        elif event_type == "complete" and on_complete and parsed_data:
                            on_complete(parsed_data.get("timestamp"))
                        elif event_type == "error" and on_error and parsed_data:
                            on_error(
                                parsed_data.get("error", "Unknown error"),
                                parsed_data.get("timestamp"),
                            )

                        # Skip yielding heartbeats
                        if event_type != "heartbeat":
                            yield event

                        # If complete event received, exit the loop
                        if event_type == "complete":
                            break

    async def async_wait_for_agent_completion(
        self, agent_session_id: str, timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Wait for an agent session to complete processing (asynchronous).

        This method blocks until the agent completes or the timeout is reached.

        Args:
            agent_session_id: ID of the agent session to wait for
            timeout: Maximum time to wait in seconds (default: 60s)

        Returns:
            Dict with status information

        Example:
            ```python
            result = await client.async_wait_for_agent_completion(session_id, timeout=30.0)
            if result["status"] == "completed":
                print("Agent completed successfully")
            else:
                print("Timeout waiting for agent to complete")
            ```
        """
        completion_event = asyncio.Event()
        result = {
            "status": "timeout",
            "agent_session_id": agent_session_id,
            "timestamp": None,
        }

        def on_status(is_awake: bool, timestamp: float):
            if not is_awake:
                result["status"] = "completed"
                result["timestamp"] = timestamp
                completion_event.set()

        def on_complete(timestamp: float):
            result["status"] = "completed"
            result["timestamp"] = timestamp
            completion_event.set()

        def on_error(error: str, timestamp: float):
            result["status"] = "error"
            result["error"] = error
            result["timestamp"] = timestamp
            completion_event.set()

        # Start streaming task
        stream_task = asyncio.create_task(
            self._stream_until_event(
                agent_session_id,
                completion_event,
                on_status=on_status,
                on_complete=on_complete,
                on_error=on_error,
            )
        )

        # Wait for completion or timeout
        try:
            await asyncio.wait_for(completion_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["timestamp"] = time.time()
        finally:
            # Clean up the streaming task
            if not stream_task.done():
                stream_task.cancel()
                try:
                    await stream_task
                except asyncio.CancelledError:
                    pass

        # Check if there was an error
        if result.get("status") == "error":
            raise ActxAPIError(
                f"Error while waiting for agent completion: {result.get('error')}"
            )

        return result

    async def _stream_until_event(
        self, agent_session_id: str, stop_event: asyncio.Event, **callbacks
    ):
        """Helper method to stream events until a stop event is triggered."""
        try:
            async for _ in self.async_stream_agent_session_events(
                agent_session_id, **callbacks
            ):
                if stop_event.is_set():
                    break
        except Exception as e:
            # If we get an exception and the event isn't set, set it and propagate the error
            if not stop_event.is_set():
                callbacks.get("on_error", lambda *args: None)(str(e), time.time())
                stop_event.set()

    def wait_for_agent_completion(
        self, agent_session_id: str, timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Wait for an agent session to complete processing (synchronous).

        This method blocks until the agent completes or the timeout is reached.

        Args:
            agent_session_id: ID of the agent session to wait for
            timeout: Maximum time to wait in seconds (default: 60s)

        Returns:
            Dict with status information

        Example:
            ```python
            result = client.wait_for_agent_completion(session_id, timeout=30.0)
            if result["status"] == "completed":
                print("Agent completed successfully")
            else:
                print("Timeout waiting for agent to complete")
            ```
        """
        # Run the async version in a new event loop
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.async_wait_for_agent_completion(agent_session_id, timeout)
            )
        finally:
            loop.close()
