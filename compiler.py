import http.server
import socketserver
import json
import urllib.parse
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
import os

PORT = 8080

class CompilerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(self.get_css().encode())
        elif self.path.startswith('/files'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            files = [f for f in os.listdir('.') if f.endswith('.sql')]
            self.wfile.write(json.dumps(files).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/analyze':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            source_code = data.get('code', '')
            
            # Run lexical analysis
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            # Run syntax analysis
            parser = Parser(tokens)
            parse_tree = parser.parse()
            
            # Run semantic analysis
            semantic = SemanticAnalyzer(parse_tree, tokens)
            semantic_errors = semantic.analyze()
            
            # Format results
            result = {
                'lexer': {
                    'errors': lexer.errors,
                    'tokens': tokens,
                    'symbols': lexer.symbols,
                    'token_count': len(tokens),
                    'identifier_count': len(lexer.symbols)
                },
                'parser': {
                    'errors': parser.errors,
                    'tree': self.tree_to_dict(parse_tree) if parse_tree else None
                },
                'semantic': {
                    'errors': semantic_errors,
                    'symbol_table': semantic.symbol_table,
                    'symbol_table_dump': semantic.get_symbol_table_dump(),
                    'annotated_tree': semantic.get_annotated_tree()
                },
                'summary': {
                    'lexical_errors': len(lexer.errors),
                    'syntax_errors': len(parser.errors),
                    'semantic_errors': len(semantic_errors),
                    'success': len(lexer.errors) == 0 and len(parser.errors) == 0 and len(semantic_errors) == 0
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == '/load':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            filename = data.get('filename', '')
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'content': content, 'filename': filename}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def tree_to_dict(self, node):
        if node is None:
            return None
        return {
            'name': str(node),
            'children': [self.tree_to_dict(child) for child in node.children]
        }
    
    def get_html(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL-Like Language Compiler</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>SQL-Like Language Compiler</h1>
            <p>Lexical, Syntax & Semantic Analysis</p>
        </header>
        
        <div class="toolbar">
            <select id="fileSelect">
                <option value="">-- Select a file --</option>
            </select>
            <button class="btn" onclick="loadFile()">Load File</button>
            <button class="btn btn-primary" onclick="analyze()">Analyze Code</button>
            <button class="btn" onclick="clearAll()">Clear Output</button>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('source')">Source Code</button>
            <button class="tab-btn" onclick="showTab('lexer')">Lexical Analysis</button>
            <button class="tab-btn" onclick="showTab('parser')">Syntax Analysis</button>
            <button class="tab-btn" onclick="showTab('semantic')">Semantic Analysis</button>
            <button class="tab-btn" onclick="showTab('summary')">Summary</button>
        </div>
        
        <div id="source" class="tab-content active">
            <textarea id="sourceCode" placeholder="Enter or load SQL code here..."></textarea>
        </div>
        
        <div id="lexer" class="tab-content">
            <div id="lexerOutput"></div>
        </div>
        
        <div id="parser" class="tab-content">
            <div id="parserOutput"></div>
        </div>
        
        <div id="semantic" class="tab-content">
            <div id="semanticOutput"></div>
        </div>
        
        <div id="summary" class="tab-content">
            <div id="summaryOutput"></div>
        </div>
        
        <div id="status" class="status">Ready</div>
    </div>
    
    <script>
        // Load available files
        fetch('/files')
            .then(r => r.json())
            .then(files => {
                const select = document.getElementById('fileSelect');
                files.forEach(f => {
                    const opt = document.createElement('option');
                    opt.value = f;
                    opt.textContent = f;
                    select.appendChild(opt);
                });
            });
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function loadFile() {
            const filename = document.getElementById('fileSelect').value;
            if (!filename) {
                setStatus('Please select a file');
                return;
            }
            
            fetch('/load', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({filename})
            })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    setStatus('Error: ' + data.error);
                } else {
                    document.getElementById('sourceCode').value = data.content;
                    setStatus('Loaded: ' + data.filename);
                }
            });
        }
        
        function analyze() {
            const code = document.getElementById('sourceCode').value;
            if (!code.trim()) {
                setStatus('Please enter some code to analyze');
                return;
            }
            
            setStatus('Analyzing...');
            
            fetch('/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code})
            })
            .then(r => r.json())
            .then(data => {
                displayLexerResults(data.lexer);
                displayParserResults(data.parser);
                displaySemanticResults(data.semantic);
                displaySummary(data);
                
                if (data.summary.success) {
                    setStatus('✓ Analysis complete - No errors');
                } else {
                    setStatus(`Analysis complete with errors (Lexical: ${data.summary.lexical_errors}, Syntax: ${data.summary.syntax_errors}, Semantic: ${data.summary.semantic_errors})`);
                }
                
                showTab('summary');
            });
        }
        
        function displayLexerResults(lexer) {
            let html = '<h2>LEXICAL ANALYSIS RESULTS</h2>';
            
            if (lexer.errors.length > 0) {
                html += '<h3>Lexical Errors:</h3><pre class="errors">';
                lexer.errors.forEach(e => html += '• ' + e + '\\n');
                html += '</pre>';
            } else {
                html += '<p class="success">✓ No lexical errors detected.</p>';
            }
            
            html += `<h3>Tokens (${lexer.token_count} total):</h3>`;
            html += '<table><tr><th>Token</th><th>Lexeme</th><th>Line</th><th>Column</th></tr>';
            lexer.tokens.forEach(t => {
                html += `<tr><td>${t[0]}</td><td>${t[1]}</td><td>${t[2]}</td><td>${t[3]}</td></tr>`;
            });
            html += '</table>';
            
            if (Object.keys(lexer.symbols).length > 0) {
                html += `<h3>Symbol Table (${lexer.identifier_count} identifiers):</h3>`;
                html += '<table><tr><th>Identifier</th><th>First Seen</th><th>Count</th></tr>';
                Object.keys(lexer.symbols).sort().forEach(name => {
                    const info = lexer.symbols[name];
                    html += `<tr><td>${name}</td><td>Line ${info.line}, Col ${info.col}</td><td>${info.count}</td></tr>`;
                });
                html += '</table>';
            }
            
            document.getElementById('lexerOutput').innerHTML = html;
        }
        
        function displayParserResults(parser) {
            let html = '<h2>SYNTAX ANALYSIS RESULTS</h2>';
            
            if (parser.errors.length > 0) {
                html += '<h3>Syntax Errors:</h3><pre class="errors">';
                parser.errors.forEach(e => html += '• ' + e + '\\n');
                html += '</pre>';
            } else {
                html += '<p class="success">✓ No syntax errors detected.</p>';
            }
            
            if (parser.tree) {
                html += '<h3>Parse Tree:</h3><pre class="tree">';
                html += renderTree(parser.tree, '');
                html += '</pre>';
            }
            
            document.getElementById('parserOutput').innerHTML = html;
        }
        
        function renderTree(node, prefix) {
            let result = node.name + '\\n';
            for (let i = 0; i < node.children.length; i++) {
                const isLast = i === node.children.length - 1;
                const child = node.children[i];
                result += prefix + (isLast ? '└── ' : '├── ');
                result += renderTree(child, prefix + (isLast ? '    ' : '│   '));
            }
            return result;
        }
        
        function displaySemanticResults(semantic) {
            let html = '<h2>SEMANTIC ANALYSIS RESULTS</h2>';
            
            if (semantic.errors.length > 0) {
                html += '<h3>Semantic Errors:</h3><pre class="errors">';
                semantic.errors.forEach(e => html += '• ' + e + '\\n');
                html += '</pre>';
            } else {
                html += '<p class="success">✓ Semantic Analysis Successful. Query is valid.</p>';
            }
            
            html += '<h3>Symbol Table:</h3>';
            html += '<pre class="tree">' + semantic.symbol_table_dump + '</pre>';
            
            if (semantic.errors.length === 0 && semantic.annotated_tree) {
                html += '<h3>Annotated Parse Tree:</h3>';
                html += '<pre class="tree">' + semantic.annotated_tree + '</pre>';
            }
            
            document.getElementById('semanticOutput').innerHTML = html;
        }
        
        function displaySummary(data) {
            let html = '<h2>COMPILATION SUMMARY</h2>';
            html += '<table>';
            html += `<tr><td>Total tokens:</td><td>${data.lexer.token_count}</td></tr>`;
            html += `<tr><td>Total identifiers:</td><td>${data.lexer.identifier_count}</td></tr>`;
            html += `<tr><td>Lexical errors:</td><td>${data.summary.lexical_errors}</td></tr>`;
            html += `<tr><td>Syntax errors:</td><td>${data.summary.syntax_errors}</td></tr>`;
            html += `<tr><td>Semantic errors:</td><td>${data.summary.semantic_errors}</td></tr>`;
            html += '<tr><td>Status:</td><td>';
            if (data.summary.success) {
                html += '<span class="success">✓ COMPILATION SUCCESSFUL</span>';
            } else {
                html += '<span class="error">✗ COMPILATION FAILED</span>';
            }
            html += '</td></tr></table>';
            
            document.getElementById('summaryOutput').innerHTML = html;
        }
        
        function clearAll() {
            document.getElementById('lexerOutput').innerHTML = '';
            document.getElementById('parserOutput').innerHTML = '';
            document.getElementById('semanticOutput').innerHTML = '';
            document.getElementById('summaryOutput').innerHTML = '';
            setStatus('Output cleared');
        }
        
        function setStatus(msg) {
            document.getElementById('status').textContent = msg;
        }
    </script>
    <footer style="text-align: center; padding: 20px; margin-top: 40px; border-top: 2px solid #2c3e50; background-color: #34495e; color: #ecf0f1;">
        <p style="margin: 5px 0; font-size: 14px;"><strong>Team Members:</strong></p>
        <p style="margin: 5px 0;">Omar Bassam Tawfik • Mostafa Mohamed El-Sheikh • Yassin Suleiman Hamad • Kareem Mohamed Tantawi</p>
        <p style="margin: 10px 0 5px 0; font-size: 12px; color: #bdc3c7;">CSCI415: Compiler Design Project</p>
    </footer>
