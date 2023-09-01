import pygame
from pygame.locals import *
from CONSTANTS import *
import threading
import time
import json
from pieces import *

class Game(object):
	def __init__(self, tcp_connection, window, clock):
		self.tcp_connection = tcp_connection
		self.window = window
		self.clock = clock
		self.board = [
					[Rook("B"), Knight("B"), Bishop("B"), Queen("B"), King("B"), Bishop("B"), Knight("B"), Rook("B")],
					[Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B")],
					[0, 0, 0, 0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0, 0, 0, 0],
					[0, 0, 0, 0, 0, 0, 0, 0],
					[Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W")],
					[Rook("W"), Knight("W"), Bishop("W"), Queen("W"), King("W"), Bishop("W"), Knight("W"), Rook("W")],
					]
		self.iswhite = -1
		self.turn = -1
		self.running = True
		self.message_queue = []
		self.clicked = ()
		self.dragging = ()
		self.legal_moves = []

	def receive(self):
		self.tcp_connection.send(json.dumps({"command": "goingtogame"}).encode())
		received = json.loads(self.tcp_connection.recv(1024).decode())
		self.iswhite = received["white"]
		self.turn = received["turn"]
		if not self.iswhite:
			for row in self.board:
				row.reverse()
			for row in check_board:
				row.reverse()
			check_board.reverse()
			self.board.reverse()
		self.tcp_connection.send(json.dumps({"command": "ok"}).encode())

		while self.running: #we have a threaded connection with the server that ends when the main loop ends
			received = json.loads(self.tcp_connection.recv(1024).decode())
			if received:
				if received["command"] == "move":
					self.turn = 1 - self.turn
					from_pos = received["from"]
					to_pos = received["to"]
					piecex, piecey = 7 - from_pos[0], 7 - from_pos[1]
					x, y = 7 - to_pos[0], 7 - to_pos[1]
					self.board[piecex][piecey].move_number += 1
					self.board[piecex][piecey], self.board[x][y] = 0, self.board[piecex][piecey]
					while Piece.reversing: pass #if we just so happen to be reversing check_board, we wait for that process to be finished
					check_board[piecex][piecey].move_number += 1
					check_board[piecex][piecey], check_board[x][y] = 0, check_board[piecex][piecey]
					self.clicked, self.dragging = (), ()
				elif received["command"] == "kingside" or received["command"] == "queenside":
					self.turn = 1 - self.turn
					king_from_x, king_from_y = 7 - received["kingfrom"][0], 7 - received["kingfrom"][1]
					king_to_x, king_to_y = 7 - received["kingto"][0], 7 - received["kingto"][1]
					rook_from_x, rook_from_y = 7 - received["rookfrom"][0], 7 - received["rookfrom"][1]
					rook_to_x, rook_to_y = 7 - received["rookto"][0], 7 - received["rookto"][1]
					self.board[king_from_x][king_from_y].move_number += 1
					self.board[king_from_x][king_from_y], self.board[king_to_x][king_to_y] = 0, self.board[king_from_x][king_from_y]
					self.board[rook_from_x][rook_from_y], self.board[rook_to_x][rook_to_y] = 0, self.board[rook_from_x][rook_from_y]
					check_board[king_from_x][king_from_y].move_number += 1
					while Piece.reversing: pass
					check_board[king_from_x][king_from_y], check_board[king_to_x][king_to_y] = 0, check_board[king_from_x][king_from_y]
					check_board[rook_from_x][rook_from_y], check_board[rook_to_x][rook_to_y] = 0, check_board[rook_from_x][rook_from_y]
					self.clicked, self.dragging = (), ()


			if not self.message_queue:
				self.tcp_connection.send(json.dumps({"command": "wait"}).encode())
			else:
				self.tcp_connection.send(self.message_queue.pop(0))
			time.sleep(.1)


	def handle_queenside(self, pos):
		x, y = pos
		if self.iswhite:
			king_pos = 4
			rook_pos = 0
			direction = -1
		else:
			king_pos = 3
			rook_pos = 7
			direction = 1
		self.board[7][king_pos].move_number += 1
		self.board[7][king_pos], self.board[7][king_pos + 2 * direction] = 0, self.board[7][king_pos]
		self.board[7][rook_pos], self.board[7][rook_pos - 3 * direction] = 0, self.board[7][rook_pos]
		check_board[7][king_pos].move_number += 1
		check_board[7][king_pos], check_board[7][king_pos + 2 * direction] = 0, check_board[7][king_pos]
		check_board[7][rook_pos], check_board[7][rook_pos - 3 * direction] = 0, check_board[7][rook_pos]
		self.clicked, self.legal_moves = (), []
		self.turn = 1 - self.turn
		self.message_queue.append(json.dumps(
			{"command": "queenside",
			"kingfrom": (7, king_pos),
			"kingto": (7, king_pos + 2 * direction),
			"rookfrom": (7, rook_pos),
			"rookto": (7, rook_pos - 3 * direction)}
			).encode())

	def handle_kingside(self, pos):
		x, y = pos
		if self.iswhite:
			king_pos = 4
			rook_pos = 7
			direction = 1
		else:
			king_pos = 3
			rook_pos = 0
			direction = -1
		self.board[7][king_pos].move_number += 1
		self.board[7][king_pos], self.board[7][king_pos + 2 * direction] = 0, self.board[7][king_pos]
		self.board[7][rook_pos], self.board[7][rook_pos - 2 * direction] = 0, self.board[7][rook_pos]
		check_board[7][king_pos].move_number += 1
		check_board[7][king_pos], check_board[7][king_pos + 2 * direction] = 0, check_board[7][king_pos]
		check_board[7][rook_pos], check_board[7][rook_pos - 2 * direction] = 0, check_board[7][rook_pos]
		self.clicked, self.legal_moves = (), []
		self.turn = 1 - self.turn
		self.message_queue.append(json.dumps(
			{"command": "kingside",
			"kingfrom": (7, king_pos),
			"kingto": (7, king_pos + 2 * direction),
			"rookfrom": (7, rook_pos),
			"rookto": (7, rook_pos - 2 * direction)}
			).encode())


	def move_piece(self, click_pos):
		x, y = click_pos
		piecex, piecey = self.clicked
		#move the real board
		self.board[piecex][piecey].move_number += 1
		self.board[piecex][piecey], self.board[x][y] = 0, self.board[piecex][piecey]

		#move the check board (see pieces.py)
		check_board[piecex][piecey].move_number += 1
		check_board[piecex][piecey], check_board[x][y] = 0, check_board[piecex][piecey]

		#tell the server that we have moved and reset some variables
		self.clicked, self.legal_moves = (), []
		self.turn = 1 - self.turn
		self.message_queue.append(json.dumps({"command": "move", "from": (piecex, piecey), "to": (x, y)}).encode())

	def mouse_handling(self, is_down):
		y, x = pygame.mouse.get_pos()
		y, x = (y - 50) // 80, (x - 50) // 80
		if is_down:
			if x >= 0 and x < 8 and y >= 0 and y < 8:
				if (x, y) in self.legal_moves:
					self.move_piece((x, y))
				elif (x, y, "kingside") in self.legal_moves:
					self.handle_kingside((x, y))
				elif (x, y, "queenside") in self.legal_moves:
					self.handle_queenside((x, y))
				elif self.board[x][y]:
					self.dragging = (x, y)
					self.clicked = (x, y)
					if (self.board[x][y].color == "W") == bool(self.iswhite) and self.turn == bool(self.iswhite):
						self.legal_moves = self.board[x][y].get_moves((x, y), self.board)
				else:
					self.clicked = ()
					self.legal_moves = []
		else:
			self.dragging = ()
			if (x, y) != self.clicked:
				if (x, y) in self.legal_moves:
					self.move_piece((x, y))
				elif (x, y, "kingside") in self.legal_moves:
					self.handle_kingside((x, y))
				elif (x, y, "queenside") in self.legal_moves:
					self.handle_queenside((x, y))
				self.clicked = ()
				self.legal_moves = []


	def draw_initial_board(self):
		self.window.fill(TAN)
		self.window.blit(FRAME, (10, 10))
		pygame.draw.rect(self.window, WOOD, pygame.Rect(47, 47, 646, 646))


		#DRAWS BOARD
		for x in range(8):
			for y in range(8):
				if (x % 2 and not y % 2) or (not x % 2 and y % 2):
					self.window.blit(DARK, (y * 80 + 50, x * 80 + 50))
				else:
					self.window.blit(LIGHT, (y * 80 + 50, x * 80 + 50))
				pygame.display.update()
				pygame.time.wait(10)

		for x in range(8):
			for y in range(8):
				if self.board[x][y]:
					self.window.blit(PIECEMAP[self.board[x][y].color_and_type], (y * 80 + 50, x * 80 + 50))
					pygame.display.update()
					pygame.time.wait(10)



	def draw_board(self):
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

		if self.clicked:
			x, y = self.clicked
			current_square = (x % 2 - y % 2) % 2
			self.window.blit(HIGHLIGHTMAP[current_square], (y * 80 + 50, x * 80 + 50))


		for x in range(8):
			for y in range(8):
				if self.board[x][y]:
					if (x, y) == self.dragging:
						continue
					else:
						self.window.blit(PIECEMAP[self.board[x][y].color_and_type], (y * 80 + 50, x * 80 + 50))

		for move in self.legal_moves:
			x, y  = move[0], move[1]
			self.window.blit(MOVE, (y * 80 + 81, x * 80 + 81))

		if self.dragging:
			x, y = self.dragging
			mouse_x, mouse_y = pygame.mouse.get_pos()
			self.window.blit(PIECEMAP[self.board[x][y].color_and_type], (mouse_x - 40, mouse_y - 40))
			


	def run(self):
		threading.Thread(target = self.receive).start()
		self.draw_initial_board()

		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.mouse_handling(True)
				elif event.type == pygame.MOUSEBUTTONUP:
					self.mouse_handling(False)


			self.draw_board()
			pygame.display.flip()
			self.clock.tick(FPS)

		time.sleep(.15)