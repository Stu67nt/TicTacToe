"""
TODO:
 1) Proper win/tie screen.
 Prio change: Refactoring and commenting
 2) Main Menu:\n
	i) Local Multiplayer - Regular tic tac toe with no AI.\n
	ii) Single Player - Plays against AI. Will bring up choice of against easy or hard AI.\n
	iii) Settings - Allows adding custom music, Volume slider, Custom colour scheme.
 3) Single Player vs Random input AI.
 4) Unbeatable AI.\n
 5) Game Modes:\n
 Stealing spaces. Can be done once per game within the first 2 turns.\n
 Infinite sized boards. (more for proof of concept) \n
 Tic Tac Toe but you do WarioWare style minigames for each square.
"""
"""
General design choices:
You will see the array dirty_rects a lot so I figured I should explain it here. What it does it act as a way of only
what has updated on the screen rather than literally everything, another performance enhancement was to only attempt
and update when anything could of feasibly changed such as when a click is made. This means that useless updates where
no changes are made aren't done leading to upwards of 25x performance.

width_unit and height_unit: These act a bit like columns and rows for placement of squares. This is to make it so the
squares will still fill the window no matter the window size. Furthermore this mkaes the program easily scalable to
larger board sizes such as 4x4, 5x5, ect.
"""

import sys
import pygame
import random
import pathlib


# Draws the grid stucture for the board.
def draw_grid(screen, width_unit, height_unit, ln_col, bg_col):
	dirty_rects = [screen.fill(bg_col),
	               pygame.draw.line(screen, ln_col, (width_unit, 0), (width_unit, (height_unit * 3)), 3),
	               pygame.draw.line(screen, ln_col, ((2 * width_unit), 0), ((2 * width_unit), (height_unit * 3)), 3),
	               pygame.draw.line(screen, ln_col, (0, height_unit), ((width_unit * 3), height_unit), 3),
	               pygame.draw.line(screen, ln_col, (0, (2 * height_unit)), ((width_unit * 3), (2 * height_unit)), 3)]
	return dirty_rects  # Grid is drawn to screen out of function so fade function doesn't bug out.

def finish_screen(screen, width_unit, height_unit, ln_col, bg_col, turn_piece=""):
	if turn_piece == "X":
		text = "O wins! Press R to play again!"
		font = pygame.font.SysFont("comic sans", 20)
		text_settings = font.render(text, True, "black")
		dirty_rects = [screen.fill(bg_col),
		               pygame.draw.line(screen, ln_col, (width_unit + 35, height_unit + 20),
		                                ((width_unit * 2) - 35, (height_unit * 2) - 20), width=30),
		               pygame.draw.line(screen, ln_col, ((width_unit * 2) - 35, height_unit + 20),
		                                (width_unit + 35, (height_unit * 2) - 20), width=30),
		               screen.blit(text_settings, (width_unit - 13, height_unit * 2))]
		return dirty_rects
	
	elif turn_piece == "O":
		text = "O wins! Press R to play again!"
		font = pygame.font.SysFont("comic sans", 20)
		text_settings = font.render(text, True, "black")
		dirty_rects = [screen.fill(bg_col),
		               pygame.draw.circle(screen, ln_col,
		        (width_unit + (0.5 * width_unit), height_unit + (0.5 * height_unit)), width=30, radius=100),
		               screen.blit(text_settings, (width_unit - 13, height_unit * 2))]  # / num is for positioning
		return dirty_rects
	
	else:
		text = "Tie! Press R to Start a new game at any time."
		font = pygame.font.SysFont("comic sans", 20)
		text_settings = font.render(text, True, "black")
		dirty_rects = [screen.fill(bg_col),
		               screen.blit(text_settings, ((3*width_unit) / 5, (3*height_unit) / 5))]
		return dirty_rects
	
# Checks all possible win conditions
def check_win(grid):
	for row in grid:  # Checks rows
		if (row[0] == row[1]) and (row[1] == row[2]) and (row[0] != ""): return True
	
	for row in range(0, len(grid)):  # Checks columns
		if (grid[0][row] == grid[1][row]) and (grid[1][row] == grid[2][row]) and (grid[0][row] != ""): return True
	
	if (grid[0][0] == grid[1][1]) and (grid[1][1] == grid[2][2]) and (
		grid[0][0] != ""): return True  # Checks L to R diagonal
	
	if (grid[0][2] == grid[1][1]) and (grid[1][1] == grid[2][0]) and (
		grid[0][2] != ""): return True  # Checks R to L diagonal
	
	return False  # No win conditions were met; therefore, there isn't a win yet.

