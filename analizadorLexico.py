import ply.lex as lex
import re
import codecs
import os
import sys

lexer = lex.lex()

tokens=['PTOCOMA',
        'LLAVEIZQ',
        'LLAVEDER',
        'PARENTIZQ',
        'PARENTDER',
        'IGUAL',
        'MAS',
        'MENOS',
        'POR',
        'DIVIDIDO',
        'CONCAT',
        'MENORQUE',
        'MAYORQUE',
        'IGUALQUE',
        'NOIGUALQUE',
        'DECIMAL',
        'ENTERO',
        'CADENA',
        'ID']

reservadas={
    'numero':'NUMERO',
    'mostrar':'MOSTRAR',
    'mientras':'MIENTRAS',
    'if':'IF',
    'else':'ELSE'
}

tokens=tokens + list(reservadas.values())

# tokens

# caracteres ignorados
t_ignore=" \t"

t_PTOCOMA = r';'
t_LLAVEIZQ= r'{'
t_LLAVEDER= r'}'
t_PARENTIZQ= r'('
t_PARENTDER= r')'
t_IGUAL= r'='
t_MAS       = r'\+'
t_MENOS     = r'-'
t_POR       = r'\*'
t_DIVIDIDO  = r'/'
t_CONCAT    = r'&'
t_MENORQUE    = r'<'
t_MAYORQUE    = r'>'
t_IGUALQUE  = r'=='
t_NOIGUALQUE = r'!='

# numeros decimales
def t_DECIMAL(t):
    r'\d+\.\d+'
    try:
        t.value=float(t.values())
    except ValueError:
        print("valor decimal demasiado grande %d", t.values())
        t.values()=0
    return t

# numeros enteros
def t_ENTERO(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("valor entero demasiado grande %d", t.value)
        t.value = 0
    return t

# IDs o variables
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type=reservadas.get(t.values().lower(),'ID') # verificar que las variables que se declaren no sean alguna palabra reservada
    return t

# strings o Cadenas de caracteres
def t_CADENA(t):
    r'\".*?\"'
    t.value=t.values()[1:-1] # quita las comillas 
    return t

# comentarios de multiples lineas /* .... */
def _COMENTARIO_MULTILINEA(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno +=t.values().count('\n')

# Comentario simple // ...
def t_COMENTARIO_SIMPLE(t):
    r'//.*\n'
    t.lexer.lineno += 1

# lineas nuevas para hacer codigo
def t_newline(t):
    r'\n+'
    t.lexer.lineno +=t.values().count("\n")

# Error de caracteres
def t_error(t):
    print("Caracter Ilegal uwu '%s'" % t.value[0])
    t.lexer.skip(1)
