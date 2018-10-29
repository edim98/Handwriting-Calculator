import re
import RPi.GPIO as GPIO

from time import sleep

SIGNS_1 = ('*', '/')
SIGNS_2 = ('+', '-')
SIGNS_3 = ('(', ')')

def send_instruction(num1, sign, num2):
	acknowledged = False

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(2, GPIO.OUT)
	GPIO.setup(3, GPIO.OUT)
	GPIO.setup(4, GPIO.OUT)
	GPIO.setup(5, GPIO.OUT)
	GPIO.setup(6, GPIO.OUT)
	GPIO.setup(7, GPIO.OUT)
	GPIO.setup(8, GPIO.OUT)
	GPIO.setup(9, GPIO.OUT)
	GPIO.setup(10, GPIO.OUT)
	GPIO.setup(11, GPIO.OUT)
	GPIO.setup(12, GPIO.OUT)
	GPIO.setup(13, GPIO.IN)
	GPIO.setup(14, GPIO.IN)
	GPIO.setup(15, GPIO.IN)
	GPIO.setup(16, GPIO.IN)
	GPIO.setup(25, GPIO.IN)
	GPIO.setup(26, GPIO.IN)
	GPIO.setup(27, GPIO.IN)
	state1 = GPIO.input(13)
	state2 = GPIO.input(14)
	state3 = GPIO.input(15)
	sol1 = GPIO.input(25)
	sol2 = GPIO.input(26)
	sol3 = GPIO.input(27)

	# Send begin calculation
	GPIO.output(2, GPIO.LOW)
	GPIO.output(3, GPIO.LOW)
	GPIO.output(4, GPIO.LOW)
	GPIO.output(5, GPIO.HIGH)

	#wait for ack start calc
	while(!acknowledged):
		if (state1 == 0 and state2 == 1 and state3 == 0):
			acknowledged = True
	acknowledged = False

	#send operation type:
	GPIO.output(11, GPIO.HIGH)
	GPIO.output(12, GPIO.HIGH)
	if sign == '+' :
		GPIO.output(2, GPIO.LOW)
		GPIO.output(3, GPIO.HIGH)
		GPIO.output(4, GPIO.HIGH)
		GPIO.output(5, GPIO.LOW)
	elif sign == '-':
		GPIO.output(2, GPIO.LOW)
		GPIO.output(3, GPIO.HIGH)
		GPIO.output(4, GPIO.HIGH)
		GPIO.output(5, GPIO.HIGH)
	elif sign == '*':
		GPIO.output(2, GPIO.HIGH)
		GPIO.output(3, GPIO.LOW)
		GPIO.output(4, GPIO.LOW)
		GPIO.output(5, GPIO.LOW)
	elif sign == '/':
		GPIO.output(2, GPIO.HIGH)
		GPIO.output(3, GPIO.LOW)
		GPIO.output(4, GPIO.LOW)
		GPIO.output(5, GPIO.HIGH)

	#wait for ack operation type
	while(!acknowledged):
		if (state1 == 0 and state2 == 1 and state3 == 1):
			acknowledged = True
	acknowledged = False

	#send num1
	num1_binary = '{0:11b}'.format(num1)
	for pin in range (2, 12):
		if num1_binary[pin-2] == 1:
			GPIO.output(pin, GPIO.HIGH)
		else:
			GPIO.output(pin, GPIO.LOW)

	#wait for ack num1
	while(!acknowledged):
		if (state1 == 1 and state2 == 0 and state3 == 0):
			acknowledged = True
	acknowledged = False

	#send num2
	num2_binary = '{0:11b}'.format(num2)
	for pin in range (2, 12):
		if num2_binary[pin-2] == 1:
			GPIO.output(pin, GPIO.HIGH)
		else:
			GPIO.output(pin, GPIO.LOW)

	#wait for ack num2
	while(!acknowledged):
		if (state1 == 1 and state2 == 0 and state3 == 1):
			acknowledged = True
	acknowledged = False

	#wait for solution header
	while(!acknowledged):
		if (state1 == 0 and state2 == 0 and state3 == 1):
			acknowledged = True
	acknowledged = False

	#get the solution (15 bits long)
	solution = "010101010101010"
	for pin in range (13, 27):
		solution[pin-13] = GPIO.input(pin)

	print(solution)
	solution_int = int(solution, 2)
	print(solution_int)

	#send end calculation instruction
	GPIO.output(2, GPIO.LOW)
	GPIO.output(3, GPIO.LOW)
	GPIO.output(4, GPIO.HIGH)
	GPIO.output(5, GPIO.HIGH)

	return solution_int

# Communicates a certain calculation to the fpga and waits for an answer.
#change to communicate to fpga
def fpga_calc(num1, sign, num2):
	string = str(num1)
	string += str(sign)
	string += str(num2)
	integer = int(eval(string))
	return integer

# Gets what calculations need to be done on the numbers and symbols in the array
def get_calcs(start_array, signs):
	end_array = []
	for i in range(0, len(start_array)):
		if start_array[i] in signs:
			end_array.pop(len(end_array)-1)
			start_array[i+1] = fpga_calc(start_array[i-1], start_array[i], start_array[i+1])
		else:
			end_array.append(start_array[i])
	return end_array

# Takes the formula string and puts it into an array with ints for integers and char for symbols.
# Keeps the integers as big as possible (255 stays 255 and does not become 2, 5, 5)
def formula_to_array(formula):
	print(formula)
	while ')' in formula:
		old_partition = formula.partition(')')[0]
		reversed_partition = old_partition[::-1]
		reversed_partition = reversed_partition.partition('(')[0]
		new_partition = reversed_partition[::-1]
		answer = formula_to_array(new_partition)
		replace_str = ''.join(['(' , new_partition, ')'])
		formula = formula.replace(replace_str, str(answer), 1)
		print(formula)

	if formula[0] == '-':
		formula = formula.replace('-', "0-", 1)

	temp = ""
	array = []
	for character in range (0, len(formula)):
		if re.match(r"[0-9]", formula[character]):
			temp += str(formula[character])
		else:
			if len(temp) != 0:
				array.append(int(temp))
				temp = ""
			array.append(formula[character])
	if len(temp) != 0:
		array.append(int(temp))
	return get_calcs(get_calcs(array, SIGNS_1), SIGNS_2)[0]

# Executes all functions necessary to calculate the formula string and get the answer
# def get_formula_answer(formula):
# 	return get_calcs(get_calcs(formula_to_array(formula), SIGNS_1), SIGNS_2)[0]

# Checks if the formula is correct, if not it will return a correct string if the formula is correct or it can be corrected, or "Error" if the formula cannot be corrected
def check_formula(formula):
	new_formula = ""
	if formula[0] in SIGNS_1:
		return "Error"
	elif formula[len(formula)-1] in (SIGNS_1 or SIGNS_2):
		return "Error"
	if formula[0] == '+':
		new_formula = formula[1:]
	else:
		new_formula = formula
	for char_pos in range(0, len(new_formula)):
		if new_formula[char_pos] in (SIGNS_1 or SIGNS_2):
			if new_formula[char_pos - 1] in (SIGNS_1 or SIGNS_2):
				return "Error"
	return new_formula


# In and output. Should be retrieved form the 
# formula = "(0-512)+12/6*256-1024-3*12"
formula = "7*((5+3)*2)+2"
formula = check_formula(formula)
fin_answer = 0
if formula != "Error":
	# print(get_formula_answer(formula))
	print(formula_to_array(formula))
else:
	print("Error")