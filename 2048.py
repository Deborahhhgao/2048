from copy import deepcopy
from multiprocessing.sharedctypes import copy
import tkinter as tk
from tkinter import BOTH, BOTTOM, E, TOP, W, Frame, messagebox
from support import *

class Model():
	""" The overall model for a game of 2048. """
	def __init__(self) -> None:
		""" Constructs a new 2048 model instance. """
		self.new_game()

	def new_game(self) -> None:
		""" Sets up a new game. """
		self._matrix = [[None]*NUM_COLS for i in range(NUM_ROWS)]
		self._score = 0
		self._undo_time = MAX_UNDOS
		self._last_matrix = deepcopy(self._matrix)
		self.add_tile()
		self.add_tile()

	def get_tiles(self) -> list[list[Optional[int]]]:
		""" Return the current tiles matrix. """
		return self._matrix

	def add_tile(self) -> None:
		""" Randomly generate a new tile at an empty location 
		    and add it to the current tiles matrix. 
		"""
		# add tiles in grids which has no number
		if any(None in row for row in self._matrix): 
			random_tile = generate_tile(self._matrix)
			num_col = random_tile[0][1]
			num_row = random_tile[0][0]
			self._matrix[num_row][num_col] = random_tile[1]

	def move_left(self) -> None:
		""" Moves all tiles to their left extreme, 
		    merging where necessary. 
		"""
		self._matrix = stack_left(self._matrix)
		(self._matrix, self._add_score) = combine_left(self._matrix)
		self._matrix = stack_left(self._matrix)
		self._score += self._add_score

	def move_right(self) -> None:
		""" Moves all tiles to their right extreme, 
		    merging where necessary. 
		"""
		self._matrix = reverse(self._matrix)
		self.move_left()
		self._matrix = reverse(self._matrix)
    
	def move_up(self) -> None:
		""" Moves all tiles to their top extreme, 
		    merging where necessary. 
		"""
		self._matrix = transpose(self._matrix)
		self.move_left()
		self._matrix = transpose(self._matrix)

	def move_down(self) -> None:
		""" Moves all tiles to their bottom extreme, 
		    merging where necessary. 
		"""
		self._matrix = transpose(self._matrix)
		self.move_right()
		self._matrix = transpose(self._matrix)

	def attempt_move(self, move: str) -> bool:
		""" Makes the appropriate move according to the move string provided.

		Parameters:
		    move: one of wsad, representing the four directions of up, down, left and right.

		Returns: 
		    True if the move resulted in a change to the game state, else False.
		"""
		self._last_matrix =deepcopy(self._matrix)
		if move == LEFT:
			self.move_left()
		elif move == UP:
			self.move_up()
		elif move == DOWN:
			self.move_down()
		elif move == RIGHT:
			self.move_right()
		if self._last_matrix == self._matrix:
			return False
		return True

	def get_score(self) -> int:
		""" Returns the current score for the game. """
		return self._score

	def get_undos_remaining(self) -> int:
		""" Return the number of undos the player has remaining. """
		return self._undo_time
	
	def use_undo(self) -> None:
		""" Attempts to undo the previous move. 
		    If the player does not have any undos remaining,
			or they are back at the initial state, this method should do nothing.
		"""
		if self._undo_time > 0:
			self._matrix = self._last_matrix
			self._undo_time -= 1

	def has_won(self) -> bool:
		""" Returns True if the game has been won, else False. """
		if any(2048 in row for row in self._matrix):
			return True
		return False
    
	def has_lost(self) -> bool:
		""" Returns True if the game has been lost, else False. """
		if any(None in row for row in self._matrix):
			return False
		for row in range (NUM_ROWS - 1):
			for col in range(NUM_COLS - 1):
				if self._matrix[row][col] == self._matrix[row + 1][col] or\
					self._matrix[row][col] == self._matrix[row][col + 1]:
					return False
		for row in range(NUM_ROWS - 1):
			if self._matrix[row][NUM_COLS - 1] == self._matrix[row + 1][NUM_COLS - 1]:
				return False
		for col in range(NUM_COLS - 1):
			if self._matrix[NUM_ROWS - 1][col] == self._matrix[NUM_ROWS - 1][col + 1]:
				return False
		return True