</body>
</html>'''
    
    def get_css(self):
        return '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f5f5;
    padding: 20px;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    text-align: center;
}

header h1 {
    font-size: 2em;
    margin-bottom: 5px;
}

header p {
    opacity: 0.9;
}

.toolbar {
    padding: 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    gap: 10px;
    align-items: center;
}

select, .btn {
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

select {
    flex: 1;
    max-width: 300px;
}

.btn {
    background: white;
    cursor: pointer;
    transition: all 0.3s;
}

.btn:hover {
    background: #f8f9fa;
    transform: translateY(-1px);
}

.btn-primary {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.btn-primary:hover {
    background: #5568d3;
}

.tabs {
    display: flex;
    background: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
}

.tab-btn {
    flex: 1;
    padding: 15px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: #666;
    transition: all 0.3s;
}

.tab-btn:hover {
    background: rgba(102, 126, 234, 0.1);
}

.tab-btn.active {
    color: #667eea;
    border-bottom: 3px solid #667eea;
    margin-bottom: -2px;
}

.tab-content {
    display: none;
    padding: 20px;
    min-height: 500px;
    max-height: 600px;
    overflow-y: auto;
}

.tab-content.active {
    display: block;
}

#sourceCode {
    width: 100%;
    height: 550px;
    padding: 15px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th, td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
}

th {
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
}

tr:hover {
    background: #f8f9fa;
}

.tree, .errors {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    overflow-x: auto;
    white-space: pre;
}

.errors {
    color: #dc3545;
    background: #fff5f5;
}

.success {
    color: #28a745;
    font-weight: 500;
    padding: 10px;
    background: #f0f9f4;
    border-radius: 4px;
    margin: 10px 0;
}

.error {
    color: #dc3545;
    font-weight: 500;
}

h2 {
    color: #495057;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f8f9fa;
}

h3 {
    color: #667eea;
    margin: 20px 0 10px 0;
    font-size: 1.1em;
}

.status {
    padding: 15px 20px;
    background: #f8f9fa;
    border-top: 1px solid #dee2e6;
    color: #666;
    font-size: 14px;
}
'''

def main():
    with socketserver.TCPServer(("", PORT), CompilerHandler) as httpd:
        print(f"=============================================================")
        print(f"SQL-Like Language Compiler - Web Interface")
        print(f"=============================================================")
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Press Ctrl+C to stop the server")
        print(f"=============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\nServer stopped.")

if __name__ == "__main__":
    main()
