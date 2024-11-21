import ply.yacc as yacc
from lexico import tokens

# Diccionarios para almacenar variables y funciones en tiempo de ejecución
variables = {}
functions = {}

# Precedencia de operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'LESS', 'GREATER', 'LESSEQ', 'GREATEREQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIVIDE', 'MODULE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
)

# ========================
# CLASES DEL AST (Árbol de Sintaxis Abstracta)
# ========================
class Number:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value


class String:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value

class Char:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value

class Boolean:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value

class Variable:
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        if self.name not in variables:
            raise ValueError(f"Undefined variable '{self.name}'")
        return variables[self.name]

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self):
        left_val = self.left.evaluate()
        right_val = self.right.evaluate()
        
        # Define las operaciones binarias
        if self.op == '+': return left_val + right_val
        if self.op == '-': return left_val - right_val
        if self.op == '*': return left_val * right_val
        if self.op == '/': return left_val / right_val
        if self.op == '%': return left_val % right_val
        if self.op == '<': return left_val < right_val
        if self.op == '>': return left_val > right_val
        if self.op == '<=': return left_val <= right_val
        if self.op == '>=': return left_val >= right_val
        if self.op == '==': return left_val == right_val
        if self.op == '!=': return left_val != right_val
        if self.op == '&&': return left_val and right_val
        if self.op == '||': return left_val or right_val
        raise ValueError(f"Operador desconocido '{self.op}'")

class NotOp:
    def __init__(self, expression):
        self.expression = expression

    def evaluate(self):
        return not self.expression.evaluate()

class Assign:
    def __init__(self, target, expression):
        self.target = target
        self.expression = expression

    def execute(self):
        value = self.expression.evaluate()  # Evaluar la expresión antes de asignar
        if isinstance(self.target, Variable):
            variables[self.target.name] = value
        elif isinstance(self.target, ListAccess):
            list_obj = self.target.list_expr.evaluate()
            index = self.target.index_expr.evaluate()
            if isinstance(list_obj, list):
                if index < 0:
                    raise IndexError("Índice negativo no permitido")
                if index >= len(list_obj):
                    list_obj.extend([None] * (index - len(list_obj) + 1))
                list_obj[index] = value
            else:
                raise TypeError("El objeto no es una lista")
        else:
            raise ValueError("Invalid assignment target")


class Print:
    def __init__(self, expressions):
        self.expressions = expressions

    def execute(self):
        values = [expr.evaluate() for expr in self.expressions]
        print(*values)

class IfElse:
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

    def execute(self):
        if self.condition.evaluate():
            return self.if_block.execute()
        elif self.else_block:
            return self.else_block.execute()

class Block:
    def __init__(self, statements):
        self.statements = statements

    def execute(self):
        for stmt in self.statements:
            result = stmt.execute()
            if isinstance(result, Return):
                return result
        return None

class WhileLoop:
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def execute(self):
        while self.condition.evaluate():
            self.block.execute()

class ForLoop:
    def __init__(self, init, condition, update, block):
        self.init = init
        self.condition = condition
        self.update = update
        self.block = block

    def execute(self):
        self.init.execute()
        while self.condition.evaluate():
            self.block.execute()
            self.update.execute()

class Function:
    def __init__(self, name, parameters, block):
        self.name = name
        self.parameters = parameters
        self.block = block

    def execute(self, args):
        prev_variables = variables.copy()
        for param, arg in zip(self.parameters, args):
            variables[param] = arg

        result = self.block.execute()

        variables.clear()
        variables.update(prev_variables)
        return result

class FunctionCall:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def evaluate(self):
        if self.name in functions:
            func = functions[self.name]
            args = [arg.evaluate() for arg in self.arguments]
            return func.execute(args)
        else:
            raise ValueError(f"Undefined function '{self.name}'")

class Return:
    def __init__(self, expression):
        self.expression = expression

    def evaluate(self):
        return self.expression.evaluate()

    def execute(self):
        return self

class List:
    def __init__(self, elements):
        self.elements = [element.evaluate() for element in elements]

    def evaluate(self):
        return self.elements

