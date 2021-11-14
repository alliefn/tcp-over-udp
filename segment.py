import hexa
import binary

'''
This is a representation of TCP segment in the form of a python class.
Every byte written in the form of hexadecimals or hexstring.
'''

PAYLOAD_MAX_SIZE = 4092 # bytes or 32768 bits

ZERO_2BYTES = "0000"
ZERO_4BYTES = ZERO_2BYTES*2

class Segment:

	def __init__(self):
		'''
		Basic constructor, all bits are zeros
		'''
		self.seqNum = ZERO_4BYTES
		self.ackNum = ZERO_4BYTES
		self.flagsAndEmpty = ZERO_2BYTES
		self.checkSum = ZERO_2BYTES
		self.payLoad = ""

	def getSeqNum(self) -> int:
		'''
		[DESC]
			Method returning sequence number in integer form
		[RETURNS]
			int : sequence number
		'''
		return hexa.toint(self.seqNum)

	def setSeqNum(self,num : int):
		'''
		[DESC]
			Method to set sequence number with an integer argument
		[PARAMS]
			num : int
		'''
		self.seqNum = hexa.inttohex(num)

	def getAckNum(self) -> int:
		'''
		[DESC]
			Method returning acknowledgement number in integer form
		[RETURNS]
			int : acknowledgement number
		'''
		return hexa.toint(self.ackNum)

	def setAckNum(self,num : int):
		'''
		[DESC]
			Method to set sequence number with an integer argument
		[PARAMS]
			num : int
		'''
		self.ackNum = hexa.inttohex(num)

	def getBinFlag(self) -> str:
		'''
		[DESC]
			Method returning the binary form of flags field
		[RETURNS]
			str : binary form of the flags field
		'''
		binFlagAndEmpty = hexa.tobin(self.flagsAndEmpty)
		binFlag = binFlagAndEmpty[:8]
		return binFlag

	def switchFlag(self,flagType : str):
		'''
		[DESC]
			Method to switch wether to on or off the flag.
			Allowed flagType : "SYN", "ACK", "FIN", "DATA"
		[PARAMS]
			flagType : str
		'''
		binFlag = self.getBinFlag()
		if flagType == "SYN":
			binFlag = binary.switch(binFlag,6)
		elif flagType == "ACK":
			binFlag = binary.switch(binFlag,3)
		elif flagType == "FIN":
			binFlag = binary.switch(binFlag,7)
		elif flagType == "DATA":
			binFlag = "00000000"

		intFlagAndEmpty = binary.toint(binFlag + "00000000")
		self.flagsAndEmpty = hexa.inttohex(intFlagAndEmpty)

	def getCheckSum(self) -> int:
		'''
		[DESC]
			Method returning the checksum field in the integer form
		[RETURNS]
			int : checksm in integer form
		'''
		return hexa.toint(self.checkSum)

	def compileCheckSum(self):
		'''
		[DESC]
			Method to calculate the checksum field using 16 bit one's complement
		'''
		seqNumChunks = hexa.split2byte(self.seqNum)
		ackNumChunks = hexa.split2byte(self.ackNum)
		flagsAndEmptyChunks = hexa.split2byte(self.flagsAndEmpty)
		payLoadChunks = hexa.split2byte(self.payLoad)

		allChunks = seqNumChunks + ackNumChunks + flagsAndEmptyChunks + payLoadChunks

		while len(allChunks) > 1:
			res = 0
			for chunk in allChunks:
				res ^= hexa.toint(chunk)
			allChunks = hexa.split2byte(hexa.inttohex(res))

		self.checkSum = allChunks[0]

	def loadPayLoad(self,payLoad : str):
		'''
		[DESC]
			Method to load the payload field in the form of hexstring
		[PARAMS]
			payLoad : str
		'''

		# one hexstring character == 0.5 byte, so the maximum payLoad hexstring size is 8192
		if len(payLoad) > PAYLOAD_MAX_SIZE * 2:
			raise Exception("Payload cannot exceed more than 4096 bytes or 32768 bit")

		self.payLoad = payLoad

	def construct(self):
		'''
		[DESC]
			Method to construct the whole segment into hexstring
		[RETURNS]
			str : whole segment in the form of hexstring
		'''
		result = self.seqNum + self.ackNum + self.flagsAndEmpty + self.checkSum + self.payLoad
		return result

	def build(self,constructedSegment):
		'''
		[DESC]
			Method to convert hexstring segment into the object form
		'''
		self.seqNum = constructedSegment[:8]
		self.ackNum = constructedSegment[8:16]
		self.flagsAndEmpty = constructedSegment[16:20]
		self.checkSum = constructedSegment[20:24]
		self.payLoad = constructedSegment[24:]