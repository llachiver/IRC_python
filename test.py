import tkinter
from tkinter import *

tk = Tk()
tk.title("PICROM chat v0.1")
tk.resizable(True, True)
tk.geometry('400x500')

channel_name=tkinter.Label(tk,bg='light blue',text='HUB')
channel_name.grid(row=0,column=0)

msg_frame=tkinter.Frame(tk,bg='light green')
msg_frame.grid(row=1,column=0)
msg_frame.pack_propagate(0)

msgs=tkinter.Label(msg_frame,text="trouducul > slt lé gen")
msgs.grid(row=1,column=0)
msgs.pack_propagate(0)

#saisie = tkinter.Entry()
#saisie.grid()

tkinter.mainloop()
