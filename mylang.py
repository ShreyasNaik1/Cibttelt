import Interpreter

while True:
	text = input('cibttelt > ')
	if text.strip() == "": continue
	result, error = Interpreter.run('<testfile>', text)

	if error:
		print(error.printStr())
	elif result:
		if len(result.elements) == 1:
			print(repr(result.elements[0]))
		else:
			print(repr(result))