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