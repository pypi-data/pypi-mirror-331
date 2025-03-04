from typing import TYPE_CHECKING, Dict, List, Optional, Union, AsyncGenerator, Callable, Any
import asyncio

from tiptree.utils import ClientBind

if TYPE_CHECKING:
    from tiptree.interface_models import (
        AgentSession,
        AgentSessionWake,
        Message,
        MessageCreate,
        MessagePayload,
        AgentSessionUpdate,
        AgentSessionConfig,
    )


class AgentSessionMixin(ClientBind):
    id: str
    config: Optional["AgentSessionConfig"]
    info: dict | None

    def _create_agent_session_update_params(
        self,
        agent_session_update: Optional["AgentSessionUpdate"],
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> "AgentSessionUpdate":
        """Create AgentSessionUpdate from parameters if needed."""
        if agent_session_update is None and (
            initial_prompt is not None or metadata is not None
        ):
            from tiptree.interface_models import AgentSessionUpdate, AgentSessionConfig

            # Start with current values if available
            current_config = self.config

            # Create new config if needed
            if current_config:
                # Update existing config with new values
                config_dict = current_config.model_dump()
                if initial_prompt is not None:
                    config_dict["initial_prompt"] = initial_prompt
                if metadata is not None:
                    config_dict["metadata"] = metadata
                config = AgentSessionConfig(**config_dict)
            else:
                # Create new config with provided values
                config = AgentSessionConfig(
                    initial_prompt=initial_prompt, metadata=metadata
                )

            return AgentSessionUpdate(config=config)
        return agent_session_update

    @property
    def title(self) -> str | None:
        if self.info is None:
            return None
        return self.info.get("title")

    def wake(self) -> "AgentSessionWake":
        """
        Wake this agent session (synchronous).

        Returns:
            AgentSessionWake response
        """
        self.ensure_client_bound()
        return self.client.wake_agent_session(self.id)

    async def async_wake(self) -> "AgentSessionWake":
        """
        Wake this agent session (asynchronous).

        Returns:
            AgentSessionWake response
        """
        self.ensure_client_bound()
        return await self.client.async_wake_agent_session(self.id)

    def get_messages(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List["Message"]:
        """
        Get messages for this agent session with optional filtering (synchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        self.ensure_client_bound()
        return self.client.list_messages(
            self.id,
            offset=offset,
            limit=limit,
            read=read,
            sender=sender,
            created_after=created_after,
            created_before=created_before,
        )

    async def async_get_messages(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List["Message"]:
        """
        Get messages for this agent session with optional filtering (asynchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        self.ensure_client_bound()
        return await self.client.async_list_messages(
            self.id,
            offset=offset,
            limit=limit,
            read=read,
            sender=sender,
            created_after=created_after,
            created_before=created_before,
        )

    def send_message(
        self, message: Union["MessageCreate", "MessagePayload", str], wake: bool = False
    ) -> "Message":
        """
        Send a message to this agent session (synchronous).

        Args:
            message: Message to send (can be a MessageCreate, MessagePayload, or string)
            wake: Whether to wake the agent session after sending the message

        Returns:
            Created Message object
        """
        self.ensure_client_bound()
        result = self.client.send_message(self.id, message)
        if wake:
            self.wake()
        return result

    async def async_send_message(
        self, message: Union["MessageCreate", "MessagePayload", str], wake: bool = False
    ) -> "Message":
        """
        Send a message to this agent session (asynchronous).

        Args:
            message: Message to send (can be a MessageCreate, MessagePayload, or string)
            wake: Whether to wake the agent session after sending the message

        Returns:
            Created Message object
        """
        self.ensure_client_bound()
        result = await self.client.async_send_message(self.id, message)
        if wake:
            await self.async_wake()
        return result

    def update(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_update: Optional["AgentSessionUpdate"] = None,
    ) -> "AgentSession":
        """
        Update this agent session (synchronous).

        Args:
            initial_prompt: Optional new initial prompt for the session
            metadata: Optional new metadata for the session
            agent_session_update: Optional session update parameters

        Returns:
            Updated AgentSession object
        """
        self.ensure_client_bound()
        agent_session_update = self._create_agent_session_update_params(
            agent_session_update, initial_prompt, metadata
        )
        return self.client.update_agent_session(self.id, agent_session_update)

    async def async_update(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_update: Optional["AgentSessionUpdate"] = None,
    ) -> "AgentSession":
        """
        Update this agent session (asynchronous).

        Args:
            initial_prompt: Optional new initial prompt for the session
            metadata: Optional new metadata for the session
            agent_session_update: Optional session update parameters

        Returns:
            Updated AgentSession object
        """
        self.ensure_client_bound()
        agent_session_update = self._create_agent_session_update_params(
            agent_session_update, initial_prompt, metadata
        )
        return await self.client.async_update_agent_session(
            self.id, agent_session_update
        )

    async def async_stream_events(
        self,
        on_status: Optional[Callable[[bool, float], None]] = None,
        on_complete: Optional[Callable[[float], None]] = None,
        on_error: Optional[Callable[[str, float], None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream events from this agent session using Server-Sent Events (asynchronous).
        
        This method returns an async generator that yields event data as dictionaries.
        You can also provide callback functions to handle specific event types.
        
        Args:
            on_status: Optional callback for status events (is_awake, timestamp)
            on_complete: Optional callback for complete events (timestamp)
            on_error: Optional callback for error events (error_message, timestamp)
            
        Yields:
            Dict containing event type and data
            
        Example:
            ```python
            async for event in session.async_stream_events():
                print(f"Event: {event['event']}, Data: {event['data']}")
            ```
        """
        self.ensure_client_bound()
        async for event in self.client.async_stream_agent_session_events(
            self.id, on_status=on_status, on_complete=on_complete, on_error=on_error
        ):
            yield event
    
    async def async_wait_for_completion(self, timeout: float = 60.0) -> Dict[str, Any]:
        """
        Wait for this agent session to complete processing (asynchronous).
        
        This method blocks until the agent completes or the timeout is reached.
        
        Args:
            timeout: Maximum time to wait in seconds (default: 60s)
            
        Returns:
            Dict with status information
            
        Example:
            ```python
            result = await session.async_wait_for_completion(timeout=30.0)
            if result["status"] == "completed":
                print("Agent completed successfully")
            else:
                print("Timeout waiting for agent to complete")
            ```
        """
        self.ensure_client_bound()
        return await self.client.async_wait_for_agent_completion(self.id, timeout=timeout)
    
    def wait_for_completion(self, timeout: float = 120.0) -> Dict[str, Any]:
        """
        Wait for this agent session to complete processing (synchronous).
        
        This method blocks until the agent completes or the timeout is reached.
        
        Args:
            timeout: Maximum time to wait in seconds (default: 60s)
            
        Returns:
            Dict with status information
            
        Example:
            ```python
            result = session.wait_for_completion(timeout=30.0)
            if result["status"] == "completed":
                print("Agent completed successfully")
            else:
                print("Timeout waiting for agent to complete")
            ```
        """
        self.ensure_client_bound()
        return self.client.wait_for_agent_completion(self.id, timeout=timeout)
