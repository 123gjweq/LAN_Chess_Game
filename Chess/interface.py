import pygame
from pygame.locals import *
from CONSTANTS import *
import threading
import time
import json
from lobby import Lobby
from game import Game


class Interface(object):
	def __init__(self, tcp_connection, self_info):
		self.window = pygame.display.set_mode((WIDTH, HEIGHT))
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("LAN Chess")
		pygame.display.set_icon(WN)
		self.tcp_connection = tcp_connection
		self.self_info = self_info
		self.current_display = Lobby(self.window, self.tcp_connection, self.self_info, self.clock)


		did_user_close = self.current_display.run() #lobby
		if did_user_close:
			self.close()
		else:
			self.current_display = Game(self.tcp_connection, self.window, self.clock)
			self.current_display.run() #chess game
			self.close()

	def close(self):
		self.tcp_connection.send(json.dumps({"command": "close"}).encode())