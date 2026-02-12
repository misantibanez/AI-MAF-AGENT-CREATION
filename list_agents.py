"""List all agents in Foundry"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

PROJECT_ENDPOINT = "https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec"

async def list_agents():
    async with AzureCliCredential() as cred:
        client = AIProjectClient(PROJECT_ENDPOINT, cred)
        async with client:
            print("=== Agentes en Foundry ===")
            async for agent in client.agents.list():
                print(f"- {agent.name} (ID: {agent.id})")

asyncio.run(list_agents())
