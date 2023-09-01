import socket
import threading
import json
import time
import random
from CONSTANTS import *

class ThreadedClient(object):
	def __init__(self, connection_address, server_data):
		self.connection, self.address = connection_address


		self.server_data = server_data
		self.user_info = {"username": "", "challenges": [], "pos": (), "piece": "", "pending": False, "gamenumber": None, "iswhite": None, "turn": 1}
		self.server_data.users.append(self.user_info)


		threading.Thread(target = self.threaded_connection).start()

	def handle_game(self):
		self.gamenumber = self.user_info["gamenumber"] #shortcut for this value
		self.iswhite = self.user_info["iswhite"]
		received = json.loads(self.connection.recv(1024))
		self.connection.sendall(json.dumps({"white": self.user_info["iswhite"], "turn": self.user_info["turn"]}).encode())
		while True:
			received = json.loads(self.connection.recv(1024))
			print(received)
			if received["command"] == "close":
				break
			elif received["command"] == "move":
				self.server_data.games[self.gamenumber][1 - self.iswhite].append({"command": "move", "from": received["from"], "to": received["to"]})
			elif received["command"] == "kingside": #special move
				self.server_data.games[self.gamenumber][1 - self.iswhite].append(received)
			elif received["command"] == "queenside":
				self.server_data.games[self.gamenumber][1 - self.iswhite].append(received)

			if not self.server_data.games[self.gamenumber][self.iswhite]:
				self.connection.send(json.dumps({}).encode())
			else:
				self.connection.sendall(json.dumps(self.server_data.games[self.gamenumber][self.iswhite].pop(0)).encode())
			time.sleep(.1)
		

	def handle_lobby(self):
		self.pos = (random.randrange(8), random.randrange(8))
		while self.pos in self.server_data.user_poses:
			self.pos = (random.randrange(8), random.randrange(8))
		self.server_data.user_poses.add(self.pos)
		self.piece = random.choice(ALLPIECES)

		self.user_info["pos"] = self.pos
		self.user_info["piece"] = self.piece

		while True:
			received = json.loads(self.connection.recv(1024))
			if self.user_info not in self.server_data.users:
				self.connection.sendall(json.dumps({"response": "transferring"}).encode())
				return False

			print(received)
			if received["command"] == "close":
				return True
			elif received["command"] == "challenge":
				if received["user"] == self.user_info["username"]:
					self.connection.sendall(json.dumps({"response": "invalid"}).encode())
				else:
					self.connection.sendall(json.dumps({"response": "pending"}).encode())
					self.user_info["pending"] = received["user"]
					for user in self.server_data.users:
						if user["username"] == received["user"]:
							user["challenges"].append(self.user_info["username"])
			elif received["command"] == "unchallenge":
				self.connection.sendall(json.dumps({"response": "ok"}).encode())
				self.user_info["pending"] = False
				for user in self.server_data.users:
					if user["username"] == received["user"]:
						user["challenges"].remove(self.user_info["username"])
			elif received["command"] == "decline":
				self.connection.sendall(json.dumps({"response": "ok"}).encode())
				self.user_info["challenges"].remove(received["user"])
				for user in self.server_data.users:
					if user["username"] == received["user"]:
						user["pending"] = False
			elif received["command"] == "accept":
				self.connection.sendall(json.dumps({"response": "transferring"}).encode())
				self.user_info["gamenumber"] = self.server_data.next_game
				self.user_info["iswhite"] = random.choice([0, 1])
				self.server_data.users.remove(self.user_info)

				for user in self.server_data.users:
					if user["username"] == received["user"]:
						user["gamenumber"] = self.server_data.next_game
						user["iswhite"] = 1 - self.user_info["iswhite"]
						self.server_data.users.remove(user)
				self.server_data.next_game += 1
				return False
			else:
				if self.user_info["pending"] and self.user_info["pending"] not in self.server_data.usernames:
					self.user_info["pending"] = ""
				self.connection.sendall(json.dumps(self.server_data.users).encode())
			time.sleep(.1)

	def handle_initialization(self):
		print(f"Connected by {self.address}")
		self.connection.send(b"username_prompt")
		self.username = self.connection.recv(1024).decode("ascii")
		while len(self.username) > MAXUSERNAME or self.username in self.server_data.usernames:
			if len(self.username) > MAXUSERNAME:
				self.connection.send(b"too_long")
			else:
				self.connection.send(b"already_taken")
			self.username = self.connection.recv(1024).decode("ascii")


		self.user_info["username"] = self.username
		self.server_data.usernames.add(self.username)
		self.connection.send(b"good_to_go")


	#the server's threaded conncetion with a client
	def threaded_connection(self):
		with self.connection:
			self.handle_initialization() #get the username and stuff
			did_close = self.handle_lobby()
			if not did_close:
				self.handle_game()
		if self.user_info in self.server_data.users:
			self.server_data.users.remove(self.user_info)