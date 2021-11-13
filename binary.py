def revert(bit):
	if bit == "0":
		return "1"
	elif bit == "1":
		return "0"
	raise Exception("Error revertion")

def switch(binary,index):
	binary = binary[:index] + revert(binary[index]) + binary[index+1:]
	return binary

def toint(binary):
	return int(binary,2)