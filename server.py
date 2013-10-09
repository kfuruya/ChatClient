# server.py

import time
import sys
import thread
import threading
import socket
import pickle
import java.lang as lang

DEFAULT_PORT = 6666

class Server:
	def __init__(self, port):
		self.connectedClients = { }
		self.chats = { }  # fix me: obsolete chats never get pruned. Maybe problematic if a user reconnects to running server, since LEAVE notifications will be sent to old chats
		self.lastChatID = 15
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', port))
		self.sock.listen(5)
		print "Server running on port", port
		self.updateTimer = Timer(5, self.sendUpdates)
		self.updateTimer.start()
		self.handleNewClients()
			
	def handleNewClients(self):
		print "Ready to handle new clients"
		while 1:
			try:
				requestSock, peerAddress = self.sock.accept()
				print "Accepted connection from address", peerAddress
			except socket.error:
				print "Error getting new connection from client"
				return
			
			try:
				handler = Handler(requestSock, peerAddress, self)
				print "Created handler"
			except Exception, inst:
				print "Error starting handler:", str(inst)

				requestSock.close()

		
	# called by the timer to push out the updated user list to all clients	
	def sendUpdates(self, timer):
		users = self.connectedClients.keys()
		# build dictionary that represents online users
		onlineUserInfo = { }
		for user in users:
			handler = self.connectedClients[user]
			onlineUserInfo[user] = handler.status
			print "Timer sending user info update to connected clients:", onlineUserInfo
		# delegate to all handlers to send to their respective clients
		for user in users:
			handler = self.connectedClients[user]
			handler.sendOnlineUsers(onlineUserInfo)
			
	# called by a handler whose client has issued an invite; finds handlers for invitees
	# and gets them to send an invitation to their clients.
	def sendInvitations(self, invitor, invitees, chatID):
		print "User", invitor, "is inviting the following users:", invitees
		for i in invitees:
			if not self.connectedClients.has_key(i):
				print "User", i, "does not exist or has already logged off"
			handler = self.connectedClients[i]
			handler.sendInvitation(invitor, invitees, chatID)
			
	# called by a handler when its client accepts an invitation; finds handlers for
	# everyone else in the chat and notifies them via a JOINED message
	def sendJoinedOrDeclined(self, state, chatID, userName):
		print "User", userName, "has", state, "the chat", chatID, "... notifying members of that chat."
		if not self.chats.has_key(chatID):
			print "No such chat", chatID, "or it has already ended."
			return
		chat = self.chats[chatID]	# returns a tuple (invitor, invitees)... need to message all of them
		membersSansSender = [chat[0]] + chat[1]
		membersSansSender.remove(userName)
		for m in membersSansSender:
			if not self.connectedClients.has_key(m):
				print "Participant", m, "appears to have already left?"
			else:
				handler = self.connectedClients[m]
				handler.sendJoinedOrDeclined(state, chatID, userName)
				
	def sendMessage(self, userName, chatID, message):
		print "User", userName, "has sent message to chat", chatID, ":", message
		if not self.chats.has_key(chatID):
			print "No such chat", chatID, "or it has already ended."
			return
		chat = self.chats[chatID] #returns a tuple (invitor, invitees)
		membersSansSender = [chat[0]] + chat[1]
		membersSansSender.remove(userName)
		for m in membersSansSender:
			if not self.connectedClients.has_key(m):
				print "Participant", m, "appears to have already left?"
			else:
				handler = self.connectedClients[m]
				handler.sendMessage(chatID, userName, message)		
		
	def sendLeave(self, userName, chatID):
		print "User", userName, "has left chat", chatID
		if not self.chats.has_key(chatID):
			print "No such chat", chatID, "or it has already ended."
			return
		chat = self.chats[chatID] #returns a tuple (invitor, invitees)
		membersSansSender = [chat[0]] + chat[1]
		membersSansSender.remove(userName)
		for m in membersSansSender:
			if not self.connectedClients.has_key(m):
				print "Participant", m, "appears to have already left?"
			else:
				handler = self.connectedClients[m]
				handler.sendLeft(chatID, userName)
							
	# called by a handler when its client issues an invite, to establish a new chatID->chatters mapping
	# and increment the chatID
	def updateChats(self, invitor, invitees):
		self.lastChatID = self.lastChatID + 1
		chatID = self.lastChatID
		self.chats[chatID] = (invitor, invitees)
		return chatID
		
	# this is called by a handler when its user completely disconnects.  We find all of the chats the
	# guy was involved in and send LEFT messages to each.  We also remove the client from the list of
	# chats	
	def processDisconnectedClient(self, userName):
		print "Notifying clients involved in chat with", userName, "that he/she has left"
		for chatID in self.chats.keys():
			chat = self.chats[chatID]  # returns a tuple (invitor, [invitees])
			if userName == chat[0] or userName in chat[1]:
				# He's in this chat.  Make a list of everybody else, find their handlers, and message them
				userList = [chat[0]] + chat[1]
				userList.remove(userName)
				for u in userList:
					if not self.connectedClients.has_key(u):
						print "Participant", u, "appears to have already left?"
					else:
						handler = self.connectedClients[u]
						handler.sendLeft(chatID, userName)			
			
