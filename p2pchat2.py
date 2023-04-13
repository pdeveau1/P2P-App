# EC530 P2P Chat App Python - Paige DeVeau and Abhinoor Singh 2023

import socket
import threading
import json
import base64
import os
import random
import pymongo
import hashlib
from getpass import getpass
from cryptography.fernet import Fernet

# Establish a connection to the MongoDB server
mongo_client = pymongo.MongoClient("mongodb+srv://abhinoorbu:rkgy2pemFiKx3UWr@cluster0.o0mejie.mongodb.net/?retryWrites=true&w=majority")
chat_db = mongo_client["chat_db"]
users_col = chat_db["users"]


def load_chat_history(auth_hash):
    try:
        with open(f"{auth_hash}.json", "r") as f:
            encrypted_data = f.read()
            decrypted_data = decrypt_data(encrypted_data.encode())
            chat_history = json.loads(decrypted_data)
            return chat_history
    except FileNotFoundError:
        return {}


def save_chat_history(auth_hash, peer_username, message):
    chat_history = load_chat_history(auth_hash)
    if peer_username not in chat_history:
        chat_history[peer_username] = []

    chat_history[peer_username].append(message)
    encrypted_data = encrypt_data(json.dumps(chat_history).encode())
    with open(f"{auth_hash}.json", "w") as f:
        f.write(encrypted_data.decode())


def generate_key(auth_hash):
    return base64.urlsafe_b64encode(hashlib.sha256(auth_hash.encode()).digest())


def encrypt_data(data):
    key = generate_key(auth_hash)
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(data)


def decrypt_data(encrypted_data):
    key = generate_key(auth_hash)
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_data)


def handle_client(conn, addr, username, auth_hash):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg = conn.recv(1024).decode("utf-8")
        if not msg or msg.lower() == "exit":
            print(f"{username} has left the chat.")
            break

        sender_username = msg.split(": ")[0]
        save_chat_history(auth_hash, sender_username, msg)
        print(f"[{username}] {msg}")

    conn.close()


def start_server(username, auth_hash, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen()
    print(f"[SERVER] Listening for connections on port {port}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, username, auth_hash))
        thread.start()


def connect_to_peer(peer_ip, port):
    peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer.connect((peer_ip, port))
    return peer


def chat_with_peer(peer, username, peer_username):
    global auth_hash
    chat_history = load_chat_history(auth_hash)

    if peer_username in chat_history:
        print("Chat history:")
        for message in chat_history[peer_username]:
            print(message)
    else:
        print(f"No previous chat history with {peer_username}.")

    while True:
        msg = input("Type your message (or type 'exit' to leave the chat): ")
        if msg.lower() == "exit":
            print("Leaving chat...")
            break
        formatted_msg = f"{username}: {msg}"
        peer.send(formatted_msg.encode("utf-8"))
        save_chat_history(auth_hash, peer_username, formatted_msg)


def login():
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    auth_hash = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
    user = users_col.find_one({"Id": auth_hash})
    if user:
        print("Login successful.")
        return auth_hash, user
    else:
        print("Invalid username or password.")
        return None, None


def register():
    while True:
        username = input("Enter a username: ")
        password = getpass("Enter a password: ")
        auth_hash = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
        if users_col.find_one({"username": username}):
            print("Username already exists. Choose another one.")
            continue
        else:
            ip_address = socket.gethostbyname(socket.gethostname())
            random_port = random.randint(10000, 65535)
            user = {"Id": auth_hash, "username": username, "ip_address": ip_address, "port": random_port}
            users_col.insert_one(user)
            print("Registration successful.")
            return auth_hash, user


def main():
    global auth_hash
    while True:
        print("\nCommands:\n1. Login\n2. Register\n")
        choice = input("Enter your choice (login/register): ").lower()
        if choice == "login":
            auth_hash, user = login()
            if user:
                break
        elif choice == "register":
            auth_hash, user = register()
            break
        else:
            print("Invalid choice. Try again.")

    print("\nWelcome, {}!".format(user['username']))
    server_thread = threading.Thread(target=start_server, args=(user['username'], auth_hash, user['port']))
    server_thread.start()

    while True:
        print("\nCommands:\n1. Search\n2. Chat\n3. Logout\n")
        choice = input("Enter your choice (search/chat/logout): ").lower()
        if choice == "search":
            search_username = input("Enter the username to search: ")
            peer = users_col.find_one({"username": search_username})
            if peer:
                print(f"User found: {peer['username']} (IP: {peer['ip_address']} - Port: {peer['port']})")
            else:
                print("User not found.")
        elif choice == "chat":
            peer_username = input("Enter the username of the person you want to chat with: ")
            peer = users_col.find_one({"username": peer_username})
            if peer:
                print(f"Connecting to {peer['username']}...")
                try:
                    peer_socket = connect_to_peer(peer['ip_address'], peer['port'])
                    print(f"Connected to {peer['username']}. Start chatting!")
                    chat_with_peer(peer_socket, user['username'], peer_username)
                except ConnectionRefusedError:
                    print(f"{peer['username']} is offline.")
            else:
                print("User not found.")

        elif choice == "logout":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")

    print("Goodbye!")
    os._exit(0)


if __name__ == "__main__":
    main()
