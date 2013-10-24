# Dr. Mario
# By Dan Ford dpford@gmail.com
# http://github.com/dpford

import random
import time
import pygame
import sys
import math
import copy

from pygame.locals import *

STARTING_VIRUS_COUNT = 10

FPS = 25
WINDOWWIDTH = 1920
WINDOWHEIGHT = 1080
BOXSIZE = 40
BOARDWIDTH = 10
BOARDHEIGHT = 20

MOVESIDEWAYSFREQ = 0.1
MOVEDOWNFREQ = 0.1

# XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
XMARGIN1 = 450
XMARGIN2 = 1070
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) -5

WHITE = (255, 255, 255)
GRAY = (185, 185, 185)
BLACK = (0, 0, 0)
RED = (155, 0, 0)
LIGHTRED = (175, 20, 20)
BLUE = (0, 0, 155)
LIGHTBLUE = (20, 20, 175)
YELLOW = (155, 155, 0)
LIGHTYELLOW = (175, 175, 20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS = (RED, BLUE, YELLOW)
LIGHTCOLORS = (LIGHTRED, LIGHTBLUE, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS)

TEMPLATEWIDTH = 2
TEMPLATEHEIGHT = 2
BLANK = '.'

ORIENTATION = [	  ['..',
				   'AB'],
				  ['B.',
				   'A.'],
				  ['..',
				   'BA'],
				  ['A.',
				   'B.']]

def main():
	global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, complete, BIGVIRUSCOUNTFONT, INGAMETITLEFONT, P1WINS, P2WINS, P1LEVEL, P2LEVEL
	# global MONSTERS
	pygame.mixer.pre_init(44100, -16, 2, 512)
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	P1WINS = 0
	P2WINS = 0
	# initialize levels
	P1LEVEL = 1
	P2LEVEL = 1
	# DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	DISPLAYSURF = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
	BASICFONT = pygame.font.Font('fonts/Chunkfive.otf', 60)
	BIGVIRUSCOUNTFONT = pygame.font.Font('fonts/Chunkfive.otf', 140)
	BIGFONT = pygame.font.Font('fonts/Chunkfive.otf', 120)
	INGAMETITLEFONT = pygame.font.Font('fonts/Super Mario Bros..ttf', 60)
	complete = pygame.mixer.Sound('doctor_music/smw-gain.ogg')
	# MONSTERS = 0
	pygame.display.set_caption("Mario, M.D.")

	if pygame.joystick.get_count() == 0 or pygame.joystick.Joystick(0).get_name()[:10] == 'VirtualBox':
		print 'no joysticks'
	else:
		pygame.joystick.Joystick(0).init()
		pygame.joystick.Joystick(1).init()

	showLogoScreen()
	while True: #game loop
		songs = ['doctor_music/doctor_fever_guitar.ogg', 
				 'doctor_music/cold-ruins.ogg', 
				 'doctor_music/dkc-gangplank.ogg',
				 'doctor_music/starfox.ogg']
		song_to_play = songs[random.randint(0,3)]
		pygame.mixer.music.load(song_to_play)
		pygame.mixer.music.play(-1, 0.0)
		message = runGame()
		pygame.mixer.music.fadeout(1000)
		if P2WINS == 3 or P1WINS == 3:
			pygame.mixer.music.load('doctor_music/08_-_Dr._Mario_-_NES_-_VS_Game_Over.ogg')
		else:
			pygame.mixer.music.load('doctor_music/05_-_Dr._Mario_-_NES_-_Fever_Clear.ogg')
		pygame.mixer.music.play(-1, 0.0)
		showTextScreen('%s' % (message,))
		

def runGame():
	global P1WINS, P2WINS, P1PIECE, P2PIECE, P1LEVEL, P2LEVEL
	# Player 1
	board1 = getInitialBoard()
	piecesList1 = createPieces(200)
	piecesList2 = copy.deepcopy(piecesList1)
	P1PIECE = 2
	P2PIECE = 2
	lastMoveDownTime1 = time.time()
	lastMoveSidewaysTime1 = time.time()
	lastFallTime1 = time.time()
	movingDown1 = False
	movingLeft1 = False
	movingRight1 = False
	score1 = 0
	level1, fallFreq1 = calculateLevelAndFallFreq(score1)
	print level1
	if level1 > P1LEVEL:
		pygame.mixer.Sound('doctor_music/level_up.ogg').play()
		P1LEVEL = level1


	# fallingPiece1 = getNewPiece()
	# nextPiece1 = getNewPiece()

	fallingPiece1 = piecesList1[0]
	nextPiece1 = piecesList1[1]

	# Player 2
	board2 = copy.deepcopy(board1)
	lastMoveDownTime2 = time.time()
	lastMoveSidewaysTime2 = time.time()
	lastFallTime2 = time.time()
	movingDown2 = False
	movingLeft2 = False
	movingRight2 = False
	score2 = 0
	level2, fallFreq2 = calculateLevelAndFallFreq(score2)
	if level2 > P2LEVEL:
		pygame.mixer.Sound('doctor_music/level_up.ogg').play()
		P2LEVEL = level2

	# fallingPiece2 = getNewPiece()
	# nextPiece2 = getNewPiece()

	fallingPiece2 = piecesList2[0]
	nextPiece2 = piecesList2[1]




	while True: #main game loop
		#Player 1
		if fallingPiece1 == None:
			# No falling pill in play, so put one at the top
			fallingPiece1 = nextPiece1
			nextPiece1 = piecesList1[P1PIECE]
			P1PIECE += 1
			lastFallTime1 = time.time() #reset lastFallTime

			if not isValidPosition(board1, fallingPiece1):
				P2WINS += 1
				if P2WINS == 3: #first to three, winner!
					P1WINS = 0
					P2WINS = 0
					return 'P1, take a shot. Suck it down!'
				return 'Player 2 Wins!'# can't find a new pill, so you lose!
		#Player 2
		if fallingPiece2 == None:
			# No falling pill in play, so put one at the top
			fallingPiece2 = nextPiece2
			nextPiece2 = piecesList2[P2PIECE]
			P2PIECE += 1
			lastFallTime2 = time.time() #reset lastFallTime

			if not isValidPosition(board2, fallingPiece2):
				P1WINS += 1
				if P1WINS == 3: #first to three, winner!
					P1WINS = 0
					P2WINS = 0
					return 'P2, take a shot. Suck it down!'
				return 'Player 1 Wins!'# can't find a new pill, so you lose!

		checkForQuit()
		if MONSTERS1 == 0:
			return 'Player 1 Wins!'
		elif MONSTERS2 == 0:
			return 'Player 2 Wins!'
		for event in pygame.event.get(): #event handling loop
			if event.type == JOYBUTTONUP:
				if (event.button == 3): # pause game
					DISPLAYSURF.fill(BGCOLOR)
					pygame.mixer.music.stop()
					showTextScreen('Paused') #until a key is pressed
					pygame.mixer.music.play(-1, 0.0)
					lastFallTime1 = time.time()
					lastMoveDownTime1 = time.time()
					lastMoveSidewaysTime1 = time.time()
					lastFallTime2 = time.time()
					lastMoveDownTime2 = time.time()
					lastMoveSidewaysTime2 = time.time()			

			elif event.type == JOYBUTTONDOWN:
				
				#rotating the pill (if there's room), player 1
				if event.joy == 0:
					if (event.button == 1):
						fallingPiece1['rotation'] = (fallingPiece1['rotation'] + 1) % 4
						if not isValidPosition(board1, fallingPiece1):
							fallingPiece1['rotation'] = (fallingPiece1['rotation'] - 1) % 4
					elif (event.button == 5): #other direction
						fallingPiece1['rotation'] = (fallingPiece1['rotation'] - 1) % 4
						if not isValidPosition(board1, fallingPiece1):
							fallingPiece1['rotation'] = (fallingPiece1['rotation'] + 1) % 4

				#rotating the pill (if there's room), player 2
				elif event.joy == 1:
					if (event.button == 1):
						fallingPiece2['rotation'] = (fallingPiece2['rotation'] + 1) % 4
						if not isValidPosition(board2, fallingPiece2):
							fallingPiece2['rotation'] = (fallingPiece2['rotation'] - 1) % 4
					elif (event.button == 5): #other direction
						fallingPiece2['rotation'] = (fallingPiece2['rotation'] - 1) % 4
						if not isValidPosition(board2, fallingPiece2):
							fallingPiece2['rotation'] = (fallingPiece2['rotation'] + 1) % 4
				
			elif event.type == JOYAXISMOTION:
				# axis stuff, player 1
				if event.joy == 0:
					if (event.axis == 0) and (event.value == 1) and isValidPosition(board1, fallingPiece1, adjX=1):
						fallingPiece1['x'] += 1
						movingRight1 = True
					 	movingLeft1 = False
					 	lastMoveSidewaysTime1 = time.time()
					elif (event.axis == 0) and (event.value == 0):
						movingLeft1 = False
						movingRight1 = False
					elif (event.axis == 1) and (event.value == 1):
						movingDown1 = True
						if isValidPosition(board1, fallingPiece1, adjY=1):
							fallingPiece1['y'] += 1
						lastMoveDownTime1 = time.time()
					elif (event.axis == 1) and (event.value == 0):
						movingDown1 = False
					elif (event.axis == 0) and int(event.value) == -1 and isValidPosition(board1, fallingPiece1, adjX=-1):
						fallingPiece1['x'] -= 1
					 	movingLeft1 = True
					 	movingRight1 = False
					 	lastMoveSidewaysTime1 = time.time()

				# axis stuff, player 2
				if event.joy == 1:
					if (event.axis == 0) and (event.value == 1) and isValidPosition(board2, fallingPiece2, adjX=1):
						fallingPiece2['x'] += 1
						movingRight2 = True
					 	movingLeft2 = False
					 	lastMoveSidewaysTime2 = time.time()
					elif (event.axis == 0) and (event.value == 0):
						movingLeft2 = False
						movingRight2 = False
					elif (event.axis == 1) and (event.value == 1):
						movingDown2 = True
						if isValidPosition(board2, fallingPiece2, adjY=1):
							fallingPiece2['y'] += 1
						lastMoveDownTime2 = time.time()
					elif (event.axis == 1) and (event.value == 0):
						movingDown2 = False
					elif (event.axis == 0) and int(event.value) == -1 and isValidPosition(board2, fallingPiece2, adjX=-1):
						fallingPiece2['x'] -= 1
					 	movingLeft2 = True
					 	movingRight2 = False
					 	lastMoveSidewaysTime2 = time.time()

			# elif event.type == KEYUP:
			# 	if (event.key == K_p): # pause game
			# 		DISPLAYSURF.fill(BGCOLOR)
			# 		pygame.mixer.music.stop()
			# 		showTextScreen('Paused') #until a key is pressed
			# 		pygame.mixer.music.play(-1, 0.0)
			# 		lastFallTime = time.time()
			# 		lastMoveDownTime = time.time()
			# 		lastMoveSidewaysTime = time.time()
			# 	elif (event.key == K_LEFT or event.key == K_a):
			# 		movingLeft = False
			# 	elif (event.key == K_RIGHT or event.key == K_d):
			# 		movingRight = False
			# 	elif (event.key == K_DOWN or event.key == K_s):
			# 		movingDown = False

			# elif event.type == KEYDOWN:
			# 	# moving block sideways
			# 	if (event.key == K_LEFT or event.key == K_a) and \
			# 		isValidPosition(board, fallingPiece, adjX=-1):
			# 	 	fallingPiece['x'] -= 1
			# 	 	movingLeft = True
			# 	 	movingRight = False
			# 	 	lastMoveSidewaysTime = time.time()

			# 	elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
			# 	 	fallingPiece['x'] += 1
			# 	 	movingRight = True
			# 	 	movingLeft = False
			# 	 	lastMoveSidewaysTime = time.time()

			# 	 #rotating the pill (if there's room)
			# 	elif (event.key == K_UP or event.key == K_z):
			# 		fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % 4
			# 		if not isValidPosition(board, fallingPiece):
			# 			fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % 4
			# 	elif (event.key ==K_x): #other direction
			# 		fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % 4
			# 		if not isValidPosition(board, fallingPiece):
			# 			fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % 4
			# 	# drop pill faster with down key
			# 	elif (event.key == K_DOWN or event.key == K_s):
			# 		movingDown = True
			# 		if isValidPosition(board, fallingPiece, adjY=1):
			# 			fallingPiece['y'] += 1
			# 		lastMoveDownTime = time.time()


					

		#Player 1
		if (movingLeft1 or movingRight1) and time.time() - lastMoveSidewaysTime1 > MOVESIDEWAYSFREQ:
			if movingLeft1 and isValidPosition(board1, fallingPiece1, adjX=-1):
				fallingPiece1['x'] -= 1
			elif movingRight1 and isValidPosition(board1, fallingPiece1, adjX=1):
				fallingPiece1['x'] += 1
			lastMoveSidewaysTime1 = time.time()

		if movingDown1 and time.time() - lastMoveDownTime1 > MOVEDOWNFREQ and isValidPosition(board1, fallingPiece1, adjY=1):
			fallingPiece1['y'] += 1
			lastMoveDownTime1 = time.time()

		#let the pill fall down on its own
		if time.time() - lastFallTime1 > fallFreq1:
			# see if pill has landed
			if not isValidPosition(board1, fallingPiece1, adjY=1):
				# it's landed, add to board
				addToBoard(board1, fallingPiece1)
# THIS WAS LAZY, FIX THIS _________________________________***************************************************
				score1 += removeCompletes(board1, 1)
				findOrphans(board1)
				score1 += removeCompletes(board1, 1)
				level1, fallFreq1 = calculateLevelAndFallFreq(score1)
				if level1 > P1LEVEL:
					print 'player 1 move up'
					pygame.mixer.Sound('doctor_music/level_up.ogg').play()
					P1LEVEL = level1
				fallingPiece1 = None
			else:
				fallingPiece1['y'] += 1
				lastFallTime1 = time.time()

		#Player 2
		if (movingLeft2 or movingRight2) and time.time() - lastMoveSidewaysTime2 > MOVESIDEWAYSFREQ:
			if movingLeft2 and isValidPosition(board2, fallingPiece2, adjX=-1):
				fallingPiece2['x'] -= 1
			elif movingRight2 and isValidPosition(board2, fallingPiece2, adjX=1):
				fallingPiece2['x'] += 1
			lastMoveSidewaysTime2 = time.time()

		if movingDown2 and time.time() - lastMoveDownTime2 > MOVEDOWNFREQ and isValidPosition(board2, fallingPiece2, adjY=1):
			fallingPiece2['y'] += 1
			lastMoveDownTime2 = time.time()

		#let the pill fall down on its own
		if time.time() - lastFallTime2 > fallFreq2:
			# see if pill has landed
			if not isValidPosition(board2, fallingPiece2, adjY=1):
				# it's landed, add to board
				addToBoard(board2, fallingPiece2)
# THIS WAS LAZY, FIX THIS _________________________________***************************************************
				score2 += removeCompletes(board2, 2)
				findOrphans(board2)
				score2 += removeCompletes(board2, 2)
				level2, fallFreq2 = calculateLevelAndFallFreq(score2)
				if level2 > P2LEVEL:
					print 'player 2 move up'
					pygame.mixer.Sound('doctor_music/level_up.ogg').play()
					P2LEVEL = level2
				fallingPiece2 = None
			else:
				fallingPiece2['y'] += 1
				lastFallTime2 = time.time()
#----------------------------------------------------------------------------
		# draw everything on the screen
		DISPLAYSURF.fill(BGCOLOR)
		drawBoard(board1, 1)
		drawBoard(board2, 2)
		drawStatus(score1, level1, MONSTERS1, 1)
		drawStatus(score2, level2, MONSTERS2, 2)
		drawNextPiece(nextPiece1, 1)
		drawNextPiece(nextPiece2, 2)
		if fallingPiece1 != None:
			drawPiece(fallingPiece1, 1)

		if fallingPiece2 != None:
			drawPiece(fallingPiece2, 2)

		pygame.display.update()
		FPSCLOCK.tick(FPS)

def makeTextObjs(text, font, color):
	surf = font.render(text, True, color)
	return surf, surf.get_rect()

def terminate():
	pygame.quit()
	sys.exit()

def checkForKeyPress():
	# go through event queue looking for KEYUP
	# Grab KEYDOWN events to remove them from the queue
	checkForQuit()

	for event in pygame.event.get([KEYDOWN, KEYUP, JOYBUTTONDOWN, JOYBUTTONUP]):
		if event.type == KEYUP:
			return event.key
		elif event.type == JOYBUTTONUP:
			return event.button
	return None

def showTextScreen(text):
	# Displays large text in center of screen until a key is pressed
	# Draw the text drop shadow
	titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
	titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
	DISPLAYSURF.blit(titleSurf, titleRect)

	# Draw the text
	titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
	titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)

	DISPLAYSURF.blit(titleSurf, titleRect)

	# Draw the additional "Press a key to play." text.
	pressKeySurf, pressKeyRect = makeTextObjs('Press a button to continue', BASICFONT, TEXTCOLOR)
	pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)

	DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

	while checkForKeyPress() == None:
		pygame.display.update()
		FPSCLOCK.tick()

