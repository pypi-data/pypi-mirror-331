from typing import TYPE_CHECKING, Dict, List, Optional

from tiptree.utils import ClientBind

if TYPE_CHECKING:
    from tiptree.interface_models import (
        Agent,
        AgentSession,
        AgentSessionCreate,
        AgentSessionConfig,
        AgentUpdate,
        AgentConfig,
        AgentCreate,
    )
    from tiptree.client import TiptreeClient


class AgentMixin(ClientBind):
    id: str
    config: Optional["AgentConfig"]
    info: Optional[Dict]

    def _create_agent_session_params(
        self,
        agent_session_create: Optional["AgentSessionCreate"],
        initial_prompt: Optional[str],
        metadata: Optional[Dict],
    ) -> Optional["AgentSessionCreate"]:
        """Create AgentSessionCreate from parameters if needed."""
        if agent_session_create is None and (
            initial_prompt is not None or metadata is not None
        ):
            from tiptree.interface_models import AgentSessionCreate, AgentSessionConfig

            config = AgentSessionConfig(
                initial_prompt=initial_prompt, metadata=metadata
            )
            return AgentSessionCreate(config=config)
        return agent_session_create

    def _create_agent_update_params(
        self,
        agent_update: Optional["AgentUpdate"],
        name: Optional[str],
        description: Optional[str],
        info: Optional[Dict],
    ) -> "AgentUpdate":
        """Create AgentUpdate from parameters if needed."""
        if agent_update is None and (
            name is not None or description is not None or info is not None
        ):
            from tiptree.interface_models import AgentUpdate, AgentConfig

            # Start with current values if available
            current_config = self.config
            current_info = self.info

            # Create new config if needed
            if name is not None or description is not None:
                config_kwargs = {}
                if name is not None:
                    config_kwargs["name"] = name
                if description is not None:
                    config_kwargs["description"] = description

                if current_config:
                    # Update existing config with new values
                    config_dict = current_config.model_dump()
                    config_dict.update(config_kwargs)
                    config = AgentConfig(**config_dict)
                else:
                    # Create new config
                    config = AgentConfig(**config_kwargs)
            else:
                config = current_config

            # Use provided info or current info
            final_info = info if info is not None else current_info

            return AgentUpdate(config=config, info=final_info)
        return agent_update

    @classmethod
    def _create_agent_create_params(
        cls,
        agent_create: Optional["AgentCreate"],
        name: Optional[str],
        description: Optional[str],
        info: Optional[Dict],
    ) -> Optional["AgentCreate"]:
        """Create AgentCreate from parameters if needed."""
        if agent_create is None and (
            name is not None or description is not None or info is not None
        ):
            from tiptree.interface_models import AgentCreate, AgentConfig

            config = None
            if name is not None or description is not None:
                config = AgentConfig(name=name or "", description=description)

            return AgentCreate(config=config, info=info)
        return agent_create

    @classmethod
    def create(
        cls,
        client: "TiptreeClient",
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        agent_create: Optional["AgentCreate"] = None,
    ) -> "Agent":
        """
        Create a new agent (synchronous).

        Args:
            client: TiptreeClient instance
            name: Optional name for the agent
            description: Optional description for the agent
            info: Optional info dictionary for the agent
            agent_create: Optional agent creation parameters

        Returns:
            Created Agent object
        """
        agent_create = cls._create_agent_create_params(
            agent_create, name, description, info
        )
        return client.create_agent(agent_create)

    @classmethod
    async def async_create(
        cls,
        client: "TiptreeClient",
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        agent_create: Optional["AgentCreate"] = None,
    ) -> "Agent":
        """
        Create a new agent (asynchronous).

        Args:
            client: TiptreeClient instance
            name: Optional name for the agent
            description: Optional description for the agent
            info: Optional info dictionary for the agent
            agent_create: Optional agent creation parameters

        Returns:
            Created Agent object
        """
        agent_create = cls._create_agent_create_params(
            agent_create, name, description, info
        )
        return await client.async_create_agent(agent_create)

    def create_agent_session(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_create: Optional["AgentSessionCreate"] = None,
    ) -> "AgentSession":
        """
        Create a new agent session for this agent (synchronous).

        Args:
            agent_session_create: Optional session creation parameters
            initial_prompt: Optional initial prompt for the session
            metadata: Optional metadata for the session

        Returns:
            Created AgentSession object
        """
        self.ensure_client_bound()
        agent_session_create = self._create_agent_session_params(
            agent_session_create, initial_prompt, metadata
        )
        return self.client.create_agent_session(self.id, agent_session_create)

    async def async_create_agent_session(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_create: Optional["AgentSessionCreate"] = None,
    ) -> "AgentSession":
        """
        Create a new agent session for this agent (asynchronous).

        Args:
            agent_session_create: Optional session creation parameters
            initial_prompt: Optional initial prompt for the session
            metadata: Optional metadata for the session

        Returns:
            Created AgentSession object
        """
        self.ensure_client_bound()
        agent_session_create = self._create_agent_session_params(
            agent_session_create, initial_prompt, metadata
        )
        return await self.client.async_create_agent_session(
            self.id, agent_session_create
        )

    def get_agent_session(self, agent_session_id: str) -> "AgentSession":
        """
        Get an agent session by ID (synchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        self.ensure_client_bound()
        return self.client.get_agent_session(agent_session_id)

    async def async_get_agent_session(self, agent_session_id: str) -> "AgentSession":
        """
        Get an agent session by ID (asynchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        self.ensure_client_bound()
        return await self.client.async_get_agent_session(agent_session_id)

    def list_agent_sessions(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List["AgentSession"]:
        """
        List all sessions for this agent with optional pagination and sorting (synchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        self.ensure_client_bound()
        return self.client.list_agent_sessions(
            self.id, offset=offset, limit=limit, most_recent_first=most_recent_first
        )

    async def async_list_agent_sessions(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List["AgentSession"]:
        """
        List all sessions for this agent with optional pagination and sorting (asynchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        self.ensure_client_bound()
        return await self.client.async_list_agent_sessions(
            self.id, offset=offset, limit=limit, most_recent_first=most_recent_first
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        agent_update: Optional["AgentUpdate"] = None,
    ) -> "Agent":
        """
        Update this agent (synchronous).

        Args:
            agent_update: Optional agent update parameters
            name: Optional new name for the agent
            description: Optional new description for the agent
            info: Optional new info dictionary for the agent

        Returns:
            Updated Agent object
        """
        self.ensure_client_bound()
        agent_update = self._create_agent_update_params(
            agent_update, name, description, info
        )
        return self.client.update_agent(self.id, agent_update)

    async def async_update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        agent_update: Optional["AgentUpdate"] = None,
    ) -> "Agent":
        """
        Update this agent (asynchronous).

        Args:
            agent_update: Optional agent update parameters
            name: Optional new name for the agent
            description: Optional new description for the agent
            info: Optional new info dictionary for the agent

        Returns:
            Updated Agent object
        """
        self.ensure_client_bound()
        agent_update = self._create_agent_update_params(
            agent_update, name, description, info
        )
        return await self.client.async_update_agent(self.id, agent_update)
