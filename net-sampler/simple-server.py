import socket
import sys

class SimpleServer:
	def __init__(self, port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', port))
		self.sock.listen(5)
		while 1:
			requestSock, peerAddress = self.sock.accept()
			print "Accepted connection from", peerAddress
			while 1:
				input = requestSock.recv(1024)
				if not input:
					print "Peer closed connection"
					break
				requestSock.send(input)	

			requestSock.close()		
		
if __name__ == "__main__":
	port = 7777
	if len(sys.argv) > 1:
		port = sys.argv[1]
	server=SimpleServer(port)

