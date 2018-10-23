import re

SIGNS_1 = ('*', '/')
SIGNS_2 = ('+', '-')

#change to communicate to fpga
def fpga_calc(num1, sign, num2):
	string = str(num1)
	string += str(sign)
	string += str(num2)
	integer = int(eval(string))
	return integer

def get_calcs(start_array, signs):
	end_array = []
	for i in range(0, len(start_array)):
		if start_array[i] in signs:
			end_array.pop(len(end_array)-1)
			start_array[i+1] = fpga_calc(start_array[i-1], start_array[i], start_array[i+1])
		else:
			end_array.append(start_array[i])
	return end_array

def formula_to_array(formula):
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
	return array

def get_formula_answer(formula):
	return get_calcs(get_calcs(formula_to_array(formula), SIGNS_1), SIGNS_2)[0]



formula = "245*22/11+33/11-1"
print(get_formula_answer(formula))