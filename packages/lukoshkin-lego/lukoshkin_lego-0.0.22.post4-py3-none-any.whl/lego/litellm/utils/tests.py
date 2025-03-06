import pytest

from lego.litellm.utils.utils import (
    build_bedrock_model,
    build_litellm_router,
    build_openai_model,
)
from lego.llm.utils.parse import llm_stream_content


@pytest.fixture
def router_haiku3():
    return build_litellm_router(
        [
            build_bedrock_model(
                "anthropic.claude-3-haiku-20240307-v1:0",
                model_settings={"temperature": 0.2},
                proxy_settings={"num_retries": 2},
            )
        ],
        num_retries=1,
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def router_sonnet37():
    return build_litellm_router(
        [
            build_bedrock_model(
                "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                model_settings={
                    "temperature": 1,
                    "thinking": {
                        "type": "enabled",
                        "budget_tokens": 1024,
                    },
                },
                proxy_settings={"num_retries": 2},
            )
        ],
        num_retries=1,
        set_verbose=True,
        debug_level="DEBUG",
    )


@pytest.fixture
def router_openai():
    return build_litellm_router(
        [build_openai_model("o1-mini")],
        num_retries=1,
        set_verbose=True,
        debug_level="DEBUG",
    )


messages = [
    {
        "role": "user",
        "content": (
            "Where is the beginning of the end"
            " which ends with the beginning?"
        ),
    }
]


@pytest.mark.asyncio
async def test_call(router_haiku3, router_sonnet37, router_openai):
    await router_haiku3(messages=messages, temperature=0)
    await router_openai(messages=messages)
    stream_response = await router_sonnet37(messages=messages, stream=True)
    answer, reasoning = await llm_stream_content(stream_response)
    assert answer
    assert reasoning
