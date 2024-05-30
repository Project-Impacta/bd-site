# Image Gallery

Este é um projeto de galeria de imagens usando Flask para o backend.

## Pré-requisitos

- Python 3.x
- PostgreSQL

## Configuração do Projeto

1. Clone este repositório:

    ```bash
    git clone https://github.com/seu_usuario/seu_repositorio.git
    cd seu_repositorio
    ```

2. Crie um ambiente virtual (recomendado) e ative-o:

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. Instale as dependências do projeto:

    ```bash
    pip install .
    ```

4. Configure seu banco de dados PostgreSQL e crie a tabela `imagens`:

    ```sql
    CREATE TABLE imagens (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        caminho TEXT NOT NULL,
        hash VARCHAR(64) NOT NULL
    );
    ```

## Executando o Projeto

1. Execute o servidor Flask:

    ```bash
    flask run
    ```

## Estrutura do Projeto

- `app.py`: Arquivo principal que contém a configuração do servidor Flask e os endpoints da API.
- `uploads/`: Diretório onde as imagens enviadas serão armazenadas.
- `setup.py`: Arquivo para definir as dependências do projeto.
- `README.md`: Instruções para configuração e execução do projeto.

## Endpoints da API

### Upload de Imagem

- **URL:** `/imagens`
- **Método:** `POST`
- **Descrição:** Envia uma nova imagem para o servidor.

### Listar Imagens

- **URL:** `/imagens`
- **Método:** `GET`
- **Descrição:** Lista todas as imagens armazenadas no servidor.

### Excluir Imagem

- **URL:** `/imagens/<int:id>`
- **Método:** `DELETE`
- **Descrição:** Exclui uma imagem específica pelo ID.

## Código do Backend

### app.py

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from urllib.parse import urlparse
import os
import base64
import hashlib

app = Flask(__name__)
CORS(app)

# Extrair as partes da URL de conexão
url = urlparse("postgresql://docker:docker@localhost:5432/images?schemas=public")

# Função para conectar ao banco de dados
def connect():
    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )

# Endpoint para enviar uma nova imagem
@app.route("/imagens", methods=["POST"])
def upload_image():
    try:
        if 'imagem' not in request.files:
            return jsonify({"error": "Nenhuma imagem foi enviada"}), 400

        imagem = request.files['imagem']
        if imagem.filename == '':
            return jsonify({"error": "Nenhuma imagem foi enviada"}), 400

        # Calcular o hash da imagem
        image_content = imagem.read()
        image_hash = hashlib.sha256(image_content).hexdigest()

        # Verificar se a imagem já existe
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM imagens WHERE hash = %s", (image_hash,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            connection.close()
            return jsonify({"error": "Imagem já existe"}), 400

        # Salvar a imagem
        filepath = os.path.join("uploads", imagem.filename)
        with open(filepath, 'wb') as f:
            f.write(image_content)

        # Inserir os dados da imagem no banco de dados
        cursor.execute(
            "INSERT INTO imagens (nome, caminho, hash) VALUES (%s, %s, %s)",
            (imagem.filename, filepath, image_hash)
        )
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "Imagem enviada com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao enviar imagem: {e}")
        return jsonify({"error": "Erro ao enviar imagem"}), 500

# Endpoint para listar todas as imagens
@app.route("/imagens", methods=["GET"])
def list_images():
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, nome, caminho FROM imagens")
        imagens = cursor.fetchall()
        cursor.close()
        connection.close()

        # Codificar dados das imagens em base64
        imagens_list = []
        for imagem in imagens:
            try:
                with open(imagem[2], 'rb') as file:
                    dados_base64 = base64.b64encode(file.read()).decode('utf-8')
                    imagens_list.append({"id": imagem[0], "nome": imagem[1], "dados": dados_base64})
            except FileNotFoundError:
                print(f"Arquivo não encontrado: {imagem[2]}")

        return jsonify({"imagens": imagens_list}), 200
    except Exception as e:
        print(f"Erro ao buscar imagens: {e}")
        return jsonify({"error": "Erro ao buscar imagens"}), 500

# Endpoint para excluir uma imagem específica
@app.route("/imagens/<int:id>", methods=["DELETE"])
def delete_image(id):
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT caminho FROM imagens WHERE id = %s", (id,))
        caminho_imagem = cursor.fetchone()[0]
        os.remove(caminho_imagem)  # Remove o arquivo da imagem do diretório de upload
        cursor.execute("DELETE FROM imagens WHERE id = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": f"Imagem com o ID {id} excluída com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao excluir imagem: {e}")
        return jsonify({"error": "Erro ao excluir imagem"}), 500

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
```

### Instruções Adicionais

- Certifique-se de que o diretório `uploads` esteja criado na raiz do projeto para armazenar as imagens enviadas.
- Caso ocorra algum erro ao buscar ou excluir imagens, verifique se o arquivo realmente existe no diretório `uploads`.

Com estas instruções e arquivos, você deve ser capaz de configurar e executar o projeto de galeria de imagens com Flask. Se você tiver alguma dúvida ou encontrar problemas, sinta-se à vontade para perguntar.
