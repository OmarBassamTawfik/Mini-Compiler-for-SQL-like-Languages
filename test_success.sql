-- Create employee database tables
CREATE TABLE employees (
    id INT,
    name TEXT,
    age INT,
    salary FLOAT
);

CREATE TABLE departments (
    dept_id INT,
    dept_name TEXT,
    budget FLOAT
);

-- Insert employee records
INSERT INTO employees VALUES (1, 'Alice Johnson', 30, 75000.50);
INSERT INTO employees VALUES (2, 'Bob Smith', 25, 60000.00);
INSERT INTO employees VALUES (3, 'Carol White', 35, 85000.75);

-- Insert department records
INSERT INTO departments VALUES (10, 'Engineering', 500000.00);
INSERT INTO departments VALUES (20, 'Sales', 300000.00);

-- Query employees
SELECT name, age, salary FROM employees WHERE age >= 25;
SELECT * FROM employees WHERE salary > 70000.00;

-- Update employee data
UPDATE employees SET salary = 80000.00 WHERE id = 1;
UPDATE employees SET age = 26 WHERE id = 2;

-- Query departments
SELECT dept_name, budget FROM departments WHERE budget > 400000.00;

-- Clean up old records
DELETE FROM employees WHERE age < 20;
DELETE FROM departments WHERE budget = 0;
