def encode(string : str):
	return "".join("{:02x}".format(ord(c)) for c in string)

def decode(hexstring : str):
	bytes_obj = bytes.fromhex(hexstring)
	return bytes_obj.decode("utf-8")

def toint(hexstring : str):
	return int(hexstring,16)

def inttohex(num : int):
	res = '{:02x}'.format(num)
	if len(res)%2 == 1:
		res = "0" + res
	return res