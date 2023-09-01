#a class to keep track of server data
from CONSTANTS import *
from copy import deepcopy

class ServerData(object):


	def __init__(self):
		self.users = []
		self.usernames = set()
		self.user_poses = set()
		self.games = [[[], []] for i in range(32)]
		self.next_game = 0