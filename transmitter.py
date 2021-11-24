import math
import file
import filehandler
import segment
import hexa

'''
Representation of a TCP transmitter in the form of a python class
'''

class Transmitter:	
	def __init__(self, counter_start=1):
		'''
		[DESC]
			Default constructor, consist of some attribute:
			- segmentQueue : queue of segments
		'''
		self.segmentQueue = []
		self.counter = counter_start

	def prepareSegment(self,filePath : str):
		'''
		[DESC]
			Method to prepare the segment queue by loading the file
		[PARAMS]
			filePath : str
		'''
		handler = filehandler.FileHandler()
		fileHexString = handler.dumpFile(filePath)
		for i in range(0,len(fileHexString),segment.PAYLOAD_MAX_HEXLENGTH):
			s = segment.Segment()
			s.setSeqNum(self.counter)
			s.loadPayLoad(fileHexString[i:i + segment.PAYLOAD_MAX_HEXLENGTH])
			s.switchFlag("DATA")
			self.segmentQueue.append(s)
			self.counter += len(s.getPayLoad())
			print(self.counter)
		
	def hasNextSegment(self) -> bool:
		'''
		[DESC]
			Method to check if there is still segment to be transmitted
		[PARAMS]
			None
		'''
		return len(self.segmentQueue) != 0

	def getNextSegment(self) -> segment.Segment:
		'''
		[DESC]
			Method to get the next segment to be transmitted
		'''
		return self.segmentQueue.pop(0)

	def getSeqNum(self) -> int:
		'''
		[DESC]
			Method to get the sequence number of the next segment to be transmitted
		'''
		return self.segmentQueue[0].getSeqNum()


	def transmitSegment(self,index : int) -> bytes:
		'''
		[DESC]
			Method to send the segment in the form of hexstring
		'''
		return hexa.byte(self.segmentQueue[index].construct(),'utf-8')