#!/usr/bin/env python3
import os
import random
import base64
import argparse
from colorama import Fore, Style

def start_command():
    """Generate an 8-digit connection code and save it to a file."""
    code = ''.join(str(random.randint(0, 9)) for _ in range(8))
    print(Fore.GREEN + Style.BRIGHT + "Your connection code: " + code)
    with open("connection_code.txt", "w", encoding="utf-8") as f:
        f.write(code)

def connect_command(provided_code):
    """Verify the provided connection code against the saved code."""
    if not os.path.exists("connection_code.txt"):
        print(Fore.RED + Style.BRIGHT + "No connection code found. Please run 'bsb start' first.")
        return
    with open("connection_code.txt", "r", encoding="utf-8") as f:
        saved_code = f.read().strip()
    if provided_code == saved_code:
        print(Fore.GREEN + Style.BRIGHT + "Successfully connected!")
    else:
        print(Fore.RED + Style.BRIGHT + "Incorrect connection code.")

def list_command():
    """List all files and directories in the current folder."""
    items = os.listdir('.')
    print(Fore.BLUE + Style.BRIGHT + "Listing files and directories:")
    for item in items:
        print(Fore.YELLOW + f" - {item}")

def download_command(target):
    """Base64 encode a file and save the output to <file>.b64."""
    if not os.path.exists(target):
        print(Fore.RED + Style.BRIGHT + f"Error: '{target}' not found.")
        return
    try:
        with open(target, "rb") as f:
            content = f.read()
        encoded = base64.b64encode(content).decode('utf-8')
        out_file = target + ".b64"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(encoded)
        print(Fore.GREEN + Style.BRIGHT + f"'{target}' encoded successfully as '{out_file}'.")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Download error: {e}")

def upload_command(target):
    """Decode a Base64 encoded file (<file>.b64) and save the decoded content."""
    encoded_file = target + ".b64"
    if not os.path.exists(encoded_file):
        print(Fore.RED + Style.BRIGHT + f"Error: '{encoded_file}' not found.")
        return
    try:
        with open(encoded_file, "r", encoding="utf-8") as f:
            encoded_content = f.read()
        decoded = base64.b64decode(encoded_content)
        out_file = "uploaded_" + target
        with open(out_file, "wb") as f:
            f.write(decoded)
        print(Fore.GREEN + Style.BRIGHT + f"'{target}' decoded successfully as '{out_file}'.")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Upload error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="BlackSpammerBD CLI - Professional Edition",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Define subparser for 'start' command with alias '-start'
    subparsers.add_parser("start", aliases=["-start"], help="Generate a connection code")

    # Define subparser for 'connect' command with alias '-connect'
    connect_parser = subparsers.add_parser("connect", aliases=["-connect"], help="Verify the connection code")
    connect_parser.add_argument("code", help="The connection code to verify")

    # Define subparser for 'list' command with alias '-list'
    subparsers.add_parser("list", aliases=["-list"], help="List all files and directories")

    # Define subparser for 'download' command with alias '-download'
    download_parser = subparsers.add_parser("download", aliases=["-download"], help="Encode a file in Base64")
    download_parser.add_argument("file", help="Name of the file to encode")

    # Define subparser for 'upload' command with alias '-upload'
    upload_parser = subparsers.add_parser("upload", aliases=["-upload"], help="Decode a Base64 encoded file")
    upload_parser.add_argument("file", help="Name of the file to decode")

    args = parser.parse_args()

    if args.command in ["start", "-start"]:
        start_command()
    elif args.command in ["connect", "-connect"]:
        connect_command(args.code)
    elif args.command in ["list", "-list"]:
        list_command()
    elif args.command in ["download", "-download"]:
        download_command(args.file)
    elif args.command in ["upload", "-upload"]:
        upload_command(args.file)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
