import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

load_dotenv()
endpoint = os.getenv('AZURE_AI_PROJECT_ENDPOINT')

async def main():
    async with AzureCliCredential() as cred:
        client = AIProjectClient(endpoint=endpoint, credential=cred)
        async with client:
            print("=== Agents ===")
            async for agent in client.agents.list():
                print(f"Name: {agent.name}")
                print(f"  ID: {agent.id}")
                if hasattr(agent, 'versions') and agent.versions:
                    print(f"  Versions: {agent.versions}")
                    if hasattr(agent.versions, 'latest'):
                        latest = agent.versions.latest
                        print(f"  Latest Version: {latest}")
                        if hasattr(latest, 'version'):
                            print(f"    Version Number: {latest.version}")
                        if hasattr(latest, 'definition'):
                            print(f"    Definition: {latest.definition}")
                print()

asyncio.run(main())
