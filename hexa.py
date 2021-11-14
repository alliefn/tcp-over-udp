from typing import List

'''
Group of functions to handle hexstring.
'''

def encode(string : str) -> str:
	'''
	[DESC]
		Function to convert a string (e.g. "Hello World") into the form of hexstring
	[PARAMS]
		string : str
	[RETURNS]
		str : hexstring form of the original string/text
	'''
	return "".join("{:02x}".format(ord(c)) for c in string)

def decode(hexstring : str) -> str:
	'''
	[DESC]
		Function to convert a hexstring (e.g. "ff00a3e8") into the form of regular string
	[PARAMS]
		hexstring : str
	[RETURNS]
		str : regular string
	'''
	bytes_obj = bytes.fromhex(hexstring)
	return bytes_obj.decode("utf-8")

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

def tobin(hexstring : str) -> str:
	'''
	[DESC]
		Function to convert a hexstring into the form of binary string (e.g. "01001100")
	[PARAMS]
		hexstring : str
	[RETURNS]
		str : binary string form of the hexstring
	'''
	intval = toint(hexstring)
	res = bin(intval)[2:]
	if len(res)%2 == 1:
		res = "0" + res
	return res

def inttohex(num : int) -> str:
	'''
	[DESC]
		Function to convert an integer into the form of hexstring
	[PARAMS]
		num : int
	[RETURNS]
		str : hexstring form of the integer number
	'''
	res = '{:02x}'.format(num)
	if len(res)%2 == 1:
		res = "0" + res
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