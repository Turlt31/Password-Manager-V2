# Password Manager (Tkinter)

A desktop password & card manager built with Tkinter. It supports per-user profiles, theming, optional OTP, and favicon lookups for a friendly UI.

## Features
- User accounts with login/register flow; per-user data stored under `files/<username>/`.
- Password vault: website, username, password, optional TOTP secret; quick copy and toggle visibility.
- Card vault: bank, cardholder, number, expiry, CVC, PIN; quick copy and show/hide.
- Search + reorder: filter entries and move them up/down for custom ordering.
- OTP support: pyotp-based verification at login (optional) and live TOTP display for saved secrets.
- Theming: multiple color themes (blue/dark/light/purple/red/green) and favicon fetching for sites.
- Clipboard helpers and password generator.
- Settings per user: default screen, theme, favicon toggle, password visibility, require PIN, OTP on/off.

## Requirements
- Python 3.11+ (Tkinter included)
- Pip packages: `Pillow`, `pyotp`, `pyperclip`, `pandas`
- Local filesystem access (data stored in plain text in `files/`)

Install deps:
```bash
python -m pip install Pillow pyotp pyperclip pandas
```

## Run
```bash
python main.py
```

## Usage
1. **Register** a new user on first launch (creates `files/<username>/` with `passwords.txt`, `cards.txt`, `notes.txt`, and `config/settings.json`).
2. **Login** with your credentials. If OTP is enabled for the user, enter the 6-digit code.
3. Use the left menu to switch between **Logins**, **Cards**, and **Settings**.
4. Click **+** to add entries. Fields have placeholders; passwords can be generated and toggled hidden/visible.
5. Click items in the detail panel to copy (username/password/TOTP/card fields). Use the eye/edit/bin icons to show, edit, or delete.
6. Adjust **Settings** for theme, default screen, favicon loading, default password visibility, PIN requirement, and OTP toggle.

## Data & Settings Layout
- `files/logins.txt` — list of usernames/passwords for the app.
- `files/<user>/passwords.txt` — CSV lines: `name,url,username,password,[otpSecret]`
- `files/<user>/cards.txt` — CSV lines: `bank,url,nameOnCard,cardNumber,expiry,cvc,pin`
- `files/<user>/notes.txt` — reserved for notes (if used).
- `files/<user>/config/settings.json` — per-user UI/auth preferences.
- Favicons cached in `icon/favicons/`.

## Security Notes
- Entries are stored **unencrypted** in plain text. Do not use for sensitive production secrets without adding encryption (e.g., filling out `cryption.py`).
- OTP and PIN improve access control but do not encrypt stored data. Consider disk encryption or adding crypto before real-world use.

## Customization Ideas
- Implement encryption in `cryption.py` for stored files.
- Add export/import and note management.
- Package with a virtual environment and `requirements.txt`/`pyproject.toml`.
