from google.adk.agents.llm_agent import Agent
from trello import TrelloClient
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

API_KEY = os.getenv('TRELLO_API_KEY')
API_SECRET = os.getenv('TRELLO_API_SECRET')
TOKEN = os.getenv('TRELLO_TOKEN')
client = None
meu_board = None
listas = None


def get_context():
    global client, meu_board, listas

    if client and meu_board and listas:
        return client, meu_board, listas

    client = TrelloClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        token=TOKEN
    )

    boards = client.list_boards()
    meu_board = next(b for b in boards if b.name == 'DIO')
    listas = meu_board.list_lists()

    return client, meu_board, listas

def get_temporal_context():
    now = datetime.now()
    return now.strftime("%Y/%m/%d, %H:%M:%S")

def adicionar_tarefa(nome_da_task: str, descricao_da_task: str, due_date: str):
    try:
        _, _, listas = get_context()
        minha_lista = [l for l in listas if l.name.upper() == 'TO DO' or l.name.upper() == 'A FAZER'][0]

        minha_lista.add_card(
            name=nome_da_task,
            desc=descricao_da_task,
            due=due_date
        )

    except Exception as e:
        return f"X Error: '{str(e)}'"

def listar_tarefas(status: str = "todas"):
    try:
        _, _, listas = get_context()
        if status.lower() == "todas":
            listas_filtradas = listas
        elif status.lower() == "a fazer":
            listas_filtradas = [l for l in listas if l.name.upper() in ["A FAZER", "TO DO", "TODO"]]
        elif status.lower() == "em andamento":
            listas_filtradas = [l for l in listas if l.name.upper() in ["EM ANDAMENTO", "DOING"]]
        elif status.lower() == "concluido":
            listas_filtradas = [l for l in listas if l.name.upper() in ["CONCLUÍDO", "CONCLUIDO", "DONE"]]
        else:
            listas_filtradas = listas

        tarefas = []

        for lista in listas_filtradas:
            cards = lista.list_cards()
            for card in cards:
                tarefas.append({
                    "nome": card.name,
                    "descrição": card.desc,
                    "vencimento": card.due,
                    "status": lista.name,
                    "id": card.id
                })
        return tarefas

    except Exception as e:
        return f"X Error: '{str(e)}'"

def mudar_status_tarefa(nome_da_task: str, novo_status: str) -> str:
    try:
        _, _, listas = get_context()

        status_map = {
            "a fazer": "A FAZER",
            "em andamento": "EM ANDAMENTO",
            "concluido": "CONCLUÍDO",
            "concluído": "CONCLUÍDO",
            "terminar": "CONCLUÍDO",
            "finalizar": "CONCLUÍDO",
            "finalize": "CONCLUÍDO",
            "completar": "CONCLUÍDO",
            "conclua": "CONCLUÍDO",
            "finalizada": "CONCLUÍDO"
        }

        nome_lista_destino = status_map.get(novo_status.lower())

        if not nome_lista_destino:
            return f"X Status invalido. Use: 'a fazer', 'em andamento' ou 'concluido'"

        lista_destino = next(
            (l for l in listas if l.name.upper() == nome_lista_destino.upper()),
            None
        )

        if not lista_destino:
            return f"X Lista '{nome_lista_destino}' não encontrada no Board."

        card_encontrado = None
        lista_origem = None

        for lista in listas:
            cards = lista.list_cards()
            card_encontrado = next(
                (c for c in cards if c.name.lower() == nome_da_task.lower()),
                None
            )
            if card_encontrado:
                lista_origem = lista
                break

        if not card_encontrado:
            return f"X Card '{nome_da_task}' não encontrado."
        
        card_encontrado.change_list(lista_destino.id)
        return f"Tarefa '{nome_da_task}' movida do '{lista_origem.name}' para status '{lista_destino.name}' com sucesso!"



    except Exception as e:
        return f"X Error: '{str(e)}'"





root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction="""
        Você é um agente que vai me ajudar a gerenciar as minhas Tasks no Trello.
        Sua função é receber uma tarefa e criar um card no Trello com nome e com descrição.
        Você deve perguntar as tarefas que tenho para o dia e criar um card para cada uma delas.
        Você inicia a conversa assim que for ativado, perguntando quais são as tarefas do dia.
        Sempre inicie a conversa perguntando quais são as tarefas do dia informando a data com o tool get_temporal_context,
        e depois vá perguntando se tem mais alguma tarefa, até que o usuário diga que não tem mais tarefas.
        Suas Funções:
            1. Adicionar novas tarefas com nome e descrição
            2. Listar todas as tarefas ou filtrar por status.
            3. Marcar tarefas como concluídas.
            4. Remover tarefas da lista.
            5. Mudar o status da tarefa (ex: de "A fazer" para "Em andamento" e de "Em andamento" para "Concluído").
            6. Gerar contexto temporal (data e hora atual) para organizar as tarefas do dia.
    """,
    tools=[get_temporal_context, adicionar_tarefa, listar_tarefas, mudar_status_tarefa],
)
