#Monta os arquivos finais

import os #criar pastas
import pandas as pd #tabelas
from datetime import datetime #horário de execução
import uuid #gerar indicadores únicos
import time #Contar os segundos de duração

#Cria as pastas da Gold e da saída final
os.makedirs("gold/data", exist_ok=True)
os.makedirs("output", exist_ok=True)

#Cria a tabela dim_indicador
def create_dim_indicador():
    #Monta manualmente os 3 indicadores:
    dim = pd.DataFrame([
        #Essa tabela serve para evitar repetir nome, código e fonte na fato
        {
            "sk_indicador": 1,
            "codigo": "11",
            "nome": "SELIC",
            "periodicidade": "diaria",
            "fonte": "SGS/BCB"
        },
        {
            "sk_indicador": 2,
            "codigo": "USD",
            "nome": "Dólar comercial",
            "periodicidade": "diaria",
            "fonte": "PTAX/BCB"
        },
        {
            "sk_indicador": 3,
            "codigo": "EUR",
            "nome": "Euro comercial",
            "periodicidade": "diaria",
            "fonte": "PTAX/BCB"
        }
    ])

    return dim #Devolve a dimensão pronta.


def create_fct_indicador_diario(): #Cria a tabela fato principal
    silver = pd.read_csv("silver/data/indicadores_silver.csv") #Lê o arquivo final da Silver

    #Cria a dimensão
    dim = create_dim_indicador()
    #Junta a Silver com a dimensão para trazer o sk_indicador
    fct = silver.merge(
        dim[["sk_indicador", "codigo"]],
        on="codigo",
        how="left"
    )
    #Seleciona só as colunas exigidas na fato
    fct = fct[[
        "data_referencia",
        "sk_indicador",
        "valor",
        "preenchido",
        "vigencia_inicio",
        "vigencia_fim",
        "registro_atual"
    ]]
    #Ordena por data e indicador
    fct = fct.sort_values(["data_referencia", "sk_indicador"]).reset_index(drop=True)
    #Cria a chave sequencial da fato
    fct.insert(0, "sk_fato", range(1, len(fct) + 1))
    fct["valor"] = fct["valor"].round(6)
    
    #Retorna a fato pronta
    return fct

#Cria a tabela de rastreabilidade
def create_pipeline_runs(rows_fct, duracao):
    #Pega o horário atual
    now = datetime.now()

    runs = pd.DataFrame([
        {   
            #Gera um ID único para cada execução
            "id_execucao": str(uuid.uuid4()),
            #Registra qual etapa rodou e se deu certo
            "rotulo": "SELIC",
            "etapa": "bronze",
            "status": "success",
            #Registra quantidade de linhas
            "linhas_retornadas": None,
            "duracao_s": duracao,
            "executado_em": now,
            "mensagem_erro": None
        },
        {
            "id_execucao": str(uuid.uuid4()),
            "rotulo": "PTAX_USD",
            "etapa": "bronze",
            "status": "success",
            "linhas_retornadas": None,
            "duracao_s": duracao,
            "executado_em": now,
            "mensagem_erro": None
        },
        {
            "id_execucao": str(uuid.uuid4()),
            "rotulo": "PTAX_EUR",
            "etapa": "bronze",
            "status": "success",
            "linhas_retornadas": None,
            "duracao_s": duracao,
            "executado_em": now,
            "mensagem_erro": None
        },
        {
            "id_execucao": str(uuid.uuid4()),
            "rotulo": "INDICADORES",
            "etapa": "silver",
            "status": "success",
            "linhas_retornadas": rows_fct,
            "duracao_s": duracao,
            "executado_em": now,
            "mensagem_erro": None
        },
        {
            "id_execucao": str(uuid.uuid4()),
            "rotulo": "FCT_INDICADOR_DIARIO",
            "etapa": "gold",
            "status": "success",
            "linhas_retornadas": rows_fct,
            "duracao_s": duracao,
            "executado_em": now,
            "mensagem_erro": None
        }
    ])

    return runs

#Função principal da Gold
def run_gold():
    inicio = time.time()  #Marca o início da execução

    print("Criando dim_indicador...")
    dim = create_dim_indicador() #Cria a dimensão

    print("Criando fct_indicador_diario...")
    fct = create_fct_indicador_diario() #Cria a fato

    print("Criando pipeline_runs...")

    fim = time.time() #Marca o fim da execução
    duracao = round(fim - inicio, 2) #Calcula o tempo em segundos

    runs = create_pipeline_runs(len(fct), duracao) #Cria a tabela de execução com duração real

    #Salva os 2 arquivos principais na pasta output
    dim.to_csv("output/dim_indicador.csv", index=False, encoding="utf-8-sig")
    fct.to_csv("output/fct_indicador_diario.csv", index=False, encoding="utf-8-sig")

    #Caminho do histórico de execução
    pipeline_path = "output/pipeline_runs.csv"

    #Se já existir histórico, adiciona a nova execução sem apagar as anteriores
    if os.path.exists(pipeline_path):
        historico = pd.read_csv(pipeline_path)
        runs = pd.concat([historico, runs], ignore_index=True)

    #Salva histórico atualizado
    runs.to_csv(pipeline_path, index=False, encoding="utf-8-sig")

    #Também salva uma cópia dentro da Gold
    dim.to_csv("gold/data/dim_indicador.csv", index=False, encoding="utf-8-sig")
    fct.to_csv("gold/data/fct_indicador_diario.csv", index=False, encoding="utf-8-sig")
    runs.to_csv("gold/data/pipeline_runs.csv", index=False, encoding="utf-8-sig")

    print(f"Gold concluído com sucesso! Tempo: {duracao}s")


if __name__ == "__main__":
    run_gold()