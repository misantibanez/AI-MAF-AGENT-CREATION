"""Check MicrosoftLearn5 connection details"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

PROJECT_ENDPOINT = "https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec"

async def check():
    async with AzureCliCredential() as cred:
        client = AIProjectClient(PROJECT_ENDPOINT, cred)
        async with client:
            print("=== Connections with 'Learn' ===")
            async for conn in client.connections.list():
                if 'Learn' in conn.name:
                    print(f"Name: {conn.name}")
                    print(f"ID: {conn.id}")
                    print(f"Type: {getattr(conn, 'type', 'N/A')}")
                    print(f"Target: {getattr(conn, 'target', 'N/A')}")
                    # Print all attributes
                    for attr in dir(conn):
                        if not attr.startswith('_'):
                            val = getattr(conn, attr, None)
                            if not callable(val):
                                print(f"  {attr}: {val}")
                    print()

asyncio.run(check())
