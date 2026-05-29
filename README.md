Case Work Avanti — Pipeline de Dados Banco Central

## Objetivo

Este projeto implementa um pipeline de dados para consumo, tratamento e disponibilização de indicadores econômicos públicos disponibilizados pelo Banco Central do Brasil.

O pipeline consome dados históricos de:

- Taxa SELIC diária
- Cotação USD
- Cotação EUR

O objetivo é disponibilizar uma tabela histórica contínua, sem lacunas, pronta para consumo analítico.

---

## Arquitetura adotada

Foi adotado o padrão **Medallion Architecture**, dividido em três camadas:

### Bronze — Ingestão bruta

Responsável por:

- Consumir APIs públicas do Banco Central
- Persistir payload bruto sem transformação
- Garantir retry automático em falhas de comunicação

Saídas:

- `selic.json`
- `usd.json`
- `eur.json`

---

### Silver — Limpeza e padronização

Responsável por:

- Normalização de formatos de data
- Conversão de tipos
- Unificação de schemas
- Geração de calendário contínuo
- Aplicação de forward fill
- Identificação de registros preenchidos

Saída:

- `indicadores_silver.csv`

---

### Gold — Camada analítica

Responsável por gerar a modelagem analítica final.

Saídas:

- `fct_indicador_diario.csv`
- `dim_indicador.csv`
- `pipeline_runs.csv`

---

## Estrutura do projeto

```text
case-work-avanti/
│
├── bronze/
├── silver/
├── gold/
├── output/
├── main.py
├── requirements.txt
└── README.md
```

---

## Decisões técnicas

### Retry com backoff exponencial

Implementado com a biblioteca `tenacity`.

Objetivo:

Garantir robustez no consumo das APIs públicas do Banco Central.

---

### Forward Fill

Como as APIs não retornam dados para finais de semana e feriados, foi implementado preenchimento com o último valor conhecido.

Exemplo:

- Sexta: 4.90
- Sábado: 4.90
- Domingo: 4.90

Os registros preenchidos recebem:

```python
preenchido = True
```

---

### Idempotência

A estrutura do pipeline permite reprocessamento sem impacto sobre a consistência da saída final, sobrescrevendo arquivos gerados.

---

### SCD Type 2

Foi implementada estrutura base para versionamento histórico através dos campos:

- `vigencia_inicio`
- `vigencia_fim`
- `registro_atual`

---

## Modelo de dados

### dim_indicador

| Campo | Descrição |
|------|-----------|
| sk_indicador | Chave substituta |
| codigo | Código do indicador |
| nome | Nome do indicador |
| periodicidade | Frequência |
| fonte | Origem |

---

### fct_indicador_diario

| Campo | Descrição |
|------|-----------|
| sk_fato | Chave da fato |
| data_referencia | Data do indicador |
| sk_indicador | FK |
| valor | Valor diário |
| preenchido | Flag de preenchimento |
| vigencia_inicio | Início da vigência |
| vigencia_fim | Fim da vigência |
| registro_atual | Registro vigente |

---

### pipeline_runs

Tabela de rastreabilidade das execuções.

Campos principais:

- etapa
- status
- linhas_retornadas
- executado_em
- mensagem_erro
- duracao_s

---

## Como executar

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

### 2. Ativar ambiente

Windows:

```bash
venv\Scripts\activate
```

---

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 4. Executar pipeline completo

```bash
python main.py
```

---

## Arquivos gerados

Após execução:

```text
output/
├── dim_indicador.csv
├── fct_indicador_diario.csv
└── pipeline_runs.csv
```

---

## Tecnologias utilizadas

- Python
- Pandas
- Requests
- Tenacity

---

## Autor

Daphine Andrade
