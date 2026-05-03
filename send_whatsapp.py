# send_whatsapp.py
import subprocess
import os
from pathlib import Path
from cli_interface import BLAXKCLI
import json

def main():
    cli = BLAXKCLI()
    cli.show_banner()
    
    # Check messages file
    messages_file = Path("output/phone_numbers.json")
    if not messages_file.exists():
        cli.error("No messages found! Run 'python main.py' first.")
        return
    
    # Load message count
    with open(messages_file) as f:
        messages = json.load(f)
    
    cli.show_whatsapp_banner(len(messages))
    
    # Check Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except:
        cli.error("Node.js not installed! Get it from: https://nodejs.org/")
        return
    
    # Install dependencies
    bot_dir = Path("whatsapp_bot")
    if not (bot_dir / "node_modules").exists():
        cli.step("Installing dependencies...")
        os.chdir(bot_dir)
        subprocess.run(["npm", "install"], check=True, capture_output=True)
        os.chdir("..")
        cli.success("Dependencies installed")
    
    # Run bot
    cli.step("Starting WhatsApp Bot...")
    os.chdir("whatsapp_bot")
    subprocess.run(["node", "bot.js"])

if __name__ == "__main__":
    main()
