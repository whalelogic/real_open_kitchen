# 🔑 API Key Acquisition Guide

If your teammates need to grab their own keys to test your code, you can send them these quick steps:

## How to get a Google Gemini API Key

1. Go to [aistudio.google.com](https://aistudio.google.com) and sign in with your Google account.
2. Look at the left-hand navigation menu and click **Get API key**.
3. Click the blue **Create API key** button.
4. Copy the long string of text generated (it usually starts with `AIzaSy...`).

## How to get a Freepik API Key

1. Go to [freepik.com/api](https://www.freepik.com/api) and sign in (or create a free account).
2. Navigate to your **Developer Dashboard / API** section.
3. Click to generate a new API key.
4. Copy the key (it usually starts with `FPSX...`).

---

# ⚙️ Local Project Setup

To make sure the application actually uses these new keys, tell your team to do the following:

### 1. Create or update your `.flaskenv` file

In the root directory of the project (where `run.sh` lives), open the `.flaskenv` file and make sure it looks exactly like this. **Do not use spaces around the `=` sign, and do not use quotes!**

```
FLASK_APP=run.py
FLASK_ENV=development

# --- AI API KEYS ---
GEMINI_API_KEY=PasteYourGoogleKeyHere
FREEPIK_API_KEY=PasteYourFreepikKeyHere
```

### 2. Delete any old `.env` files

If you have a `.env` file floating around from older tutorials, delete it so it doesn't accidentally override your `.flaskenv` settings.

### 3. Restart the Server

Environment variables are only loaded when the server boots up. If your server is currently running, click into your terminal, press `Ctrl + C` to stop it, and then run `./run.sh` again to lock in the new keys.
