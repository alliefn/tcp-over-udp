import socket
import sys

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

