import sqlite3

conn = sqlite3.connect('./test.db')
cursor = conn.cursor()

# Listar tabelas
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print(f'Tabelas: {tables}')

# Contar registros
cursor.execute('SELECT COUNT(*) FROM users')
print(f'Usuários: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM products')
print(f'Produtos: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM orders')
print(f'Pedidos: {cursor.fetchone()[0]}')

conn.close()