class ListAccess:
    def __init__(self, list_expr, index_expr):
        self.list_expr = list_expr
        self.index_expr = index_expr

    def evaluate(self):
        list_val = self.list_expr.evaluate()
        index_val = self.index_expr.evaluate()
        return list_val[index_val]

# ========================
# REGLAS DE LA GRAMÁTICA
# ========================
def p_program(p):
    'program : statement_list'
    statements = [stmt for stmt in p[1] if stmt is not None]
    for statement in statements:
        statement.execute()

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : print_statement
                 | assign_statement
                 | if_statement
                 | while_statement
                 | for_statement
                 | function_definition
                 | return_statement
                 | expression SEMICOLON'''
    if len(p) == 3:
        p[0] = ExpressionStatement(p[1])
    else:
        p[0] = p[1]


def p_print_statement(p):
    'print_statement : PRINT LPAREN print_arguments RPAREN SEMICOLON'
    p[0] = Print(p[3])



def p_print_arguments(p):
    '''print_arguments : print_arguments COMMA expression
                       | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_assign_statement(p):
    'assign_statement : lvalue EQUALS expression SEMICOLON'
    p[0] = Assign(p[1], p[3])

def p_lvalue(p):
    '''lvalue : ID
              | expression LBRACKET expression RBRACKET'''
    if len(p) == 2:
        p[0] = Variable(p[1])
    else:
        p[0] = ListAccess(p[1], p[3])

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN block
                    | IF LPAREN expression RPAREN block ELSE block'''
    if len(p) == 6:
        p[0] = IfElse(p[3], p[5])
    else:
        p[0] = IfElse(p[3], p[5], p[7])


def p_while_statement(p):
    'while_statement : WHILE LPAREN expression RPAREN block'
    p[0] = WhileLoop(p[3], p[5])


def p_for_statement(p):
    '''for_statement : FOR LPAREN assign_statement expression SEMICOLON assign_statement RPAREN block'''
    p[0] = ForLoop(p[3], p[4], p[6], p[8])


def p_function_definition(p):
    'function_definition : FUNC ID LPAREN parameters RPAREN block'
    functions[p[2]] = Function(p[2], p[4], p[6])


def p_parameters(p):
    '''parameters : parameters COMMA ID
                  | ID
                  | empty'''
    if len(p) == 2:
        p[0] = [] if p[1] is None else [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_block(p):
    'block : LKEY statement_list RKEY'
    p[0] = Block(p[2])

def p_return_statement(p):
    'return_statement : RETURN expression SEMICOLON'
    p[0] = Return(p[2])

def p_expression(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT expression
                  | expression DIVIDE expression
                  | expression MODULE expression
                  | expression LESS expression
                  | expression GREATER expression
                  | expression LESSEQ expression
                  | expression GREATEREQ expression
                  | expression EQ expression
                  | expression NEQ expression
                  | expression AND expression
                  | expression OR expression
                  | NOT expression %prec UMINUS
                  | MINUS expression %prec UMINUS
                  | LPAREN expression RPAREN
                  | NUMBER
                  | STRING
                  | CHAR
                  | BOOLEAN
                  | ID'''
    if len(p) == 2:  # Valores primitivos o variables
        if isinstance(p[1], int) or isinstance(p[1], float):  # Números
            p[0] = Number(p[1])
        elif isinstance(p[1], str):
            if p.slice[1].type == "STRING":
                p[0] = String(p[1])
            elif p.slice[1].type == "CHAR":
                p[0] = Char(p[1])
            elif p.slice[1].type == "BOOLEAN":
                p[0] = Boolean(p[1])
            else:  # Es un ID
                p[0] = Variable(p[1])
        else:
            p[0] = p[1]
    elif len(p) == 3:  # Operadores unarios
        if p[1] == '-':
            p[0] = BinOp(Number(0), '-', p[2])
        else:
            p[0] = NotOp(p[2])
    elif len(p) == 4:  # Operadores binarios o agrupación
        if p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = BinOp(p[1], p[2], p[3])


def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}' on line {p.lineno}")
    else:
        print("Syntax error: Unexpected end of input")

# Construir el parser
parser = yacc.yacc(start='program')
