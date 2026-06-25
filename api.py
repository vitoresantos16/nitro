import sqlite3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

NOME_BANCO = 'nitro.db'

def configurar_banco():
        conexao = sqlite3.connect(NOME_BANCO)
        cursor = conexao.cursor()
        
        cursor.executescript('''
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS "usuarios" (
                        "id_usuario" INTEGER PRIMARY KEY AUTOINCREMENT,
                        "nome" TEXT NOT NULL,
                        "email" TEXT NOT NULL,
                        "senha" TEXT NOT NULL,
                        "telefone" TEXT NOT NULL,
                        "endereco" TEXT NOT NULL,
                        "data_cadastro" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        "anunciante" TINYINT NOT NULL
                );

                CREATE UNIQUE INDEX IF NOT EXISTS "nome_UNIQUE" ON "usuarios" ("nome" ASC);
                CREATE UNIQUE INDEX IF NOT EXISTS "email_UNIQUE" ON "usuarios" ("email" ASC);
                CREATE UNIQUE INDEX IF NOT EXISTS "telefone_UNIQUE" ON "usuarios" ("telefone" ASC);

                CREATE TABLE IF NOT EXISTS "produtos" (
                        "id_produto" INTEGER PRIMARY KEY AUTOINCREMENT,
                        "id_usuario" INTEGER NOT NULL,
                        "nome" TEXT NOT NULL,
                        "categoria" TEXT NOT NULL,
                        "descricao" TEXT NOT NULL,
                        "preco" DECIMAL(10,2) NOT NULL,
                        "estoque" INTEGER NOT NULL,
                        "marca" TEXT NOT NULL,
                        "imagem" TEXT NOT NULL,
                        
                        CONSTRAINT "fk_id_usuario1"
                        FOREIGN KEY ("id_usuario")
                        REFERENCES "usuarios" ("id_usuario")
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );

                CREATE INDEX IF NOT EXISTS "id_usuario_idx" ON "produtos" ("id_usuario" ASC);

                CREATE TABLE IF NOT EXISTS "carrinho" (
                        "id_carrinho" INTEGER PRIMARY KEY AUTOINCREMENT,
                        "id_usuario" INTEGER NOT NULL,
                        "data_criacao" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        
                        CONSTRAINT "fk_id_usuario2"
                        FOREIGN KEY ("id_usuario")
                        REFERENCES "usuarios" ("id_usuario")
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );

                CREATE UNIQUE INDEX IF NOT EXISTS "id_usuario_UNIQUE" ON "carrinho" ("id_usuario" ASC);

                CREATE TABLE IF NOT EXISTS "itens_carrinho" (
                        "id_itens_carrinho" INTEGER PRIMARY KEY AUTOINCREMENT,
                        "id_carrinho" INTEGER NOT NULL,
                        "id_produto" INTEGER NOT NULL,
                        "quantidade" INTEGER NOT NULL DEFAULT 1,
                        
                        CONSTRAINT "fk_id_carrinho1"
                        FOREIGN KEY ("id_carrinho")
                        REFERENCES "carrinho" ("id_carrinho")
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,
                        CONSTRAINT "fk_id_produto1"
                        FOREIGN KEY ("id_produto")
                        REFERENCES "produtos" ("id_produto")
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );

                CREATE INDEX IF NOT EXISTS "id_carrinho1_idx" ON "itens_carrinho" ("id_carrinho" ASC);
                CREATE INDEX IF NOT EXISTS "id_produto1_idx" ON "itens_carrinho" ("id_produto" ASC);

                CREATE TABLE IF NOT EXISTS "pedidos" (
                        "id_pedidos" INTEGER PRIMARY KEY AUTOINCREMENT,
                        "id_usuario" INTEGER NOT NULL,
                        "valor_total" DECIMAL(10,2) NOT NULL,
                        "status" TEXT NOT NULL DEFAULT 'Pendente',
                        "data_pedido" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        
                        CONSTRAINT "fk_id_usuario3"
                        FOREIGN KEY ("id_usuario")
                        REFERENCES "usuarios" ("id_usuario")
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );

                CREATE INDEX IF NOT EXISTS "id_usuario3_idx" ON "pedidos" ("id_usuario" ASC);

                CREATE TABLE IF NOT EXISTS "itens_pedido" (
                        "id_itens_pedido" INTEGER PRIMARY KEY AUTOINCREMENT,
                        "id_pedido" INTEGER NOT NULL,
                        "id_produto" INTEGER NOT NULL,
                        "quantidade" INTEGER NOT NULL DEFAULT 1,
                        "preco_unidade" DECIMAL(10,2) NOT NULL,
                        
                        CONSTRAINT "fk_id_pedido1"
                        FOREIGN KEY ("id_pedido")
                        REFERENCES "pedidos" ("id_pedidos")
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,
                        CONSTRAINT "fk_id_produto2"
                        FOREIGN KEY ("id_produto")
                        REFERENCES "produtos" ("id_produto")
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );

                CREATE INDEX IF NOT EXISTS "id_pedido1_idx" ON "itens_pedido" ("id_pedido" ASC);
                CREATE INDEX IF NOT EXISTS "id_produto2_idx" ON "itens_pedido" ("id_produto" ASC);
        ''')

        conexao.commit()
        print('Banco de dados criado e populado com sucesso.')
        conexao.close()

