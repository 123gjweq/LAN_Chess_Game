import time

class Piece():

	reversing = False

	def __init__(self, specific_piece, color):
		self.type = specific_piece
		self.color = color
		self.int_color = int(color == "W")
		self.color_and_type = color + specific_piece
		self.move_number = 0

	def __repr__(self):
		return self.color_and_type

	def reverse_check_board(self):
		for row in check_board:
			row.reverse()
		check_board.reverse()

	def bishop_moves(self, pos, board):
		legal_moves = []
		x, y = pos
		upleft_x, upleft_y = x - 1, y + 1
		upright_x, upright_y = x + 1, y + 1
		downleft_x, downleft_y = x - 1, y - 1
		downright_x, downright_y = x + 1, y - 1

		while upleft_x >= 0 and upleft_y < 8:
			legal_moves.append((upleft_x, upleft_y))
			if board[upleft_x][upleft_y]:
				break
			upleft_x -= 1
			upleft_y += 1

		while downright_x < 8 and downright_y >= 0:
			legal_moves.append((downright_x, downright_y))
			if board[downright_x][downright_y]:
				break
			downright_x += 1
			downright_y -= 1

		while upright_x < 8 and upright_y < 8:
			legal_moves.append((upright_x, upright_y))
			if board[upright_x][upright_y]:
				break
			upright_x += 1
			upright_y += 1

		while downleft_x >= 0 and downleft_y >= 0:
			legal_moves.append((downleft_x, downleft_y))
			if board[downleft_x][downleft_y]:
				break
			downleft_x -= 1
			downleft_y -= 1

		return legal_moves

	def rook_moves(self, pos, board):
		legal_moves = []
		x, y = pos
		up, left, down, right = y + 1, x - 1, y - 1, x + 1
		while up < 8:
			legal_moves.append((x, up))
			if board[x][up]:
				break
			up += 1
		while down >= 0:
			legal_moves.append((x, down))
			if board[x][down]:
				break
			down -= 1
		while left >= 0:
			legal_moves.append((left, y))
			if board[left][y]:
				break
			left -= 1
		while right < 8:
			legal_moves.append((right, y))
			if board[right][y]:
				break
			right += 1
		return legal_moves

	def check_for_checks(self, legal_moves_corrected, pos):
		legal_moves_corrected_for_check = []
		piecex, piecey = pos
		Piece.reversing = True
		self.reverse_check_board()
		piecex, piecey = 7 - piecex, 7 - piecey

		for move in legal_moves_corrected:
			if len(move) > 2:
				legal_moves_corrected_for_check.append(move)
				continue
			x, y = move
			x, y = 7 - x, 7 - y
			temp_piece = check_board[piecex][piecey]
			temp_square = check_board[x][y]
			check_board[piecex][piecey].move_number += 1
			check_board[piecex][piecey], check_board[x][y] = 0, check_board[piecex][piecey]

			set_of_enemy_moves = set()
			ally_king = None

			for row in range(8):
				for col in range(8):
					if check_board[row][col] and check_board[row][col].color_and_type == self.color + "K":
						ally_king = (7 - row, 7 - col)
					elif check_board[row][col] and check_board[row][col].color != self.color:
						for enemy_move in check_board[row][col].get_moves((row, col), check_board, False):
							set_of_enemy_moves.add((7 - enemy_move[0], 7 - enemy_move[1]))
			if ally_king not in set_of_enemy_moves:
				legal_moves_corrected_for_check.append(move)

			check_board[piecex][piecey] = temp_piece
			check_board[piecex][piecey].move_number -= 1
			check_board[x][y] = temp_square
		self.reverse_check_board()
		Piece.reversing = False
		return legal_moves_corrected_for_check


	def remove_moves(self, legal_moves, pos):
		piecex, piecey = pos
		legal_moves_corrected = []
		#phase 1: remove all moves which have a piece capturing another piece of its same color
		for move in legal_moves:
			if len(move) > 2:
				legal_moves_corrected.append(move)
				continue
			x, y = move
			if not check_board[x][y] or check_board[x][y].color != self.color:
				legal_moves_corrected.append(move)


		#phase 2: remove all moves that lead to/leave the king in check
		return self.check_for_checks(legal_moves_corrected, pos)


class Pawn(Piece):
	def __init__(self, color):
		super().__init__("P", color)

	def get_moves(self, pos, board, real_move = True):
		x, y = pos
		legal_moves = []

		if x - 1 >= 0:
			if not board[x - 1][y]:
				legal_moves.append((x - 1, y))
			if y - 1 >= 0 and board[x - 1][y - 1] and board[x - 1][y - 1].int_color != self.int_color:
				legal_moves.append((x - 1, y - 1))
			if y + 1 < 8 and board[x - 1][y + 1] and board[x - 1][y + 1].int_color != self.int_color:
				legal_moves.append((x - 1, y + 1))
		if not self.move_number and x - 2 >= 0 and not board[x - 2][y]:
			legal_moves.append((x - 2, y))
		if real_move:
			return self.remove_moves(legal_moves, pos)
		return legal_moves


