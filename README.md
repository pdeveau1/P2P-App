# Python CLI Peer-to-Peer Chat Application

This is a simple Python command-line interface (CLI) application that allows users to chat with each other using a peer-to-peer network. The application uses a MongoDB database to store user information, such as usernames, IP addresses, and ports. The app also saves chat history locally, and secures it using encryption. This app only works on a local network and not across the internet.

## Features

- User registration and login
- Search for other users
- Chat with other online users
- Leave chat and return to the main menu
- Saves chat history locally and securely

## Requirements

- Python 3.6 or higher
- MongoDB Server
- pymongo

## Installation

1. Make sure you have Python 3.6 or higher installed on your machine.

2. Install pymongo using pip:

```bash
pip install pymongo
```
3. Clone the repository or download the Python script.

## Running the Application
1. Open two terminal windows.

2. In each terminal window, navigate to the directory containing the Python script.

3. Run the Python script in both terminal windows:

```bash
python3 p2p_chat.py
```

4. In one terminal, register a new user or log in with an existing user.

5. In the other terminal, register a new user or log in with a different existing user.

6. Use the "search" command in either terminal to search for the other user by their username.

7. Use the "chat" command in either terminal to start a chat with the other user.

8. Type messages in both terminals to chat with each other.

9. Type "exit" to leave the chat and return to the main menu.

10. Use the "logout" command to log out of the application.

## Testing
To test the application, you can create multiple user accounts and chat between them. You can also search for users who are not online to see how the application behaves in such scenarios.

Make sure both users are online and connected to the same network to enable successful peer-to-peer communication.

## Troubleshooting
If you encounter issues, such as "Address already in use" or connection problems, please check your firewall settings and ensure that the required ports are open. If the error occurs where the application says "0.0.0.0" is already bound you have to close the terminal and restart the application. Please note, this application only works on a local network.