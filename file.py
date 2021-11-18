import os

'''
Representation of file in a python class
'''
class File:
	def __init__(self,filePath : str):
		'''
		[DESC]
			Defalt constructor, consist of some attributes:
			- name : file name without extension
			- extension : the extension of the file
			- content : the content inside the file in the form of bytes
		[PARAMS]
			filePath : str
		'''
		f = open(filePath,"rb")
		fileNameAndExtension = os.path.splitext(os.path.basename(filePath))
		self.name = fileNameAndExtension[0]
		self.extension = fileNameAndExtension[1]
		self.content = f.read()
		f.close()

	def getFileName(self) -> str:
		'''
		[DESC]
			Return the file name tailed by the extension
		[RETURNS]
			str : file name tailed by extension
		'''
		return self.name + self.extension