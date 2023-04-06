import socket
import threading
import json
import base64
import os
import random
import pymongo
from getpass import getpass

# Establish a connection to the MongoDB server
mongo_client = pymongo.MongoClient("mongodb+srv://abhinoorbu:rkgy2pemFiKx3UWr@cluster0.o0mejie.mongodb.net/?retryWrites=true&w=majority")
chat_db = mongo_client["chat_db"]
users_col = chat_db["users"]

def handle_client(conn, addr, username):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        msg = conn.recv(1024).decode("utf-8")
        if not msg or msg.lower() == "exit":
            print(f"{username} has left the chat.")
            break
        print(f"[{username}] {msg}")

    conn.close()


def start_server(username, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen()
    print(f"[SERVER] Listening for connections on port {port}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, username))
        thread.start()

def connect_to_peer(peer_ip, port):
    peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer.connect((peer_ip, port))
    return peer

def chat_with_peer(peer, username):
    while True:
        msg = input("Type your message (or type 'exit' to leave the chat): ")
        if msg.lower() == "exit":
            print("Leaving chat...")
            break
        formatted_msg = f"{username}: {msg}"
        peer.send(formatted_msg.encode("utf-8"))


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
    server_thread = threading.Thread(target=start_server, args=(user['username'], user['port']))
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
                    chat_with_peer(peer_socket, user['username'])
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

