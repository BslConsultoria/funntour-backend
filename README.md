# Funntour API

API de backend para o sistema Funntour.

## Requisitos

* Python 3.8+
* MySQL Server

## Instalação

1. Clone o repositório
2. Instale as dependências com:
   ```
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente no arquivo `.env`:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USERNAME=root
   DB_PASSWORD=suasenha
   DB_NAME=db_funntour
   ```

## Configuração do Banco de Dados

Antes de iniciar a aplicação, crie um banco de dados MySQL com o nome especificado em `DB_NAME`.

Para criar as tabelas, execute o seguinte comando:
```
alembic upgrade head
```

## Execução

Para iniciar o servidor de desenvolvimento:
```
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

## Documentação

A documentação da API estará disponível em:
* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

## Estrutura do Projeto

```
funntour/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config/
  │   │   └── database.py
  │   ├── models/
  │   │   └── pais.py
  │   ├── schemas/
  │   │   └── pais.py
  │   ├── routes/
  │   │   └── pais.py
  │   └── services/
  │       └── pais.py
  ├── requirements.txt
  ├── .env
  └── README.md
```
