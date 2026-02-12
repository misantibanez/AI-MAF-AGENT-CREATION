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
            print("=== MCP Tools (REMOTE_TOOL connections) ===")
            async for conn in client.connections.list():
                conn_type = str(getattr(conn, 'type', 'N/A'))
                # Filter only REMOTE_TOOL type (MCP servers)
                if 'REMOTE_TOOL' in conn_type:
                    print(f"Name: {conn.name}")
                    print(f"  ID: {conn.id}")
                    print(f"  Target: {getattr(conn, 'target', 'N/A')}")
                    print()

asyncio.run(main())