def showLogoScreen():
	# Displays the logo until a button is pressed
	mainLogoSurf = pygame.image.load('marioMD_v1_green.png')
	mainLogoRect = mainLogoSurf.get_rect()
	mainLogoRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) - 100)

	DISPLAYSURF.blit(mainLogoSurf, mainLogoRect)

	# Draw the additional "Press a key to play." text.
	pressKeySurf, pressKeyRect = makeTextObjs('Press a button to start', BASICFONT, TEXTCOLOR)
	pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)

	DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


	while checkForKeyPress() == None:
		pygame.display.update()
		FPSCLOCK.tick()

def checkForQuit():
	for event in pygame.event.get(QUIT): #get all QUIT events
		terminate() #terminate if any QUIT event present
	for event in pygame.event.get(KEYUP): # get all KEYUP events
		if event.key == K_ESCAPE:
			terminate() #terminate if KEYUP was esc key
		pygame.event.post(event) # put other KEYUP event objects back

def calculateLevelAndFallFreq(score):
	level = int(score / 20) + 1
	fallFreq = 0.27 - (level * 0.01)
	return level, fallFreq

def getNewPiece():
	# return a new pill with random colors
	newPiece = {'A': random.randint(0, len(COLORS)-1),
				'B': random.randint(0, len(COLORS)-1),
				'rotation': 0,
				'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
				'y': 0}
	return newPiece

