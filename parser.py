import ply.yacc as yacc
from lexico import tokens

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

    def evaluate(self):
        return self.value

class Boolean:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value

class Input:
    def __init__(self, target):
        self.target = target  # Debería ser una instancia de Variable

    def execute(self):
        try:
            # Leer la entrada del usuario
            user_input = input()
            # Asignar la entrada a la variable
            variables[self.target.name] = user_input
            print(f"Asignado: {self.target.name} = {user_input}")  # Mensaje de depuración
        except Exception as e:
            print(f"Error al leer la entrada: {e}")

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
        if isinstance(self.target, Variable):
            value = self.expression.evaluate()
            variables[self.target.name] = value
        elif isinstance(self.target, ListOperation) and self.target.operation == 'set':
            self.target.value = self.expression
            self.target.evaluate()
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
            # Si encontramos un retorno, lo propagamos
            if isinstance(result, Return):
                return result.expression.evaluate()
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

        # Restaurar las variables después de ejecutar la función
        variables.clear()
        variables.update(prev_variables)

        # Retornar el resultado si lo hay
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

    def execute(self):
        return self  # Se devuelve a sí misma para ser manejada en el bloque

class List:
    def __init__(self, elements):
        self.elements = elements

    def evaluate(self):
        return [element.evaluate() for element in self.elements]

class ListOperation:
    def __init__(self, list_expr, operation, argument=None, value=None):
        self.list_expr = list_expr
        self.operation = operation
        self.argument = argument
        self.value = value

    def evaluate(self):
        list_val = self.list_expr.evaluate()
        if self.operation == 'insert':
            if self.argument is None:
                raise ValueError("insert() requiere un argumento")
            # Supongamos que insert actúa como append
            list_val.append(self.argument.evaluate())
            print(f"Elemento insertado: {self.argument.evaluate()}")  # Depuración
            return list_val
        elif self.operation == 'explode':
            if self.argument is None:
                raise ValueError("explode() requiere un índice")
            index = self.argument.evaluate()
            try:
                removed_element = list_val.pop(index)
                print(f"Elemento removido en posición {index}: {removed_element}")  # Depuración
                return list_val
            except IndexError:
                raise IndexError(f"explode(): Índice {index} fuera de rango")
        elif self.operation == 'get':
            if self.argument is None:
                raise ValueError("get() requiere un índice")
            index = self.argument.evaluate()
            try:
                return list_val[index]
            except IndexError:
                raise IndexError(f"get(): Índice {index} fuera de rango")
        elif self.operation == 'size':
            return len(list_val)
        elif self.operation == 'set':
            if self.argument is None or self.value is None:
                raise ValueError("set() requiere un índice y un valor")
            index = self.argument.evaluate()
            value = self.value.evaluate()
            try:
                list_val[index] = value
                print(f"Elemento en posición {index} actualizado a: {value}")  # Depuración
            except IndexError:
                raise IndexError(f"set(): Índice {index} fuera de rango")
            return list_val
        else:
            raise ValueError(f"Método de lista desconocido '{self.operation}'")
        return list_val

    def execute(self):
        # Para operaciones que modifican la lista sin retornar valor
        self.evaluate()




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
                 | input_statement
                 | expression SEMICOLON'''
    if len(p) == 3:
        p[0] = p[1].evaluate()
    else:
        p[0] = p[1]

def p_input_statement(p):
    'input_statement : INPUT LPAREN lvalue RPAREN SEMICOLON'
    p[0] = Input(p[3])


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
        # Para asignar a un índice específico de una lista
        p[0] = ListOperation(p[1], 'set', p[3])




def p_argument_list(p):
    '''argument_list : argument_list COMMA expression
                     | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

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

def p_function_call(p):
    'expression : ID LPAREN argument_list RPAREN'
    p[0] = FunctionCall(p[1], p[3])

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

# Reglas específicas para métodos de lista
def p_expression_insert(p):
    'expression : expression DOT INSERT LPAREN expression RPAREN'
    p[0] = ListOperation(p[1], 'insert', p[5])

def p_expression_explode(p):
    'expression : expression DOT EXPLODE LPAREN expression RPAREN'
    p[0] = ListOperation(p[1], 'explode', p[5])

def p_expression_size(p):
    'expression : expression DOT SIZE LPAREN RPAREN'
    p[0] = ListOperation(p[1], 'size')

def p_expression_get(p):
    'expression : expression DOT GET LPAREN expression RPAREN'
    p[0] = ListOperation(p[1], 'get', p[5])



def p_expression_general(p):
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
                  | BOOLEAN
                  | ID
                  | LBRACKET list_elements RBRACKET'''
    if len(p) == 2:  # Valores primitivos o variables
        if isinstance(p[1], int) or isinstance(p[1], float):  # Números
            p[0] = Number(p[1])
        elif isinstance(p[1], str):
            if p.slice[1].type == "STRING":
                p[0] = String(p[1])
            elif p.slice[1].type == "BOOLEAN":
                p[0] = Boolean(p[1])
            else:  # Es un ID
                p[0] = Variable(p[1])
    elif len(p) == 3:  # Operadores unarios
        if p[1] == '-':
            p[0] = BinOp(Number(0), '-', p[2])
        else:
            p[0] = NotOp(p[2])
    elif len(p) == 4:
        if p[1] == '(':  # Agrupación
            p[0] = p[2]
        elif p[1] == '[':  # Lista
            p[0] = List(p[2])
        else:  # Operadores binarios
            p[0] = BinOp(p[1], p[2], p[3])
    return



def p_list_elements(p):
    '''list_elements : expression
                     | list_elements COMMA expression'''
    if len(p) == 2:  # Un solo elemento
        p[0] = [p[1]]  # `p[1]` ya debería ser un objeto con `evaluate`
    else:  # Más de un elemento
        p[0] = p[1] + [p[3]]  # Combina la lista acumulada con el nuevo elemento

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
