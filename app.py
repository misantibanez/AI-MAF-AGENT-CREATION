"""
Agent Portal - Web application for creating and chatting with custom AI agents.
"""

import os
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from agent_factory import AgentFactory, FoundryAgent, FoundryTool

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")

# Global agent factory
agent_factory: Optional[AgentFactory] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the agent factory on startup."""
    global agent_factory
    
    if not PROJECT_ENDPOINT:
        raise RuntimeError("AZURE_AI_PROJECT_ENDPOINT no está configurado")
    
    agent_factory = AgentFactory(
        project_endpoint=PROJECT_ENDPOINT,
        model_deployment=MODEL_DEPLOYMENT,
    )
    print("🚀 Agent Factory inicializado")
    yield
    print("👋 Cerrando Agent Portal")


app = FastAPI(
    title="Agent Portal",
    description="Portal para crear y chatear con agentes de IA personalizados",
    version="1.0.0",
    lifespan=lifespan,
)


# ============== Pydantic Models ==============

class CreateAgentRequest(BaseModel):
    """Request model for creating a new agent."""
    name: str
    description: str
    purpose: str
    personality: str = "profesional y amigable"
    capabilities: Optional[list[str]] = None
    rules: Optional[list[str]] = None
    tool_names: Optional[list[str]] = None  # Selected tool names


class ChatRequest(BaseModel):
    """Request model for chatting with an agent."""
    message: str
    thread_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Response model for agent information."""
    id: str
    name: str
    description: str
    created_at: str


class ToolResponse(BaseModel):
    """Response model for tool information."""
    id: str
    name: str
    target: str
    tool_type: str


class FoundryAgentResponse(BaseModel):
    """Response model for Foundry agent information."""
    id: str
    name: str
    description: str
    model: str
    created_at: str
    source: str = "foundry"
    has_tools: bool = False
    tool_types: Optional[list[str]] = None


