-- SEMANTIC ERROR #1: Table not declared
SELECT * FROM nonexistent_table;

-- SEMANTIC ERROR #2: INSERT into undeclared table
INSERT INTO undefined_table VALUES (1, 'test');

-- Create a table for remaining semantic tests
CREATE TABLE users (
    id INT,
    name TEXT,
    age INT
);

-- SEMANTIC ERROR #3: Column doesn't exist
SELECT salary FROM users;

-- SEMANTIC ERROR #4: Wrong number of values (table has 3 columns, insert has 2)
INSERT INTO users VALUES (1, 'Alice');

-- SEMANTIC ERROR #5: Type mismatch - TEXT column gets NUMBER
INSERT INTO users VALUES (1, 123, 25);

-- SEMANTIC ERROR #6: Type mismatch - INT column gets FLOAT
INSERT INTO users VALUES (1.5, 'Bob', 30);

-- SEMANTIC ERROR #7: Type mismatch in WHERE - TEXT column compared with NUMBER
SELECT * FROM users WHERE name = 456;

-- SEMANTIC ERROR #8: Type mismatch in WHERE - INT column compared with STRING
SELECT * FROM users WHERE age = 'twenty';

-- Create another table
CREATE TABLE products (
    product_id INT,
    price FLOAT
);

-- SEMANTIC ERROR #9: UPDATE non-existent column
UPDATE products SET discount = 10.00 WHERE product_id = 1;

-- SEMANTIC ERROR #10: Duplicate table declaration
CREATE TABLE users (
    user_id INT,
    email TEXT
);