def createPieces(length):
	piecesList = []
	for i in range(length):
		piecesList.append(getNewPiece())
	return piecesList



def addToBoard(board, piece):
	# fill in the board based on piece's location
	for x in range(TEMPLATEWIDTH):
		for y in range(TEMPLATEHEIGHT):
			if ORIENTATION[piece['rotation']][y][x] == 'A':
				# this needs to be fixed
				if piece['rotation'] == 0:
					put_on_board = piece['A'] + 6
				elif piece['rotation'] == 1:
					put_on_board = piece['A'] + 9
				elif piece['rotation'] == 2:
					put_on_board = piece['A']
				elif piece['rotation'] == 3:
					put_on_board = piece['A'] + 3
				board[x + piece['x']][y + piece['y']] = put_on_board
			elif ORIENTATION[piece['rotation']][y][x] == 'B':
				if piece['rotation'] == 0:
					put_on_board = piece['B']
				elif piece['rotation'] == 1:
					put_on_board = piece['B'] + 3
				elif piece['rotation'] == 2:
					put_on_board = piece['B'] + 6
				elif piece['rotation'] == 3:
					put_on_board = piece['B'] + 9
				board[x + piece['x']][y + piece['y']] = put_on_board

def getInitialBoard():
	global MONSTERS
	MONSTERS = 0
	board = []
	for i in range(BOARDWIDTH):
		# board.append([BLANK] * BOARDHEIGHT)
		column = []
		for p in range(BOARDHEIGHT):
			if p > (5*BOARDHEIGHT / 12) and MONSTERS < STARTING_VIRUS_COUNT and random.randint(1,100) < 9: #bottom 7/12
				column.append(random.randint(90,92))
				MONSTERS += 1
			else:
				column.append(BLANK)
		board.append(column)
	global MONSTERS1
	MONSTERS1 = MONSTERS
	global MONSTERS2
	MONSTERS2 = MONSTERS
	return board

