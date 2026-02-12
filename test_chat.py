"""
Test chat with a Foundry agent using the new API.
"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient
import json

PROJECT_ENDPOINT = "https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec"

async def test_chat():
    async with AzureCliCredential() as credential:
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential,
        )
        async with client:
            # First, list agents to get one to test
            print("=== Getting Agent ===")
            agents = [a async for a in client.agents.list()]
            
            # Use a simple agent (Storyteller has no tools - simpler test)
            test_agent_name = "Storyteller"
            agent = await client.agents.get(test_agent_name)
            print(f"Agent: {agent.name}")
            print(f"ID: {agent.id}")
            
            # Get version
            version = "1"
            if hasattr(agent, 'versions') and agent.versions:
                if hasattr(agent.versions, 'latest') and agent.versions.latest:
                    if hasattr(agent.versions.latest, 'version'):
                        version = str(agent.versions.latest.version)
            print(f"Version: {version}")
            
            # Get OpenAI client
            openai_client = client.get_openai_client()
            print(f"\n=== OpenAI Client Type: {type(openai_client)} ===")
            
            # List available attributes
            print("\n=== Available attributes on openai_client ===")
            for attr in dir(openai_client):
                if not attr.startswith('_'):
                    print(f"  - {attr}")
            
            # Try different approaches
            print("\n=== Attempting chat ===")
            
            # Approach 1: Using conversations API
            try:
                print("\n--- Trying conversations.create ---")
                conversation = await openai_client.conversations.create()
                print(f"Conversation created: {conversation}")
                print(f"Conversation ID: {conversation.id if hasattr(conversation, 'id') else 'N/A'}")
                
                # Now try responses
                print("\n--- Trying responses.create with conversation ---")
                response = await openai_client.responses.create(
                    conversation=conversation.id,
                    input="Cuéntame una historia corta",
                    extra_body={
                        "agent": {
                            "type": "agent_reference",
                            "name": agent.name,
                            "version": version
                        }
                    }
                )
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error with conversations: {e}")
            
            # Approach 2: Direct responses without conversation
            try:
                print("\n--- Trying responses.create without conversation ---")
                response = await openai_client.responses.create(
                    input="Cuéntame una historia corta",
                    extra_body={
                        "agent": {
                            "type": "agent_reference",
                            "name": agent.name,
                            "version": version
                        }
                    }
                )
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error without conversation: {e}")
            
            # Approach 3: Try with list input
            try:
                print("\n--- Trying responses.create with list input ---")
                response = await openai_client.responses.create(
                    input=[{"role": "user", "content": "Cuéntame una historia corta"}],
                    extra_body={
                        "agent": {
                            "type": "agent_reference",
                            "name": agent.name,
                            "version": version
                        }
                    }
                )
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error with list input: {e}")

asyncio.run(test_chat())
