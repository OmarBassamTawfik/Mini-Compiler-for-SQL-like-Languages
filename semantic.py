class SemanticAnalyzer:
    def __init__(self, parse_tree, tokens):
        self.parse_tree = parse_tree
        self.tokens = tokens
        self.errors = []
        self.symbol_table = {}
        self.token_map = self._build_token_map()
    
    def _build_token_map(self):
        token_map = {}
        for token in self.tokens:
            token_type, value, line, col = token
            if value not in token_map:
                token_map[value] = {'line': line, 'col': col, 'type': token_type}
        return token_map
    
    def get_token_info(self, value):
        if value in self.token_map:
            return self.token_map[value]
        return {'line': 0, 'col': 0, 'type': 'UNKNOWN'}
    
    def analyze(self):
        if not self.parse_tree:
            return self.errors
        
        for stmt_node in self.parse_tree.children:
            if stmt_node.name == "Statement":
                for child in stmt_node.children:
                    if child.name == "CreateStmt":
                        self._process_create(child)
        
        for stmt_node in self.parse_tree.children:
            if stmt_node.name == "Statement":
                for child in stmt_node.children:
                    if child.name == "InsertStmt":
                        self._process_insert(child)
                    elif child.name == "SelectStmt":
                        self._process_select(child)
                    elif child.name == "UpdateStmt":
                        self._process_update(child)
                    elif child.name == "DeleteStmt":
                        self._process_delete(child)
        
        return self.errors
    
    def _process_create(self, node):
        table_name = None
        columns = {}
        
        for child in node.children:
            if child.name == "IDENTIFIER":
                table_name = child.value
                break
        
        if not table_name:
            return
        
        if table_name in self.symbol_table:
            token_info = self.get_token_info(table_name)
            self.errors.append(
                f"Semantic Error: Table '{table_name}' is already declared at line {token_info['line']}, column {token_info['col']}."
            )
            return
        
        for child in node.children:
            if child.name == "ColumnList":
                self._extract_columns(child, columns)
        
        self.symbol_table[table_name] = {'columns': columns}
    
    def _extract_columns(self, node, columns):
        for child in node.children:
            if child.name == "ColumnDef":
                col_name = None
                col_type = None
                
                for subchild in child.children:
                    if subchild.name == "IDENTIFIER":
                        col_name = subchild.value
                    elif subchild.name == "DataType":
                        col_type = subchild.value
                
                if col_name and col_type:
                    if col_type not in ['INT', 'FLOAT', 'TEXT']:
                        token_info = self.get_token_info(col_type)
                        self.errors.append(
                            f"Semantic Error: Invalid data type '{col_type}' at line {token_info['line']}, column {token_info['col']}. Expected INT, FLOAT, or TEXT."
                        )
                    columns[col_name] = col_type
    
    def _process_insert(self, node):
        table_name = None
        values = []

        for child in node.children:
            if child.name == "IDENTIFIER":
                table_name = child.value
                break
        
        if not table_name:
            return
        
        if table_name not in self.symbol_table:
            token_info = self.get_token_info(table_name)
            self.errors.append(
                f"Semantic Error: Table '{table_name}' is not declared at line {token_info['line']}, column {token_info['col']}."
            )
            return
        
        for child in node.children:
            if child.name == "ValueList":
                self._extract_values(child, values)
        
        table_columns = list(self.symbol_table[table_name]['columns'].items())
        
        if len(values) != len(table_columns):
            token_info = self.get_token_info(table_name)
            self.errors.append(
                f"Semantic Error: Type mismatch at line {token_info['line']}, column {token_info['col']}. Table '{table_name}' expects {len(table_columns)} values, but {len(values)} were provided."
            )
            return
        
        for i, (col_name, col_type) in enumerate(table_columns):
            if i < len(values):
                value_type, value_literal = values[i]
                if not self._check_type_compatibility(col_type, value_type, value_literal):
                    token_info = self.get_token_info(value_literal)
                    self.errors.append(
                        f"Semantic Error: Type mismatch at line {token_info['line']}, column {token_info['col']}. Column '{col_name}' is defined as {col_type}, but a {value_type} literal was provided for insertion."
                    )
    
    def _extract_values(self, node, values):
        for child in node.children:
            if child.name == "Value":
                parts = child.value.split(':', 1)
                if len(parts) == 2:
                    value_type = parts[0]
                    value_literal = parts[1]
                    values.append((value_type, value_literal))
    
    def _check_type_compatibility(self, col_type, value_type, value_literal):
        if col_type == "INT":
            if value_type == "NUMBER_LITERAL":
                return '.' not in value_literal
            return False
        elif col_type == "FLOAT":
            return value_type == "NUMBER_LITERAL"
        elif col_type == "TEXT":
            return value_type == "STRING_LITERAL"
        return False
    
    def _process_select(self, node):
        table_name = None
        columns = []
        
        for i, child in enumerate(node.children):
            if child.name == "FROM":
                if i + 1 < len(node.children) and node.children[i + 1].name == "IDENTIFIER":
                    table_name = node.children[i + 1].value
                break
        
        if not table_name:
            return

        if table_name not in self.symbol_table:
            token_info = self.get_token_info(table_name)
            self.errors.append(
                f"Semantic Error: Table '{table_name}' is not declared at line {token_info['line']}, column {token_info['col']}."
            )
            return
        
        for child in node.children:
            if child.name == "SelectList":
                self._extract_select_columns(child, columns)
        
        for col_name in columns:
            if col_name != "*" and col_name not in self.symbol_table[table_name]['columns']:
                token_info = self.get_token_info(col_name)
                self.errors.append(
                    f"Semantic Error: Column '{col_name}' does not exist in table '{table_name}' at line {token_info['line']}, column {token_info['col']}."
                )
        
        for child in node.children:
            if child.name == "WhereClause":
                self._process_where(child, table_name)
    
    def _extract_select_columns(self, node, columns):
        for child in node.children:
            if child.name == "MULTIPLY":
                columns.append("*")
            elif child.name == "ExpressionList":
                self._extract_expression_columns(child, columns)
    
    def _extract_expression_columns(self, node, columns):
        for child in node.children:
            if child.name == "Expression":
                self._extract_from_expression(child, columns)
    
    def _extract_from_expression(self, node, columns):
        for child in node.children:
            if child.name == "Term":
                self._extract_from_term(child, columns)
    
    def _extract_from_term(self, node, columns):
        for child in node.children:
            if child.name == "Factor":
                if child.value and child.value.startswith("IDENTIFIER:"):
                    col_name = child.value.split(':', 1)[1]
                    columns.append(col_name)
            elif child.name in ["Expression", "Term"]:
                self._extract_from_expression(child, columns)
    
    def _process_update(self, node):
        table_name = None
        assignments = []
        
        for child in node.children:
            if child.name == "IDENTIFIER":
                table_name = child.value
                break
        
        if not table_name:
            return
        
        if table_name not in self.symbol_table:
            token_info = self.get_token_info(table_name)
            self.errors.append(
                f"Semantic Error: Table '{table_name}' is not declared at line {token_info['line']}, column {token_info['col']}."
            )
            return
        
        for child in node.children:
            if child.name == "AssignmentList":
                self._extract_assignments(child, assignments)
        
        for col_name, value_type, value_literal in assignments:
            if col_name not in self.symbol_table[table_name]['columns']:
                token_info = self.get_token_info(col_name)
                self.errors.append(
                    f"Semantic Error: Column '{col_name}' does not exist in table '{table_name}' at line {token_info['line']}, column {token_info['col']}."
                )
            else:
                col_type = self.symbol_table[table_name]['columns'][col_name]
                if value_type and not self._check_type_compatibility(col_type, value_type, value_literal):
                    token_info = self.get_token_info(value_literal)
                    self.errors.append(
                        f"Semantic Error: Type mismatch at line {token_info['line']}, column {token_info['col']}. Column '{col_name}' is defined as {col_type}, but a {value_type} was provided."
                    )
                    
        for child in node.children:
            if child.name == "WhereClause":
                self._process_where(child, table_name)
    
    def _extract_assignments(self, node, assignments):
        for child in node.children:
            if child.name == "Assignment":
                col_name = None
                value_type = None
                value_literal = None
                
                for subchild in child.children:
                    if subchild.name == "IDENTIFIER":
                        col_name = subchild.value
                    elif subchild.name == "Expression":
                        value_info = self._extract_value_from_expression(subchild)
                        if value_info:
                            value_type, value_literal = value_info
                
                if col_name:
                    assignments.append((col_name, value_type, value_literal))
    
    def _extract_value_from_expression(self, node):
        for child in node.children:
            if child.name == "Term":
                return self._extract_value_from_term(child)
        return None
    
    def _extract_value_from_term(self, node):
        for child in node.children:
            if child.name == "Factor":
                if child.value and ':' in child.value:
                    parts = child.value.split(':', 1)
                    return (parts[0] + '_LITERAL', parts[1])
        return None
    
    def _process_delete(self, node):
        table_name = None
        
        for i, child in enumerate(node.children):
            if child.name == "FROM":
                if i + 1 < len(node.children) and node.children[i + 1].name == "IDENTIFIER":
                    table_name = node.children[i + 1].value
                break
        
        if not table_name:
            return
        
        if table_name not in self.symbol_table:
            token_info = self.get_token_info(table_name)
            self.errors.append(
                f"Semantic Error: Table '{table_name}' is not declared at line {token_info['line']}, column {token_info['col']}."
            )
            return
        
        for child in node.children:
            if child.name == "WhereClause":
                self._process_where(child, table_name)
    
    def _process_where(self, node, table_name):
        for child in node.children:
            if child.name == "Condition":
                self._process_condition(child, table_name)
    
    def _process_condition(self, node, table_name):
        for child in node.children:
            if child.name in ["AndCondition", "Condition"]:
                self._process_condition(child, table_name)
            elif child.name == "NotCondition":
                self._process_not_condition(child, table_name)
    
    def _process_not_condition(self, node, table_name):
        for child in node.children:
            if child.name == "Comparison":
                self._process_comparison(child, table_name)
            elif child.name == "BooleanExpr":
                if child.value and child.value.startswith("IDENTIFIER:"):
                    col_name = child.value.split(':', 1)[1]
                    if col_name not in self.symbol_table[table_name]['columns']:
                        token_info = self.get_token_info(col_name)
                        self.errors.append(
                            f"Semantic Error: Column '{col_name}' does not exist in table '{table_name}' at line {token_info['line']}, column {token_info['col']}."
                        )
    
    def _process_comparison(self, node, table_name):
        left_col = None
        left_type = None
        right_type = None
        right_literal = None
        
        expressions = []
        for child in node.children:
            if child.name == "Expression":
                expressions.append(child)
        
        if len(expressions) >= 2:
            left_info = self._extract_comparison_operand(expressions[0])
            if left_info:
                left_col, left_type, left_literal = left_info
                
                if left_type == "IDENTIFIER" and left_col:
                    if left_col not in self.symbol_table[table_name]['columns']:
                        token_info = self.get_token_info(left_col)
                        self.errors.append(
                            f"Semantic Error: Column '{left_col}' does not exist in table '{table_name}' at line {token_info['line']}, column {token_info['col']}."
                        )
                        return
                    col_type = self.symbol_table[table_name]['columns'][left_col]
                    
                    right_info = self._extract_comparison_operand(expressions[1])
                    if right_info:
                        _, right_type, right_literal = right_info
                        
                        if right_type == "NUMBER":
                            if col_type == "TEXT":
                                token_info = self.get_token_info(right_literal)
                                self.errors.append(
                                    f"Semantic Error: Type mismatch at line {token_info['line']}, column {token_info['col']}. Column '{left_col}' is defined as {col_type}, but a NUMBER literal was used in comparison."
                                )
                        elif right_type == "STRING":
                            if col_type in ["INT", "FLOAT"]:
                                token_info = self.get_token_info(right_literal)
                                self.errors.append(
                                    f"Semantic Error: Type mismatch at line {token_info['line']}, column {token_info['col']}. Column '{left_col}' is defined as {col_type}, but a STRING literal was used in comparison."
                                )
    
    def _extract_comparison_operand(self, node):
        for child in node.children:
            if child.name == "Term":
                return self._extract_from_term_comparison(child)
        return None
    
    def _extract_from_term_comparison(self, node):
        for child in node.children:
            if child.name == "Factor":
                if child.value and ':' in child.value:
                    parts = child.value.split(':', 1)
                    return (parts[1], parts[0], parts[1])
        return None
    
    def get_symbol_table_dump(self):
        if not self.symbol_table:
            return "Symbol Table is empty.\n"
        
        output = "\n=== Symbol Table ===\n"
        for table_name, table_info in self.symbol_table.items():
            output += f"\nTable: {table_name}\n"
            output += "  Columns:\n"
            for col_name, col_type in table_info['columns'].items():
                output += f"    {col_name}: {col_type}\n"
        return output
    
    def get_annotated_tree(self):
        if not self.parse_tree:
            return ""
        
        output = "\n=== Annotated Parse Tree ===\n"
        output += self._annotate_node(self.parse_tree, "")
        return output
    
    def _annotate_node(self, node, prefix, is_last=True):
        if node is None:
            return ""
        
        output = ""
        connector = "└── " if is_last else "├── "
        
        node_str = str(node)
        type_info = self._get_type_annotation(node)
        if type_info:
            node_str += f" [{type_info}]"
        
        if prefix:
            output += prefix + connector + node_str + "\n"
        else:
            output += node_str + "\n"
        
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            output += self._annotate_node(child, new_prefix, is_last_child)
        
        return output
    
    def _get_type_annotation(self, node):
        if node.name == "Factor" and node.value:
            if node.value.startswith("IDENTIFIER:"):
                col_name = node.value.split(':', 1)[1]
                for table_name, table_info in self.symbol_table.items():
                    if col_name in table_info['columns']:
                        return f"Type: {table_info['columns'][col_name]}"
            elif node.value.startswith("NUMBER:"):
                return "Type: NUMBER"
            elif node.value.startswith("STRING:"):
                return "Type: STRING"
        elif node.name == "Value" and node.value:
            if node.value.startswith("NUMBER_LITERAL:"):
                return "Type: NUMBER"
            elif node.value.startswith("STRING_LITERAL:"):
                return "Type: STRING"
        elif node.name == "DataType" and node.value:
            return f"Type: {node.value}"
        return None
