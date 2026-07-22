# CVM Funds Analytics

A aplicação baixa dados públicos da CVM, trata e carrega os arquivos em PostgreSQL, disponibiliza uma API com FastAPI e apresenta uma interface web para consulta.

## Funcionalidades

- ETL reexecutável por script
- Download de dados cadastrais e informes diários da CVM
- Normalização de CNPJs
- Remoção de duplicidades
- Identificação de registros sem correspondência cadastral
- Carga em PostgreSQL
- API REST com FastAPI
- Consulta de fundos por nome ou CNPJ
- Resumo por fundo
- Histórico diário
- Ranking por patrimônio líquido
- Frontend simples em HTML, CSS e JavaScript

## Tecnologias

- Python 3.12
- Pandas
- FastAPI
- Psycopg
- PostgreSQL 16
- Docker e Docker Compose
- HTML, CSS e JavaScript

## Estrutura

```text
cvm-funds-analytics/
├── data/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── src/
│   ├── api/
│   │   └── main.py
│   ├── etl/
│   │   ├── extractor.py
│   │   ├── transformer.py
│   │   └── loader.py
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Pré-requisitos

Para executar o projeto, é necessário ter Docker e Docker Compose instalados.

### Windows e macOS

Instale o Docker Desktop e confirme que ele está aberto antes de executar o projeto.

Valide a instalação:

```bash
docker --version
docker compose version
docker info

## Como executar

### 1. Subir os containers

Na raiz do projeto:

```bash
docker compose up --build -d
```

Verifique os serviços:

```bash
docker compose ps
```

### 2. Executar o ETL

```bash
docker compose run --rm api python src/main.py
```

O ETL:

1. cria as tabelas;
2. baixa os arquivos da CVM;
3. transforma os dados;
4. remove duplicidades;
5. identifica inconsistências;
6. carrega os dados válidos no PostgreSQL.

### 3. Acessar a aplicação

Frontend:

```text
http://localhost:5500
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Endpoints

### Buscar fundos

```http
GET /funds
```

Parâmetros opcionais:

- `q`
- `cnpj`
- `limit`

### Consultar informes

```http
GET /funds/{cnpj}/reports
```

### Consultar resumo

```http
GET /funds/{cnpj}/summary
```

Retorna:

- cota mais recente;
- patrimônio líquido;
- número de cotistas;
- retorno no período;
- captação líquida.

### Consultar histórico

```http
GET /funds/{cnpj}/history
```

Retorna a série diária de cota, patrimônio, captação, resgate, fluxo líquido e cotistas.

### Ranking

```http
GET /analytics/ranking?limit=10
```

Ordena os fundos pelo patrimônio líquido mais recente.

## Janela de dados

Os meses processados são definidos em `src/main.py`.

Exemplo:

```python
month_window = [
    ("2026", "04"),
    ("2026", "05"),
    ("2026", "06"),
]
```

## Tratamento de inconsistências

Alguns informes possuem CNPJs que não aparecem no cadastro atual de classes.

Para preservar a integridade referencial:

- esses registros são identificados;
- a quantidade é exibida nos logs;
- exemplos de CNPJs são informados;
- os registros sem correspondência são ignorados.

Exemplo:

```text
[AVISO] 202604: 10244 registros ignorados
[OK] 202604: 493982 informes carregados
```

## Reexecução

O banco pode ser reconstruído executando novamente o ETL:

```bash
docker compose run --rm api python src/main.py
```

Os arquivos já baixados são reaproveitados. Para forçar novo download, remova os arquivos de `data/raw/`.

## Sustentabilidade do pipeline

Em uma versão de produção, o pipeline poderia ser mantido com:

- execução agendada;
- retries no download;
- logs estruturados;
- alertas de falha;
- validação de mudanças no schema;
- testes dos transformers;
- carga incremental;
- métricas de qualidade dos dados.

Como os serviços estão containerizados, o projeto pode ser executado em qualquer ambiente com Docker.


## Encerrar os serviços

```bash
docker compose down
```

Para remover também o volume do PostgreSQL:

```bash
docker compose down -v
```

