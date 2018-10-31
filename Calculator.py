import re
import RPi.GPIO as GPIO

SIGNS_1 = ('*', '/')
SIGNS_2 = ('+', '-')
SIGNS_3 = ('(', ')')

def reset_pins_to_low():
	for pin in range(2, 13):
	GPIO.output(pin, GPIO.LOW)

def send_instruction(num1, sign, num2):
	acknowledged = False
	finished = False
	error = False
	overflow = False
	solution_int = 0

	#check for overflow before sending
	if num1>1023 or num2>1023:
		return "Input number too high"

	#make sbutract calculations into add calculations
	if sign == '-':
		num2 *= -1

	two_complement_num1 = bin(num1 & int("1"*11, 2))[2:]
	two_complement_11bit_num1 = ("{0:0>%s}" % (11)).format(two_complement_num1)
	print(two_complement_11bit_num1)

	two_complement_num2 = bin(num2 & int("1"*11, 2))[2:]
	two_complement_11bit_num2 = ("{0:0>%s}" % (11)).format(two_complement_num2)
	print(two_complement_11bit_num2)

	while not finished:
		error = False
		GPIO.setmode(GPIO.BCM)
		for pin in range(2, 13):
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, GPIO.LOW)
		for pin in range(13, 28):
			GPIO.setup(pin, GPIO.IN)

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
				error = True
				print("Received error")
				break
		acknowledged = False
		if error or overflow:
			reset_pins_to_low()
			break

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
				error = True
				print("Received error")
				break
			# print("waiting for ack operation type")
		acknowledged = False
		if error or overflow:
			reset_pins_to_low()
			break

		#send num1
		for pin in range (2, 13):
			if two_complement_11bit_num1[pin-2] == '1':
				GPIO.output(pin, GPIO.HIGH)
				# print("%s%d" % ("PinH", pin))
			else:
				GPIO.output(pin, GPIO.LOW)
				# print("%s%d" % ("PinL", pin))

		#wait for ack num1
		while(not acknowledged):
			if (GPIO.input(13) == 1 and GPIO.input(14) == 0 and GPIO.input(15) == 0):
				acknowledged = True
			elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				error = True
				print("Received error")
				break
			elif (GPIO.input(13) == 0 and GPIO.input(14) == 0 and GPIO.input(15) == 1):
				print("debug")
			# print("waiting for ack num1")
		acknowledged = False
		if error or overflow:
			reset_pins_to_low()
			break

		#send num2
		for pin in range (2, 13):
			if two_complement_11bit_num2[pin-2] == '1':
				GPIO.output(pin, GPIO.HIGH)
			else:
				GPIO.output(pin, GPIO.LOW)

		#wait for ack num2
		while(not acknowledged):
			if (GPIO.input(13) == 1 and GPIO.input(14) == 0 and GPIO.input(15) == 1):
				acknowledged = True
			elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				error = True
				print("Received error")
				break
			# print("waiting for ack num2")
		acknowledged = False
		if error or overflow:
			reset_pins_to_low()
			break

		#wait for solution header
		while(not acknowledged):
			if (GPIO.input(13) == 0 and GPIO.input(14) == 0 and GPIO.input(15) == 1):
				acknowledged = True
			elif (GPIO.input(13) == 1 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
				error = True
				print("Received Error")
				break
			elif (GPIO.input(13) == 0 and GPIO.input(14) == 1 and GPIO.input(15) == 1):
					overflow = True
					print("Received Overflow")
					break;
			# print("waiting for ack solution header")
		acknowledged = False
		if error or overflow:
			reset_pins_to_low()
			break

		#get the solution (15 bits long)
		solution = [0]*12
		for pin in range (16, 28):
			solution[pin-16] = GPIO.input(pin)

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
			solution_int = solution_int - 4096
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
# formula
# formula = str(input("Enter the operation you want to perform: "))
formula = "2-5"
formula = check_formula(formula)
fin_answer = 0
if formula != "Error":
	# print(get_formula_answer(formula))
	print(formula_to_array(formula))
else:
	print("Error")
