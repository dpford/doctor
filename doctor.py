# Dr. Mario
# By Dan Ford dpford@gmail.com
# http://github.com/dpford

import random
import time
import pygame
import sys
import math

from pygame.locals import *

FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
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
	global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, complete
	pygame.mixer.pre_init(44100, -16, 2, 512)
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
	BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
	complete = pygame.mixer.Sound('doctor_music/doctor_sonic.ogg')
	pygame.display.set_caption('Dr. Mario')

	showTextScreen('Dr. Mario')
	while True: #game loop
		pygame.mixer.music.load('doctor_music/doctor_fever_guitar.ogg')
		pygame.mixer.music.play(-1, 0.0)
		runGame()
		pygame.mixer.music.fadeout(1000)
		showTextScreen('Game Over')
		pygame.mixer.music.load('doctor_music/08_-_Dr._Mario_-_NES_-_VS_Game_Over.ogg')
		pygame.mixer.music.play(-1, 0.0)

def runGame():
	board = getInitialBoard()
	lastMoveDownTime = time.time()
	lastMoveSidewaysTime = time.time()
	lastFallTime = time.time()
	movingDown = False
	movingLeft = False
	movingRight = False
	score = 0
	level, fallFreq = calculateLevelAndFallFreq(score)

	fallingPiece = getNewPiece()
	nextPiece = getNewPiece()

	while True: #main game loop
		if fallingPiece == None:
			# No falling pill in play, so put one at the top
			fallingPiece = nextPiece
			nextPiece = getNewPiece()
			lastFallTime = time.time() #reset lastFallTime

			if not isValidPosition(board, fallingPiece):
				return # can't find a new pill, so you lose!

		checkForQuit()
		for event in pygame.event.get(): #event handling loop
			if event.type == KEYUP:
				if (event.key == K_p): # pause game
					DISPLAYSURF.fill(BGCOLOR)
					pygame.mixer.music.stop()
					showTextScreen('Paused') #until a key is pressed
					pygame.mixer.music.play(-1, 0.0)
					lastFallTime = time.time()
					lastMoveDownTime = time.time()
					lastMoveSidewaysTime = time.time()
				elif (event.key == K_LEFT or event.key == K_a):
					movingLeft = False
				elif (event.key == K_RIGHT or event.key == K_d):
					movingRight = False
				elif (event.key == K_DOWN or event.key == K_s):
					movingDown = False

			elif event.type == KEYDOWN:
				# moving block sideways
				if (event.key == K_LEFT or event.key == K_a) and \
					isValidPosition(board, fallingPiece, adjX=-1):
				 	fallingPiece['x'] -= 1
				 	movingLeft = True
				 	movingRight = False
				 	lastMoveSidewaysTime = time.time()

				elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
				 	fallingPiece['x'] += 1
				 	movingRight = True
				 	movingLeft = False
				 	lastMoveSidewaysTime = time.time()

				 #rotating the pill (if there's room)
				elif (event.key == K_UP or event.key == K_z):
					fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % 4
					if not isValidPosition(board, fallingPiece):
						fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % 4
				elif (event.key ==K_x): #other direction
					fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % 4
					if not isValidPosition(board, fallingPiece):
						fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % 4
				# drop pill faster with down key
				elif (event.key == K_DOWN or event.key == K_s):
					movingDown = True
					if isValidPosition(board, fallingPiece, adjY=1):
						fallingPiece['y'] += 1
					lastMoveDownTime = time.time()

		if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
			if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
				fallingPiece['x'] -= 1
			elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
				fallingPiece['x'] += 1
			lastMoveSidewaysTime = time.time()

		if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and isValidPosition(board, fallingPiece, adjY=1):
			fallingPiece['y'] += 1
			lastMoveDownTime = time.time()

		#let the pill fall down on its own
		if time.time() - lastFallTime > fallFreq:
			# see if pill has landed
			if not isValidPosition(board, fallingPiece, adjY=1):
				# it's landed, add to board
				addToBoard(board, fallingPiece)
				score += removeCompletes(board)
				findOrphans(board)
				score += removeCompletes(board)
				findOrphans(board)
				score += removeCompletes(board)
				level, fallFreq = calculateLevelAndFallFreq(score)
				fallingPiece = None
			else:
				fallingPiece['y'] += 1
				lastFallTime = time.time()

		# draw everything on the screen
		DISPLAYSURF.fill(BGCOLOR)
		drawBoard(board)
		drawStatus(score, level)
		drawNextPiece(nextPiece)
		if fallingPiece != None:
			drawPiece(fallingPiece)

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

	for event in pygame.event.get([KEYDOWN, KEYUP]):
		if event.type == KEYDOWN:
			continue
		return event.key
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
	pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
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


