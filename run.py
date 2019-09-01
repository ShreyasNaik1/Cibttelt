
from Interpreter import Interpreter
from Lexer import Lexer 
from Parser import Parser 
from Context import Context 
from SymbolTable import SymbolTable 
import sys 
import math

sys.path.insert(0, './Value')
sys.path.insert(0, './Value/BaseFunction')
from Number import *
from BuiltInFunction import BuiltInFunction


Number.null = Number(0)
Number.false = "false"
Number.true = "true"
Number.math_PI = Number(math.pi)


BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.printRet    = BuiltInFunction("printRet")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.inpInt   	= BuiltInFunction("inpInt")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.isNum   	= BuiltInFunction("isNum")
BuiltInFunction.isStr  	    = BuiltInFunction("isStr")
BuiltInFunction.isList      = BuiltInFunction("isList")
BuiltInFunction.isFunc 		= BuiltInFunction("isFunc")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len			= BuiltInFunction("len")
BuiltInFunction.run			= BuiltInFunction("run")


GlobalSymTable = SymbolTable()
GlobalSymTable.set("NULL", Number.null)
GlobalSymTable.set("FALSE", Number.false)
GlobalSymTable.set("TRUE", Number.true)
GlobalSymTable.set("MATH_PI", Number.math_PI)
GlobalSymTable.set("PRINT", BuiltInFunction.print)
GlobalSymTable.set("PRINT_RET", BuiltInFunction.printRet)
GlobalSymTable.set("INPUT", BuiltInFunction.input)
GlobalSymTable.set("INPUT_INT", BuiltInFunction.inpInt)
GlobalSymTable.set("CLEAR", BuiltInFunction.clear)
GlobalSymTable.set("CLS", BuiltInFunction.clear)
GlobalSymTable.set("IS_NUM", BuiltInFunction.isNum)
GlobalSymTable.set("IS_STR", BuiltInFunction.isStr)
GlobalSymTable.set("IS_LIST", BuiltInFunction.isList)
GlobalSymTable.set("IS_FUN", BuiltInFunction.isFunc)
GlobalSymTable.set("APPEND", BuiltInFunction.append)
GlobalSymTable.set("POP", BuiltInFunction.pop)
GlobalSymTable.set("EXTEND", BuiltInFunction.extend)
GlobalSymTable.set("LEN", BuiltInFunction.len)
GlobalSymTable.set("RUN", BuiltInFunction.run)



def run(fname, text):
	lexer = Lexer(fname, text)
	tokens, error = lexer.genTok()
	if error: return None, error
	
	parser = Parser(tokens)
	bTree = parser.parse()
	if bTree.error: return None, bTree.error

	interpreter = Interpreter()
	context = Context('<program>')
	context.symbTable = GlobalSymTable
	result = interpreter.visit(bTree.node, context)

	return result.value, result.error