def isOnBoard(x, y):
	return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT

def isValidPosition(board, piece, adjX=0, adjY=0):
	# returns true if piece is in board and doesn't collide with anything
	for x in range(TEMPLATEWIDTH):
		for y in range(TEMPLATEHEIGHT):
			isAboveBoard = y + piece['y'] + adjY < 0
			if isAboveBoard or ORIENTATION[piece['rotation']][y][x] == BLANK:
				continue
			if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
				return False
			if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
				return False
	return True

def isCompleteSetHoriz(board, y, board_number):
	if board_number == 1:
		global MONSTERS1
		count = 0
		monster_count = 0
		last_color = -1
		for x in range(BOARDWIDTH):
			if board[x][y] != BLANK:
				this_color = board[x][y] % 3
				if (this_color == last_color) or (last_color == -1):
					last_color = this_color
					count += 1
					if board[x][y] > 11:
						monster_count += 1
				else:
					if count >= 4:
						complete.play()
						MONSTERS1 = MONSTERS1 - monster_count
						return x-1, count
					else:
						last_color = this_color
						count = 1
						if board[x][y] > 11:
							monster_count = 1
						else:
							monster_count = 0
			else:
				if count >= 4:
					complete.play()
					MONSTERS1 = MONSTERS1 - monster_count
					return x-1, count
				else:
					count = 0
					monster_count = 0
			if x == (BOARDWIDTH - 1):
				if count >= 4:
					complete.play()
					MONSTERS1 = MONSTERS1 - monster_count
					return x, count
	elif board_number == 2:
		global MONSTERS2
		count = 0
		monster_count = 0
		last_color = -1
		for x in range(BOARDWIDTH):
			if board[x][y] != BLANK:
				this_color = board[x][y] % 3
				if (this_color == last_color) or (last_color == -1):
					last_color = this_color
					count += 1
					if board[x][y] > 11:
						monster_count += 1
				else:
					if count >= 4:
						complete.play()
						MONSTERS2 = MONSTERS2 - monster_count
						return x-1, count
					else:
						last_color = this_color
						count = 1
						if board[x][y] > 11:
							monster_count = 1
						else:
							monster_count = 0
			else:
				if count >= 4:
					complete.play()
					MONSTERS2 = MONSTERS2 - monster_count
					return x-1, count
				else:
					count = 0
					monster_count = 0
			if x == (BOARDWIDTH - 1):
				if count >= 4:
					complete.play()
					MONSTERS2 = MONSTERS2 - monster_count
					return x, count
	return False

