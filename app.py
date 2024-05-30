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

# Função para calcular o hash de uma imagem
def calcular_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Endpoint para enviar uma nova imagem
@app.route("/imagens", methods=["POST"])
def upload_image():
    try:
        if 'imagem' not in request.files:
            return jsonify({"error": "Nenhuma imagem foi enviada"}), 400

        imagem = request.files['imagem']
        if imagem.filename == '':
            return jsonify({"error": "Nenhuma imagem foi enviada"}), 400

        filepath = os.path.join("uploads", imagem.filename)
        imagem.save(filepath)

        # Calcula o hash da imagem
        imagem_hash = calcular_hash(filepath)

        connection = connect()
        cursor = connection.cursor()
        
        # Verifica se o hash já existe no banco de dados
        cursor.execute("SELECT COUNT(*) FROM imagens WHERE hash = %s", (imagem_hash,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            connection.close()
            os.remove(filepath)
            return jsonify({"error": "Imagem duplicada"}), 400

        cursor.execute(
            "INSERT INTO imagens (nome, caminho, hash) VALUES (%s, %s, %s)",
            (imagem.filename, filepath, imagem_hash)
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
            caminho_imagem = imagem[2]
            if os.path.exists(caminho_imagem):
                with open(caminho_imagem, 'rb') as file:
                    dados_base64 = base64.b64encode(file.read()).decode('utf-8')
                    imagens_list.append({"id": imagem[0], "nome": imagem[1], "dados": dados_base64})
            else:
                print(f"Arquivo de imagem não encontrado: {caminho_imagem}")

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
        
        # Verifica se o arquivo de imagem existe
        if os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)  # Remove o arquivo da imagem do diretório de upload
        else:
            print(f"Arquivo de imagem não encontrado: {caminho_imagem}")
        
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
