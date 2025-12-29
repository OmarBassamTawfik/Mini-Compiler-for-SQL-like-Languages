KEYWORDS = {'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 
            'DELETE', 'CREATE', 'TABLE', 'INT', 'FLOAT', 'TEXT', 'AND', 'OR', 'NOT'}

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.errors = []
        self.symbols = {}
    
    def current(self):
        return self.code[self.pos] if self.pos < len(self.code) else None
    
    def peek(self):
        return self.code[self.pos + 1] if self.pos + 1 < len(self.code) else None
    
    def advance(self):
        if self.pos < len(self.code):
            if self.code[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.current() and self.current() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        if self.current() == '-' and self.peek() == '-':
            self.advance()
            self.advance()
            while self.current() and self.current() != '\n':
                self.advance()
            return
        
        if self.current() == '/' and self.peek() == '*':
            start_line, start_col = self.line, self.col
            self.advance()
            self.advance()
            while self.current():
                if self.current() == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    return
                self.advance()
            self.errors.append(f"Error: unclosed comment starting at line {start_line}, column {start_col}.")
            return
        
        if self.current() == '#' and self.peek() == '#':
            start_line, start_col = self.line, self.col
            self.advance()
            self.advance()
            while self.current():
                if self.current() == '#' and self.peek() == '#':
                    self.advance()
                    self.advance()
                    return
                self.advance()
            self.errors.append(f"Error: unclosed comment starting at line {start_line}, column {start_col}.")
            return

        if self.current() == '#':
            self.advance()
            while self.current() and self.current() != '\n':
                self.advance()
            return
    
    def read_string(self):
        start_line, start_col = self.line, self.col
        value = ""
        self.advance()
        while self.current():
            if self.current() == "'":
                if self.peek() == "'":
                    value += "'"
                    self.advance()
                    self.advance()
                else:
                    self.advance()
                    return ('STRING_LITERAL', value, start_line, start_col)
            else:
                value += self.current()
                self.advance()
        self.errors.append(f"Error: unclosed string starting at line {start_line}, column {start_col}.")
        return ('STRING_LITERAL', value, start_line, start_col)
    
    def read_number(self):
        start_line, start_col = self.line, self.col
        value = ""
        has_dot = False
        while self.current() and (self.current().isdigit() or self.current() == '.'):
            if self.current() == '.':
                if has_dot:
                    break
                has_dot = True
            value += self.current()
            self.advance()
        return ('NUMBER_LITERAL', value, start_line, start_col)
    
    def read_word(self):
        start_line, start_col = self.line, self.col
        value = ""
        while self.current() and (self.current().isalnum() or self.current() == '_'):
            value += self.current()
            self.advance()
        
        if value in KEYWORDS:
            return (value, value, start_line, start_col)
        else:
            if value.upper() in KEYWORDS:
                self.errors.append(f"Error: keyword '{value.upper()}' must be uppercase at line {start_line}, column {start_col}.")
            
            if value not in self.symbols:
                self.symbols[value] = {'line': start_line, 'col': start_col, 'count': 0}
            self.symbols[value]['count'] += 1
            return ('IDENTIFIER', value, start_line, start_col)
    
    def tokenize(self):
        operators = {'+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE', 
                    '%': 'MODULO', '=': 'EQUAL', '<': 'LESS_THAN', '>': 'GREATER_THAN', 
                    '(': 'LPAREN', ')': 'RPAREN', ',': 'COMMA', ';': 'SEMICOLON', '.': 'DOT'}
        
        while self.current():
            if self.current() in ' \t\n\r':
                self.skip_whitespace()
            elif self.current() == '-' and self.peek() == '-':
                self.skip_comment()
            elif self.current() == '/' and self.peek() == '*':
                self.skip_comment()
            elif self.current() == '#':
                self.skip_comment()
            elif self.current() == "'":
                self.tokens.append(self.read_string())
            elif self.current().isdigit():
                self.tokens.append(self.read_number())
            elif self.current().isalpha() or self.current() == '_':
                self.tokens.append(self.read_word())
            else:
                char = self.current()
                line, col = self.line, self.col
                
                if char == '!' and self.peek() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(('NOT_EQUAL', '!=', line, col))
                elif char == '<' and self.peek() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(('LESS_EQUAL', '<=', line, col))
                elif char == '>' and self.peek() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(('GREATER_EQUAL', '>=', line, col))
                elif char in operators:
                    self.tokens.append((operators[char], char, line, col))
                    self.advance()
                else:
                    self.errors.append(f"Error: invalid character '{char}' at line {line}, column {col}.")
                    self.advance()
        return self.tokens
    