import socket
import sys
import segment
import hexa
import transmitter
import receiver
import random
from connection import Connection

NUMBERS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]

'''
Pseudocode:

1. Program menambil port dari input terminal (args)
2. Server menginisialisasi broadcast address
3. Server listen pada port yang diambil di poin 1
4. Saat mendapat request dari client
		- ambil portnya dan simpan di suatu list
		- jika pengguna masih ingin memperoleh client
			- bila ya, maka ulangi step 3
			- bila tidak, lanjut poin 5
5. Untuk setiap client yang ada pada list
		- lakukan 3-way handshake untuk setiap client
		- prepare segmentnya
			- ambil filenya dari filepath yang diminta client
			- jalankan method prepareSegment
		- kirim menggunakan protokol go back n arq
		- close koneksi bila sudah selesai
6. Ulangi sampai pengguna menyelesaikan program server
'''

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if (len(sys.argv) > 1):
	port = int(sys.argv[1])
	print("Server started at port "+str(port)+"...")
else:
	print("Port number not specified. Run: 'python server.py <port-number> </path/to/file>'")
	exit()

if (len(sys.argv) > 2):
	filepath = sys.argv[2]
else:
	print("File not specified. Run: 'python server.py <port-number> </path/to/file>'")
	exit()

s.bind(('127.0.0.1',port))

def listen_broadcast():
	print("Listening to broadcast address for clients.")

	clients = []

	while True:
		data, address = s.recvfrom(1024)
		client = str(address[0])+":"+str(address[1])
		connectionObj = Connection(address[0], address[1], 0)
		clients.append(connectionObj)
		print("[!] Client ("+client+") found")
		cont = input("[?] Listen more? (y/n) ").lower()
		if (cont == "n" or cont != "y"):
			break
	
	print()
	
	return list_clients(clients)

def list_clients(clients):
	print(NUMBERS[len(clients)].title()+" clients found:")
	for i in range(len(clients)):
		print(str(i+1)+". "+str(clients[i].IP)+":"+str(clients[i].port))
	
	return clients

def send_and_connect(clients, filepath):
	print("\nCommencing file transfer...")

	# server menghubungi setiap client dan mengirim filenya
	for client in clients:
		connect(client, filepath)

	print("\n\nFiles sent. Closing connection...\n")

	# server mengakhiri hubungan dengan setiap client
	for client in clients:
		closeConnection(client)