class NitroAPI(BaseHTTPRequestHandler):
        def do_GET(self):
                if self.path == '/api/usuarios':
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()

                        conexao = sqlite3.connect(NOME_BANCO)
                        conexao.row_factory = sqlite3.Row
                        cursor = conexao.cursor()
                        cursor.execute('SELECT * FROM usuarios')

                        usuarios = [dict(linha) for linha in cursor.fetchall()]

                        conexao.close()
                        self.wfile.write(json.dumps(usuarios).encode('utf-8'))

                elif self.path == '/api/produtos':
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()

                        conexao = sqlite3.connect(NOME_BANCO)
                        conexao.row_factory = sqlite3.Row
                        cursor = conexao.cursor()
                        cursor.execute('SELECT * FROM produtos')

                        produtos = [dict(linha) for linha in cursor.fetchall()]

                        conexao.close()
                        self.wfile.write(json.dumps(produtos).encode('utf-8'))

                elif self.path.startswith('/api/carrinho/'):
                        id_usuario = self.path.split('/')[-1]

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()

                        conexao = sqlite3.connect(NOME_BANCO)
                        conexao.row_factory = sqlite3.Row
                        cursor = conexao.cursor()

                        cursor.execute("""
                                SELECT
                                p.id_produto,
                                p.nome,
                                p.preco,
                                ic.quantidade
                                FROM carrinho c
                                JOIN itens_carrinho ic ON c.id_carrinho = ic.id_carrinho
                                JOIN produtos p ON ic.id_produto = p.id_produto
                                WHERE c.id_usuario = ?
                        """, (id_usuario,))

                        itens = [dict(linha) for linha in cursor.fetchall()]

                        conexao.close()
                        self.wfile.write(json.dumps(itens).encode('utf-8'))

                elif self.path.startswith('/api/pedidos/'):
                        id_usuario = self.path.split('/')[-1]

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()

                        conexao = sqlite3.connect(NOME_BANCO)
                        conexao.row_factory = sqlite3.Row
                        cursor = conexao.cursor()

                        cursor.execute("""
                                SELECT
                                p.id_pedidos,
                                p.status,
                                p.valor_total,
                                p.data_pedido,
                                pr.id_produto,
                                pr.nome,
                                ip.quantidade,
                                ip.preco_unidade
                                FROM pedidos p
                                JOIN itens_pedido ip ON p.id_pedidos = ip.id_pedido
                                JOIN produtos pr ON ip.id_produto = pr.id_produto
                                WHERE p.id_usuario = ?
                                ORDER BY p.data_pedido DESC
                        """, (id_usuario,))

                        pedidos = [dict(linha) for linha in cursor.fetchall()]

                        conexao.close()
                        self.wfile.write(json.dumps(pedidos).encode('utf-8'))

                else:
                        self.send_response(404)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"erro": "Rota não encontrada"}).encode('utf-8'))

        def do_POST(self):
                if self.path == '/api/usuarios':
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        dados = json.loads(post_data.decode('utf-8'))

                        conexao = sqlite3.connect(NOME_BANCO)
                        cursor = conexao.cursor()

                        try:
                                cursor.execute('''
                                        INSERT INTO usuarios
                                        (nome, email, senha, telefone, endereco, anunciante)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                ''', (
                                        dados['nome'],
                                        dados['email'],
                                        dados['senha'],
                                        dados['telefone'],
                                        dados['endereco'],
                                        dados['anunciante']
                                ))

                                conexao.commit()

                                self.send_response(201)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "mensagem": "Usuário cadastrado com sucesso"
                                }).encode('utf-8'))

                        except sqlite3.IntegrityError:
                                self.send_response(400)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "erro": "Nome, E-mail ou Telefone já cadastrado"
                                }).encode('utf-8'))

                        finally:
                                conexao.close()

                elif self.path == '/api/carrinho':
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        dados = json.loads(post_data.decode('utf-8'))

                        conexao = sqlite3.connect(NOME_BANCO)
                        cursor = conexao.cursor()

                        try:
                                cursor.execute('''
                                        INSERT INTO itens_carrinho
                                        (id_carrinho, id_produto, quantidade)
                                        VALUES (?, ?, ?)
                                ''', (
                                        dados['id_carrinho'],
                                        dados['id_produto'],
                                        dados['quantidade']
                                ))

                                conexao.commit()

                                self.send_response(201)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "mensagem": "Produto adicionado ao carrinho"
                                }).encode('utf-8'))

                        except Exception as e:
                                self.send_response(400)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "erro": str(e)
                                }).encode('utf-8'))

                        finally:
                                conexao.close()

                elif self.path == '/api/pedidos':
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        dados = json.loads(post_data.decode('utf-8'))

                        conexao = sqlite3.connect(NOME_BANCO)
                        cursor = conexao.cursor()

                        try:
                                cursor.execute('''
                                        INSERT INTO pedidos
                                        (id_usuario, valor_total, status)
                                        VALUES (?, ?, ?)
                                ''', (
                                        dados['id_usuario'],
                                        dados['valor_total'],
                                        dados.get('status', 'Pendente')
                                ))

                                id_pedido = cursor.lastrowid

                                for item in dados['itens']:
                                        cursor.execute('''
                                        INSERT INTO itens_pedido
                                        (id_pedido, id_produto, quantidade, preco_unidade)
                                        VALUES (?, ?, ?, ?)
                                        ''', (
                                        id_pedido,
                                        item['id_produto'],
                                        item['quantidade'],
                                        item['preco']
                                        ))

                                conexao.commit()

                                self.send_response(201)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "mensagem": "Pedido criado com sucesso"
                                }).encode('utf-8'))

                        except Exception as e:
                                self.send_response(400)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "erro": str(e)
                                }).encode('utf-8'))

                        finally:
                                conexao.close()


        def do_DELETE(self):
                if self.path.startswith('/api/usuarios/'):
                        try:
                                id_usuario = int(self.path.split('/')[-1])

                                conexao = sqlite3.connect(NOME_BANCO)
                                cursor = conexao.cursor()

                                cursor.execute(
                                        'DELETE FROM usuarios WHERE id_usuario = ?',
                                        (id_usuario,)
                                )

                                conexao.commit()

                                if cursor.rowcount == 0:
                                        self.send_response(404)
                                        resposta = {"erro": "Usuário não encontrado"}
                                else:
                                        self.send_response(200)
                                        resposta = {"mensagem": "Usuário deletado com sucesso"}

                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps(resposta).encode('utf-8'))

                        except Exception as e:
                                self.send_response(500)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "erro": str(e)
                                }).encode('utf-8'))

                        finally:
                                conexao.close()

                elif self.path.startswith('/api/carrinho/'):
                        try:
                                id_item = int(self.path.split('/')[-1])

                                conexao = sqlite3.connect(NOME_BANCO)
                                cursor = conexao.cursor()

                                cursor.execute(
                                        'DELETE FROM itens_carrinho WHERE id_itens_carrinho = ?',
                                        (id_item,)
                                )

                                conexao.commit()

                                if cursor.rowcount == 0:
                                        self.send_response(404)
                                        resposta = {"erro": "Item não encontrado"}
                                else:
                                        self.send_response(200)
                                        resposta = {"mensagem": "Item removido do carrinho"}

                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps(resposta).encode('utf-8'))

                        except Exception as e:
                                self.send_response(500)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "erro": str(e)
                                }).encode('utf-8'))

                        finally:
                                conexao.close()

                elif self.path.startswith('/api/pedidos/'):
                        try:
                                id_pedido = int(self.path.split('/')[-1])

                                conexao = sqlite3.connect(NOME_BANCO)
                                cursor = conexao.cursor()

                                cursor.execute(
                                        'DELETE FROM pedidos WHERE id_pedidos = ?',
                                        (id_pedido,)
                                )

                                conexao.commit()

                                if cursor.rowcount == 0:
                                        self.send_response(404)
                                        resposta = {"erro": "Pedido não encontrado"}
                                else:
                                        self.send_response(200)
                                        resposta = {"mensagem": "Pedido removido com sucesso"}

                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps(resposta).encode('utf-8'))

                        except Exception as e:
                                self.send_response(500)
                                self.send_header('Content-Type', 'application/json')
                                self.send_header('Access-Control-Allow-Origin', '*')
                                self.end_headers()

                                self.wfile.write(json.dumps({
                                        "erro": str(e)
                                }).encode('utf-8'))

                        finally:
                                conexao.close()

        def do_OPTIONS(self):
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()

def iniciar_servidor(porta=8000):
        configurar_banco()
        endereco = ('', porta)
        servidor = HTTPServer(endereco, NitroAPI)
        print(f'Servidor rodando na porta {porta} com SQLite.')
        print(f'Teste os dados em: http://localhost:{porta}/api/usuarios')

        try:
                servidor.serve_forever()
        except KeyboardInterrupt:
                pass

        servidor.server_close()
        print('\nServidor encerrado.')

if __name__ == '__main__':
        iniciar_servidor()