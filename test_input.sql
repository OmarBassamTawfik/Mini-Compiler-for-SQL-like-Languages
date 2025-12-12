/* Multi-line comment
  with multiple lines
  testing comment handling */

-- Test 1: SELECT with WHERE clause
SELECT name, age, salary FROM employees WHERE age >= 18 AND salary > 50000.50;

-- Test 2: INSERT with string literals
INSERT INTO users VALUES ('John Doe', 25, 'john@email.com');

-- Test 3: String with escaped quotes
INSERT INTO messages VALUES ('It''s a beautiful day', 'O''Brien');

-- Test 4: UPDATE with multiple conditions
UPDATE products SET price = 99.99, stock = 100 WHERE id = 1 OR id = 2;

-- Test 5: DELETE operation
DELETE FROM orders WHERE status = 'cancelled' AND date < '2024-01-01';

-- Test 6: CREATE TABLE with types
CREATE TABLE customers (
    id INT,
    name TEXT,
    balance FLOAT,
    active INT
);

-- Test 7: Complex expression with operators
SELECT price * 1.2 + 5, quantity % 10, (price - discount) / 2 FROM products;

-- Test 8: NOT and comparison operators
SELECT * FROM items WHERE NOT deleted AND price != 0 AND stock <= 100;

-- Test 9: Identifiers with underscores
SELECT user_id, first_name, last_name FROM user_table;

-- Test 10: Number literals (integers and floats)
SELECT 42, 3.14, 0.5, 100.0, 999 FROM test;

-- ERROR TEST 1: Invalid character
SELECT @ FROM table1;

-- ERROR TEST 2: Case Sensitive
select * FROM Users;

-- ERROR TEST 3: Unclosed string
SELECT name FROM test WHERE desc = 'unclosed;

-- ERROR TEST 4: Unclosed multi-line comment
/* This comment never closes
SELECT * FROM broken;
