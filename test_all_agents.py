"""
Test chat with agents to identify which ones work.
"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

PROJECT_ENDPOINT = "https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec"

async def test_all_agents():
    async with AzureCliCredential() as credential:
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential,
        )
        async with client:
            openai_client = client.get_openai_client()
            
            # List all agents
            agents = [a async for a in client.agents.list()]
            
            print(f"Total agents: {len(agents)}\n")
            
            for agent in agents:
                agent_name = agent.name
                version = "1"
                has_tools = False
                tool_types = []
                
                if hasattr(agent, 'versions') and agent.versions:
                    if hasattr(agent.versions, 'latest') and agent.versions.latest:
                        if hasattr(agent.versions.latest, 'version'):
                            version = str(agent.versions.latest.version)
                        if hasattr(agent.versions.latest, 'definition'):
                            definition = agent.versions.latest.definition
                            if isinstance(definition, dict) and 'tools' in definition:
                                tools = definition['tools']
                                if tools and len(tools) > 0:
                                    has_tools = True
                                    tool_types = [t.get('type', 'unknown') for t in tools]
                
                status = "Testing..."
                print(f"Agent: {agent_name} (v{version}) - Tools: {tool_types if has_tools else 'None'}")
                
                try:
                    response = await openai_client.responses.create(
                        input="Hola",
                        extra_body={
                            "agent": {
                                "type": "agent_reference",
                                "name": agent_name,
                                "version": version
                            }
                        }
                    )
                    print(f"  ✅ Works!")
                except Exception as e:
                    error_msg = str(e)
                    if "500" in error_msg:
                        print(f"  ❌ Error 500 (server error)")
                    else:
                        print(f"  ❌ Error: {error_msg[:100]}")
                
                print()

asyncio.run(test_all_agents())