def addToBoard(board, piece):
	# fill in the board based on piece's location
	print piece
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
				print piece['A']
			elif ORIENTATION[piece['rotation']][y][x] == 'B':
				if piece['rotation'] == 0:
					put_on_board = piece['B']
				elif piece['rotation'] == 1:
					put_on_board = piece['B'] + 3
				elif piece['rotation'] == 2:
					put_on_board = piece['B'] + 6
				elif piece['rotation'] == 3:
					put_on_board = piece['B'] + 9
				print "put on board B is " + str(put_on_board)
				board[x + piece['x']][y + piece['y']] = put_on_board

def getInitialBoard():
	board = []
	for i in range(BOARDWIDTH):
		board.append([BLANK] * BOARDHEIGHT)
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

def isCompleteSetHoriz(board, y):
	count = 0
	last_color = -1
	for x in range(BOARDWIDTH):
		if board[x][y] != BLANK:
			this_color = board[x][y] % 3
			if (this_color == last_color) or (last_color == -1):
				last_color = this_color
				count += 1
			else:
				if count >= 4:
					complete.play()
					return x-1, count
				else:
					last_color = this_color
					count = 1
		else:
			if count >= 4:
				complete.play()
				return x-1, count
			else:
				count = 0
		if x == (BOARDWIDTH - 1):
			if count >= 4:
				complete.play()
				return x, count
	return False

def isCompleteSetVert(board, x):
	count = 0
	last_color = -1
	for y in range(BOARDHEIGHT):
		if board[x][y] != BLANK:
			this_color = board[x][y] % 3
			if (this_color == last_color) or (last_color == -1):
				last_color = this_color
				count += 1
			else:
				if count >= 4:
					complete.play()
					return y-1, count
				else:
					last_color = this_color
					count = 1
		else:
			if count >= 4:
				complete.play()
				return y-1, count
			else:
				count = 0
		if y == (BOARDHEIGHT - 1):
			if count >= 4:
				complete.play()
				return y, count
	if count >= 4:
		print "fucked up, x is ", x
	return False

def shiftRemainingYHoriz(board, x, count, y):
	print "x is " + str(x)
	print "y is " + str(y)
	print "count is " + str(count)
	for pullDownY in range(y, 0, -1):
		for x_1 in range(x, x-count, -1):
			board[x_1][pullDownY] = board[x_1][pullDownY-1]

def shiftRemainingXVert(board, x, y, count):
	print "y is " + str(y)
	for pullDownY in range(y, count, -1):
		board[x][pullDownY] = board[x][pullDownY-count]

def dropOrphan(board, x, y):
	board[x][y + 1] = board[x][y]
	board[x][y] = BLANK
	depth = y + 2
	while depth < (BOARDHEIGHT-1) and (board[x][depth] == BLANK):
		board[x][depth] = board[x][depth-1]
		board[x][depth-1] = BLANK
		depth += 1
		print 'hi'

def findOrphans(board):
	y = 0
	while y < (BOARDHEIGHT - 1):
		for x in range(0, BOARDWIDTH):
			if x == (BOARDWIDTH - 1): # if x is against the right wall
				if (board[x][y]) != BLANK and (board[x][y+1] == BLANK) and (board[x-1][y] == BLANK):
					dropOrphan(board, x, y)
			elif x == 0:
				if (board[x][y]) != BLANK and (board[x][y+1] == BLANK) and (board[x+1][y] == BLANK):
					dropOrphan(board, x, y)
			else:
				if (board[x][y]) != BLANK and (board[x][y+1] == BLANK) and (board[x+1][y] == BLANK) and (board[x-1][y] == BLANK):
					print board[x][y+1], board[x+1][y], board[x-1][y]
					dropOrphan(board, x, y)
		y += 1