# ============== API Endpoints ==============

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main portal page."""
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Agent Portal - Crea tu Agente de IA</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e4e4e4;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 40px 0;
        }
        
        header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        header p {
            color: #a0a0a0;
            font-size: 1.1rem;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        
        @media (max-width: 900px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .card h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #00d4ff;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: #fff;
            font-size: 1rem;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #00d4ff;
            box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
        }
        
        .form-group textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .form-group input::placeholder,
        .form-group textarea::placeholder {
            color: #666;
        }
        
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        .btn-primary {
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .agents-list {
            margin-top: 20px;
        }
        
        .agent-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: background 0.3s, transform 0.2s;
            border: 1px solid transparent;
        }
        
        .agent-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }
        
        .agent-item.active {
            border-color: #00d4ff;
            background: rgba(0, 212, 255, 0.1);
        }
        
        .agent-item h3 {
            font-size: 1.1rem;
            margin-bottom: 5px;
        }
        
        .agent-item p {
            font-size: 0.9rem;
            color: #888;
        }
        
        .chat-section {
            display: none;
        }
        
        .chat-section.active {
            display: block;
        }
        
        .chat-messages {
            height: 300px;
            overflow-y: auto;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .message {
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 85%;
        }
        
        .message.user {
            background: linear-gradient(90deg, #7c3aed, #00d4ff);
            margin-left: auto;
            text-align: right;
        }
        
        .message.agent {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .message .sender {
            font-size: 0.8rem;
            color: #aaa;
            margin-bottom: 5px;
        }
        
        .chat-input {
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 14px 16px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: #fff;
            font-size: 1rem;
        }
        
        .chat-input button {
            padding: 14px 24px;
        }
        
        .status {
            padding: 12px 16px;
            border-radius: 8px;
            margin-top: 15px;
            display: none;
        }
        
        .status.success {
            display: block;
            background: rgba(0, 200, 100, 0.2);
            border: 1px solid rgba(0, 200, 100, 0.5);
            color: #00c864;
        }
        
        .status.error {
            display: block;
            background: rgba(255, 50, 50, 0.2);
            border: 1px solid rgba(255, 50, 50, 0.5);
            color: #ff5050;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .empty-state span {
            font-size: 3rem;
            display: block;
            margin-bottom: 10px;
        }
        
        .tools-list {
            max-height: 200px;
            overflow-y: auto;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }
        
        .tool-item {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin-bottom: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .tool-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .tool-item input[type="checkbox"] {
            margin-right: 10px;
            width: 18px;
            height: 18px;
            accent-color: #00d4ff;
        }
        
        .tool-item label {
            flex: 1;
            cursor: pointer;
        }
        
        .tool-item .tool-name {
            font-weight: 500;
            color: #fff;
        }
        
        .tool-item .tool-target {
            font-size: 0.75rem;
            color: #666;
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Agent Portal</h1>
            <p>Crea agentes de IA personalizados en Microsoft Foundry</p>
        </header>
        
        <div class="main-content">
            <!-- Left Panel: Create Agent -->
            <div class="card">
                <h2>✨ Crear Nuevo Agente</h2>
                <form id="createAgentForm">
                    <div class="form-group">
                        <label for="agentName">Nombre del Agente</label>
                        <input type="text" id="agentName" placeholder="Ej: Asistente de Ventas" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="agentDescription">Descripción Breve</label>
                        <input type="text" id="agentDescription" placeholder="Ej: Ayuda a los clientes con consultas de productos" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="agentPurpose">¿Qué quieres que haga el agente?</label>
                        <textarea id="agentPurpose" placeholder="Describe en detalle las tareas y funciones que debe realizar el agente..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="agentPersonality">Personalidad</label>
                        <input type="text" id="agentPersonality" placeholder="Ej: Amigable, profesional, con sentido del humor" value="profesional y amigable">
                    </div>
                    
                    <div class="form-group">
                        <label>🔧 Tools Disponibles (MCP)</label>
                        <div id="toolsList" class="tools-list">
                            <p style="color: #666; font-size: 0.9rem;">Cargando tools...</p>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" id="createBtn">
                        🚀 Crear Agente en Foundry
                    </button>
                </form>
                
                <div id="createStatus" class="status"></div>
            </div>
            
            <!-- Right Panel: Agents List & Chat -->
            <div class="card">
                <div id="agentsListSection">
                    <h2>📋 Mis Agentes</h2>
                    <div id="agentsList" class="agents-list">
                        <div class="empty-state">
                            <span>🤖</span>
                            <p>No hay agentes creados aún</p>
                            <p>¡Crea tu primer agente!</p>
                        </div>
                    </div>
                </div>
                
                <div id="chatSection" class="chat-section">
                    <h2>💬 Chat con <span id="chatAgentName"></span></h2>
                    <button class="btn btn-secondary" onclick="showAgentsList()" style="margin-bottom: 15px; width: auto; padding: 8px 16px;">
                        ← Volver a la lista
                    </button>
                    
                    <div id="chatMessages" class="chat-messages"></div>
                    
                    <div class="chat-input">
                        <input type="text" id="messageInput" placeholder="Escribe tu mensaje..." onkeypress="handleKeyPress(event)">
                        <button class="btn btn-primary" onclick="sendMessage()" id="sendBtn">Enviar</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentAgentId = null;
        let agents = [];
        let tools = [];
        
        // Load agents and tools on page load
        document.addEventListener('DOMContentLoaded', () => {
            loadAgents();
            loadTools();
        });
        
        // Load available tools
        async function loadTools() {
            try {
                const response = await fetch('/api/tools');
                tools = await response.json();
                renderToolsList();
            } catch (error) {
                console.error('Error loading tools:', error);
                document.getElementById('toolsList').innerHTML = 
                    '<p style="color: #ff5050;">Error cargando tools</p>';
            }
        }
        
        // Render tools list with checkboxes
        function renderToolsList() {
            const container = document.getElementById('toolsList');
            
            if (tools.length === 0) {
                container.innerHTML = '<p style="color: #666;">No hay tools disponibles</p>';
                return;
            }
            
            container.innerHTML = tools.map(tool => `
                <div class="tool-item">
                    <input type="checkbox" id="tool-${tool.name}" value="${tool.name}" name="tools">
                    <label for="tool-${tool.name}">
                        <div class="tool-name">🔧 ${tool.name}</div>
                        <div class="tool-target">${tool.target}</div>
                    </label>
                </div>
            `).join('');
        }
        
        // Get selected tool names
        function getSelectedTools() {
            const checkboxes = document.querySelectorAll('input[name="tools"]:checked');
            return Array.from(checkboxes).map(cb => cb.value);
        }
        
        // Create Agent Form Handler
        document.getElementById('createAgentForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('createBtn');
            const status = document.getElementById('createStatus');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Creando...';
            status.className = 'status';
            status.style.display = 'none';
            
            const selectedTools = getSelectedTools();
            
            const data = {
                name: document.getElementById('agentName').value,
                description: document.getElementById('agentDescription').value,
                purpose: document.getElementById('agentPurpose').value,
                personality: document.getElementById('agentPersonality').value,
                tool_names: selectedTools.length > 0 ? selectedTools : null,
            };
            
            try {
                const response = await fetch('/api/agents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
                
                if (!response.ok) throw new Error('Error al crear el agente');
                
                const agent = await response.json();
                
                const toolsMsg = selectedTools.length > 0 
                    ? ` con ${selectedTools.length} tool(s)` 
                    : '';
                status.className = 'status success';
                status.innerHTML = `✅ Agente "${agent.name}" creado exitosamente${toolsMsg}!`;
                
                // Clear form
                document.getElementById('createAgentForm').reset();
                document.getElementById('agentPersonality').value = 'profesional y amigable';
                
                // Uncheck all tools
                document.querySelectorAll('input[name="tools"]').forEach(cb => cb.checked = false);
                
                // Reload agents list
                loadAgents();
                
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = `❌ Error: ${error.message}`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '🚀 Crear Agente en Foundry';
            }
        });
        
        // Load agents from API
        async function loadAgents() {
            try {
                const response = await fetch('/api/agents');
                agents = await response.json();
                renderAgentsList();
            } catch (error) {
                console.error('Error loading agents:', error);
            }
        }
        
        // Render agents list
        function renderAgentsList() {
            const container = document.getElementById('agentsList');
            
            if (agents.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <span>🤖</span>
                        <p>No hay agentes creados aún</p>
                        <p>¡Crea tu primer agente!</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = agents.map(agent => {
                // Build tools badge HTML
                let toolsBadge = '';
                if (agent.has_tools && agent.tool_types && agent.tool_types.length > 0) {
                    const toolsText = agent.tool_types.join(', ');
                    toolsBadge = `
                        <p style="font-size: 0.75rem; margin-top: 3px;">
                            <span style="background: #ff6b35; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem;">
                                🔧 Tools: ${toolsText}
                            </span>
                        </p>
                    `;
                }
                
                return `
                    <div class="agent-item" onclick="selectAgent('${agent.id}')">
                        <h3>🤖 ${agent.name}</h3>
                        <p>${agent.description || 'Sin descripción'}</p>
                        <p style="font-size: 0.8rem; color: #00d4ff; margin-top: 5px;">
                            📦 ${agent.model || 'N/A'}
                        </p>
                        ${toolsBadge}
                        <p style="font-size: 0.75rem; color: #666; margin-top: 3px;">
                            🏷️ ${agent.id.substring(0, 20)}...
                        </p>
                    </div>
                `;
            }).join('');
        }
        
        // Select an agent to chat with
        function selectAgent(agentId) {
            currentAgentId = agentId;
            const agent = agents.find(a => a.id === agentId);
            
            // Build warning message if agent has MCP tools
            let warningMsg = '';
            if (agent.has_tools && agent.tool_types && agent.tool_types.includes('mcp')) {
                warningMsg = `
                    <div class="message agent" style="background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%);">
                        <div class="sender">⚠️ Aviso</div>
                        <div>Este agente tiene MCP tools configuradas. Actualmente hay un problema conocido con la API de Azure que puede causar errores al chatear. Si experimentas problemas, prueba el agente directamente en el portal de Azure AI Foundry.</div>
                    </div>
                `;
            }
            
            document.getElementById('chatAgentName').textContent = agent.name;
            document.getElementById('chatMessages').innerHTML = `
                <div class="message agent">
                    <div class="sender">🤖 ${agent.name}</div>
                    <div>¡Hola! Soy ${agent.name}. ${agent.description}. ¿En qué puedo ayudarte?</div>
                </div>
                ${warningMsg}
            `;
            
            document.getElementById('agentsListSection').style.display = 'none';
            document.getElementById('chatSection').classList.add('active');
            document.getElementById('messageInput').focus();
        }
        
        // Show agents list
        function showAgentsList() {
            currentAgentId = null;
            document.getElementById('agentsListSection').style.display = 'block';
            document.getElementById('chatSection').classList.remove('active');
        }
        
        // Handle Enter key in chat input
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        // Send message to agent
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || !currentAgentId) return;
            
            const messagesContainer = document.getElementById('chatMessages');
            const sendBtn = document.getElementById('sendBtn');
            
            // Add user message
            messagesContainer.innerHTML += `
                <div class="message user">
                    <div class="sender">👤 Tú</div>
                    <div>${message}</div>
                </div>
            `;
            
            input.value = '';
            sendBtn.disabled = true;
            
            // Add agent thinking message
            const agentMsgId = 'agent-msg-' + Date.now();
            const agent = agents.find(a => a.id === currentAgentId);
            messagesContainer.innerHTML += `
                <div class="message agent" id="${agentMsgId}">
                    <div class="sender">🤖 ${agent.name}</div>
                    <div class="content"><span class="loading"></span> Pensando...</div>
                </div>
            `;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            try {
                const response = await fetch(`/api/agents/${currentAgentId}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message }),
                });
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullResponse = '';
                
                const msgElement = document.getElementById(agentMsgId);
                const contentElement = msgElement.querySelector('.content');
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    fullResponse += chunk;
                    contentElement.textContent = fullResponse;
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
                
            } catch (error) {
                const msgElement = document.getElementById(agentMsgId);
                msgElement.querySelector('.content').textContent = '❌ Error al obtener respuesta';
            } finally {
                sendBtn.disabled = false;
                input.focus();
            }
        }
    </script>
</body>
</html>
"""


