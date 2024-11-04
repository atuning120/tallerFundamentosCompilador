class Instruccion:
    '''Clase abstracta'''

class Mostrar(Instruccion):
    '''Clase que representa la instrucción mostrar que hace referencia a la impresión de un valor en pantalla'''
    def __init__(self, valor):
        self.valor = valor

class Mientras(Instruccion):
    '''Clase que representa la instrucción mientras que hace referencia a un ciclo que se ejecuta mientras una condición sea verdadera'''
    def __init__(self, condicion, instrucciones):
        self.condicion = condicion
        self.instrucciones = instrucciones

class Definicion(Instruccion):
    '''Clase que representa la definición de una variable'''
    def __init__(self, id, valor):
        self.id = id
        self.valor = valor

class Asignacion(Instruccion):
    '''Clase que representa la asignación de un valor a una variable'''
    def __init__(self, id, valor):
        self.id = id
        self.valor = valor

class If(Instruccion):
    '''Clase que representa la instrucción if que hace referencia a una condición que se ejecuta si es verdadera'''
    def __init__(self, condicion, instrucciones, else_instrucciones):
        self.condicion = condicion
        self.instrucciones = instrucciones
        self.else_instrucciones = else_instrucciones

class IfElse(Instruccion):
    '''Clase que representa la instrucción if else que hace referencia a una condición que se ejecuta si es verdadera y otra si es falsa'''
    def __init__(self, condicion, instrucciones, else_instrucciones):
        self.condicion = condicion
        self.instrucciones = instrucciones
        self.else_instrucciones = else_instrucciones