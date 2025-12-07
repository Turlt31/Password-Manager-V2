from argon2.low_level import hash_secret_raw, Type
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps


import secrets
import base64
import random
import string
import pyotp
import json
import os

from theme import loadTheme
import cryption
import apps

root = Tk()
root.title("Password Manager")
root.geometry("1266x668")
root.configure(bg="#161A20")
root.iconbitmap('icon/pwm.ico')
menuOpen = ""

def loginScreen():
    for widget in root.winfo_children(): widget.destroy()
    
    BG_COLOR_LIGHT = "#E2DFD2"
    FG_COLOR = "#FFFFFF"
    HIGHLIGHT_COLOR = "#D0D0D0"
    
    placeholderU = "Username/Email"
    placeholderP = "Password"

    def onHoverEnter(event):
            widget = event.widget

            if widget == logB: logB.configure(fg="grey")
            if widget == regB: regB.configure(fg="#89CFF0")
    def onHoverLeave(event): 
        widget = event.widget

        if widget == logB: logB.configure(fg="black")
        if widget == regB: regB.configure(fg="blue")

    def on_focus_in(event):
        widget = event.widget

        if widget == u:
            if widget.get() == placeholderU:
                widget.delete(0, END)
                widget.config(fg="black")
        elif widget == p:
            if widget.get() == placeholderP:
                widget.delete(0, END)
                widget.config(show="●", fg="black")
    def on_focus_out(event):
        widget = event.widget

        if widget == u:
            if widget.get() == "":
                widget.insert(0, placeholderU)
                widget.config(fg="grey")
        elif widget == p:
            if widget.get() == "":
                widget.insert(0, placeholderP)
                widget.config(show="", fg="grey")

    def register(event):
        for widget in rect.winfo_children(): widget.destroy()
        def on_focus_in(event):
            widget = event.widget

            if widget == u:
                if widget.get() == placeholderU:
                    widget.delete(0, END)
                    widget.config(fg="black")
            elif widget == p:
                if widget.get() == placeholderP:
                    widget.delete(0, END)
                    widget.config(show="●", fg="black")
        def on_focus_out(event):
            widget = event.widget

            if widget == u:
                if widget.get() == "":
                    widget.insert(0, placeholderU)
                    widget.config(fg="grey")
            elif widget == p:
                if widget.get() == "":
                    widget.insert(0, placeholderP)
                    widget.config(show="", fg="grey")
        
        def saveAcc():
            username = u.get()
            password = p.get()

            passwordData = cryption.createMasterPassword(password)

            if username == placeholderU or username == "":
                Label(rect, text="Please enter a username!", font=('arial', 20), bg=BG_COLOR_LIGHT, fg="red").place(x=80, y=340)
                return   
            if password == placeholderP or password == "":
                Label(rect, text="Please enter a password!", font=('arial', 20), bg=BG_COLOR_LIGHT, fg="red").place(x=80, y=340)
                return

            with open('files/logins.txt', 'r') as f: usernames = f.readlines()
            
            usernameAvailable = True
            for i in usernames:
                i = i.split(',')
                if i[2] == username:
                    usernameAvailable = False
                    break
            
            if not usernameAvailable:
                Label(rect, text="Username already exists!", font=('arial', 20), bg=BG_COLOR_LIGHT, fg="red").place(x=80, y=340)
            else:
                data = {
                    "settings": {
                        "General Settings": {
                            "passwordsShownByDefault": False,
                            "favicons": True,
                            "defaultScreen": "pasw",
                            "theme": "blue"
                        },
                        "Authentication": {
                            "requirePin": False,
                            "pin": "1111",
                            "auth": False,
                            "authKey": f"{pyotp.random_base32()}"
                        }
                    }
                }
                with open('files/logins.txt', 'a') as f:
                    f.write(f"{passwordData["salt"]},{passwordData["login_hash"]},{username}\n")
                os.mkdir(f"files/{username}")
                os.mkdir(f"files/{username}/config")


                [open(f"files/{username}/{file}", 'w').close() for file in ["cards.txt", "passwords.txt", "notes.txt"]]
                with open(f"files/{username}/config/settings.json", "w") as f:
                    json.dump(data, f, indent=4)

                Label(rect, text="Account Created!", font=('arial', 32), bg=BG_COLOR_LIGHT, fg="green").place(x=80, y=340)

        Label(rect, text="Welcome New User!", font=('arial', 35), bg=BG_COLOR_LIGHT).place(x=40, y=10)
        Label(rect, text="Register", font=('arial', 32), bg=BG_COLOR_LIGHT).place(x=155, y=60)
        
        u = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=1.5, justify='center')
        u.place(x=10, y=120, width=480, height=60)
        u.insert(0, placeholderU)
        u.bind("<FocusIn>", on_focus_in)
        u.bind("<FocusOut>", on_focus_out)

        p = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=1.5, justify='center')
        p.place(x=10, y=185, width=480, height=60)
        p.insert(0, placeholderP)
        p.bind("<FocusIn>", on_focus_in)
        p.bind("<FocusOut>", on_focus_out)
    
        Button(rect, text="Register", font=("arial", 32), command=saveAcc).place(x=150, y=260, width=200, height=60)
        Button(rect, text="Return", font=("arial", 32), command=loginScreen).place(x=150, y=420, width=200, height=60)
    def login():
        def otp():
            def on_return(event): authenticate()
            def authenticate():
                with open(f"files/{user}/config/settings.json", 'r') as f: data = json.load(f)
                totp = pyotp.TOTP(data["settings"]["Authentication"]["authKey"])
                if totp.verify(code.get()): mainScreen(user.strip('\n')); otpS.destroy()
                else: pass
            

            otpS = Toplevel(root)
            otpS.title("2 Factor Authentication")
            otpS.geometry("500x200")
            otpS.resizable(False, False)
            otpS.config(bg=BG_COLOR_LIGHT)
            
            Label(otpS, text="2 Factor Authentication", font=('arial', 25), bg=BG_COLOR_LIGHT).place(x=80,y=10)
            Label(otpS, text="Code", font=('arial', 20), bg=BG_COLOR_LIGHT).place(x=15, y=70)
            code = Entry(otpS, font=('arial', 20), justify='center')
            code.place(x=100, y=73, height=35, width=200)
            code.bind("<Return>", on_return)
            Button(otpS, text="Authenticate", font=('arial', 20), command=authenticate).place(x=310, y=73, height=35, width=180)
        user = u.get()
        pasw = p.get()

        with open("files/logins.txt", 'r') as f:
            data = f.readlines()

            for i in data:
                i = i.split(",")
                if user == i[2].strip('\n'):
                    loginBool, vaultKey = cryption.verifyMasterPassword(pasw, i[0], i[1])
                    if loginBool:
                        with open(f'files/{user}/config/settings.json', 'r') as f:
                            data = json.load(f)
                        if not data["settings"]["Authentication"]["auth"]:
                            mainScreen(user, vaultKey)
                        else:
                            print("Auth Needed")
                            otp()
                        break
                    elif user == i[2].strip('\n') and not loginBool: errL.config(text="[-] Incorrect Password", fg="red"); break
                    else: errL.config(text="[-] Account Does Not Exist", fg="red")

    rect = Canvas(root, width=500, height=500, bg=BG_COLOR_LIGHT, highlightthickness=0)
    rect.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    rect.create_line(0, 0, 0, 500, fill="black", width=10)
    rect.create_line(0, 0, 500, 0, fill="black", width=10)
    rect.create_line(500, 0, 500, 500, fill="black", width=10)
    rect.create_line(0, 500, 500, 500, fill="black", width=10)

    Label(rect, text="Welcome Back!", font=('arial', 35), bg=BG_COLOR_LIGHT).place(x=85, y=10)
    Label(rect, text="Login", font=('arial', 32), bg=BG_COLOR_LIGHT).place(x=195, y=60)

    u = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=1.5, justify='center')
    u.place(x=10, y=120, width=480, height=60)
    u.insert(0, placeholderU)
    u.bind("<FocusIn>", on_focus_in)
    u.bind("<FocusOut>", on_focus_out)

    p = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=1.5, justify='center')
    p.place(x=10, y=185, width=480, height=60)
    p.insert(0, placeholderP)
    p.bind("<FocusIn>", on_focus_in)
    p.bind("<FocusOut>", on_focus_out)

    errL = Label(rect, font=('arial', 30), bg=BG_COLOR_LIGHT)
    errL.place(x=10, y=350)

    logB = Button(rect, text="Login", font=("arial", 32), command=login)
    logB.place(x=150, y=260, width=200, height=60)
    logB.bind("<Enter>", onHoverEnter)
    logB.bind("<Leave>", onHoverLeave)
    regB = Label(rect, text="Dont have an account? Register", font=('arial', 20, 'underline'), bg=BG_COLOR_LIGHT, fg="blue")
    regB.place(x=10, y=450)
    regB.bind("<Button-1>", register)
    regB.bind("<Enter>", onHoverEnter)
    regB.bind("<Leave>", onHoverLeave)

