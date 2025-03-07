#!/usr/bin/env python3
"""
CLI Module for blackspammerbd_tool Package

এই মডিউলটি নিরাপদ ডিভাইস সংযোগ ও ফাইল ট্রান্সফার প্রদান করে।
উপলব্ধ কমান্ডসমূহ:
• start   : সিক্রেট কোড (অব্যবহৃত থাকলে) তৈরি করে TCP সার্ভার চালু করে।
• connect : সিক্রেট কোড ব্যবহার করে রিমোট সার্ভারে সংযোগ করে।
ব্যবহার:
   bsb connect <secret_code> [host] [--port <port>]
(যদি host প্রদান না করা হয়, তাহলে সার্ভারের আইপি ঠিকানা টার্মাক্সে দেখানো হবে)
ইন্টারেক্টিভ মোডে কমান্ডসমূহ: list, download <filename>, upload <filename>, exit
"""

import os
import sys
import random
import base64
import argparse
import socket
from colorama import Fore, Style

# সিক্রেট কোড সংরক্ষণের ফাইল
SECRET_CODE_FILE = ".connection_code"
DEFAULT_PORT = 9000

def generate_secret_code() -> str:
    """৮-সংখ্যার সিক্রেট কোড তৈরি করে।"""
    return ''.join(str(random.randint(0, 9)) for _ in range(8))

