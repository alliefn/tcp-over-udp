import socket
import sys
import segment
import hexa
import receiver
import time
from connection import Connection
import pickle

'''
Pseudocode
1. Program mengambil port dari input user (args)
2. Program melakukan koneksi dengan server (mengirim request, isinya port client dengan broadcast address)
3. Client tinggal mengikuti prosedur protokol dari server (3 way handshake)
4. Dalam keberlangsungan pengiriman (Go back n arq) lakukan
		- pemeriksaan apakah segmen yang diperoleh rusak atau tidak
		- jika tidak rusak, kirim acknowledgement kepada server
		- jika rusak abaikan
5. Menyudahi koneksi dengan server
6. Menutup program
'''

#--- Client compile file
def saveFile(segmentPool, folderpath):
	filename = input("\nSaving file...\n\nFile name: ")
	if ("." in filename):
		filename = filename[0:filename.index(".")+1]
	
	res = ""
	for s in segmentPool:
		res += s

	res = hexa.byte(res,'latin-1')

	res = pickle.loads(res)
	res.name = filename

	f = open(folderpath + "/" + res.name + ".txt", "wb")
	f.write(res.content)
	f.close()

#--- Initialize broadcast socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
host = socket.gethostname()
print("Host: "+str(host))

if (len(sys.argv) > 1):
	port = sys.argv[1]
	if (int(port) > 1400 or int(port) < 1300):
		print("Port number must be between 1300 and 1400")
		sys.exit()
	s.bind(('127.0.0.1', int(port)))
else:
	print("Port number not specified. Run: 'python client.py <port-number> </path/to/folder>'")
	print("Note: Due to program limitations. Port must be between 1300 and 1400.")
	exit()

if (len(sys.argv) > 2):
	folderpath = sys.argv[2]
else:
	print("Folder not specified. Run: 'python client.py <port-number> </path/to/folder>'")
	exit()

#--- Send broadcast

port_found = False
for port_ in range(1300,1401):
	try:
		s.sendto(str(port_).encode(), ('127.0.0.1', port_))
		data, addr = s.recvfrom(1024)
		if (data.decode() == "Yes" and int(port_) != int(port)):
			# Found server
			print("Server found at port "+str(port_))
			port_found = True
			time.sleep(0.5)
			print("Awaiting server actions... Please wait.")
			break
	except:
		pass

if (not port_found):
	print("No server responded. Please try again later.")
	exit()

#--- TCP over UDP, receive file from server

fin = False
serverConnection = Connection('127.0.0.1', 1337, 0)
stage = "RECEIVE_SYN_SEND_SYN_ACK"
received_data = None

segmentPool = []

