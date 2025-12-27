-- LEXICAL ERROR #1: Invalid character '@'
SELECT @ FROM users;

-- LEXICAL ERROR #2: Invalid character '&'
SELECT name & age FROM products;

-- LEXICAL ERROR #3: Lowercase keyword 'select'
select * FROM customers;

-- LEXICAL ERROR #4: Lowercase keyword 'where'
SELECT id FROM orders where status = 'active';

-- LEXICAL ERROR #5: Unclosed string literal
SELECT name FROM employees WHERE name = 'John;

-- LEXICAL ERROR #6: Unclosed multi-line comment
/* This is an unclosed comment
SELECT * FROM test;

-- LEXICAL ERROR #7: Invalid character '#' used incorrectly
SELECT price # discount FROM items;
