-- LEXICAL ERROR: Invalid character '@'
SELECT @ FROM users;

-- LEXICAL ERROR: Lowercase keyword
select * FROM products;

-- SYNTAX ERROR: Missing FROM keyword
SELECT name, age employees WHERE id = 1;

-- SYNTAX ERROR: Missing VALUES keyword
INSERT INTO items (1, 'Widget', 19.99);

-- SEMANTIC ERROR: Table not declared
INSERT INTO nonexistent VALUES (1, 'test');

-- Create table for semantic testing
CREATE TABLE test_table (
    id INT,
    name TEXT
);

-- SEMANTIC ERROR: Type mismatch (TEXT column gets NUMBER)
INSERT INTO test_table VALUES (123, 456);

-- SEMANTIC ERROR: Column doesn't exist
SELECT age FROM test_table;

-- LEXICAL ERROR: Unclosed string
SELECT name FROM test_table WHERE name = 'unclosed;

-- SYNTAX ERROR: Missing semicolon and incomplete statement
UPDATE test_table SET
