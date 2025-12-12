# SQL-Like Language Compiler

A two-phase compiler implementation for a SQL-like language, featuring lexical analysis and syntax analysis with comprehensive error handling and recovery.

## Project Structure

```
.
├── lexer.py          # Phase 1: Lexical Analyzer
├── parser.py         # Phase 2: Syntax Analyzer (Parser)
├── compiler.py       # Web-based compiler interface
├── test_input.sql    # Test file with lexical errors
├── test_valid.sql    # Test file with valid SQL
├── test_errors.sql   # Test file for syntax error recovery
└── README.md         # This file
```

## Features

### Phase 1: Lexical Analyzer (`lexer.py`)
- Tokenizes SQL-like language statements
- Supports keywords: SELECT, FROM, WHERE, INSERT, INTO, VALUES, UPDATE, SET, DELETE, CREATE, TABLE, INT, FLOAT, TEXT, AND, OR, NOT
- Handles operators: +, -, *, /, %, =, !=, <, >, <=, >=
- Supports comments: 
  - Single-line: `--`, `#`
  - Multi-line: `/* */`, `## ##`
- String literals with single quotes (supports escape with `''`)
- Number literals (integers and floats)
- Identifiers with symbol table tracking
- Comprehensive error reporting

### Phase 2: Syntax Analyzer (`parser.py`)
- Recursive descent parser with comprehensive error handling
- Generates parse trees for valid SQL statements
- **Advanced Error Handling:**
  - Detects misplaced, unexpected, or missing tokens
  - Reports errors with line number, column number, and descriptive messages
  - Implements panic mode error recovery to detect multiple errors in single run
  - Synchronizes on SEMICOLON and major keywords (CREATE, INSERT, SELECT, UPDATE, DELETE)
  - Continues parsing after errors to find all syntax issues
- Supports all major SQL operations:
  - CREATE TABLE with column definitions
  - INSERT INTO with value lists
  - SELECT with expressions and WHERE clauses
  - UPDATE with SET assignments and WHERE clauses
  - DELETE with WHERE clauses
- Expression parsing with operator precedence:
  - Arithmetic: +, -, *, /, %
  - Comparison: =, !=, <, >, <=, >=
  - Logical: AND, OR, NOT
- Detailed syntax error reporting with "expected vs found" format

### Grammar Supported

```
Query → Statement | Statement Query
Statement → CreateStmt SEMICOLON | InsertStmt SEMICOLON | SelectStmt SEMICOLON | UpdateStmt SEMICOLON | DeleteStmt SEMICOLON
CreateStmt → CREATE TABLE IDENTIFIER LEFT_PAREN ColumnList RIGHT_PAREN
InsertStmt → INSERT INTO IDENTIFIER VALUES LEFT_PAREN ValueList RIGHT_PAREN
SelectStmt → SELECT SelectList FROM IDENTIFIER WhereClause | SELECT SelectList FROM IDENTIFIER
UpdateStmt → UPDATE IDENTIFIER SET AssignmentList WHERE Condition
DeleteStmt → DELETE FROM IDENTIFIER WHERE Condition
WhereClause → WHERE Condition
```

## Usage

Run the web-based compiler:
```bash
python compiler.py
```

Then open `http://localhost:8080` in your browser. 

### Features:
- Load SQL files from dropdown menu
- Run analysis with one click
- View results in separate tabs (Source, Lexical Analysis, Syntax Analysis, Summary)
- Beautiful modern interface with syntax highlighting
- **No external dependencies needed** - uses only Python standard library
- Test multiple files without restarting

## Examples

### Valid SQL Example
```sql
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
```

## Output

### Lexer Output
- Token stream with type, lexeme, line, and column
- Symbol table with identifier information
- Lexical errors (if any)
- Summary statistics

### Parser Output
- Lexical errors (if any)
- Syntax errors (if any)
- Parse tree showing the hierarchical structure
- Parsing status and statistics

### Compiler Output
- Phase 1: Lexical analysis results
- Phase 2: Syntax analysis results
- Complete parse tree
- Compilation summary with success/failure status