class StatusBar(tk.Frame):
	""" Inherits from tk.Frame, and represents information 
	    about score and remaining undos, 
	    as well as a button to start a new game 
		and a button to undo the previous move.
	"""
	def __init__(self, master, **kwargs) -> None:
		SCORE_FONT = ("Arial", 25)
		""" Sets up self to be an instance of tk.Frame,
            and sets up inner frames, labels and buttons in this status bar. 
		
		Parameters:
		    master: The master frame of StatusBar.
		"""
		super().__init__(master)

		# Main frame for score label and score number
		self._score_frame = tk.Frame(
            self,
		    width = 120,
		    height = 60,
			bg = "#bbada0"
            )
		# Create the 'SCORE' text label
		self._score_label = tk.Label(
			self._score_frame,
			text = "SCORE",
			font = SCORE_FONT,
			bg = BACKGROUND_COLOUR,
			fg = "#ccc0b3"
			).pack()
		# Create the score number label
		self._score_num = tk.Label(
			self._score_frame,
			text = 0,
			font = SCORE_FONT,
			bg = BACKGROUND_COLOUR,
			fg = "#f5ebe4"
			)
		self._score_num.pack()
		# Pack the main score frame
		self._score_frame.pack(
			anchor = tk.W,
			side = tk.LEFT,
		    padx = 10,
		    pady = 10,
			fill = tk.BOTH,
			expand = tk.YES,
			)

		# Main frame for undo label and undo remaining number
		self._undo_frame = tk.Frame(
			self,
		    width = 120,
		    height = 60,
			bg = "#bbada0"
			)
		# Create the the 'UNDO' text label
		self._undo_label = tk.Label(
			self._undo_frame,
			text = "UNDOS",
			font = SCORE_FONT,
			bg = BACKGROUND_COLOUR,
			fg = "#ccc0b3"
			)
		self._undo_label.pack()
		# Create the undo number label
		self._undo_num = tk.Label(
			self._undo_frame,
			text = MAX_UNDOS,
			font = SCORE_FONT,
			bg = BACKGROUND_COLOUR,
			fg = "#f5ebe4"
			)
		self._undo_num.pack()
		# Pack the main undo frame 
		self._undo_frame.pack(
			anchor = tk.W,
			side = tk.LEFT,
		    padx = 10,
		    pady = 10,
			fill = tk.BOTH,
			expand = tk.YES
			)

		# Main frame for new game button and undo button
		self._button_frame = tk.Frame(
			self,
		    width = 120,
		    height = 60
			)
		# Create the new game button
		self._new_game = tk.Button(
			self._button_frame,
			text = "New Game",
			)
		self._new_game.pack(side = tk.TOP)
		# Create the undo button
		self._undo = tk.Button(
			self._button_frame,
			text = "Undo Move"
			)
		self._undo.pack(side = tk.BOTTOM)
		# Pack the main button frame
		self._button_frame.pack(
			side = tk.LEFT,
		    padx = 10,
			anchor = tk.W,
		    pady = 10
			)

	def redraw_infos(self, score: int, undos: int) -> None:
		""" Updates the score and undos labels to reflect the information given. 

		Parameters:
		    score: The current score for the game.
			undos: The number of undos the player has remaining.
		"""
		self._score_num['text'] = score
		self._undo_num['text'] = undos

	def set_callbacks(self, new_game_command: callable, undo_command: callable) -> None:
		""" Sets the commands for the new game 
		    and undo buttons to the given commands.
		
		Parameters: 
		    new_game_command: The command to start a new game.
			undo_command: The command to use undo.
		"""
		self._new_game['command'] = new_game_command
		self._undo['command'] = undo_command


