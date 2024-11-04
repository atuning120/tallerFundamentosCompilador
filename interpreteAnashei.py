import analizadorLexico as lexico
import ts as TS
from expresionesSintactico import *
from analizadorSintactico import *

f= open("entrada.txt", "r")
input = f.read()

instrucciones = lexico.parse(input)