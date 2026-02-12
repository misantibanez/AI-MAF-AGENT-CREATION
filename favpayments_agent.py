"""
Microsoft Learn Agent - Creates an agent in Azure AI Foundry with MicrosoftLearn5 MCP tool.
Uses Azure AI Agent Service v2 (azure-ai-projects SDK).
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")

# Agent and Tool configuration
AGENT_NAME = "FavoritePayments1234"
MCP_TOOL_NAME = "favorite-payment"


async def get_connection_info(client: AIProjectClient, connection_name: str) -> tuple[str, str] | None:
    """Find connection ID and target URL by name."""
    async for conn in client.connections.list():
        if conn.name == connection_name:
            target = getattr(conn, 'target', '') or ''
            return conn.id, target
    return None


async def main():
    """Create and run the Microsoft Learn agent in Foundry."""
    
    if not PROJECT_ENDPOINT:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT no está configurado")
        return
    
    print(f"🚀 Microsoft Learn Agent - Agent Service v2")
    print(f"📍 Project Endpoint: {PROJECT_ENDPOINT}")
    print(f"🤖 Model: {MODEL_DEPLOYMENT}")
    print(f"🔧 Tool: {MCP_TOOL_NAME}")
    print("-" * 50)
    
    async with AzureCliCredential() as credential:
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential,
        )
        async with client:
            # Get the MCP tool connection ID and URL
            print(f"\n🔍 Buscando connection '{MCP_TOOL_NAME}'...")
            conn_info = await get_connection_info(client, MCP_TOOL_NAME)
            
            if not conn_info:
                print(f"❌ Error: Connection '{MCP_TOOL_NAME}' no encontrada en Foundry")
                print("\nConnections disponibles:")
                async for conn in client.connections.list():
                    print(f"  - {conn.name}")
                return
            
            connection_id, connection_url = conn_info
            print(f"✅ Connection encontrada: {connection_id}")
            print(f"📍 URL: {connection_url}")
            
            # Create the MCP tool with the actual URL
            mcp_tool = MCPTool(
                server_label=MCP_TOOL_NAME,
                server_url=connection_url,  # Use the actual URL from connection
                project_connection_id=connection_id,
                allowed_tools=[],
                require_approval="never",
            )
            
            # Create agent definition
            definition = PromptAgentDefinition(
                model=MODEL_DEPLOYMENT,
                instructions="""Eres un asistente experto en documentación de Microsoft Learn.

PROPÓSITO PRINCIPAL:
Ayudar a los usuarios a encontrar y entender documentación técnica de Microsoft.

CAPACIDADES:
- Buscar documentación en Microsoft Learn usando la tool MicrosoftLearn5
- Explicar conceptos técnicos de Azure, Microsoft 365, y otros productos Microsoft
- Proporcionar ejemplos de código cuando sea relevante

REGLAS:
1. Siempre usa la herramienta MicrosoftLearn5 para buscar información actualizada
2. Proporciona respuestas claras y estructuradas
3. Incluye enlaces a la documentación cuando sea posible
""",
                tools=[mcp_tool],
            )
            
            # Create or get the agent
            print(f"\n📝 Creando agente '{AGENT_NAME}' en Foundry...")
            try:
                agent = await client.agents.create(
                    name=AGENT_NAME,
                    definition=definition,
                )
                print(f"✅ Agente creado: {agent.name} (ID: {agent.id})")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⚠️ El agente ya existe, recuperándolo...")
                    agent = await client.agents.get(AGENT_NAME)
                    print(f"✅ Agente recuperado: {agent.name}")
                else:
                    raise
            
            # Chat with the agent using responses API
            openai_client = client.get_openai_client()
            
            # Get version
            agent_version = "1"
            if hasattr(agent, 'versions') and agent.versions:
                if hasattr(agent.versions, 'latest') and agent.versions.latest:
                    if hasattr(agent.versions.latest, 'version'):
                        agent_version = str(agent.versions.latest.version)
            
            print(f"\n💬 ¡Agente listo! (v{agent_version})")
            print("Escribe tu pregunta (o 'salir' para terminar)")
            print("-" * 50)
            
            while True:
                user_input = input("\n👤 Tú: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("\n👋 ¡Hasta luego!")
                    break
                
                if not user_input:
                    continue
                
                print(f"\n🤖 {AGENT_NAME}: ", end="", flush=True)
                
                try:
                    response = await openai_client.responses.create(
                        input=user_input,
                        extra_body={
                            "agent": {
                                "type": "agent_reference",
                                "name": agent.name,
                                "version": agent_version,
                            }
                        }
                    )
                    
                    # Extract response text
                    if hasattr(response, 'output') and response.output:
                        for output_item in response.output:
                            if hasattr(output_item, 'content') and output_item.content:
                                for content_part in output_item.content:
                                    if hasattr(content_part, 'text'):
                                        print(content_part.text, end="", flush=True)
                    print()
                    
                except Exception as e:
                    print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