@app.post("/api/agents", response_model=FoundryAgentResponse)
async def create_agent(request: CreateAgentRequest):
    """Create a new agent in Azure AI Foundry with optional tools."""
    if not agent_factory:
        raise HTTPException(status_code=500, detail="Agent factory not initialized")
    
    from agent_factory import generate_agent_instructions
    
    # Debug: Log received tool_names
    print(f"📝 Creating agent: {request.name}")
    print(f"🔧 Tool names received: {request.tool_names}")
    
    # Generate instructions from the request
    instructions = generate_agent_instructions(
        agent_purpose=request.purpose,
        agent_personality=request.personality,
        agent_capabilities=request.capabilities,
        agent_rules=request.rules,
    )
    
    try:
        # Create agent in Foundry with tools
        agent = await agent_factory.create_foundry_agent(
            name=request.name,
            instructions=instructions,
            model=agent_factory.model_deployment,
            tool_names=request.tool_names,
        )
        
        return FoundryAgentResponse(
            id=agent.id,
            name=agent.name,
            description=request.description,
            model=agent.model,
            created_at=agent.created_at,
            source="foundry",
        )
    except Exception as e:
        print(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")


@app.get("/api/tools", response_model=list[ToolResponse])
async def list_tools():
    """List all available MCP tools from Azure AI Foundry."""
    if not agent_factory:
        raise HTTPException(status_code=500, detail="Agent factory not initialized")
    
    try:
        tools = await agent_factory.list_foundry_tools()
        return [
            ToolResponse(
                id=tool.id,
                name=tool.name,
                target=tool.target,
                tool_type=tool.tool_type,
            )
            for tool in tools
        ]
    except Exception as e:
        print(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")


@app.get("/api/agents", response_model=list[FoundryAgentResponse])
async def list_agents():
    """List all agents from Azure AI Foundry."""
    if not agent_factory:
        raise HTTPException(status_code=500, detail="Agent factory not initialized")
    
    try:
        foundry_agents = await agent_factory.list_foundry_agents()
        return [
            FoundryAgentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                model=agent.model,
                created_at=agent.created_at,
                source="foundry",
                has_tools=agent.has_tools,
                tool_types=agent.tool_types,
            )
            for agent in foundry_agents
        ]
    except Exception as e:
        print(f"Error listing Foundry agents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")


@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID."""
    if not agent_factory:
        raise HTTPException(status_code=500, detail="Agent factory not initialized")
    
    config = agent_factory.get_agent_config(agent_id)
    if not config:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        id=config.id,
        name=config.name,
        description=config.description,
        created_at=config.created_at,
    )


@app.post("/api/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """Chat with an agent using streaming response."""
    if not agent_factory:
        raise HTTPException(status_code=500, detail="Agent factory not initialized")
    
    async def generate():
        async for chunk in agent_factory.chat_with_foundry_agent(
            agent_id=agent_id,
            message=request.message,
            thread_id=request.thread_id,
        ):
            yield chunk
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
