from tavily import TavilyClient

tavily = TavilyClient(api_key="Stvly-dev-3YXBOg-D90CM8ILOOD7bv8XpYZ0gsTmjIriWnu1KIRKZxVRBp")

def buscar_internet(pergunta):
    try:
        resposta = tavily.search(query=pergunta, max_results=3)
        return resposta
    except Exception as e:
        return f"Erro na busca: {e}"