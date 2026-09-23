import streamlit as st


st.set_page_config(page_title="Color Puzzle", page_icon="🎨", layout="centered")

COLORS = {
	"Red": (235, 68, 68),
	"Green": (64, 180, 105),
	"Blue": (68, 125, 235),
}
SOLUTION = [
	["Red", "Red", "Blue"],
	["Green", "Blue", "Blue"],
	["Red", "Green", "Green"],
]


def average_color(color_names):
	channels = zip(*(COLORS[color_name] for color_name in color_names))
	return tuple(sum(channel) // len(color_names) for channel in channels)


def color_css(rgb):
	return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def target_colors():
	rows = [average_color(row) for row in SOLUTION]
	columns = [average_color([SOLUTION[row][column] for row in range(3)]) for column in range(3)]
	return rows, columns


def reset_game():
	st.session_state.board = [[None for _ in range(3)] for _ in range(3)]
	st.session_state.selected_color = "Red"
	st.session_state.locked_rows = set()
	st.session_state.locked_columns = set()


def board_is_ready():
	return all(cell is not None for row in st.session_state.board for cell in row)


def update_locks():
	row_targets, column_targets = target_colors()
	for row_index, row in enumerate(st.session_state.board):
		if row_index not in st.session_state.locked_rows and None not in row:
			if average_color(row) == row_targets[row_index]:
				st.session_state.locked_rows.add(row_index)

	for column_index in range(3):
		column = [st.session_state.board[row][column_index] for row in range(3)]
		if column_index not in st.session_state.locked_columns and None not in column:
			if average_color(column) == column_targets[column_index]:
				st.session_state.locked_columns.add(column_index)


if "board" not in st.session_state:
	reset_game()

row_targets, column_targets = target_colors()

st.markdown(
	"""
	<style>
	.puzzle-shell { max-width: 640px; margin: 0 auto; }
	.target-label { color: #687080; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; text-align: center; margin-bottom: 0.35rem; }
	.target-swatch { height: 22px; border-radius: 6px; border: 1px solid rgba(0, 0, 0, 0.12); margin-bottom: 0.45rem; }
	.row-target { display: flex; align-items: center; justify-content: center; height: 74px; }
	.tile { height: 74px; border-radius: 8px; border: 1px solid rgba(0, 0, 0, 0.12); }
	.tile-empty { background: #ffffff; }
	.tile-locked { box-shadow: inset 0 0 0 3px #1f2937; }
	.legend { color: #687080; font-size: 0.9rem; text-align: center; margin: 0.5rem 0 1rem; }
	</style>
	""",
	unsafe_allow_html=True,
)

st.title("Color Puzzle")
st.caption("Fill the grid so every row and column matches its target color.")

with st.container():
	st.markdown('<div class="puzzle-shell">', unsafe_allow_html=True)
	target_columns = st.columns([0.7, 1, 1, 1])
	target_columns[0].markdown('<div class="target-label">Rows</div>', unsafe_allow_html=True)
	for column_index, target in enumerate(column_targets):
		target_columns[column_index + 1].markdown(
			f'<div class="target-label">{column_index + 1}</div><div class="target-swatch" style="background:{color_css(target)}"></div>',
			unsafe_allow_html=True,
		)

	for row_index in range(3):
		grid_columns = st.columns([0.7, 1, 1, 1])
		row_status = "Locked" if row_index in st.session_state.locked_rows else f"{row_index + 1}"
		grid_columns[0].markdown(
			f'<div class="row-target"><div><div class="target-label">{row_status}</div><div class="target-swatch" style="background:{color_css(row_targets[row_index])}"></div></div></div>',
			unsafe_allow_html=True,
		)
		for column_index in range(3):
			cell = st.session_state.board[row_index][column_index]
			is_locked = row_index in st.session_state.locked_rows or column_index in st.session_state.locked_columns
			background = color_css(COLORS[cell]) if cell else "#ffffff"
			classes = "tile tile-locked" if is_locked else "tile tile-empty"
			grid_columns[column_index + 1].markdown(
				f'<div class="{classes}" style="background:{background}"></div>',
				unsafe_allow_html=True,
			)
			if grid_columns[column_index + 1].button(
				f"Place {row_index + 1},{column_index + 1}",
				key=f"tile_{row_index}_{column_index}",
				disabled=is_locked,
				use_container_width=True,
			):
				st.session_state.board[row_index][column_index] = st.session_state.selected_color
				update_locks()
				st.rerun()
	st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.subheader("Choose a color")
palette = st.columns(3)
for palette_column, color_name in zip(palette, COLORS):
	selected = color_name == st.session_state.selected_color
	if palette_column.button(
		f"{'● ' if selected else ''}{color_name}",
		key=f"palette_{color_name}",
		type="primary" if selected else "secondary",
		use_container_width=True,
	):
		st.session_state.selected_color = color_name
		st.rerun()

locked_count = len(st.session_state.locked_rows) + len(st.session_state.locked_columns)
if locked_count:
	st.success(f"{locked_count} line{'s' if locked_count != 1 else ''} locked in.")
if board_is_ready() and locked_count == 6:
	st.balloons()
	st.success("Puzzle complete!")

st.button("Reset puzzle", on_click=reset_game, use_container_width=True)
