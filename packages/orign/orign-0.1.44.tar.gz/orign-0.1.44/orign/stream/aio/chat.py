import base64
import json
from io import BytesIO
from typing import AsyncIterator, List, Optional
from urllib.parse import quote

import websockets
from PIL import Image

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


class AsyncChatModel:
    def __init__(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        config: Optional[GlobalConfig] = None,
    ):
        config = config or GlobalConfig.read()
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

    async def connect(self):
        """Establish WebSocket connection if not already connected"""
        if not self.websocket:
            config = GlobalConfig.read()
            headers = {"Authorization": f"Bearer {config.api_key}"}
            print("connecting to ", self.ws_url)
            self.websocket = await websockets.connect(
                self.ws_url, extra_headers=headers
            )

    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def chat(
        self,
        msg: Optional[str] = None,
        image: Optional[str | Image.Image] = None,
        prompt: Optional[Prompt] = None,
        batch: Optional[List[Prompt]] = None,
        sampling_params: Optional[SamplingParams] = None,
        stream_tokens: bool = False,
        adapter: Optional[str] = None,
    ) -> AsyncIterator[ChatResponse | TokenResponse]:
        await self.connect()

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
        await self.websocket.send(request.model_dump_json())

        # Yield responses as they arrive
        try:
            while True:
                response = await self.websocket.recv()
                response_data = json.loads(response)

                if response_data.get("type") == TokenResponse.__name__:
                    resp = TokenResponse.model_validate(response_data)
                    yield resp
                    all_done = all(
                        choice.finish_reason == "stop" for choice in resp.choices
                    )
                    if all_done:
                        print("stream complete", flush=True)
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

        except websockets.exceptions.ConnectionClosed:
            await self.close()
            raise ConnectionError("WebSocket connection closed unexpectedly")