class GameGrid(tk.Canvas):
	""" A view class which inherits from tk.Canvas 
	    and represents the 4x4 grid. 
	"""
	BOX_WIDTH = BOARD_WIDTH/NUM_ROWS
	BOX_HEIGHT = BOARD_HEIGHT/NUM_COLS

	def __init__(self, master, **kwargs) -> None:
		""" Sets up a new GameGrid in the master window.
		    The canvas is 400 pixels wide and 400 pixels tall.

		Parameters:
		    master: The master canvas of GameGrid.
		"""
		super().__init__(
			master,
			width = BOARD_WIDTH,
			height = BOARD_HEIGHT,
			bg = BACKGROUND_COLOUR,
			**kwargs
		)

	def _draw_number(self, position: tuple[int, int], number: int) -> None:
		""" Draws number in tiles.
            
		Parameters:
		    position: The position to draw the number.
			number: The number to draw.
		"""
		x, y = self._get_midpoint(position)
		self.create_text(
            x,y,	
			text = str(number),
			fill = FG_COLOURS.get(number),
			font = TILE_FONT
			)  
        
	def _get_bbox(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
		""" Return the top left corner of the position 
		    and the bottom right corner of the cell.

		Parameters:
		    position: In the form of (row, column)

		Returns:
		    Bounding box for the (row, column) position, 
			in the form (x_min, y_min, x_max, y_max).
		"""
		x_min = BUFFER + (self.BOX_WIDTH * position[1])
		y_min = BUFFER + (self.BOX_HEIGHT * position[0])
		x_max = x_min + (self.BOX_WIDTH - BUFFER)
		y_max = y_min + (self.BOX_HEIGHT - BUFFER)
		return (x_min, y_min, x_max, y_max)

	def _get_midpoint(self, position: tuple[int, int]) ->tuple[int, int]:
		""" Return the graphics coordinates for the center of the cell.

		Parameters:
		    position: The given (row, col) position.
		"""
		(x_min, y_min, x_max, y_max) = self._get_bbox(position)
		x = (x_min + x_max)//2
		y = (y_min + y_max)//2
		return (x,y)

	def clear(self) -> None:
		""" Clears all items. """
		self.delete("all")

	def redraw(self, tiles: list[list[Optional[int]]]) -> None:
		""" Clears and redraws the entire grid based on the given tiles.

		Parameters:
		    tiles: The current tiles matrix of the game.
		"""
		self.clear()
		# A for loop that creates the appropriate rectangle and numbers at each position
		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):
				(x_min, y_min, x_max, y_max) = self._get_bbox([row, col])
				self.create_rectangle(
					x_min, y_min,
			        x_max, y_max,
			        fill = COLOURS.get(tiles[row][col]), 
			        width = 0
                )
				if tiles[row][col] != None:
					self._draw_number([row, col], tiles[row][col])


class Game():
	""" A class for the controller. """
	def __init__(self, master: tk.Tk) -> None:
		""" Constructs a new 2048 game.
		    Creates a Model instance, sets the window title, 
			creates the title label and create instances 
			of any view classes packed into master,
			binds key press events to an appropriate handler, 
			and causes the initial GUI to be drawn.
		
		Parameters:
		    master: The master window of Game.
		"""
		self._model = Model()
		self._master = master
		self._master.title("2048")
		self._title = tk.Label(
			self._master,
			text = "2048",
			bg = "yellow",
			fg = "white",
			font = TITLE_FONT
		)
		self._title.pack(
			side = tk.TOP,
			fill = tk.X
		)
		self._view = GameGrid(master)
		self._view.pack()
		self._statusbar = StatusBar(master, height = 120, width = 400)
		self._statusbar.pack()
		self.draw()
		self._statusbar.set_callbacks(self.start_new_game, self.undo_previous_move)
		self._master.bind("<KeyPress>", self.attempt_move)# user interactions (key presses)
	
	def draw(self) -> None:
		""" Redraws any view classes based on the current model state."""
		self._view.redraw(self._model.get_tiles())
		
	def new_tile(self) -> None:
		""" Adds a new tile to the model and redraws. 
		    If the game has been lost with the addition of the new tile,
			then the player should be prompted with the messagebox 
			displaying the LOSS_MESSAGE.
		"""
		self._model.add_tile()
		self.draw()
		if self._model.has_lost():
			messagebox.showinfo(message = LOSS_MESSAGE)# check game lost

	def attempt_move(self, event: tk.Event) -> None:
		""" Attempt a move if the event represents a key press in 'wasd'. 
		    The method should redraw the view, 
			display the appropriate messagebox if the game has been won,
			or create a new tile after 150ms if the game has not been.

		Parameters:
		    event: The keypress event.
		"""
		if self._model.attempt_move(event.char):
				self.draw()
				self._statusbar.redraw_infos(self._model._score, self._model._undo_time)
				if self._model.has_won():
					messagebox.showinfo(message = WIN_MESSAGE)# check game won
				else:
					self._master.after(NEW_TILE_DELAY, self.new_tile)# draw a new tile
	
	def undo_previous_move(self) -> None:
		""" A handler for when the 'Undo' button is pressed in the status bar. """
		self._model.use_undo()
		self._statusbar.redraw_infos(self._model._score, self._model._undo_time)
		self.draw()

	def start_new_game(self) -> None:
		""" A handler for when the 'New Game' button is pressed in the status bar."""
		self._model.new_game()
		self._statusbar.redraw_infos(0, MAX_UNDOS)
		self.draw()


def play_game(root):
	""" Makes the game start. 

	Parameters:
	    root: The root widget of the game.
	"""
	game = Game(root)

if __name__ == '__main__':
	root = tk.Tk()
	play_game(root)
	root.mainloop()
