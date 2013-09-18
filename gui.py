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
import javax.swing as swing
import sys

class login:
    def setText(self, event):
        self.label.text = "Button clicked"

    def change_username(self, event):
        print "serverside magic!"
        #TODO: check server if username taken
        self.message.text = "Logging in..."
        #TODO: log in here
        username = self.usernameField.text
        self.window.windowClosing = self.goodbye
        try:
            self.window.visible = False
            self.friendsList(username)
            self.message.text = "Logged in"
        except:
            self.message.text = "How did you fail to login?"
            raise

    def __init__(self):
        # Launches the login screen, initializes self.window, the primary frame
        
        self.window = swing.JFrame("Catchy Messenger Name")
        self.chatWindow = swing.JFrame()
        self.window.windowClosing = self.goodbye

        self.loginPage = JPanel(GridLayout(0,2))
        self.window.add(self.loginPage)
        
        self.usernameField = JTextField('',20)
        self.loginPage.add(JLabel("Enter today's username", SwingConstants.RIGHT))
        self.loginPage.add(self.usernameField)
        
        self.loginButton = JButton('Log in', actionPerformed=self.change_username)
        self.loginPage.add(self.loginButton)
        self.message = JLabel("Please log in")
        self.loginPage.add(self.message)
        
        self.window.pack()
        self.window.visible = True
        return

    
        
    # This is the callback for all the radio buttons.
    #TODO: ping server with new status
    def radioCallback(self, event):
        print event
        return
                
    def launchChat(self, event):
        #Launches one chat window per conversation. TODO: less wizard of oz
        chatWindow = swing.JFrame("The Boss")
        chatWindow.contentPane.layout = awt.BorderLayout()
        chatHistory = swing.JTextArea(text = "new chat instance!", editable = False, lineWrap = True, size = (300,1))
        chatHistoryPanel = swing.JPanel()
        chatHistoryPanel.add(chatHistory)
        chatWindow.contentPane.add("North", chatHistoryPanel)
        
        #TODO: key listener so [return] enters text
        #TODO: more complicated than boss parroting action
        entryPanel = swing.JPanel()
        chatWindow.contentPane.add("South", entryPanel)
        entryPanel.layout = awt.BorderLayout()
        #Must change data structure of chatHistory to hold multiple chats
        self.field = swing.JTextArea()
        entryPanel.add(self.field)
        entryPanel.add("East", swing.JButton("Enter Text", actionPerformed=self.enterText))
        chatWindow.pack()
        chatWindow.show()
        self.chatWindow.visible = False
        
        
        return
    
    def enterText(self, event):
        #TODO: fancy server things.
        #self.chatHistory.setText(self.chatHistory.setText(self.field))
        print self.field
        #self.chatHistory.setText(self.chatHistory.setText("Get to work!"))
        self.chatHistory.append(self.field.text())        
        
    def hide(self, event):
            self.chatWindow.visible = False
                
    def callBoss(self, event):
        self.chatWindow = swing.JFrame("Incoming message!")
        newPanel = JPanel(GridLayout())
        self.chatWindow.add(newPanel)
        newPanel.add(swing.JLabel("New message from The Boss. Accept?"))
        newPanel.add(JButton("Yes", actionPerformed=self.launchChat))
        newPanel.add(JButton("No", actionPerformed=self.hide))
        
        self.chatWindow.pack()
        self.chatWindow.show()
    
    def offline(self, event):
        #TODO: build real chat client functionality
        dialog = swing.JFrame("Server error")
        dialog.contentPane.layout = awt.BorderLayout()
        dialog.contentPane.add(swing.JLabel("Internal error. User not online."))
        dialog.size=(400,200)
        dialog.show()
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
        
        #Buddy list
        panel = swing.JPanel()
        panel.layout = awt.BorderLayout()
        panel.border = swing.BorderFactory.createTitledBorder("Friends Online")
        friendsData = ["April", "Jun", "The Parrot", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo", "foo"]
        self.list = swing.JList(friendsData)
        panel.add("Center", swing.JScrollPane(self.list))
        launchChatButton = swing.JButton("Launch chat?", actionPerformed=self.offline)
        panel.add("South", launchChatButton)
        self.window.windowClosing = self.goodbye
        pane = JScrollPane()
        pane.getViewport().add(self.list)
        panel.add(pane)
        self.window.add("North", statusPanel)
        self.window.add("South", panel)
        self.window.pack()
        self.window.visible = True
        
        return
        
        

    
    def goodbye(self, event):
        print "Goodbye!"
        sys.exit()
        return
                         
                         
                         
if __name__ == '__main__':
    login = login()