class Rook(Piece):
	def __init__(self, color):
		super().__init__("R", color)

	def get_moves(self, pos, board, real_move = True):
		legal_moves = self.rook_moves(pos, board)
		if real_move:
			return self.remove_moves(legal_moves, pos)
		return legal_moves


class Knight(Piece):
	def __init__(self, color):
		super().__init__("N", color)

	def get_moves(self, pos, board, real_move = True):
		x, y = pos
		legal_moves = []

		if x - 2 >= 0 and y - 1 >= 0: legal_moves.append((x - 2, y - 1))
		if x - 2 >= 0 and y + 1 < 8: legal_moves.append((x - 2, y + 1))
		if x - 1 >= 0 and y - 2 >= 0: legal_moves.append((x - 1, y - 2))
		if x - 1 >= 0 and y + 2 < 8: legal_moves.append((x - 1, y + 2))
		if x + 1 < 8 and y - 2 >= 0: legal_moves.append((x + 1, y - 2))
		if x + 1 < 8 and y + 2 < 8: legal_moves.append((x + 1, y + 2))
		if x + 2 < 8 and y - 1 >= 0: legal_moves.append((x + 2, y - 1))
		if x + 2 < 8 and y + 1 < 8: legal_moves.append((x + 2, y + 1))
		if real_move:
			return self.remove_moves(legal_moves, pos)
		return legal_moves


class Bishop(Piece):
	def __init__(self, color):
		super().__init__("B", color)

	def get_moves(self, pos, board, real_move = True):
		legal_moves = self.bishop_moves(pos, board)
		if real_move:
			return self.remove_moves(legal_moves, pos)
		return legal_moves


class Queen(Piece):
	def __init__(self, color):
		super().__init__("Q", color)

	def get_moves(self, pos, board, real_move = True):
		legal_moves = self.rook_moves(pos, board) + self.bishop_moves(pos, board)
		if real_move:
			return self.remove_moves(legal_moves, pos)
		return legal_moves


class King(Piece):
	def __init__(self, color):
		super().__init__("K", color)

	def get_moves(self, pos, board, real_move = True):
		x, y = pos
		legal_moves = []

		if x - 1 >= 0 and y - 1 >= 0: legal_moves.append((x - 1, y - 1))
		if y - 1 >= 0: legal_moves.append((x, y - 1))
		if x - 1 >= 0: legal_moves.append((x - 1, y))
		if x + 1 < 8 and y + 1 < 8: legal_moves.append((x + 1, y + 1))
		if x + 1 < 8: legal_moves.append((x + 1, y))
		if y + 1 < 8: legal_moves.append((x, y + 1))
		if x + 1 < 8 and y - 1 >= 0: legal_moves.append((x + 1, y - 1))
		if x - 1 >= 0 and y + 1 < 8: legal_moves.append((x - 1, y + 1))

		#white castle
		if self.color == "W":
			#kingside
			if not board[x][y].move_number and board[x][y + 3] and not board[x][y + 3].move_number: #if neither the kign and the right rook hasm oved
				if not board[x][y + 1] and not board[x][y + 2]: #if there are no pieces in between the king and the rook
					if [(x, y), (x, y + 1), (x, y + 2)] == self.check_for_checks([(x, y), (x, y + 1), (x, y + 2)], (x, y)):
						legal_moves.append((x, y + 2, "kingside"))
			if not board[x][y].move_number and board[x][y - 4] and not board[x][y - 4].move_number:
				if not board[x][y - 3] and not board[x][y - 2] and not board[x][y - 1]:
					if [(x, y), (x, y - 1), (x, y - 2)] == self.check_for_checks([(x, y), (x, y - 1), (x, y - 2)], (x, y)):
						legal_moves.append((x, y - 2, "queenside"))
		#black castle
		else:
			#queenside
			if not board[x][y].move_number and board[x][y - 3] and not board[x][y - 3].move_number: #if neither the kign and the right rook hasm oved
				if not board[x][y - 1] and not board[x][y - 2]: #if there are no pieces in between the king and the rook
					if [(x, y), (x, y - 1), (x, y - 2)] == self.check_for_checks([(x, y), (x, y - 1), (x, y - 2)], (x, y)):
						legal_moves.append((x, y - 2, "kingside"))
			if not board[x][y].move_number and board[x][y + 4] and not board[x][y + 4].move_number:
				if not board[x][y + 3] and not board[x][y + 2] and not board[x][y + 1]:
					if [(x, y), (x, y + 1), (x, y + 2)] == self.check_for_checks([(x, y), (x, y + 1), (x, y + 2)], (x, y)):
						legal_moves.append((x, y + 2, "queenside"))

		if real_move:
			return self.remove_moves(legal_moves, pos)
		return legal_moves

"""
a board that will help check if each move that can be performed by a piece
leads to check
"""
check_board = 	[
				[Rook("B"), Knight("B"), Bishop("B"), Queen("B"), King("B"), Bishop("B"), Knight("B"), Rook("B")],
				[Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B"), Pawn("B")],
				[0, 0, 0, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 0, 0, 0],
				[0, 0, 0, 0, 0, 0, 0, 0],
				[Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W"), Pawn("W")],
				[Rook("W"), Knight("W"), Bishop("W"), Queen("W"), King("W"), Bishop("W"), Knight("W"), Rook("W")],
				]