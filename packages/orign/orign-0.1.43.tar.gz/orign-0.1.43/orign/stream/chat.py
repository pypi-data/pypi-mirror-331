import base64
import json
from io import BytesIO
from typing import Iterator, List, Optional, Type, Union
from urllib.parse import quote

import websocket
from PIL import Image
from pydantic import BaseModel

from orign.config import GlobalConfig
from orign.models import (
    ChatRequest,
    ChatResponse,
    ContentItem,
    ErrorResponse,
    ImageUrlContent,
    MessageItem,
    ModelReadyResponse,
    Prompt,
    SamplingParams,
    TokenResponse,
)


class ChatModel:
    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        config: Optional[GlobalConfig] = None,
    ):
        config = config or GlobalConfig.read()
        self.debug = config.debug
        self.model = model
        self.provider = provider
        self.orign_host = config.server.strip("http://").strip("https://")
        self.websocket = None

        # Construct the WebSocket URL with query parameters
        self.ws_url = f"wss://{self.orign_host}/v1/chat/stream"
        params = []
        if self.model:
            params.append(f"model={quote(self.model)}")
        if self.provider:
            params.append(f"provider={quote(self.provider)}")

        if params:
            self.ws_url += "?" + "&".join(params)

        # Set up the headers
        self.headers = {"Authorization": f"Bearer {config.api_key}"}

    def connect(self):
        """Establish WebSocket connection if not already connected."""
        if not self.websocket:
            print(f"Connecting to {self.ws_url}")
            self.websocket = websocket.WebSocket()
            # Pass the headers when connecting
            self.websocket.connect(self.ws_url, header=self._format_headers())

    def _format_headers(self):
        """Format headers for websocket-client."""
        return [f"{key}: {value}" for key, value in self.headers.items()]

    def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            self.websocket.close()
            self.websocket = None

    def chat(
        self,
        msg: Optional[str] = None,
        image: Optional[str | Image.Image] = None,
        prompt: Optional[Prompt] = None,
        batch: Optional[List[Prompt]] = None,
        sampling_params: Optional[SamplingParams] = None,
        stream_tokens: bool = False,
        adapter: Optional[str] = None,
    ) -> Union[ChatResponse, Iterator[Union[TokenResponse, ChatResponse]]]:
        """Synchronous chat method."""
        self.connect()

        # Create ChatRequest object
        request = ChatRequest(
            sampling_params=sampling_params or SamplingParams(),
            stream=stream_tokens,
            prompt=prompt,
            batch=batch,
            model=self.model,
            adapter=adapter,
        )

        # If msg is provided, convert it to a Prompt
        if msg:
            content = [ContentItem(type="text", text=msg)]
            if image:
                if isinstance(image, Image.Image):
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    image = "data:image/png;base64," + base64.b64encode(
                        buffered.getvalue()
                    ).decode("utf-8")
                content.append(
                    ContentItem(type="image_url", image_url=ImageUrlContent(url=image))
                )
            request.prompt = Prompt(
                messages=[MessageItem(role="user", content=content)]
            )
        elif prompt:
            request.prompt = prompt
        elif batch:
            request.batch = batch

        if not self.websocket:
            raise ConnectionError("WebSocket connection not established")

        # Send the request
        self.websocket.send(request.model_dump_json())

        # Receive and process responses
        if stream_tokens:
            return self._chat_stream()
        else:
            return self._chat_once()

    def expect(
        self,
        schema: Type[BaseModel],
        msg: Optional[str] = None,
        image: Optional[str | Image.Image] = None,
        prompt: Optional[Prompt] = None,
        sampling_params: Optional[SamplingParams] = None,
        adapter: Optional[str] = None,
    ) -> Union[ChatResponse, Iterator[Union[TokenResponse, ChatResponse]]]:
        """Synchronous chat method."""
        self.connect()

        # Create ChatRequest object
        request = ChatRequest(
            sampling_params=sampling_params or SamplingParams(),
            prompt=prompt,
            model=self.model,
            adapter=adapter,
        )

        # If msg is provided, convert it to a Prompt
        if msg:
            content = [ContentItem(type="text", text=msg)]
            if image:
                if isinstance(image, Image.Image):
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    image = "data:image/png;base64," + base64.b64encode(
                        buffered.getvalue()
                    ).decode("utf-8")
                content.append(
                    ContentItem(type="image_url", image_url=ImageUrlContent(url=image))
                )
            request.prompt = Prompt(
                messages=[MessageItem(role="user", content=content)]
            )
        elif prompt:
            request.prompt = prompt

        if not self.websocket:
            raise ConnectionError("WebSocket connection not established")

        return self._expect_once(request, schema)

    def _expect_once(
        self,
        request: ChatRequest,
        schema: Type[BaseModel],
        max_retries: int = 3,
    ) -> ChatResponse:
        """Send the request, parse the response using the given schema, and retry if needed."""
        attempts = 0

        while attempts < max_retries:
            # If the WebSocket connection was lost between retries, ensure it's open
            if not self.websocket:
                self.connect()
            try:
                if not self.websocket:
                    raise ConnectionError("WebSocket connection not established")

                # Send the request
                self.websocket.send(request.model_dump_json())

                # Wait for and parse the single response
                response = self._chat_once()
                if self.debug:
                    print("expect response: ", response.choices[0].text, flush=True)

                response.parsed = schema.model_validate_json(response.choices[0].text)

                return response

            except (ConnectionError, ValueError, websocket.WebSocketException) as e:
                attempts += 1
                print(f"Attempt {attempts} failed with error: {e}", flush=True)

                # If we've used all retries, re-raise
                if attempts >= max_retries:
                    raise

                # Otherwise, close and reconnect before attempting again
                self.close()
                print("Reconnecting before retry...", flush=True)

        # Should never reach here since we either return or raise
        raise RuntimeError("Unexpected error in _expect_once (retry loop).")

    def _chat_once(self) -> ChatResponse:
        """Receive a single ChatResponse."""
        try:
            while True:
                response = self.websocket.recv()  # type: ignore
                response_data = json.loads(response)

                if response_data.get("type") == ChatResponse.__name__:
                    return ChatResponse.model_validate(response_data)
                elif response_data.get("type") == TokenResponse.__name__:
                    # Consume tokens until final response
                    continue
                elif response_data.get("type") == ModelReadyResponse.__name__:
                    ready = ModelReadyResponse.model_validate(response_data)
                    if not ready.ready:
                        raise ValueError(f"Model not ready: {ready.error}")
                elif response_data.get("type") == ErrorResponse.__name__:
                    error = ErrorResponse.model_validate(response_data)
                    raise ValueError(f"Error: {error.error}")
                else:
                    raise ValueError(f"Unknown response type: {response_data}")

        except websocket.WebSocketException as e:
            self.close()
            raise ConnectionError("WebSocket connection closed unexpectedly") from e

    def _chat_stream(self) -> Iterator[Union[TokenResponse, ChatResponse]]:
        """Yield responses as they arrive."""
        try:
            while True:
                response = self.websocket.recv()  # type: ignore
                response_data = json.loads(response)

                if response_data.get("type") == TokenResponse.__name__:
                    resp = TokenResponse.model_validate(response_data)
                    yield resp
                    all_done = all(
                        choice.finish_reason == "stop" for choice in resp.choices
                    )
                    if all_done:
                        print("Stream complete", flush=True)
                        break
                elif response_data.get("type") == ChatResponse.__name__:
                    yield ChatResponse.model_validate(response_data)
                    break
                elif response_data.get("type") == ModelReadyResponse.__name__:
                    ready = ModelReadyResponse.model_validate(response_data)
                    if not ready.ready:
                        raise ValueError(f"Model not ready: {ready.error}")
                elif response_data.get("type") == ErrorResponse.__name__:
                    error = ErrorResponse.model_validate(response_data)
                    raise ValueError(f"Error: {error.error}")
                else:
                    raise ValueError(f"Unknown response type: {response_data}")

        except websocket.WebSocketException as e:
            self.close()
            raise ConnectionError("WebSocket connection closed unexpectedly") from e

    def _parse_response(
        self, response: ChatResponse, model: Optional[Type[BaseModel]]
    ) -> ChatResponse:
        """Parse the response into a specific type."""
        if not model:
            return response

        # How do we handle multiple choices?
        response.parsed = model.model_validate(response.choices[0].text)
        return response
