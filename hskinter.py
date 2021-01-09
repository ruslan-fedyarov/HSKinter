# -*- coding: UTF-8 -*-
""" Chinese Words Study (HSK 1-4) on Desktop and Phone

A Python/Tkinter tool for learning HSK 1-4 Mandarin words with flashcards,
pinyin and level stats.

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
__copyright__ = "Copyright 2021"
__date__ = "2021/01/08"
__deprecated__ = False
__email__ =  "fedyarov@ukr.net"
__license__ = "GPLv3"
__maintainer__ = "Ruslan Fedyarov"
__status__ = "Production"
__version__ = "0.4.9"

import sys
if sys.version_info.major==3:
    from tkinter import *
else:
    from Tkinter import *
from random import randrange, choice
from time import time, sleep
from os import path, mkdir
import json
from math import pow

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
cumul=[]

soundfailed=False
changed=False
changed2=False
yn=False
proposed=''

np={'-': '1', '/': '2', '_': '3', '\\': '4', '.': '5'}

mp={u'à': 'a\\', u'á': 'a/', u'è': 'e\\', u'é': 'e/', u'ì': 'i\\', u'í': 'i/', u'ò': 'o\\', u'ó': 'o/', u'ù': 'u\\',
   u'ú': 'u/', u'ü': 'v.', u'ā': 'a-', u'ē': 'e-', u'ě': 'e_', u'ī': 'i-', u'ń': 'n/', u'ō': 'o-', u'ū': 'u-', u'ǎ': 'a_',
   u'ǐ': 'i_', u'ǒ': 'o_', u'ǔ': 'u_', u'ǚ': 'v_', u'ǜ': 'v\\'}

def pinyin_num(s):
    ls=s.split(", ")
    rez0=[]
    for i in ls:
        wrd=i.split(" ")
        rez=[]
        rez2=[]
        for w in wrd:
            w2=""
            plus="."
            plus2="5"
            for c in w:
                if c in mp.keys():
                    w2+=mp[c][0]
                    if len(mp[c])>1:
                        plus=mp[c][1]
                        plus2=np[plus]
                else:
                    w2+=c
            rez.append(w2+plus)
            rez2.append(w2+plus2)
        rez0.append("".join(rez))
        rez0.append("".join(rez2))
    return rez0

def get_rand(n, degr):
    x=randrange(1000000)
    y=int(pow(x, degr)/(pow(1000000, degr))*n)
    return y

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
    global s, i, ni, cni, lasti, cards, ntries, yn, proposed

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
                srtd.append((i, bin(hsk[i*7+4]).count("1"), (int(time())-hsk[i*7+3])//86400, cumul[i][0]/cumul[i][1] if cumul[i][1]>0 else 0))
        srtd.sort(key=lambda tup:(tup[1], -tup[2], tup[3]))
        ntries=0
        while True:
            i=get_rand(min(len(srtd), span if span!=0 else len(srtd)), 5)
            i_low=i
            while i_low>=0:
                if srtd[i_low][1]!=srtd[i][1] or srtd[i_low][2]!=srtd[i][2]:
                    break
                i_low-=1
            i_low+=1

            i_hi=i
            while i_hi<min(len(srtd), span if span!=0 else len(srtd)):
                if srtd[i_hi][1]!=srtd[i][1] or srtd[i_hi][2]!=srtd[i][2]:
                    break
                i_hi+=1
            if i_low!=i_hi:
                i=srtd[i_low+get_rand(i_hi-i_low, 2)][0]
            else:
                i=srtd[i][0]
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
        lab2.config(text=hsk[i*7+1])
        lab2.config(fg="blue")
        lab5.config(text=hsk[i*7+5])
        lab5.config(fg="black")
        lab8.config(text="Crd "+str(nc))
        lab8.config(fg="black" if nc%25!=0 else "red")
    else:
        if yn:
            proposed=choice(hsk[i*7+1].split(", "))
            if randrange(2):
                proposed=choice(hsk[randrange(len(hsk)//7)*7+1].split(", "))
            lab2.config(text="Is it\n'"+proposed+"'?")
            lab2.config(fg="blue")
        lab8.config(text=str(ni-cni)+" / "+str(ni))
        lab8.config(fg="black" if ni%25!=0 else "red")
    se.focus()
    return i

def btnclicked():
    global i, s, soundon, ni, cni, nc, lasti, tm, changed, changed2, ntries, span, yn, proposed
    
    t=int(time())
    if t-tm<1:
        lab2.config(text="Too fast!")
        lab2.config(fg="red")
        return
    tm=t
    su=se.get().lower().strip()

    if (not cards) and su=='':
        lab2.config(text="Take a guess!" if not yn else "Enter 'Y' or 'N'.")
        lab2.config(fg="blue")
        return

    if len(su)>0:
        if su[0]=="'" and su[-1]=="'":
            su=su[1:-1]

    if su.startswith("sp4n") and len(su)>4:
        if su[4].isdigit:
            span=int(su[4:])
            changed2=True
            ntries=0
            i=newquestion()
            return

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
                ntries=0
                i=newquestion()
            return

    if cards:
        nc+=1
        if i in flasti:
            flasti.remove(i)
        flasti.append(i)
        while len(flasti)>10:
            flasti.pop(0)
        i=newquestion()
        if len(su)>0:
            lab2.config(text="You're in flashcard mode.\nClick ' ? ' to turn it off.")
            lab2.config(fg="red")
        
    else:
        s1=hsk[i*7+1]
        s2=hsk[i*7+2]
        hsk[i*7+3]=int(time())
        ss1=s1.lower()

        if yn:
            found2=proposed.lower() in ss1.split(", ") or proposed.lower() in s2.split(", ")
            found=(found2 and su=='y') or (not found2 and su=='n')
        else:
            found=(ss1==su or su in ss1.split(", ") or su in s2.split(", ") or s==su or su.replace(" ", "") in pinyin_num(hsk[i*7+5])) and su!=""
        hsk[i*7+4]<<=1
        hsk[i*7+4]&=0b111111111
        if found:
            hsk[i*7+4]+=1
            cni+=1
            cumul[i][0]+=1
        ni+=1
        cumul[i][1]+=1
        changed=True
    changed2=True

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
    if yn:
        lab5.config(text="True" if found else "False")
        lab5.config(fg="#008000" if found else "red")
    else:
        lab2.config(text="Correct!"+(" It was\n'"+s1+"'." if ss1!=su and (s3=="" or randrange(2)>0) else s3) if found else ("Wrong! " if su!="" else "")+"It was\n'"+s1+"'.")
        lab2.config(fg="#008000" if found else "red")
        lab5.config(text=t)
        lab5.config(fg="black")

def enterpressed(event):
    btnclicked()

def update_exit():
    su=se.get().lower().strip()
    exit_text.set("Exit" if su=="" else "Clear")

def switch_yn():
    global yn, changed2, i
    
    se.delete(0, END)
    yn=not yn
    changed2=True
    if not yn:
        lab2.config(text="'Yes/no' mode off.\nEnter translation.")
        lab2.config(fg="blue")
    i=newquestion()
    update_exit()

def anykey(*args):
    global i, s, cards, flasti, yn
    
    s1=hsk[i*7+1]
    s2=hsk[i*7+2]
    ss1=s1.lower()

    su=se.get().lower().strip()

    update_exit()

    if len(su)>0:
        if su[0]=="'" and su[-1]=="'":
            su=su[1:-1]

    if su=="st4ts":
        se.delete(0, END)
        showst4ts()
        update_exit()
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

    if su.startswith("sp4n"):
        lab2.config(text=str(span if span!=0 else "All")+" words.")
        lab2.config(fg="blue")
        return

    if su=="fl4sh":
        se.delete(0, END)
        switchcrd(None)
        update_exit()
        return

    if not cards and su=="ye5no":
        switch_yn()
        return

    if cards and su=="pr3v":
        if len(flasti)>0:
            i=newquestion(flasti[-1])
            update_exit()
            return

    if su=="s0und":
        se.delete(0, END)
        switchsnd("")
        update_exit()
        return
    
    found=(ss1==su or su in ss1.split(", ") or su in s2.split(", ") or s==su or su.replace(" ", "") in pinyin_num(hsk[i*7+5])) and su!=""
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
        lab2.config(text="" if (any(ans.startswith(su) for ans in [prefix, s, "st4ts", "fl4sh", "pr3v", "s0und", "sp4n", "ye5no", "n"]) or su=='' or any(ans.startswith(su) for ans in ss1.split(", ")) or any(ans.startswith(su) for ans in s2.split(", ")) or any(ans.startswith(su.replace(" ", "")) for ans in pinyin_num(hsk[i*7+5]))) else "Are you sure?")
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

        lab5.config(text=str(int(cumul[i][0]/cumul[i][1]*100 if cumul[i][1]*100>0 else 0))+"%")
        
def escpressed(event):
    finita()

def finita():
    global changed, changed2, yn

    if se.get()!='':
        se.delete(0, END)
        return

    if changed:
        lab2.config(text="Saving...")
        lab2.config(fg="blue")
        root.update_idletasks()
        with open(prefix, 'w') as f:
            f.write(",".join(str(x) for x in lev)+"\n")
            f.write(",".join(str(x) for x in lasti)+"\n")
            for i in range(len(hsk)//7):
                f.write(str(hsk[i*7+3])+","+str(hsk[i*7+4])+","+str(cumul[i][0])+","+str(cumul[i][1])+"\n")
        sleep(0.5)
    if changed2:
        with open(prefix+"tot", 'w') as f:
            f.write("\n".join([str(i) for i in (cni, ni, nc, span, (1 if cards else 0), (1 if yn else 0))]))
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
            if len(s)==2:
                cumul.append([0, 0])
            else:
                cumul.append([int(s[2]), int(s[3])])
            i+=1
else:
    for i in range(len(hsk)//7):
        cumul.append([0, 0])

ni=0
cni=0
nc=0
span=0

if path.isfile(prefix+"tot"):
    with open(prefix+"tot", 'r') as f:
        cni=int(f.readline().rstrip("\n"))
        ni=int(f.readline().rstrip("\n"))
        nc=int(f.readline().rstrip("\n"))
        span=int(f.readline().rstrip("\n"))
        cards=int(f.readline().rstrip("\n"))!=0
        yn=int(f.readline().rstrip("\n"))!=0

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
        
    lab7.config(text="X )" if soundon else "< )")

def switchcrd(event):
    global i, cards, changed2, nc
    cards=not cards
    if cards:
        nc-=1
    lab9.config(text=" ? " if cards else "[ ]")
    if cards:
        btnclicked()
    else:
        i=newquestion()
        if not yn:
            lab2.config(text="Flashcards are off.\nEnter translation.")
            lab2.config(fg="blue")
        lab5.config(text="Y / N")
        lab5.config(fg="black")
    changed2=True

def c4rdhelp(event):
    if lab5.cget("text")=="Y / N":
        switch_yn()
        return
    lab2.config(text=("Pinyin or the word's accuracy ever\n("+str(cumul[i][0])+' of '+str(cumul[i][1]))+").")
    lab2.config(fg="blue")
        
def herozero(event):
    global cni, ni, nc, cards, changed2
    if cards:
        nc=0
        lab8.config(text="Card "+str(nc))
        lab8.config(fg="red")
        lab2.config(text="Number of flashcards shown.\nZeroed.")
        lab2.config(fg="blue")
    else:
        cni=0
        ni=0
        lab8.config(text="0 / 0")
        lab8.config(fg="red")
        lab2.config(text="Wrong vs total.\nZeroed.")
        lab2.config(fg="blue")
    changed2=True

def hskhelp(event):
    lab2.config(text="'"+prefix+"N' & '"+prefix+"N-N'\nturn levels on or off.\nAdd .N or .NN to set % instead (.0 = 100%).")
    lab2.config(fg="blue")

def lastshwn(event):
    lab2.config(text="Last time answered.")
    lab2.config(fg="blue")

def lvlclicked(event):
    showst4ts()

def hanzi(event):
    global i, proposed, yn

    lab2.config(text=hsk[i*7+1] if cards else ("You can also enter\nthe word itself." if not yn else "Is it\n'"+proposed+"'?"))
    lab2.config(fg="blue")
    if cards:
        lab5.config(text=hsk[i*7+5])
        lab5.config(fg="black")

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
lab5=Label(root, text="Y / N", wraplength=75 if pydroid else 50)
lab5.bind("<Button-1>", c4rdhelp)
lab6=Label(root, text="1")
lab6.bind("<Button-1>", hskhelp)
fr=Frame(root)
lab7=Label(fr, text="X )" if soundon else "< )", bd=1, relief=SUNKEN)
lab7.bind("<Button-1>", switchsnd)
lab9=Label(fr, text=" ? " if cards else "[ ]", bd=1, relief=SUNKEN)
lab9.bind("<Button-1>", switchcrd)

lab8=Label(root, text="", bd=1, relief=SUNKEN)
lab8.bind("<Button-1>", herozero)

button = Button (root, text = "OK", command = btnclicked)
exit_text = StringVar()
button2 = Button (root, textvariable=exit_text, command = finita)
exit_text.set("Exit")

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

tm=0
ntries=0
i=newquestion()

if not cards and not yn:
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
    lab7.config(text="< )")
    soundfailed=True

root.protocol("WM_DELETE_WINDOW", finita)
root.mainloop()
