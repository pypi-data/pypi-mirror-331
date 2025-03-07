#!/usr/bin/env python3
"""
CLI Module for blackspammerbd_bsb Package

This module provides the following commands:
  - start: Generate a secret connection code (if not already created) and start
           a TCP server to accept connections from trusted devices.
  - connect: Connect to a remote server using the secret connection code.
             Once connected, an interactive session supports the commands:
             list, download <filename>, upload <filename>, and exit.
"""

import os
import sys
import random
import base64
import argparse
import socket
from colorama import Fore, Style

# Hidden file for storing the secret connection code
SECRET_CODE_FILE = ".connection_code"
DEFAULT_PORT = 9000

def generate_secret_code() -> str:
    """Generate an 8-digit secret connection code."""
    return ''.join(str(random.randint(0, 9)) for _ in range(8))

def save_secret_code() -> None:
    """Generate and save the secret connection code to a hidden file with restricted permissions."""
    code = generate_secret_code()
    try:
        with open(SECRET_CODE_FILE, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            os.chmod(SECRET_CODE_FILE, 0o600)
        except Exception:
            pass
        print(Fore.GREEN + "Secret connection code generated and stored securely.")
        print(Fore.CYAN + "Share this code only with trusted devices.")
        print(Fore.CYAN + f"Secret Code: {code}")
    except Exception as e:
        print(Fore.RED + f"Error saving secret code: {e}")

def load_secret_code() -> str:
    """Load the secret connection code from the hidden file."""
    if not os.path.exists(SECRET_CODE_FILE):
        return ""
    try:
        with open(SECRET_CODE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(Fore.RED + f"Error reading secret code: {e}")
        return ""

def start_server(port: int) -> None:
    """Start the TCP server to accept client connections and handle commands interactively."""
    code = load_secret_code()
    if not code:
        print(Fore.RED + "No secret connection code found. Please run 'bsb start' first to generate it.")
        return

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_sock.bind(('', port))
        server_sock.listen(1)
    except Exception as e:
        print(Fore.RED + f"Error starting server: {e}")
        return

    print(Fore.CYAN + f"Server listening on port {port} for incoming connections...")
    conn, addr = server_sock.accept()
    print(Fore.CYAN + f"Connection established from {addr}")

    # Authenticate the client by verifying the secret code
    try:
        received = conn.recv(1024).decode().strip()
    except Exception as e:
        print(Fore.RED + f"Error receiving data: {e}")
        conn.close()
        server_sock.close()
        return

    if received != code:
        conn.sendall("ERROR: Invalid connection code.\n".encode())
        print(Fore.RED + "Invalid connection code received. Closing connection.")
        conn.close()
        server_sock.close()
        return
    else:
        conn.sendall("OK\n".encode())
        print(Fore.GREEN + "Client authenticated successfully.")

    # Interactive session for file transfer commands
    print(Fore.CYAN + "Entering interactive session. Available commands: list, download <filename>, upload <filename> <data>, exit")
    while True:
        try:
            data = conn.recv(4096).decode().strip()
            if not data:
                break
            parts = data.split(" ", 2)
            command = parts[0].lower()
            if command == "list":
                items = os.listdir('.')
                response = "\n".join(items) if items else "No files found."
                conn.sendall((response + "\n").encode())
            elif command == "download":
                if len(parts) < 2:
                    conn.sendall("ERROR: Filename not provided.\n".encode())
                    continue
                filename = parts[1]
                if not os.path.exists(filename):
                    conn.sendall(f"ERROR: File '{filename}' not found.\n".encode())
                    continue
                try:
                    with open(filename, "rb") as f:
                        content = f.read()
                    encoded = base64.b64encode(content).decode()
                    conn.sendall(f"DATA {encoded}\n".encode())
                except Exception as e:
                    conn.sendall(f"ERROR: Failed to read file: {e}\n".encode())
            elif command == "upload":
                if len(parts) < 3:
                    conn.sendall("ERROR: Filename or data not provided.\n".encode())
                    continue
                filename = parts[1]
                b64data = parts[2]
                try:
                    file_data = base64.b64decode(b64data)
                    out_filename = "uploaded_" + filename
                    with open(out_filename, "wb") as f:
                        f.write(file_data)
                    conn.sendall(f"File '{filename}' uploaded as '{out_filename}'.\n".encode())
                except Exception as e:
                    conn.sendall(f"ERROR: Failed to upload file: {e}\n".encode())
            elif command == "exit":
                conn.sendall("Goodbye!\n".encode())
                break
            else:
                conn.sendall("ERROR: Unknown command.\n".encode())
        except Exception as e:
            conn.sendall(f"ERROR: {e}\n".encode())
    conn.close()
    server_sock.close()
    print(Fore.CYAN + "Connection closed. Server shutting down.")

def start_client(provided_code: str, host: str, port: int) -> None:
    """Connect to the server using the provided secret code and start an interactive session."""
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((host, port))
    except Exception as e:
        print(Fore.RED + f"Error connecting to server: {e}")
        return

    # Send the connection code for authentication
    client_sock.sendall((provided_code + "\n").encode())
    try:
        response = client_sock.recv(1024).decode().strip()
    except Exception as e:
        print(Fore.RED + f"Error receiving authentication response: {e}")
        client_sock.close()
        return

    if response != "OK":
        print(Fore.RED + f"Authentication failed: {response}")
        client_sock.close()
        return

    print(Fore.GREEN + "Authenticated successfully. Entering interactive session.")
    print(Fore.CYAN + "Available commands: list, download <filename>, upload <filename>, exit")
    while True:
        try:
            command = input(">> ").strip()
            if not command:
                continue
            if command.lower().startswith("upload"):
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print(Fore.RED + "Error: Filename not provided for upload.")
                    continue
                filename = parts[1]
                if not os.path.exists(filename):
                    print(Fore.RED + f"Error: File '{filename}' not found.")
                    continue
                try:
                    with open(filename, "rb") as f:
                        content = f.read()
                    b64data = base64.b64encode(content).decode()
                    # Send command in the format: upload <filename> <b64data>
                    full_command = f"upload {filename} {b64data}"
                    client_sock.sendall((full_command + "\n").encode())
                except Exception as e:
                    print(Fore.RED + f"Error reading file: {e}")
                    continue
            else:
                client_sock.sendall((command + "\n").encode())
            data = client_sock.recv(4096).decode()
            if data.startswith("DATA "):
                # Response to a download command: decode and save the file
                encoded = data[5:].strip()
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print(Fore.RED + "Error: Filename missing for download.")
                    continue
                filename = parts[1]
                out_filename = "downloaded_" + filename
                try:
                    file_data = base64.b64decode(encoded)
                    with open(out_filename, "wb") as f:
                        f.write(file_data)
                    print(Fore.GREEN + f"File '{filename}' downloaded and saved as '{out_filename}'.")
                except Exception as e:
                    print(Fore.RED + f"Error decoding file data: {e}")
            else:
                print(data.strip())
            if command.lower() == "exit":
                break
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
            break
    client_sock.close()

def main():
    parser = argparse.ArgumentParser(
        description="BlackSpammerBD_BSB CLI - Professional Edition for Secure Device Connection and File Transfer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Server mode: 'start' command
    start_parser = subparsers.add_parser("start", aliases=["-start"],
                                          help="Generate secret connection code (if needed) and start server mode")
    start_parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT,
                              help="Port to listen on (default: 9000)")

    # Client mode: 'connect' command
    connect_parser = subparsers.add_parser("connect", aliases=["-connect"],
                                            help="Connect to a remote server using the secret connection code")
    connect_parser.add_argument("code", help="Secret connection code for authentication")
    connect_parser.add_argument("--host", "-H", required=True,
                                help="Server IP address")
    connect_parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT,
                                help="Server port (default: 9000)")

    args = parser.parse_args()

    if args.command in ["start", "-start"]:
        if not os.path.exists(SECRET_CODE_FILE):
            save_secret_code()
        else:
            print(Fore.CYAN + "Secret connection code already exists.")
        start_server(args.port)
    elif args.command in ["connect", "-connect"]:
        start_client(args.code, args.host, args.port)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
