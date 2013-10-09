import socket
import sys
import threading

class MTServer:
	def __init__(self, port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', port))
		self.sock.listen(1)
		while 1:
			requestSock, peerAddress = self.sock.accept()
			print "Accepted connection from", peerAddress
			handler = Handler(requestSock)

class Handler:
	def __init__(self, requestSock):
		self.requestSock = requestSock
		self.thread = threading.Thread(target=self.handle)
		self.thread.start()

	def handle(self):
		while 1:
			input = self.requestSock.recv(1024)
			if not input:
				print "Peer closed connection"
				break
			self.requestSock.send(input)
		self.requestSock.close()

if __name__ == "__main__":
	port = 7777
	if len(sys.argv) > 1:
		port = sys.argv[1]
	server=MTServer(port)

