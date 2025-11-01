"""Lexical Analyzer for SQL-like Language - Phase 1"""
import sys

# Keywords (case-sensitive)
KEYWORDS = {'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE', 'INT', 'FLOAT', 'TEXT', 'AND', 'OR', 'NOT'}

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
            while self.current() and self.current() != '\n':
                self.advance()
        elif self.current() == '#':
            start_line, start_col = self.line, self.col
            self.advance()
            while self.current():
                if self.current() == '#':
                    self.advance()
                    return
                self.advance()
            self.errors.append(f"Error: unclosed comment starting at line {start_line}, column {start_col}.")
    
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
        while self.current() and (self.current().isdigit() or self.current() == '.'):
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
            if value not in self.symbols:
                self.symbols[value] = {'line': start_line, 'col': start_col, 'count': 0}
            self.symbols[value]['count'] += 1
            return ('IDENTIFIER', value, start_line, start_col)
    
    def tokenize(self):
        operators = {'+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE', '%': 'MODULO', '=': 'EQUAL', '<': 'LESS_THAN', '>': 'GREATER_THAN', '(': 'LPAREN', ')': 'RPAREN', ',': 'COMMA', ';': 'SEMICOLON', '.': 'DOT'}
        
        while self.current():
            if self.current() in ' \t\n\r':
                self.skip_whitespace()
            elif self.current() == '-' and self.peek() == '-':
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python lexer.py <input_file>")
        return
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    print("="*70)
    print("LEXICAL ANALYZER - SQL-LIKE LANGUAGE")
    print("="*70)
    print(f"Input file: {input_file}")
    print("="*70)
    
    if lexer.errors:
        print("LEXICAL ERRORS")
        print("="*70)
        for error in lexer.errors:
            print(error)
        print("="*70)
    
    print("TOKENS")
    print("="*70)
    print(f"{'Token':<20} {'Lexeme':<20} {'Line':<10} {'Column':<10}")
    print("-"*70)
    for token in tokens:
        print(f"{token[0]:<20} {token[1]:<20} {token[2]:<10} {token[3]:<10}")
    print("="*70)
    
    print("SYMBOL TABLE")
    print("="*70)
    print(f"{'Identifier':<20} {'Type':<15} {'First Seen':<20} {'Count':<10}")
    print("-"*70)
    for name, info in sorted(lexer.symbols.items()):
        print(f"{name:<20} {'IDENTIFIER':<15} Line {info['line']}, Col {info['col']:<10} {info['count']:<10}")
    print("="*70)
    
    print("SUMMARY")
    print("="*70)
    print(f"Total tokens (excluding EOF): {len(tokens)}")
    print(f"Total identifiers: {len(lexer.symbols)}")
    print(f"Total errors: {len(lexer.errors)}")
    print("="*70)

if __name__ == "__main__":
    main()
