import pygame

pygame.init()

FPS = 60
WIDTH, HEIGHT = 1020, 770
WOOD = (80, 55, 25)
TAN = (50, 0, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

DARK = pygame.image.load("images/dark.png")
LIGHT = pygame.image.load("images/light.png")
FRAME = pygame.transform.scale(pygame.image.load("images/frame.png"), (720, 720))

BB = pygame.transform.scale(pygame.image.load("images/bb.png"), (80, 80))
BQ = pygame.transform.scale(pygame.image.load("images/bq.png"), (80, 80))
BR = pygame.transform.scale(pygame.image.load("images/br.png"), (80, 80))
BK = pygame.transform.scale(pygame.image.load("images/bk.png"), (80, 80))
BN = pygame.transform.scale(pygame.image.load("images/bn.png"), (80, 80))
BP = pygame.transform.scale(pygame.image.load("images/bp.png"), (80, 80))
WB = pygame.transform.scale(pygame.image.load("images/wb.png"), (80, 80))
WQ = pygame.transform.scale(pygame.image.load("images/wq.png"), (80, 80))
WR = pygame.transform.scale(pygame.image.load("images/wr.png"), (80, 80))
WK = pygame.transform.scale(pygame.image.load("images/wk.png"), (80, 80))
WN = pygame.transform.scale(pygame.image.load("images/wn.png"), (80, 80))
WP = pygame.transform.scale(pygame.image.load("images/wp.png"), (80, 80))
HIGHLIGHT = pygame.image.load("images/highlight.png")
HIGHLIGHT2 = pygame.image.load("images/highlight2.png")
HIGHLIGHTMAP = {0: HIGHLIGHT, 1: HIGHLIGHT2}

CHALLENGE = pygame.image.load("images/challenge.png")
CHALLENGEHIGHLIGHT = pygame.image.load("images/challengehighlight.png")
CANCEL = pygame.image.load("images/cancel.png")
CANCELHIGHLIGHT = pygame.image.load("images/cancelhighlight.png")
ACCEPT = pygame.image.load("images/accept.png")
ACCEPTHIGHLIGHT = pygame.image.load("images/accepthighlight.png")
DECLINE = pygame.image.load("images/decline.png")
DECLINEHIGHLIGHT = pygame.image.load("images/declinehighlight.png")
MOVE = pygame.transform.scale(pygame.image.load("images/move.png"), (18, 18))

PIECEMAP = {
	"BB": BB,
	"BQ": BQ,
	"BR": BR,
	"BK": BK,
	"BN": BN,
	"BP": BP,
	"WB": WB,
	"WQ": WQ,
	"WR": WR,
	"WK": WK,
	"WN": WN,
	"WP": WP,
}
ALLPIECES = list(PIECEMAP.keys())

FONT = pygame.font.Font('freesansbold.ttf', 15)
LOBBYTEXT = pygame.font.Font('freesansbold.ttf', 25).render("Welcome to the Lobby", True, RED, BLACK)
LOBBYTEXT2 = pygame.font.Font('freesansbold.ttf', 16).render("Click on a user to challenge them.", True, RED, BLACK)
LOBBYTEXT3 = pygame.font.Font('freesansbold.ttf', 15).render("Would you like to challenge this user?", True, RED, BLACK)
INVALIDCHALLENGE = pygame.font.Font('freesansbold.ttf', 15).render("You can't challenge yourself.", True, RED, BLACK)
PENDING1 = pygame.font.Font('freesansbold.ttf', 15).render("Pending.", True, RED, BLACK)
PENDING2 = pygame.font.Font('freesansbold.ttf', 15).render("Pending..", True, RED, BLACK)
PENDING3 = pygame.font.Font('freesansbold.ttf', 15).render("Pending...", True, RED, BLACK)
PENDINGANIMATION = [PENDING1, PENDING2, PENDING3]
REQUEST = pygame.font.Font('freesansbold.ttf', 15).render("wants to challenge you:", True, RED, BLACK)


MAXUSERNAME = 10

BOARD = [
		["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
		["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
		[0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0],
		["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
		["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"],
		]