def save_secret_code() -> None:
    """সিক্রেট কোড তৈরি করে এবং সীমিত পারমিশনে একটি হিডেন ফাইলে সংরক্ষণ করে।"""
    code = generate_secret_code()
    try:
        with open(SECRET_CODE_FILE, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            os.chmod(SECRET_CODE_FILE, 0o600)
        except Exception:
            pass
        print(Fore.GREEN + "সিক্রেট কোড সফলভাবে তৈরি ও সংরক্ষিত।")
        print(Fore.CYAN + "এই কোডটি শুধুমাত্র বিশ্বাসযোগ্য ডিভাইসের সাথে শেয়ার করুন।")
        print(Fore.CYAN + f"Secret Code: {code}")
    except Exception as e:
        print(Fore.RED + f"সিক্রেট কোড সংরক্ষণে সমস্যা: {e}")

def load_secret_code() -> str:
    """হিডেন ফাইল থেকে সিক্রেট কোড লোড করে।"""
    if not os.path.exists(SECRET_CODE_FILE):
        return ""
    try:
        with open(SECRET_CODE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(Fore.RED + f"সিক্রেট কোড পড়তে সমস্যা: {e}")
        return ""

def get_server_ip() -> str:
    """সার্ভারের কার্যকর আইপি ঠিকানা স্বয়ংক্রিয়ভাবে নির্ধারণ করে।"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # এক্সটার্নাল DNS সার্ভারের সাথে কানেক্ট করে সঠিক আইপি পাওয়া যায়
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"
    return ip

def start_server(port: int) -> None:
    """TCP সার্ভার চালু করে, ক্লায়েন্ট কানেকশন গ্রহণ ও ইন্টারেক্টিভ মোড পরিচালনা করে।"""
    code = load_secret_code()
    if not code:
        print(Fore.RED + "সিক্রেট কোড পাওয়া যায়নি। প্রথমে 'bsb start' কমান্ড রান করুন।")
        return

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_sock.bind(('', port))
        server_sock.listen(1)
    except Exception as e:
        print(Fore.RED + f"সার্ভার চালু করতে সমস্যা: {e}")
        return

    # সার্ভারের আইপি ঠিকানা স্বয়ংক্রিয়ভাবে বের করে প্রদর্শন
    server_ip = get_server_ip()
    print(Fore.CYAN + f"Server IP Address: {server_ip}")
    print(Fore.CYAN + f"পোর্ট {port} এ ইনকামিং কানেকশনের জন্য অপেক্ষমান...")

    conn, addr = server_sock.accept()
    print(Fore.CYAN + f"কানেকশন প্রতিষ্ঠিত হয়েছে: {addr}")

    # ক্লায়েন্টের সিক্রেট কোড যাচাই
    try:
        received = conn.recv(1024).decode().strip()
    except Exception as e:
        print(Fore.RED + f"ডাটা গ্রহণে সমস্যা: {e}")
        conn.close()
        server_sock.close()
        return

    if received != code:
        conn.sendall("ERROR: Invalid connection code.\n".encode())
        print(Fore.RED + "ভুল সিক্রেট কোড। কানেকশন বন্ধ করা হচ্ছে।")
        conn.close()
        server_sock.close()
        return
    else:
        conn.sendall("OK\n".encode())
        print(Fore.GREEN + "ক্লায়েন্ট সফলভাবে অথেনটিকেট হয়েছে।")

    # ফাইল ট্রান্সফারের জন্য ইন্টারেক্টিভ সেশন
    print(Fore.CYAN + "ইন্টারেক্টিভ মোডে প্রবেশ করা হচ্ছে। উপলব্ধ কমান্ড: list, download <filename>, upload <filename>, exit")
    while True:
        try:
            data = conn.recv(4096).decode().strip()
            if not data:
                break
            parts = data.split(" ", 2)
            command = parts[0].lower()
            if command == "list":
                items = os.listdir('.')
                response = "\n".join(items) if items else "কোন ফাইল পাওয়া যায়নি।"
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
    print(Fore.CYAN + "কানেকশন বন্ধ হয়েছে। সার্ভার শাটডাউন।")

def start_client(provided_code: str, host: str, port: int) -> None:
    """সিক্রেট কোড ব্যবহার করে সার্ভারে সংযোগ স্থাপন করে ইন্টারেক্টিভ সেশন শুরু করে।"""
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((host, port))
    except Exception as e:
        print(Fore.RED + f"সার্ভারে কানেক্ট করতে সমস্যা: {e}")
        return

    # অথেনটিকেশনের জন্য সিক্রেট কোড পাঠানো হচ্ছে
    client_sock.sendall((provided_code + "\n").encode())
    try:
        response = client_sock.recv(1024).decode().strip()
    except Exception as e:
        print(Fore.RED + f"অথেনটিকেশন রেসপন্স নিতে সমস্যা: {e}")
        client_sock.close()
        return

    if response != "OK":
        print(Fore.RED + f"অথেনটিকেশন ব্যর্থ: {response}")
        client_sock.close()
        return

    print(Fore.GREEN + "অথেনটিকেট হয়েছে। ইন্টারেক্টিভ মোডে প্রবেশ করা হচ্ছে।")
    print(Fore.CYAN + "উপলব্ধ কমান্ড: list, download <filename>, upload <filename>, exit")
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
                    full_command = f"upload {filename} {b64data}"
                    client_sock.sendall((full_command + "\n").encode())
                except Exception as e:
                    print(Fore.RED + f"Error reading file: {e}")
                    continue
            else:
                client_sock.sendall((command + "\n").encode())
            data = client_sock.recv(4096).decode()
            if data.startswith("DATA "):
                # Download response: decode and save the file
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
        description="BlackSpammerBD_Tools CLI - Professional Edition for Secure Device Connection and File Transfer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # সার্ভার মোড: 'start' কমান্ড
    start_parser = subparsers.add_parser("start", aliases=["-start"],
                                         help="সিক্রেট কোড তৈরি (যদি না থাকে) এবং সার্ভার মোড চালু করে")
    start_parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT,
                              help="লিসেন করার পোর্ট (ডিফল্ট: 9000)")

    # ক্লায়েন্ট মোড: 'connect' কমান্ড
    connect_parser = subparsers.add_parser("connect", aliases=["-connect"],
                                           help="সিক্রেট কোড ব্যবহার করে রিমোট সার্ভারে সংযোগ করে")
    connect_parser.add_argument("code", help="অথেনটিকেশনের জন্য সিক্রেট কোড")
    connect_parser.add_argument("host", nargs="?", default=None,
                                help="সার্ভারের আইপি ঠিকানা (প্রদান না করলে সার্ভার থেকে কপি করুন)")
    connect_parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT,
                                help="সার্ভারের পোর্ট (ডিফল্ট: 9000)")

    args = parser.parse_args()

    if args.command in ["start", "-start"]:
        if not os.path.exists(SECRET_CODE_FILE):
            save_secret_code()
        else:
            print(Fore.CYAN + "সিক্রেট কোড পূর্বেই বিদ্যমান।")
        start_server(args.port)
    elif args.command in ["connect", "-connect"]:
        if not args.host:
            args.host = input("Enter server IP address: ").strip()
        start_client(args.code, args.host, args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
