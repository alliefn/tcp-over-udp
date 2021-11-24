import socket
import sys
import segment
import hexa
import transmitter
import receiver
import random

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

def listen_broadcast():
	print("Listening to broadcast address for clients.")

	clients = []

	while True:
		data, address = s.recvfrom(1024)
		client = str(address[0])+":"+str(address[1])
		clients.append(address)
		print("[!] Client ("+client+") found")
		cont = input("[?] Listen more? (y/n) ").lower()
		if (cont == "n" or cont != "y"):
			break
	
	print()
	
	return list_clients(clients)

def list_clients(clients):
	print(NUMBERS[len(clients)].title()+" clients found:")
	for i in range(len(clients)):
		print(str(i+1)+". "+str(clients[i][0])+":"+str(clients[i][1]))
	
	return clients

def send_and_connect(clients):
	print("\nCommencing file transfer...")

	for client in clients:
		connect(client)

def connect(client):
	IP = client[0]
	port = client[1]

	stage = "SEND_SYN"
	server_seq_num = random.randint(0, 4294967295)
	n_data_sent = 0
	n_data_received = 0
	fin = False

	while not(fin):
		if (stage == "SEND_SYN"):
			#send SYN

			syn_packet = segment.Segment()
			seq_num = server_seq_num #kirim random secure integer sebagai seq_num awal server

			#--- Nanti set seq_num sama ack_num pake go-back-n ---#
			n_data_sent += 1 #tambah satu karena mengirim paket SYN (kalo paket ACK saja tidak diinkremen)
			#--- END ---#

			syn_packet.switchFlag("SYN")
			syn_packet.setSeqNum(seq_num)

			message = hexa.byte(syn_packet.construct(),'utf-8')
			s.sendto(message, (IP, port))

			stage = "RECEIVE_SYN_ACK_SEND_ACK"
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
				n_data_received += 1 #diinkremen karena menerima paket SYN

				seq_num = server_seq_num + n_data_sent
				ack_num = server_seq_num + n_data_received
				curr_ack_num = ack_num
				#--- END ---#

				ack_packet.switchFlag("ACK")
				ack_packet.setSeqNum(seq_num)
				ack_packet.setAckNum(ack_num)

				message = hexa.byte(ack_packet.construct(),'utf-8')
				s.sendto(message, (IP, port))

				print("\nACK sent to client "+IP+":"+str(port)+" with seq num: "+str(seq_num)+" and ack num: "+str(ack_num))

				stage = "SEND_FILE"

		elif (stage == "SEND_FILE"):
			print("\nSending file...")
			tm = transmitter.Transmitter(server_seq_num + n_data_received)
			'''
				Go-Back-N-ARQ starts here
			'''
			tm.prepareSegment("./test.mp4")
			message = tm.transmitSegment(0)
			s.sendto(message, (IP, port))

			r = receiver.Receiver()
			rec_packet = segment.Segment()

			rec_packet.build(r.receiveSegment(data))
			n_data_sent += len(tm.segmentQueue[0].getPayLoad())
			'''
				Go-Back-N-ARQ ends here
			'''
			stage = "FIN"

		elif (stage == "FIN"):
			data, address = s.recvfrom(32777)
			rec_packet = segment.Segment()
			r = receiver.Receiver()

			rec_packet.build(r.receiveSegment(data))

			if (r.isAckSegment(rec_packet)):
				#server receive ACK of file sent
				seq_num0 = rec_packet.getSeqNum()
				ack_num0 = rec_packet.getAckNum()

				print("\nACK received from client "+address[0]+":"+str(address[1])+" with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

				if ((address[0] == IP) and (address[1] == port)):
					print("\nClosing connection with client: "+IP+":"+str(port))

					#server send FIN to close connection
					
					fin_packet = segment.Segment()

					#--- Nanti set seq_num sama ack_num pake go-back-n ---#
					seq_num = server_seq_num + n_data_sent
					ack_num = server_seq_num + n_data_received
					
					n_data_sent += 1
					#--- END ---#

					fin_packet.switchFlag("FIN")
					fin_packet.setSeqNum(seq_num)
					fin_packet.setAckNum(ack_num)

					message = hexa.byte(fin_packet.construct(), 'utf-8')
					s.sendto(message, (IP, port))

					print("\nFIN sent to client "+IP+":"+str(port)+" with seq num: "+str(seq_num)+" and ack_num: "+str(ack_num))

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

								print(address)

								if ((address[0] == IP) and (address[1] == port)):
									#if correct client wants to close

									print("\nFIN received from client "+address[0]+":"+str(address[1])+" with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

									ack_packet = segment.Segment()

									#--- Nanti set seq_num sama ack_num pake go-back-n ---#
									n_data_received += 1

									seq_num = server_seq_num + n_data_sent
									ack_num = server_seq_num + n_data_received
									#--- END ---#

									ack_packet.switchFlag("ACK")
									ack_packet.setSeqNum(seq_num)
									ack_packet.setAckNum(ack_num)

									message = hexa.byte(ack_packet.construct(), 'utf-8')
									s.sendto(message, (IP, port))

									print("\nACK sent to client "+IP+":"+str(port)+" with seq_num: "+str(seq_num)+" and ack_num: "+str(ack_num))

									fin = True #close connection

									print("\nConnection with client "+IP+":"+str(port)+" closed.")


# Main Program
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if (len(sys.argv) > 1):
	port = int(sys.argv[1])
	print("Server started at port "+str(port)+"...")

else:
	print("Port number not specified. Run: 'python server.py <port-number>'")
	exit()

hostname = socket.gethostname()
print(hostname)
local_ip = socket.gethostbyname(hostname)
print(local_ip)

s.bind(('127.0.0.1',port))
clients = listen_broadcast()
send_and_connect(clients)