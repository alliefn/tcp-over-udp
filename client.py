import socket
import sys
import random
import segment
import hexa
import receiver

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

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
host = socket.gethostname()
print("Host: "+str(host))

if (len(sys.argv) > 1):
	port = sys.argv[1]
	s.bind(('127.0.0.1', int(port)))

message = "Hello server"

s.sendto(message.encode(),('127.0.0.1',1337))
print("Sent broadcast: "+message)

fin = False
server_seq_num = None
n_data_sent = 0
n_data_received = 0
stage = "RECEIVE_SYN_SEND_SYN_ACK"
received_data = None

while (not(fin)):
	if (stage == "RECEIVE_SYN_SEND_SYN_ACK"):
		data, address = s.recvfrom(32777)
	
		r = receiver.Receiver()
		rec_packet = segment.Segment()

		rec_packet.build(r.receiveSegment(data))

		if (r.isSynSegment(rec_packet) and not(r.isAckSegment(rec_packet))):
			#if server send SYN to start connection,
			seq_num0 = rec_packet.getSeqNum()
			server_seq_num = seq_num0

			print("\nSYN received with seq num: "+str(seq_num0))

			ack_packet = segment.Segment()

			#--- Nanti set seq_num sama ack_num pake go-back-n ---#
			n_data_received += 1

			seq_num = server_seq_num #paket pertama
			ack_num = seq_num0 + n_data_received #ekspektasi: seq_num berikut adalah seq_num + 1

			n_data_sent += 1
			#--- END ---#

			ack_packet.switchFlag("SYN")
			ack_packet.switchFlag("ACK")
			ack_packet.setSeqNum(seq_num)
			ack_packet.setAckNum(ack_num)

			message = hexa.byte(ack_packet.construct(),'utf-8')
			s.sendto(message, (address[0], address[1]))

			print("\nSent SYN-ACK with seq_num: "+str(seq_num)+" and ack num: "+str(ack_num))

			stage = "RECEIVE_ACK"
	elif (stage == "RECEIVE_ACK"):
		data, address = s.recvfrom(32777)
	
		r = receiver.Receiver()
		rec_packet = segment.Segment()

		rec_packet.build(r.receiveSegment(data))

		if (not(r.isSynSegment(rec_packet)) and r.isAckSegment(rec_packet)):
			#if server send ACK to acknowledge client SYN,
			seq_num0 = rec_packet.getSeqNum()
			ack_num0 = rec_packet.getAckNum()

			print("\nACK received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

			if (seq_num0 == server_seq_num + n_data_received):
				print("\nConnection established, receiving data...")

				stage = "RECEIVE_DATA"
	elif (stage == "RECEIVE_DATA"):
		'''
			Pemeriksaan apakah segmen yang diperoleh rusak atau tidak
			Jika tidak rusak
				Kirim acknowledgement kepada server
			Jika rusak
			abaikan
		'''
		req_num = 0
		while True:
			# receive data
			data, address = s.recvfrom(32777)
			r = receiver.Receiver()
			rec_packet = segment.Segment()
			rec_packet.build(r.receiveSegment(data))
			# check the received segment broken or not
			if (r.isDataSegment(rec_packet) and r.isNotBroken(rec_packet.getCheckSum())):
				seq_num0 = rec_packet.getSeqNum()
				ack_num0 = rec_packet.getSeqNum()

				print("\nData received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))
				req_num += 1

				if (seq_num0 == server_seq_num + n_data_received): #curr_ack_num masih sama karena sebelum ini, client belum menerima paket dengan payload
					received_data = rec_packet.getPayLoad()
					print("\nReceived data: "+received_data)

					ack_packet = segment.Segment()

					#--- Nanti set seq_num sama ack_num pake go-back-n ---#
					n_data_received += len(received_data) #tambah jumlah bit dalam payload

					seq_num = server_seq_num + n_data_sent
					ack_num = server_seq_num + n_data_received
					#--- END ---#

					ack_packet.switchFlag("ACK")
					ack_packet.setSeqNum(seq_num)
					ack_packet.setAckNum(ack_num)

					message = hexa.byte(ack_packet.construct(),'utf-8')
					s.sendto(message, (address[0], address[1]))

					print("\nSent ACK with seq_num: "+str(seq_num)+" and ack num: "+str(ack_num))

					stage = "CLOSE_CONNECTION"
			else:
				print("Packet corrupted. Packet refused.")



		'''
		data, address = s.recvfrom(32777)
	
		r = receiver.Receiver()
		rec_packet = segment.Segment()

		rec_packet.build(r.receiveSegment(data))

		if (r.isDataSegment(rec_packet)):
			#if server send data
			seq_num0 = rec_packet.getSeqNum()
			ack_num0 = rec_packet.getSeqNum()

			print("\nData received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

			if (seq_num0 == server_seq_num + n_data_received): #curr_ack_num masih sama karena sebelum ini, client belum menerima paket dengan payload
				received_data = rec_packet.getPayLoad()
				print("\nReceived data: "+received_data)

				ack_packet = segment.Segment()

				#--- Nanti set seq_num sama ack_num pake go-back-n ---#
				n_data_received += len(received_data) #tambah jumlah bit dalam payload

				seq_num = server_seq_num + n_data_sent
				ack_num = server_seq_num + n_data_received
				#--- END ---#

				ack_packet.switchFlag("ACK")
				ack_packet.setSeqNum(seq_num)
				ack_packet.setAckNum(ack_num)

				message = hexa.byte(ack_packet.construct(),'utf-8')
				s.sendto(message, (address[0], address[1]))

				print("\nSent ACK with seq_num: "+str(seq_num)+" and ack num: "+str(ack_num))

				stage = "CLOSE_CONNECTION"
		'''
	elif (stage == "CLOSE_CONNECTION"):
		data, address = s.recvfrom(32777)
	
		r = receiver.Receiver()
		rec_packet = segment.Segment()

		rec_packet.build(r.receiveSegment(data))
		if (r.isFinSegment(rec_packet)):
			#if server close connection
			
			seq_num0 = rec_packet.getSeqNum()
			ack_num0 = rec_packet.getAckNum()

			print("\nFIN received with seq num: "+str(seq_num0)+" and ack num: "+str(ack_num0))

			if (seq_num0 == server_seq_num + n_data_received):
				ack_packet = segment.Segment()

				#--- Nanti set seq_num sama ack_num pake go-back-n ---#
				n_data_received += 1

				seq_num = server_seq_num + n_data_sent
				ack_num = server_seq_num + n_data_received
				#--- END ---#

				ack_packet.switchFlag("ACK")
				ack_packet.setSeqNum(seq_num)
				ack_packet.setAckNum(ack_num)

				message = hexa.byte(ack_packet.construct(),'utf-8')
				s.sendto(message, (address[0], address[1]))

				print("\nACK sent with seq num: "+str(seq_num)+" and ack num: "+str(ack_num))

				fin_packet = segment.Segment()

				#--- Nanti set seq_num sama ack_num pake go-back-n ---#
				seq_num = server_seq_num + n_data_sent
				ack_num = server_seq_num + n_data_received

				n_data_sent += 1
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
