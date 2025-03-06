import os
from enum import Enum
from typing import Any, Dict, List, Optional
import asyncio
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    Tool,
    GoogleSearch,
    Content,
    Part
)
from asyncio.log import logger

from ..base_classes.llm_client import LLMClient


class Gemini(LLMClient):
    """
    A streamlined and consolidated client for interfacing with the Gemini LLM,
    integrating functionalities for text generation and chat.
    """

    class Models(Enum):
        GEMINI_2_0_FLASH = "gemini-2.0-flash"
        GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"
        GEMINI_2_0_FLASH_THINKING = "gemini-2.0-flash-thinking-exp"
        GEMINI_2_0_PRO = "gemini-2.0-pro-exp-02-05"

    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        location: Optional[str] = "us-central1",
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        use_tools: Optional[bool] = False,
        generation_config: Optional[Dict[str, Any]] = None,
        max_retries: int = 8,
        base_wait_time: int = 10
    ):
        """
        Initializes the Gemini client.

        :param model: Name of the model to use (e.g. 'gemini-2.0-flash-exp').
        :param location: The default location to use when making API calls. Defaults to 'us-central1'.
        :param max_output_tokens: Maximum number of tokens to generate in the response.
        :param temperature: Controls the randomness of the responses.
        :param top_p:  Nucleus sampling parameter.
        :param use_tools: Whether to enable Google Search tool by default for `run` method.
        :param generation_config: Optional dictionary to directly pass generation parameters.
                                  If provided, it overrides individual parameters like temperature, top_p, etc.
        :param max_retries: Maximum number of retries for the `run` method.
        :param base_wait_time: Base wait time (in seconds) for exponential backoff.
        """
        self._use_tools = use_tools
        self._client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        self._model_name = model
        self._location = location
        self._chat_session = None  # Initialize chat session to None
        self._max_retries = max_retries  # Store max_retries
        self._base_wait_time = base_wait_time # Store base_wait_time

        if generation_config is not None:
            # Use provided generation_config directly, overriding individual parameters
            self._generation_config = GenerateContentConfig(**generation_config)
        else:
            # Construct generation config from individual parameters if not provided
            config_params = {}
            if max_output_tokens is not None:
                config_params["max_output_tokens"] = max_output_tokens
            if temperature is not None:
                config_params["temperature"] = temperature
            if top_p is not None:
                config_params["top_p"] = top_p
            self._generation_config = GenerateContentConfig(**config_params) if config_params else None


    async def start_chat(self, history: Optional[List[Dict[str, str]]] = None) -> None:
        """
        Starts a new chat session with the Gemini model (async).

        :param history: Optional chat history to initialize the chat with.
        """
        if history is not None:
            genai_history = []
            for turn in history:
                user_message = [Part(text=text) for text in turn.get('user', [''])]
                model_message = [Part(text=text) for text in turn.get('model', [''])]
                genai_history.append(Content(role='user', parts=user_message))
                genai_history.append(Content(role='model', parts=model_message))

            self._chat_session = await asyncio.to_thread(
                self._client.chats.create,
                model=self._model_name,
                history=genai_history
            )
        else:
            self._chat_session = await asyncio.to_thread(
                self._client.chats.create,
                model=self._model_name
            )

    async def send_message(self, message: str) -> Dict[str, Any]:
        """
        Sends a message to the active chat session and gets the model's response (async).

        :param message: The message to send to the Gemini model.
        :raises RuntimeError: if a chat session has not been started yet.
        :returns: A dictionary with the following key:
            - `replies`: A list containing the model's response.
        """
        if self._chat_session is None:
            raise RuntimeError("Chat session not started.")

        response = await asyncio.to_thread(
            self._chat_session.send_message,
            message=message
        )
        replies = [response.text]
        return {"replies": replies}

    async def run_text_internal(self, parts: List[str]) -> Dict[str, Any]:
        """
        Generates content using the Gemini model in a non-chat setting. Internal method, accepts Part objects.

        :param parts: Prompt for the model as a list of Part objects.
        :returns: A dictionary with the following key:
            - `replies`: A list of generated content.
        """
        prompt_text = " ".join(parts)

        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._model_name,
            contents=prompt_text,
            config=self._generation_config
        )

        replies = [response.text]
        return {"replies": replies}

    async def run_search_internal(self, parts: List[str]) -> Dict[str, Any]:
        """
        Generates content using the Gemini model *with* the Google Search tool enabled in a non-chat setting.
        Internal method, accepts Part objects.

        :param parts: Prompt or question for the model as a list of Part objects.
        :returns: A dictionary with the following key:
            - `replies`: A list of generated content that may include grounded answers from search.
        """
        query_text = " ".join(parts)

        # Define the Google Search tool
        google_search_tool = Tool(google_search=GoogleSearch())

        # Build a config that includes the GoogleSearch tool
        search_config = GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"]
        )

        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._model_name,
            contents=query_text,
            config=search_config
        )

        replies = []
        for candidate in response.candidates:
            # Each candidate may have multiple parts
            text_parts = [part.text for part in candidate.content.parts]
            # Combine text parts for a single candidate
            replies.append(" ".join(text_parts))

        return {"replies": replies}

    async def run(self, prompt_parts: List[str]) -> Dict[str, Any]:
        """
        Generates content using the Gemini model in a non-chat setting.
        If `use_tools` is True during initialization, it will use Google Search.
        Includes a retry mechanism.

        Args:
            prompt_parts (List[str]): The prepared prompt sections to send to Gemini.

        Returns:
            Dict[str, Any]: A dictionary containing the output text.
        """
        for attempt in range(1, self._max_retries + 1):
            try:
                if self._use_tools:
                    response = await self.run_search_internal(prompt_parts)
                else:
                    response = await self.run_text_internal(prompt_parts)
                return response

            except Exception as e:
                logger.info(f"Attempt {attempt} failed with error: {e} \n------\n")
                if attempt == self._max_retries:
                    raise  # Re-raise the exception after the last retry
                else:
                    # Exponential back-off
                    backoff_time = self._base_wait_time + (3 ** attempt)
                    await asyncio.sleep(backoff_time)

        return {"replies": []}  # Should never reach here because of the re-raise


    def component_run_stats(self, prompt_parts: List[str], replies: List[str]) -> Dict[str, Any]:
        """
        Calculates and returns component run statistics, including token usage.

        Args:
            prompt_parts (List[str]): The input prompt parts.
            replies (List[str]): The Gemini model's replies.

        Returns:
            Dict[str, Any]: A dictionary containing component run statistics.
        """
        output_text = " ".join(replies)
        output_char_count = len(output_text)
        output_token_count = output_char_count // self.CHARS_PER_TOKEN

        input_text = " ".join(prompt_parts)
        input_char_count = len(input_text)
        input_token_count = input_char_count // self.CHARS_PER_TOKEN

        token_usage = {
            "input_tokens": input_token_count,
            "output_tokens": output_token_count,
            "total_tokens": input_token_count + output_token_count,
        }

        component_run_stats = {
            "model": self._model_name,
            "input": input_text,
            "output": output_text,
            "token_usage": token_usage
        }

        return component_run_stats
