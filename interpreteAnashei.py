import analizadorLexico as alex
import ts as TS
from expresionesSintactico import *
from analizadorSintactico import *

f = open("./entrada.txt", "r")
input = f.read()

instrucciones = alex.parse(input)
ts_global = TS.TablaDeSimbolos()
