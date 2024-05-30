import psycopg2
from urllib.parse import urlparse

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

def add_hash_column():
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # Adicionar a coluna hash à tabela imagens
        cursor.execute("ALTER TABLE imagens ADD COLUMN hash VARCHAR(64);")
        connection.commit()
        
        print("Coluna 'hash' adicionada com sucesso.")
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Erro ao adicionar coluna 'hash': {e}")

if __name__ == "__main__":
    add_hash_column()
