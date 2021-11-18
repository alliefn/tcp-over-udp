import pickle
import file
import hexa
import math

'''
Class to handle the file
'''

class FileHandler:
	def dumpFile(self,filePath : str) -> str:
		'''
		[DESC]
			Method to convert a file class from file.File into the form of hexstring
		[PARAMS]
			filePath : str
		[RETURNS]
			str : hexstring result
		'''
		file_ = file.File(filePath)
		dumpRes = pickle.dumps(file_) # byte obj
		fileHexString =  hexa.encode(dumpRes) #str
		return fileHexString