def mainScreen(user, vaultKey):
    for widget in root.winfo_children(): widget.destroy()
    placeholder = "Search..."
    
    with open(f'files/{user}/config/settings.json', 'r') as f:
        global menuOpen
        data = json.load(f)
        menuOpen = data["settings"]["General Settings"]["defaultScreen"]
        currentTheme = loadTheme(data["settings"]["General Settings"]["theme"])

    BG_PANEL = currentTheme["BG_PANEL"]
    BG_LIST = currentTheme["BG_LIST"]
    BG_CARD = currentTheme["BG_CARD"]
    
    BG_INPUT = currentTheme["BG_INPUT"]
    BG_BUTTON = currentTheme["BG_BUTTON"]
    BG_BUTTON_ALT = currentTheme["BG_BUTTON_ALT"]

    FG_COLOR_P = currentTheme["FG_PRIMARY"]
    FG_COLOR_S = currentTheme["FG_SECONDARY"]
    ACCENT_BLUE = currentTheme["ACCENT_BLUE"]
    ACCENT_BLUE_GLOW = currentTheme["ACCENT_BLUE_GLOW"]
    
    def load(user):
        pa, ca = [], []
        with open(f"files/{user}/passwords.txt", 'r') as f: data = f.readlines()
        for i in data: pa.append(cryption.decrypt_line(vaultKey, i))
        
        with open(f"files/{user}/cards.txt", 'r') as f: data = f.readlines()
        for i in data: ca.append(cryption.decrypt_line(vaultKey, i))


        return pa, ca

    passwordList, cardList = load(user)

    def onClick(event):
        global menuOpen
        widget = event.widget

        if widget == loginsB:
            addB.config(state="normal")
            searchE.config(state="normal")
            loginsB.config(fg=ACCENT_BLUE, image=loginsIconBPTK)
            cardsB.config(fg=FG_COLOR_P, image=cardsIconWPTK)
            menuOpen = "pasw"
            passwordList, cardList = load(user)
            apps.passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        if widget == cardsB:
            addB.config(state="normal")
            searchE.config(state="normal")
            cardsB.config(fg=ACCENT_BLUE, image=cardsIconBPTK)
            loginsB.config(fg=FG_COLOR_P, image=loginsIconWPTK)
            menuOpen = "card"
            passwordList, cardList = load(user)
            apps.cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        if widget == logoutB: loginScreen()
        if widget == settingsB:
            addB.config(state="disabled")
            searchE.config(state="disabled")
            menuOpen = "sett"
            cardsB.config(fg=FG_COLOR_P, image=cardsIconWPTK)
            loginsB.config(fg=FG_COLOR_P, image=loginsIconWPTK)
            apps.settings(inner_frame, contFrame, canvas, dataFrame, user)
    def onHoverEnter(event):
        global menuOpen
        widget = event.widget

        if widget == loginsB:
            if menuOpen == "pasw": loginsB.configure(fg=ACCENT_BLUE_GLOW, bg=BG_PANEL, image=loginsIconBSTK)
            else: loginsB.configure(fg=FG_COLOR_S, bg=BG_PANEL, image=loginsIconWSTK)
        if widget == cardsB:
            if menuOpen == "card": cardsB.configure(fg=ACCENT_BLUE_GLOW, bg=BG_PANEL, image=cardsIconBSTK)
            else: cardsB.configure(fg=FG_COLOR_S, bg=BG_PANEL, image=cardsIconWSTK)
        if widget == logoutB: logoutB.configure(fg=FG_COLOR_S, bg=BG_BUTTON_ALT, image=logoutIconGTK)
        if widget == settingsB: settingsB.configure(fg=FG_COLOR_S, bg=BG_BUTTON_ALT, image=settingsIconGTK)
    def onHoverLeave(event): 
        widget = event.widget

        if widget == loginsB:
            if menuOpen == "pasw": loginsB.configure(fg=ACCENT_BLUE, bg=BG_PANEL, image=loginsIconBPTK)
            else: loginsB.configure(fg=FG_COLOR_P, bg=BG_PANEL, image=loginsIconWPTK)
        if widget == cardsB: 
            if menuOpen == "card": cardsB.configure(fg=ACCENT_BLUE, bg=BG_PANEL, image=cardsIconBPTK)
            else: cardsB.configure(fg=FG_COLOR_P, bg=BG_PANEL, image=cardsIconWPTK)
        if widget == logoutB: logoutB.configure(fg=FG_COLOR_P, bg=BG_BUTTON_ALT, image=logoutIconWTK)
        if widget == settingsB: settingsB.configure(fg=FG_COLOR_P, bg=BG_BUTTON_ALT, image=settingsIconWTK)
    def onFocusIn(event):
        if searchE.get() == placeholder:
            searchE.delete(0, END)
            searchE.config(fg=FG_COLOR_P)
    def onFocusOut(event):
        if searchE.get() == "":
            searchE.insert(0, placeholder)
            searchE.config(fg=FG_COLOR_S)
    
    def search(event):
        global menuOpen
        if menuOpen == "pasw":
            apps.passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        if menuOpen == "card":
            apps.cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
    def add():
        def centerWindow(root, win, w, h):
            root.update_idletasks()
            win.update_idletasks()
            root_x = root.winfo_x()
            root_y = root.winfo_y()
            root_w = root.winfo_width()
            root_h = root.winfo_height()

            x = root_x + (root_w // 2) - (w // 2)
            y = root_y + (root_h // 2) - (h // 2)

            win.geometry(f"{w}x{h}+{x-140}+{y+60}")
        global menuOpen
        addScreen = Toplevel(root)
        addScreen.resizable(False, False)
        addScreen.geometry(f"400x570")
        addScreen.iconbitmap('icon/pwm.ico')
        addScreen.configure(bg=BG_PANEL)
        centerWindow(root, addScreen, 400, 570)

        if menuOpen == "pasw":
            addScreen.title("Add Password")
            phN = "Website"
            phU = "Username"
            phP = "Password"
            phAuth = "Authentication Code"
            showVar = [True]
            
            tld = [".com", ".net", ".lt", ".org", ".gov", ".io"]
            selected = StringVar(value=tld[0])


            def on_focus_in(event):
                widget = event.widget

                if widget == wnE:
                    if widget.get() == phN:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left")
                elif widget == uE:
                    if widget.get() == phU:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left")
                elif widget == pE:
                    if widget.get() == phP:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left")
                elif widget == authE:
                    if widget.get() == phAuth:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="center")
            def on_focus_out(event):
                widget = event.widget

                if widget == wnE:
                    if widget.get() == "":
                        widget.insert(0, phN)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == uE:
                    if widget.get() == "":
                        widget.insert(0, phU)
                        widget.config(fg=FG_COLOR_P, justify="center")
                elif widget == pE:
                    if widget.get() == "":
                        widget.insert(0, phP)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == authE:
                    if widget.get() == "":
                        widget.insert(0, phAuth)
                        widget.config(fg=FG_COLOR_P, justify="center")
            
            def showPassword():
                showVar[0] = not showVar[0]

                if showVar[0]:
                    showB.config(text="Show Password")
                    pE.config(show="●")
                else:
                    showB.config(text="Hide Password")
                    pE.config(show="")
            def genPassword():
                length = 10
                letters = string.ascii_letters
                digits = string.digits
                symbols = string.punctuation

                all_chars = letters + digits + symbols.replace(",", "")

                password = [
                    secrets.choice(letters),
                    secrets.choice(digits),
                    secrets.choice(symbols)
                ]

                password += [secrets.choice(all_chars) for _ in range(length - 3)]
                secrets.SystemRandom().shuffle(password)

                pE.delete(0, "end")
                pE.insert(0, "".join(password))
                pE.config(fg=FG_COLOR_P, justify="left")
            def savePassword():
                passwordList = []
                website = wnE.get()
                websiteLink = f"www.{website.lower()}{selected.get()}"
                username = uE.get()
                password = pE.get()
                auth = authE.get()

                if auth == phAuth: account = cryption.encrypt_line(vaultKey, f"{website},{websiteLink},{username},{password}")
                else: account = cryption.encrypt_line(vaultKey, f"{website},{websiteLink},{username},{password},{auth}")

                with open(f"files/{user}/passwords.txt", 'a') as f: f.write(account+'\n')
                with open(f"files/{user}/passwords.txt", 'r') as f: data = f.readlines()
                for i in data: passwordList.append(cryption.decrypt_line(vaultKey, i))
                addScreen.destroy()
                apps.passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)

            Label(addScreen, text="Add Password", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(x=60, y=5)

            wnE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            wnE.place(x=10, y=70, height=50, width=260)
            wnE.insert(0, phN)
            wnE.bind("<FocusIn>", on_focus_in)
            wnE.bind("<FocusOut>", on_focus_out)

            tldB =  OptionMenu(addScreen, selected, *tld)
            tldB.config(font=('arial', 26), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            tldB["menu"].config(font=('arial', 18))
            tldB.place(x=280, y=70, height=50, width=110)

            uE = Entry(addScreen, font=('arial', 24), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            uE.place(x=10, y=135, height=50, width=380)
            uE.insert(0, phU)
            uE.bind("<FocusIn>", on_focus_in)
            uE.bind("<FocusOut>", on_focus_out)

            pE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            pE.place(x=10, y=200, height=50, width=380)
            pE.insert(0, phP)
            pE.bind("<FocusIn>", on_focus_in)
            pE.bind("<FocusOut>", on_focus_out)

            Label(addScreen, text="Optional", font=('arial', 30), bg=BG_PANEL, fg=FG_COLOR_P).place(x=125, y=280)

            authE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            authE.place(x=10, y=340, height=50, width=380)
            authE.insert(0, phAuth)
            authE.bind("<FocusIn>", on_focus_in)
            authE.bind("<FocusOut>", on_focus_out)

            genB = Button(addScreen, text="Generate Password", font=('arial', 14), command=genPassword, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=2, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            genB.place(x=15, y=455, height=45, width=180)

            showB = Button(addScreen, text="Show Password", font=('arial', 14), command=showPassword, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=1, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            showB.place(x=205, y=455, height=45, width=180)

            saveB = Button(addScreen, text="Save Account", font=('arial', 30),command=savePassword, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=1, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            saveB.place(x=10, y=510, height=50, width=380)

            showPassword()
        if menuOpen == "card":
            addScreen.title("Add Card")

            cardList = []
            phB = "Bank Name"
            phN = "Name on Card"
            phC = "Card Number"
            phExpd = "MM/YY"
            phCvc = "CVC Code"
            phPin = "PIN Code"

            tld = [".com", ".net", ".lt", ".org", ".gov", ".io"]
            selected = StringVar(value=tld[0])

            def on_focus_in(event):
                widget = event.widget

                if widget == bE:
                    if widget.get() == phB:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left")
                elif widget == nE:
                    if widget.get() == phN:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left")
                elif widget == cE:
                    if widget.get() == phC:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left")
                elif widget == expdE:
                    if widget.get() == phExpd:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="center")
                elif widget == cvcE:
                    if widget.get() == phCvc:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="center")
                elif widget == pinE:
                    if widget.get() == phPin:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="center") 
            def on_focus_out(event):
                widget = event.widget

                if widget == bE:
                    if widget.get() == "":
                        widget.insert(0, phB)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == nE:
                    if widget.get() == "":
                        widget.insert(0, phN)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == cE:
                    if widget.get() == "":
                        widget.insert(0, phC)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == expdE:
                    if widget.get() == "":
                        widget.insert(0, phExpd)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == cvcE:
                    if widget.get() == "":
                        widget.insert(0, phCvc)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == pinE:
                    if widget.get() == "":
                        widget.insert(0, phPin)
                        widget.config(fg=FG_COLOR_S, justify="center")
            def format_expiry(event=None):
                text = expdE.get()

                digits = "".join([c for c in text if c.isdigit()])

                digits = digits[:4]

                formatted = ""
                if len(digits) >= 2:
                    formatted = digits[:2] + "/" + digits[2:]
                else:
                    formatted = digits

                if expdE.get() != formatted:
                    expdE.delete(0, END)
                    expdE.insert(0, formatted)
            def saveCard():
                cardDetails = cryption.encrypt_line(vaultKey, f"{bE.get()},www.{bE.get().lower()}{selected.get()},{nE.get()},{cE.get()},{expdE.get()},{cvcE.get()},{pinE.get()}")

                with open(f"files/{user}/cards.txt", 'a') as f: f.write(cardDetails+'\n')
                with open(f"files/{user}/cards.txt", 'r') as f: data = f.readlines()
                for i in data: cardList.append(cryption.decrypt_line(vaultKey, i))
                addScreen.destroy()
                apps.cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)

            Label(addScreen, text="Add Card", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(x=100, y=5)

            bE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            bE.place(x=10, y=70, height=50, width=260)
            bE.insert(0, phB)
            bE.bind("<FocusIn>", on_focus_in)
            bE.bind("<FocusOut>", on_focus_out)

            tldB =  OptionMenu(addScreen, selected, *tld)
            tldB.config(font=('arial', 26), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            tldB["menu"].config(font=('arial', 18))
            tldB.place(x=280, y=70, height=50, width=110)

            nE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            nE.place(x=10, y=135, height=50, width=380)
            nE.insert(0, phN)
            nE.bind("<FocusIn>", on_focus_in)
            nE.bind("<FocusOut>", on_focus_out)

            cE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            cE.place(x=10, y=220, height=50, width=380)
            cE.insert(0, phC)
            cE.bind("<FocusIn>", on_focus_in)
            cE.bind("<FocusOut>", on_focus_out)

            expdE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            expdE.place(x=10, y=285, height=50, width=380)
            expdE.insert(0, phExpd)
            expdE.bind("<FocusIn>", on_focus_in)
            expdE.bind("<FocusOut>", on_focus_out)
            expdE.bind("<KeyRelease>", format_expiry)

            cvcE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            cvcE.place(x=10, y=365, height=50, width=380)
            cvcE.insert(0, phCvc)
            cvcE.bind("<FocusIn>", on_focus_in)
            cvcE.bind("<FocusOut>", on_focus_out)

            pinE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            pinE.place(x=10, y=430, height=50, width=380)
            pinE.insert(0, phPin)
            pinE.bind("<FocusIn>", on_focus_in)
            pinE.bind("<FocusOut>", on_focus_out)

            saveB = Button(addScreen, text="Save Card", font=('arial', 30), command=saveCard, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=1, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            saveB.place(x=10, y=510, height=50, width=380)

    root.columnconfigure(0, weight=3)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=5)
    root.rowconfigure(0, weight=1)

    menuFrame = Frame(root, bg=BG_PANEL)
    menuFrame.grid(row=0, column=0, sticky="nsew")
    
    Label(menuFrame, text=f"Welcome!", font=('arial', 30), bg=BG_PANEL, fg=FG_COLOR_P).place(x=5, y=5)
    Label(menuFrame, text=user, font=('arial', 30), bg=BG_PANEL, fg=FG_COLOR_P).place(x=30, y=45)

    listFrame = Frame(root, bg=BG_LIST)
    listFrame.grid(row=0, column=1, sticky="nsew")
    listFrame.grid_rowconfigure(0, minsize=50, weight=0)
    listFrame.grid_rowconfigure(1, weight=1)
    listFrame.grid_columnconfigure(0, weight=1)
    listFrame.grid_columnconfigure(1, weight=0)

    contFrame = Frame(listFrame, bg=BG_PANEL)
    contFrame.grid(row=0, column=0, columnspan=2, sticky="ew")
    contFrame.grid_columnconfigure(0, weight=1)
    contFrame.grid_columnconfigure(1, weight=0)

    style = ttk.Style()
    style.theme_use("default")

    style.layout("Vertical.TScrollbar", [
    ('Vertical.Scrollbar.trough', {
        'children': [
            ('Vertical.Scrollbar.thumb', {'unit': '1', 'sticky': 'nswe'})
        ],
        'sticky': 'ns'
    })
])
    style.configure(
        "Vertical.TScrollbar",
        background="#3a3f47",
        troughcolor=BG_LIST,
        bordercolor=BG_LIST,
        arrowcolor="#ffffff",
        relief="flat",
        borderwidth=0
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", "#505660")]
    )

    canvas = Canvas(listFrame, bg=BG_LIST, highlightthickness=0, bd=0, relief="flat")
    scrollbar = ttk.Scrollbar(listFrame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar.grid(row=1, column=1, sticky="ns")
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    inner_frame = Frame(canvas, bg=BG_LIST)
    inner_frame.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    canvas.create_window((0,0), window=inner_frame, anchor="nw")

    searchE = Entry(contFrame, font=("arial", 20), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify='center')
    searchE.grid(row=0, column=0, sticky="ew", padx=3, pady=3)
    searchE.insert(0, placeholder)
    searchE.bind("<FocusIn>", onFocusIn)
    searchE.bind("<FocusOut>", onFocusOut)
    searchE.bind("<Key>", search)

    addB = Button(contFrame, text="+", font=('arial', 35, 'bold'), command=add, bg=BG_BUTTON, fg=FG_COLOR_P, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
    addB.grid(row=0, column=1, sticky="e", padx=3, pady=3)

    dataFrame = Frame(root, bg=BG_CARD)
    dataFrame.grid(row=0, column=2, sticky="nsew")

    loginsIconWP = Image.open("icon/buttonImg/key_WP.png").resize((52,52), Image.Resampling.LANCZOS)
    loginsIconWPTK = ImageTk.PhotoImage(loginsIconWP)
    loginsIconWS = Image.open("icon/buttonImg/key_WS.png").resize((52,52), Image.Resampling.LANCZOS)
    loginsIconWSTK = ImageTk.PhotoImage(loginsIconWS)

    loginsIconBP = Image.open("icon/buttonImg/key_BP.png").resize((52,52), Image.Resampling.LANCZOS)
    loginsIconBPTK = ImageTk.PhotoImage(loginsIconBP)
    loginsIconBS = Image.open("icon/buttonImg/key_BS.png").resize((52,52), Image.Resampling.LANCZOS)
    loginsIconBSTK = ImageTk.PhotoImage(loginsIconBS)

    loginsB = Label(menuFrame, text=" Logins", image=loginsIconWPTK, compound='left', font=('arial', 32), anchor="w", bg=BG_PANEL, fg=FG_COLOR_P)
    loginsB.place(relx=0.05, y=120, relwidth=0.9, height=60)
    loginsB.image = loginsIconWPTK
    loginsB.image = loginsIconWSTK
    loginsB.image = loginsIconBPTK
    loginsB.image = loginsIconBSTK
    loginsB.bind("<Enter>", onHoverEnter)
    loginsB.bind("<Leave>", onHoverLeave)
    loginsB.bind("<Button-1>", onClick)

    cardsIconWP = Image.open("icon/buttonImg/card_WP.png").resize((52,52), Image.Resampling.LANCZOS)
    cardsIconWPTK = ImageTk.PhotoImage(cardsIconWP)
    cardsIconWS = Image.open("icon/buttonImg/card_WS.png").resize((52,52), Image.Resampling.LANCZOS)
    cardsIconWSTK = ImageTk.PhotoImage(cardsIconWS)

    cardsIconBP = Image.open("icon/buttonImg/card_BP.png").resize((52,52), Image.Resampling.LANCZOS)
    cardsIconBPTK = ImageTk.PhotoImage(cardsIconBP)
    cardsIconBS = Image.open("icon/buttonImg/card_BS.png").resize((52,52), Image.Resampling.LANCZOS)
    cardsIconBSTK = ImageTk.PhotoImage(cardsIconBS)

    cardsB = Label(menuFrame, text=" Cards", image=cardsIconWPTK, compound='left', font=('arial', 32), anchor="w", bg=BG_PANEL, fg=FG_COLOR_P)
    cardsB.place(relx=0.05, y=190, relwidth=0.9, height=60)
    cardsB.image = cardsIconWPTK
    cardsB.image = cardsIconWSTK
    cardsB.image = cardsIconBPTK
    cardsB.image = cardsIconBSTK
    cardsB.bind("<Enter>", onHoverEnter)
    cardsB.bind("<Leave>", onHoverLeave)
    cardsB.bind("<Button-1>", onClick)

    settingsIconW = Image.open("icon/buttonImg/settings_W.png").convert("RGBA")
    settingsIconW = settingsIconW.resize((52,52))
    settingsIconWTK = ImageTk.PhotoImage(settingsIconW)

    settingsIconG = Image.open("icon/buttonImg/settings_G.png").convert("RGBA")
    settingsIconG = settingsIconG.resize((52,52))
    settingsIconGTK = ImageTk.PhotoImage(settingsIconG)

    settingsB = Label(menuFrame, image=settingsIconWTK, font=('arial', 25), bg=BG_BUTTON_ALT, fg=FG_COLOR_P, border=1, relief="solid")
    settingsB.image = settingsIconWTK
    settingsB.image = settingsIconGTK
    settingsB.place(relx=0.5, rely=0.9, relwidth=0.45, height=60)
    settingsB.bind("<Button-1>", onClick)
    settingsB.bind("<Enter>", onHoverEnter)
    settingsB.bind("<Leave>", onHoverLeave)

    logoutIconW = Image.open("icon/buttonImg/logout_W.png").convert("RGBA")
    logoutIconW = logoutIconW.resize((52,52))
    logoutIconWTK = ImageTk.PhotoImage(logoutIconW)

    logoutIconG = Image.open("icon/buttonImg/logout_G.png").convert("RGBA")
    logoutIconG = logoutIconG.resize((52,52))
    logoutIconGTK = ImageTk.PhotoImage(logoutIconG)

    logoutB = Label(menuFrame, image=logoutIconWTK, font=('arial', 32), bg=BG_BUTTON_ALT, fg=FG_COLOR_P, border=1, relief="solid")
    logoutB.place(relx=0.05, rely=0.9, relwidth=0.4, height=60)
    logoutB.image = logoutIconWTK
    logoutB.image = logoutIconGTK
    logoutB.bind("<Button-1>", onClick)
    logoutB.bind("<Enter>", onHoverEnter)
    logoutB.bind("<Leave>", onHoverLeave)

    if menuOpen == "pasw":
        apps.passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        loginsB.config(fg=ACCENT_BLUE, image=loginsIconBPTK)
    elif menuOpen == "card":
        apps.cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        cardsB.config(fg=ACCENT_BLUE, image=cardsIconBPTK)
    elif menuOpen == "sett":
        cardsB.config(fg=FG_COLOR_P, image=cardsIconWPTK)
        loginsB.config(fg=FG_COLOR_P, image=loginsIconWPTK)
        apps.settings(inner_frame, contFrame, canvas, dataFrame, user)

loginScreen()

root.mainloop()