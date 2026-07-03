# VoiceScript Bot 🎤🤖

A robust, modular Python Telegram bot that transforms running input text items into beautiful, professional studio narration voice files using the **OpenAI TTS engine**. Optimized for deployment on **Render.com**.

## 📁 Repository Structure
- `bot.py`: Main gateway application and polling router loops.
- `tts.py`: Outbound request processing wrapper interacting with OpenAI endpoints.
- `database.py`: Clean SQLite persistent tracking mappings layer.
- `requirements.txt`: System package dependency configurations.
- `runtime.txt`: Pinned environment target configurations.

## 🚀 Deployment Instructions for Render.com

### Step 1: Push Code base to your Personal GitHub Profile
Initialize and sync your directory to an assigned public/private GitHub repository:
```bash
git init
git add .
git commit -m "Deployment release build footprint"
git branch -M main
git remote add origin [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
git push -u origin main