def isCompleteSetVert(board, x, board_number):
	if board_number == 1:
		global MONSTERS1
	
		count = 0
		monster_count = 0
		last_color = -1
		for y in range(BOARDHEIGHT):
			if board[x][y] != BLANK:
				this_color = board[x][y] % 3
				if (this_color == last_color) or (last_color == -1):
					last_color = this_color
					count += 1
					if board[x][y] > 11:
						monster_count += 1
				else:
					if count >= 4:
						complete.play()
						MONSTERS1 = MONSTERS1 - monster_count
						return y-1, count
					else:
						last_color = this_color
						count = 1
						if board[x][y] > 11:
							monster_count = 1
						else:
							monster_count = 0
			else:
				if count >= 4:
					complete.play()
					MONSTERS1 = MONSTERS1 - monster_count
					return y-1, count
				else:
					count = 0
					monster_count = 0
			if y == (BOARDHEIGHT - 1):
				if count >= 4:
					complete.play()
					MONSTERS1 = MONSTERS1 - monster_count
					return y, count
	elif board_number == 2:
		global MONSTERS2
		count = 0
		monster_count = 0
		last_color = -1
		for y in range(BOARDHEIGHT):
			if board[x][y] != BLANK:
				this_color = board[x][y] % 3
				if (this_color == last_color) or (last_color == -1):
					last_color = this_color
					count += 1
					if board[x][y] > 11:
						monster_count += 1
				else:
					if count >= 4:
						complete.play()
						MONSTERS2 = MONSTERS2 - monster_count
						return y-1, count
					else:
						last_color = this_color
						count = 1
						if board[x][y] > 11:
							monster_count = 1
						else:
							monster_count = 0
			else:
				if count >= 4:
					complete.play()
					MONSTERS2 = MONSTERS2 - monster_count
					return y-1, count
				else:
					count = 0
					monster_count = 0
			if y == (BOARDHEIGHT - 1):
				if count >= 4:
					complete.play()
					MONSTERS2 = MONSTERS2 - monster_count
					return y, count



	return False

def shiftRemainingYHoriz(board, x, count, y):
	keep_going = True
	for pullDownY in range(y, 0, -1):
		if keep_going:
			for x_1 in range(x, x-count, -1):
				if board[x_1][pullDownY-1] != BLANK and board[x_1][pullDownY-1] > 11:
					keep_going = False
					print 'falsed at %s, %s. piece is %s' % (x_1, pullDownY-1, board[x_1][pullDownY-1])
				else:
					board[x_1][pullDownY] = board[x_1][pullDownY-1]

def shiftRemainingXVert(board, x, y, count):
	board[x][y-count+1:y+1] = BLANK * count
	for pullDownY in range(y, count, -1):
		if board[x][pullDownY-count] != BLANK and board[x][pullDownY-count] > 11:
			break
		else:
			board[x][pullDownY] = board[x][pullDownY-count]
	# keep_going = True
	# for pullDownY in range(y, count, -1):
	# 	if board[x][pullDownY-1] != BLANK and board[x][pullDownY-1] > 11:
	# 		break
	# 	else:
			# board[x][pullDownY] = board[x][pullDownY-count]

def dropOrphan(board, x, y):
	# board[x][y + 1] = board[x][y]
	# board[x][y] = BLANK
	# depth = y + 2
	# while depth < (BOARDHEIGHT-1) and (board[x][depth] == BLANK):
	# 	board[x][depth] = board[x][depth-1]
	# 	board[x][depth-1] = BLANK
	# 	depth += 1
	# 	print 'hi'
	additional = 0
	drop_height = 0
	for height in range(y-1, -1, -1):
		if isAlsoOrphan(board, x, height):
			additional += 1
	for drop in range(y+1, BOARDHEIGHT):
		if board[x][drop] == BLANK:
			drop_height += 1
		else:
			break

	#actually do the drop
	for actual_drop in range(y, y+drop_height):
		board[x][actual_drop-additional+1:actual_drop+2] = board[x][actual_drop - additional:actual_drop+1]
		board[x][actual_drop - additional] = BLANK

def isAlsoOrphan(board, x, y):
	if board[x][y] > 11: #if it's a virus
		return False
	if x == (BOARDWIDTH - 1): # if x is against the right wall
		if board[x-1][y] == BLANK:
			return True
	elif x == 0: # against the left wall
		if board[x+1][y] == BLANK:
			return True
	else:
		if (board[x-1][y] == BLANK) and (board[x+1][y] == BLANK):
			return True
	return False


