-- Valid SQL statements for testing

-- Simple SELECT
SELECT name, age FROM users;

-- SELECT with WHERE
SELECT * FROM products WHERE price > 100;

-- INSERT statement
INSERT INTO customers VALUES ('Alice', 30, 'alice@email.com');

-- UPDATE statement
UPDATE inventory SET quantity = 50 WHERE id = 1;

-- DELETE statement
DELETE FROM orders WHERE status = 'cancelled';

-- CREATE TABLE
CREATE TABLE employees (
    id INT,
    name TEXT,
    salary FLOAT
);

-- Complex WHERE with AND/OR
SELECT * FROM items WHERE price > 10 AND stock <= 100 OR discount > 0;

-- Expression in SELECT
SELECT price * 1.1, quantity + 5 FROM products;
