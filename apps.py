from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
from pathlib import Path

from pandas import DataFrame
import cryption
import qrcode
import shutil
import base64
import pyotp
import time
import json
import os

from theme import loadTheme
import webbrowser
import pyperclip

def get_favicon(url, user):
    with open(f'files/{user}/config/settings.json', 'r') as f:
        data = json.load(f)
        favicon = data["settings"]["General Settings"]["favicons"]
    if favicon:
        cache_dir = f"icon/favicons"
        os.makedirs(cache_dir, exist_ok=True)
        
        clean_url = url.replace("www.", "").replace("http://", "").replace("https://", "").replace("/", "_").split("?")[0]
        if clean_url.endswith("_"): clean_url = clean_url[:-1]
        cache_path = f"{cache_dir}/{clean_url}.png"
        
        if os.path.exists(cache_path): return cache_path
        
        try:
            if not url.startswith("http"): url = "https://" + url
            
            favicon_url = f"https://www.google.com/s2/favicons?domain={url}&sz=128"     
            with urllib.request.urlopen(favicon_url, timeout=5) as response: image_data = response.read()
                
            image = Image.open(BytesIO(image_data))
            if image.size[0] < 128 or image.size[1] < 128:
                image = image.resize((128, 128), Image.Resampling.LANCZOS)
            image.save(cache_path, "PNG", quality=95, optimize=True)
            
            return cache_path
        
        except Exception as e:
            return "icon/favicons/worldwide.png"
    else: return "icon/favicons/worldwide.png"
def _clear_content(inner_frame: Frame, contFrame: Frame, dataFrame: Frame) -> None:
    for widget in inner_frame.winfo_children():
        if widget is not contFrame:
            widget.destroy()
    for widget in dataFrame.winfo_children():
        widget.destroy()