def findOrphans(board):
	# y = 0
	# while y < (BOARDHEIGHT - 1):
	# 	for x in range(0, BOARDWIDTH):
	# 		if x == (BOARDWIDTH - 1): # if x is against the right wall
	# 			if (board[x][y]) != BLANK and board[x][y] <= 11 and (board[x][y+1] == BLANK) and (board[x-1][y] == BLANK or board[x-1][y] > 11):
	# 				dropOrphan(board, x, y)
	# 		elif x == 0: # against the left wall
	# 			if (board[x][y]) != BLANK and board[x][y] <= 11 and (board[x][y+1] == BLANK) and (board[x+1][y] == BLANK or board[x+1][y] > 11):
	# 				dropOrphan(board, x, y)
	# 		else:
	# 			if (board[x][y]) != BLANK and board[x][y] <= 11 and (board[x][y+1] == BLANK) and (board[x+1][y] == BLANK or board[x+1][y] > 11) and (board[x-1][y] == BLANK or board[x-1][y] > 11):
	# 				print board[x][y+1], board[x+1][y], board[x-1][y]
	# 				dropOrphan(board, x, y)
	# 	y += 1
	for x in range(BOARDWIDTH):
		continue_now = True
		for y in range (BOARDHEIGHT -2, -1, -1):
			if continue_now == True:
				if x == (BOARDWIDTH - 1): # if x is against the right wall
					if (board[x][y]) != BLANK and board[x][y] <= 11 and (board[x][y+1] == BLANK) and (board[x-1][y] == BLANK or board[x-1][y] > 11):
						dropOrphan(board, x, y)
				elif x == 0: # against the left wall
					if (board[x][y]) != BLANK and board[x][y] <= 11 and (board[x][y+1] == BLANK) and (board[x+1][y] == BLANK or board[x+1][y] > 11):
						dropOrphan(board, x, y)
				else:
					if (board[x][y]) != BLANK and board[x][y] <= 11 and (board[x][y+1] == BLANK) and (board[x+1][y] == BLANK or board[x+1][y] > 11) and (board[x-1][y] == BLANK or board[x-1][y] > 11):
						dropOrphan(board, x, y)



def removeCompletes(board, board_number):
	y = BOARDHEIGHT - 1 #start at bottom of board
	while y >= 0:
		setLocation = isCompleteSetHoriz(board, y, board_number)
		if setLocation:
			shiftRemainingYHoriz(board, setLocation[0], setLocation[1], y)
		else:
			y -= 1
	x = BOARDWIDTH - 1
	while x >= 0:
		setLocation = isCompleteSetVert(board, x, board_number)
		if setLocation:
			shiftRemainingXVert(board, x, setLocation[0], setLocation[1])
		else:
			x -= 1
	return 1

def convertToPixelCoords(boxx, boxy, board_number):
	# convert the given xy coordinates of the board to xy 
	#coords of the location on screen
	if board_number == 1:
		return (XMARGIN1 + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))
	elif board_number == 2:
		return (XMARGIN2 + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))

def drawBox(boxx, boxy, color, rotation, pill_half, board_number, pixelx=None, pixely=None, next_piece=False):
	#draw a single box at xy coordinates at the board. or if pixelx/pixely 
	#specified, draw to the pixel coords stored there (for next piece)
	if color == BLANK:
		return
	# if pixelx != None:
	# 	if board_number == 2:
	# 		pixelx += 1070
	if pixelx == None and pixely == None:
		pixelx, pixely = convertToPixelCoords(boxx, boxy, board_number)
	# pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely +1, 
	# 				BOXSIZE - 1, BOXSIZE - 1))
	# pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, 
	# 				BOXSIZE - 4, BOXSIZE - 4))
	# pygame.draw.arc(DISPLAYSURF, 
	# 			COLORS[color], 
	# 			(pixelx + 1, pixely +1, BOXSIZE - 1, BOXSIZE - 1),
	# 			math.radians(90),
	# 			math.radians(270),
	# 			3)
	# pygame.draw.circle(DISPLAYSURF, 
	# 			COLORS[color], 
	# 			(pixelx + (BOXSIZE/2), pixely + (BOXSIZE/2)),
	# 			10)
	pill_right = pygame.image.load('%sfs.png' % (color,))
	pillrect = (pixelx + 1, pixely +1, BOXSIZE, BOXSIZE)
	if rotation == 0:
		if next_piece:
			pillrect = (pixelx + 1, pixely + 1, BOXSIZE*2, BOXSIZE*2)
			if pill_half == 'A':
				pill_left = pygame.transform.rotozoom(pill_right, 180, 2)
				pill_left_flipped = pygame.transform.flip(pill_left, False, True)
				DISPLAYSURF.blit(pill_left_flipped, pillrect)
			else:
				pill_right2 = pygame.transform.scale2x(pill_right)
				DISPLAYSURF.blit(pill_right2, pillrect)
		else:
			if pill_half == 'A':
				pill_left = pygame.transform.rotate(pill_right, 180)
				pill_left_flipped = pygame.transform.flip(pill_left, False, True)
				DISPLAYSURF.blit(pill_left_flipped, pillrect)
			else:
				DISPLAYSURF.blit(pill_right, pillrect)
	elif rotation == 1:
		if pill_half == 'A':
			pill_bottom = pygame.transform.rotate(pill_right, 270)
			pill_bottom_flipped = pygame.transform.flip(pill_bottom, True, False)
			DISPLAYSURF.blit(pill_bottom_flipped, pillrect)
		else:
			pill_top = pygame.transform.rotate(pill_right, 90)
			DISPLAYSURF.blit(pill_top, pillrect)
	elif rotation == 2:
		if pill_half == 'B':
			pill_left = pygame.transform.rotate(pill_right, 180)
			pill_left_flipped = pygame.transform.flip(pill_left, False, True)
			DISPLAYSURF.blit(pill_left_flipped, pillrect)
		else:
			DISPLAYSURF.blit(pill_right, pillrect)
	elif rotation == 3:
		if pill_half == 'B':
			pill_bottom = pygame.transform.rotate(pill_right, 270)
			pill_bottom_flipped = pygame.transform.flip(pill_bottom, True, False)
			DISPLAYSURF.blit(pill_bottom_flipped, pillrect)
		else:
			pill_top = pygame.transform.rotate(pill_right, 90)
			DISPLAYSURF.blit(pill_top, pillrect)
		
	# pygame.draw.arc(DISPLAYSURF, 
	# 			COLORS[color], 
	# 			(pixelx + 1, pixely +1, BOXSIZE - 4, BOXSIZE - 4),
	# 			30,
	# 			120)