def removeCompletes(board):
	y = BOARDHEIGHT - 1 #start at bottom of board
	while y >= 0:
		setLocation = isCompleteSetHoriz(board, y)
		if setLocation:
			print "horiz"
			shiftRemainingYHoriz(board, setLocation[0], setLocation[1], y)
			print 'complete line y, y is %s, setLocation is %s' % (y, setLocation)
		else:
			y -= 1
	x = BOARDWIDTH - 1
	while x >= 0:
		setLocation = isCompleteSetVert(board, x)
		if setLocation:
			print "vert"
			shiftRemainingXVert(board, x, setLocation[0], setLocation[1])
		else:
			x -= 1
	return 1

def convertToPixelCoords(boxx, boxy):
	# convert the given xy coordinates of the board to xy 
	#coords of the location on screen
	return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))

def drawBox(boxx, boxy, color, rotation, pill_half, pixelx=None, pixely=None):
	#draw a single box at xy coordinates at the board. or if pixelx/pixely 
	#specified, draw to the pixel coords stored there (for next piece)
	if color == BLANK:
		return
	if pixelx == None and pixely == None:
		pixelx, pixely = convertToPixelCoords(boxx, boxy)
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
	pill_right = pygame.image.load('%s.png' % (color,))
	pillrect = (pixelx + 1, pixely +1, BOXSIZE, BOXSIZE)
	if rotation == 0:
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

def drawBoxLanded(boxx, boxy, colorOrient, pixelx=None, pixely=None):
	if colorOrient == BLANK:
		return
	if pixelx == None and pixely == None:
		pixelx, pixely = convertToPixelCoords(boxx, boxy)

	pill_right = pygame.image.load('%s.png' % (colorOrient % 3,))
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


def drawBoard(board):
	# draw the border around the board
	# pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, 
	# 	(BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

	#fill the background of the board
	# pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, 
	# 	BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
	background = pygame.image.load('my_checkerboard.jpg')
	backgroundRect = background.get_rect()
	DISPLAYSURF.blit(background, backgroundRect)

	#draw the individual boxes on the board
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if isinstance(board[x][y], int):
				drawBoxLanded(x, y, board[x][y])
			else:
				drawBox(x, y, board[x][y], 0, 'A')

def drawStatus(score, level):
	#draw the score text
	scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
	scoreRect = scoreSurf.get_rect()
	scoreRect.topleft = (WINDOWWIDTH - 150, 20)
	DISPLAYSURF.blit(scoreSurf, scoreRect)

	#draw the level text
	levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
	levelRect = levelSurf.get_rect()
	levelRect.topleft = (WINDOWWIDTH - 150, 50)
	DISPLAYSURF.blit(levelSurf, levelRect)

def drawPiece(piece, pixelx=None, pixely=None):
	shapeToDraw = ORIENTATION[piece['rotation']]
	if pixelx == None and pixely == None:
		#if pixelx and y hasn't bee specified, use location 
		#stored in piece data structure
		pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])
	#draw each block that make up the pill
	for x in range(TEMPLATEWIDTH):
		for y in range(TEMPLATEHEIGHT):
			if shapeToDraw[y][x] == 'A':
				drawBox(None, None, piece['A'], piece['rotation'], 'A', pixelx + (x * BOXSIZE), 
						pixely + (y * BOXSIZE))
			elif shapeToDraw[y][x] == 'B':
				drawBox(None, None, piece['B'], piece['rotation'], 'B', pixelx + (x * BOXSIZE), 
						pixely + (y * BOXSIZE))

def drawNextPiece(piece):
	# draw the next text
	nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
	nextRect = nextSurf.get_rect()
	nextRect.topleft = (WINDOWWIDTH - 120, 80)
	DISPLAYSURF.blit(nextSurf, nextRect)
	#draw the next piece
	drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)

if __name__ == '__main__':
	main()