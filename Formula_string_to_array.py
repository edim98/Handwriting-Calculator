import re

#change to communicate to fpga
def fpga_calc(num1, sign, num2):
	string = str(num1)
	string += str(sign)
	string += str(num2)
	integer = int(eval(string))
	return integer

formula = "245*22/11+33/11-1"

array = []
temp = ""

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

start_array = array
end_array = []

for i in range(0, len(start_array)):
	if start_array[i] == '*':
		end_array.pop(len(end_array)-1)
		start_array[i+1] = fpga_calc(start_array[i-1], start_array[i], start_array[i+1])
	elif start_array[i] == '/':
		end_array.pop(len(end_array)-1)
		start_array[i+1] = fpga_calc(start_array[i-1], start_array[i], start_array[i+1])
	else:
		end_array.append(start_array[i])

start_array = end_array
end_array = []

for i in range(0, len(start_array)):
	if start_array[i] == '+':
		end_array.pop(len(end_array)-1)
		start_array[i+1] = fpga_calc(start_array[i-1], start_array[i], start_array[i+1])
	elif start_array[i] == '-':
		end_array.pop(len(end_array)-1)
		start_array[i+1] = fpga_calc(start_array[i-1], start_array[i], start_array[i+1])
	else:
		end_array.append(start_array[i])

print(end_array[0])