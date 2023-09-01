import pygame
from pygame.locals import *
from CONSTANTS import *
import threading
import time
import json


class Lobby(object):
	def __init__(self, window, tcp_connection, self_info, clock):
		self.running = True
		self.window = window
		self.tcp_connection = tcp_connection
		self.clock = clock
		self.self_info = self_info
		self.data = [] #all of the users' data is stored locally here
		self.user_usernames = {} #key: username, val: [username text object, username text position, user position].
		#note: useful for quickly converting a username to its text object and its position

		self.user_poses = {} #key: user position, val: username. converts a mouse position into a username quickly (for the purposes of selecting a user)
		self.local_data = {"clicked": "", "pending": False, "challenged": "", "challenges": set(), "challengebuttons": {}} #important data that is used often
		#button images. they switch between the highlighted image and the normal image depending on where the mouse is (see self.mouse_motion() method)
		self.challenge_button = CHALLENGE
		self.cancel_button = CANCEL

		self.message_queue = [] #holds important commands waiting to be sent to the server. first in first out.
		self.temporary_text = [] #temporary text list. each text object has a counter representing the # of frames it is displayed for
		self.pending_counter, self.pending_pointer = 30, 0 #used for the pending animation
		self.cancel_counter = 150 #displays cancel button that allows the user to cancel a challenge after 2.5 seconds (note: 150 frames, 60 frames/second)
		self.closed_window = False #this tells us whether or not the user has closed the connection so we can send the appropriate messages to the server.

	#a helper function to receive which updates our current challenge requests
	def update_challenges(self):
		for user in self.data:
			if user["username"] == self.self_info["username"]:
				self.local_data["pending"] = user["pending"]
				for challenge_request in user["challenges"]:
					if challenge_request not in self.local_data["challenges"] and challenge_request in self.user_usernames:
						self.local_data["challengebuttons"][challenge_request] = [self.user_usernames[challenge_request][2], ACCEPT, DECLINE]
				self.local_data["challenges"] = set(user["challenges"])
				break
		else: #otherwise, we are no longer in the lobby
			self.running = False


	def receive(self):
		while self.running: #we have a threaded connection with the server that ends when the main loop ends

			if not self.message_queue: #message_queue will send commands to the server when necessary (like when you challenge a user/cancel a challenge)
				self.tcp_connection.send(json.dumps({"command": "wait"}).encode())
			else:
				self.tcp_connection.send(self.message_queue.pop(0))

			received = json.loads(self.tcp_connection.recv(1024).decode())
			if type(received) == dict: #basically if we have received a command rather than the user data
				if received["response"] == "invalid":
					self.temporary_text.append([INVALIDCHALLENGE, (770, 340), 180])
				elif received["response"] == "transferring":
					self.running = False #move on to the game

			else: #we have received user data
				self.data = received #updates our client-side data
				self.update_challenges()



	#CHECKS IF THE MOUSE HAS CLICKED ON BUTTONS
	def check_click(self, mouse_pos):
		x, y = mouse_pos

		#accept/decline buttons for each user who has sent the client a challenge
		for user in self.local_data["challenges"]:
			user_challenge_info = self.local_data["challengebuttons"][user][0]

			#ACCEPT BUTTON
			lo_x, hi_x, lo_y, hi_y = user_challenge_info[0] * 80 + 65, user_challenge_info[0] * 80 + 115,\
			user_challenge_info[1] * 80 + 150, user_challenge_info[1] * 80 + 170
			if x >= lo_x and x <= hi_x and y >= lo_y and y <= hi_y:
				self.message_queue.append(json.dumps({"command": "accept", "user": user}).encode())
				return

			#DECLINE BUTTON
			lo_x, hi_x, lo_y, hi_y = user_challenge_info[0] * 80 + 65, user_challenge_info[0] * 80 + 115,\
			user_challenge_info[1] * 80 + 175, user_challenge_info[1] * 80 + 195
			if x >= lo_x and x <= hi_x and y >= lo_y and y <= hi_y:
				self.message_queue.append(json.dumps({"command": "decline", "user": user}).encode())
				return

		#handles clicking on the pending button along with resetting local pending variables
		if self.local_data["pending"]:
			if x >= 825 and x <= 925 and y >= 365 and y <= 407:
				self.message_queue.append(json.dumps({"command": "unchallenge", "user": self.local_data["challenged"]}).encode())
				#reset pending variables
				self.local_data["challenged"] = ""
				self.pending_counter, self.pending_pointer = 30, 0
				self.cancel_counter = 150
		else:
			#handles sending a challenge button if we have selected a user
			if x >= 775 and x <= 979 and y >= 250 and y <= 310 and self.local_data["clicked"]:
				self.message_queue.append(json.dumps({"command": "challenge", "user": self.local_data["clicked"]}).encode())
				self.local_data["challenged"] = self.local_data["clicked"]

			#selets or unselects a user
			x, y = ((x - 50) // 80, (y - 50) // 80)
			if (x, y) in self.user_poses:
				self.local_data["clicked"] = self.user_poses[(x, y)]
			else:
				self.local_data["clicked"] = ""


	#HIGHLIGHTS BUTTONS WHEN MOUSE IS OVER THEM
	def mouse_motion(self):
		x, y = pygame.mouse.get_pos()

		#handles the highlighting of the accept/decline buttons for each user who has sent a challenge
		for user in self.local_data["challenges"]:
			user_challenge_info = self.local_data["challengebuttons"][user][0]
			lo_x, hi_x, lo_y, hi_y = user_challenge_info[0] * 80 + 65, user_challenge_info[0] * 80 + 115,\
			user_challenge_info[1] * 80 + 150, user_challenge_info[1] * 80 + 170

			if x >= lo_x and x <= hi_x and y >= lo_y and y <= hi_y:
				self.local_data["challengebuttons"][user][1] = ACCEPTHIGHLIGHT
			else:
				self.local_data["challengebuttons"][user][1] = ACCEPT

			lo_x, hi_x, lo_y, hi_y = user_challenge_info[0] * 80 + 65, user_challenge_info[0] * 80 + 115,\
			user_challenge_info[1] * 80 + 175, user_challenge_info[1] * 80 + 195

			if x >= lo_x and x <= hi_x and y >= lo_y and y <= hi_y:
				self.local_data["challengebuttons"][user][2] = DECLINEHIGHLIGHT
			else:
				self.local_data["challengebuttons"][user][2] = DECLINE

		#handles the highlighting of the challenge button
		if x >= 775 and x <= 979 and y >= 250 and y <= 310:
			self.challenge_button = CHALLENGEHIGHLIGHT
		else:
			self.challenge_button = CHALLENGE
		#handles the highlighting of the cancel button
		if x >= 825 and x <= 925 and y >= 365 and y <= 407:
			self.cancel_button = CANCELHIGHLIGHT
		else:
			self.cancel_button = CANCEL

	def draw_background(self):
		self.window.fill(TAN)
		self.window.blit(FRAME, (10, 10))
		pygame.draw.rect(self.window, WOOD, pygame.Rect(47, 47, 646, 646))


		#DRAWS BOARD
		for x in range(8):
			for y in range(8):
				if (x % 2 and not y % 2) or (not x % 2 and y % 2):
					self.window.blit(DARK, (x * 80 + 50, y * 80 + 50))
				else:
					self.window.blit(LIGHT, (x * 80 + 50, y * 80 + 50))

		self.window.blit(LOBBYTEXT, (740, 50))
		self.window.blit(LOBBYTEXT2, (740, 100))

	def draw_users(self):
		#DRAWS USERS
		for user in self.data:
			if user["piece"] != "": #user is in the lobby

				if self.local_data["clicked"] == user["username"]: #if a user is selected (clicked on)
					current_square = (user["pos"][0] % 2 - user["pos"][1] % 2) % 2
					self.window.blit(HIGHLIGHTMAP[current_square], (user["pos"][0] * 80 + 50, user["pos"][1] * 80 + 50))
					self.window.blit(LOBBYTEXT3, (740, 200))
					self.window.blit(self.challenge_button, (775, 250))

				self.window.blit(PIECEMAP[user["piece"]], (user["pos"][0] * 80 + 50, user["pos"][1] * 80 + 50))
				if user["username"] not in self.user_usernames:
					text = FONT.render(user["username"], True, RED, BLACK)
					self.user_usernames[user["username"]] = [text,\
					text.get_rect(center=(user["pos"][0] * 80 + 90, user["pos"][1] * 80 + 121)), user["pos"]]
					self.user_poses[tuple(user["pos"])] = user["username"]

				self.window.blit(self.user_usernames[user["username"]][0], self.user_usernames[user["username"]][1])

		for user in self.data:
			#draws extra challenge surfaces (text, accept button, deny button) if the user has a current challenge sent for us
			if user["username"] in self.local_data["challenges"]:
				self.window.blit(REQUEST, (user["pos"][0] * 80 + 3, user["pos"][1] * 80 + 130))
				self.window.blit(self.local_data["challengebuttons"][user["username"]][1], (user["pos"][0] * 80 + 65, user["pos"][1] * 80 + 150))
				self.window.blit(self.local_data["challengebuttons"][user["username"]][2], (user["pos"][0] * 80 + 65, user["pos"][1] * 80 + 175))


	#DRAWS EXTRA TEXT AND BUTTONS
	def draw_extra_text(self):
		#draws temporary text, such as "you can't challenge yourself"
		for text in self.temporary_text:
			if not text[2]:
				self.temporary_text.remove(text)
			self.window.blit(text[0], text[1])
			text[2] -= 1

		#if we are currently pending, we will draw the pending animation + cancel button
		if self.local_data["pending"]:
			if not self.pending_counter:
				self.pending_pointer = (self.pending_pointer + 1) % 3
				self.pending_counter = 30 #display each pending message every half second (60 frames/second)
			self.window.blit(PENDINGANIMATION[self.pending_pointer], (840, 360))
			self.pending_counter -= 1
			if self.cancel_counter:
				self.cancel_counter -= 1
			else:
				self.window.blit(self.cancel_button, (825, 385))


	#main loop
	def run(self):
		threading.Thread(target = self.receive).start()

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					self.closed_window = True
				if event.type == pygame.MOUSEBUTTONUP:
					self.check_click(pygame.mouse.get_pos())

			self.mouse_motion()
			self.draw_background()
			self.draw_users()
			self.draw_extra_text()

			pygame.display.flip()
			self.clock.tick(FPS) #Frames Per Second = 60

		time.sleep(.15)
		return self.closed_window
		#after we have closed out of the game, program sends closing message to the server