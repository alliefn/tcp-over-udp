import hexa
import binary

PAYLOAD_MAX_SIZE = 32768 #bits (according to website and bytes according to tubes spec)

ZERO_2BYTES = hexa.encode("0")

# Segment representation in the form of a python class
class Segment:

	# segment written in hexa decimals
	def __init__(self):
		self.seqNum = ZERO_2BYTES
		self.ackNum = ZERO_2BYTES
		self.flagsAndEmpty = ZERO_2BYTES
		self.checkSum = ZERO_2BYTES
		self.payLoad = ZERO_2BYTES

	def getSeqNum():
		return hexa.toint(self.seqNum)

	def setSetNum(num : int):
		self.seqNum = hexa.inttohex(num)

	def getAckNum():
		return hexa.toint(self.ackNum)

	def setAckNum(num):
		self.ackNum = hexa.inttohex(num)

	def getBinFlag():
		intFlagAndEmpty = hexa.toint(self.flagsAndEmpty)
		binFlagAndEmpty = bin(intFlagAndEmpty)[2:]
		binFlag = binFlagAndEmpty[:8]
		return binFlag

	def switchFlag(flagType):
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

	def isSyn():
		binFlag = self.getBinFlag()
		return binFlag[6] == "1"

	def isAck():
		binFlag = self.getBinFlag()
		return binFlag[3] == "1"

	def isFin():
		binFlag = self.getBinFlag()
		return binFlag[7] == "1"

	def isData():
		binFlag = self.getBinFlag()
		return binFlag == "00000000"

	def getCheckSum():
		return hexa.toint(self.checkSum)