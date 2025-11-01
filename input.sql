-- Sample SQL queries for testing the lexer
# This is a multi-line comment
  demonstrating comment handling #

SELECT name, age FROM students WHERE age > 18;

INSERT INTO employees VALUES ('John Doe', 30, 50000.50);

UPDATE products SET price = 99.99 WHERE id = 1;

DELETE FROM orders WHERE status = 'cancelled';

CREATE TABLE users (
    id INT,
    username TEXT,
    email TEXT
);

-- Test case sensitivity
select * FROM Users; -- 'select' is not recognized as keyword

-- Test invalid characters
SELECT @ FROM table1; -- @ is invalid

-- Test unclosed string
SELECT name FROM test WHERE desc = 'unclosed;