def passwords(passwordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey):
    _clear_content(inner_frame, contFrame, dataFrame)
    if searchParam == "Search...": searchParam = ""
    yPos = 10

    with open(f'files/{user}/config/settings.json', 'r') as f:
        data = json.load(f)
        currentTheme = loadTheme(data["settings"]["General Settings"]["theme"])

    BG_PANEL = currentTheme["BG_PANEL"]
    BG_LIST = currentTheme["BG_LIST"]
    BG_CARD = currentTheme["BG_CARD"]

    BG_INPUT = currentTheme["BG_INPUT"]
    BG_BUTTON = currentTheme["BG_BUTTON"]
    BG_BUTTON_ALT = currentTheme["BG_BUTTON_ALT"]

    FG_COLOR_P = currentTheme["FG_PRIMARY"]
    FG_COLOR_S = currentTheme["FG_SECONDARY"]
    FG_HIGHLIGHT = currentTheme["FG_MUTED"]
    ACCENT_BLUE = currentTheme["ACCENT_BLUE"]
    ACCENT_BLUE_GLOW = currentTheme["ACCENT_BLUE_GLOW"]

    showIconP = Image.open("icon/buttonImg/eyeP.png").resize((30, 30), Image.Resampling.LANCZOS)
    showIconPTK = ImageTk.PhotoImage(showIconP)
    showIconS = Image.open("icon/buttonImg/eyeS.png").resize((30, 30), Image.Resampling.LANCZOS)
    showIconSTK = ImageTk.PhotoImage(showIconS)

    hideIconP = Image.open("icon/buttonImg/hiddenP.png").resize((30, 30), Image.Resampling.LANCZOS)
    hideIconPTK = ImageTk.PhotoImage(hideIconP)
    hideIconS = Image.open("icon/buttonImg/hiddenS.png").resize((30, 30), Image.Resampling.LANCZOS)
    hideIconSTK = ImageTk.PhotoImage(hideIconS)

    editIconP = Image.open("icon/buttonImg/editP.png").resize((58, 58), Image.Resampling.LANCZOS)
    editIconPTK = ImageTk.PhotoImage(editIconP)
    editIconS = Image.open("icon/buttonImg/editS.png").resize((58, 58), Image.Resampling.LANCZOS)
    editIconSTK = ImageTk.PhotoImage(editIconS)

    deleteIconP = Image.open("icon/buttonImg/binP.png").resize((58, 58), Image.Resampling.LANCZOS)
    deleteIconPTK = ImageTk.PhotoImage(deleteIconP)
    deleteIconS = Image.open("icon/buttonImg/binS.png").resize((58, 58), Image.Resampling.LANCZOS)
    deleteIconSTK = ImageTk.PhotoImage(deleteIconS)

    def displayPassword(parts, lineStr, event):
        for widget in dataFrame.winfo_children():
            widget.destroy()
        favicon_path = get_favicon(parts[1], user)
        with open(f'files/{user}/config/settings.json', 'r') as f: data = json.load(f)
        showVar = [data["settings"]["General Settings"]["passwordsShownByDefault"]]

        def confirmPin(option, code):
            pinConfirmScreen = Toplevel(root)
            pinConfirmScreen.title("Confirm Pin")
            pinConfirmScreen.resizable(False, False)
            pinConfirmScreen.geometry("300x150")
            pinConfirmScreen.config(bg=BG_PANEL)

            def confirm(*_):
                value = pinVar.get()
                if len(value) > 4:
                    pinVar.set(value[:4])
                if len(value) == 4:
                    if pinE.get() == code:
                        if option == "show": showPassword()
                        if option == 'edit': editPassword()
                        if option == "delete": deletePassword()
                        pinConfirmScreen.destroy()

            Label(pinConfirmScreen, text="Enter Pin", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(relx=0.5, y=25, anchor='center')
            pinVar = StringVar()
            pinVar.trace_add('write', confirm)
            pinE = Entry(pinConfirmScreen, textvariable=pinVar, font=('arial', 30), bg=BG_INPUT, fg=FG_COLOR_P, justify='center', relief="flat", bd=0)
            pinE.place(x=10, y=85, height=50, width=280)
            pinE.focus_force()
        def controlButtons(option):
            with open(f'files/{user}/config/settings.json', 'r') as f:
                data = json.load(f)
                data = data["settings"]["Authentication"]

            if data["requirePin"]:
                confirmPin(option, data["pin"])
            else:
                if option == "show": showPassword()
                if option == 'edit': editPassword()
                if option == "delete": deletePassword()

        def showPassword():
            showVar[0] = not showVar[0]
            if showVar[0]:
                showB.config(image=hideIconPTK)
                passL.config(text=parts[3].strip('\n'))
            else:
                showB.config(image=showIconPTK)
                passL.config(text="●"*len(parts[3].strip('\n')))
        def editPassword():
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
                editB.config(state="normal")
                editScreen.destroy()
            editScreen = Toplevel(dataFrame)
            editScreen.resizable(False, False)
            editScreen.geometry("400x570")
            editScreen.title("Edit Password")
            editScreen.iconbitmap('icon/pwm.ico')
            editScreen.configure(bg=BG_PANEL)
            editScreen.protocol("WM_DELETE_WINDOW", onClose)
            centerWindow(root, editScreen, 400, 570)
            editB.config(state="disabled")

            phN = "Website"
            phU = "Username"
            phP = "Password"
            phAuth = "Authentication Code"

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
                        widget.config(fg=FG_COLOR_P, justify="left", font=('arial', 20))        
            def on_focus_out(event):
                widget = event.widget

                if widget == wnE:
                    if widget.get() == "":
                        widget.insert(0, phN)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == uE:
                    if widget.get() == "":
                        widget.insert(0, phU)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == pE:
                    if widget.get() == "":
                        widget.insert(0, phP)
                        widget.config(fg=FG_COLOR_S, justify="center")
                elif widget == authE:
                    if widget.get() == "":
                        widget.insert(0, phAuth)
                        widget.config(fg=FG_COLOR_S, justify="center", font=('arial', 25))
        
            def saveUpdates():
                def isAuthValid(secret: str) -> bool:
                    try:
                        pyotp.TOTP(secret).now()
                        return True
                    except Exception:
                        return False
                site = wnE.get() if not getattr(wnE, "_is_placeholder", False) else ""
                username = uE.get() if not getattr(uE, "_is_placeholder", False) else ""
                password = pE.get() if not getattr(pE, "_is_placeholder", False) else ""
                auth = authE.get() if not getattr(authE, "_is_placeholder", False) else ""

                url = f"www.{site.lower()}{selected.get()}" if site else parts[1]

                if isAuthValid(auth): newPlainLine = f"{site},{url},{username},{password},{auth}"
                else: newPlainLine = f"{site},{url},{username},{password}"
                
                fullAccountList = []
                with open(f"files/{user}/passwords.txt", 'r') as f:
                    for enc in f.readlines():
                        dec = cryption.decrypt_line(vaultKey, enc.strip())
                        fullAccountList.append(dec)

                newPasswordList = []
                for record in fullAccountList:
                    if record == lineStr:
                        newPasswordList.append(newPlainLine)
                    else:
                        newPasswordList.append(record)

                with open(f"files/{user}/passwords.txt", 'w') as f:
                    for record in newPasswordList:
                        enc = cryption.encrypt_line(vaultKey, record)
                        f.write(enc + "\n")

                editScreen.destroy()
                passwords(newPasswordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey)

            Label(editScreen, text="Edit Password", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(x=60, y=5)

            wnE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="left")
            wnE.place(x=10, y=70, height=50, width=260)
            wnE.insert(0, parts[0])
            wnE.bind("<FocusIn>", on_focus_in)
            wnE.bind("<FocusOut>", on_focus_out)

            tldB =  OptionMenu(editScreen, selected, *tld)
            tldB.config(font=('arial', 26), fg=FG_COLOR_P, bg=BG_BUTTON, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            tldB["menu"].config(font=('arial', 18), bg=BG_BUTTON_ALT, fg=FG_COLOR_S)
            tldB.place(x=280, y=70, height=50, width=110)

            uE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="left")
            uE.place(x=10, y=135, height=50, width=380)
            uE.insert(0, parts[2])
            uE.bind("<FocusIn>", on_focus_in)
            uE.bind("<FocusOut>", on_focus_out)

            pE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="left")
            pE.place(x=10, y=200, height=50, width=380)
            pE.insert(0, parts[3].strip('\n'))
            pE.bind("<FocusIn>", on_focus_in)
            pE.bind("<FocusOut>", on_focus_out)

            Label(editScreen, text="Optional", font=('arial', 30), bg=BG_PANEL, fg=FG_COLOR_P).place(x=125, y=280)

            authE = Entry(editScreen, font=('arial', 20), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            authE.place(x=10, y=340, height=50, width=380)
            if len(parts) == 5: authE.insert(0, parts[4].strip('\n')); authE.config(fg=FG_COLOR_P)
            else :authE.insert(0, phAuth)
            authE.bind("<FocusIn>", on_focus_in)
            authE.bind("<FocusOut>", on_focus_out)

            saveB = Button(editScreen, text="Save Account", font=('arial', 30), command=saveUpdates, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=1)
            saveB.place(x=10, y=510, height=50, width=380)
        def deletePassword():
            newPasswordList = []

            with open(f"files/{user}/passwords.txt", "r") as f:
                encryptedLines = f.readlines()

            decryptedList = []
            for enc in encryptedLines:
                enc = enc.strip()
                dec = cryption.decrypt_line(vaultKey, enc)

                if dec == lineStr: continue
                decryptedList.append(dec)

            with open(f"files/{user}/passwords.txt", "w") as f:
                for record in decryptedList:
                    f.write(cryption.encrypt_line(vaultKey, record) + "\n")

            for record in passwordList:
                if record == lineStr: continue
                newPasswordList.append(record)

            passwords(newPasswordList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey)

        def onClick(event):
            widget = event.widget
            if len(parts) == 5:
                totp = pyotp.TOTP(parts[4].strip('\n'), interval=30)
                if widget == authL: pyperclip.copy(totp.now())

            if widget == linkL: webbrowser.open(parts[1])
            if widget == userL: pyperclip.copy(parts[2])
            if widget == passL: pyperclip.copy(parts[3].strip('\n'))    
        def onHoverEnter(event):
            widget = event.widget

            if widget == linkL: linkL.configure(fg=ACCENT_BLUE_GLOW)
            if widget == userL: userL.configure(fg=FG_HIGHLIGHT)
            if widget == passL: passL.configure(fg=FG_HIGHLIGHT)
            if widget == editB: editB.configure(image=editIconSTK)
            if widget == deleteB: deleteB.configure(image=deleteIconSTK)
            if widget == showB:
                if showVar[0]:showB.configure(image=hideIconSTK)
                else: showB.configure(image=showIconSTK)
        def onHoverLeave(event):
            widget = event.widget

            if widget == linkL: linkL.configure(fg=ACCENT_BLUE)
            if widget == userL: userL.configure(fg=FG_COLOR_S)
            if widget == passL: passL.configure(fg=FG_COLOR_S)
            if widget == editB: editB.configure(image=editIconPTK)
            if widget == deleteB: deleteB.configure(image=deleteIconPTK)
            if widget == showB:
                if showVar[0]: showB.configure(image=hideIconPTK)
                else: showB.configure(image=showIconPTK)

        try:
            favicon_image = Image.open(favicon_path).resize((96, 96), Image.Resampling.LANCZOS)
            favicon_photo = ImageTk.PhotoImage(favicon_image)

            icon_label = Label(dataFrame, image=favicon_photo, bg=BG_CARD)
            icon_label.image = favicon_photo
            icon_label.place(relx=0.02, rely=0.02, width=100, height=100)
        except: pass

        Label(dataFrame, text=parts[0], font=('arial', 32, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.25, rely=0.03)
        linkL = Label(dataFrame, text=parts[1], font=('arial', 24, 'underline'), bg=BG_CARD, fg=ACCENT_BLUE)
        linkL.place(relx=0.25, rely=0.11)
        linkL.bind("<Button-1>", onClick)
        linkL.bind("<Enter>", onHoverEnter)
        linkL.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="Username", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.02, rely=0.2)
        userL = Label(dataFrame, text=parts[2], font=('arial', 22), bg=BG_CARD, fg=FG_COLOR_S)
        userL.place(relx=0.02, rely=0.29)
        userL.bind("<Button-1>", onClick)
        userL.bind("<Enter>", onHoverEnter)
        userL.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="Password", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.02, rely=0.37)
        passL = Label(dataFrame, font=('arial', 22), bg=BG_CARD, fg=FG_COLOR_S)
        passL.place(relx=0.02, rely=0.45)
        passL.bind("<Button-1>", onClick)
        passL.bind("<Enter>", onHoverEnter)
        passL.bind("<Leave>", onHoverLeave)

        if len(parts) == 5:
            def start_totp_label(label):
                totp = pyotp.TOTP(parts[4].strip('\n'), interval=30)

                current_code = None
                cycle_start = None
                base_color = "#00ff00"
                is_hovered = False

                def darkenHex(color, factor=0.8):
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)

                    r = int(r * factor)
                    g = int(g * factor)
                    b = int(b * factor)

                    return f"#{r:02x}{g:02x}{b:02x}"

                def updateCode():
                    nonlocal current_code, cycle_start
                    current_code = totp.now()
                    cycle_start = time.time()
                    label.config(text=current_code)
                    updateColor()
                def updateColor():
                    nonlocal base_color
                    elapsed = time.time() - cycle_start
                    remaining = 30 - elapsed

                    if remaining <= 0:
                        updateCode()
                        return

                    ratio = remaining / 30

                    r = int((1 - ratio) * 255)
                    g = int(ratio * 255)
                    base_color = f"#{r:02x}{g:02x}00"

                    color = darkenHex(base_color) if is_hovered else base_color
                    label.config(fg=color)

                    label.after(100, updateColor)

                def onEnter(event):
                    nonlocal is_hovered
                    is_hovered = True
                    label.config(fg=darkenHex(base_color))
                def onLeave(event):
                    nonlocal is_hovered
                    is_hovered = False
                    label.config(fg=base_color)

                label.bind("<Enter>", onEnter)
                label.bind("<Leave>", onLeave)

                updateCode()

            Label(dataFrame, text="Auth Code", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.02, rely=0.55)
            authL = Label(dataFrame, font=('arial', 22), bg=BG_CARD)
            authL.place(relx=0.02, rely=0.64)
            authL.bind("<Button-1>", onClick)

            start_totp_label(authL)

        showB = Button(dataFrame, command=lambda:controlButtons("show"), relief="flat", bd=0, bg=BG_CARD, activebackground=BG_CARD)
        showB.place(relx=0.9, rely=0.46, width=32, height=32)
        showB.bind("<Enter>", onHoverEnter)
        showB.bind("<Leave>", onHoverLeave)

        editB = Button(dataFrame, image=editIconPTK, command=lambda:controlButtons("edit"), relief="flat", bd=0, bg=BG_CARD, activebackground=BG_CARD)
        editB.place(relx=0.85, rely=0.02, height=64, width=64)
        editB.bind("<Enter>", onHoverEnter)
        editB.bind("<Leave>", onHoverLeave)

        deleteB = Button(dataFrame, image=deleteIconPTK, command=lambda:controlButtons("delete"), relief="flat", bd=0, bg=BG_CARD, activebackground=BG_CARD)
        deleteB.place(relx=0.85, rely=0.9, height=64, width=64)
        deleteB.bind("<Enter>", onHoverEnter)
        deleteB.bind("<Leave>", onHoverLeave)

        if showVar[0]:
            passL.config(text=parts[3])
            showB.config(image=hideIconPTK)
        else:
            passL.config(text="●"*len(parts[3].strip('\n')))
            showB.config(image=showIconPTK)

        Label(dataFrame, text="Hint: Click to Copy", font=('arial', 15), bg=BG_CARD, fg="#424242").place(relx=0.35, rely=0.95)
    def move_password(lineStr, direction):
        with open(f"files/{user}/passwords.txt", "r") as f:
            encryptedLines = f.readlines()

        plainList = []
        for enc in encryptedLines:
            enc = enc.strip()
            plainList.append(cryption.decrypt_line(vaultKey, enc))

        try: idx = plainList.index(lineStr)
        except ValueError: return

        target_idx = idx - 1 if direction == "up" else idx + 1
        if target_idx < 0 or target_idx >= len(plainList):
            return

        plainList[idx], plainList[target_idx] = plainList[target_idx], plainList[idx]

        with open(f"files/{user}/passwords.txt", "w") as f:
            for record in plainList:
                encrypted = cryption.encrypt_line(vaultKey, record)
                f.write(encrypted + "\n")

        passwords(plainList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey)


    filtered_passwords = []
    passwordListLower = [p.lower() for p in passwordList]

    if not searchParam:
        filtered_passwords = list(enumerate(passwordList))
    else:
        search_lower = searchParam.lower()
        for idx, lower_line in enumerate(passwordListLower):
            if search_lower in lower_line:
                filtered_passwords.append((idx, passwordList[idx]))

    for idx, line in filtered_passwords:
        parts = line.strip("\n").split(",")
        if len(parts) < 4:
            continue

        accFrame = Frame(inner_frame, bg=BG_CARD, bd=0, highlightthickness=0)
        accFrame.place(x=10, y=yPos, relwidth=0.95, height=80)
        accFrame.bind("<Button-1>", lambda e, p=parts, ln=line: displayPassword(p, ln, e))
        accFrame.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        favicon_path = get_favicon(parts[1], user)
        if favicon_path and os.path.exists(favicon_path):
            try:
                favicon_image = Image.open(favicon_path)
                favicon_image = favicon_image.resize((64, 64), Image.Resampling.LANCZOS)
                favicon_photo = ImageTk.PhotoImage(favicon_image)
                icon_label = Label(accFrame, image=favicon_photo, bg=BG_CARD, bd=0)
                icon_label.image = favicon_photo
                icon_label.place(x=8, y=8, width=64, height=64)
                icon_label.bind("<Button-1>", lambda e, p=parts, ln=line: displayPassword(p, ln, e))
                icon_label.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
            except Exception as e:
                pass

        siteL = Label(accFrame, text=parts[0], font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
        siteL.place(x=80, y=2)
        siteL.bind("<Button-1>", lambda e, p=parts, ln=line: displayPassword(p, ln, e))
        siteL.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        userL = Label(accFrame, text=parts[2], font=("arial", 14), bg=BG_CARD, fg=FG_COLOR_S)
        userL.place(x=80, y=46)
        userL.bind("<Button-1>", lambda e, p=parts, ln=line: displayPassword(p, ln, e))
        userL.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        move_up_disabled = idx == 0
        move_down_disabled = idx == len(passwordList) - 1

        upB = Button(accFrame, text="↑", font=('arial', 16, 'bold'), command=lambda ln=line: move_password(ln, "up"), bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", bd=0, state="disabled" if move_up_disabled else "normal", activebackground=BG_BUTTON)
        upB.place(relx=0.92, y=8, width=32, height=28)
        upB.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        downB = Button(accFrame, text="↓", font=('arial', 16, 'bold'), command=lambda ln=line: move_password(ln, "down"), bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", bd=0, state="disabled" if move_down_disabled else "normal", activebackground=BG_BUTTON)
        downB.place(relx=0.92, y=44, width=32, height=28)
        downB.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        yPos += 100

    inner_frame.update_idletasks()
    total_height = yPos + 10
    inner_frame.config(height=total_height, width=canvas.winfo_width())
    canvas.update_idletasks()
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), total_height))
def cards(cardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey):
    _clear_content(inner_frame, contFrame, dataFrame)
    if searchParam == "Search...": searchParam = ""      
    yPos = 10

    with open(f'files/{user}/config/settings.json', 'r') as f:
        data = json.load(f)
        currentTheme = loadTheme(data["settings"]["General Settings"]["theme"])

    BG_PANEL = currentTheme["BG_PANEL"]
    BG_LIST = currentTheme["BG_LIST"]
    BG_CARD = currentTheme["BG_CARD"]

    BG_INPUT = currentTheme["BG_INPUT"]
    BG_BUTTON = currentTheme["BG_BUTTON"]
    BG_BUTTON_ALT = currentTheme["BG_BUTTON_ALT"]

    FG_COLOR_P = currentTheme["FG_PRIMARY"]
    FG_COLOR_S = currentTheme["FG_SECONDARY"]
    FG_HIGHLIGHT = currentTheme["FG_MUTED"]
    ACCENT_BLUE = currentTheme["ACCENT_BLUE"]
    ACCENT_BLUE_GLOW = currentTheme["ACCENT_BLUE_GLOW"]

    showIconP = Image.open("icon/buttonImg/eyeP.png").resize((30, 30), Image.Resampling.LANCZOS)
    showIconPTK = ImageTk.PhotoImage(showIconP)
    showIconS = Image.open("icon/buttonImg/eyeS.png").resize((30, 30), Image.Resampling.LANCZOS)
    showIconSTK = ImageTk.PhotoImage(showIconS)

    hideIconP = Image.open("icon/buttonImg/hiddenP.png").resize((30, 30), Image.Resampling.LANCZOS)
    hideIconPTK = ImageTk.PhotoImage(hideIconP)
    hideIconS = Image.open("icon/buttonImg/hiddenS.png").resize((30, 30), Image.Resampling.LANCZOS)
    hideIconSTK = ImageTk.PhotoImage(hideIconS)

    editIconP = Image.open("icon/buttonImg/editP.png").resize((58, 58), Image.Resampling.LANCZOS)
    editIconPTK = ImageTk.PhotoImage(editIconP)
    editIconS = Image.open("icon/buttonImg/editS.png").resize((58, 58), Image.Resampling.LANCZOS)
    editIconSTK = ImageTk.PhotoImage(editIconS)

    deleteIconP = Image.open("icon/buttonImg/binP.png").resize((58, 58), Image.Resampling.LANCZOS)
    deleteIconPTK = ImageTk.PhotoImage(deleteIconP)
    deleteIconS = Image.open("icon/buttonImg/binS.png").resize((58, 58), Image.Resampling.LANCZOS)
    deleteIconSTK = ImageTk.PhotoImage(deleteIconS)

    def displayCard(parts, lineStr, event=None):
        for widget in dataFrame.winfo_children(): widget.destroy()
        favicon_path = get_favicon(parts[1], user)
        with open(f'files/{user}/config/settings.json', 'r') as f: data = json.load(f)
        showVar = [data["settings"]["General Settings"]["passwordsShownByDefault"]]

        def confirmPin(option, code):
            pinConfirmScreen = Toplevel(root)
            pinConfirmScreen.title("Confirm Pin")
            pinConfirmScreen.resizable(False, False)
            pinConfirmScreen.geometry("300x150")
            pinConfirmScreen.config(bg=BG_PANEL)

            def confirm(*_):
                value = pinVar.get()
                if len(value) > 4:
                    pinVar.set(value[:4])
                if len(value) == 4:
                    if pinE.get() == code:
                        if option == "show": showCard()
                        if option == 'edit': editCard()
                        if option == "delete": deleteCard()
                        pinConfirmScreen.destroy()

            Label(pinConfirmScreen, text="Enter Pin", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(relx=0.5, y=25, anchor='center')
            pinVar = StringVar()
            pinVar.trace_add('write', confirm)
            pinE = Entry(pinConfirmScreen, textvariable=pinVar, font=('arial', 30), bg=BG_INPUT, fg=FG_COLOR_P, justify='center', relief="flat", bd=0)
            pinE.place(x=10, y=85, height=50, width=280)
            pinE.focus_force()
        def controlButtons(option):
            with open(f'files/{user}/config/settings.json', 'r') as f:
                data = json.load(f)
                data = data["settings"]["Authentication"]

            if data["requirePin"]:
                confirmPin(option, data["pin"])
            else:
                if option == "show": showCard()
                if option == 'edit': editCard()
                if option == "delete": deleteCard()

        def showCard():
            def formatCard(number, mode="n"):
                digits = "".join(c for c in number if c.isdigit())

                if mode == "m": 
                    if len(digits) >= 8:
                        masked_digits = digits[:-8] + "●" * 8
                    else:
                        masked_digits = "●" * len(digits)
                    final = masked_digits
                else: final = digits

                spaced = " ".join(final[i:i+4] for i in range(0, len(final), 4))
                return spaced
            showVar[0] = not showVar[0]

            if not showVar[0]:
                cardNumber = formatCard(parts[3])
                showB.config(image=hideIconPTK)
                cardNoL.config(text=cardNumber)
                cvcL.config(text=parts[5])
                pinL.config(text=parts[6])
            else:
                cardNumber = formatCard(parts[3], mode="m")
                showB.config(image=showIconPTK)
                cardNoL.config(text=cardNumber)
                cvcL.config(text="●"*len(parts[5]))
                pinL.config(text="●"*len(parts[6].strip('\n')))
        def editCard():
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
                editB.config(state="normal")
                editScreen.destroy()
            editScreen = Toplevel(dataFrame)
            editScreen.resizable(False, False)
            editScreen.geometry("400x570")
            editScreen.title("Edit Card")
            editScreen.iconbitmap('icon/pwm.ico')
            editScreen.configure(bg=BG_PANEL)
            editScreen.protocol("WM_DELETE_WINDOW", onClose)
            centerWindow(root, editScreen, 400, 570)
            editB.config(state="disabled")

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
                        widget.config(fg="black", justify="left")
                elif widget == nE:
                    if widget.get() == phN:
                        widget.delete(0, END)
                        widget.config(fg="black", justify="left")
                elif widget == cE:
                    if widget.get() == phC:
                        widget.delete(0, END)
                        widget.config(fg="black", justify="left")
                elif widget == expdE:
                    if widget.get() == phExpd:
                        widget.delete(0, END)
                        widget.config(fg="black", justify="center")
                elif widget == cvcE:
                    if widget.get() == phCvc:
                        widget.delete(0, END)
                        widget.config(fg="black", justify="center")
                elif widget == pinE:
                    if widget.get() == phPin:
                        widget.delete(0, END)
                        widget.config(fg="black", justify="center")        
            def on_focus_out(event):
                widget = event.widget

                if widget == bE:
                    if widget.get() == "":
                        widget.insert(0, phB)
                        widget.config(fg="grey", justify="center")
                elif widget == nE:
                    if widget.get() == "":
                        widget.insert(0, phN)
                        widget.config(fg="grey", justify="center")
                elif widget == cE:
                    if widget.get() == "":
                        widget.insert(0, phC)
                        widget.config(fg="grey", justify="center")
                elif widget == expdE:
                    if widget.get() == "":
                        widget.insert(0, phExpd)
                        widget.config(fg="grey", justify="center")
                elif widget == cvcE:
                    if widget.get() == "":
                        widget.insert(0, phCvc)
                        widget.config(fg="grey", justify="center")
                elif widget == pinE:
                    if widget.get() == "":
                        widget.insert(0, phPin)
                        widget.config(fg="grey", justify="center")
            
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

            def saveUpdates():
                bank = bE.get() if not getattr(bE, "_is_placeholder", False) else ""
                name = nE.get() if not getattr(nE, "_is_placeholder", False) else ""
                card_no = cE.get() if not getattr(cE, "_is_placeholder", False) else ""
                exp = expdE.get() if not getattr(expdE, "_is_placeholder", False) else ""
                cvc = cvcE.get() if not getattr(cvcE, "_is_placeholder", False) else ""
                pin = pinE.get() if not getattr(pinE, "_is_placeholder", False) else ""

                url = f"www.{bank.lower()}{selected.get()}" if bank else parts[1]
                newPlainLine = f"{bank},{url},{name},{card_no},{exp},{cvc},{pin}"

                with open(f"files/{user}/cards.txt", "r") as f:
                    encryptedLines = f.readlines()

                decryptedList = []
                for enc in encryptedLines:
                    enc = enc.strip()
                    decryptedList.append(cryption.decrypt_line(vaultKey, enc))

                updatedCardList = []
                for record in decryptedList:
                    if record == lineStr: updatedCardList.append(newPlainLine)
                    else: updatedCardList.append(record)

                with open(f"files/{user}/cards.txt", "w") as f:
                    for record in updatedCardList:
                        f.write(cryption.encrypt_line(vaultKey, record) + "\n")

                newCardList = []
                for record in cardList:
                    if record == lineStr: newCardList.append(newPlainLine)
                    else: newCardList.append(record)

                editScreen.destroy()
                cards(newCardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey)

            Label(editScreen, text="Edit Card", font=('arial', 32), bg=BG_PANEL, fg=FG_COLOR_P).place(x=100, y=5)

            bE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="left")
            bE.place(x=10, y=70, height=50, width=260)
            bE.insert(0, parts[0])
            bE.bind("<FocusIn>", on_focus_in)
            bE.bind("<FocusOut>", on_focus_out)

            tldB =  OptionMenu(editScreen, selected, *tld)
            tldB.config(font=('arial', 26), fg=FG_COLOR_P, bg=BG_BUTTON, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            tldB["menu"].config(font=('arial', 18), bg=BG_BUTTON_ALT, fg=FG_COLOR_S)
            tldB.place(x=280, y=70, height=50, width=110)

            nE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="left")
            nE.place(x=10, y=135, height=50, width=380)
            nE.insert(0, parts[2])
            nE.bind("<FocusIn>", on_focus_in)
            nE.bind("<FocusOut>", on_focus_out)

            cE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="left")
            cE.place(x=10, y=220, height=50, width=380)
            cE.insert(0, parts[3])
            cE.bind("<FocusIn>", on_focus_in)
            cE.bind("<FocusOut>", on_focus_out)
            cE.bind("<KeyRelease>", formatCard)

            expdE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            expdE.place(x=10, y=285, height=50, width=380)
            expdE.insert(0, parts[4])
            expdE.bind("<FocusIn>", on_focus_in)
            expdE.bind("<FocusOut>", on_focus_out)
            expdE.bind("<KeyRelease>", formatExpiry)

            cvcE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            cvcE.place(x=10, y=365, height=50, width=380)
            cvcE.insert(0, parts[5])
            cvcE.bind("<FocusIn>", on_focus_in)
            cvcE.bind("<FocusOut>", on_focus_out)
            cvcE.bind("<KeyRelease>", formatCvc)

            pinE = Entry(editScreen, font=('arial', 28), fg=FG_COLOR_P, bg=BG_INPUT, relief="flat", borderwidth=0, justify="center")
            pinE.place(x=10, y=430, height=50, width=380)
            pinE.insert(0, parts[6].strip('\n'))
            pinE.bind("<FocusIn>", on_focus_in)
            pinE.bind("<FocusOut>", on_focus_out)
            pinE.bind("<KeyRelease>", formatPin)

            saveB = Button(editScreen, text="Save Card", font=('arial', 30), command=saveUpdates, bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", borderwidth=1)
            saveB.place(x=10, y=510, height=50, width=380)
        def deleteCard():
            with open(f"files/{user}/cards.txt", "r") as f:
                encryptedLines = f.readlines()

            decryptedList = []
            for enc in encryptedLines:
                enc = enc.strip()
                dec = cryption.decrypt_line(vaultKey, enc)

                if dec == lineStr: continue
                decryptedList.append(dec)

            with open(f"files/{user}/cards.txt", "w") as f:
                for record in decryptedList:
                    f.write(cryption.encrypt_line(vaultKey, record) + "\n")

            newCardList = []
            for record in cardList:
                if record == lineStr: continue
                newCardList.append(record)

            cards(newCardList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey)

        try:
            favicon_image = Image.open(favicon_path)
            favicon_image = favicon_image.resize((96, 96), Image.Resampling.LANCZOS)
            favicon_photo = ImageTk.PhotoImage(favicon_image)

            icon_label = Label(dataFrame, image=favicon_photo, bg=BG_CARD)
            icon_label.image = favicon_photo
            icon_label.place(relx=0.02, rely=0.02, width=100, height=100)
        except: pass

        def onClick(event):
            widget = event.widget

            if widget == linkL: webbrowser.open(parts[1])
            if widget == nameOnCardL: pyperclip.copy(parts[2])
            if widget == cardNoL: pyperclip.copy(parts[3])
            if widget == expDateL: pyperclip.copy(parts[4])
            if widget == cvcL: pyperclip.copy(parts[5])
            if widget == pinL: pyperclip.copy(parts[6])
        def onHoverEnter(event):
            widget = event.widget

            if widget == linkL: linkL.config(fg=ACCENT_BLUE_GLOW)
            if widget == nameOnCardL: nameOnCardL.config(fg=FG_HIGHLIGHT)
            if widget == cardNoL: cardNoL.config(fg=FG_HIGHLIGHT)
            if widget == expDateL: expDateL.config(fg=FG_HIGHLIGHT)
            if widget == cvcL: cvcL.config(fg=FG_HIGHLIGHT)
            if widget == pinL: pinL.config(fg=FG_HIGHLIGHT)
            if widget == editB: editB.configure(image=editIconSTK)
            if widget == deleteB: deleteB.configure(image=deleteIconSTK)
            if widget == showB:
                if showVar[0]:showB.configure(image=showIconSTK)
                else: showB.configure(image=hideIconSTK)
        def onHoverLeave(event):
            widget = event.widget

            if widget == linkL: linkL.config(fg=ACCENT_BLUE)
            if widget == nameOnCardL: nameOnCardL.config(fg=FG_COLOR_S)
            if widget == cardNoL: cardNoL.config(fg=FG_COLOR_S)
            if widget == expDateL: expDateL.config(fg=FG_COLOR_S)
            if widget == cvcL: cvcL.config(fg=FG_COLOR_S)
            if widget == pinL: pinL.config(fg=FG_COLOR_S)
            if widget == editB: editB.configure(image=editIconPTK)
            if widget == deleteB: deleteB.configure(image=deleteIconPTK)
            if widget == showB:
                if showVar[0]: showB.configure(image=showIconPTK)
                else: showB.configure(image=hideIconPTK)

        Label(dataFrame, text=parts[0], font=('arial', 32, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.25, rely=0.03)
        linkL = Label(dataFrame, text=parts[1], font=('arial', 24, 'underline'), bg=BG_CARD, fg=ACCENT_BLUE)
        linkL.place(relx=0.25, rely=0.1)
        linkL.bind("<Button-1>", onClick)
        linkL.bind("<Enter>", onHoverEnter)
        linkL.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="Name on Card", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.02, rely=0.2)
        nameOnCardL = Label(dataFrame, text=parts[2], font=('arial', 22), bg=BG_CARD, fg=FG_COLOR_S)
        nameOnCardL.place(relx=0.02, rely=0.28)
        nameOnCardL.bind("<Button-1>", onClick)
        nameOnCardL.bind("<Enter>", onHoverEnter)
        nameOnCardL.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="Card Number", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.02, rely=0.37)
        cardNoL = Label(dataFrame, text=" ".join(parts[3][i:i+4] for i in range(0, len(parts[3]), 4)), font=('arial', 22), bg=BG_CARD, fg=FG_COLOR_S)
        cardNoL.place(relx=0.02, rely=0.45)
        cardNoL.bind("<Button-1>", onClick)
        cardNoL.bind("<Enter>", onHoverEnter)
        cardNoL.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="MM/YY", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.02, rely=0.54)
        expDateL = Label(dataFrame, text=parts[4], font=('arial', 22), bg=BG_CARD, fg=FG_COLOR_S)
        expDateL.place(relx=0.02, rely=0.62)
        expDateL.bind("<Button-1>", onClick)
        expDateL.bind("<Enter>", onHoverEnter)
        expDateL.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="CVC", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.5, rely=0.54)
        cvcL = Label(dataFrame, text=parts[5], font=('arial', 22), bg=BG_CARD, fg=FG_COLOR_S)
        cvcL.place(relx=0.52, rely=0.62)
        cvcL.bind("<Button-1>", onClick)
        cvcL.bind("<Enter>", onHoverEnter)
        cvcL.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="Pin Code", font=('arial',35, 'bold'), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.02, rely=0.71)
        pinL = Label(dataFrame, text=parts[6], font=('arial', 22), bg=BG_CARD, fg=FG_COLOR_S)
        pinL.place(relx=0.02, rely=0.79)
        pinL.bind("<Button-1>", onClick)
        pinL.bind("<Enter>", onHoverEnter)
        pinL.bind("<Leave>", onHoverLeave)

        showB = Button(dataFrame, image=showIconPTK, command=lambda:controlButtons("show"), relief="flat", bd=0, bg=BG_CARD, activebackground=BG_CARD)
        showB.place(relx=0.9, rely=0.46, width=32, height=32)
        showB.bind("<Enter>", onHoverEnter)
        showB.bind("<Leave>", onHoverLeave)

        editB = Button(dataFrame, image=editIconPTK, command=lambda:controlButtons("edit"), relief="flat", bd=0, bg=BG_CARD, activebackground=BG_CARD)
        editB.place(relx=0.85, rely=0.02, height=64, width=64)
        editB.bind("<Enter>", onHoverEnter)
        editB.bind("<Leave>", onHoverLeave)

        deleteB = Button(dataFrame, image=deleteIconPTK, command=lambda:controlButtons("delete"), relief="flat", bd=0, bg=BG_CARD, activebackground=BG_CARD)
        deleteB.place(relx=0.85, rely=0.9, height=64, width=64)
        deleteB.bind("<Enter>", onHoverEnter)
        deleteB.bind("<Leave>", onHoverLeave)

        Label(dataFrame, text="Hint: Click to Copy", font=('arial', 15), bg=BG_CARD, fg=FG_HIGHLIGHT).place(relx=0.35, rely=0.95)
        showCard()
    def move_card(lineStr, direction):
        with open(f"files/{user}/cards.txt", "r") as f:
            encryptedLines = f.readlines()

        plainList = []
        for enc in encryptedLines:
            enc = enc.strip()
            plainList.append(cryption.decrypt_line(vaultKey, enc))

        try: idx = plainList.index(lineStr)
        except ValueError: return

        target_idx = idx - 1 if direction == "up" else idx + 1
        if target_idx < 0 or target_idx >= len(plainList):
            return

        plainList[idx], plainList[target_idx] = plainList[target_idx], plainList[idx]

        with open(f"files/{user}/cards.txt", "w") as f:
            for record in plainList:
                f.write(cryption.encrypt_line(vaultKey, record) + "\n")

        cards(plainList, inner_frame, contFrame, canvas, dataFrame, root, user, searchParam, vaultKey)

    filteredCards = []
    cardListLower = [c.lower() for c in cardList]

    if not searchParam:
        filteredCards = list(enumerate(cardList))
    else:
        search_lower = searchParam.lower()
        for idx, lower_line in enumerate(cardListLower):
            if search_lower in lower_line:
                filteredCards.append((idx, cardList[idx]))

    for idx, line in filteredCards:
        parts = line.strip("\n").split(",")
        if len(parts) < 7: continue

        accFrame = Frame(inner_frame, bg=BG_CARD, bd=0, highlightthickness=0)
        accFrame.place(x=10, y=yPos, relwidth=0.95, height=80)
        accFrame.bind("<Button-1>", lambda e, p=parts, ln=line: displayCard(p, ln, e))
        accFrame.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        favicon_path = get_favicon(parts[1], user)
        if favicon_path and os.path.exists(favicon_path):
            try:
                favicon_image = Image.open(favicon_path)
                favicon_image = favicon_image.resize((64, 64), Image.Resampling.LANCZOS)
                favicon_photo = ImageTk.PhotoImage(favicon_image)
                icon_label = Label(accFrame, image=favicon_photo, bg=BG_CARD, bd=0)
                icon_label.image = favicon_photo
                icon_label.place(x=8, y=8, width=64, height=64)
                icon_label.bind("<Button-1>", lambda e, p=parts, ln=line: displayCard(p, ln, e))
                icon_label.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
            except Exception as e:
                pass

        bankNameL = Label(accFrame, text=parts[0], font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
        bankNameL.place(x=80, y=2)
        bankNameL.bind("<Button-1>", lambda e, p=parts, ln=line: displayCard(p, ln, e))
        bankNameL.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        cardNameL = Label(accFrame, text=parts[2], font=('arial', 14), bg=BG_CARD, fg=FG_COLOR_S)
        cardNameL.place(x=80, y=46)
        cardNameL.bind("<Button-1>", lambda e, p=parts, ln=line: displayCard(p, ln, e))
        cardNameL.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        move_up_disabled = idx == 0
        move_down_disabled = idx == len(cardList) - 1

        upB = Button(accFrame, text="↑", font=('arial', 16, 'bold'), command=lambda ln=line: move_card(ln, "up"), bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", bd=0, state="disabled" if move_up_disabled else "normal", activebackground=BG_BUTTON)
        upB.place(relx=0.92, y=8, width=32, height=28)
        upB.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        downB = Button(accFrame, text="↓", font=('arial', 16, 'bold'), command=lambda ln=line: move_card(ln, "down"), bg=BG_BUTTON, fg=FG_COLOR_P, relief="flat", bd=0, state="disabled" if move_down_disabled else "normal", activebackground=BG_BUTTON)
        downB.place(relx=0.92, y=44, width=32, height=28)
        downB.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        yPos += 100

    inner_frame.update_idletasks()
    total_height = yPos + 10
    inner_frame.config(height=total_height, width=canvas.winfo_width())
    canvas.update_idletasks()
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), total_height))

