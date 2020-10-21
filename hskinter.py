""" Chinese Words Study (HSK 1-4) on Desktop and Phone

A Python/Tkinter tool for learning HSK 1-4 Mandarin words with flashcards,
Pinyin and level statistics.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
__author__ = "Ruslan Fedyarov"
__contact__ = "fedyarov@ukr.net"
__copyright__ = "Copyright 2020"
__date__ = "2020/10/21"
__deprecated__ = False
__email__ =  "fedyarov@ukr.net"
__license__ = "GPLv3"
__maintainer__ = "Ruslan Fedyarov"
__status__ = "Production"
__version__ = "0.4.5"

import sys
if sys.version_info.major==3:
    from tkinter import *
else:
    from Tkinter import *
from random import randrange
from time import time, sleep
from os import path, mkdir
import json
from math import sqrt

pydroid=False # change to True on Android
soundon=False # default sound status
cards=True # start in flashcard mode

prefix="hsk"
prefix2="HSK"
lng="zh-cn"
mp3s="gtts/"
tit="HSKinter"

lev=[1, 0, 0, 0, 0, 0]
lsiz=[0, 150, 300, 600, 1200, 2500, 5000]

lasti=[]
flasti=[]

soundfailed=False
changed=False

def showst4ts():
    lev2=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for j in range(len(hsk)//7):
        for jj in range(len(lsiz)):
            if lsiz[jj]>j:
                break
            lbase=lsiz[jj]

        ll=lev[hsk[j*7+6]-1]    

        if ll==1 or (ll>1 and round((j-lbase+1)/(lsiz[jj]-lbase), 5)<=round(ll-int(ll), 5)):
            lev2[bin(hsk[j*7+4]).count("1")]+=1
    ss=""
    jj=0
    for j in range(9, -1, -1):
        if lev2[j]!=0:
            if jj!=0:
                ss+=","+("\n" if (jj%3==0 and jj<9) else " ")
            ss+=str(j)+"-"+str(lev2[j])
            jj+=1

    lab2.config(text=ss+("." if ss!="" else ""))
    lab2.config(fg="blue")

def newquestion(oldi=-1):
    global s, i, ni, cni, lasti, cards, nc, ntries

    se.delete(0, END)
    iii=0
    for ii in range(6):
        if lev[ii]>=1:
            iii+=1
    if iii==0:
        lev[0]+=1
        lab2.config(text="Can't turn off all levels!")
        lab2.config(fg="red")
    
    if oldi==-1:
        srtd=[]
        for i in range(len(hsk)//7):
            for j in range(len(lsiz)):
                if lsiz[j]>i:
                    break
                lbase=lsiz[j]

            ll=lev[hsk[i*7+6]-1]    
            if ll==1 or (ll>1 and round((i-lbase+1)/(lsiz[j]-lbase), 5)<=round(ll-int(ll), 5)):
                srtd.append((i, bin(hsk[i*7+4]).count("1"), (int(time())-hsk[i*7+3])//60))
        srtd.sort(key=lambda tup:(tup[1], -tup[2]))
        ntries=0
        while True:
            i=randrange(min(ntries+1, len(srtd))**2)
            i=srtd[int(sqrt(i))][0]

            if hsk[i*7+1]!="" and ((not (not cards and i in lasti) and not (cards and i in flasti)) or ntries==20) and lev[hsk[i*7+6]-1]>=1: 
                if cards:
                    if len(flasti)==0:
                        break
                    elif i!=flasti[-1]:
                        break
                else:
                    if len(lasti)==0:
                        break
                    elif i!=lasti[-1]:
                        break
            
            if ntries<20:
                ntries+=1
    else:
        i=oldi

    s=hsk[i*7]
    lab.config(text=s)
    ii=hsk[i*7+3]
    if ii!=0:
        ii=(int(time())-ii)//60
        if ii<60:
            lab3.config(text=str(ii)+" min")
        elif ii<1440:
            lab3.config(text=str((ii)//60)+" hr"+("s" if ii//60>1 else ""))
        elif ii<10080:
            lab3.config(text=str((ii)//1440)+" day"+("s" if ii//1440>1 else ""))
        elif ii<43830:
            lab3.config(text=str((ii)//10080)+" wk"+("s" if ii//10080>1 else ""))
        elif ii<525960:
            lab3.config(text=str((ii)//43830)+" mth")
        else:
            lab3.config(text=str((ii)//525960)+" yr"+("s" if ii//525960>1 else ""))
        
    else :
        lab3.config(text="Never")
    lab4.config(text="Lvl "+str(bin(hsk[i*7+4]).count("1")))
    
    lab6.config(text=prefix2+" "+chr(48+hsk[i*7+6]))
    if cards:
        nc+=1
        lab2.config(text=hsk[i*7+1])
        lab2.config(fg="blue")
        lab5.config(text=hsk[i*7+5])
        lab5.config(fg="black")
        lab8.config(text="Crd "+str(nc))
    else:
        lab8.config(text=str(cni)+" / "+str(ni))
    se.focus()
    return i

def btnclicked():
    global i, s, soundon, ni, cni, lasti, tm, changed, ntries
    
    t=int(time())
    if t-tm<1:
    	return
    tm=t
    su=se.get().lower()

    if len(su)>0:
        if su[0]=="'" and su[-1]=="'":
            su=su[1:-1]

    if len(su)>=len(prefix)+1:
        if su[:len(prefix)]==prefix and su[len(prefix)] in "1234":
            t=int(su[len(prefix)])-1
            su=su.replace(".", "")
            if len(su)==len(prefix)+2:
                if su[len(prefix)+1].isdigit():
                    lev[t]=int(lev[t])+int(su[len(prefix)+1])/10.0
                    changed=True
                else:
                    se.delete(0, END)
                    t=round((lev[t]-int(lev[t]))*100)
                    if t==0:
                        t=100
                    lab2.config(text=str(t)+"%")
                    lab2.config(fg="blue")
                    return
            elif len(su)==len(prefix)+3:
                if su[len(prefix):].isdigit():
                    lev[t]=int(lev[t])+int(su[len(prefix)+1:])/100.0
                    changed=True
                elif su[len(prefix)+2].isdigit():
                    while t<=int(su[len(prefix)+2])-1:
                        lev[t]=lev[t]+(-1 if lev[t]>=1 else 1)
                        t+=1
                    changed=True
            elif len(su)>len(prefix)+3 and su[len(prefix)+2].isdigit() and su[len(prefix)+3:].isdigit():
                while t<=int(su[len(prefix)+2])-1:
                    if len(su)==len(prefix)+4:
                        lev[t]=int(lev[t])+int(su[len(prefix)+3])/10.0
                    else:
                        lev[t]=int(lev[t])+int(su[len(prefix)+3:])/100.0
                    t+=1
                changed=True
            else:
                lev[t]=lev[t]+(-1 if lev[t]>=1 else 1)
                changed=True

            if changed:
                i=newquestion()
                ntries=0
            return

    if cards:
        if i in flasti:
            flasti.remove(i)
        flasti.append(i)
        while len(flasti)>10:
            flasti.pop(0)
        i=newquestion()
        if len(su)>0:
            lab2.config(text="You're in flashcard mode.\nType 'fl4sh' to turn it off.")
            lab2.config(fg="red")
        
    else:
        s1=hsk[i*7+1]
        s2=hsk[i*7+2]
        hsk[i*7+3]=int(time())
        ss1=s1.lower()

        found=(ss1==su or su in ss1.split(", ") or su in s2.split(", ") or s==su) and su!=""
        hsk[i*7+4]<<=1
        hsk[i*7+4]&=0b111111111
        if found:
            hsk[i*7+4]+=1
            cni+=1
        ni+=1
        changed=True

    if soundon:
        if not path.exists(mp3s.rstrip("/")):
            mkdir(mp3s.rstrip("/"))
        if not path.isfile(mp3s+str(i)+".mp3"):
            tts = gTTS(s, lang=lng)
            tts.save(mp3s+str(i)+".mp3")

        if not pydroid:
            playsound(mp3s+str(i)+".mp3")
        else:
            sound = SoundLoader.load(mp3s+str(i)+".mp3")
            sound.pitch=.5
            sound.play()

    if cards:
        return

    t=hsk[i*7+5]
    if i in lasti:
        lasti.remove(i)
    lasti.append(i)
    while len(lasti)>10:
        lasti.pop(0)
    s3=""
    if len(su)>0:
        s3="*"*100
        for j in ss1.split(", "):
            if len(j)>0 and len(j)<len(s3):
                s3=j
        for j in s2.split(", "):
            if len(j)>0 and len(j)<len(s3):
                s3=j
        s3="" if len(s3)>=len(su) else "\nYou could also type '"+s3+"'."

    i=newquestion()
    lab2.config(text="Correct!"+(" It was\n'"+s1+"'." if ss1!=su and (s3=="" or randrange(2)>0) else s3) if found else ("Wrong! " if su!="" else "")+"It was\n'"+s1+"'.")
    lab2.config(fg="#008000" if found else "red")
    lab5.config(text=t)
    lab5.config(fg="black")

def enterpressed(event):
    btnclicked()

def anykey(*args):
    global i, s, cards, nc, flasti
    
    s1=hsk[i*7+1]
    s2=hsk[i*7+2]
    ss1=s1.lower()

    su=se.get().lower()
    
    if len(su)>0:
        if su[0]=="'" and su[-1]=="'":
            su=su[1:-1]

    if su=="st4ts":
        se.delete(0, END)
        showst4ts()
        return

    if su.startswith(prefix):
        voc4b=''
        for k in range(6):
            if lev[k]<1:
                continue
            t=round((lev[k]-int(lev[k]))*100)
            if t==0:
                t=100
            voc4b+=str(k+1)+": "+str(t)+"%,"+(" " if k%2==0 else "\n")
        
        lab2.config(text=voc4b.rstrip(", ").rstrip(",\n"))
        lab2.config(fg="blue")
        return


    if su=="fl4sh":
        cards=not cards
        if cards:
            nc=0
            se.delete(0, END)
            btnclicked()
        else:
            i=newquestion()
            lab2.config(text="Flashcards are off.\nEnter your answer.")
            lab2.config(fg="blue")
        return

    if su=="b4ck":
        if len(flasti)>0:
            i=newquestion(flasti[-1])
            return

    if su=="s0und":
        se.delete(0, END)
        switchsnd("")
        return
    
    found=(ss1==su or su in ss1.split(", ") or su in s2.split(", ") or s==su) and su!=""
    if found:
        if not cards:
            lab2.config(text="Correct!\nPress 'OK' to proceed.")
            lab2.config(fg="#008000")
            lab5.config(text=hsk[i*7+5])
            lab5.config(fg="black")
        else:
            lab2.config(text="Nice try.")
            lab2.config(fg="red")
    else:
        lab2.config(fg="red")
        lab2.config(text="" if (su.startswith(prefix) or any(ans.startswith(su) for ans in [prefix, s, "st4ts", "fl4sh", "b4ck", "s0und"]) or su=='' or any(ans.startswith(su) for ans in ss1.split(", ")) or any(ans.startswith(su) for ans in s2.split(", "))) else "Are you sure?")
        t=str(bin(hsk[i*7+4]))[2:]
        while len(t)<9:
            t="0"+t

        if t.count("1")<3:
            lab5.config(fg="red")
        elif t.count("1")<6:
            lab5.config(fg="yellow")
        elif t.count("1")<9:
            lab5.config(fg="#008000")
        else:
            lab5.config(fg="black")


        lab5.config(text=t.replace("1", "|").replace("0", ":"))
        
def escpressed(event):
    finita()

def finita():
    global changed

    if changed:
        lab2.config(text="Saving...")
        lab2.config(fg="blue")
        root.update_idletasks()
        with open(prefix, 'w') as f:
            f.write(",".join(str(x) for x in lev)+"\n")
            f.write(",".join(str(x) for x in lasti)+"\n")
            for i in range(len(hsk)//7):
                f.write(str(hsk[i*7+3]) + ","+str(hsk[i*7+4])+"\n")
        sleep(0.5)
    root.destroy()

if sys.version_info.major==3:
    f=open(prefix+'.json', 'r', encoding='utf8')
else:
    f=open(prefix+'.json', 'r')
hsk=json.load(f)


if path.isfile(prefix):
    with open(prefix, 'r') as f:
        lev=[round(float(i), 2) for i in f.readline().split(",")]
        s=f.readline().rstrip("\n")
        if s!="":
            lasti=[int(i) for i in s.split(",")]
        
        i=0
        for line in f:
            s=line.rstrip('\n').split(",")
            hsk[i*7+3]=int(s[0])
            hsk[i*7+4]=int(s[1])
            i+=1

def switchsnd(event):
    global soundon, soundfailed
    soundon=not soundon
    if soundon and soundfailed:
        soundon=False
        lab2.config(text="Can't initialize sound.")
        lab2.config(fg="red")
    else:
        lab2.config(text="Sound is now "+("on." if soundon else "off."))
        lab2.config(fg="blue")
        
    lab7.config(text="< )" if soundon else "X )")

def switchcrd(event):
    global cards, nc
    cards=not cards
    lab9.config(text="[ ]" if cards else "?")
    if cards:
        nc=0
        btnclicked()
    else:
        i=newquestion()
        lab2.config(text="Flashcards are off.\nEnter your answer.")
        lab2.config(fg="blue")
        lab5.config(text="Type!")
        lab5.config(fg="black")


def c4rdhelp(event):
    lab2.config(text=("Pinyin or level details.\n':' is wrong answer, '|' is correct one."))
    lab2.config(fg="blue")

        
def herozero(event):
    global cni, ni, cards
    if cards:
        lab2.config(text="Number of flashcards shown.")
        lab2.config(fg="blue")
    else:
        cni=0
        ni=0
        lab8.config(text=str(cni)+" of "+str(ni))
        lab2.config(text="Correct vs total.\nZeroed.")
        lab2.config(fg="blue")

def hskhelp(event):
    lab2.config(text="'"+prefix+"N' & '"+prefix+"N-N'\nturn levels on or off.\nAdd .N or .NN to set % instead (.0 = 100%).")
    lab2.config(fg="blue")

def lastshwn(event):
    lab2.config(text="Last time answered.")
    lab2.config(fg="blue")

def lvlclicked(event):
    showst4ts()

def hanzi(event):
    global i

    lab2.config(text=hsk[i*7+1] if cards else "You can also enter\nthe word itself.")
    lab2.config(fg="blue")

def st4ts(event):
    lab2.config(text="Click 'Lvl' or type 'st4ts' for stats.")
    lab2.config(fg="blue")

root=Tk()
root.title(tit)
root.minsize(400, 200)

lab=Label(root, text="")
lab.bind("<Button-1>", hanzi)
lab.config(font=("Helvetica", 30)) # you can adjust the font
lab2=Label(root, text="", wraplength=250 if pydroid else 200, justify="center")
lab2.bind("<Button-1>", st4ts)
lab3=Label(root)
lab3.bind("<Button-1>", lastshwn)
lab4=Label(root)
lab4.bind("<Button-1>", lvlclicked)

var = StringVar()
se=Entry(root, width=20, justify="center", textvariable=var)
se.bind('<Return>', enterpressed)
se.bind('<KP_Enter>', enterpressed)
se.bind('<Escape>', escpressed)
var.trace("w", anykey)
lab5=Label(root, text="Type!", wraplength=75 if pydroid else 50)
lab5.bind("<Button-1>", c4rdhelp)
lab6=Label(root, text="1")
lab6.bind("<Button-1>", hskhelp)
fr=Frame(root)
lab7=Label(fr, text="< )" if soundon else "X )", bd=1, relief=SUNKEN)
lab7.bind("<Button-1>", switchsnd)
lab9=Label(fr, text="[ ]" if cards else " ? ", bd=1, relief=SUNKEN)
lab9.bind("<Button-1>", switchcrd)

lab8=Label(root, text="", bd=1, relief=SUNKEN)
lab8.bind("<Button-1>", herozero)

button = Button (root, text = "OK", command = btnclicked)
button2 = Button (root, text = "Exit", command = finita)

se.grid(column=1, row=3, columnspan=3)
button.grid(column=1, row=5, sticky="e")
button2.grid(column=3, row=5, sticky="w")
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(2, weight=2)
root.grid_rowconfigure(4, weight=3 if not pydroid else 1)
root.grid_rowconfigure(6, weight=12)
root.grid_columnconfigure(0, weight=2)
root.grid_columnconfigure(4, weight=2)
lab.grid(column=0, row=1, columnspan=5)
lab2.grid(column=1, row=2, columnspan=3)
lab3.grid(column=0, row=2)
lab4.grid(column=4, row=3)
lab5.grid(column=4, row=2)
lab6.grid(column=0, row=3)
lab8.grid(column=0, row=5)
fr.grid(column=4, row=5)
lab7.pack(side="left", ipadx=2, padx=2)
lab9.pack(side="left", ipadx=2, padx=2)

ni=0
cni=0
nc=0
tm=0
ntries=0
i=newquestion()

if not cards:
	showst4ts()
try:
    if not pydroid:
        from playsound import playsound
    else:
        from kivy.core.audio import SoundLoader
    from gtts import gTTS
except:
    soundon=False
    lab2.config(text="Can't initialize sound.\n"+("Just press 'OK'." if cards else "But that's okay."))
    lab2.config(fg="red")
    lab7.config(text="X )")
    soundfailed=True

root.protocol("WM_DELETE_WINDOW", finita)
root.mainloop()