# Checks if all cells full.
def check_tie(grid):
	# We iterate through each cell in the board and check if it is empty; if it is, then the game isn't tied
	for row in grid:
		for item in row:
			if item == "":
				return False
	return True  # This means that the game is done and no one won therefore must be a tie.

# When a Left click input is sent, it manages it appropriately as needed.
def check_click(screen, width_unit, height_unit, grid, turn_piece, square_state, turn, allow_input, ln_col):
	if allow_input:
		mouse_pos = pygame.mouse.get_pos()  # Returns a tuple with x and y coords of mouse respectively.
		i = 0  # Index for access to array which says if each square is full or not.
		y_axis = 0  # Acts as an index for finding out which squre the loop is on
		dirty_rects = []
		
		# Iterating through each row on the grid.
		for row in grid:
			x_axis = 0  # This one has to be inside the for loop becasue for each row it has to be reset.
			for item in range(0, len(row)):  # Iterating through each item within the row
				if (((width_unit * x_axis) <= mouse_pos[0] <= (width_unit * (x_axis + 1))) and
					((height_unit * y_axis) <= mouse_pos[1] <= (height_unit * (y_axis + 1))) and
					square_state[i]):
					grid[y_axis][x_axis] = turn_piece
					turn += 1
					square_state[i] = False
					pygame.display.update(draw_current_piece(screen, width_unit, height_unit, x_axis, y_axis, turn_piece, ln_col))
				x_axis += 1  # Moving onto the next item in row
				i += 1
			y_axis += 1  # Mobing onto the next row.
	return turn

def draw_current_piece(screen, width_unit, height_unit, x_axis, y_axis, turn_piece, ln_col):
	if turn_piece == "X":
		piece = [pygame.draw.line(screen, ln_col, ((width_unit * x_axis) + 35, (height_unit * y_axis) + 20),
		                ((width_unit * (1 + x_axis)) - 35, (height_unit * (y_axis + 1)) - 20), width=30),
		         pygame.draw.line(screen, ln_col, ((width_unit * (1 + x_axis) - 35), (height_unit * y_axis) + 20),
		                ((width_unit * x_axis) + 35, (height_unit * (1 + y_axis)) - 20), width=30)]
	elif turn_piece == "O":
		piece = [pygame.draw.circle(screen, ln_col, ((width_unit * x_axis) + (0.5 * width_unit),
		                            (height_unit * y_axis) + (0.5 * height_unit)), radius=100, width=30)]
	elif turn_piece == "":
		piece = []
	return piece

# Responsible for ending the game and checking if gaem has ended.
def control_game_state(grid, turn_piece, screen, screen_width, screen_height, width_unit, height_unit, bg_col, ln_col):
	if (check_win(grid)) and (turn_piece == "X"):
		fade(screen, screen_width, screen_height, ln_col, bg_col, grid, turn_piece)
		dirty_rects = finish_screen(screen, width_unit, height_unit, ln_col, bg_col, "X")
		pygame.display.update(dirty_rects)
		return False  # Game is still running in the background, so I disable input upon deciding game's outcome.
	
	elif (check_win(grid)) and (turn_piece == "O"):
		fade(screen, screen_width, screen_height, ln_col, bg_col, grid, turn_piece)
		dirty_rects = finish_screen(screen, width_unit, height_unit, ln_col, bg_col, "O")
		pygame.display.update(dirty_rects)
		return False
	
	elif check_tie(grid):
		fade(screen, screen_width, screen_height, ln_col, bg_col, grid)
		dirty_rects = finish_screen(screen, width_unit, height_unit, ln_col, bg_col, "")
		pygame.display.update(dirty_rects)
		return False
	else:
		allow_input = True  # The game is not tied or won, so the game's outcome is not decided yet.
		return allow_input

