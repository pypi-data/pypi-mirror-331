import logging
import sys
import requests
from typing import List, Dict, Any
from urllib.parse import urljoin

# 设置默认日志格式
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class AgentSDK:
    """Agent SDK for interacting with Agent services."""

    def __init__(self, base_url: str, agent_id: int):
        """Initialize SDK.

        Args:
            base_url: API base URL
            agent_id: Agent ID
        """
        self.base_url = base_url.rstrip("/")
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"{__name__}.AgentSDK_{agent_id}")

    def _make_url(self, path: str) -> str:
        """Build complete API URL.

        Args:
            path: API path

        Returns:
            Complete API URL
        """
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    def think(self, content: str) -> str:
        """Send a thought to the Agent.

        Args:
            content: Thought content

        Returns:
            Agent's response
        """
        url = self._make_url("/v1/agents/python/think")
        data = {"agent_id": self.agent_id, "content": content}

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            if "result" in result:
                return result["result"]
            raise Exception(f"Unexpected response: {result}")
        except Exception as e:
            self.logger.error(f"Think failed: {e}")
            raise

    def look(self, query: str, img_urls: List[str]) -> str:
        """Have the Agent process images.

        Args:
            query: Query content
            img_urls: List of image URLs

        Returns:
            Processing result
        """
        url = self._make_url("/v1/agents/python/look")
        data = {"agent_id": self.agent_id, "query": query, "image_urls": img_urls}

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            if "result" in result:
                return result["result"]
            raise Exception(f"Unexpected response: {result}")
        except Exception as e:
            self.logger.error(f"Look failed: {e}")
            raise

    def call_ability(self, namespace: str, name: str, *args: Any) -> Any:
        """Call an Agent ability.

        Args:
            namespace: Ability namespace
            name: Ability name
            args: Ability arguments

        Returns:
            Ability execution result
        """
        url = self._make_url("/v1/agents/python/call_ability")
        data = {
            "agent_id": self.agent_id,
            "namespace": namespace,
            "name": name,
            "args": args,
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            if "result" in result:
                return result["result"]
            raise Exception(f"Unexpected response: {result}")
        except Exception as e:
            self.logger.error(f"Call ability failed: {e}")
            raise

    def clear_memory(self, session_id: str = None) -> Dict[str, Any]:
        """Clear agent's memory.

        Args:
            session_id: Optional session ID to clear specific session memory

        Returns:
            Response containing code, message and data
        """
        url = self._make_url("/v1/memory/clear")
        params = {"agent_id": self.agent_id}
        if session_id:
            params["session_id"] = session_id

        try:
            response = requests.delete(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Clear memory failed: {e}")
            raise


class AgentContext:
    """Agent context manager."""

    def __init__(
        self,
        agent_info: Dict[str, Any],
        base_url: str = "http://127.0.0.1:8086",
    ):
        """Initialize context.

        Args:
            agent_info: Agent information dictionary with at least 'id' field.
                      In platform environment, this will be automatically injected.
                      In local development, you can mock it with {"id": your_agent_id}
            base_url: API base URL (defaults to http://127.0.0.1:8086)
        """
        if not isinstance(agent_info, dict):
            raise ValueError("agent_info must be a dictionary")

        if "id" not in agent_info:
            raise ValueError("agent_info must contain 'id' field")

        self.agent_info = agent_info
        self.sdk = AgentSDK(base_url, agent_info["id"])
        self.logger = logger

    def __enter__(self):
        """Enter context."""
        name = self.agent_info.get("name", f"Agent_{self.agent_info['id']}")
        self.logger.info(f"Starting execution: {name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type:
            self.logger.error(f"Execution error: {exc_val}")
        else:
            self.logger.info("Execution complete")
        return False

    def think(self, content: str) -> str:
        """Send a thought to the Agent."""
        return self.sdk.think(content)

    def look(self, query: str, img_urls: List[str]) -> str:
        """Have the Agent process images."""
        return self.sdk.look(query, img_urls)

    def call_ability(self, namespace: str, name: str, *args: Any) -> Any:
        """Call an Agent ability."""
        return self.sdk.call_ability(namespace, name, *args)

    def clear_memory(self, session_id: str = None) -> Dict[str, Any]:
        """Clear agent's memory.

        Args:
            session_id: Optional session ID to clear specific session memory

        Returns:
            Response containing code, message and data
        """
        return self.sdk.clear_memory(session_id)
