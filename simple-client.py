import socket
import sys

class SimpleClient:
	def __init__(self, serverAddr, serverPort):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print "Connecting to", serverAddr, serverPort
		self.sock.connect((serverAddr, serverPort))
		print "Connected"

	def sendToServer(self, message):
		self.sock.send(message)
		return self.sock.recv(1024)

	def close(self):
		self.sock.close()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Usage: simple-client <ipaddr> <port>"
		sys.exit(1)
	else:
		client = SimpleClient(sys.argv[1], int(sys.argv[2]))

	while 1:
		string = sys.stdin.readline()
		if string == "close\n":
			print "Closing connection to server"
			client.close()
			sys.exit(0)
		else:
			print "Sending '" + string + "' to server"
			response = client.sendToServer(string)
			print "Server replied '", response,  "'"
			
		
