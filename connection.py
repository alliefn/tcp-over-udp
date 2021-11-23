class Connection:
	def __init__(self, IP, port, initial_seq_num):
		self.IP = IP
		self.port = port
		self.name = IP+":"+str(port)
		self.initial_seq_num = initial_seq_num
		self.n_data_sent = 0
		self.n_data_received = 0