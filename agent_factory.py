"""
Agent Factory - Creates agents dynamically based on user specifications.
Uses the joke_agent as a template pattern.
"""

import uuid
from dataclasses import dataclass
from typing import Optional, AsyncIterator
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient
from agent_framework import Agent
from agent_framework.azure import AzureAIClient


@dataclass
class AgentConfig:
    """Configuration for a custom agent."""
    id: str
    name: str
    description: str
    instructions: str
    created_at: str


@dataclass 
class FoundryAgent:
    """Agent from Azure AI Foundry."""
    id: str
    name: str
    description: str
    model: str
    created_at: str
    has_tools: bool = False
    tool_types: list = None  # List of tool type strings like ['mcp', 'code_interpreter']


@dataclass
class FoundryTool:
    """Tool/Connection from Azure AI Foundry."""
    id: str
    name: str
    target: str
    tool_type: str


def generate_agent_instructions(
    agent_purpose: str,
    agent_personality: str = "profesional y amigable",
    agent_capabilities: Optional[list[str]] = None,
    agent_rules: Optional[list[str]] = None,
) -> str:
    """Generate agent instructions based on user input."""
    
    capabilities_text = ""
    if agent_capabilities:
        capabilities_text = "\n".join(f"- {cap}" for cap in agent_capabilities)
    else:
        capabilities_text = "- Responder preguntas de manera clara y concisa\n- Ayudar al usuario con sus consultas"
    
    rules_text = ""
    if agent_rules:
        rules_text = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(agent_rules))
    else:
        rules_text = """1. Siempre mantén un tono profesional y respetuoso
2. Si no sabes algo, admítelo honestamente
3. Sé conciso pero completo en tus respuestas
4. Usa emojis cuando sea apropiado para hacer la conversación más amena"""
    
    instructions = f"""Eres un asistente especializado con el siguiente propósito:

PROPÓSITO PRINCIPAL:
{agent_purpose}

PERSONALIDAD:
{agent_personality}

CAPACIDADES:
{capabilities_text}

REGLAS DE COMPORTAMIENTO:
{rules_text}

FORMATO DE RESPUESTA:
- Responde de manera clara y estructurada
- Usa viñetas o numeración cuando sea apropiado
- Incluye ejemplos cuando ayuden a clarificar
"""
    return instructions