def settings(inner_frame, contFrame, canvas, dataFrame, user, vaultKey):
    _clear_content(inner_frame, contFrame, dataFrame)
    yPos = 10

    with open(f'files/{user}/config/settings.json', 'r') as f:
        data = json.load(f)
        currentTheme = loadTheme(data["settings"]["General Settings"]["theme"])

    BG_PANEL = currentTheme["BG_PANEL"]
    BG_LIST = currentTheme["BG_LIST"]
    BG_CARD = currentTheme["BG_CARD"]

    BG_INPUT = currentTheme["BG_INPUT"]
    BG_BUTTON = currentTheme["BG_BUTTON"]
    BG_BUTTON_ALT = currentTheme["BG_BUTTON_ALT"]

    FG_COLOR_P = currentTheme["FG_PRIMARY"]
    FG_COLOR_S = currentTheme["FG_SECONDARY"]
    FG_HIGHLIGHT = currentTheme["FG_MUTED"]
    ACCENT_BLUE = currentTheme["ACCENT_BLUE"]
    ACCENT_BLUE_GLOW = currentTheme["ACCENT_BLUE_GLOW"]

    def displaySetting(settingOption, event=None):
        for widget in dataFrame.winfo_children(): widget.destroy()

        if settingOption == "General Settings":
            def place_right_of(left_widget, right_widget, rely, padding=20):
                left_widget.update_idletasks()
                x = left_widget.winfo_x() + left_widget.winfo_reqwidth() + padding
                right_widget.place(x=x, rely=rely, anchor='w')

            with open(f'files/{user}/config/settings.json', 'r') as f:
                settings = json.load(f)["settings"][settingOption]

            Label(dataFrame, text="General Settings", font=('arial', 32), bg=BG_CARD, fg=FG_COLOR_P ).place(relx=0.5, rely=0.05, anchor="center")


            def saveSetting(event):
                with open(f'files/{user}/config/settings.json', 'r') as f:
                    data = json.load(f)

                if event in defaultScreenOptions:
                    data["settings"][settingOption]["defaultScreen"] = defaultScreenOptions[event]

                if event in themeOptions:
                    data["settings"][settingOption]["theme"] = themeOptions[event]

                with open(f'files/{user}/config/settings.json', 'w') as f:
                    json.dump(data, f, indent=4)
            def onHoverEnter(event):
                if event.widget == faviconB: faviconB.config(fg=FG_COLOR_S, bg=BG_BUTTON_ALT)
                if event.widget == passwordB: passwordB.config(fg=FG_COLOR_S, bg=BG_BUTTON_ALT)
            def onHoverLeave(event):
                if event.widget == faviconB: faviconB.config(fg=FG_COLOR_P, bg=BG_CARD)
                if event.widget == passwordB: passwordB.config(fg=FG_COLOR_P, bg=BG_CARD)
            def onClick(event):
                widget = event.widget

                with open(f'files/{user}/config/settings.json', 'r') as f:
                    data = json.load(f)

                if widget == faviconB:
                    curr = data["settings"][settingOption]["favicons"]
                    data["settings"][settingOption]["favicons"] = not curr
                    faviconB.config(text="On" if not curr else "Off")
                if widget == passwordB:
                    curr = data["settings"][settingOption]["passwordsShownByDefault"]
                    data["settings"][settingOption]["passwordsShownByDefault"] = not curr
                    passwordB.config(text="Off" if not curr else "On")

                with open(f'files/{user}/config/settings.json', 'w') as f:
                    json.dump(data, f, indent=4)

            defaultScreenOptions = {
                "Logins": "pasw",
                "Cards": "card",
                "Notes": "note",
                "Settings": "sett"
            }
            valueDefaultScreen = {v: k for k, v in defaultScreenOptions.items()}
            defaultScreen = StringVar(value=valueDefaultScreen[settings["defaultScreen"]])

            lbl_defaultScreen = Label(dataFrame, text="Default Screen:", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            lbl_defaultScreen.place(relx=0.02, rely=0.15, anchor='w')

            defaultScreenOM = OptionMenu(dataFrame, defaultScreen, *defaultScreenOptions.keys(), command=saveSetting)
            defaultScreenOM.config(font=('arial', 30), fg=FG_COLOR_P, bg=BG_BUTTON, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            defaultScreenOM["menu"].config(font=('arial', 20), bg=BG_BUTTON_ALT, fg=FG_COLOR_S)
            place_right_of(lbl_defaultScreen, defaultScreenOM, 0.15)

            themeOptions = {
                "Blue": "blue", "Dark": "dark",
                "Purple": "purple", "Red": "red",
                "Green": "green", "Light": "light"
            }
            valueTheme = {v: k for k, v in themeOptions.items()}
            theme = StringVar(value=valueTheme[settings["theme"]])

            lbl_theme = Label(
                dataFrame, text="Color Theme:",
                font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P
            )
            lbl_theme.place(relx=0.02, rely=0.25, anchor='w')

            themeOM = OptionMenu(dataFrame, theme, *themeOptions.keys(), command=saveSetting)
            themeOM.config(font=('arial', 30), fg=FG_COLOR_P, bg=BG_BUTTON, relief="flat", borderwidth=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            themeOM["menu"].config(font=('arial', 20), bg=BG_BUTTON_ALT, fg=FG_COLOR_S)
            place_right_of(lbl_theme, themeOM, 0.25)

            Label(dataFrame, text="For themes to change you need to re-open the app", font=('arial', 12), bg=BG_CARD, fg=FG_COLOR_S).place(relx=0.02, rely=0.35, anchor='w')

            lbl_favicon = Label(dataFrame, text="Load Favicons:", font=("arial", 28), bg=BG_CARD, fg=FG_COLOR_P)
            lbl_favicon.place(relx=0.02, rely=0.42, anchor='w')

            faviconB = Label(dataFrame, text="On" if settings["favicons"] else "Off", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            place_right_of(lbl_favicon, faviconB, 0.42)

            faviconB.bind("<Enter>", onHoverEnter)
            faviconB.bind("<Leave>", onHoverLeave)
            faviconB.bind("<Button-1>", onClick)


            lbl_passwords = Label(dataFrame, text="Hide Passwords:", font=("arial", 28), bg=BG_CARD, fg=FG_COLOR_P)
            lbl_passwords.place(relx=0.02, rely=0.52, anchor='w')

            passwordB = Label(dataFrame, text="Off" if settings["passwordsShownByDefault"] else "On", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            place_right_of(lbl_passwords, passwordB, 0.52)

            passwordB.bind("<Enter>", onHoverEnter)
            passwordB.bind("<Leave>", onHoverLeave)
            passwordB.bind("<Button-1>", onClick)
        if settingOption == "Authentication":
            with open(f'files/{user}/config/settings.json', 'r') as f:
                settings = json.load(f)
                settings = settings["settings"][settingOption]

            def place_right_of(left_widget, right_widget, rely, padding=20):
                left_widget.update_idletasks()
                x = left_widget.winfo_x() + left_widget.winfo_reqwidth() + padding
                right_widget.place(x=x, rely=rely, anchor='w')
            def onHoverEnter(event):
                widget = event.widget
                if widget == requirePinB: requirePinB.config(fg=FG_COLOR_S, bg=BG_BUTTON_ALT)
                if widget == otpB: otpB.config(fg=FG_COLOR_S, bg=BG_BUTTON_ALT)
                if widget == otpL: otpL.config(fg=FG_COLOR_S)
            def onHoverLeave(event):
                widget = event.widget
                if widget == requirePinB: requirePinB.config(fg=FG_COLOR_P, bg=BG_CARD)
                if widget == otpB: otpB.config(fg=FG_COLOR_P, bg=BG_CARD)
                if widget == otpL: otpL.config(fg=FG_COLOR_P)
            def onClick(event):
                widget = event.widget
                with open(f'files/{user}/config/settings.json', 'r') as f:
                    data = json.load(f)

                if widget == requirePinB:
                    current = data["settings"][settingOption]["requirePin"]
                    new_value = not current
                    data["settings"][settingOption]["requirePin"] = new_value
                    requirePinB.config(text="On" if new_value else "Off")
                if widget == otpB:
                    current = data["settings"][settingOption]["auth"]
                    new_value = not current
                    data["settings"][settingOption]["auth"] = new_value
                    otpB.config(text="On" if new_value else "Off")
                if widget == otpL: pyperclip.copy(settings["authKey"])

                with open(f'files/{user}/config/settings.json', 'w') as f: json.dump(data, f, indent=4)

            def focusIn(event): pinE.delete(0, END)
            def focusOut(event): pinE.delete(0, END); pinE.insert(0, settings["pin"])
            def keyStroke(*_):
                value = pinVar.get()
                if len(value) > 4:
                    pinVar.set(value[:4])
                if len(value) == 4:
                    with open(f'files/{user}/config/settings.json', 'r') as f: data = json.load(f)
                    with open(f'files/{user}/config/settings.json', 'w') as f:
                        data["settings"][settingOption]["pin"] = pinVar.get()
                        json.dump(data, f, indent=4)

            Label(dataFrame, text="Authentication", font=('arial', 32), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.5, rely=0.05, anchor="center")

            lbl_requirePin = Label(dataFrame, text="Require Pin:", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            lbl_requirePin.place(relx=0.02, rely=0.15, anchor='w')
            requirePinB = Label(dataFrame, text="On" if settings["requirePin"] else "Off", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            place_right_of(lbl_requirePin, requirePinB, 0.15)
            requirePinB.bind("<Enter>", onHoverEnter)
            requirePinB.bind("<Leave>", onHoverLeave)
            requirePinB.bind("<Button-1>", onClick)

            lbl_pin = Label(dataFrame, text="Pin:", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            lbl_pin.place(relx=0.02, rely=0.25, anchor='w')
            pinVar = StringVar()
            pinVar.trace_add('write', keyStroke)
            pinE = Entry(dataFrame, textvariable=pinVar, font=('arial', 25), justify='center', bg=BG_INPUT, fg=FG_COLOR_P, relief="flat", bd=0)
            place_right_of(lbl_pin, pinE, 0.25)
            pinE.insert(0, settings["pin"])
            pinE.bind("<FocusIn>", focusIn)
            pinE.bind("<FocusOut>", focusOut)
            pinE.bind("<Key>", keyStroke)

            lbl_useOTP = Label(dataFrame, text="Use OTP:", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            lbl_useOTP.place(relx=0.02, rely=0.36, anchor='w')
            otpB = Label(dataFrame, text="On" if settings["auth"] else "Off", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            place_right_of(lbl_useOTP, otpB, 0.36)
            otpB.bind("<Enter>", onHoverEnter)
            otpB.bind("<Leave>", onHoverLeave)
            otpB.bind("<Button-1>", onClick)

            lbl_key = Label(dataFrame, text="OTP Key:", font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
            lbl_key.place(relx=0.02, rely=0.46, anchor='w')
            otpL = Label(dataFrame, text=settings["authKey"], font=('arial', 15), bg=BG_CARD, fg=FG_COLOR_P, wraplength=1000, justify='left')
            otpL.bind("<Enter>", onHoverEnter)
            otpL.bind("<Leave>", onHoverLeave)
            otpL.bind("<Button-1>", onClick)
            place_right_of(lbl_key, otpL, 0.46)

            uri = pyotp.totp.TOTP(settings["authKey"]).provisioning_uri(name=user, issuer_name="")
            qrcode.make(uri).save(f'files/{user}/config/temp.png')
            img = ImageTk.PhotoImage(Image.open(f"files/{user}/config/temp.png").resize((250, 250)))
            os.remove(f"files/{user}/config/temp.png")

            imgLabel = Label(dataFrame)
            imgLabel.place(relx=0.5, rely=0.7, anchor='center')
            imgLabel.image = img
            imgLabel['image'] = imgLabel.image
            
        if settingOption == "Change Password":
            Label(dataFrame, text="Change Password", font=('arial', 32), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.5, rely=0.05, anchor="center")
        
            def focusIn(event):
                widget = event.widget
    
                if widget == oldPasw: 
                    if widget.get() == "Old Password":
                        oldPasw.delete(0, END)
                        oldPasw.config(fg=FG_COLOR_P)
                if widget == newPasw:
                    if widget.get() == "New Password":
                        newPasw.delete(0, END)
                        newPasw.config(fg=FG_COLOR_P)
            def focusOut(event):
                widget = event.widget

                if widget == oldPasw: 
                    if widget.get() == "":
                        oldPasw.insert(0, "Old Password")
                        oldPasw.config(fg=FG_COLOR_S)
                if widget == newPasw:
                    if widget.get() == "":
                        newPasw.insert(0, "New Password")
                        newPasw.config(fg=FG_COLOR_S)
            def changePasw():
                nonlocal vaultKey

                old_pw = oldPasw.get()
                new_pw = newPasw.get()

                if not old_pw or not new_pw:
                    Label(dataFrame, text="Please fill in both old and new password", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return

                with open("files/logins.txt", 'r') as f:
                    login_lines = f.readlines()

                user_idx = None
                stored_salt_b64 = None
                stored_hash_b64 = None

                for idx, line in enumerate(login_lines):
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        salt_b64, hash_b64, username = parts[0], parts[1], parts[2]
                        if username == user:
                            user_idx = idx
                            stored_salt_b64 = salt_b64
                            stored_hash_b64 = hash_b64
                            break

                if user_idx is None:
                    Label(dataFrame, text="User not found", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return

                try:
                    salt = base64.b64decode(stored_salt_b64)
                    expected_hash = base64.b64decode(stored_hash_b64)
                    derived = cryption.deriveMasterKey(old_pw, salt)
                except Exception:
                    Label(dataFrame, text="Login record corrupted", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return

                if derived != expected_hash:
                    Label(dataFrame, text="Wrong old password", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return

                passwords_plain = []
                try:
                    with open(f"files/{user}/passwords.txt", 'r') as f:
                        for enc_line in f:
                            enc_line = enc_line.strip()
                            if enc_line: passwords_plain.append(cryption.decrypt_line(vaultKey, enc_line))
                except FileNotFoundError: pass

                cards_plain = []
                try:
                    with open(f"files/{user}/cards.txt", 'r') as f:
                        for enc_line in f:
                            enc_line = enc_line.strip()
                            if enc_line: cards_plain.append(cryption.decrypt_line(vaultKey, enc_line))
                except FileNotFoundError: pass

                notes_dir = f"files/{user}/notes"
                notes_plain = {}

                if os.path.isdir(notes_dir):
                    for filename in os.listdir(notes_dir):
                        path = os.path.join(notes_dir, filename)
                        if not os.path.isfile(path): continue

                        try:
                            with open(path, "r", encoding="utf-8") as f: raw = f.read()

                            content = cryption.decrypt_note(vaultKey, raw)
                            notes_plain[path] = content
                        except Exception: continue

                new_salt = os.urandom(16)
                new_key = cryption.deriveMasterKey(new_pw, new_salt)

                new_salt_b64 = base64.b64encode(new_salt).decode()
                new_hash_b64 = base64.b64encode(new_key).decode()

                login_lines[user_idx] = f"{new_salt_b64},{new_hash_b64},{user}\n"

                with open("files/logins.txt", 'w') as f:
                    f.writelines(login_lines)

                if passwords_plain:
                    with open(f"files/{user}/passwords.txt", 'w') as f:
                        for rec in passwords_plain:
                            f.write(cryption.encrypt_line(new_key, rec) + "\n")

                if cards_plain:
                    with open(f"files/{user}/cards.txt", 'w') as f:
                        for rec in cards_plain:
                            f.write(cryption.encrypt_line(new_key, rec) + "\n")

                for path, content in notes_plain.items():
                    cryption.save_note(new_key, path, content)

                vaultKey = new_key

                Label(dataFrame, text="Master password changed and vault re-encrypted", font=('arial', 20), fg="green", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
            
            oldPasw = Entry(dataFrame, font=('arial', 32), bg=BG_INPUT, fg=FG_COLOR_S, relief='flat', bd=0, justify='center')
            oldPasw.place(relx=0.5, rely=0.17, relwidth=0.8, relheight=0.08, anchor="center")
            oldPasw.insert(0, "Old Password")
            oldPasw.bind("<FocusIn>", focusIn)
            oldPasw.bind("<FocusOut>", focusOut)

            newPasw = Entry(dataFrame, font=('arial', 28), bg=BG_INPUT, fg=FG_COLOR_S, relief='flat', bd=0, justify='center')
            newPasw.place(relx=0.5, rely=0.27, relwidth=0.8, relheight=0.08, anchor="center")
            newPasw.insert(0, "New Password")
            newPasw.bind("<FocusIn>", focusIn)
            newPasw.bind("<FocusOut>", focusOut)

            confirmB = Button(dataFrame, text="Confirm Change", font=('arial', 28), command=changePasw, bg=BG_BUTTON, fg=FG_COLOR_P, relief='flat', bd=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            confirmB.place(relx=0.5, rely=0.4, relwidth=0.8, relheight=0.08, anchor="center")
        if settingOption == "Delete Account":
            Label(dataFrame, text="Delete Account", font=('arial', 32), bg=BG_CARD, fg=FG_COLOR_P).place(relx=0.5, rely=0.05, anchor="center")

            def focusIn(event):
                widget = event.widget
    
                if widget == pasw1: 
                    if widget.get() == "Password":
                        pasw1.delete(0, END)
                        pasw1.config(fg=FG_COLOR_P)
                if widget == pasw2:
                    if widget.get() == "Confirm Password":
                        pasw2.delete(0, END)
                        pasw2.config(fg=FG_COLOR_P)
            def focusOut(event):
                widget = event.widget

                if widget == pasw1: 
                    if widget.get() == "":
                        pasw1.insert(0, "Password")
                        pasw1.config(fg=FG_COLOR_S)
                if widget == pasw2:
                    if widget.get() == "":
                        pasw2.insert(0, "Confirm Password")
                        pasw2.config(fg=FG_COLOR_S)

            def delete():
                password1 = pasw1.get()
                password2 = pasw2.get()

                if not password1 or not password2 or password1 in ("Password",) or password2 in ("Confirm Password",):
                    Label(dataFrame, text="Please enter and confirm your password", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return
                if password1 != password2:
                    Label(dataFrame, text="Passwords do not match", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return

                with open("files/logins.txt", 'r') as f:
                    login_lines = f.readlines()

                user_idx = None
                salt_b64 = hash_b64 = None
                for idx, line in enumerate(login_lines):
                    parts = line.strip().split(',')
                    if len(parts) >= 3 and parts[2] == user:
                        user_idx = idx
                        salt_b64, hash_b64 = parts[0], parts[1]
                        break

                if user_idx is None:
                    Label(dataFrame, text="User not found", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return

                login_ok, _ = cryption.verifyMasterPassword(password1, salt_b64, hash_b64)
                if not login_ok:
                    Label(dataFrame, text="Incorrect password", font=('arial', 20), fg="red", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")
                    return

                del login_lines[user_idx]
                with open("files/logins.txt", 'w') as f:
                    f.writelines(login_lines)

                shutil.rmtree(f"files/{user}", ignore_errors=True)

                Label(dataFrame, text="Account deleted", font=('arial', 20), fg="green", bg=BG_CARD).place(relx=0.5, rely=0.55, anchor="center")

            pasw1 = Entry(dataFrame, font=('arial', 32), bg=BG_INPUT, fg=FG_COLOR_S, relief='flat', bd=0, justify='center')
            pasw1.place(relx=0.5, rely=0.17, relwidth=0.8, relheight=0.08, anchor="center")
            pasw1.insert(0, "Password")
            pasw1.bind("<FocusIn>", focusIn)
            pasw1.bind("<FocusOut>", focusOut)

            pasw2 = Entry(dataFrame, font=('arial', 28), bg=BG_INPUT, fg=FG_COLOR_S, relief='flat', bd=0, justify='center')
            pasw2.place(relx=0.5, rely=0.27, relwidth=0.8, relheight=0.08, anchor="center")
            pasw2.insert(0, "Confirm Password")
            pasw2.bind("<FocusIn>", focusIn)
            pasw2.bind("<FocusOut>", focusOut)

            confirmB = Button(dataFrame, text="Confirm Deletion", font=('arial', 28), command=delete, bg=BG_BUTTON, fg=FG_COLOR_P, relief='flat', bd=0, activebackground=BG_BUTTON_ALT, activeforeground=FG_COLOR_S)
            confirmB.place(relx=0.5, rely=0.4, relwidth=0.8, relheight=0.08, anchor="center")

    settingList = ["General Settings", "Authentication", "Change Password", "Delete Account"]

    for line in settingList:
        accFrame = Frame(inner_frame, bg=BG_CARD, bd=0, highlightthickness=0)
        accFrame.place(x=10, y=yPos, relwidth=0.95, height=80)
        accFrame.bind("<Button-1>", lambda e, s=line: displaySetting(s, e))

        settingNameL = Label(accFrame, text=line, font=('arial', 32), bg=BG_CARD, fg=FG_COLOR_P)
        settingNameL.place(x=10, y=15)
        settingNameL.bind("<Button-1>", lambda e, s=line: displaySetting(s, e))

        yPos += 100
    
    inner_frame.update_idletasks()
    total_height = yPos + 20
    inner_frame.config(height=total_height, width=canvas.winfo_width())
    canvas.update_idletasks()
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), total_height))
def notes(inner_frame, contFrame, canvas, dataFrame, user, root, vaultKey):
    _clear_content(inner_frame, contFrame, dataFrame)
    yPos = 10

    with open(f'files/{user}/config/settings.json', 'r') as f:
        data = json.load(f)
        currentTheme = loadTheme(data["settings"]["General Settings"]["theme"])

    BG_PANEL = currentTheme["BG_PANEL"]
    BG_LIST = currentTheme["BG_LIST"]
    BG_CARD = currentTheme["BG_CARD"]

    BG_INPUT = currentTheme["BG_INPUT"]
    BG_BUTTON = currentTheme["BG_BUTTON"]
    BG_BUTTON_ALT = currentTheme["BG_BUTTON_ALT"]

    FG_COLOR_P = currentTheme["FG_PRIMARY"]
    FG_COLOR_S = currentTheme["FG_SECONDARY"]
    FG_HIGHLIGHT = currentTheme["FG_MUTED"]
    ACCENT_BLUE = currentTheme["ACCENT_BLUE"]
    ACCENT_BLUE_GLOW = currentTheme["ACCENT_BLUE_GLOW"]

    def displayNote(noteFile, noteDesc, event):
        for widget in dataFrame.winfo_children():
            widget.destroy()
        
        def save_note(event=None):
            nonlocal isEdited
            content = notesText.get("1.0", "end-1c")
            encrypted = cryption.encrypt_note(vaultKey, content)

            isEdited = False
            updateTitle()

            with open(f"files/{user}/notes/{noteFile}-{noteDesc}.txt", "w", encoding="utf-8") as f:
                f.write(encrypted)
        def updateTitle():
            if isEdited:
                titleL.config(text=f"{noteName}*")
            else:
                titleL.config(text=noteName)
        def onTextModified(event=None):
            nonlocal isEdited

            if not isEdited:
                isEdited = True
                updateTitle()

            notesText.edit_modified(False)

        noteName = noteFile
        isEdited = False

        titleL = Label(dataFrame, text=noteName, font=("arial", 32, 'bold'), bg=BG_CARD, fg=FG_COLOR_P )
        titleL.place(relx=0.5, rely=0.05, anchor="center")

        textFrame = Frame(dataFrame, bg=BG_CARD)
        textFrame.place(relx=0, rely=0.12, relwidth=1, relheight=0.88)

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
            troughcolor=BG_INPUT,
            bordercolor=BG_INPUT,
            arrowcolor="#ffffff",
            relief="flat",
            borderwidth=0
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", "#505660")]
        )

        scrollbar = ttk.Scrollbar(textFrame, style="Vertical.TScrollbar")
        scrollbar.place(relx=0.98, rely=0, relwidth=0.02, relheight=1)

        notesText = Text( textFrame, bg=BG_INPUT, fg=FG_COLOR_P, font=('consolas', 20), borderwidth=2, relief="solid", yscrollcommand=scrollbar.set, wrap="word")
        notesText.place(relx=0, rely=0, relwidth=0.98, relheight=1)
        notesText.bind("<<Modified>>", onTextModified)

        scrollbar.config(command=notesText.yview)
        notesText.focus_set()
        root.bind("<Control-s>", save_note)

        if os.path.exists(f"files/{user}/notes/{noteFile}-{noteDesc}.txt"):
            try:
                with open(f"files/{user}/notes/{noteFile}-{noteDesc}.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                content = cryption.decrypt_note(vaultKey, content)
                notesText.insert("1.0", content)
            except Exception as e:
                notesText.insert("1.0", f"[Error loading note]\n{e}")
        else:
            notesText.insert("1.0", "")

        notesText.edit_modified(False)
        isEdited = False
        updateTitle()
    
    notesFiles = [ note.stem.split("-") for note in Path(f"files/{user}/notes").glob("*.txt") ]

    for note in notesFiles:
        accFrame = Frame(inner_frame, bg=BG_CARD, bd=0, highlightthickness=0)
        accFrame.place(x=10, y=yPos, relwidth=0.95, height=80)
        accFrame.bind("<Button-1>", lambda e, n=note[0], d=note[1]: displayNote(n, d, e))
        accFrame.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        noteNameL = Label(accFrame, text=note[0], font=('arial', 28), bg=BG_CARD, fg=FG_COLOR_P)
        noteNameL.place(x=5, y=2)
        noteNameL.bind("<Button-1>", lambda e, n=note[0], d=note[1]: displayNote(n, d, e))
        noteNameL.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        noteDescL = Label(accFrame, text=note[1], font=('arial', 14), bg=BG_CARD, fg=FG_COLOR_S)
        noteDescL.place(x=5, y=46)
        noteDescL.bind("<Button-1>", lambda e, n=note[0], d=note[1]: displayNote(n, d, e))
        noteDescL.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        yPos += 100
    
    inner_frame.update_idletasks()
    total_height = yPos + 20
    inner_frame.config(height=total_height, width=canvas.winfo_width())
    canvas.update_idletasks()
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), total_height))
