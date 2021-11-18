import math
import file
import filehandler
import segment

'''
Representation of a TCP transmitter in the form of a python class
'''

class Transmitter:	
	def __init__(self):
		'''
		[DESC]
			Default constructor, consist of some attribute:
			- segmentQueue : queue of segments
		'''
		self.segmentQueue = []

	def prepareSegment(self,filePath : str):
		'''
		[DESC]
			Method to prepare the segment queue by loading the file
		[PARAMS]
			filePath : str
		'''
		handler = filehandler.FileHandler()
		fileHexString = handler.dumpFile(filePath)
		counter = 1
		for i in range(0,len(fileHexString),segment.PAYLOAD_MAX_HEXLENGTH):
			s = segment.Segment()
			s.setSeqNum(counter)
			s.loadPayLoad(fileHexString[i:i + segment.PAYLOAD_MAX_HEXLENGTH])
			self.segmentQueue.append(s)
			counter += 1

	def transmitSegment(index : int) -> str: # incomplete
		'''
		[DESC]
			Method to send the segment in the form of hexstring
		'''
		return self.segmentQueue[index].construct()