while (not(fin)):
	# 1. client menerima SYN dari server, lalu mengirim SYN-ACK
	if (stage == "RECEIVE_SYN_SEND_SYN_ACK"):
		data, address = s.recvfrom(32777)
	
		r = receiver.Receiver()
		rec_packet = segment.Segment()

		rec_packet.build(r.receiveSegment(data))

		if (r.isSynSegment(rec_packet) and not(r.isAckSegment(rec_packet))):
			#if server send SYN untuk memulai koneksi
			seq_num0 = rec_packet.getSeqNum()
			serverConnection.server_seq_num = seq_num0

			print("\nSYN received with seq num: "+str(seq_num0))

			ack_packet = segment.Segment()

			#--- Nanti set seq_num sama ack_num pake go-back-n?? ---#
			serverConnection.n_data_received += 1

			seq_num = serverConnection.server_seq_num #paket pertama, random sequence number
			ack_num = seq_num0 + serverConnection.n_data_received #ekspektasi: seq_num berikut adalah seq_num + 1

			serverConnection.n_data_sent += 1
			#--- END ---#

			ack_packet.switchFlag("SYN")
			ack_packet.switchFlag("ACK")
			ack_packet.setSeqNum(seq_num)
			ack_packet.setAckNum(ack_num)

			message = hexa.byte(ack_packet.construct(),'utf-8')
			s.sendto(message, (address[0], address[1]))

			print("\nSYN-ACK sent with seq_num: "+str(seq_num)+" and ack num: "+str(ack_num))

			stage = "RECEIVE_ACK"

	# 2. client menerima ACK dari server
	elif (stage == "RECEIVE_ACK"):
		data, address = s.recvfrom(32777)
	
		r = receiver.Receiver()
		rec_packet = segment.Segment()

		rec_packet.build(r.receiveSegment(data))

		if (not(r.isSynSegment(rec_packet)) and r.isAckSegment(rec_packet)):
			#if server mengirim ACK untuk acknowledge client SYN,
			seq_num0 = rec_packet.getSeqNum()
			ack_num0 = rec_packet.getAckNum()

			print("\nACK received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

			if (seq_num0 == serverConnection.server_seq_num + serverConnection.n_data_received):
				print("\nConnection established, receiving data...")

				stage = "RECEIVE_DATA"

	# 3. client menerima data dari server
	elif (stage == "RECEIVE_DATA"):
		repeat = True

		while repeat:
			data, address = s.recvfrom(32777)
		
			r = receiver.Receiver()
			rec_packet = segment.Segment()
			rec_packet.build(r.receiveSegment(data))

			if (r.isDataSegment(rec_packet) and r.isNotBroken(rec_packet.checkSum)):
				seq_num0 = rec_packet.getSeqNum()
				ack_num0 = rec_packet.getSeqNum()

				print("\nData received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

				if (seq_num0 == serverConnection.server_seq_num + serverConnection.n_data_received):
					received_data = rec_packet.getPayLoad()
					print("\nReceived data from server")

					# Save received data for file construction later
					segmentPool.append(received_data)

					ack_packet = segment.Segment()
					serverConnection.n_data_received += len(received_data)
					seq_num = serverConnection.server_seq_num + serverConnection.n_data_sent
					ack_num = serverConnection.server_seq_num + serverConnection.n_data_received
					ack_packet.switchFlag("ACK")
					ack_packet.setSeqNum(seq_num)
					ack_packet.setAckNum(ack_num)

					message = hexa.byte(ack_packet.construct(),'utf-8')
					s.sendto(message, (address[0], address[1]))
					print("\nACK sent with seq_num: "+str(seq_num)+" and ack num: "+str(ack_num))

			elif (not r.isNotBroken(rec_packet.checkSum)):
				print("Segment corrupted.")

			elif (r.isFinSegment(rec_packet)):
				saveFile(segmentPool, folderpath)
				stage = "CLOSE_CONNECTION"
				repeat = False
				break

	# 4. server menutup koneksi, client mengikuti
	elif (stage == "CLOSE_CONNECTION"):
		if (r.isFinSegment(rec_packet)):
			#if server close connection
			
			seq_num0 = rec_packet.getSeqNum()
			ack_num0 = rec_packet.getAckNum()

			print("\nFIN received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

			if (seq_num0 == serverConnection.server_seq_num + serverConnection.n_data_received):
				ack_packet = segment.Segment()

				#--- Nanti set seq_num sama ack_num pake go-back-n ---#
				serverConnection.n_data_received += 1

				seq_num = serverConnection.server_seq_num + serverConnection.n_data_sent
				ack_num = serverConnection.server_seq_num + serverConnection.n_data_received
				#--- END ---#

				ack_packet.switchFlag("ACK")
				ack_packet.setSeqNum(seq_num)
				ack_packet.setAckNum(ack_num)

				message = hexa.byte(ack_packet.construct(),'utf-8')
				s.sendto(message, (address[0], address[1]))

				print("\nACK sent with seq num: "+str(seq_num)+" and ack num: "+str(ack_num))

				fin_packet = segment.Segment()

				#--- Nanti set seq_num sama ack_num pake go-back-n ---#
				seq_num = serverConnection.server_seq_num + serverConnection.n_data_sent
				ack_num = serverConnection.server_seq_num + serverConnection.n_data_received

				serverConnection.n_data_sent += 1
				#--- END ---#

				fin_packet.switchFlag("FIN")
				fin_packet.setSeqNum(seq_num)
				fin_packet.setAckNum(ack_num)

				message = hexa.byte(fin_packet.construct(),'utf-8')
				s.sendto(message, (address[0], address[1]))

				print("\nFIN sent with seq num: "+str(seq_num)+" and ack num: "+str(ack_num))

				data, address = s.recvfrom(32777)
	
				r = receiver.Receiver()
				rec_packet = segment.Segment()

				rec_packet.build(r.receiveSegment(data))
				if (r.isAckSegment(rec_packet)):
					#client receive ACK of client's FIN
					
					seq_num0 = rec_packet.getSeqNum()
					ack_num0 = rec_packet.getAckNum()

					print("\nACK received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

					fin = True #close connection

					print("\nConnection with server closed.")
