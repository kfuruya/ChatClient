#herpderp how do you comment
# ############################### #
# Kimberly Furuya                 #
# CS 6452 Fall 2013               #
# Prototyping Interactive Systems #
# adapted from http://www.jython.org/jythonbook/en/1.0/GUIApplications.html
# ############################### #

# java swing!

from javax.swing import (BoxLayout, ImageIcon, JButton, JFrame, JPanel, JPasswordField, JLabel, JTextArea, JTextField, JScrollPane, SwingConstants, WindowConstants, GroupLayout, BorderFactory)
import java.awt as awt
from java.awt import Component, GridLayout, BorderLayout
import java.net as net
import java.lang as lang
import javax.swing as swing
import pickle
import socket
import sys
import thread
import threading
import time







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










class chatInstance:
    def __init__(self):
        self.messageText = swing.JTextArea(text = "new chat instance!", editable = False, lineWrap = True, size = (300,1))
        self.state = "Not in chatroom"
        self.CHATID = 0
        self.status = swing.JLabel("")
        return
    








class login:
    
    

    def __init__(self):
        # Launches the login screen, initializes self.window, the primary frame
        self.done = False
        self.friendsData = ['']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chatHistory = {}
        self.usernameField = JTextField('guest',20)
        self.status = JTextField(text='setStatus', editable=True)
        self.portNumber = "6666"
        self.IP = "127.0.0.1"
        self.window = swing.JFrame("Catchy Messenger Name")
        self.chatWindow = swing.JFrame()
        self.window.windowClosing = self.goodbye
        tempPanel = swing.JPanel()
        tempPanel = awt.BorderLayout()
        loginPage = JPanel(GridLayout(0,2))
        self.window.add(loginPage)
        loginPage.add(JLabel("Enter today's username", SwingConstants.RIGHT))
        loginPage.add(self.usernameField)
        textIP = swing.JTextField(text = self.IP, editable = True)
        #chatHistory = swing.JTextArea(text = "new chat instance!", editable = False, lineWrap = True, size = (300,1))
        loginButton = JButton('Log in', actionPerformed=self.login)
        loginPage.add(JLabel(""))
        loginPage.add(loginButton)
        loginPage.add(textIP)
        loginPage.add(JLabel("Change IP from default?", SwingConstants.LEFT))
        loginPage.add(swing.JTextField(text=self.portNumber, editable=True))
        loginPage.add(JLabel("Change Port from default?"))
        self.window.pack()
        self.window.visible = True
        return

    def sendToServer(self, message):
        self.sock.send(message)
        return self.sock.recv(1024)

    def login(self, event):
        #TODO: check server if username taken
        #TODO: log in here
        username = self.usernameField.text
        try:
            self.window.visible = False
            self.window = self.friendsList(username)
            print "Connecting To", self.portNumber, self.IP
        
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ((self.IP, self.portNumber))
            self.sock.connect((self.IP, int(self.portNumber)))
            print "Connected"
            self.sock.send(pickle.dumps(("HELLO", str(self.usernameField.text), str(self.status.text))))
            self.done = True
            
            return
        #self.friendsData = self.friendsData[1]
        #self.friendsData = list(self.friendsData.keys())
        except:
            print "Clientside magic smoke left the box"
            raise

    # This is the callback for all the radio buttons.
    #TODO: ping server with new status
    def radioCallback(self, event):
        print event
        return
                
    def launchChatIn(self, event):
        #Launches one chat window per conversation. TODO: less wizard of oz
        chatWindow = swing.JFrame("The Boss")
        self.chatHistory['The Boss'] = chatInstance()
        chatWindow.contentPane.layout = awt.BorderLayout()
        #self.chatHistory = swing.JTextArea(text = "new chat instance!", editable = False, lineWrap = True, size = (300,1))
        chatHistoryPanel = swing.JPanel()
        chatHistoryPanel.add(swing.JScrollPane(self.chatHistory['The Boss'].messageText))
        chatWindow.contentPane.add(chatHistoryPanel)
        #TODO: key listener so [return] enters text
        #TODO: more complicated than boss parroting action
        entryPanel = swing.JPanel()
        chatWindow.contentPane.add("South", entryPanel)
        entryPanel.layout = awt.BorderLayout()
        #TODO change data structure of chatHistory to hold multiple chats
        self.field = swing.JTextField()
        entryPanel.add(self.field)
        entryPanel.add("East", swing.JButton("Enter Text", actionPerformed=self.enterText))
        chatWindow.pack()
        chatWindow.show()
        self.chatWindow.visible = False
    
    def enterText(self, event):
        #TODO: fancy server things.
        #self.chatHistory.setText(self.chatHistory.setText(self.field))
        print self.field.text
        user = 'The Boss'
        #self.chatHistory.setText(self.chatHistory.setText("Get to work!"))
        chatLog = self.chatHistory[user].messageText.text
        chatLog = chatLog + "\n" + self.field.text
        self.chatHistory[user].messageText.setText(chatLog)
        
    def hide(self, event):
        self.chatWindow.visible = False
                
    def callBoss(self, event):
        self.chatWindow = swing.JFrame("Incoming message!")
        newPanel = JPanel(GridLayout())
        self.chatWindow.add(newPanel)
        newPanel.add(swing.JLabel("New message from The Boss. Accept?"))
        newPanel.add(JButton("Yes", actionPerformed=self.launchChatIn))
        newPanel.add(JButton("No", actionPerformed=self.hide))
        self.chatWindow.pack()
        self.chatWindow.show()
    
    def launchChatOut(self, event):
        
		# format: ["INVITE", [user1, user2, ...]]
        print self.list.selectedValue
        self.sock.send(pickle.dumps(["INVITE", [str(self.list.selectedValue)]]))
        #TODO: build real chat client functionality
        dialog = swing.JFrame("Server error")
        dialog.contentPane.layout = awt.BorderLayout()
        dialog.contentPane.add(swing.JLabel("Internal error. " + self.list.selectedValue + " is not online."))
        dialog.size=(400,200)
        dialog.show()
        return
    
    def updateSatus(self, event):
        print self.status.text
        return
    

    def friendsList(self, username):
        
        self.window = swing.JFrame(username)
        self.window.layout = awt.BorderLayout()
        statusPanel = swing.JPanel()
        statusPanel.layout = awt.GridLayout(4,1)

        # Set status placeholder UI
        statusPanel.border = swing.BorderFactory.createTitledBorder("Status")
        buttonGroup = swing.ButtonGroup()
        radioButton = swing.JRadioButton("Away", actionPerformed=self.radioCallback)
        buttonGroup.add(radioButton)
        statusPanel.add(radioButton)
        radioButton = swing.JRadioButton("Here", actionPerformed=self.radioCallback)
        buttonGroup.add(radioButton)
        statusPanel.add(radioButton)
        #Wizard of Oz incoming chat request
        radioButton = swing.JButton("Page Boss", actionPerformed=self.callBoss)
        buttonGroup.add(radioButton)
        statusPanel.add(radioButton)
        statusPanel.add(self.status)
        #statusPanel.add(swing.JButton("Update Status", actionPerformed=self.updateStatus))
        #Buddy list
        panel = swing.JPanel()
        panel.layout = awt.BorderLayout()
        panel.border = swing.BorderFactory.createTitledBorder("Friends Online")
        
        
        
        ##TODO: fix threading so that friends load before the window
        print self.friendsData
        self.friendsData.append('guest')
        print '2'
        
        
        
        self.list = swing.JList(self.friendsData)
        panel.add("Center", swing.JScrollPane(self.list))
        launchChatButton = swing.JButton("Launch chat?", actionPerformed=self.launchChatOut)
        panel.add("South", launchChatButton)
        self.window.windowClosing = self.goodbye
        pane = JScrollPane()
        pane.getViewport().add(self.list)
        panel.add(pane)
        self.window.add("North", statusPanel)
        self.window.add("South", panel)
        self.window.pack()
        self.window.visible = True
        return self.window
    
    def goodbye(self, event):
        print "Goodbye!"
        self.sock.send(pickle.dumps(["GOODBYE"]))
        print self.sock.recv(1024)
        sys.exit()
        return

    def readin(self):
        ##handles input from server
        hold = ''
        while not(hold):
            hold = self.sock.recv(1024)
        hold = pickle.loads(hold)
        type = hold[0]
        if type == "ONLINE_USERS":
            self.friendsData = hold[1]
            del self.friendsData[str(self.usernameField.text)]
            self.friendsData = list(self.friendsData.keys())
            self.window.visible = False
            self.friendsList(str(self.usernameField.text))



if __name__ == '__main__':
    login = login()
    while 1:
        if login.done:
            login.readin()

