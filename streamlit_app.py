import random

import streamlit as st


st.set_page_config(page_title="Color Puzzle", page_icon="⬡", layout="centered")

RADIUS = 3
COLORS = ("red", "green", "blue")
COLOR_LABELS = {"red": "Red", "green": "Green", "blue": "Blue"}
COLOR_MARKS = {"red": "🔴", "green": "🟢", "blue": "🔵"}
EMPTY_MARK = "·"


def board_coordinates():
	return [
		(q, r)
		for r in range(-RADIUS, RADIUS + 1)
		for q in range(-RADIUS, RADIUS + 1)
		if max(abs(q), abs(r), abs(q + r)) <= RADIUS
	]


def neighbors(coordinate):
	q, r = coordinate
	directions = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))
	return [(q + dq, r + dr) for dq, dr in directions]


def make_puzzle(seed):
	rng = random.Random(seed)
	coordinates = board_coordinates()
	solution = {coordinate: rng.choice(COLORS) for coordinate in coordinates}
	clue_coordinates = [
		coordinate
		for coordinate in coordinates
		if max(abs(coordinate[0]), abs(coordinate[1]), abs(sum(coordinate))) <= 2
	]
	rng.shuffle(clue_coordinates)
	clue_coordinates = clue_coordinates[:8]
	clues = {
		coordinate: {
			"color": solution[coordinate],
			"count": sum(
				solution.get(neighbor) == solution[coordinate]
				for neighbor in neighbors(coordinate)
			),
		}
		for coordinate in clue_coordinates
	}
	return solution, clues


def start_puzzle():
	seed = st.session_state.get("seed", 0) + 1
	solution, clues = make_puzzle(seed)
	st.session_state.seed = seed
	st.session_state.solution = solution
	st.session_state.clues = clues
	st.session_state.board = {
		coordinate: None
		for coordinate in board_coordinates()
		if coordinate not in clues
	}
	st.session_state.feedback = ""


def cycle_color(coordinate):
	current = st.session_state.board[coordinate]
	next_index = -1 if current is None else COLORS.index(current)
	st.session_state.board[coordinate] = COLORS[(next_index + 1) % len(COLORS)]
	st.session_state.feedback = ""


def check_puzzle():
	board = dict(st.session_state.board)
	board.update(
		{coordinate: clue["color"] for coordinate, clue in st.session_state.clues.items()}
	)
	if any(color is None for color in st.session_state.board.values()):
		st.session_state.feedback = "Vul eerst alle lege hexagonen in."
		return

	incorrect = []
	for coordinate, clue in st.session_state.clues.items():
		matching = sum(
			board.get(neighbor) == clue["color"]
			for neighbor in neighbors(coordinate)
		)
		if matching != clue["count"]:
			incorrect.append(coordinate)

	if incorrect:
		st.session_state.feedback = (
			f"Nog niet goed: {len(incorrect)} clue{'s' if len(incorrect) != 1 else ''} "
			"klopt niet."
		)
	else:
		st.session_state.feedback = "Goed gedaan. Alle clues kloppen!"


if "clues" not in st.session_state:
	start_puzzle()

st.title("Color Puzzle")
st.caption("Kleur de zes buren van elke clue zo dat het cijfer precies klopt.")

st.markdown(
	"""
	<style>
	div.stButton > button {
		min-height: 58px;
		padding: 0;
		border: 1px solid #c9c4b8;
		border-radius: 0;
		clip-path: polygon(25% 4%, 75% 4%, 98% 50%, 75% 96%, 25% 96%, 2% 50%);
		font-size: 1.25rem;
	}
	div.stButton > button:disabled {
		opacity: 1;
		color: #1f2933;
		background: #f1eee7;
	}
	</style>
	""",
	unsafe_allow_html=True,
)

legend = "  ".join(f"{COLOR_MARKS[color]} {COLOR_LABELS[color]}" for color in COLORS)
st.markdown(legend)

for row in range(-RADIUS, RADIUS + 1):
	row_coordinates = [
		coordinate for coordinate in board_coordinates() if coordinate[1] == row
	]
	left_padding = abs(row) if row < 0 else RADIUS - row
	columns = st.columns(left_padding + len(row_coordinates))
	for column in columns[:left_padding]:
		column.write("")
	for column, coordinate in zip(columns[left_padding:], row_coordinates):
		if coordinate in st.session_state.clues:
			clue = st.session_state.clues[coordinate]
			label = f"{COLOR_MARKS[clue['color']]} {clue['count']}"
			column.button(label, key=f"clue_{coordinate}", disabled=True)
		else:
			color = st.session_state.board[coordinate]
			label = EMPTY_MARK if color is None else COLOR_MARKS[color]
			if column.button(label, key=f"cell_{coordinate}"):
				cycle_color(coordinate)
				st.rerun()

action_columns = st.columns(2)
if action_columns[0].button("Check puzzle", type="primary", use_container_width=True):
	check_puzzle()
if action_columns[1].button("New puzzle", use_container_width=True):
	start_puzzle()
	st.rerun()

if st.session_state.feedback:
	st.info(st.session_state.feedback)
