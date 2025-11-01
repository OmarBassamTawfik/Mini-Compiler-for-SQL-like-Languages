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

-- EXTRA TESTS ADDED BY MOSTAFA

-- 1) Multi-line ## comment contains keywords inside (should be ignored)
## CREATE TABLE hidden (x INT);
   SELECT hidden_col FROM hidden; ##

-- 2) String with escaped single quote using doubled quote (should be one string)
INSERT INTO quotes VALUES ('O''Connor', 'It''s OK');

-- 3) Float starts with dot (should be handled: .5 or 0.5? If lexer doesn't accept .5, test it)
SELECT 0.5 AS half, .5 AS half2;

-- 4) Identifier with underscore and digits
SELECT employee_1, dept_2 FROM dept_table;

-- 5) Operators together and two-char ops
SELECT * FROM t WHERE a<=10 AND b>=5 AND c<>0 AND d!= 1;

-- 6) Leading plus/minus on numbers
INSERT INTO nums VALUES (+10, -3.14);

-- 7) Edge invalid char near eof
SELECT name FROM users WHERE note = 'done'@

-- 8) Arithmetic expressions
SELECT id, price + 10 * 2 AS total_price FROM products;

-- 9) WHERE clause using arithmetic and logic
SELECT name FROM employees WHERE salary/12 > 2000 AND NOT age < 30;

-- 10) Multiple statements in one line
INSERT INTO test VALUES (1); DELETE FROM test WHERE id=1;

-- 11) Complex nested parentheses
SELECT ((a + b) * (c - d)) AS result FROM calc_table;

-- 12) Float without leading digit (lexer may or may not handle .5, test both)
SELECT .75 AS ratio, 0.25 AS fraction;

-- 13) String with internal space and punctuation
INSERT INTO notes VALUES ('Hello, world! This is SQL.');

-- 14) Using OR operator
SELECT * FROM users WHERE role = 'admin' OR role = 'superuser';
