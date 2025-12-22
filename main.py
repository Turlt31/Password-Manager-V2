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

from theme import loadTheme, theme
from icons import loadAllIcons, loadIcon, icon
import cryption
import apps

root = Tk()
root.title("Password Manager")
root.geometry("1266x668")
root.configure(bg="#161A20")
root.iconbitmap('icon/pwm.ico')
menuOpen = ""

def loginScreen(username_prefill=""):
    for widget in root.winfo_children(): widget.destroy()
    loadIcon("eye_p1", "icon/buttonImg/eyeP.png", (50, 50))
    loadIcon("hidden_p1", "icon/buttonImg/hiddenP.png", (50, 50))

    loadIcon("checkT", "icon/buttonImg/checked.png", (50, 50))
    loadIcon("checkF", "icon/buttonImg/unchecked.png", (50, 50))

    BG_COLOR_LIGHT = "#E2DFD2"
    FG_COLOR = "#FFFFFF"
    HIGHLIGHT_COLOR = "#D0D0D0"
    ERROR_COLOR = "#D64545"
    
    placeholderU = "Username/Email"
    placeholderP = "Password"

    def setEntryNormal(entry):
        entry.configure(highlightthickness=1, highlightbackground=HIGHLIGHT_COLOR, highlightcolor=HIGHLIGHT_COLOR)
    def setEntryError(entry, label, message):
        entry.configure(highlightthickness=2, highlightbackground=ERROR_COLOR, highlightcolor=ERROR_COLOR)
        label.config(text=message, fg=ERROR_COLOR)
    def clearEntryError(entry, label):
        setEntryNormal(entry)
        label.config(text="")

    def updatePasswordVisibility(entry, button, show_var):
        if entry.get() == placeholderP:
            entry.config(show="")
            button.config(image=icon("hidden_p1") if show_var.get() else icon("eye_p1"))
        else:
            entry.config(show="" if show_var.get() else "●")
            button.config(image=icon("hidden_p1") if show_var.get() else icon("eye_p1"))

    def loadRememberedUsername():
        if username_prefill:
            return username_prefill
        try:
            with open('files/logins.txt', 'r') as f:
                usernames = [line.split(',')[2].strip() for line in f if line.strip()]
            for name in usernames:
                settings_path = f"files/{name}/config/settings.json"
                if not os.path.exists(settings_path):
                    continue
                with open(settings_path, 'r') as settings_file:
                    data = json.load(settings_file)
                remember = data.get("settings", {}).get("General Settings", {}).get("rememberUsername", False)
                if remember:
                    return name
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return ""
    def persistRememberSetting(username, remember_flag):
        settings_path = f"files/{username}/config/settings.json"
        try:
            with open(settings_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        data.setdefault("settings", {}).setdefault("General Settings", {})["rememberUsername"] = bool(remember_flag)
        with open(settings_path, 'w') as f:
            json.dump(data, f, indent=4)

    def onHoverEnter(event):
            widget = event.widget

            if widget == logB: logB.configure(fg="grey")
            if widget == regB: regB.configure(fg="#89CFF0")
            if widget == rememberL: rememberL.config(fg="grey")
    def onHoverLeave(event): 
        widget = event.widget

        if widget == logB: logB.configure(fg="black")
        if widget == regB: regB.configure(fg="blue")
        if widget == rememberL: rememberL.config(fg="black")

    def getUsernameValue(entry):
        value = entry.get().strip()
        if value in ("", placeholderU):
            return ""
        return value

    def register(event=None, username_prefill=""):
        for widget in rect.winfo_children(): widget.destroy()
        showPasswordVar = BooleanVar(value=False)

        def onFocusIn(event):
            widget = event.widget

            if widget == u:
                if widget.get() == placeholderU:
                    widget.delete(0, END)
                    widget.config(fg="black")
                clearEntryError(u, u_err)
                statusL.config(text="")
            elif widget == p:
                if widget.get() == placeholderP:
                    widget.delete(0, END)
                    widget.config(fg="black")
                updatePasswordVisibility(p, showB, showPasswordVar)
                clearEntryError(p, p_err)
                statusL.config(text="")
        def onFocusOut(event):
            widget = event.widget

            if widget == u:
                if widget.get() == "":
                    widget.insert(0, placeholderU)
                    widget.config(fg="grey")
            elif widget == p:
                if widget.get() == "":
                    widget.insert(0, placeholderP)
                    widget.config(show="", fg="grey")
        def togglePassword():
            showPasswordVar.set(not showPasswordVar.get())
            updatePasswordVisibility(p, showB, showPasswordVar)

        def saveAcc():
            statusL.config(text="")
            clearEntryError(u, u_err)
            clearEntryError(p, p_err)

            username = u.get().strip()
            password = p.get()

            passwordData = cryption.createMasterPassword(password)
            if username == placeholderU or username == "":
                setEntryError(u, u_err, "Enter a username.")
                statusL.config(text="Please fix the highlighted fields.", fg=ERROR_COLOR)
                return   
            if password == placeholderP or password == "":
                setEntryError(p, p_err, "Enter a password.")
                statusL.config(text="Please fix the highlighted fields.", fg=ERROR_COLOR)
                return
            
            try: os.mkdir(f"files/{username}")
            except:
                setEntryError(u, u_err, "Username not avalible.")
                statusL.config(text="Please fix the highlighted fields.", fg=ERROR_COLOR)
                return 

            with open('files/logins.txt', 'r') as f: usernames = f.readlines()
            
            usernameAvailable = True
            for i in usernames:
                i = i.split(',')
                if i[2] == username:
                    usernameAvailable = False
                    break
            
            if not usernameAvailable:
                setEntryError(u, u_err, "Username already exists.")
                statusL.config(text="That username is already taken.", fg=ERROR_COLOR)
            else:
                settingsData = {
                    "settings": {
                        "General Settings": {
                            "passwordsShownByDefault": False,
                            "favicons": True,
                            "defaultScreen": "pasw",
                            "theme": "blue",
                            "clipboardAutoClear": True,
                            "rememberUsername": False,
                            "clipboardTimeoutSeconds": 20
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
                    f.write(f"{passwordData['salt']},{passwordData['login_hash']},{username}\n")
                
                os.mkdir(f"files/{username}/config")
                os.mkdir(f"files/{username}/notes")


                [open(f"files/{username}/{file}", 'w').close() for file in ["cards.txt", "passwords.txt"]]
                with open(f"files/{username}/config/settings.json", "w") as f:
                    json.dump(settingsData, f, indent=4)

                statusL.config(text="Account Created!", fg="green")

        Label(rect, text="Welcome New User!", font=('arial', 35), bg=BG_COLOR_LIGHT).place(x=40, y=10)
        Label(rect, text="Register", font=('arial', 32), bg=BG_COLOR_LIGHT).place(x=155, y=60)
        
        u = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=1.5, justify='center', highlightthickness=1, highlightbackground=HIGHLIGHT_COLOR, highlightcolor=HIGHLIGHT_COLOR)
        u.place(x=10, y=120, width=480, height=60)
        if username_prefill:
            u.insert(0, username_prefill)
            u.config(fg="black")
        else: u.insert(0, placeholderU)

        u.bind("<FocusIn>", onFocusIn)
        u.bind("<FocusOut>", onFocusOut)

        u_err = Label(rect, font=('arial', 12), bg=BG_COLOR_LIGHT, fg=ERROR_COLOR)
        u_err.place(x=10, y=182)

        p = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=1.5, justify='center', highlightthickness=1, highlightbackground=HIGHLIGHT_COLOR, highlightcolor=HIGHLIGHT_COLOR)
        p.place(x=10, y=205, width=480, height=60)
        p.insert(0, placeholderP)
        p.bind("<FocusIn>", onFocusIn)
        p.bind("<FocusOut>", onFocusOut)
    
        showB = Button(rect, relief="flat", bd=0, bg="white", command=togglePassword, activebackground="white")
        showB.config(image=icon("eye_p1"))
        showB.place(x=434, y=209)

        p_err = Label(rect, font=('arial', 12), bg=BG_COLOR_LIGHT, fg=ERROR_COLOR)
        p_err.place(x=10, y=292)

        statusL = Label(rect, font=('arial', 18), bg=BG_COLOR_LIGHT)
        statusL.place(x=10, y=388)
    
        Button(rect, text="Register", font=("arial", 32), command=saveAcc).place(x=40, y=420, width=200, height=60)
        Button(rect, text="Return", font=("arial", 32), command=lambda: loginScreen(getUsernameValue(u))).place(x=260, y=420, width=200, height=60)
    def login():
        def otp():
            def on_return(event): authenticate()
            def authenticate():
                with open(f"files/{user}/config/settings.json", 'r') as f: data = json.load(f)
                totp = pyotp.TOTP(data["settings"]["Authentication"]["authKey"])
                entered = code.get().strip()
                if entered == "":
                    code.configure(highlightthickness=2, highlightbackground=ERROR_COLOR, highlightcolor=ERROR_COLOR)
                    otpErr.config(text="Enter your 2FA code.", fg=ERROR_COLOR)
                    return
                if totp.verify(entered):
                    persistRememberSetting(user.strip('\n'), remember_var.get())
                    mainScreen(user.strip('\n'), vaultKey)
                    otpS.destroy()
                else:
                    code.configure(highlightthickness=2, highlightbackground=ERROR_COLOR, highlightcolor=ERROR_COLOR)
                    otpErr.config(text="Incorrect 2FA code.", fg=ERROR_COLOR)
            

            otpS = Toplevel(root)
            otpS.title("2 Factor Authentication")
            otpS.geometry("500x200")
            otpS.resizable(False, False)
            otpS.config(bg=BG_COLOR_LIGHT)
            
            Label(otpS, text="2 Factor Authentication", font=('arial', 25), bg=BG_COLOR_LIGHT).place(x=80,y=10)
            Label(otpS, text="Code", font=('arial', 20), bg=BG_COLOR_LIGHT).place(x=15, y=70)
            code = Entry(otpS, font=('arial', 20), justify='center',
                         highlightthickness=1, highlightbackground=HIGHLIGHT_COLOR, highlightcolor=HIGHLIGHT_COLOR)
            code.place(x=100, y=73, height=35, width=200)
            code.bind("<Return>", on_return)
            Button(otpS, text="Authenticate", font=('arial', 20), command=authenticate).place(x=310, y=73, height=35, width=180)
            otpErr = Label(otpS, font=('arial', 14), bg=BG_COLOR_LIGHT)
            otpErr.place(x=15, y=120)
            code.bind("<Key>", lambda event: code.configure(highlightthickness=1, highlightbackground=HIGHLIGHT_COLOR, highlightcolor=HIGHLIGHT_COLOR))
            code.bind("<Key>", lambda event: otpErr.config(text=""))
        user = usernameE.get().strip()
        pasw = passwordE.get()

        statusL.config(text="")
        clearEntryError(usernameE, username_err)
        clearEntryError(passwordE, password_err)

        if user == "" or user == placeholderU:
            setEntryError(usernameE, username_err, "Enter your username.")
            statusL.config(text="Please fix the highlighted fields.", fg=ERROR_COLOR)
            return
        if pasw == "" or pasw == placeholderP:
            setEntryError(passwordE, password_err, "Enter your password.")
            statusL.config(text="Please fix the highlighted fields.", fg=ERROR_COLOR)
            return

        try:
            with open("files/logins.txt", 'r') as f:
                data = f.readlines()
        except FileNotFoundError:
            statusL.config(text="No accounts found. Please register first.", fg=ERROR_COLOR)
            return

        found = False
        for i in data:
            i = i.split(",")
            if user == i[2].strip('\n'):
                found = True
                loginBool, vaultKey = cryption.verifyMasterPassword(pasw, i[0], i[1])
                if loginBool:
                    with open(f'files/{user}/config/settings.json', 'r') as f: data = json.load(f)
                    if not data["settings"]["Authentication"]["auth"]:
                        persistRememberSetting(user, remember_var.get())
                        mainScreen(user, vaultKey)
                    else:
                        otp()
                else:
                    setEntryError(passwordE, password_err, "Incorrect password.")
                    statusL.config(text="Incorrect password. Try again.", fg=ERROR_COLOR)
                break
        if not found:
            setEntryError(usernameE, username_err, "Account not found.")
            statusL.config(text="Account does not exist.", fg=ERROR_COLOR)

    rect = Canvas(root, width=500, height=500, bg=BG_COLOR_LIGHT, highlightthickness=0)
    rect.place(relx=0.5, rely=0.5, anchor=CENTER)

    rect.create_line(0, 0, 0, 500, fill="black", width=10)
    rect.create_line(0, 0, 500, 0, fill="black", width=10)
    rect.create_line(500, 0, 500, 500, fill="black", width=10)
    rect.create_line(0, 500, 500, 500, fill="black", width=10)

    Label(rect, text="Welcome Back!", font=('arial', 35), bg=BG_COLOR_LIGHT).place(x=85, y=10)
    Label(rect, text="Login", font=('arial', 32), bg=BG_COLOR_LIGHT).place(x=195, y=60)

    prefillUsername = loadRememberedUsername()
    showPasswordVar = BooleanVar(value=False)
    remember_var = BooleanVar(value=bool(prefillUsername))

    def onFocusIn(event):
        widget = event.widget

        if widget == usernameE:
            if widget.get() == placeholderU:
                widget.delete(0, END)
                widget.config(fg="black")
            clearEntryError(usernameE, username_err)
            statusL.config(text="")
        elif widget == passwordE:
            if widget.get() == placeholderP:
                widget.delete(0, END)
                widget.config(fg="black")
            updatePasswordVisibility(passwordE, showB, showPasswordVar)
            clearEntryError(passwordE, password_err)
            statusL.config(text="")
    def onFocusOut(event):
        widget = event.widget

        if widget == usernameE:
            if widget.get() == "":
                widget.insert(0, placeholderU)
                widget.config(fg="grey")
        elif widget == passwordE:
            if widget.get() == "":
                widget.insert(0, placeholderP)
                widget.config(show="", fg="grey")
    
    def togglePassword():
        showPasswordVar.set(not showPasswordVar.get())
        updatePasswordVisibility(passwordE, showB, showPasswordVar)
    def toggleRemember(event=None):
        remember_var.set(not remember_var.get())
        rememberL.config(image=icon("checkT") if remember_var.get() else icon("checkF"))

        username = usernameE.get().strip()
        if username: persistRememberSetting(username, remember_var.get())

    usernameE = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=1.5, justify='center',highlightthickness=1, highlightbackground=HIGHLIGHT_COLOR, highlightcolor=HIGHLIGHT_COLOR)
    usernameE.place(x=10, y=120, width=480, height=60)
    if prefillUsername:
        usernameE.insert(0, prefillUsername)
        usernameE.config(fg="black")
    else: usernameE.insert(0, placeholderU)
    usernameE.bind("<FocusIn>", onFocusIn)
    usernameE.bind("<FocusOut>", onFocusOut)

    username_err = Label(rect, font=('arial', 12), bg=BG_COLOR_LIGHT, fg=ERROR_COLOR)
    username_err.place(x=10, y=180)

    passwordE = Entry(rect, font=("arial", 28), fg="grey", relief="solid", borderwidth=2, justify='center', highlightthickness=1, highlightbackground=HIGHLIGHT_COLOR, highlightcolor=HIGHLIGHT_COLOR)
    passwordE.place(x=10, y=205, width=480, height=60)
    passwordE.insert(0, placeholderP)
    passwordE.bind("<FocusIn>", onFocusIn)
    passwordE.bind("<FocusOut>", onFocusOut)

    showB = Button(rect, relief="flat", bd=0, bg="white", command=togglePassword, activebackground="white")
    showB.config(image=icon("eye_p1"))
    showB.place(x=434, y=209)

    rememberL = Label(rect, text="Remeber me", image=icon("checkT") if remember_var.get() else icon("checkF"), compound="left", font=('arial', 22), bg=BG_COLOR_LIGHT)
    rememberL.place(x=10, y=285)
    rememberL.bind("<Button-1>", toggleRemember)
    rememberL.bind("<Enter>", onHoverEnter)
    rememberL.bind("<Leave>", onHoverLeave)

    password_err = Label(rect, font=('arial', 12), bg=BG_COLOR_LIGHT, fg=ERROR_COLOR)
    password_err.place(x=10, y=265)

    statusL = Label(rect, font=('arial', 18), bg=BG_COLOR_LIGHT)
    statusL.place(x=10, y=420)

    logB = Button(rect, text="Login", font=("arial", 32), command=login)
    logB.place(x=150, y=350, width=200, height=60)
    logB.bind("<Enter>", onHoverEnter)
    logB.bind("<Leave>", onHoverLeave)

    regB = Label(rect, text="Dont have an account? Register", font=('arial', 20, 'underline'), bg=BG_COLOR_LIGHT, fg="blue")
    regB.place(x=10, y=450)
    regB.bind("<Button-1>", lambda event: register(event, getUsernameValue(usernameE)))
    regB.bind("<Enter>", onHoverEnter)
    regB.bind("<Leave>", onHoverLeave)
def mainScreen(user, vaultKey):
    for widget in root.winfo_children(): widget.destroy()
    placeholder = "Search..."
    loadAllIcons()
    
    with open(f'files/{user}/config/settings.json', 'r') as f:
        global menuOpen
        data = json.load(f)
        menuOpen = data["settings"]["General Settings"]["defaultScreen"]
        loadTheme(data["settings"]["General Settings"]["theme"])

    BG_PANEL = theme("BG_PANEL")
    BG_LIST = theme("BG_LIST")
    BG_CARD = theme("BG_CARD")
    
    BG_INPUT = theme("BG_INPUT")
    BG_BUTTON = theme("BG_BUTTON")
    BG_BUTTON_ALT = theme("BG_BUTTON_ALT")

    FG_COLOR_P = theme("FG_PRIMARY")
    FG_COLOR_S = theme("FG_SECONDARY")
    ACCENT_BLUE = theme("ACCENT_BLUE")
    ACCENT_BLUE_GLOW = theme("ACCENT_BLUE_GLOW")
    
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
            notesB.config(fg=FG_COLOR_P, image=notesIconWPTK)
            menuOpen = "pasw"
            passwordList, cardList = load(user)
            apps.passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        if widget == cardsB:
            addB.config(state="normal")
            searchE.config(state="normal")
            cardsB.config(fg=ACCENT_BLUE, image=cardsIconBPTK)
            loginsB.config(fg=FG_COLOR_P, image=loginsIconWPTK)
            notesB.config(fg=FG_COLOR_P, image=notesIconWPTK)
            menuOpen = "card"
            passwordList, cardList = load(user)
            apps.cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        if widget == notesB:
            addB.config(state="normal")
            searchE.config(state="normal")
            cardsB.config(fg=FG_COLOR_P, image=cardsIconWPTK)
            loginsB.config(fg=FG_COLOR_P, image=loginsIconWPTK)
            notesB.config(fg=ACCENT_BLUE, image=notesIconBPTK)
            menuOpen = "note"
            passwordList, cardList = load(user)
            apps.notes(inner_frame, contFrame, canvas, dataFrame, user, root, vaultKey)
        if widget == logoutB: loginScreen()
        if widget == settingsB:
            addB.config(state="disabled")
            searchE.config(state="disabled")
            menuOpen = "sett"
            cardsB.config(fg=FG_COLOR_P, image=cardsIconWPTK)
            loginsB.config(fg=FG_COLOR_P, image=loginsIconWPTK)
            apps.settings(inner_frame, contFrame, canvas, dataFrame, user, vaultKey)
    def onHoverEnter(event):
        global menuOpen
        widget = event.widget

        if widget == loginsB:
            if menuOpen == "pasw": loginsB.configure(fg=ACCENT_BLUE_GLOW, bg=BG_PANEL, image=loginsIconBSTK)
            else: loginsB.configure(fg=FG_COLOR_S, bg=BG_PANEL, image=loginsIconWSTK)
        if widget == cardsB:
            if menuOpen == "card": cardsB.configure(fg=ACCENT_BLUE_GLOW, bg=BG_PANEL, image=cardsIconBSTK)
            else: cardsB.configure(fg=FG_COLOR_S, bg=BG_PANEL, image=cardsIconWSTK)
        if widget == notesB:
            if menuOpen == "note": notesB.configure(fg=ACCENT_BLUE_GLOW, bg=BG_PANEL, image=notesIconBSTK)
            else: notesB.configure(fg=FG_COLOR_S, bg=BG_PANEL, image=notesIconWSTK)

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
        if widget == notesB: 
            if menuOpen == "note": notesB.configure(fg=ACCENT_BLUE, bg=BG_PANEL, image=notesIconBPTK)
            else: notesB.configure(fg=FG_COLOR_P, bg=BG_PANEL, image=notesIconWPTK)
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
        def onClose():
            addB.config(state="normal")
            addScreen.destroy()
        global menuOpen
        addScreen = Toplevel(root)
        addScreen.resizable(False, False)
        addScreen.geometry(f"400x570")
        addScreen.iconbitmap('icon/pwm.ico')
        addScreen.configure(bg=BG_PANEL)
        addScreen.protocol("WM_DELETE_WINDOW", onClose)
        centerWindow(root, addScreen, 400, 570)
        addB.config(state="disabled")

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
                def isAuthValid(secret: str) -> bool:
                    try:
                        pyotp.TOTP(secret).now()
                        return True
                    except Exception:
                        return False
                passwordList = []
                website = wnE.get()
                websiteLink = f"www.{website.lower()}{selected.get()}"
                username = uE.get()
                password = pE.get()
                auth = authE.get()

                if isAuthValid(auth):
                    account = cryption.encrypt_line(vaultKey, f"{website},{websiteLink},{username},{password},{auth}")
                else:
                    account = cryption.encrypt_line(vaultKey, f"{website},{websiteLink},{username},{password}")
                     

                with open(f"files/{user}/passwords.txt", 'a') as f: f.write(account+'\n')
                with open(f"files/{user}/passwords.txt", 'r') as f: data = f.readlines()
                for i in data: passwordList.append(cryption.decrypt_line(vaultKey, i))
                addScreen.destroy()
                addB.config(state="normal")
                apps.passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)

            Label(addScreen, text="Add Password", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(x=60, y=5)

            wnE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            wnE.place(x=10, y=70, height=50, width=260)
            wnE.insert(0, phN)
            wnE.bind("<FocusIn>", on_focus_in)
            wnE.bind("<FocusOut>", on_focus_out)

            tldB =  OptionMenu(addScreen, selected, *tld)
            tldB.config(font=('arial', 26), fg=FG_COLOR_P, bg=BG_BUTTON, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            tldB["menu"].config(font=('arial', 18), bg=BG_BUTTON_ALT, fg=FG_COLOR_S)
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

            def onFocusIn(event):
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
            def onFocusOut(event):
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
            def formatExpiry(event):
                entry = event.widget
                value = entry.get()

                digits = "".join([c for c in value if c.isdigit()])

                digits = digits[:4]

                formatted = ""
                if len(digits) >= 2:
                    formatted = digits[:2] + "/" + digits[2:]
                else:
                    formatted = digits

                if expdE.get() != formatted:
                    expdE.delete(0, END)
                    expdE.insert(0, formatted)
            def formatCard(event):
                entry = event.widget
                old = entry.get()
                cursor_before = entry.index(INSERT)

                digits = ''.join(ch for ch in old if ch.isdigit())
                digits = digits[:16]

                new = " ".join(digits[i:i+4] for i in range(0, len(digits), 4))

                if old == new:
                    return

                digits_before_cursor = len(''.join(ch for ch in old[:cursor_before] if ch.isdigit()))

                new_cursor_pos = digits_before_cursor
                new_cursor_pos += digits_before_cursor // 4

                entry.delete(0, END)
                entry.insert(0, new)

                if new_cursor_pos <= len(new): entry.icursor(new_cursor_pos)
                else: entry.icursor(len(new))
            def formatCvc(event):
                entry = event.widget
                value = entry.get()

                digits = ''.join(ch for ch in value if ch.isdigit())

                digits = digits[:3]

                if entry.get() != digits:
                    entry.delete(0, END)
                    entry.insert(0, digits)
            def formatPin(event):
                entry = event.widget
                value = entry.get()

                digits = ''.join(ch for ch in value if ch.isdigit())

                digits = digits[:4]

                if entry.get() != digits:
                    entry.delete(0, END)
                    entry.insert(0, digits)

            def saveCard():
                cardDetails = cryption.encrypt_line(vaultKey, f"{bE.get()},www.{bE.get().lower()}{selected.get()},{nE.get()},{cE.get()},{expdE.get()},{cvcE.get()},{pinE.get()}")

                with open(f"files/{user}/cards.txt", 'a') as f: f.write(cardDetails+'\n')
                with open(f"files/{user}/cards.txt", 'r') as f: data = f.readlines()
                for i in data: cardList.append(cryption.decrypt_line(vaultKey, i))
                addScreen.destroy()
                addB.config(state="normal")
                apps.cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)

            Label(addScreen, text="Add Card", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(x=100, y=5)

            bE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            bE.place(x=10, y=70, height=50, width=260)
            bE.insert(0, phB)
            bE.bind("<FocusIn>", onFocusIn)
            bE.bind("<FocusOut>", onFocusOut)

            tldB =  OptionMenu(addScreen, selected, *tld)
            tldB.config(font=('arial', 26), fg=FG_COLOR_P, bg=BG_BUTTON, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            tldB["menu"].config(font=('arial', 18), bg=BG_BUTTON_ALT, fg=FG_COLOR_S)
            tldB.place(x=280, y=70, height=50, width=110)

            nE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            nE.place(x=10, y=135, height=50, width=380)
            nE.insert(0, phN)
            nE.bind("<FocusIn>", onFocusIn)
            nE.bind("<FocusOut>", onFocusOut)

            cE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            cE.place(x=10, y=220, height=50, width=380)
            cE.insert(0, phC)
            cE.bind("<FocusIn>", onFocusIn)
            cE.bind("<FocusOut>", onFocusOut)
            cE.bind("<KeyRelease>", formatCard)

            expdE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            expdE.place(x=10, y=285, height=50, width=380)
            expdE.insert(0, phExpd)
            expdE.bind("<FocusIn>", onFocusIn)
            expdE.bind("<FocusOut>", onFocusOut)
            expdE.bind("<KeyRelease>", formatExpiry)

            cvcE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            cvcE.place(x=10, y=365, height=50, width=380)
            cvcE.insert(0, phCvc)
            cvcE.bind("<FocusIn>", onFocusIn)
            cvcE.bind("<FocusOut>", onFocusOut)
            cvcE.bind("<KeyRelease>", formatCvc)

            pinE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            pinE.place(x=10, y=430, height=50, width=380)
            pinE.insert(0, phPin)
            pinE.bind("<FocusIn>", onFocusIn)
            pinE.bind("<FocusOut>", onFocusOut)
            pinE.bind("<KeyRelease>", formatPin)

            saveB = Button(addScreen, text="Save Card", font=('arial', 30), command=saveCard, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=1, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            saveB.place(x=10, y=510, height=50, width=380)
        if menuOpen == "note":
            addScreen.title("Add New Note File")
            Label(addScreen, text="Add Note File", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(x=70, y=5)

            notesNamePH = "Notes Name"
            notesDescPH = "Notes Description"

            def onFocusIn(event):
                widget = event.widget

                if widget == notesNameE:
                    if widget.get() == notesNamePH:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left")
                elif widget == notesDescE:
                    if widget.get() == notesDescPH:
                        widget.delete(0, END)
                        widget.config(fg=FG_COLOR_P, justify="left") 
            def onFocusOut(event):
                widget = event.widget

                if widget == notesNameE:
                    if widget.get() == "":
                        widget.insert(0, notesNamePH)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == notesDescE:
                    if widget.get() == "":
                        widget.insert(0, notesDescPH)
                        widget.config(fg=FG_COLOR_S, justify="center")
            def createNewFile():
                notesName = notesNameE.get()
                notesDesc = notesDescE.get()
                if notesName != notesNamePH:
                    if notesDesc != notesDescPH:
                        with open(f"files/{user}/notes/{notesName}-{notesDesc}.txt", 'w') as f: f.close()

                addScreen.destroy()
                addB.config(state="normal")
                apps.notes(inner_frame, contFrame, canvas, dataFrame, user, root, vaultKey)

            notesNameE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            notesNameE.place(x=10, y=70, height=50, width=380)
            notesNameE.insert(0, notesNamePH)
            notesNameE.bind("<FocusIn>", onFocusIn)
            notesNameE.bind("<FocusOut>", onFocusOut)

            notesDescE = Entry(addScreen, font=('arial', 28), fg=FG_COLOR_S, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            notesDescE.place(x=10, y=135, height=50, width=380)
            notesDescE.insert(0, notesDescPH)
            notesDescE.bind("<FocusIn>", onFocusIn)
            notesDescE.bind("<FocusOut>", onFocusOut)

            saveB = Button(addScreen, text="Create New File", font=('arial', 30), command=createNewFile, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=1, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
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
    contFrame.grid_rowconfigure(0, weight=0)
    contFrame.grid_rowconfigure(1, weight=0)

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

    clipboard_status = StringVar(value="")
    statusL = Label(contFrame, textvariable=clipboard_status, font=('arial', 12), bg=BG_PANEL, fg=FG_COLOR_S, anchor='w')
    statusL.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

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

    notesIconWP = Image.open("icon/buttonImg/notes_WP.png").resize((52,52), Image.Resampling.LANCZOS)
    notesIconWPTK = ImageTk.PhotoImage(notesIconWP)
    notesIconWS = Image.open("icon/buttonImg/notes_WS.png").resize((52,52), Image.Resampling.LANCZOS)
    notesIconWSTK = ImageTk.PhotoImage(notesIconWS)

    notesIconBP = Image.open("icon/buttonImg/notes_BP.png").resize((52,52), Image.Resampling.LANCZOS)
    notesIconBPTK = ImageTk.PhotoImage(notesIconBP)
    notesIconBS = Image.open("icon/buttonImg/notes_BS.png").resize((52,52), Image.Resampling.LANCZOS)
    notesIconBSTK = ImageTk.PhotoImage(notesIconBS)

    notesB = Label(menuFrame, text=" Notes", image=notesIconWPTK, compound='left', font=('arial', 32), anchor="w", bg=BG_PANEL, fg=FG_COLOR_P)
    notesB.place(relx=0.05, y=260, relwidth=0.9, height=60)
    notesB.image = notesIconWPTK
    notesB.image = notesIconWSTK
    notesB.image = notesIconBPTK
    notesB.image = notesIconBSTK
    notesB.bind("<Enter>", onHoverEnter)
    notesB.bind("<Leave>", onHoverLeave)
    notesB.bind("<Button-1>", onClick)

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

    apps.init_clipboard_controls(root, clipboard_status)

    if menuOpen == "pasw":
        apps.passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        loginsB.config(fg=ACCENT_BLUE, image=loginsIconBPTK)
    elif menuOpen == "card":
        apps.cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchE.get(), vaultKey)
        cardsB.config(fg=ACCENT_BLUE, image=cardsIconBPTK)
    elif menuOpen == "note":
        apps.notes(inner_frame, contFrame, canvas, dataFrame, user, root, vaultKey)
        notesB.config(fg=ACCENT_BLUE, image=notesIconBPTK)
    elif menuOpen == "sett":
        cardsB.config(fg=FG_COLOR_P, image=cardsIconWPTK)
        loginsB.config(fg=FG_COLOR_P, image=loginsIconWPTK)
        notesB.config(fg=FG_COLOR_P, image=notesIconWPTK)
        apps.settings(inner_frame, contFrame, canvas, dataFrame, user, vaultKey)
        
loginScreen()
root.mainloop()