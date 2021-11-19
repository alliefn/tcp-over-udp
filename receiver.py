from segment import Segment
import hexa

'''
This is a representation of TCP receiver in the form of python class.
'''

class Receiver:

	def checkSumAlgorithm(self,segmentString : str) -> str:
		'''
		[DESC]
			Method to check the checksum value of a segment
		[PARAMS]
			segmentString : str (segment in the form of hexstring)
		[RETURNS]
			str : checksum hexstring
		'''
		segment = Segment()
		segment.build(segmentString)
		seqNumChunks = hexa.split2byte(segment.seqNum)
		ackNumChunks = hexa.split2byte(segment.ackNum)
		flagsAndEmptyChunks = hexa.split2byte(segment.flagsAndEmpty)
		checkSumChunk = hexa.split2byte(segment.checkSum)
		payLoadChunks = hexa.split2byte(segment.payLoad)

		allChunks = seqNumChunks + ackNumChunks + flagsAndEmptyChunks + checkSumChunk + payLoadChunks 

		while len(allChunks) > 1:
			res = 0
			for chunk in allChunks:
				res ^= hexa.toint(chunk)
			allChunks = hexa.split2byte(hexa.inttohex(res,4))
		return allChunks[0]

	def isNotBroken(self,segmentString : str) -> bool:
		'''
		[DESC]
			Method to check wether a segment is broken or not
		[PARAMS]
			segmentString : str (segment in the form of hexstring)
		[RETURNS]
			boolean : True if segnment is not broken, else False
		'''
		return self.checkSumAlgorithm(segmentString) == "ffff"

	def isSynSegment(self,segment : Segment) -> bool:
		'''
		[DESC]
			Method to check a segment wether it is a SYN segment or not
		[PARAMS]
			segment : Segment
		[RETURNS]
			boolean : True if segment is a SYN segment , else False
		'''
		binFlag = segment.getBinFlag()

		return binFlag[6] == "1"

	def isAckSegment(self,segment : Segment) -> bool:
		'''
		[DESC]
			Method to check a segment wether it is an ACK segment or not
		[PARAMS]
			segment : Segment
		[RETURNS]
			boolean : True if segment is an ACK segment , else False
		'''
		binFlag = segment.getBinFlag()
		return binFlag[3] == "1"

	def isFinSegment(self,segment : Segment) -> bool:
		'''
		[DESC]
			Method to check a segment wether it is a FIN segment or not
		[PARAMS]
			segment : Segment
		[RETURNS]
			boolean : True if segment is a FIN segment , else False
		'''
		binFlag = segment.getBinFlag()
		return binFlag[7] == "1"

	def isDataSegment(self,segment : Segment) -> bool:
		'''
		[DESC]
			Method to check a segment wether it is a regular segment (only consist of payload data)
			or not
		[PARAMS]
			segment : Segment
		[RETURNS]
			boolean : True if segment is a regular segment , else False
		'''
		binFlag = segment.getBinFlag()
		return binFlag == "00000000"

	def receiveSegment(self,segmentByte : bytes) -> str:
		'''
		[DESC]
			Method to receive segment
		'''
		return hexa.hexstring(segmentByte)