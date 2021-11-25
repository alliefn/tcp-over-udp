'''
Group of functions to handle binary string
'''

def revert(bit : str) -> str:
	'''
	[DESC]
		Function to revert a bit from 0 to 1 or 1 to 0
	[PARAMS]
		bit : str
	[RETURNS]
		str : a reverted bit
	'''
	if bit == "0":
		return "1"
	elif bit == "1":
		return "0"
	raise Exception('Error revertion, bit should be "1" or "0"')

def switch(binary : str,index : str) -> str:
	'''
	[DESC]
		Function to revert a certain bit in a binary string (e.g. "00011010") located in a certain index
	[PARAMS]
		binary : str
		index : int
	[RETURNS]
		str : new binary string
	'''
	binary = binary[:index] + revert(binary[index]) + binary[index+1:]
	return binary

def toint(binary : str) -> int:
	'''
	[DESC]
		Function to revert a binary string into the integer form
	[PARAMS]
		binary : str
	[RETURNS]
		int : python integer form of a binary string
	'''
	return int(binary,2)

def onescomplement(binary : str) -> str:
	'''
	[DESC]
		Function to revert every bit in the binary string (one's complement method)
	[PARAMS]
		binary : str
	[RETURNS]
		str : binary string
	'''
	result = ""
	for b in binary:
		result += revert(b)
	return result