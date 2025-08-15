#!/usr/bin/env python3
"""
Script para criar dados de teste no SQLite
"""
import sqlite3
import os

# Remover arquivo existente se houver
if os.path.exists('./test.db'):
    os.remove('./test.db')

# Conectar ao SQLite
conn = sqlite3.connect('./test.db')
cursor = conn.cursor()

# Criar tabelas
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
)
''')

cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
''')

cursor.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

# Inserir dados de teste
# Usuários
users = [
    ('João Silva', 'joao@email.com', 30),
    ('Maria Santos', 'maria@email.com', 25),
    ('Pedro Costa', 'pedro@email.com', 35)
]
cursor.executemany('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', users)

# Categorias
categories = [
    ('Eletrônicos', 'Dispositivos eletrônicos em geral'),
    ('Livros', 'Livros físicos e digitais'),
    ('Roupas', 'Vestuário e acessórios')
]
cursor.executemany('INSERT INTO categories (name, description) VALUES (?, ?)', categories)

# Produtos
products = [
    ('Smartphone Samsung', 'Smartphone Android última geração', 1200.00, 1),
    ('Notebook Dell', 'Notebook para trabalho e estudos', 2500.00, 1),
    ('Python Programming', 'Livro sobre programação Python', 89.90, 2),
    ('Camiseta Polo', 'Camiseta polo algodão azul', 59.90, 3),
    ('Calça Jeans', 'Calça jeans masculina slim fit', 129.90, 3)
]
cursor.executemany('INSERT INTO products (name, description, price, category_id) VALUES (?, ?, ?, ?)', products)

# Pedidos
orders = [
    (1, 1200.00, 'concluido'),
    (2, 2589.90, 'processando'),
    (3, 189.80, 'concluido')
]
cursor.executemany('INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)', orders)

# Itens do pedido
order_items = [
    (1, 1, 1, 1200.00),  # João comprou Samsung
    (2, 2, 1, 2500.00),  # Maria comprou Dell
    (2, 3, 1, 89.90),    # Maria comprou livro Python
    (3, 4, 1, 59.90),    # Pedro comprou camiseta
    (3, 5, 1, 129.90)    # Pedro comprou calça
]
cursor.executemany('INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)', order_items)

# Confirmar e fechar
conn.commit()
conn.close()

print("Base de dados SQLite criada com sucesso!")
print("5 tabelas criadas: users, categories, products, orders, order_items")
print("Dados de teste inseridos: 3 usuários, 3 categorias, 5 produtos, 3 pedidos")
