# Configuração do Banco de Dados com Docker

Este documento fornece instruções sobre como configurar e executar o banco de dados PostgreSQL usando Docker Compose.

## Pré-requisitos

- Docker
- Docker Compose

## Configuração do Docker Compose

1. Crie um arquivo `docker-compose.yml` com o seguinte conteúdo:

    ```yaml
    version: '3.7'

    services:
      postgres:
        image: bitnami/postgresql:latest
        ports:
          - '5432:5432'
        environment:
          - POSTGRES_USER=docker
          - POSTGRES_PASSWORD=docker
          - POSTGRES_DB=images
        volumes:
          - images_pg_data:/bitnami/postgresql

    volumes:
      images_pg_data:
    ```

2. Inicie o contêiner do PostgreSQL executando o seguinte comando no diretório onde o arquivo `docker-compose.yml` está localizado:

    ```bash
    docker-compose up -d
    ```

    Este comando fará o download da imagem do PostgreSQL, criará e iniciará o contêiner, e mapeará a porta 5432 do contêiner para a porta 5432 do host.

3. Verifique se o contêiner está em execução:

    ```bash
    docker-compose ps
    ```

    Você deverá ver o contêiner `postgres` listado como `Up`.

## Configuração do Banco de Dados

1. Conecte-se ao banco de dados PostgreSQL usando a URL de conexão:

    ```
    postgresql://docker:docker@localhost:5432/images?schemas=public
    ```

2. Crie a tabela `imagens` no banco de dados executando o seguinte script SQL:

    ```sql
    CREATE TABLE imagens (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        caminho TEXT NOT NULL,
        hash VARCHAR(64) NOT NULL
    );
    ```

## Gerenciamento do Contêiner

### Parar o Contêiner

Para parar o contêiner PostgreSQL, execute:

```bash
docker-compose down
```
