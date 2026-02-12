# 🎭 Agente Contador de Chistes

Un agente de IA que cuenta chistes usando **Microsoft Agent Framework (MAF)** con **Microsoft Foundry**.

## 📋 Requisitos

- Python 3.10+
- Cuenta de Azure con acceso a Microsoft Foundry
- Modelo desplegado en Microsoft Foundry (ej: gpt-4o)

## 🚀 Instalación

1. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   ```bash
   copy .env.example .env
   ```
   
   Edita el archivo `.env` con tus credenciales de Microsoft Foundry:
   ```
   AZURE_AI_PROJECT_ENDPOINT=https://<tu-proyecto>.services.ai.azure.com/api/projects/<nombre-proyecto>
   AZURE_AI_MODEL_DEPLOYMENT=gpt-4o
   ```

## 🎮 Uso

### Modo Interactivo
```bash
python joke_agent.py
```

El agente iniciará una conversación donde puedes:
- Pedir diferentes tipos de chistes
- Especificar categorías (programadores, animales, etc.)
- Mantener una conversación continua
- Escribir "salir" para terminar

### Ejemplo de conversación:
```
🎭 ¡Bienvenido al Agente Contador de Chistes!
==================================================
🤖 Agente: ¡Hola! Soy tu comediante personal 🎭 ¿Listo para reír?

👤 Tú: cuéntame un chiste de programadores
🤖 Agente: ¿Por qué los programadores confunden Halloween con Navidad? 
          Porque Oct 31 = Dec 25 🎃🎄

👤 Tú: otro!
🤖 Agente: ¿Cuántos programadores se necesitan para cambiar una bombilla?
          Ninguno, ¡es un problema de hardware! 💡😄
```

## 📁 Estructura del Proyecto

```
aif-maf-agent-creation/
├── joke_agent.py      # Agente principal
├── requirements.txt   # Dependencias
├── .env.example       # Plantilla de configuración
├── .env               # Configuración (crear desde .env.example)
└── README.md          # Este archivo
```

## 🔧 Librerías Utilizadas

| Librería | Versión | Descripción |
|----------|---------|-------------|
| `azure-ai-projects` | >=2.0.0b2 | Cliente Azure AI Projects |
| `agent-framework` | 1.0.0b251120 | Microsoft Agent Framework Core |
| `agent-framework-azure-ai` | 1.0.0b251120 | Integración MAF con Azure AI |
| `azure-identity` | latest | Autenticación Azure |

## 🔐 Autenticación

El agente usa `DefaultAzureCredential` que soporta:
- Azure CLI (`az login`)
- Variables de entorno
- Managed Identity
- Visual Studio Code

Asegúrate de estar autenticado:
```bash
az login
```

## 📝 Personalización

Puedes modificar el comportamiento del agente editando `JOKE_AGENT_INSTRUCTIONS` en `joke_agent.py`:
- Cambiar el estilo de humor
- Agregar nuevas categorías
- Modificar el idioma predeterminado
- Ajustar la personalidad
