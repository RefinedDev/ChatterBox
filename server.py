from random import randint

import socket
import threading
import pickle
import time 

class Server:
    def __init__(self,IP):
        self.BUFFER = 1000000

        self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        try:
            self.serverSocket.bind((IP,80))
        except:
            return

        self.clientConnections = []
        self.clientUsernames = []
        self.channels = ['logs','general']
        self.channelsData = {
            'logs': [],
            'general': [],
        }

        self.serverOwner = None

        joinThread = threading.Thread(target=self.clientJoinEvent)
        joinThread.start()

        print(f"SERVER with IP [{IP}] has been established.")
        
    def fireToAllClients(self,data):
        for i in self.clientConnections:
            try:
                i.send(pickle.dumps(data))
            except Exception as e:
                print(f"FIRE ALL CLIENTS ERROR: {e}")

    def handleClientCommunication(self,clientConnection):
        userName = False
        while True:
            try:
                message = pickle.loads(clientConnection.recv(self.BUFFER))
                if message:
                    if not userName:
                        userName = message[0]

                        if userName in self.clientUsernames:
                            userName = userName + str(randint(1,10000))

                        self.clientUsernames.append(userName)
                        
                        if self.serverOwner == clientConnection:
                            self.channels.append('yesOWNER')

                        clientConnection.send(pickle.dumps(["updateUSERNAMEe",userName]))
                        self.fireToAllClients((self.clientUsernames,self.channels,self.channelsData))
                        time.sleep(0.1)
                        self.fireToAllClients([f"[SERVER] {userName} has joined the Chat!\n",'logs'])
                       
                        if 'yesOWNER' in self.channels:
                            self.channels.remove('yesOWNER')

                    elif 'nEWANNCHANNELDATIAJIJDAJIFAIJF' in message:
                        if not(message[1] in self.channels):
                            self.channels.append(message[1])
                            self.channelsData[message[1]] = []
                        else:
                            self.channels.remove(message[1])
                            self.channelsData.pop(message[1])
                
                        self.fireToAllClients((self.clientUsernames,self.channels,self.channelsData))
                    elif 'KCIKAUSAEJAHRFAJfhASJGH' in message:
                        self.fireToAllClients(["PEALSLASLAEAFJAILEAVEA",message[1]])
                    else:
                        msg = f'\n{userName} \n{message[0]}\n'
                        self.fireToAllClients([msg,message[1]])
                        self.channelsData[message[1]].append(msg)

                        if len(self.channelsData[message[1]]) > 50:
                            self.channelsData[message[1]] = self.channelsData[message[1]][-50:]
            except:
                self.clientConnections.remove(clientConnection)
                self.clientUsernames.remove(userName)

                if len(self.clientConnections) == 0:
                    self.channels = []

                self.fireToAllClients([f"[SERVER] {userName} has left the Chat!\n",'logs'])
                self.fireToAllClients((self.clientUsernames,self.channels,self.channelsData))

                clientConnection.close()
                break

    def clientJoinEvent(self):
        self.serverSocket.listen()

        while True:
            cc,_ = self.serverSocket.accept()
            
            if len(self.clientConnections) == 0:
                self.serverOwner = cc
                
            self.clientConnections.append(cc)

            commsThread = threading.Thread(target=self.handleClientCommunication, args=(cc,))
            commsThread.start()