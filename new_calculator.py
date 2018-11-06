import re
import RPi.GPIO as GPIO

SIGNS_1 = ('*', '/')
SIGNS_2 = ('+', '-')
SIGNS_3 = ('(', ')')
NON_DOUBLES = ('+', '*', '/')
SYMBOLS = ('+', '-', '*', '/')

def reset_pins_to_low():
	for pin in range(2, 13):
		GPIO.output(pin, GPIO.LOW)

def send_instruction(num1, sign, num2):
	acknowledged = False
	finished = False
	solution_int = 0

	# Check if each input num is an int (and not an error), if not, return the error
	if not isinstance(num1, int):
		return num1
	elif not isinstance(num2, int):
		return num2

	# Set pins as in and output
	GPIO.setmode(GPIO.BCM)
	for pin in range(2, 13):
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, GPIO.LOW)
	for pin in range(13, 28):
		GPIO.setup(pin, GPIO.IN)

	#check for overflow before sending
	if num1 > 2**55-1 or num2 > 2**55-1 or num1 < -2*55 or num2 < -2**55:
		# Send Error
		GPIO.output(2, GPIO.HIGH)
		GPIO.output(3, GPIO.HIGH)
		GPIO.output(4, GPIO.HIGH)
		GPIO.output(5, GPIO.HIGH)
		return "Input number too high"

	#make sbutract calculations into add calculations
	if sign == '-':
		num2 *= -1

	#make num1 into two's commplement binary
	two_complement_num1 = bin(num1 & int("1"*56, 2))[2:]
	two_complement_56bit_num1 = ("{0:0>%s}" % (56)).format(two_complement_num1)
	print(two_complement_56bit_num1)

	#make num2 into two's commplement binary
	two_complement_num2 = bin(num2 & int("1"*56, 2))[2:]
	two_complement_56bit_num2 = ("{0:0>%s}" % (56)).format(two_complement_num2)
	print(two_complement_56bit_num2)

	#communicate with the fpga to get the calculations
	while not finished:

		# Send begin calculation
		GPIO.output(2, GPIO.LOW)
		GPIO.output(3, GPIO.LOW)
		GPIO.output(4, GPIO.LOW)
		GPIO.output(5, GPIO.HIGH)

		#wait for ack start calc
		#print("waiting for ack start calc")
		while(not acknowledged):
			if (GPIO.input(13) == 0 and GPIO.input(14) == 1 and GPIO.input(15) == 0):
				acknowledged = True
			elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				reset_pins_to_low()
				print("Received error")
				return "Received Error"
		acknowledged = False

		#send operation type:
		# GPIO.output(11, GPIO.HIGH)
		if sign == '+' :
			print('+')
			GPIO.output(2, GPIO.LOW)
			GPIO.output(3, GPIO.HIGH)
			GPIO.output(4, GPIO.HIGH)
			GPIO.output(5, GPIO.LOW)
		elif sign == '-':
			print('-')
			GPIO.output(2, GPIO.LOW)
			GPIO.output(3, GPIO.HIGH)
			GPIO.output(4, GPIO.HIGH)
			GPIO.output(5, GPIO.LOW)
		elif sign == '*':
			print('*')
			GPIO.output(2, GPIO.HIGH)
			GPIO.output(3, GPIO.LOW)
			GPIO.output(4, GPIO.LOW)
			GPIO.output(5, GPIO.LOW)
		elif sign == '/':
			print('/')
			GPIO.output(2, GPIO.HIGH)
			GPIO.output(3, GPIO.LOW)
			GPIO.output(4, GPIO.LOW)
			GPIO.output(5, GPIO.HIGH)

		#wait for ack operation type
		while(not acknowledged):
			if (GPIO.input(13) == 0 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				acknowledged = True
			elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				reset_pins_to_low()
				print("Received error")
				return "Received Error"
			# print("waiting for ack operation type")
		acknowledged = False

		#send num1 in 8 parts of 7 bits
		for section in range(0, 8):
			for pin in range (6, 13):
				place = pin + section*7
				if two_complement_56bit_num1[place-6] == '1':
					GPIO.output(pin, GPIO.HIGH)
					# print("%s%d" % ("PinH", pin))
				else:
					GPIO.output(pin, GPIO.LOW)
					# print("%s%d" % ("PinL", pin))
			if section %2 == 0:
				GPIO.output(2, GPIO.LOW)
				GPIO.output(3, GPIO.HIGH)
				GPIO.output(4, GPIO.LOW)
				GPIO.output(5, GPIO.LOW)
			else:
				GPIO.output(2, GPIO.LOW)
				GPIO.output(3, GPIO.HIGH)
				GPIO.output(4, GPIO.LOW)
				GPIO.output(5, GPIO.HIGH)

			#wait for ack num1
			while(not acknowledged):
				if section %2 == 0 and GPIO.input(13) == 1 and GPIO.input(14) == 0 and GPIO.input(15) == 0:
					acknowledged = True
				if section %2 == 1 and GPIO.input(13) == 1 and GPIO.input(14) == 0 and GPIO.input(15) == 1:
					acknowledged = True
				elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
					reset_pins_to_low()
					print("Received error")
					return "Received Error"
				elif (GPIO.input(13) == 0 and GPIO.input(14) == 0 and GPIO.input(15) == 1):
					reset_pins_to_low()
					print("debug")
					return "Debug"
				# print("waiting for ack num1")
			acknowledged = False

		#send num2 in 8 parts of 7 bits
		for section in range(0, 8):
			for pin in range(6, 13):
				place = pin + section*7
				if two_complement_56bit_num2[place-6] == '1':
					GPIO.output(pin, GPIO.HIGH)
					# print("%s%d" % ("PinH", pin))
				else:
					GPIO.output(pin, GPIO.LOW)
					# print("%s%d" % ("PinL", pin))
			if section %2 == 0:
				GPIO.output(2, GPIO.LOW)
				GPIO.output(3, GPIO.HIGH)
				GPIO.output(4, GPIO.LOW)
				GPIO.output(5, GPIO.LOW)
			else:
				GPIO.output(2, GPIO.LOW)
				GPIO.output(3, GPIO.HIGH)
				GPIO.output(4, GPIO.LOW)
				GPIO.output(5, GPIO.HIGH)

			#wait for ack num2
			while(not acknowledged):
				if section %2 == 0 and GPIO.input(13) == 1 and GPIO.input(14) == 0 and GPIO.input(15) == 0:
					acknowledged = True
				if section %2 == 1 and GPIO.input(13) == 1 and GPIO.input(14) == 0 and GPIO.input(15) == 1:
					acknowledged = True
				elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
					reset_pins_to_low()
					print("Received error")
					return "Received Error"
				elif (GPIO.input(13) == 0 and GPIO.input(14) == 0 and GPIO.input(15) == 1):
					reset_pins_to_low()
					print("debug")
					return "Debug"
				# print("waiting for ack num2")
			acknowledged = False

		#wait for solution header
		while(not acknowledged):
			if (GPIO.input(13) == 0 and GPIO.input(14) == 0 and GPIO.input(15) == 1):
				acknowledged = True
			elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				reset_pins_to_low()
				print("Received Error")
				return "Received Error"
			elif (GPIO.input(13) == 0 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				reset_pins_to_low()
				print("Received Overflow")
				return "Received Overflow"
			# print("waiting for ack solution header")
		acknowledged = False

		#wait for the right solution header and get the solution in 5 parts of 12 bits
		solution = [0]*60
		for section in range(0, 5):
			#check for the right header
			while not acknowledged:
				if section %2 == 0 and GPIO.input(13) == 0 and GPIO.input(14) == 0 and GPIO.input(15) == 1:
					acknowledged = True
				elif section %2 == 1 and GPIO.input(13) == 1 and GPIO.input(14) == 0 and GPIO.input(15) == 1:
					acknowledged = True
				elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
					reset_pins_to_low()
					print("Received Error")
					return "Received Error"
				elif (GPIO.input(13) == 0 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
					reset_pins_to_low()
					print("Received Overflow")
					return "Received Overflow"
			# print("waiting for ack solution header")
			acknowledged = False

			#get the solution in 5 parts of 12 bits
			for pin in range(16, 28):
				place = pin + section*12
				solution[place-16] = GPIO.input(pin)

		#reset all out pins to low
		reset_pins_to_low()

		#give back solution
		solution_str = ""
		for binary in solution:
			solution_str += str(binary)
		print(solution_str)
		print(isinstance(solution_str, str))
		solution_int = int(solution_str, 2)
		if solution_str[0] == '1':
			solution_int = solution_int - 2**60
		print(solution_int)

		finished = True

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
			start_array[i+1] = send_instruction(start_array[i-1], start_array[i], start_array[i+1])
		else:
			end_array.append(start_array[i])
	return end_array

# Takes the formula string and puts it into an array with ints for integers and char for symbols.
# Keeps the integers as big as possible (255 stays 255 and does not become 2, 5, 5)
def formula_to_array(formula):
	print(formula)
	#check for brackets
	while ')' in formula:
		#take part up to the first )
		old_partition = formula.partition(')')[0]
		#reverse that part and take the part up to the first (
		reversed_partition = old_partition[::-1]
		reversed_partition = reversed_partition.partition('(')[0]
		#reverse that part again and put that part as a new formula into this function (recursion)
		new_partition = reversed_partition[::-1]
		answer = formula_to_array(new_partition)
		#replace the taken formula part with the answer
		replace_str = ''.join(['(' , new_partition, ')'])
		formula = formula.replace(replace_str, str(answer), 1)
		print(formula)

	temp = ""
	array = []
	skip = False

	for index, character in enumerate(formula):
		if re.match(r"[0-9]", character):
			temp += character
		elif character == '-' and (formula[index-1] in SIGNS_1 or formula[index-1] in SIGNS_2 or (index == 0)):
			temp += character
		else:
			if len(temp) != 0:
				array.append(int(temp))
				temp = ""
			array.append(character)
	if len(temp) != 0:
		array.append(int(temp))

	print(array)

	return get_calcs(get_calcs(array, SIGNS_1), SIGNS_2)[0]

# Executes all functions necessary to calculate the formula string and get the answer
# def get_formula_answer(formula):
# 	return get_calcs(get_calcs(formula_to_array(formula), SIGNS_1), SIGNS_2)[0]

# Checks if a formula is correct or not
# Returns True if correct, False if incorrect
def check_formula_correct(formula):
	openbracket = 0
	closebracket = 0

	#check everything in this loop for every character in the formula
	for index, character in enumerate(formula):
		if index == 0 or index == len(formula)-1:
			#check if the character at index 0 is not a symbol other than minus
			if index == 0 and character in NON_DOUBLES:
				return False
			#check if the character at the last index is not a symbol
			elif index == len(formula)-1 and character in SYMBOLS:
				return False

		if character in SYMBOLS:
			#check if the next character after a symbol is not a symbol other than minus
			if formula[index+1] in NON_DOUBLES:
				return False
			#check if the next character after a minus after a symbol is not a symbol too
			elif formula[index+1] == '-' and formula[index+2] in SYMBOLS:
				return False
			#check for a open or closing bracket and count them
			elif character == '(':
				openbracket += 1
			elif character == ')':
				closebracket += 1
				#check if the number of closing brackets after finding a closing bracket
				#exceeds the number of opening brackets
				if closebracket > openbracket:
					return False
	#if formula is not deemed incorrect in the above loop, return True
	return True

# In and output. Should be retrieved form the 
# formula
#formula = str(input("Enter the operation you want to perform: "))
# formula = "-5*-3--7+666/6"
#fin_answer = 0
#if formula != "Error":
	# print(get_formula_answer(formula))
#	print(formula_to_array(formula))
#else:
#	print("Error")
