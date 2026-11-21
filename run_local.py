"""
DocuLens Enterprise AI: 1-Click Automated Local Setup & Model Runner.
Automatically verifies Ollama, starts the daemon if needed, downloads/pulls
Qwen 2.5 (1.5B), and launches the full DocuLens platform locally in your browser.
"""

import os
import sys
import time
import shutil
import subprocess
import urllib.request
import json
import webbrowser

OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:1.5b"
PORT = 8000

def find_ollama_binary():
    """Locates the Ollama executable on Windows, macOS, or Linux."""
    # 1. Check system PATH
    ollama_path = shutil.which("ollama")
    if ollama_path:
        return ollama_path

    # 2. Check standard Windows AppData location
    user_profile = os.environ.get("USERPROFILE", "")
    win_path = os.path.join(user_profile, "AppData", "Local", "Programs", "Ollama", "ollama.exe")
    if os.path.exists(win_path):
        return win_path

    # 3. Check Program Files
    win_prog = r"C:\Program Files\Ollama\ollama.exe"
    if os.path.exists(win_prog):
        return win_prog

    # 4. Check macOS / Linux standard paths
    for p in ["/usr/local/bin/ollama", "/usr/bin/ollama"]:
        if os.path.exists(p):
            return p

    return None

def is_ollama_running():
    """Pings the Ollama local API."""
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, models
    except Exception:
        return False, []

def start_ollama_daemon(ollama_bin):
    """Spawns 'ollama serve' in the background if not already active."""
    print("⏳ Starting local Ollama background service...")
    try:
        if sys.platform == "win32":
            subprocess.Popen([ollama_bin, "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen([ollama_bin, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait up to 10 seconds for daemon to initialize
        for _ in range(20):
            time.sleep(0.5)
            active, models = is_ollama_running()
            if active:
                print("✅ Ollama background service is active!")
                return True, models
    except Exception as e:
        print(f"⚠️ Could not start Ollama automatically: {e}")
    return False, []

def ensure_model_installed(ollama_bin, installed_models):
    """Verifies that qwen2.5:1.5b is downloaded; pulls it automatically if missing."""
    for m in installed_models:
        if DEFAULT_MODEL in m:
            print(f"✅ AI Model '{DEFAULT_MODEL}' is already downloaded and ready to use!")
            return True

    print(f"\n📥 Model '{DEFAULT_MODEL}' not found. Downloading open-weight model now (~980 MB)...")
    print("This only happens once. Please wait a few moments...\n")
    try:
        proc = subprocess.run([ollama_bin, "pull", DEFAULT_MODEL], check=True)
        if proc.returncode == 0:
            print(f"\n✅ Successfully downloaded and configured '{DEFAULT_MODEL}'!")
            return True
    except Exception as e:
        print(f"⚠️ Error downloading model: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 DocuLens Enterprise AI — 1-Click Automated Local Setup")
    print("=" * 70)

    # 1. Check Ollama Installation
    ollama_bin = find_ollama_binary()
    if not ollama_bin:
        print("\n❌ Ollama is not installed on this machine.")
        print("Please download and run the 1-click free installer from:")
        print("👉 https://ollama.com/download\n")
        print("After installing, run this script again: python run_local.py")
        sys.exit(1)

    print(f"✅ Located Ollama at: {ollama_bin}")

    # 2. Check if Ollama Daemon is Running
    active, installed_models = is_ollama_running()
    if not active:
        active, installed_models = start_ollama_daemon(ollama_bin)
        if not active:
            print("⚠️ Ollama did not respond in time. Please run 'ollama serve' in a terminal.")
            sys.exit(1)
    else:
        print("✅ Ollama background daemon is actively running.")

    # 3. Ensure Qwen 2.5 Model is Downloaded
    ensure_model_installed(ollama_bin, installed_models)

    # 4. Launch FastAPI Application
    app_url = f"http://127.0.0.1:{PORT}/static/index.html"
    print("\n" + "=" * 70)
    print(f"🌐 Launching DocuLens Enterprise Studio on: {app_url}")
    print("=" * 70)

    # Open browser automatically after 1.5 seconds
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(app_url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run uvicorn
    import uvicorn
    from app import app
    uvicorn.run(app, host="127.0.0.1", port=PORT)

if __name__ == "__main__":
    main()
