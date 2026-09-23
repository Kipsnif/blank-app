import random
import time

import streamlit as st


st.set_page_config(page_title="Color Puzzle", page_icon="🎨", layout="centered")

BOARD_SIZE = 8
PRIMARY_COLORS = ("Yellow", "Red", "Blue")
PRIMARY_RGB = {
    "Yellow": (246, 196, 64),
    "Red": (224, 69, 64),
    "Blue": (52, 104, 220),
}
SECONDARY_RGB = {
    "Orange": (235, 132, 45),
    "Green": (83, 157, 91),
    "Purple": (133, 91, 174),
}
HYBRID_COLORS = {
    frozenset(("Yellow", "Red")): "Orange",
    frozenset(("Yellow", "Blue")): "Green",
    frozenset(("Red", "Blue")): "Purple",
}
SECONDARY_COLORS = tuple(SECONDARY_RGB)
ALL_COLORS = PRIMARY_COLORS + SECONDARY_COLORS


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
    st.session_state.goals = {
        color: random.randint(5, 20) for color in SECONDARY_COLORS
    }
    st.session_state.counts = {color: 0 for color in SECONDARY_COLORS}
    st.session_state.message = "Choose a source color, then place it on a different tile."
    st.session_state.pending_move = None


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
        replacements = [
            random.choice(PRIMARY_COLORS)
            for _ in range(BOARD_SIZE - len(remaining))
        ]
        values = replacements + remaining
        for row in range(BOARD_SIZE):
            st.session_state.board[row][column] = values[row]


def tile_rgb(color):
    if color in PRIMARY_RGB:
        return PRIMARY_RGB[color]
    return SECONDARY_RGB[color]


def render_board(interactive=True):
    for row in range(BOARD_SIZE):
        columns = st.columns(BOARD_SIZE)
        for column in range(BOARD_SIZE):
            color = st.session_state.board[row][column]
            columns[column].markdown(
                f'<div class="board-tile" style="background:{rgb_css(tile_rgb(color))}"></div>',
                unsafe_allow_html=True,
            )
            if interactive:
                is_primary = color in PRIMARY_COLORS
                if columns[column].button(
                    "Place" if is_primary else "Settled",
                    key=f"tile_{row}_{column}",
                    disabled=not is_primary,
                    use_container_width=True,
                ):
                    st.session_state.pending_move = (row, column)
                    st.rerun()


def resolve_move(row, column):
    base_color = st.session_state.board[row][column]
    selected_color = st.session_state.selected_color
    if base_color not in PRIMARY_COLORS:
        st.session_state.message = "Settled secondary colors cannot be changed."
        return
    if base_color == selected_color:
        st.session_state.message = "Choose one of the other two colors to make a hybrid."
        return

    hybrid_color = HYBRID_COLORS[frozenset((base_color, selected_color))]
    tiles = connected_tiles(row, column, base_color)
    for tile_row, tile_column in tiles:
        st.session_state.board[tile_row][tile_column] = hybrid_color

    animation_slot = st.empty()
    with animation_slot.container():
        render_board(interactive=False)
    time.sleep(0.45)
    animation_slot.empty()

    goal = st.session_state.goals.get(hybrid_color)
    if goal is None or st.session_state.counts[hybrid_color] >= goal:
        st.session_state.message = (
            f"{hybrid_color} is full for this game, so the connected tiles stay on the board."
        )
        return

    st.session_state.counts[hybrid_color] += len(tiles)
    for tile_row, tile_column in tiles:
        st.session_state.board[tile_row][tile_column] = None
    drop_tiles()
    st.session_state.message = (
        f"{len(tiles)} connected tile{'s' if len(tiles) != 1 else ''} became "
        f"{hybrid_color.lower()} and cleared."
    )


def valid_state():
    board = st.session_state.get("board")
    return (
        isinstance(board, list)
        and len(board) == BOARD_SIZE
        and all(
            isinstance(row, list)
            and len(row) == BOARD_SIZE
            and all(color in ALL_COLORS for color in row)
            for row in board
        )
        and isinstance(st.session_state.get("goals"), dict)
        and set(st.session_state.goals) == set(SECONDARY_COLORS)
    )


if not valid_state():
    reset_game()
else:
    if "selected_color" not in st.session_state or st.session_state.selected_color not in PRIMARY_COLORS:
        st.session_state.selected_color = "Red"
    if "counts" not in st.session_state:
        st.session_state.counts = {color: 0 for color in SECONDARY_COLORS}
    if "message" not in st.session_state:
        st.session_state.message = "Choose a source color, then place it on a different tile."
    if "pending_move" not in st.session_state:
        st.session_state.pending_move = None

st.markdown(
    """
    <style>
    .board-tile { height: 34px; border-radius: 6px; border: 1px solid rgba(0, 0, 0, 0.14); margin-bottom: 3px; }
    .palette-swatch { height: 28px; border-radius: 7px; border: 1px solid rgba(0, 0, 0, 0.14); margin-bottom: 5px; }
    .score { background: #f4f1e8; border-radius: 8px; padding: 9px 8px; text-align: center; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Color Puzzle")
st.caption("Blend a source color into a connected group, then clear it from the board.")

if st.session_state.pending_move is not None:
    pending_row, pending_column = st.session_state.pending_move
    st.session_state.pending_move = None
    resolve_move(pending_row, pending_column)

score_columns = st.columns(3)
for score_column, color in zip(score_columns, SECONDARY_COLORS):
    score_column.markdown(
        f'<div class="score"><strong>{color}</strong><br>'
        f'{st.session_state.counts[color]} / {st.session_state.goals[color]}</div>',
        unsafe_allow_html=True,
    )

st.write("")
render_board()

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
st.button("Reset board", on_click=reset_game, use_container_width=True)
