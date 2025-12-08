# Password Manager (Tkinter)

A desktop password and card manager built with Tkinter. Each user gets a themed vault with optional OTP, clipboard helpers, and now encrypted storage using Argon2id + AES‑256‑GCM.

## Features
- Per-user vaults (`files/<username>/`) with login/register flow.
- Password items: website, username, password, optional TOTP secret; copy and toggle visibility.
- Card items: bank, cardholder, number, expiry, CVC, PIN; copy and show/hide.
- Search and reorder entries; favicon fetching and multiple color themes.
- Optional OTP at login and live TOTP display for saved secrets.
- Encryption: keys derived with Argon2id; vault lines encrypted with AES‑256‑GCM.

## Requirements
- Python 3.11+ with Tkinter.
- Pip packages:
  - Pillow
  - pyotp
  - pyperclip
  - pandas
  - cryptography
  - argon2-cffi

Install:
```bash
python -m pip install Pillow pyotp pyperclip pandas cryptography argon2-cffi
```

## Run
```bash
python main.py
```

## Usage
1. Launch and **Register** a user (creates `files/<user>/` with encrypted vault files and `config/settings.json`).
2. **Login**; if OTP is enabled, enter the 6-digit code. If a PIN is required, you will be prompted.
3. Use the left menu to switch between **Logins**, **Cards**, and **Settings**.
4. Click **+** to add entries. Passwords can be generated and toggled between hidden/visible.
5. Click fields in the detail view to copy (username/password/TOTP/card fields). Use the eye/edit/bin icons to show, edit, or delete.
6. In **Settings**, adjust theme, default screen, favicon loading, password visibility, PIN requirement, and OTP toggle.

## Data & Encryption
- User data lives in `files/<user>/`.
- Vault files (`passwords.txt`, `cards.txt`, `notes.txt`) store **encrypted** lines: AES‑256‑GCM ciphertext with a per-line nonce.
- Master keys are derived from the user’s master password via Argon2id (time_cost=3, memory_cost=64MB, parallelism=4).
- Favicon cache lives in `icon/favicons/`; UI assets in `icon/buttonImg/`.

## Security Notes
- Keep your master password safe; it derives the vault key.
- Back up `files/<user>/` if you care about the data; losing it loses the vault.
- If you have old plaintext data, re-add it through the app so it is written in encrypted form.
- OTP/PIN protects access, but does not replace the need for a strong master password and secure backups.

## Project Layout
- `main.py` — UI shell (login/register, navigation).
- `apps.py` — screens for passwords, cards, and settings.
- `theme.py` — theme definitions.
- `cryption.py` — Argon2id key derivation and AES‑GCM encryption/decryption helpers.

## Screen Shots
<img width="788" height="414" alt="image" src="https://github.com/user-attachments/assets/41a6a43d-adec-4e7e-ae35-de5d79fec15c" />
<img width="788" height="414" alt="image" src="https://github.com/user-attachments/assets/5abd3c9f-6f0a-4061-883a-ed625ef4874b" />



<br>

Feel Free to reach out to me if you have any questions <br>
Discord: `.turtl3.`
