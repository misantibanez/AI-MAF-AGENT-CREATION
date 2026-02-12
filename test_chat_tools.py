"""
Test chat with a Foundry agent that HAS MCP tools.
"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

PROJECT_ENDPOINT = "https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec"

async def test_chat_with_tools():
    async with AzureCliCredential() as credential:
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential,
        )
        async with client:
            # Test with FavoritePaymentsAgent (has MCP tool)
            test_agent_name = "FavoritePaymentsAgent"
            print(f"=== Testing agent: {test_agent_name} ===")
            
            agent = await client.agents.get(test_agent_name)
            print(f"Agent: {agent.name}")
            
            # Get version
            version = "1"
            if hasattr(agent, 'versions') and agent.versions:
                if hasattr(agent.versions, 'latest') and agent.versions.latest:
                    if hasattr(agent.versions.latest, 'version'):
                        version = str(agent.versions.latest.version)
                    # Also check tools
                    if hasattr(agent.versions.latest, 'definition'):
                        definition = agent.versions.latest.definition
                        print(f"Definition: {definition}")
                        if isinstance(definition, dict) and 'tools' in definition:
                            print(f"Tools: {definition['tools']}")
            
            print(f"Version: {version}")
            
            # Get OpenAI client
            openai_client = client.get_openai_client()
            
            # Try chat - simple message that doesn't require tool usage
            print("\n=== Attempting chat (simple message) ===")
            try:
                response = await openai_client.responses.create(
                    input="Hola, ¿qué puedes hacer?",
                    extra_body={
                        "agent": {
                            "type": "agent_reference",
                            "name": agent.name,
                            "version": version
                        }
                    }
                )
                
                # Extract response text
                if hasattr(response, 'output') and response.output:
                    for output_item in response.output:
                        if hasattr(output_item, 'content') and output_item.content:
                            for content_part in output_item.content:
                                if hasattr(content_part, 'text'):
                                    print(f"Response: {content_part.text[:500]}...")
                else:
                    print(f"Full response: {response}")
                    
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
            
            # Try chat - message that DOES require tool usage
            print("\n=== Attempting chat (tool-required message) ===")
            try:
                response = await openai_client.responses.create(
                    input="¿Cuáles son mis pagos favoritos?",
                    extra_body={
                        "agent": {
                            "type": "agent_reference",
                            "name": agent.name,
                            "version": version
                        }
                    }
                )
                
                # Extract response text
                if hasattr(response, 'output') and response.output:
                    for output_item in response.output:
                        if hasattr(output_item, 'content') and output_item.content:
                            for content_part in output_item.content:
                                if hasattr(content_part, 'text'):
                                    print(f"Response: {content_part.text[:500]}...")
                        elif hasattr(output_item, 'type'):
                            print(f"Output item type: {output_item.type}")
                else:
                    print(f"Full response: {response}")
                    
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

asyncio.run(test_chat_with_tools())