def drawBoxLanded(boxx, boxy, colorOrient, board_number, pixelx=None, pixely=None):
	# print 'landed box with boxx %s, boxy %s, colorOrient %s, board_number %s, pixelx %s, pixely %s' % (boxx, boxy, colorOrient, board_number, pixelx, pixely)
	if colorOrient == BLANK:
		return
	if pixelx:
		if board_number == 2:
			print 'hi'
			pixelx += 1070
		else:
			print 'one'
	if pixelx == None and pixely == None:
		pixelx, pixely = convertToPixelCoords(boxx, boxy, board_number)

	if colorOrient > 11: #must be a monster
		monster_pic = pygame.image.load('virus%sfs.png' % (colorOrient % 3,))
		monster_rect = (pixelx + 1, pixely +1, BOXSIZE, BOXSIZE)
		DISPLAYSURF.blit(monster_pic, monster_rect)
		# pygame.draw.circle(DISPLAYSURF, 
		# 					COLORS[colorOrient % 3], 
		# 					(pixelx + (BOXSIZE/2), pixely + (BOXSIZE/2)),
		# 					10)


	pill_right = pygame.image.load('%sfs.png' % (colorOrient % 3,))
	pillrect = (pixelx + 1, pixely +1, BOXSIZE, BOXSIZE)
	pill_rotation = colorOrient / 3
	if pill_rotation == 0:
		DISPLAYSURF.blit(pill_right, pillrect)
	elif pill_rotation == 1:
		pill_top = pygame.transform.rotate(pill_right, 90)
		DISPLAYSURF.blit(pill_top, pillrect)
	elif pill_rotation == 2:
		pill_left = pygame.transform.rotate(pill_right, 180)
		pill_left_flipped = pygame.transform.flip(pill_left, False, True)
		DISPLAYSURF.blit(pill_left_flipped, pillrect)
	elif pill_rotation == 3:
		pill_bottom = pygame.transform.rotate(pill_right, 270)
		pill_bottom_flipped = pygame.transform.flip(pill_bottom, True, False)
		DISPLAYSURF.blit(pill_bottom_flipped, pillrect)


def drawBoard(board, board_number):
	# draw the border around the board
	# pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, 
	# 	(BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

	#fill the background of the board
	# pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, 
	# 	BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
	if board_number == 1:
		background = pygame.image.load('fullscreen-twoplayer.jpg')
		backgroundRect = background.get_rect()
		DISPLAYSURF.blit(background, backgroundRect)

	#draw the individual boxes on the board
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if isinstance(board[x][y], int):
				drawBoxLanded(x, y, board[x][y], board_number)
				# if board[x][y] < 90:
				# 	print board[x][y], board_number
			else:
				drawBox(x, y, board[x][y], 0, 'A', board_number)

def drawGameCountImage(top_left_x, top_left_y):
	countImage = pygame.image.load('star-80.png')
	countImageRect = countImage.get_rect()
	countImageRect.topleft = (top_left_x, top_left_y)
	DISPLAYSURF.blit(countImage, countImageRect)