def fade(screen, screen_width, screen_height, ln_col, bg_col, grid, turn_piece=""):
	fade = pygame.Surface((screen_width, screen_height))
	width_unit = screen_width/3
	height_unit = screen_height/3
	fade.fill("#000000")
	y_axis = 0
	for alpha in range(0, 256, 4):  # Using RGB nums instead of hexcodes because easier to manipulate.
		fade.set_alpha(alpha)
		dirty_rects = draw_grid(screen, (screen_width/3), (screen_height/3), ln_col, bg_col)
		for row in grid:
			x_axis = 0
			for square in row:
				current_piece = grid[y_axis][x_axis]
				rects_list = draw_current_piece(screen, (screen_width/3), (screen_height/3), x_axis, y_axis, current_piece, ln_col)
				for item in rects_list:
					dirty_rects.append(item)
				x_axis += 1
			y_axis += 1
		dirty_rects.append(screen.blit(fade, (0, 0)))
		pygame.display.update(dirty_rects)
		pygame.time.delay(8)
		y_axis = 0
	for alpha in range(256, -1, -4):  # Using RGB nums instead of hexcodes because easier to manipulate.
		fade.set_alpha(alpha)
		dirty_rects = finish_screen(screen, width_unit, height_unit, ln_col, bg_col, turn_piece)
		dirty_rects.append(screen.blit(fade, (0, 0)))
		pygame.display.update(dirty_rects)
		pygame.time.delay(8)

def background_audio():
	# Locates where the .exe file is, then adds \Audio as that would be the location of the audio files.
	path = str(pathlib.Path.cwd()) + r"\Audio"
	# r is needed before the string, so the \ works at the beginning of the string.
	audio_list, weights = [r"\Careless_Whisper.wav", r"\gabi_song.mp3", r"\Why_Oh_Why.wav",
	                       r"\gabi_piano.wav", r"\rats.mp3"], [83.99, 10, 1, 5, 0.01]
	# Song Selected from audio_list using the weights then appended to
	sound_file_path = path + str(random.choices(audio_list, weights=weights, k=1)[0])
	pygame.mixer.init()
	pygame.mixer.music.load(sound_file_path)
	pygame.mixer.music.play(loops=-1)  # -1 means infinite loops

def local_multiplayer(screen, clock, screen_width, screen_height, width_unit, height_unit,
                      ln_col, bg_col):
	# Board setup
	grid = [["", "", ""], ["", "", ""], ["", "", ""]]
	square_state = [True, True, True, True, True, True, True, True, True]
	turn = 0
	allow_input = True
	
	pygame.display.update(draw_grid(screen, width_unit, height_unit, ln_col, bg_col))
	while True:
		mouse_pos, click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_r:  # Resetting game state.
					grid = [["", "", ""], ["", "", ""], ["", "", ""]]
					square_state = [True, True, True, True, True, True, True, True, True]
					turn = 0
					allow_input = True
					pygame.display.update(draw_grid(screen, width_unit, height_unit, ln_col, bg_col))
		
		if allow_input:  # Prevents placing when the game is over. Useful for future game modes where this matters.
			# Determines who is to place
			if (turn % 2) == 0:
				turn_piece = "X"
			else:
				turn_piece = "O"
			
			if click[0]:  # Changes can only be done with a click, so we only attempt updates when there is one.
				turn = check_click(screen, width_unit, height_unit, grid, turn_piece, square_state, turn,
				                   allow_input, ln_col)
				allow_input = control_game_state(grid, turn_piece, screen, screen_width, screen_height,
				                                 width_unit, height_unit, bg_col, ln_col)
		clock.tick(60)

def base_window():
	# Defining window settings
	pygame.init()
	screen_width, screen_height = 720, 720
	screen_width_unit, screen_height_unit = (screen_width / 3), (screen_height / 3)
	screen = pygame.display.set_mode((screen_width, screen_height))
	clock = pygame.time.Clock()
	background_colour, line_colour = "#0099ff", "#0064ff"
	
	# This is going to be a main menu eventually, so we want a way for the x button to work there.
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	
	local_multiplayer(screen, clock, screen_width, screen_height, screen_width_unit, screen_height_unit,
	                  line_colour, background_colour)

if __name__ == "__main__":
	# Ensures program doesn't crash if user deletes a soundfile.
	try:
		background_audio()
	except pygame.error as err:
		print(err)
		print("No background music will play. Redownload it from the github if you want it.")
	base_window()
