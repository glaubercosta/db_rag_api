-- Script de inicialização MySQL
-- Cria tabelas de exemplo para demonstração

-- Tabela de usuários
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de categorias
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Tabela de produtos
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Tabela de pedidos
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de itens do pedido
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Inserir dados de exemplo
INSERT INTO categories (name, description) VALUES
('Eletrônicos', 'Dispositivos eletrônicos em geral'),
('Livros', 'Livros físicos e digitais'),
('Roupas', 'Vestuário e acessórios');

INSERT INTO users (name, email, age) VALUES
('João Silva', 'joao@email.com', 30),
('Maria Santos', 'maria@email.com', 25),
('Pedro Costa', 'pedro@email.com', 35);

INSERT INTO products (name, description, price, category_id) VALUES
('Smartphone', 'Smartphone Android', 899.99, 1),
('Laptop', 'Laptop para trabalho', 2499.99, 1),
('Livro de Python', 'Guia completo de Python', 59.99, 2),
('Camiseta', 'Camiseta 100% algodão', 29.99, 3);

INSERT INTO orders (user_id, total_amount, status) VALUES
(1, 959.98, 'completed'),
(2, 2499.99, 'pending'),
(3, 89.98, 'completed');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 899.99),
(1, 2, 2, 29.99),
(2, 2, 1, 2499.99),
(3, 3, 1, 59.99),
(3, 4, 1, 29.99);
