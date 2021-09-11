import socket
import threading

import tkinter.scrolledtext
from tkinter import *
from tkinter.font import BOLD

import pickle
import re

class Client:
    def __init__(self,IP,userName,UIObject):
        self.BUFFER = 1000000

        self.IP = IP
        self.userName = userName
        self.isOwner = False

        self.clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        try:
            self.clientSocket.connect((self.IP,80))
        except:
            return

        self.UIObj = UIObject
        self.UI = UIObject.UI
        
        self.connected = True
        self.ready = False

        self.currentChannels = []

        Uiloop = threading.Thread(target=self.create_Ui)
        Uiloop.start()
        
        recThread = threading.Thread(target=self.recData)
        recThread.start()

    def create_Ui(self):
        for i in self.UI.winfo_children():
            i.destroy()

        self.UI.state('zoomed')  

        self.channel_Top = Label(text='# - general',bg='#23272A',font=('@Yu Gothic UI Semibold',17,BOLD),fg='white')
        self.channel_Top.pack(fill='x')

        self.membersFrame = Frame(self.UI,bg='#23272A',width=250)
        self.membersFrame.pack(side='right',fill='y')

        self.channelsFrame = Frame(self.UI,bg='#23272A',width=250)
        self.channelsFrame.pack(side='left',fill='y')

        self.general = tkinter.scrolledtext.ScrolledText(self.UI,bg='#23272A',fg='white',font=('@Yu Gothic UI Semibold',12,BOLD),width=120,height=30,state='disabled')
        self.general.pack(pady=20,padx=20,anchor=NW)
        
        self.inputBox = Entry(self.UI,bg='#23272A',fg='white',font=('@Yu Gothic UI Semibold',20,BOLD),borderwidth=2,width=70)
        self.inputBox.insert('end','Enter a message.')
        self.inputBox.pack(pady=20,padx=20,anchor=NW)
        
        self.currentChannel = 'general'
        self.ready = True

        self.UI.bind('<Return>',self.send_Message)
        self.UI.protocol("WM_DELETE_WINDOW",self.close)
        self.clientSocket.send(pickle.dumps([self.userName]))
        
    def send_Message(self,event):
        sussyMessage = self.inputBox.get()
    
        if len(sussyMessage) > 0:
            msg = f"{sussyMessage}"
            if len(msg) > 800:
                msg = msg[0:800]
                        
            self.clientSocket.send(pickle.dumps([msg,self.currentChannel]))
            self.inputBox.delete(0,'end')

    def recData(self):
        while self.connected:
            try:
                data = self.clientSocket.recv(self.BUFFER)
                pickled = pickle.loads(data) 
                
                if self.ready:
                    if 'yesOWNER' in pickled[1]:
                        pickled[1].remove('yesOWNER')
                        self.isOwner = True

                   
                    if isinstance(pickled,tuple):
                        """
                        LOAD THE USER's LIST
                        """

                        for i in self.membersFrame.winfo_children():
                            i.destroy()

                        for x in range(0,len(pickled[0]) + 1):
                            Grid.rowconfigure(self.membersFrame, x, weight=0)
                       
                        Grid.columnconfigure(self.membersFrame, 0, weight=0)
                        Label(self.membersFrame,bg='#5865F2',text='Members',font=('@Yu Gothic UI Semibold',25,BOLD),fg='white',width=13).grid(column=0,row=0)

                        font = '@Yu Gothic UI Semibold'
                        for i,v in enumerate(pickled[0]): 
                            if v == self.userName:
                                font = 'Arial'
                            else:
                                font = '@Yu Gothic UI Semibold'

                            if i == 0:
                                Label(self.membersFrame,bg='#23272A',text=f'👑 ({v})',font=(font,15,BOLD),fg='white').grid(column=0,row=i+1,pady=10)
                            else:
                                if self.isOwner:
                                    butt = Button(self.membersFrame,bg='#23272A',text=f'{i+1}. ({v})',font=(font,15,BOLD),fg='white',borderwidth=0)
                                    butt.grid(column=0,row=i+1,pady=10)
                                    self.set_MemberButton(butt=butt)
                                else:
                                    Label(self.membersFrame,bg='#23272A',text=f'{i+1}. ({v})',font=(font,15,BOLD),fg='white').grid(column=0,row=i+1,pady=10)

                        if len(self.membersFrame.winfo_children()) >= 15:
                            Grid.columnconfigure(self.membersFrame, 0, weight=1)
                            for x in range(0,i+1):
                                Grid.rowconfigure(self.membersFrame, x, weight=1)
                            

                        """
                        LOAD CHANNELS / CHANNEL BUTTONS
                        """

                        if self.currentChannels != pickled[1]:
                            if hasattr(self,'stop'):
                                self.stop.destroy()
                                delattr(self,'stop')

                            for i in self.channelsFrame.winfo_children():
                                i.destroy()

                            currentRow = 1

                            for v in pickled[1]: 
                                if not(hasattr(self,v)):
                                    setattr(self,v,tkinter.scrolledtext.ScrolledText(self.UI,bg='#23272A',fg='white',font=('@Yu Gothic UI Semibold',12,BOLD),width=120,height=30,state='disabled'))
                                
                                self.make_Channel_Button(v,currentRow)
                                currentRow += 1

                            if self.isOwner == True:
                                self.killMe = Frame(self.channelsFrame,bg='#23272A',width=100)
                                self.killMe.grid(column=0,row=currentRow+1,pady=10)

                                self.addChannel = Button(self.killMe,bg='#23272A',text=f'+',font=('@Yu Gothic UI Semibold',15,BOLD),fg='white',width=3,command=self.create_Channel_FRAME)

                                self.removeChannel = Button(self.killMe,bg='#23272A',text=f'-',font=('@Yu Gothic UI Semibold',15,BOLD),fg='white',width=3,command=self.start_DeleteChannel)
                                self.removeChannel.pack(side='left',padx=5)

                                if len(self.channelsFrame.winfo_children()) >= 11:
                                    self.addChannel.pack_forget()
                                else:
                                    self.removeChannel.pack_forget()
                                    self.addChannel.pack(side='left',padx=5)
                                    self.removeChannel.pack(side='left',padx=5)

                            for i in self.currentChannels:
                                if not(i in pickled[1]):
                                    getattr(self,i).pack_forget()
                                    getattr(self,i).destroy()
                                    delattr(self,i)
                                    if self.currentChannel == i:
                                        self.inputBox.pack_forget()
                                        self.channel_Top.config(text='')

                            self.currentChannels = pickled[1]
                        """
                        LOAD THE CHANNELS MESSAGES
                        """
                        for v in pickled[1]: 
                            if hasattr(self,v):
                                scrolledTextObj = getattr(self,v)
                                if len(scrolledTextObj.get('1.0','end')) == 1: 
                                    scrolledTextObj.config(state='normal')  
                                    
                                    for i in pickled[2][v]:
                                        scrolledTextObj.insert('end',i)
                                        scrolledTextObj.yview('end')

                                    scrolledTextObj.config(state='disabled')  

                    elif 'updateUSERNAMEe' in pickled:
                        self.userName = pickled[1]
                    elif 'PEALSLASLAEAFJAILEAVEA' in pickled:
                        if pickled[1] == self.userName:
                            self.connected = False
                            self.clientSocket.close()
                            self.UIObj.createError(isKicked=True)
                            exit(0)
                    else:
                        channel = getattr(self,pickled[1])
                        channel.config(state='normal')
                        channel.insert('end',pickled[0])
                        channel.yview('end')
                        channel.config(state='disabled')  

            except Exception as e:
                print(f'CLIENT ERROR: {e}')
                self.clientSocket.close()

    def close(self):
        self.connected = False
        self.UI.destroy()
        self.clientSocket.close()
        exit(0)

    def start_DeleteChannel(self):
        if hasattr(self,'stop'):
            return

        if len(self.channelsFrame.winfo_children()) == 1:
            return

        for i in self.channelsFrame.winfo_children():
            if isinstance(i,Button):
                if i.cget('text') != '# - logs':
                    i.config(bg='red')
        
        self.stop = Button(self.killMe,text=f'Stop',font=('@Yu Gothic UI Semibold',15,BOLD),fg='white',command=self.stop_Deleting,bg='#23272A')
        self.stop.pack(side='left')

    def stop_Deleting(self):
        for i in self.channelsFrame.winfo_children():
            if isinstance(i,Button):
                if i.cget('text') == f'# - {self.currentChannel}':
                    i.config(bg='#7289DA')
                else:
                    i.config(bg='#23272A')

        self.stop.destroy()
        delattr(self,'stop')

    def create_Channel_FRAME(self):
        if hasattr(self,'createChannelFrame'):
            return

        self.createChannelFrame = Frame(self.channelsFrame,bg='#2C2F33',height=350,width=300)
        self.createChannelFrame.grid(column=0,row=0)

        Label(self.createChannelFrame,text='Create Channel',bg='#2C2F33',font=('@Yu Gothic UI Semibold',15,BOLD),fg='white').pack(side='top',fill='x',pady=10)

        self.CinputBox = Entry(self.createChannelFrame,bg='#2C2F33',fg='white',font=('@Yu Gothic UI Semibold',15,BOLD),borderwidth=2,width=15)
        self.CinputBox.insert('end','Channel Name.')
        self.CinputBox.pack(side='top',padx=5,pady=10)
        
        Button(self.createChannelFrame,text='Create',bg='#2C2F33',font=('@Yu Gothic UI Semibold',15,BOLD),fg='white',width=5,command = self.create_Channel).pack(side='top',padx=5)
        Button(self.createChannelFrame,text='Close',bg='#2C2F33',font=('@Yu Gothic UI Semibold',15,BOLD),fg='white',width=5,command=self.close_Create_Frame).pack(side='top',padx=5,pady=10)
        

    def close_Create_Frame(self):
        self.createChannelFrame.destroy()
        delattr(self,'createChannelFrame')

    def create_Channel(self):
        text = self.CinputBox.get()
        if len(text) > 0:
            if len(text) > 15:
                text = text[0:15]
            
            if text in self.currentChannels:
                self.CinputBox.delete(0,'end')
                self.CinputBox.insert('end','Channel Exists!')
                return

            self.clientSocket.send(pickle.dumps(['nEWANNCHANNELDATIAJIJDAJIFAIJF',text]))
            self.createChannelFrame.destroy()
            delattr(self,'createChannelFrame')

    def make_Channel_Button(self,v,currentRow):
        setattr(self,f'{v}BUTTON',Button(self.channelsFrame,text=f'# - {v}',font=('@Yu Gothic UI Semibold',15,BOLD),fg='white',command=lambda : self.make_Channel_Button_Work(v))) 
        sus = getattr(self,f'{v}BUTTON')
        sus.grid(column=0,row=currentRow,pady=10,padx=10)

        if v == self.currentChannel:
           sus.config(bg='#7289DA')
        else:
           sus.config(bg='#23272A')
    
    def make_Channel_Button_Work(self,buttonName):
        if getattr(self,f'{buttonName}BUTTON').cget("bg") == 'red':
            self.clientSocket.send(pickle.dumps(['nEWANNCHANNELDATIAJIJDAJIFAIJF',buttonName]))
        else:
            self.inputBox.pack_forget()
            self.inputBox.delete(0,'end')

            for i in self.currentChannels:
                getattr(self,i).pack_forget()
                getattr(self,f'{i}BUTTON').config(bg='#23272A')

            self.currentChannel = buttonName
            self.channel_Top.config(text=f'# - {buttonName}')

            getattr(self,buttonName).pack(pady=20,padx=20,anchor=NW)
            getattr(self,f'{buttonName}BUTTON').config(bg='#7289DA')

            if buttonName != 'logs':
                self.inputBox.pack(pady=20,padx=20,anchor=NW)
                self.inputBox.insert('end','Enter a message.')
    
    def set_MemberButton(self,butt):
        user = re.findall("[\w']+", butt.cget('text'))[1]
    
        butt.config(command = lambda : self.KickMember(user))
        butt.bind('<Enter>',self.on_MouseEnter)
        butt.bind('<Leave>',self.on_MouseLeave)
        
    def KickMember(self,name):
        self.clientSocket.send(pickle.dumps(['KCIKAUSAEJAHRFAJfhASJGH',name]))
        
    def on_MouseEnter(self,e):
        text = e.widget.cget('text')
        text = f'Kick {text}'

        e.widget.config(background='red',text=text)

    def on_MouseLeave(self,e):
        text = e.widget.cget('text')
        text = text.split('Kick')[1].replace(' ','')

        e.widget.config(background='#23272A',text=text)