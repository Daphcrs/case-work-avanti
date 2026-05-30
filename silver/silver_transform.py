#Limpa e organiza

import json #ler arquivos JSON
import os #criar pasta
import pandas as pd #manipular tabelas
from datetime import datetime #registrar horário

os.makedirs("silver/data", exist_ok=True) #Cria a pasta da Silver


def read_json(path): #Função para ler JSON
    #Abre o arquivo e transforma em objeto Python
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def transform_selic(): #Função para transformar os dados da SELIC
    data = read_json("bronze/data/selic.json") #Lê o arquivo bruto da Bronze

    df = pd.DataFrame(data) #Transforma o JSON em tabela
    #Converte a data da SELIC para formato de data real
    df["data_referencia"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    #Transforma o valor, que veio como texto, em número
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").round(6)
    #Adiciona informações fixas da SELIC
    df["codigo"] = "11"
    df["nome"] = "SELIC"
    df["fonte"] = "SGS/BCB"

    #Retorna só as colunas que interessam
    return df[["data_referencia", "codigo", "nome", "fonte", "valor"]]

#Função genérica para dólar e euro
def transform_ptax(filename, codigo, nome):
    #Lê usd.json ou eur.json
    data = read_json(f"bronze/data/{filename}")

    #Na API PTAX, os dados vêm dentro de uma chave chamada value
    df = pd.DataFrame(data["value"]) 
    #Transforma a data/hora da cotação em data
    df["data_referencia"] = pd.to_datetime(df["dataHoraCotacao"]).dt.date
    #Pega a cotação de compra e transforma em número
    df["valor"] = pd.to_numeric(df["cotacaoCompra"])
    #Adiciona informações do indicador.
    df["codigo"] = codigo
    df["nome"] = nome
    df["fonte"] = "PTAX/BCB"

    return df[["data_referencia", "codigo", "nome", "fonte", "valor"]]


def apply_forward_fill(df): #Preenche os dias sem cotação, como sábado, domingo e feriado
    #Garante que a coluna é data
    df["data_referencia"] = pd.to_datetime(df["data_referencia"])

    #Cria uma lista para guardar os dados finais
    final = []

    #Faz o processo separado para cada indicador: SELIC, USD e EUR
    for codigo in df["codigo"].unique():
        #Filtra só um indicador por vez
        indicador = df[df["codigo"] == codigo].copy()
        #Ordena por data
        indicador = indicador.sort_values("data_referencia")

        #Cria um calendário com todos os dias, sem pular fim de semana
        calendario = pd.DataFrame({
            "data_referencia": pd.date_range(
                start=indicador["data_referencia"].min(),
                end=indicador["data_referencia"].max(),
                freq="D"
            )
        })

        #Junta o calendário com os dados reais
        completo = calendario.merge(
            indicador,
            on="data_referencia",
            how="left"
        )

        #Se o valor está vazio, marca preenchido = True
        completo["preenchido"] = completo["valor"].isna()

        #Preenche código, nome e fonte com o último valor conhecido
        completo[["codigo", "nome", "fonte"]] = completo[["codigo", "nome", "fonte"]].ffill()
        #Aqui acontece o forward fill
        completo["valor"] = completo["valor"].ffill()

        #Guarda o resultado daquele indicador
        final.append(completo)

    #Junta SELIC, USD e EUR em uma tabela só
    return pd.concat(final, ignore_index=True)

#Função principal da Silver
def run_silver():
    #Transforma os 3 indicadores
    print("Transformando SELIC...")
    selic = transform_selic()

    print("Transformando USD...")
    usd = transform_ptax("usd.json", "USD", "Dólar comercial")

    print("Transformando EUR...")
    eur = transform_ptax("eur.json", "EUR", "Euro comercial")

    #Junta tudo em uma tabela só
    print("Unificando indicadores...")
    df = pd.concat([selic, usd, eur], ignore_index=True)

    print("Aplicando calendário contínuo e forward fill...")
    df_final = apply_forward_fill(df) #Cria calendário contínuo e preenche lacunas

    #Adiciona campos relacionados ao SCD2
    df_final["vigencia_inicio"] = datetime.now()
    df_final["vigencia_fim"] = None
    df_final["registro_atual"] = True

    #Salva o resultado Silver em CSV
    df_final.to_csv("silver/data/indicadores_silver.csv", index=False, encoding="utf-8-sig")

    print("Silver concluído com sucesso!")


if __name__ == "__main__": 
    run_silver()