def drawStatus(score, level, monsters, board_number):
	global P1WINS, P2WINS
	# Player 1
	if board_number == 1:
		#draw the score text
		scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
		scoreRect = scoreSurf.get_rect()
		scoreRect.topleft = (110, 140)
		DISPLAYSURF.blit(scoreSurf, scoreRect)

		#draw the level text
		levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
		levelRect = levelSurf.get_rect()
		levelRect.topleft = (110, 200)
		DISPLAYSURF.blit(levelSurf, levelRect)

		#draw count remaining
		virusCountSurf = BIGVIRUSCOUNTFONT.render('%s' % monsters, True, TEXTCOLOR)
		virusCountRect = virusCountSurf.get_rect()
		virusCountRect.topleft = (145, 850)
		DISPLAYSURF.blit(virusCountSurf, virusCountRect)

		#draw text below count
		virusSurf = BASICFONT.render('remaining', True, TEXTCOLOR)
		virusRect = virusSurf.get_rect()
		virusRect.topleft = (70, 1000)
		DISPLAYSURF.blit(virusSurf, virusRect)


	elif board_number == 2:
		#draw the score text
		scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
		scoreRect = scoreSurf.get_rect()
		scoreRect.topleft = (WINDOWWIDTH - 350, 140)
		DISPLAYSURF.blit(scoreSurf, scoreRect)

		#draw the level text
		levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
		levelRect = levelSurf.get_rect()
		levelRect.topleft = (WINDOWWIDTH - 350, 200)
		DISPLAYSURF.blit(levelSurf, levelRect)

		#draw count remaining
		virusCountSurf = BIGVIRUSCOUNTFONT.render('%s' % monsters, True, TEXTCOLOR)
		virusCountRect = virusCountSurf.get_rect()
		virusCountRect.topleft = (WINDOWWIDTH - 310, 850)
		DISPLAYSURF.blit(virusCountSurf, virusCountRect)

		#draw text below count
		virusSurf = BASICFONT.render('remaining', True, TEXTCOLOR)
		virusRect = virusSurf.get_rect()
		virusRect.topleft = (WINDOWWIDTH - 380, 1000)
		DISPLAYSURF.blit(virusSurf, virusRect)

	#show game score visually

	#draw p1, p2
	p1Surf = BASICFONT.render('P1', True, TEXTCOLOR)
	p1Rect = p1Surf.get_rect()
	p1Rect.topleft = ((WINDOWWIDTH / 2) - 80, WINDOWHEIGHT / 2 + 300)
	DISPLAYSURF.blit(p1Surf, p1Rect)

	p2Surf = BASICFONT.render('P2', True, TEXTCOLOR)
	p2Rect = p2Surf.get_rect()
	p2Rect.topleft = ((WINDOWWIDTH / 2) + 15, WINDOWHEIGHT / 2 + 300)
	DISPLAYSURF.blit(p2Surf, p2Rect)


	#draw the boxes
	scoreBoxSurf = pygame.Surface((190, 270))
	scoreBoxRect = scoreBoxSurf.get_rect()
	scoreBoxRect.bottomleft = ((WINDOWWIDTH / 2) - 95, WINDOWHEIGHT / 2 + 285)
	scoreBoxSurf.fill(BLACK)
	scoreBoxSurf.set_alpha(150)
	DISPLAYSURF.blit(scoreBoxSurf, scoreBoxRect)

	#draw the lines
	one_third = (scoreBoxRect.bottomleft[1] - scoreBoxRect.topleft[1]) / 3
	pygame.draw.line(DISPLAYSURF, WHITE, scoreBoxRect.topleft, scoreBoxRect.bottomleft, 2)
	pygame.draw.line(DISPLAYSURF, WHITE, scoreBoxRect.topright, scoreBoxRect.bottomright, 2)
	pygame.draw.line(DISPLAYSURF, WHITE, scoreBoxRect.topleft, scoreBoxRect.topright, 2)
	pygame.draw.line(DISPLAYSURF, WHITE, scoreBoxRect.bottomleft, scoreBoxRect.bottomright, 2)
	pygame.draw.line(DISPLAYSURF, WHITE, scoreBoxRect.midtop, scoreBoxRect.midbottom, 2)
	pygame.draw.line(DISPLAYSURF, WHITE, (scoreBoxRect.topleft[0], scoreBoxRect.topleft[1] + one_third), (scoreBoxRect.topright[0], scoreBoxRect.topright[1] + one_third), 2)
	pygame.draw.line(DISPLAYSURF, WHITE, (scoreBoxRect.topleft[0], scoreBoxRect.topleft[1] + 2 * one_third), (scoreBoxRect.topright[0], scoreBoxRect.topright[1] + 2 * one_third), 2)

	#draw the stars
	if P1WINS:
		for win in range(P1WINS):
			drawGameCountImage((WINDOWWIDTH / 2) - 90, WINDOWHEIGHT / 2 + 200 - win * 90)

	if P2WINS:
		for win in range(P2WINS):
			drawGameCountImage((WINDOWWIDTH / 2) + 10, WINDOWHEIGHT / 2 + 200 - win * 90)
			

	#show game name
	nameSurf = pygame.image.load('marioMD_v1_green_small.png')
	nameRect = nameSurf.get_rect()
	nameRect.midtop = (WINDOWWIDTH/2, 60)
	DISPLAYSURF.blit(nameSurf, nameRect)


def drawPiece(piece, board_number, pixelx=None, pixely=None, next_piece=False):
	shapeToDraw = ORIENTATION[piece['rotation']]
	if pixelx == None and pixely == None:
		#if pixelx and y hasn't bee specified, use location 
		#stored in piece data structure
		pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'], board_number) # drawBox already handles the player 2, so this is always 1
	#draw each block that make up the pill
	for x in range(TEMPLATEWIDTH):
		for y in range(TEMPLATEHEIGHT):
			if shapeToDraw[y][x] == 'A':
				if not next_piece:
					drawBox(None, None, piece['A'], piece['rotation'], 'A', board_number, pixelx + (x * BOXSIZE), 
							pixely + (y * BOXSIZE), next_piece=next_piece)
				else:
					drawBox(None, None, piece['A'], piece['rotation'], 'A', board_number, pixelx + (x * BOXSIZE*2), 
							pixely + (y * BOXSIZE*2), next_piece=next_piece)
			elif shapeToDraw[y][x] == 'B':
				if not next_piece:
					drawBox(None, None, piece['B'], piece['rotation'], 'B', board_number, pixelx + (x * BOXSIZE), 
							pixely + (y * BOXSIZE), next_piece=next_piece)
				else:
					drawBox(None, None, piece['B'], piece['rotation'], 'B', board_number, pixelx + (x * BOXSIZE*2), 
							pixely + (y * BOXSIZE*2), next_piece=next_piece)

def drawNextPiece(piece, board_number):
	# Player 1
	if board_number == 1:
		# draw the next text
		px = 140
		py = 390
		nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
		nextRect = nextSurf.get_rect()
		nextRect.topleft = (150, 380)
		DISPLAYSURF.blit(nextSurf, nextRect)
		#draw the box behind piece
		boxrect = (px-7, py+70, (BOXSIZE*4+20), (BOXSIZE*2+20))
		DISPLAYSURF.fill(BLACK, boxrect)
		pygame.draw.rect(DISPLAYSURF, WHITE, boxrect, 2)
		#draw the next piece
		drawPiece(piece, 1, pixelx=px, pixely=py, next_piece=True)
	# Player 2
	elif board_number == 2:
		# draw the next text
		px = 1610
		py = 390
		nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
		nextRect = nextSurf.get_rect()
		nextRect.topleft = (WINDOWWIDTH - 310, 380)
		DISPLAYSURF.blit(nextSurf, nextRect)
		#draw the box behind the piece
		boxrect = (px-7, py+70, (BOXSIZE*4+20), (BOXSIZE*2+20))
		DISPLAYSURF.fill(BLACK, boxrect)
		pygame.draw.rect(DISPLAYSURF, WHITE, boxrect, 2)
		#draw the next piece
		drawPiece(piece, 2, pixelx=px, pixely=py, next_piece=True)

if __name__ == '__main__':
	main()