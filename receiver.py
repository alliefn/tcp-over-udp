import segment

'''
This is a representation of TCP receiver in the form of python class.
'''

class Receiver:
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