class Handler:
	def __init__(self, requestSock, peerAddress, server):
		self.stopped = None
		self.userName = None
		self.status = None
		self.sock = requestSock
		self.peerAddress = peerAddress
		self.server = server
		self.thread = threading.Thread(target=self.runHandler)
		self.thread.start()
			
	def runHandler(self):
		while not self.stopped:
			print "In run handler"
			input = self.readData()
			if not input:
				print "Connection to client closed, shutting down handler"
				self.shutdownHandler()
				break
							
			commandList = pickle.loads(input)
			if commandList[0] == "HELLO":
				print "Server received HELLO"
				self.handleHello(commandList)
			elif commandList[0] == "GOODBYE":
				print "Server received GOODBYE"
				self.handleGoodbye(commandList)
			elif commandList[0] == "CHANGE_STATUS":
				print "Server received CHANGE_STATUS"
				self.handleChangeStatus(commandList)
			elif commandList[0] == "INVITE":
				print "Server received INVITE"
				self.handleInvite(commandList)
			elif commandList[0] == "ACCEPT":
				print "Server received ACCEPT"
				self.handleAccept(commandList)
			elif commandList[0] == "REJECT":
				print "Server received REJECT"
				self.handleReject(commandList)
			elif commandList[0] == "SEND_MESSAGE":
				print "Server received SEND_MESSAGE"
				self.handleSendMessage(commandList)
			elif commandList[0] == "LEAVE":
				print "Server received LEAVE"
				self.handleLeave(commandList)
			else:
				print "Unknown command:", commandList
				
	def readData(self):
		reply = ""
		while 1:
			data = self.sock.recv(1024)
			if not data:				# got no data, connection closed?
				break
			elif len(data) == 1024:		# read a full buffer; keep trying to read more
				reply = reply + data
			else:						# read a partial buffer, end of this message
				reply = reply + data
				break
		return reply
			
				
	def shutdownHandler(self):
		print "Shutting down handler for", self.userName
		self.stopped = 1
		del self.server.connectedClients[self.userName]
		try:
			self.sock.close()
		except:
			print "Error closing socket"

		# Tell the server to send LEFT messages to anyone this dude was in a chat with, and to clean up the chats list.
		self.server.processDisconnectedClient(self.userName)
						
	def handleHello(self, commandList):
		# format: ["HELLO", username, status]
		if len(commandList) != 3:
			print "Expected HELLO to have two arguments (username, status):", commandList
			return
		if type(commandList[1]) != str:
			print "Expected username to be a string:", commandList[1], "(not a " + str(type(commandList[1])) + ")"
			return
		if type(commandList[2]) != str:
			print "Expected status to be a string:", commandList[2], "(not a " + str(type(commandList[2])) + ")"
			return
		
		self.userName = commandList[1]
		self.status = commandList[2]
		self.server.connectedClients[self.userName] = self

		print "Successfully handled HELLO from", self.userName, " (" + self.status + ")"
			
	def handleGoodbye(self, commandList):
		# format ["GOODBYE"]
		if len(commandList) != 1:
			print "Expected GOODBYE to have no arguments:", commandList
			
		self.shutdownHandler()
		print "Successfully handled GOODBYE from", self.userName
		
	def handleChangeStatus(self, commandList):
		# format: ["CHANGE_STATUS", newStatus]
		if len(commandList) != 2:
			print "Expected CHANGE_STATUS to have one argument (newStatus):", commandList
			return
		if type(commandList[1]) != str:
			print "Expected newStatus to be a string:", commandList[1], "not a ", str(type(commandList[1]))
			
		self.status = commandList[1]

		print "Successfully handled CHANGE_STATUS for", self.userName, "(" + self.status + ")"
		
	def handleInvite(self, commandList):
		# format: ["INVITE", [user1, user2, ...]]
		if len(commandList) != 2:
			print "Expected INVITE to include a list of users:", commandList
			return
		if type(commandList[1]) != list:
			print "Expected argument to INVITE to be a list of users:", commandList[1], "not a ", str(type(commandList[1]))
			return
		userList = commandList[1]
		if len(userList) == 0:
			print "No users in invitation list:", userList
			return
		for i in userList:
			if type(i) != str:
				print "Expected string username in invitation list:", i, "not a", str(type(i))
				return
		
		# Have the server update its list of chats and assign a new chatID
		chatID = self.server.updateChats(self.userName, userList)
		print "INVITE resulted in new chatID", chatID, "returning to client..."
		self.sendChatID(chatID, userList)
		
		# Now, have the server track down the handlers for each user and ask them to notify their clients
		self.server.sendInvitations(self.userName, userList, chatID)	
	
		print "Successfully handled INVITE for", userList
		
	def handleAccept(self, commandList):
		# format ["ACCEPT", chatID]
		if len(commandList) != 2:
			print "Expected ACCEPT to have a chatID as its argument:", commandList
			return
		if type(commandList[1]) != int:
			print "Expected chatID to be a number:", commandList[1], "not a ", str(type(commandList[1]))
			return
			
		# Have the server ask the handlers for all implicated clients to notify them via a JOINED message
		self.server.sendJoinedOrDeclined("JOINED", commandList[1], self.userName)
		print "Successfully handled ACCEPT for chatID", commandList[1]
		
	def handleReject(self, commandList):
		# format ["REJECT", chatID]
		if len(commandList) != 2:
			print "Expected REJECT to have a chatID as its argument:", commandList
			return
		if type(commandList[1]) != int:
			print "Expected chatID to be a number:", commandList[1], "not a ", str(type(commandList[1]))
			return
			
		# Have the server ask the handlers for all implicated clients to notify them via a DECLINED message
		self.server.sendJoinedOrDeclined("DECLINED", commandList[1], self.userName)
		print "Successfully handled REJECT for chatID", commandList[1]		
			
	def handleSendMessage(self, commandList):
		# format ["SEND_MESSAGE", chatID, message]
		if len(commandList) != 3:
			print "Expected SEND_MESSAGE to include a chatID and a message:", commandList
			return
		if type(commandList[1]) != int:
			print "Expected chatID to be a number:", commandList[1], "not a ", str(type(commandList[1]))
			return
		if type(commandList[2]) != str:
			print "Expected message to be a string:", commandList[2], "not a ", str(type(commandList[2]))
			return
		
		# Have the server ask the handlers for all clients in this chat to send the message
		self.server.sendMessage(self.userName, commandList[1], commandList[2])
		print "Successfully handled SEND_MESSAGE for chatID", commandList[1], "(" + commandList[2] + ")"
		
	def handleLeave(self, commandList):
		# format ["LEAVE", chatID]
		if len(commandList) != 2:
			print "Expected LEAVE to include a chatID and a message:", commandList
			return
		if type(commandList[1]) != int:
			print "Expected chatID to be a number:", commandList[1], "not a", str(type(commandList[1]))
			return
			
		# Have the server send a LEFT message to all of the clients in this chat
		self.server.sendLeave(self.userName, commandList[1])
		print "Successfulliy handled LEAVE for", self.userName, "chatID", commandList[1]
		
	def sendOnlineUsers(self, onlineUserInfo):
		# format: ["ONLINE_USERS", {user1 -> status1, user2 -> status2, ...}]
		msg = ["ONLINE_USERS", onlineUserInfo]
		msgData = pickle.dumps(msg)
		try:
			self.sock.send(msgData)
			print "Handler sent ONLINE_USERS to client"
		except socket.error:
			print "Error sending ONLINE_USERS message to", self.userName
			self.shutdownHandler()
			
	def sendChatID(self, chatID, invitees):
		msg = ["CHAT_ID", chatID, invitees]
		msgData = pickle.dumps(msg)
		try:
			self.sock.send(msgData)
			print "Handler sent CHAT_ID", chatID, "to client"
		except socket.errr:
			print "Error sending CHAT_ID to", self.userName
			self.shutdownHandler()
			
	def sendInvitation(self, invitor, invitees, chatID):
		msg = ["INVITATION", invitor, invitees, chatID]
		msgData = pickle.dumps(msg)
		try :
			self.sock.send(msgData)
			print "Handler sent INVITIATION(" + invitor + ", " + str(invitees) + ", " + str(chatID) + ") to", self.userName
		except socket.error:
			print "Error sending INVITATION to", self.userName
			self.shutdownHandler()			
			
	def sendJoinedOrDeclined(self, state, chatID, userName):
		if state == "JOINED":
			msg = ["JOINED", chatID, userName]
		elif state == "DECLINED":
			msg = ["DECLINED", chatID, userName]
		else:
			print "Unknown join or decline state, urrrrk"
			return
		
		msgData = pickle.dumps(msg)
		try:
			self.sock.send(msgData)
			print"Handler sent", msg
		except socket.error:
			print"Error sending", state, "to", self.userName
			self.shutdownHandler()			
	
	def sendMessage(self, chatID, userName, message):
		msg = ["MESSAGE", chatID, userName, message]
		msgData = pickle.dumps(msg)
		try:
			self.sock.send(msgData)
			print "Handler sent", msg
		except socket.error:
			print "Error sending Invitation to", self.userName
			self.shutdownHandler()			

	def sendLeft(self, chatID, userName):
		msg = ["LEFT", chatID, userName]
		msgData = pickle.dumps(msg)
		try:
			self.sock.send(msgData)
			print "Handler sent", msg
		except socket.error:
			print "Error sending Invitation to", self.userName	
			self.shutdownHandler()				
			
			
class Timer:
	def __init__(self, interval, callback):
		self.interval = interval
		self.callback = callback
		self.running = 0

	def start(self):
		if self.running:
			pass
		self.running = 1
		self.thread = threading.Thread(target=self.runloop)
		self.thread.start()

	def runloop(self):
		while self.running:
			time.sleep(self.interval)
			self.invokeCallback()
		self.running = 0
		self.thread = None

	def stop(self):
		if not self.running:
			pass
		self.running = 0

	def invokeCallback(self):
		self.callback(self)
			
	
if __name__ == "__main__":
	port = DEFAULT_PORT
	if len(sys.argv) > 1:
		port = int(sys.argv[1])
	server = Server(port)