class AgentFactory:
    """Factory class to create and manage dynamic agents."""
    
    def __init__(self, project_endpoint: str, model_deployment: str):
        self.project_endpoint = project_endpoint
        self.model_deployment = model_deployment
        self.agents: dict[str, AgentConfig] = {}
    
    def create_agent_config(
        self,
        name: str,
        description: str,
        purpose: str,
        personality: str = "profesional y amigable",
        capabilities: Optional[list[str]] = None,
        rules: Optional[list[str]] = None,
    ) -> AgentConfig:
        """Create a new agent configuration."""
        from datetime import datetime
        
        agent_id = str(uuid.uuid4())[:8]
        instructions = generate_agent_instructions(
            agent_purpose=purpose,
            agent_personality=personality,
            agent_capabilities=capabilities,
            agent_rules=rules,
        )
        
        config = AgentConfig(
            id=agent_id,
            name=name,
            description=description,
            instructions=instructions,
            created_at=datetime.now().isoformat(),
        )
        
        self.agents[agent_id] = config
        return config
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Get an agent configuration by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> list[AgentConfig]:
        """List all created agents."""
        return list(self.agents.values())
    
    async def list_foundry_agents(self) -> list[FoundryAgent]:
        """List all agents from Azure AI Foundry."""
        from datetime import datetime
        
        agents = []
        async with AzureCliCredential() as credential:
            client = AIProjectClient(
                endpoint=self.project_endpoint,
                credential=credential,
            )
            async with client:
                async for agent in client.agents.list():
                    # AgentDetails has: id, name, versions
                    # Get latest version info if available
                    model = ""
                    description = ""
                    created_at = ""
                    has_tools = False
                    tool_types = []
                    
                    if hasattr(agent, 'versions') and agent.versions:
                        latest = agent.versions.latest if hasattr(agent.versions, 'latest') else None
                        if latest:
                            # Get model and tools from definition
                            definition = getattr(latest, 'definition', None)
                            if definition:
                                # definition can be PromptAgentDefinition object or dict
                                if isinstance(definition, dict):
                                    model = definition.get('model', '') or ''
                                    tools = definition.get('tools', [])
                                else:
                                    # It's an object like PromptAgentDefinition
                                    model = getattr(definition, 'model', '') or ''
                                    tools = getattr(definition, 'tools', []) or []
                                
                                # Process tools (can be list of dicts or objects)
                                if tools and len(tools) > 0:
                                    has_tools = True
                                    for t in tools:
                                        if isinstance(t, dict):
                                            tool_types.append(t.get('type', 'unknown'))
                                        else:
                                            tool_types.append(getattr(t, 'type', 'unknown'))
                                    
                            description = getattr(latest, 'description', "") or ""
                            created_at = str(getattr(latest, 'created_at', "")) if hasattr(latest, 'created_at') else ""
                    
                    agents.append(FoundryAgent(
                        id=agent.id,
                        name=agent.name or "Sin nombre",
                        description=description,
                        model=model,
                        created_at=created_at,
                        has_tools=has_tools,
                        tool_types=tool_types if tool_types else None,
                    ))
        
        return agents
    
    async def list_foundry_tools(self) -> list[FoundryTool]:
        """List all MCP tools (REMOTE_TOOL connections) from Azure AI Foundry."""
        
        tools = []
        async with AzureCliCredential() as credential:
            client = AIProjectClient(
                endpoint=self.project_endpoint,
                credential=credential,
            )
            async with client:
                async for conn in client.connections.list():
                    conn_type = str(getattr(conn, 'type', ''))
                    # Filter only REMOTE_TOOL type (MCP servers)
                    if 'REMOTE_TOOL' in conn_type:
                        tools.append(FoundryTool(
                            id=conn.id,
                            name=conn.name,
                            target=getattr(conn, 'target', '') or '',
                            tool_type='mcp',
                        ))
        
        return tools
    
    def _sanitize_agent_name(self, name: str) -> str:
        """Sanitize agent name to meet Azure requirements.
        
        Must start and end with alphanumeric characters,
        can contain hyphens in the middle, max 63 characters.
        """
        import re
        # Replace spaces and invalid chars with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9-]', '-', name)
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        # Truncate to 63 chars
        sanitized = sanitized[:63]
        # Ensure it ends with alphanumeric
        sanitized = sanitized.rstrip('-')
        # If empty, use default
        if not sanitized:
            sanitized = "agent"
        return sanitized
    
    async def create_foundry_agent(
        self,
        name: str,
        instructions: str,
        model: str,
        tool_names: Optional[list[str]] = None,
    ) -> FoundryAgent:
        """Create a new agent in Azure AI Foundry with optional tools.
        
        Args:
            name: Agent name
            instructions: Agent instructions
            model: Model deployment name
            tool_names: List of tool/connection names (not IDs)
        """
        from azure.ai.projects.models import MCPTool, PromptAgentDefinition
        
        # Sanitize the name
        sanitized_name = self._sanitize_agent_name(name)
        
        print(f"🏭 AgentFactory.create_foundry_agent called")
        print(f"   Name: {name} -> {sanitized_name}")
        print(f"   Tool names: {tool_names}")
        
        async with AzureCliCredential() as credential:
            client = AIProjectClient(
                endpoint=self.project_endpoint,
                credential=credential,
            )
            async with client:
                # Build tools list if provided - need to find connection IDs and URLs by name
                tools = []
                if tool_names:
                    print(f"   Processing {len(tool_names)} tools...")
                    # Get all connections to find IDs and target URLs by name
                    connections_map = {}
                    async for conn in client.connections.list():
                        # Store both id and target URL
                        target_url = getattr(conn, 'target', '') or ''
                        connections_map[conn.name] = {
                            'id': conn.id,
                            'url': target_url
                        }
                    print(f"   Available connections: {list(connections_map.keys())}")
                    
                    for tool_name in tool_names:
                        if tool_name in connections_map:
                            conn_info = connections_map[tool_name]
                            tools.append(MCPTool(
                                server_label=tool_name,
                                server_url=conn_info['url'],  # Use actual URL from connection
                                project_connection_id=conn_info['id'],
                                allowed_tools=[],
                                require_approval="never",
                            ))
                        else:
                            print(f"Warning: Tool '{tool_name}' not found in connections")
                
                # Create the agent definition
                definition = PromptAgentDefinition(
                    model=model,
                    instructions=instructions,
                    tools=tools if tools else None,
                )
                
                # Create the agent
                agent = await client.agents.create(
                    name=sanitized_name,
                    definition=definition,
                )
                
                return FoundryAgent(
                    id=agent.id,
                    name=agent.name or sanitized_name,
                    description="",
                    model=model,
                    created_at="",
                )
    
    async def chat_with_foundry_agent(
        self,
        agent_id: str,
        message: str,
        thread_id: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Chat with an agent from Foundry using the new conversations/responses API."""
        
        async with AzureCliCredential() as credential:
            client = AIProjectClient(
                endpoint=self.project_endpoint,
                credential=credential,
            )
            async with client:
                # Get the agent info to get name and version
                agent = await client.agents.get(agent_id)
                agent_name = agent.name
                
                # Get the latest version and check for tools
                agent_version = "1"
                has_mcp_tools = False
                if hasattr(agent, 'versions') and agent.versions:
                    if hasattr(agent.versions, 'latest') and agent.versions.latest:
                        if hasattr(agent.versions.latest, 'version'):
                            agent_version = str(agent.versions.latest.version)
                        # Check if agent has MCP tools
                        definition = getattr(agent.versions.latest, 'definition', None)
                        if definition and isinstance(definition, dict):
                            tools = definition.get('tools', [])
                            if tools:
                                has_mcp_tools = any(t.get('type') == 'mcp' for t in tools if isinstance(t, dict))
                
                # Get OpenAI client for conversations/responses
                openai_client = client.get_openai_client()
                
                try:
                    # Create response using the agent directly with input
                    # Note: Don't pass 'model' when 'agent' is specified
                    response = await openai_client.responses.create(
                        input=[{"role": "user", "content": message}],
                        extra_body={
                            "agent": {
                                "type": "agent_reference", 
                                "name": agent_name, 
                                "version": agent_version
                            }
                        }
                    )
                    
                    # Extract the response text
                    if hasattr(response, 'output') and response.output:
                        for output_item in response.output:
                            if hasattr(output_item, 'content') and output_item.content:
                                for content_part in output_item.content:
                                    if hasattr(content_part, 'text'):
                                        yield content_part.text
                            elif hasattr(output_item, 'type') and output_item.type == 'message':
                                if hasattr(output_item, 'content'):
                                    for content_part in output_item.content:
                                        if hasattr(content_part, 'text'):
                                            yield content_part.text
                except Exception as e:
                    error_msg = str(e)
                    if "500" in error_msg and has_mcp_tools:
                        yield f"⚠️ Error del servidor (500): Este agente tiene MCP tools configuradas. Actualmente hay un problema conocido con la API de Azure AI Foundry al chatear con agentes que tienen MCP tools a través del SDK. Por favor, prueba con este agente directamente en el portal de Azure AI Foundry."
                    else:
                        yield f"Error al chatear con el agente: {error_msg}"
    
    async def chat_with_agent(
        self,
        agent_id: str,
        message: str,
        thread_id: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Chat with a specific agent using streaming."""
        
        config = self.get_agent_config(agent_id)
        if not config:
            yield f"Error: Agente '{agent_id}' no encontrado."
            return
        
        async with (
            AzureCliCredential() as credential,
            Agent(
                client=AzureAIClient(
                    project_endpoint=self.project_endpoint,
                    model_deployment_name=self.model_deployment,
                    credential=credential,
                ),
                name=config.name,
                instructions=config.instructions,
            ) as agent,
        ):
            thread = agent.get_new_thread()
            
            async for chunk in agent.run_stream(message, thread=thread):
                if chunk.text:
                    yield chunk.text
