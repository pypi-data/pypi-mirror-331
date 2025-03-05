#!/usr/bin/env python3
#
# To run this, use:
#   uv run readme-example.py
#
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "azure-switchboard",
# ]
# ///

import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4

from azure_switchboard import Deployment, Switchboard

# Define deployments
deployments = [
    Deployment(
        name="d1",
        api_base="https://your-deployment1.openai.azure.com/",
        api_key="your-api-key",
        # optionally specify ratelimits
        rpm_ratelimit=60,
        tpm_ratelimit=100000,
    ),
    Deployment(
        name="d2",
        api_base="https://your-deployment2.openai.azure.com/",
        api_key="your-api-key2",
        rpm_ratelimit=60,
        tpm_ratelimit=100000,
    ),
    Deployment(
        name="d3",
        api_base="https://your-deployment3.openai.azure.com/",
        api_key="your-api-key3",
        rpm_ratelimit=60,
        tpm_ratelimit=100000,
    ),
]

@asynccontextmanager
async def init_switchboard():
    """Wrap client initialization in a context manager for automatic cleanup.

    Analogous to FastAPI dependency injection.
    """

    # Create Switchboard with deployments
    switchboard = Switchboard(deployments)

    # Start background tasks
    # (healthchecks, ratelimiting)
    switchboard.start()

    try:
        yield switchboard
    finally:
        await switchboard.stop()

async def basic_functionality(switchboard: Switchboard):
    # Make a completion request (non-streaming)
    response = await switchboard.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, world!"}]
        )

    print(response.choices[0].message.content)

    # Make a streaming completion request
    stream = await switchboard.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, world!"}],
        stream=True
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print()

async def session_affinity(switchboard: Switchboard):
    session_id = str(uuid4())

    # First message will select a random healthy
    # deployment and associate it with the session_id
    _ = await switchboard.create(
        session_id=session_id,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Who won the World Series in 2020?"}]
    )

    # Follow-up requests with the same session_id will route to the same deployment
    _ = await switchboard.create(
        session_id=session_id,
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Who won the World Series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Who did they beat?"}
        ]
    )

    # If the deployment becomes unhealthy,
    # requests will fall back to a healthy one

    # Simulate a failure by marking down the deployment
    original_client = switchboard.select_deployment(session_id)
    original_client.cooldown()

    # A new deployment will be selected for this session_id
    _ = await switchboard.create(
        session_id=session_id,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Who won the World Series in 2021?"}]
    )

    new_client = switchboard.select_deployment(session_id)
    assert new_client != original_client

async def main():
    async with init_switchboard() as sb:
        print("Basic functionality:")
        await basic_functionality(sb)

        print("Session affinity:")
        await session_affinity(sb)

if __name__ == "__main__":
    asyncio.run(main())
