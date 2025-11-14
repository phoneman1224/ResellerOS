"""
Ollama AI client for local LLM integration.
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, List

from src.config.settings import settings
from src.core.exceptions import OllamaError, OllamaUnavailableError

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama local LLM service."""

    def __init__(self, base_url: str = None, model: str = None):
        """Initialize Ollama client.

        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = aiohttp.ClientTimeout(total=settings.ollama_timeout)

    async def is_available(self) -> bool:
        """Check if Ollama service is available.

        Returns:
            True if Ollama is running and accessible
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        logger.debug("Ollama service is available")
                        return True
                    logger.warning(f"Ollama returned status {resp.status}")
                    return False
        except asyncio.TimeoutError:
            logger.warning("Ollama connection timeout")
            return False
        except aiohttp.ClientError as e:
            logger.warning(f"Ollama not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking Ollama availability: {e}")
            return False

    async def list_models(self) -> List[str]:
        """List available Ollama models.

        Returns:
            List of model names

        Raises:
            OllamaUnavailableError: If Ollama is not available
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [model["name"] for model in data.get("models", [])]
                        return models
                    else:
                        raise OllamaUnavailableError(f"Failed to list models: HTTP {resp.status}")
        except asyncio.TimeoutError:
            raise OllamaUnavailableError("Ollama connection timeout")
        except aiohttp.ClientError as e:
            raise OllamaUnavailableError(f"Ollama not available: {str(e)}")

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """Generate completion from Ollama.

        Args:
            prompt: User prompt
            system: Optional system prompt
            model: Model name (uses default if not provided)
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text or None if failed

        Raises:
            OllamaError: If generation fails
        """
        try:
            payload = {
                "model": model or self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            if system:
                payload["system"] = system

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response_text = data.get("response", "")
                        logger.debug(f"Generated {len(response_text)} characters")
                        return response_text
                    else:
                        error_text = await resp.text()
                        logger.error(f"Ollama error {resp.status}: {error_text}")
                        raise OllamaError(f"Generation failed: HTTP {resp.status}")
        except asyncio.TimeoutError:
            logger.error("Ollama generation timeout")
            raise OllamaError("Generation timeout")
        except aiohttp.ClientError as e:
            logger.error(f"Ollama connection error: {e}")
            raise OllamaError(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            raise OllamaError(f"Generation failed: {str(e)}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """Chat completion with message history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (uses default if not provided)
            temperature: Temperature for generation (0-1)

        Returns:
            Generated response or None if failed

        Raises:
            OllamaError: If chat fails
        """
        try:
            payload = {
                "model": model or self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        message = data.get("message", {})
                        response_text = message.get("content", "")
                        return response_text
                    else:
                        error_text = await resp.text()
                        logger.error(f"Ollama chat error {resp.status}: {error_text}")
                        raise OllamaError(f"Chat failed: HTTP {resp.status}")
        except asyncio.TimeoutError:
            logger.error("Ollama chat timeout")
            raise OllamaError("Chat timeout")
        except aiohttp.ClientError as e:
            logger.error(f"Ollama connection error: {e}")
            raise OllamaError(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during chat: {e}")
            raise OllamaError(f"Chat failed: {str(e)}")

    async def pull_model(self, model: str) -> bool:
        """Pull/download a model from Ollama library.

        Args:
            model: Model name to pull

        Returns:
            True if successful

        Raises:
            OllamaError: If pull fails
        """
        try:
            payload = {"name": model}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600)) as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Successfully pulled model: {model}")
                        return True
                    else:
                        error_text = await resp.text()
                        logger.error(f"Failed to pull model {model}: {error_text}")
                        raise OllamaError(f"Pull failed: HTTP {resp.status}")
        except Exception as e:
            logger.error(f"Error pulling model {model}: {e}")
            raise OllamaError(f"Pull failed: {str(e)}")
