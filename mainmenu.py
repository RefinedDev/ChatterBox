from tkinter import *
from tkinter.font import BOLD

from server import *
from client import *
import requests

class MainMenu:
    def __init__(self):
        self.UI = Tk()

        self.Icon = PhotoImage(file='Assets/ChatterBox_Icon.png')
        self.Icon_TOP = PhotoImage(file='Assets/ChatterBox.png')

        self.UI.iconphoto(False, self.Icon_TOP)
        self.UI.config(bg='#2C2F33')
        self.UI.title("ChatterBox")

    def create_Scene(self):
        for i in self.UI.winfo_children():
            i.destroy()

        Label(self.UI,image=self.Icon,bg='#2C2F33',height=300).pack(side='top')

        self.NameBox = Entry(self.UI,bg = 'white',font=("@Yu Gothic UI Semibold",20,BOLD))
        self.NameBox.insert('end','USERNAME')   
        self.NameBox.pack()

        self.IPBox = Entry(self.UI,bg = 'white',font=("@Yu Gothic UI Semibold",20,BOLD))
        self.IPBox.insert('end','IP ADDRESS')
        self.IPBox.pack(pady=15)
        
        self.Join = Button(self.UI,bg = 'white',text='JOIN',font=("@Yu Gothic UI Semibold",20,BOLD),relief=GROOVE,borderwidth=5,command=self.join_Server)
        self.Join.pack(pady=15)

        self.UI.mainloop()

    def join_Server(self):
        ip = self.IPBox.get().replace(' ','')

        if ip == 'localhost':
            Server('0.0.0.0')
        
        Client(ip,self.NameBox.get(),self)
        
    def createError(self,isKicked = False):
        for i in self.UI.winfo_children():
            i.destroy()

        self.errorFrame = Frame(self.UI,bg='#2C2F33')
        self.errorFrame.pack(fill='both',expand=True)

        if isKicked:
            erorrLable = Label(self.errorFrame,text="KICKED FROM CHAT",bg='#2C2F33',font=('@Yu Gothic UI Semibold',30,BOLD),fg='white')
            erorrLable.pack(fill = 'x')

            description = Label(self.errorFrame,text="You were disconnected from the server because you were kicked.",bg='#2C2F33',font=('@Yu Gothic UI Semibold',30,BOLD),fg='white')
            description.pack(fill = 'x',pady=20)
        
        self.c = Button(self.errorFrame,bg = 'white',text='OK CHIEF',font=("@Yu Gothic UI Semibold",20,BOLD),relief=GROOVE,borderwidth=5,command=self.close_ErrorFrame)
        self.c.pack()


    def close_ErrorFrame(self):
        self.errorFrame.destroy()
        self.create_Scene()