-- SYNTAX ERROR #1: Missing FROM keyword
SELECT name, age employees WHERE id = 1;

-- SYNTAX ERROR #2: Missing VALUES keyword
INSERT INTO users (1, 'Alice', 25);

-- SYNTAX ERROR #3: Missing semicolon
SELECT * FROM products

-- SYNTAX ERROR #4: Double comma
SELECT id,, name FROM customers;

-- SYNTAX ERROR #5: Missing closing parenthesis
CREATE TABLE test (id INT, name TEXT;

-- SYNTAX ERROR #6: Missing column definition
CREATE TABLE items (id INT, name);

-- SYNTAX ERROR #7: Missing WHERE keyword (SET followed by nothing proper)
UPDATE products SET price = 99.99 id = 1;

-- SYNTAX ERROR #8: Missing FROM in DELETE
DELETE orders WHERE status = 'cancelled';

-- SYNTAX ERROR #9: Empty SELECT list
SELECT FROM users;

-- SYNTAX ERROR #10: Missing expression after operator
SELECT price + FROM products;
