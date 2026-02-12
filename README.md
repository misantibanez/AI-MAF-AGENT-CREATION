# � Agent Factory

Crea agentes de IA dinámicamente usando **Microsoft Agent Framework (MAF)** con **Azure AI Foundry**.

## 📋 Descripción

`agent_factory.py` es una fábrica de agentes que permite:

- ✅ Crear configuraciones de agentes personalizados
- ✅ Listar agentes existentes en Azure AI Foundry
- ✅ Listar herramientas MCP disponibles
- ✅ Crear nuevos agentes en Azure AI Foundry con herramientas MCP
- ✅ Chatear con agentes usando streaming

## 🚀 Instalación

```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

Crea un archivo `.env`:

```env
AZURE_AI_PROJECT_ENDPOINT=https://<tu-proyecto>.services.ai.azure.com/api/projects/<nombre>
AZURE_AI_MODEL_DEPLOYMENT=gpt-4o
```

Autentícate con Azure CLI:
```bash
az login
```

## 📖 Uso

### Inicializar la fábrica

```python
from agent_factory import AgentFactory

factory = AgentFactory(
    project_endpoint="https://...",
    model_deployment="gpt-4o"
)
```

### Crear un agente local

```python
config = factory.create_agent_config(
    name="AsistenteVentas",
    description="Ayuda con consultas de ventas",
    purpose="Responder preguntas sobre productos y precios",
    personality="amigable y persuasivo",
    capabilities=["Consultar catálogo", "Calcular descuentos"],
    rules=["Siempre ofrecer alternativas", "Ser honesto con disponibilidad"]
)
```

### Listar agentes de Azure AI Foundry

```python
agents = await factory.list_foundry_agents()
for agent in agents:
    print(f"{agent.name} - {agent.model}")
    if agent.has_tools:
        print(f"  Tools: {agent.tool_types}")
```

### Listar herramientas MCP disponibles

```python
tools = await factory.list_foundry_tools()
for tool in tools:
    print(f"{tool.name}: {tool.target}")
```

### Crear agente en Azure AI Foundry con MCP tools

```python
agent = await factory.create_foundry_agent(
    name="MiAgente",
    instructions="Eres un asistente útil...",
    model="gpt-4o",
    tool_names=["MicrosoftLearn5", "favorite-payment"]  # Nombres de conexiones MCP
)
print(f"Agente creado: {agent.id}")
```

### Chatear con un agente

```python
async for chunk in factory.chat_with_foundry_agent(agent_id, "Hola!"):
    print(chunk, end="", flush=True)
```

## 🏗️ Estructura

```
AgentFactory
├── create_agent_config()      # Crear config local
├── get_agent_config()         # Obtener config por ID
├── list_agents()              # Listar configs locales
├── list_foundry_agents()      # Listar agentes de Foundry
├── list_foundry_tools()       # Listar herramientas MCP
├── create_foundry_agent()     # Crear agente en Foundry
├── chat_with_foundry_agent()  # Chat con agente Foundry
└── chat_with_agent()          # Chat con agente local
```

## 📦 Dependencias

| Paquete | Versión |
|---------|---------|
| `agent-framework` | 1.0.0b260210 |
| `agent-framework-azure-ai` | 1.0.0b260210 |
| `azure-ai-projects` | >=2.0.0b2 |
| `azure-identity` | latest |

## 🌐 Portal Web

Ejecuta `app.py` para una interfaz web:

```bash
uvicorn app:app --reload --port 8000
```

Abre http://localhost:8000 para crear y chatear con agentes visualmente.

