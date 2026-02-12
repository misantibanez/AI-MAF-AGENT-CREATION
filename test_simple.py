"""
Simple test to understand the tool detection issue and find which agents work.
"""
import asyncio
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient

PROJECT_ENDPOINT = "https://aif-vig-tec-demo.services.ai.azure.com/api/projects/proj-aif-vig-tec"

async def simple_test():
    async with AzureCliCredential() as credential:
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential,
        )
        async with client:
            openai_client = client.get_openai_client()
            
            # Only test agents we know: Storyteller (no tools) vs FavoritePaymentsAgent (with tools)
            test_cases = [
                ("Storyteller", "1"),  # No tools - should work
                ("JokeAgent", "1"),    # No tools - should work
                ("FavoritePaymentsAgent", "1"),  # Has MCP tools - error 500
            ]
            
            for agent_name, version in test_cases:
                print(f"\n=== Testing: {agent_name} ===")
                
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
                    # Extract response
                    text = ""
                    if hasattr(response, 'output') and response.output:
                        for output_item in response.output:
                            if hasattr(output_item, 'content'):
                                for content_part in output_item.content:
                                    if hasattr(content_part, 'text'):
                                        text = content_part.text
                    print(f"  ✅ Works! Response: {text[:100]}...")
                except Exception as e:
                    print(f"  ❌ Error: {e}")

asyncio.run(simple_test())