## Error Handling

The compiler detects and reports errors with comprehensive information:

### Lexical Errors:
- Invalid characters
- Unclosed strings
- Unclosed comments
- Incorrect keyword casing (keywords must be uppercase)

**Example:**
```
Error: invalid character '@' at line 41, column 8.
Error: keyword 'SELECT' must be uppercase at line 44, column 1.
```

### Syntax Errors:
- Missing tokens (e.g., missing FROM, VALUES, parentheses)
- Unexpected tokens (e.g., double commas, wrong keywords)
- Invalid statement structure
- Malformed expressions

**Example:**
```
Syntax Error: Expected 'FROM' at line 4, column 18, but found 'WHERE'.
Syntax Error: Expected factor (identifier, number, string, or '(') at line 16, column 13, but found ','.
```

### Error Recovery:
- **Panic Mode Recovery**: When an error is detected, the parser skips tokens until it finds a synchronization point
- **Synchronization Tokens**: SEMICOLON, SELECT, INSERT, UPDATE, DELETE, CREATE
- **Multiple Error Detection**: Finds all errors in a single compilation pass
- **Partial Parse Trees**: Generates parse trees even when errors are present
- **Continue After Errors**: Parser continues analyzing the rest of the file after recovering from errors

This allows developers to see all issues at once rather than fixing one error at a time.

## Implementation Details

### Architecture
- **Lexer**: Class-based design with tokenization methods
  - `Lexer.__init__()`: Initialize lexer with source code
  - `tokenize()`: Main tokenization method
  - `skip_whitespace()`, `skip_comment()`: Skip non-token characters
  - `read_string()`, `read_number()`, `read_word()`: Token extraction methods
  - Symbol table tracking for identifiers
  
- **Parser**: Recursive descent parser with error recovery
  - `Parser.__init__()`: Initialize with token stream
  - `parse()`: Main parsing entry point with error handling
  - `parse_statement()`: Parse individual statements
  - `parse_create/insert/select/update/delete()`: Statement-specific parsers
  - `parse_expression/term/factor()`: Expression parsing with precedence
  - `parse_condition()`: WHERE clause parsing with AND/OR/NOT
  - `synchronize()`: Error recovery mechanism
  - `expect()`: Token matching with detailed error messages
  
- **Compiler**: Integration of both phases
  - Runs lexical analysis first
  - Passes tokens to parser
  - Displays comprehensive results
  - No standalone execution in lexer/parser (library modules only)

### Code Statistics
- `lexer.py`: 169 lines
- `parser.py`: 312 lines (includes error recovery)
- `compiler.py`: 310 lines (web-based GUI)
- **Total**: ~790 lines of code

### Parsing Technique
- **Recursive Descent Parsing**: Each grammar rule is implemented as a method
- **Panic Mode Error Recovery**: Skips to synchronization points after errors
- **Parse Tree Generation**: Hierarchical representation of program structure
- **Error Propagation**: Continues parsing to detect multiple errors

## Testing

Test files are included:
- `test_valid.sql`: Valid SQL statements for successful parsing (8 statements)
- `test_input.sql`: Test cases with lexical errors (163 tokens, 3 lexical errors)
- `test_errors.sql`: Syntax error test cases for error recovery validation (6 syntax errors detected)

Run tests:
```bash
# Use web interface for testing
python compiler.py
# Then open http://localhost:8080 and select test files
```

Expected results:
- `test_valid.sql`: 89 tokens, 0 errors, full parse tree
- `test_input.sql`: 163 tokens, 3 lexical errors (invalid char, lowercase keyword, unclosed string)
- `test_errors.sql`: 55 tokens, 6 syntax errors (missing FROM, missing SEMICOLON, etc.), partial parse tree with error recovery

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Team Members

- Omar Bassam Tawfik
- Mostafa Mohamed Elsheikh
- Yassin Suleiman Hamad
- Kareem Mohamed Tantawi

## Course Information

CSCI415: Compiler Design Project  
Phase 1 & 2: Lexical and Syntax Analysis
