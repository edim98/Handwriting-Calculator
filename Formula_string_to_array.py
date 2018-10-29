import re

SIGNS_1 = ('*', '/')
SIGNS_2 = ('+', '-')
SIGNS_3 = ('(', ')')

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
	elif formula[0] == '-':
		return "Error"
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
# formula = check_formula(formula)
fin_answer = 0
# if formula != "Error":
	# print(get_formula_answer(formula))
fin_answer = formula_to_array(formula)
# else:
print(fin_answer)