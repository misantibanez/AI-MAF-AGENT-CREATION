"""Debug definition structure"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

async def test():
    async with AzureCliCredential() as cred:
        client = AIProjectClient("https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec", cred)
        async with client:
            async for agent in client.agents.list():
                if agent.name == "FavoritePaymentsAgent":
                    latest = agent.versions.latest
                    definition = latest.definition
                    print(f"Type: {type(definition)}")
                    print(f"Is dict: {isinstance(definition, dict)}")
                    if isinstance(definition, dict):
                        print(f"Tools: {definition.get('tools')}")
                    else:
                        print(f"Repr: {repr(definition)}")
                        # Try to access as object
                        if hasattr(definition, 'tools'):
                            print(f"Tools attr: {definition.tools}")
                    break

asyncio.run(test())
