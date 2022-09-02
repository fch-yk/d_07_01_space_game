import asyncio
import curses
import itertools
import os
import random
import statistics
import time

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def get_frame_size(text):
    """Calculate size of multiline text fragment,
    return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing
    if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of
            # the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(
        canvas,
        start_row,
        start_column,
        max_row,
        max_column,
        rocket_frames):
    rocket_rows, rocket_columns = get_frame_size(rocket_frames[0])
    max_rocket_row = max_row - rocket_rows
    max_rocket_column = max_column - rocket_columns

    for rocket_frame in itertools.cycle(rocket_frames):
        draw_frame(canvas, start_row, start_column, rocket_frame)
        rows_direction, columns_direction, __ = read_controls(canvas)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, rocket_frame, True)

        start_row += rows_direction
        start_column += columns_direction
        start_row = (
            max(start_row, 1) if rows_direction < 0
            else min(start_row, max_rocket_row)
        )
        start_column = (
            max(start_column, 1) if columns_direction < 0
            else min(start_column, max_rocket_column)
        )


async def fire(
    canvas,
    start_row,
    start_column,
    rows_speed=-0.3,
    columns_speed=0
):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        sleeps_number = random.randint(20, 40)
        for __ in range(sleeps_number):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for __ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for __ in range(5):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for __ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    '''Method getmaxyx returns height and width:
    https://docs.python.org/2/library/curses.html#curses.window.getmaxyx)'''
    canvas_height, canvas_width = canvas.getmaxyx()
    max_row = canvas_height - 1
    max_column = canvas_width - 1

    rocket_frames = []
    frames_folder_name = 'frames'
    files_names = os.listdir(frames_folder_name)
    for file_name in files_names:
        file_path = os.path.join(frames_folder_name, file_name)
        with open(file_path, 'r') as frame_file:
            frame = frame_file.read()
            for __ in range(2):
                rocket_frames.append(frame)

    first_row = first_column = 0
    central_row = int(statistics.mean([first_row, max_row]))
    central_column = int(statistics.mean([first_column, max_column]))

    max_symbols = max_row * max_column
    min_stars_ratio = 0.02
    max_stars_ratio = 0.04
    stars_number = random.randint(
        int(max_symbols * min_stars_ratio),
        int(max_symbols * max_stars_ratio)
    )

    coroutines = []
    min_game_area_row = min_game_area_column = 1
    max_game_area_row = max_row - 1
    max_game_area_column = max_column - 1
    for __ in range(stars_number):
        row = random.randint(min_game_area_row, max_game_area_row)
        column = random.randint(min_game_area_column, max_game_area_column)
        symbol = random.choice('+*.:')
        coroutines.append(blink(canvas, row, column, symbol))

    coroutines.append(
        animate_spaceship(
            canvas,
            central_row,
            central_column,
            max_row,
            max_column,
            rocket_frames
        )
    )
    coroutines.append(fire(canvas, central_row, central_column, -1))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
