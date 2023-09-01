import socket
from interface import Interface
import json
import time
import threading

TEMPIP = "192.168.1.121"
PORT = 24635

class Client(object):
	def __init__(self):
		self.self_info = {}
		self.server_info = {}
		self.client_connection()


	def handle_lobby(self):
		self.user_interface = Interface(self.tcp_connection, self.self_info)

	def handle_initialization(self):
		if self.tcp_connection.recv(1024).decode("ascii") == "username_prompt":
			possible_username = input("Enter a nickname: ")
			while not possible_username: possible_username = input("Enter a nickname with characters: ")
			self.tcp_connection.sendall(possible_username.encode())
			received = self.tcp_connection.recv(1024).decode("ascii")

			while received == "too_long" or received == "already_taken":
				if received == "too_long":
					possible_username = input("Enter a shorter nickname: ")
				else:
					possible_username = input("Sorry, that username is taken. Enter a new one: ")
				while not possible_username: possible_username = input("Enter a nickname with characters: ")
				self.tcp_connection.sendall(possible_username.encode())
				received = self.tcp_connection.recv(1024).decode("ascii")
			self.self_info["username"] = possible_username


	def client_connection(self):

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.tcp_connection:
			self.tcp_connection.connect((TEMPIP, PORT))
			self.handle_initialization()
			self.handle_lobby()

if __name__ == "__main__":
	Client()