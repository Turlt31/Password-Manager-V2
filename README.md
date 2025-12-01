# Password-Maneger-V2
An updated password manager


Can safely store:
  1. Accounts with email/username, password, and (new) Authentication Codes OTP
  2. Credit/Debit cards

Encryption: (Not Implemented yet)
  * SHA256 for the Master password
  * Cryptography.Fernet for the accounts

Features:
  * Multiple Accounts
  * Two-Factor Authentication (Not implemented yet)
  * Has a text editor (Notes) (Not implemented yet)
  * It also has a new redesigned GUI with a cleaner look
  * Nice dark theme color palette (Can be easily changed in the themes.py)
  * Now it automatically downloads the favicon of a website

For an .exe version, run the following commands in the same directory as the .py file  
```
pip install pyinstaller
pyinstaller --onefile -w main.py
```
After that, 2 new folders will appear in the same directory  
You can safely delete "build"   
And in "dist" will be the .exe file  
Move the .exe file into the same directory where the .py file is

<br>
If you have any suggestions 

DM me on Discord: .turtl3.
