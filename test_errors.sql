-- Test file with various syntax errors

-- Missing FROM keyword
SELECT name, age WHERE id = 1;

-- Missing semicolon and has another statement
SELECT * FROM users
INSERT INTO test VALUES (1);

-- Missing closing parenthesis
CREATE TABLE broken (
    id INT,
    name TEXT;

-- Unexpected comma
SELECT name,, age FROM users;

-- Missing VALUES keyword
INSERT INTO users (1, 2, 3);

-- Valid statement after errors
SELECT * FROM valid;