def connect(clientConnection, filepath):
	IP = clientConnection.IP
	port = clientConnection.port

	stage = "SEND_SYN"
	server_seq_num = random.randint(0, 4294967295)
	clientConnection.server_seq_num = server_seq_num
	fin = False

	while not(fin):
		# 1. server kirim SYN ke client untuk memulai koneksi
		if (stage == "SEND_SYN"):
			syn_packet = segment.Segment()
			seq_num = server_seq_num #kirim random secure integer sebagai seq_num awal server

			#--- Nanti set seq_num sama ack_num pake go-back-n ---#
			clientConnection.n_data_sent += 1 #tambah satu karena mengirim paket SYN (kalo paket ACK saja tidak diinkremen)
			#--- END ---#

			syn_packet.switchFlag("SYN")
			syn_packet.setSeqNum(seq_num)

			message = hexa.byte(syn_packet.construct(),'utf-8')
			s.sendto(message, (IP, port))

			print("\nSYN sent to client "+IP+":"+str(port)+" with seq num: "+str(seq_num))

			stage = "RECEIVE_SYN_ACK_SEND_ACK"
		
		# 2. server menerima SYN-ACK dari client, lalu mengirim ACK untuk acknowledge SYN tersebut
		elif (stage == "RECEIVE_SYN_ACK_SEND_ACK"):
			data, address = s.recvfrom(32777)
			rec_packet = segment.Segment()
			r = receiver.Receiver()

			rec_packet.build(r.receiveSegment(data))

			if (r.isSynSegment(rec_packet) and r.isAckSegment(rec_packet)):
				seq_num0 = rec_packet.getSeqNum()
				ack_num0 = rec_packet.getAckNum()

				print("\nSYN-ACK received from client "+address[0]+":"+str(address[1])+" with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

				ack_packet = segment.Segment()

				#--- Nanti set seq_num sama ack_num pake go-back-n ---#
				clientConnection.n_data_received += 1 #diinkremen karena menerima paket SYN

				seq_num = server_seq_num + clientConnection.n_data_sent
				ack_num = server_seq_num + clientConnection.n_data_received
				#--- END ---#

				ack_packet.switchFlag("ACK")
				ack_packet.setSeqNum(seq_num)
				ack_packet.setAckNum(ack_num)

				message = hexa.byte(ack_packet.construct(),'utf-8')
				s.sendto(message, (IP, port))

				print("\nACK sent to client "+IP+":"+str(port)+" with seq num: "+str(seq_num)+" and ack num: "+str(ack_num))

				stage = "SEND_FILE"

		# 3. server mengirim file
		elif (stage == "SEND_FILE"):
			print("\nSending file...")
			tm = transmitter.Transmitter(server_seq_num + clientConnection.n_data_received)
			tm.prepareSegment(filepath)

			#--- SLIDING WINDOW, belum konkuren ---#
			for i in range(len(tm.segmentQueue)):

				#--- DRAFT TRANSMIT ---#
				message = tm.transmitSegment(i) #kirim segmen ke-i
				s.sendto(message, (IP, port))

				clientConnection.n_data_sent += len(tm.segmentQueue[i].getPayLoad())
				#--- END ---#


				#--- DRAFT RECEIVE ACK, belum konkuren ---#
				data, address = s.recvfrom(32777)
				rec_packet = segment.Segment()
				r = receiver.Receiver()

				rec_packet.build(r.receiveSegment(data))

				if (r.isAckSegment(rec_packet)):
					#server receive ACK of file sent
					seq_num0 = rec_packet.getSeqNum()
					ack_num0 = rec_packet.getAckNum()

					print("\nACK received from client "+address[0]+":"+str(address[1])+" with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))
				
			#--- SLIDING WINDOW ---#

			# 4. urusan sudah selesai, server berhenti mengirim koneksi

			fin = True


def closeConnection(clientConnection):
	IP = clientConnection.IP
	port = clientConnection.port
	server_seq_num = clientConnection.server_seq_num
	fin = False

	#--- CLOSING ---#

	print("\nClosing connection with client: "+IP+":"+str(port))

	#server send FIN to close connection

	fin_packet = segment.Segment()

	seq_num = server_seq_num + clientConnection.n_data_sent
	ack_num = server_seq_num + clientConnection.n_data_received
	
	clientConnection.n_data_sent += 1

	fin_packet.switchFlag("FIN")
	fin_packet.setSeqNum(seq_num)
	fin_packet.setAckNum(ack_num)

	message = hexa.byte(fin_packet.construct(), 'utf-8')
	s.sendto(message, (IP, port))

	print("\nFIN sent to client "+IP+":"+str(port)+" with seq num: "+str(seq_num)+" and ack_num: "+str(ack_num))

	while (fin != True):
		data, address = s.recvfrom(32777)
		rec_packet = segment.Segment()
		r = receiver.Receiver()

		rec_packet.build(r.receiveSegment(data))

		if (r.isAckSegment(rec_packet)):
			#server receive ACK of server's FIN
			if ((address[0] == IP) and (address[1] == port)):
				seq_num0 = rec_packet.getSeqNum()
				ack_num0 = rec_packet.getAckNum()

				print("\nACK received from client "+address[0]+":"+str(address[1])+" with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

				data, address = s.recvfrom(32777)
				rec_packet = segment.Segment()
				r = receiver.Receiver()

				rec_packet.build(r.receiveSegment(data))

				if (r.isFinSegment(rec_packet)):
					#sender receive FIN to close connection
					seq_num0 = rec_packet.getSeqNum()
					ack_num0 = rec_packet.getAckNum()

					if ((address[0] == IP) and (address[1] == port)):
						#if correct client wants to close

						print("\nFIN received from client "+address[0]+":"+str(address[1])+" with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

						ack_packet = segment.Segment()

						#--- Nanti set seq_num sama ack_num pake go-back-n ---#
						clientConnection.n_data_received += 1

						seq_num = server_seq_num + clientConnection.n_data_sent
						ack_num = server_seq_num + clientConnection.n_data_received
						#--- END ---#

						ack_packet.switchFlag("ACK")
						ack_packet.setSeqNum(seq_num)
						ack_packet.setAckNum(ack_num)

						message = hexa.byte(ack_packet.construct(), 'utf-8')
						s.sendto(message, (IP, port))

						print("\nACK sent to client "+IP+":"+str(port)+" with seq_num: "+str(seq_num)+" and ack_num: "+str(ack_num))

						fin = True #close connection

						print("\nConnection with client "+IP+":"+str(port)+" closed.")

#--- Main ---#

clients = listen_broadcast()

send_and_connect(clients, filepath)
