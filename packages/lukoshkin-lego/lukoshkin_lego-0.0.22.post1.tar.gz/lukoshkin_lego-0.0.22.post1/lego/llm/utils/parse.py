"""Functions to retrieve and parse OpenAI's ChatCompletion response."""

import json
from collections import Counter
from typing import AsyncIterator

import json_repair
from openai.types.chat.chat_completion import ChatCompletion

from lego.lego_types import JSONDict
from lego.llm.types import StreamChunk
from lego.logger import logger


def llm_tool_args(response: ChatCompletion) -> str | None:
    """Extract the tool arguments from the response."""
    if tools := response.choices[0].message.tool_calls:
        return tools[0].function.arguments
    return None


def llm_tool_name(response: ChatCompletion) -> str | None:
    """Extract the tool name from the response."""
    if tools := response.choices[0].message.tool_calls:
        return tools[0].function.name
    return None


def llm_tool_name_and_args(
    response: ChatCompletion,
) -> tuple[str | None, str | None]:
    """Extract the tool name from the response."""
    return llm_tool_name(response), llm_tool_args(response)


def llm_msg_content(response: ChatCompletion) -> str:
    """Extract the message content from the response."""
    return response.choices[0].message.content


def llm_stream_chunk_str(chunk: StreamChunk) -> str:
    """Extract the message content from the response."""
    return chunk.choices[0].delta.content or ""


async def llm_stream_content(response: AsyncIterator[StreamChunk]) -> str:
    """Extract the message content from the response."""
    return "".join([llm_stream_chunk_str(chunk) async for chunk in response])


def response_token_counts(response: ChatCompletion) -> Counter[str]:
    """Return the token count of the response (`collections.Counter`)."""
    return Counter(
        {
            "prompt": response.usage.prompt_tokens,
            "completion": response.usage.completion_tokens,
        }
    )


def parse_json(json_like: str) -> JSONDict:
    """Parse a JSON-like string."""
    try:
        return json_repair.loads(json_like)
    except json.JSONDecodeError as exc:
        logger.error(exc)
        logger.error(json_like)
        raise exc
