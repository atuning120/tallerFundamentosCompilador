import ply.lex as lex

# tokens
tokens = [
    'NUMBER', 'ID', 'EQUALS', 'PLUS', 'MINUS', 'MULT', 'DIVIDE', 'MODULE',
    'LPAREN', 'RPAREN', 'STRING', 'CHAR', 'SEMICOLON', 'LESS', 'GREATER',
    'LESSEQ', 'GREATEREQ', 'LKEY', 'RKEY', 'AND', 'OR', 'NOT', 'BOOLEAN',
    'EQ', 'NEQ', 'COMMA', 'LBRACKET', 'RBRACKET','DOT'
]

# palabras reservadas 
reserved = {
    'show': 'PRINT',
    'input': 'INPUT', 
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'mission': 'FUNC',
    'answer': 'RETURN',
    'insert': 'INSERT',    
    'explode': 'EXPLODE',    
    'size': 'SIZE',        
    'pick': 'GET',          
}

tokens+=list(reserved.values())

t_EQ = r'=='
t_NEQ = r'!='
t_LESSEQ = r'<='
t_GREATEREQ = r'>='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIVIDE = r'/'
t_MODULE = r'%'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOLON = r';'
t_LESS = r'<'
t_GREATER = r'>'
t_LKEY = r'\{'
t_RKEY = r'\}'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_DOT = r'\.'

# Ignorar espacios y tabulacion
t_ignore = ' \t'

# Token para cadenas de caracteres
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"' # utiliza comillas dobles
    t.value = t.value[1:-1]
    return t

# Token para caracteres individuales
def t_CHAR(t):
    r'\"([^\\\n]|(\\.))\"' # utiliza comillas dobles
    t.value = t.value[1:-1]
    return t

# Token para booleanos 
def t_BOOLEAN(t):
    r'\btrue\b|\bfalse\b'  # true o false
    t.value = True if t.value == 'true' else False
    return t

# Token para identificadores 
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Verificar si es palabra reservada
    t.type = reserved.get(t.value, 'ID')  # Busca en palabras reservadas, sino, es ID
    return t



# Token para números 
def t_NUMBER(t):
    r'-?\d+(\.\d+)?'  # Agrega el signo negativo opcional
    # para flotantes
    if '.' in t.value:
        t.value = float(t.value)
    # para enteros
    else:
        t.value = int(t.value)
    return t

# Token para comentarios simples
def t_COMMENT(t):
    r'//.*'
    pass 

# Contador de líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
def t_error(t):
    print(f"Caracter no valido '{t.value[0]}' en la línea {t.lexer.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

