import sys
from lexer import Lexer

class ParseNode:
    def __init__(self, name, value=None, children=None):
        self.name, self.value, self.children = name, value, children if children else []
    def add_child(self, child):
        self.children.append(child)
    def __repr__(self):
        return f"{self.name}({self.value})" if self.value else self.name

class Parser:
    def __init__(self, tokens):
        self.tokens, self.pos, self.errors, self.parse_tree = tokens, 0, [], None
        self.sync_tokens = {'SEMICOLON', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE'}
    
    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def peek(self, offset=1):
        return self.tokens[self.pos + offset] if self.pos + offset < len(self.tokens) else None
    
    def advance(self):
        self.pos += 1
    
    def expect(self, expected_type):
        token = self.current()
        if token and token[0] == expected_type:
            self.advance()
            return token
        if token:
            self.errors.append(f"Syntax Error: Expected '{expected_type}' at line {token[2]}, column {token[3]}, but found '{token[1]}'.")
        else:
            self.errors.append(f"Syntax Error: Expected '{expected_type}', but reached end of input.")
        return None
    
    def synchronize(self):
        while self.current():
            if self.current()[0] in self.sync_tokens:
                if self.current()[0] == 'SEMICOLON':
                    self.advance()
                return
            self.advance()
    
    def add_token_node(self, node, token_type, display_name=None):
        if (t := self.expect(token_type)):
            node.add_child(ParseNode(display_name or token_type, t[1] if token_type == 'IDENTIFIER' else display_name or token_type))
    
    def parse(self):
        self.parse_tree = ParseNode("Query")
        while self.current() and self.current()[0] in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']:
            try:
                if stmt := self.parse_statement():
                    self.parse_tree.add_child(stmt)
            except Exception as e:
                token = self.current()
                if token:
                    self.errors.append(f"Syntax Error: Unexpected error at line {token[2]}, column {token[3]}: {str(e)}")
                self.synchronize()
        if self.pos < len(self.tokens):
            t = self.current()
            if t[0] not in self.sync_tokens:
                self.errors.append(f"Syntax Error: Unexpected token '{t[1]}' at line {t[2]}, column {t[3]}.")
        return self.parse_tree
    
    def parse_statement(self):
        node, token = ParseNode("Statement"), self.current()
        if not token:
            return None
        stmt_map = {'CREATE': self.parse_create, 'INSERT': self.parse_insert, 
                    'SELECT': self.parse_select, 'UPDATE': self.parse_update, 'DELETE': self.parse_delete}
        if token[0] in stmt_map:
            if stmt := stmt_map[token[0]]():
                node.add_child(stmt)
        else:
            self.errors.append(f"Syntax Error: Unexpected statement starting with '{token[1]}' at line {token[2]}, column {token[3]}.")
            self.synchronize()
            return None
        if not self.expect('SEMICOLON'):
            self.synchronize()
            return node
        node.add_child(ParseNode("SEMICOLON", ";"))
        return node
    
    def parse_create(self):
        node = ParseNode("CreateStmt")
        self.add_token_node(node, 'CREATE', 'CREATE')
        self.add_token_node(node, 'TABLE', 'TABLE')
        self.add_token_node(node, 'IDENTIFIER')
        self.add_token_node(node, 'LPAREN', 'LEFT_PAREN')
        node.add_child(self.parse_column_list())
        self.add_token_node(node, 'RPAREN', 'RIGHT_PAREN')
        return node
    
    def parse_column_list(self):
        node = ParseNode("ColumnList")
        node.add_child(self.parse_column_def())
        while self.current() and self.current()[0] == 'COMMA':
            self.advance()
            node.add_child(ParseNode("COMMA", ","))
            node.add_child(self.parse_column_def())
        return node
    
    def parse_column_def(self):
        node = ParseNode("ColumnDef")
        self.add_token_node(node, 'IDENTIFIER')
        if (t := self.current()) and t[0] in ['INT', 'FLOAT', 'TEXT']:
            self.advance()
            node.add_child(ParseNode("DataType", t[0]))
        else:
            if t:
                self.errors.append(f"Syntax Error: Expected data type (INT, FLOAT, or TEXT) at line {t[2]}, column {t[3]}, but found '{t[1]}'.")
            else:
                self.errors.append(f"Syntax Error: Expected data type (INT, FLOAT, or TEXT), but reached end of input.")
        return node
    
    def parse_insert(self):
        node = ParseNode("InsertStmt")
        self.add_token_node(node, 'INSERT', 'INSERT')
        self.add_token_node(node, 'INTO', 'INTO')
        self.add_token_node(node, 'IDENTIFIER')
        self.add_token_node(node, 'VALUES', 'VALUES')
        self.add_token_node(node, 'LPAREN', 'LEFT_PAREN')
        node.add_child(self.parse_value_list())
        self.add_token_node(node, 'RPAREN', 'RIGHT_PAREN')
        return node
    
    def parse_value_list(self):
        node = ParseNode("ValueList")
        if (t := self.current()) and t[0] in ['STRING_LITERAL', 'NUMBER_LITERAL']:
            self.advance()
            node.add_child(ParseNode("Value", f"{t[0]}:{t[1]}"))
        while self.current() and self.current()[0] == 'COMMA':
            self.advance()
            node.add_child(ParseNode("COMMA", ","))
            if (t := self.current()) and t[0] in ['STRING_LITERAL', 'NUMBER_LITERAL']:
                self.advance()
                node.add_child(ParseNode("Value", f"{t[0]}:{t[1]}"))
        return node
    
    def parse_select(self):
        node = ParseNode("SelectStmt")
        self.add_token_node(node, 'SELECT', 'SELECT')
        node.add_child(self.parse_select_list())
        self.add_token_node(node, 'FROM', 'FROM')
        self.add_token_node(node, 'IDENTIFIER')
        if self.current() and self.current()[0] == 'WHERE':
            node.add_child(self.parse_where())
        return node
    
    def parse_select_list(self):
        node = ParseNode("SelectList")
        if self.current() and self.current()[0] == 'MULTIPLY':
            self.advance()
            node.add_child(ParseNode("MULTIPLY", "*"))
        else:
            node.add_child(self.parse_expr_list())
        return node
    
    def parse_expr_list(self):
        node = ParseNode("ExpressionList")
        node.add_child(self.parse_expression())
        while self.current() and self.current()[0] == 'COMMA':
            self.advance()
            node.add_child(ParseNode("COMMA", ","))
            node.add_child(self.parse_expression())
        return node
    
    def parse_expression(self):
        node = ParseNode("Expression")
        node.add_child(self.parse_term())
        while self.current() and self.current()[0] in ['PLUS', 'MINUS']:
            op = self.current()
            self.advance()
            node.add_child(ParseNode(op[0], op[1]))
            node.add_child(self.parse_term())
        return node
    
    def parse_term(self):
        node = ParseNode("Term")
        node.add_child(self.parse_factor())
        while self.current() and self.current()[0] in ['MULTIPLY', 'DIVIDE', 'MODULO']:
            op = self.current()
            self.advance()
            node.add_child(ParseNode(op[0], op[1]))
            node.add_child(self.parse_factor())
        return node
    
    def parse_factor(self):
        token = self.current()
        if not token:
            self.errors.append("Syntax Error: Expected factor (identifier, number, string, or parenthesized expression), but reached end of input.")
            return ParseNode("Factor", "ERROR")
        if token[0] in ['IDENTIFIER', 'NUMBER_LITERAL', 'STRING_LITERAL']:
            self.advance()
            type_map = {'IDENTIFIER': 'IDENTIFIER', 'NUMBER_LITERAL': 'NUMBER', 'STRING_LITERAL': 'STRING'}
            return ParseNode("Factor", f"{type_map[token[0]]}:{token[1]}")
        elif token[0] == 'LPAREN':
            node = ParseNode("Factor")
            self.advance()
            node.add_child(ParseNode("LPAREN", "("))
            node.add_child(self.parse_expression())
            if self.expect('RPAREN'):
                node.add_child(ParseNode("RPAREN", ")"))
            return node
        self.errors.append(f"Syntax Error: Expected factor (identifier, number, string, or '(') at line {token[2]}, column {token[3]}, but found '{token[1]}'.")
        return ParseNode("Factor", "ERROR")
    
    def parse_update(self):
        node = ParseNode("UpdateStmt")
        self.add_token_node(node, 'UPDATE', 'UPDATE')
        self.add_token_node(node, 'IDENTIFIER')
        self.add_token_node(node, 'SET', 'SET')
        node.add_child(self.parse_assignment_list())
        if self.current() and self.current()[0] == 'WHERE':
            node.add_child(self.parse_where())
        return node
    
    def parse_assignment_list(self):
        node = ParseNode("AssignmentList")
        node.add_child(self.parse_assignment())
        while self.current() and self.current()[0] == 'COMMA':
            self.advance()
            node.add_child(ParseNode("COMMA", ","))
            node.add_child(self.parse_assignment())
        return node
    
    def parse_assignment(self):
        node = ParseNode("Assignment")
        self.add_token_node(node, 'IDENTIFIER')
        self.add_token_node(node, 'EQUAL', 'EQUAL')
        node.add_child(self.parse_expression())
        return node
    
    def parse_delete(self):
        node = ParseNode("DeleteStmt")
        self.add_token_node(node, 'DELETE', 'DELETE')
        self.add_token_node(node, 'FROM', 'FROM')
        self.add_token_node(node, 'IDENTIFIER')
        if self.current() and self.current()[0] == 'WHERE':
            node.add_child(self.parse_where())
        return node
    
    def parse_where(self):
        node = ParseNode("WhereClause")
        self.add_token_node(node, 'WHERE', 'WHERE')
        node.add_child(self.parse_condition())
        return node
    
    def parse_condition(self):
        node = ParseNode("Condition")
        node.add_child(self.parse_and_condition())
        while self.current() and self.current()[0] == 'OR':
            self.advance()
            node.add_child(ParseNode("OR", "OR"))
            node.add_child(self.parse_and_condition())
        return node
    
    def parse_and_condition(self):
        node = ParseNode("AndCondition")
        node.add_child(self.parse_not_condition())
        while self.current() and self.current()[0] == 'AND':
            self.advance()
            node.add_child(ParseNode("AND", "AND"))
            node.add_child(self.parse_not_condition())
        return node
    
    def parse_not_condition(self):
        node = ParseNode("NotCondition")
        if self.current() and self.current()[0] == 'NOT':
            self.advance()
            node.add_child(ParseNode("NOT", "NOT"))
            if self.current() and self.current()[0] == 'IDENTIFIER':
                next_tok = self.peek()
                if next_tok and next_tok[0] not in ['EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL']:
                    t = self.current()
                    self.advance()
                    node.add_child(ParseNode("BooleanExpr", f"IDENTIFIER:{t[1]}"))
                    return node
        node.add_child(self.parse_comparison())
        return node
    
    def parse_comparison(self):
        node = ParseNode("Comparison")
        node.add_child(self.parse_expression())
        if (t := self.current()) and t[0] in ['EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL']:
            self.advance()
            node.add_child(ParseNode("ComparisonOp", t[1]))
        elif t:
            self.errors.append(f"Syntax Error: Expected comparison operator (=, !=, <, >, <=, >=) at line {t[2]}, column {t[3]}, but found '{t[1]}'.")
        else:
            self.errors.append(f"Syntax Error: Expected comparison operator (=, !=, <, >, <=, >=), but reached end of input.")
        node.add_child(self.parse_expression())
        return node
    
    def print_tree(self, node=None, prefix=""):
        if node is None:
            node = self.parse_tree
        if node is None:
            return
        print(node if not prefix else prefix + str(node))
        for i, child in enumerate(node.children):
            is_last = (i == len(node.children) - 1)
            new_prefix = ("├── " if not is_last else "└── ") if not prefix else prefix + ("├── " if not is_last else "└── ")
            next_prefix = ("│   " if not is_last else "    ") if not prefix else prefix + ("│   " if not is_last else "    ")
            print(new_prefix + str(child))
            self._print_subtree(child, next_prefix)
    
    def _print_subtree(self, node, prefix):
        for i, child in enumerate(node.children):
            is_last = (i == len(node.children) - 1)
            print(prefix + ("├── " if not is_last else "└── ") + str(child))
            self._print_subtree(child, prefix + ("│   " if not is_last else "    "))
