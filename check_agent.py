"""Check specific agent"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

PROJECT_ENDPOINT = "https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec"

async def check():
    async with AzureCliCredential() as cred:
        client = AIProjectClient(PROJECT_ENDPOINT, cred)
        async with client:
            try:
                agent = await client.agents.get('MicrosoftLearnAgent2')
                print(f"Agente encontrado: {agent.name}")
                print(f"ID: {agent.id}")
                if agent.versions and agent.versions.latest:
                    latest = agent.versions.latest
                    print(f"Version: {latest.version}")
                    print(f"Created at: {latest.created_at}")
                    if latest.definition:
                        defn = latest.definition
                        print(f"Model: {getattr(defn, 'model', 'N/A')}")
                        tools = getattr(defn, 'tools', []) or []
                        print(f"Tools count: {len(tools)}")
                        for t in tools:
                            if isinstance(t, dict):
                                print(f"  - type: {t.get('type')}, label: {t.get('server_label')}, url: {t.get('server_url')}")
                            else:
                                print(f"  - {t}")
            except Exception as e:
                print(f"Error: {e}")

asyncio.run(check())
