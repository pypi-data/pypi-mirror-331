#!/usr/bin/env python3
import os
import sys
import random
import base64
import argparse
from colorama import Fore, Style

def start_command():
    # Generate an 8-digit random connection code.
    code = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    print(Fore.GREEN + "Your connection code: " + code)
    with open("connection_code.txt", "w", encoding="utf-8") as f:
        f.write(code)

def connect_command(provided_code):
    if not os.path.exists("connection_code.txt"):
        print(Fore.RED + "No connection code found. Please run 'bsb -start' first.")
        return
    with open("connection_code.txt", "r", encoding="utf-8") as f:
        saved_code = f.read().strip()
    if provided_code == saved_code:
        print(Fore.GREEN + "Successfully connected!")
    else:
        print(Fore.RED + "Incorrect connection code.")

def list_command():
    files = os.listdir('.')
    print(Fore.BLUE + "Listing files and directories:")
    for f in files:
        print(Fore.YELLOW + f)

def download_command(target):
    if not os.path.exists(target):
        print(Fore.RED + f"{target} not found.")
        return
    try:
        with open(target, "rb") as f:
            content = f.read()
        encoded = base64.b64encode(content).decode('utf-8')
        out_file = target + ".b64"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(encoded)
        print(Fore.GREEN + f"{target} encoded and saved as {out_file}.")
    except Exception as e:
        print(Fore.RED + f"Error in downloading: {e}")

def upload_command(target):
    encoded_file = target + ".b64"
    if not os.path.exists(encoded_file):
        print(Fore.RED + f"{encoded_file} not found.")
        return
    try:
        with open(encoded_file, "r", encoding="utf-8") as f:
            encoded_content = f.read()
        decoded = base64.b64decode(encoded_content)
        out_file = "uploaded_" + target
        with open(out_file, "wb") as f:
            f.write(decoded)
        print(Fore.GREEN + f"{target} decoded and saved as {out_file}.")
    except Exception as e:
        print(Fore.RED + f"Error in uploading: {e}")

def main():
    parser = argparse.ArgumentParser(description="BlackSpammerBD CLI")
    parser.add_argument('command', help="Select command", choices=['-start', '-connect', '-list', '-download', '-upload'])
    parser.add_argument('argument', nargs='?', help="Argument for the command (e.g., connection code or filename)")
    args = parser.parse_args()
    
    if args.command == '-start':
        start_command()
    elif args.command == '-connect':
        if not args.argument:
            print(Fore.RED + "Please provide a connection code.")
        else:
            connect_command(args.argument)
    elif args.command == '-list':
        list_command()
    elif args.command == '-download':
        if not args.argument:
            print(Fore.RED + "Please provide a file/folder name to download.")
        else:
            download_command(args.argument)
    elif args.command == '-upload':
        if not args.argument:
            print(Fore.RED + "Please provide a file/folder name to upload.")
        else:
            upload_command(args.argument)
    else:
        print(Fore.RED + "Unknown command.")

if __name__ == '__main__':
    main()
