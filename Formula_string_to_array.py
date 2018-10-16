import re

formula = "245+33"

array = []
temp = ""

for character in range (0, len(formula)):
	print(formula[character])
	if re.match(r"[0-9]", formula[character]):
		temp += str(formula[character])
	else:
		if len(temp) != 0:
			array.append(int(temp))
			temp = ""
		array.append(formula[character])
if len(temp) != 0:
	array.append(int(temp))

print(array)

