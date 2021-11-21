import socket
import time
import sys

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
	print("Server started at port"+str(port)+"...")

else:
	print("Port number not specified. Run: 'python server.py <port-number>'")
	exit()
s.bind(('',port))

def listen_broadcast():
	print("Listening to broadcast address for clients.")
	
	clients = []

	while True:
		data, address = s.recvfrom(1024)
		client = str(address[0])+":"+str(address[1])
		clients.append(client)
		print("[!] Client ("+client+") found")
		cont = input("[?] Listen more? (y/n) ").lower()
		if (cont == "n" or cont != "y"):
			break
	
	print()
	
	list_clients(clients)

def list_clients(clients):
	print(NUMBERS[len(clients)].title()+" clients found:")
	for i in range(len(clients)):
		print(str(i+1)+". "+clients[i])

listen_broadcast()
