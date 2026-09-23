import streamlit as st
import random


st.set_page_config(page_title="Color Puzzle", page_icon="🎨", layout="centered")

BOARD_SIZE = 5
GOAL = 10
PRIMARY_COLORS = ("Yellow", "Red", "Blue")
PRIMARY_RGB = {
	"Yellow": (246, 196, 64),
	"Red": (224, 69, 64),
	"Blue": (52, 104, 220),
}
HYBRID_COLORS = {
	frozenset(("Yellow", "Red")): ("Orange", (235, 132, 45)),
	frozenset(("Yellow", "Blue")): ("Green", (83, 157, 91)),
	frozenset(("Red", "Blue")): ("Purple", (133, 91, 174)),
}


def rgb_css(rgb):
	return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def new_board():
	return [
		[random.choice(PRIMARY_COLORS) for _ in range(BOARD_SIZE)]
		for _ in range(BOARD_SIZE)
	]


def reset_game():
	st.session_state.board = new_board()
	st.session_state.selected_color = "Red"
	st.session_state.orange_count = 0
	st.session_state.message = "Choose a color, then place it on a different color tile."


def connected_tiles(row, column, color):
	found = set()
	pending = [(row, column)]
	while pending:
		current = pending.pop()
		if current in found:
			continue
		current_row, current_column = current
		if not (0 <= current_row < BOARD_SIZE and 0 <= current_column < BOARD_SIZE):
			continue
		if st.session_state.board[current_row][current_column] != color:
			continue
		found.add(current)
		pending.extend(
			(
				(current_row - 1, current_column),
				(current_row + 1, current_column),
				(current_row, current_column - 1),
				(current_row, current_column + 1),
			)
		)
	return found


def drop_tiles():
	for column in range(BOARD_SIZE):
		remaining = [
			st.session_state.board[row][column]
			for row in range(BOARD_SIZE)
			if st.session_state.board[row][column] is not None
		]
		replacements = [random.choice(PRIMARY_COLORS) for _ in range(BOARD_SIZE - len(remaining))]
		values = replacements + remaining
		for row in range(BOARD_SIZE):
			st.session_state.board[row][column] = values[row]


def play_tile(row, column):
	base_color = st.session_state.board[row][column]
	selected_color = st.session_state.selected_color
	if base_color == selected_color:
		st.session_state.message = "Choose one of the other two colors to make a hybrid."
		return

	hybrid_name, _ = HYBRID_COLORS[frozenset((base_color, selected_color))]
	tiles = connected_tiles(row, column, base_color)
	for tile_row, tile_column in tiles:
		st.session_state.board[tile_row][tile_column] = None
	drop_tiles()
	if hybrid_name == "Orange":
		st.session_state.orange_count += len(tiles)
	st.session_state.message = f"{len(tiles)} connected {base_color.lower()} tile{'s' if len(tiles) != 1 else ''} became {hybrid_name.lower()} and cleared."


board = st.session_state.get("board")
valid_board = (
	isinstance(board, list)
	and len(board) == BOARD_SIZE
	and all(
		isinstance(row, list)
		and len(row) == BOARD_SIZE
		and all(color in PRIMARY_COLORS for color in row)
		for row in board
	)
)
if not valid_board:
	reset_game()
else:
	if "selected_color" not in st.session_state or st.session_state.selected_color not in PRIMARY_COLORS:
		st.session_state.selected_color = "Red"
	if "orange_count" not in st.session_state:
		st.session_state.orange_count = 0
	if "message" not in st.session_state:
		st.session_state.message = "Choose a color, then place it on a different color tile."

st.markdown(
	"""
	<style>
	.board-tile { height: 48px; border-radius: 8px; border: 1px solid rgba(0, 0, 0, 0.14); margin-bottom: 4px; }
	.palette-swatch { height: 30px; border-radius: 7px; border: 1px solid rgba(0, 0, 0, 0.14); margin-bottom: 5px; }
	.score { background: #f4f1e8; border-radius: 8px; padding: 10px 14px; text-align: center; }
	</style>
	""",
	unsafe_allow_html=True,
)

st.title("Color Puzzle")
st.caption("Blend a source color into a connected group, then clear it from the board.")

score_column, goal_column = st.columns(2)
score_column.markdown(
	f'<div class="score"><strong>Orange cleared</strong><br>{st.session_state.orange_count} / {GOAL}</div>',
	unsafe_allow_html=True,
)
goal_column.markdown(
	'<div class="score"><strong>Selected source</strong><br>'
	f'<span style="color:{rgb_css(PRIMARY_RGB[st.session_state.selected_color])}">●</span> {st.session_state.selected_color}</div>',
	unsafe_allow_html=True,
)

st.write("")
for row in range(BOARD_SIZE):
	columns = st.columns(BOARD_SIZE)
	for column in range(BOARD_SIZE):
		color = st.session_state.board[row][column]
		columns[column].markdown(
			f'<div class="board-tile" style="background:{rgb_css(PRIMARY_RGB[color])}"></div>',
			unsafe_allow_html=True,
		)
		if columns[column].button(
			"Place",
			key=f"tile_{row}_{column}",
			use_container_width=True,
		):
			play_tile(row, column)
			st.rerun()

st.divider()
st.subheader("Choose a source color")
palette = st.columns(3)
for palette_column, color in zip(palette, PRIMARY_COLORS):
	palette_column.markdown(
		f'<div class="palette-swatch" style="background:{rgb_css(PRIMARY_RGB[color])}"></div>',
		unsafe_allow_html=True,
	)
	if palette_column.button(
		color,
		key=f"color_{color}",
		type="primary" if st.session_state.selected_color == color else "secondary",
		use_container_width=True,
	):
		st.session_state.selected_color = color
		st.rerun()

st.info(st.session_state.message)
if st.session_state.orange_count >= GOAL:
	st.success("Goal reached: you cleared enough orange tiles!")
st.button("Reset board", on_click=reset_game, use_container_width=True)
