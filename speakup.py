import tkinter as tk
from tkinter import Text,Scrollbar,Frame
import os
import speech_recognition as sr
from gtts import gTTS
language = 'en'
from Knowledge import *

class Widget():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Rule Based Questions Generator')
        self.root.configure(bg='#9b12cc')     

        self.photo=tk.PhotoImage(file="listen.gif")
        self.myLabelPic=tk.Label(self.root,image=self.photo)
        self.myLabelPic.grid(row=0,columnspan=3,pady=20)    
                
        self.root.resizable(800, 800)
        
        self.label1 = tk.Label(self.root, text='Input?', font='times 24',bg='#9b12cc', fg='white' )
        self.label1.grid(row=1,columnspan=3)
        
        self.frame1 = Frame(self.root)
        self.frame1.grid(row=2,columnspan=3,padx=20,pady=10,sticky=tk.W)

        self.scrollbar1 = Scrollbar(self.frame1) # height= not permitted here!
        self.scrollbar1.pack(side='right', fill='y')
        
        self.inputTextwid=Text(self.frame1,width=80,bg="#cce6ff",height=8, font='comicsansms 12') # sets the initial size
        self.inputTextwid.pack(side='left', fill='both', expand=True)
        self.inputTextwid.config(yscrollcommand= self.scrollbar1.set)
        
        self.scrollbar1.config(command= self.inputTextwid.yview)

        self.label2 = tk.Label(self.root, text='Output', font='times 22',bg='#9b12cc', fg='white')
        self.label2.grid(row=3,columnspan=3)
        
        self.frame2 = Frame(self.root)
        self.frame2.grid(row=4,columnspan=3,padx=20,pady=10,sticky=tk.W)

        self.scrollbar2 = Scrollbar(self.frame2) # height= not permitted here!
        self.scrollbar2.pack(side='right', fill='y')

        self.outputTextwid=Text(self.frame2,bg="#cce6ff", height=8,font='comicsansms 12') # sets the initial size
        self.outputTextwid.pack(side='left', fill='both', expand=True)
        self.outputTextwid.config(yscrollcommand= self.scrollbar2.set)
        
        self.scrollbar2.config(command= self.outputTextwid.yview)

        
        self.readInputbutton = tk.Button(self.root,bg="#cc00cc" ,fg="white", font='times 14',text='Read Input!', command=self.readInputclicked)
        self.readInputbutton.grid(row=5, column=0, sticky="ew",padx=20,pady=10)
        
        self.readInputbutton.bind("<Enter>",self.entered_readInput)
        self.readInputbutton.bind("<Leave>",self.left_readInput)
        
        self.readOutputbutton = tk.Button(self.root, bg="#cc00cc", fg="white", font='times 14', text='Read output!', command=self.readOutputclicked)
        self.readOutputbutton.grid(row=5,column=1, sticky="ew",padx=20,pady=10)
        
        self.readOutputbutton.bind("<Enter>",self.entered_readOutput)
        self.readOutputbutton.bind("<Leave>",self.left_readOutput)
     
        self.listenbutton = tk.Button(self.root, bg="#cc00cc", fg="white", font='times 14', text='Listen!', command=self.listenclicked)
        self.listenbutton.grid(row=5,column=2,sticky="ew",padx=20,pady=10)
        
        self.listenbutton.bind("<Enter>",self.entered_listen)
        self.listenbutton.bind("<Leave>",self.left_listen)
        
        self.inputSavebutton = tk.Button(self.root, bg="#cc00cc", fg="white", font='times 14',text='Save Input', command=self.saveInputclicked)
        self.inputSavebutton.grid(row=6,column=0,sticky="ew",padx=20,pady=10)
        
        self.inputSavebutton.bind("<Enter>",self.entered_inputSave)
        self.inputSavebutton.bind("<Leave>",self.left_inputSave)
        
        self.inputErasebutton = tk.Button(self.root,bg="#cc00cc", fg="white", font='times 14', text='Erase Input', command=self.eraseInputclicked)
        self.inputErasebutton.grid(row=6,column=1,sticky="ew",padx=20,pady=10)
        
        self.inputErasebutton.bind("<Enter>",self.entered_inputErase)
        self.inputErasebutton.bind("<Leave>",self.left_inputErase)
        
        self.outputSavebutton = tk.Button(self.root,bg="#cc00cc", fg="white", font='times 14', text='Save Output', command=self.saveOutputclicked)
        self.outputSavebutton.grid(row=7,column=0,sticky="ew",padx=20,pady=10)
        
        self.outputSavebutton.bind("<Enter>",self.entered_outputSave)
        self.outputSavebutton.bind("<Leave>",self.left_outputSave)
        
        self.outputErasebutton = tk.Button(self.root,bg="#cc00cc", fg="white", font='times 14', text='Erase Output', command=self.eraseOutputclicked)
        self.outputErasebutton.grid(row=7,column=1,sticky="ew",padx=20,pady=10)
        
        self.outputErasebutton.bind("<Enter>",self.entered_outputErase)
        self.outputErasebutton.bind("<Leave>",self.left_outputErase)
        
        self.Qbutton = tk.Button(self.root, bg="#cc00cc", fg="white", font='times 14',text='Search Questions', command=self.searchQuestionsclicked)
        self.Qbutton.grid(row=6,column=2,sticky="ew",padx=20,pady=10)
        
        self.Qbutton.bind("<Enter>",self.entered_SearchQ)
        self.Qbutton.bind("<Leave>",self.left_SearchQ)

        
        self.exitbutton = tk.Button(self.root,bg="#cc00cc", fg="white", font='times 14', text='Exit', command=self.root.quit)
        self.exitbutton.grid(row=7,column=2,sticky="ew",padx=20,pady=10)
        
        self.exitbutton.bind("<Enter>",self.entered_Exit)
        self.exitbutton.bind("<Leave>",self.left_Exit)
        
        self.root.mainloop()

    def entered_readInput(self, event):
        self.readInputbutton.config(bg="#990099", fg="white")
        
    def entered_readOutput(self,event):
        self.readOutputbutton.config(bg="#990099", fg="white")
                               
    def left_readInput(self,event):
        self.readInputbutton.config(bg="#cc00cc", fg="white")
        
    def left_readOutput(self,event):
        self.readOutputbutton.config(bg="#cc00cc", fg="white")
                                     
    def entered_listen(self,event):
        self.listenbutton.config(bg="#990099", fg="white")
        
    def left_listen(self,event):
        self.listenbutton.config(bg="#cc00cc", fg="white")
                                 
    def entered_inputSave(self,event):
        self.inputSavebutton.config(bg="#990099", fg="white")
        
    def left_inputSave(self,event):
        self.inputSavebutton.config(bg="#cc00cc", fg="white")
                                    
    def entered_inputErase(self,event):
        self.inputErasebutton.config(bg="#990099", fg="white")
        
    def left_inputErase(self,event):
        self.inputErasebutton.config(bg="#cc00cc", fg="white")
                                     
    def entered_outputSave(self,event):
        self.outputSavebutton.config(bg="#990099", fg="white")
        
    def left_outputSave(self,event):
        self.outputSavebutton.config(bg="#cc00cc", fg="white")
                                    
    def entered_outputErase(self,event):
        self.outputErasebutton.config(bg="#990099", fg="white")
        
    def left_outputErase(self,event):
        self.outputErasebutton.config(bg="#cc00cc", fg="white")
                                      
    def entered_Exit(self,event):
        self.exitbutton.config(bg="#990099", fg="white")
        
    def left_Exit(self,event):
        self.exitbutton.config(bg="#cc00cc", fg="white")
                               
    def entered_SearchQ(self,event):
        self.Qbutton.config(bg="#990099", fg="white")
        
    def left_SearchQ(self,event):
        self.Qbutton.config(bg="#cc00cc", fg="white")

    def readInputclicked(self):
        text = self.inputTextwid.get("1.0",tk.END).strip()
        myobj = gTTS(text=text, lang=language, slow=False)
        myobj.save("inputRecord.mp3")
        os.system("inputRecord.mp3")

    def readOutputclicked(self):
        text = self.outputTextwid.get("1.0",tk.END).strip()
        myobj = gTTS(text=text, lang=language, slow=False)
        myobj.save("outputRecord.mp3")
        os.system("outputRecord.mp3")

    def listenclicked(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('Converting speech to text')
            print ('Start talking')
            audio = r.listen(source)
            print ('Done talking')
        
        text ="\n" + r.recognize_google(audio)+'.'
        print(text)
        self.inputTextwid.insert(tk.END,text)

    def eraseInputclicked(self):
        self.inputTextwid.delete('1.0',tk.END)

    def saveInputclicked(self):
        text = "\n" + self.inputTextwid.get("1.0",tk.END).strip()
        with open ('InputRecords.txt','a+') as f:
                    f.writelines(text)
    
    def eraseOutputclicked(self):
        self.outputTextwid.delete('1.0',tk.END)

    def saveOutputclicked(self):
        text = "\n" + self.outputTextwid.get("1.0",tk.END).strip()
        with open ('Outputs.txt','a+') as f:
                    f.writelines(text)


    def searchQuestionsclicked(self):
        sentences = "\n" + self.inputTextwid.get("1.0",tk.END).strip()
        Questions_list=[]
        sentences=sentences.split('.')
        for text in sentences:
            Questions_list+=QSG_1(text) if QSG_1(text) else []
            Questions_list+=QSG_21(text) if QSG_21(text) else []
            Questions_list+=QSG_22(text) if QSG_22(text) else []
            Questions_list+=QSG_23(text) if QSG_23(text) else []
            Questions_list+=QSG_3(text) if QSG_3(text) else []
            Questions_list+=QSG_4(text) if QSG_4(text) else []
            Questions_list+=QSG_5(text) if QSG_5(text) else []
            Questions_list+=QSG_61(text) if QSG_61(text) else []
            Questions_list+=QSG_62(text) if QSG_62(text) else []
            Questions_list+=QSG_63(text) if QSG_63(text) else []
            Questions_list+=QSG_7(text) if QSG_7(text) else []
        self.displayQuestions(Questions_list)

    def displayQuestions(self,Questions_list):
        for Q_tuple in Questions_list:
            self.outputTextwid.insert(tk.END,"\nQ:"+Q_tuple[0])
            self.outputTextwid.insert(tk.END,"\nA:"+Q_tuple[1])

if __name__ == '__main__':
    widget = Widget()
    