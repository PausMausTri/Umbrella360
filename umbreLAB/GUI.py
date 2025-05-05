########def ########
boas_vindas = "Bem-vindo ao GUI"



from tkinter import *

class GUI:
    def __init__(self,master=None):
        self.widget1 = Frame(master)
        self.widget1.pack()
        self.msg = Label(self.widget1, text=boas_vindas, fg="blue", font=("Arial", 20))
        self.msg.pack()
        
        self.sair=Button(self.widget1)
        self.sair["text"]="Sair"
        self.sair["font"]=("Calibri","15")
        self.sair["width"]=5
        self.sair["command"]=self.widget1.quit
        self.sair.pack(side=RIGHT, padx=5, pady=5)

        self.clique=Button(self.widget1)
        self.clique["text"]="Clique aqui"
        self.clique["font"]=("Calibri","15")
        self.clique["width"]=15
        self.clique.bind("<Button-1>", self.mudarTexto)
        self.clique.pack(side=LEFT, padx=5, pady=5)


    def mudarTexto(self, event):
        if self.msg["text"]==boas_vindas:
            self.msg["text"]="Botão clicado"
        else:
            self.msg["text"]=boas_vindas
root=Tk()
GUI(root)
root.mainloop()

