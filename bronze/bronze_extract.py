#Pega os dados crus

import requests #Permite chamar APIs.
import json #Permite salvar os dados em formato JSON.
import os #Permite criar pastas pelo Python.
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential #Importa ferramentas para tentar de novo caso a API falhe.

# Criar pasta se não existir
os.makedirs("bronze/data", exist_ok=True)

# URLs das APIs
SELIC_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial=01/01/2024"

USD_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
    "?@moeda='USD'&@dataInicial='01-01-2024'&@dataFinalCotacao='12-31-2024'"
    "&$format=json"
)

EUR_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
    "?@moeda='EUR'&@dataInicial='01-01-2024'&@dataFinalCotacao='12-31-2024'"
    "&$format=json"
)

#Se a API falhar, tenta de novo automaticamente 3 vezes.
#Retry com backof
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2)
)
def fetch_data(url): #Cria uma função para buscar dados de uma URL.
    response = requests.get(url) #Chama a API.

    if response.status_code != 200: #Verifica se a API respondeu com sucesso. Status 200 significa “deu certo”.
        raise Exception(f"Erro na API: {response.status_code}") #Se não deu certo, gera erro.

    return response.json() #Converte a resposta da API para JSON.


def save_json(data, filename): #Cria uma função para salvar JSON em arquivo.
    with open(f"bronze/data/{filename}", "w", encoding="utf-8") as f: #Abre/cria o arquivo.
        json.dump(data, f, ensure_ascii=False, indent=4) #Salva o JSON bonitinho, com indentação.


def run_bronze(): #Função principal da Bronze.
    print("Extraindo SELIC...")
    selic = fetch_data(SELIC_URL) #Busca SELIC e salva.s
    save_json(selic, "selic.json")

    print("Extraindo USD...")
    usd = fetch_data(USD_URL) #Busca dólar e salva.
    #Salva o retorno bruto da API. (Bronze)
    save_json(usd, "usd.json")

    print("Extraindo EUR...")
    eur = fetch_data(EUR_URL) #Busca euro e salva.
    save_json(eur, "eur.json")

    print("Extração concluída com sucesso!")


if __name__ == "__main__": 
    run_bronze()