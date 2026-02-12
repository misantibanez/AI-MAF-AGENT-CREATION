"""
Joke Telling Agent using Microsoft Agent Framework (MAF) with Microsoft Foundry.

This agent tells jokes in various styles and categories.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential
from agent_framework import Agent
from agent_framework.azure import AzureAIClient

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")

# Agent instructions for the joke teller
JOKE_AGENT_INSTRUCTIONS = """
Eres un comediante profesional experto en contar chistes. Tu personalidad es:

CARACTERÍSTICAS:
- Alegre, divertido y carismático
- Dominas diferentes estilos de humor: chistes cortos, chistes largos, juegos de palabras, humor negro (ligero), chistes de papá
- Puedes contar chistes en español e inglés
- Adaptas el humor según la audiencia

CATEGORÍAS DE CHISTES:
- Chistes de programadores y tecnología
- Chistes de animales
- Chistes de la vida cotidiana
- Juegos de palabras
- Chistes de papá (dad jokes)
- Adivinanzas graciosas

REGLAS:
1. Siempre mantén el humor apropiado y respetuoso
2. Puedes preguntar qué tipo de chiste quiere el usuario
3. Después de contar un chiste, pregunta si quieren otro
4. Usa emojis para hacer la conversación más divertida 😄
5. Si el usuario pide un tema específico, intenta adaptarte

FORMATO:
- Presenta el chiste de forma clara
- Usa pausas dramáticas cuando sea apropiado (...)
- Termina con el remate de forma impactante
"""


async def run_joke_agent():
    """Run the joke telling agent with interactive conversation."""
    
    if not PROJECT_ENDPOINT:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT no está configurado.")
        print("Por favor, configura tu .env con el endpoint del proyecto.")
        return

    print("🎭 ¡Bienvenido al Agente Contador de Chistes!")
    print("=" * 50)
    print("Escribe tu mensaje o 'salir' para terminar.")
    print("=" * 50)
    print()

    async with (
        AzureCliCredential() as credential,
        Agent(
            client=AzureAIClient(
                project_endpoint=PROJECT_ENDPOINT,
                model_deployment_name=MODEL_DEPLOYMENT,
                credential=credential,
            ),
            name="JokeAgent",
            instructions=JOKE_AGENT_INSTRUCTIONS,
        ) as agent,
    ):
        # Create a thread for multi-turn conversation
        thread = agent.get_new_thread()
        
        # Initial greeting
        print("🤖 Agente: ", end="", flush=True)
        async for chunk in agent.run_stream(
            "Preséntate brevemente y ofrece contar un chiste.", 
            thread=thread
        ):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")

        # Interactive conversation loop
        while True:
            try:
                user_input = input("👤 Tú: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ["salir", "exit", "quit", "bye", "adiós"]:
                    print("\n🎭 ¡Gracias por reír conmigo! ¡Hasta la próxima! 😄")
                    break

                print("🤖 Agente: ", end="", flush=True)
                async for chunk in agent.run_stream(user_input, thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print("\n")

            except KeyboardInterrupt:
                print("\n\n🎭 ¡Nos vemos! ¡Sigue riendo! 😄")
                break


async def run_single_joke():
    """Run a single joke request (non-interactive mode)."""
    
    if not PROJECT_ENDPOINT:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT no está configurado.")
        return

    async with (
        AzureCliCredential() as credential,
        Agent(
            client=AzureAIClient(
                project_endpoint=PROJECT_ENDPOINT,
                model_deployment_name=MODEL_DEPLOYMENT,
                credential=credential,
            ),
            name="JokeAgent",
            instructions=JOKE_AGENT_INSTRUCTIONS,
        ) as agent,
    ):
        print("🎭 Chiste del día:")
        print("-" * 30)
        
        async for chunk in agent.run_stream("Cuéntame un chiste de programadores"):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    # Run interactive mode by default
    asyncio.run(run_joke_agent())
    
    # Or run single joke mode:
    # asyncio.run(run_single_joke())
