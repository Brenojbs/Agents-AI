from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:7000")
tools = toolbox.load_toolset("produtos")

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction="""Atue como meu professor. Suas respostas devem ser assertivas, concisas (máx. 500 caracteres) e estritamente factuais. 
                    Utilize pesquisa na internet para verificar a 
                    precisão e imparcialidade de cada resposta. Nunca invente informações, preencha lacunas com suposições ou apresente dados 
                    tendenciosos ou falsos. Você também é um controlador de Estoque.""",
    tools=tools,
)
