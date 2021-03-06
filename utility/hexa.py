from typing import List

'''
Group of functions to handle hexstring.
'''

def hexstring(bytes_obj : bytes) -> str:
	'''
	[DESC]
		Function to convert a string (e.g. "Hello World") into the form of hexstring
	[PARAMS]
		bytes_obj : bytes
	[RETURNS]
		str : hexstring form of the original string/text
	'''
	return "".join([inttohex(i,2) for i in bytes_obj])

def byte(hexstring : str, encoding : str) -> bytes:
	'''
	[DESC]
		Function to convert a hexstring (e.g. "ff00a3e8") into the form of bytes
	[PARAMS]
		hexstring : str
	[RETURNS]
		bytes : byte object
	'''
	bytes_obj = bytes.fromhex(hexstring)
	return bytes_obj

def toint(hexstring : str) -> int:
	'''
	[DESC]
		Function to convert a hexstring into the form of number (python integer)
	[PARAMS]
		hexstring : str
	[RETURNS]
		int : python integer form of the hexstring
	'''
	return int(hexstring,16)

def tobin(hexstring : str, formating : int) -> str:
	'''
	[DESC]
		Function to convert a hexstring into the form of binary string (e.g. "01001100")
	[PARAMS]
		hexstring : str
		formating : int
	[RETURNS]
		str : binary string form of the hexstring
	'''
	intval = toint(hexstring)
	res = bin(intval)[2:]
	if len(res)%formating != 0:
		res = "0" * (formating-len(res)%formating) + res
	return res

def inttohex(num : int, formating : int) -> str:
	'''
	[DESC]
		Function to convert an integer into the form of hexstring
	[PARAMS]
		num : int
		formating : int (2,4,8)
	[RETURNS]
		str : hexstring form of the integer number
	'''
	res = None
	if formating == 2:
		res = '{:02x}'.format(num)
		if len(res)%2 == 1:
			res = "0" + res
	elif formating == 4:
		res = '{:04x}'.format(num)
		if len(res)%4 != 0:
			res = "0" * (4-len(res)%4) + res
	elif formating == 8:
		res = '{:08x}'.format(num)
		if len(res)%8 != 0:
			res = "0" * (8-len(res)%8) + res
	return res

def split2byte(hexstring : str) -> List[str]:
	'''
	[DESC]
		Function to split hexstring into a chunk of size of 2 bytes (4 hexchar == 2 bytes)
	[PARAMS]
		hexstring : str
	[RETURNS]
		List[str] : list of 2 bytes hexstring chunks
	'''
	n = 4 # 1 hex letter == 0.5 byte ==> 4 hex letter == 2 bytes
	hex_len_remainder = len(hexstring) % 4
	hexstring_ = hexstring
	if hex_len_remainder != 0:
		hexstring_ = "0" * (4 - hex_len_remainder) + hexstring
	chunks = [hexstring_[i:i+n] for i in range(0,len(hexstring_),n)]
	return chunks