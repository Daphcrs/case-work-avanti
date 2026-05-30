#Roda todas as etapas

#Importa as funções principais de cada camada
from bronze.bronze_extract import run_bronze
from silver.silver_transform import run_silver
from gold.gold_build import run_gold

#Cria a função principal do pipeline
def run_pipeline():
    print("[INFO] Iniciando pipeline...\n")

    #Primeiro baixa os dados
    print("[INFO] Iniciando camada Bronze")
    run_bronze()
    #Depois limpa e preenche
    print("\n[INFO] Iniciando camada Silver")
    run_silver()
    #Depois gera os arquivos finais
    print("\n[INFO] Iniciando camada Gold")
    run_gold()

    print("\n[SUCCESS] Pipeline finalizado com sucesso!")


if __name__ == "__main__":
    run_pipeline()