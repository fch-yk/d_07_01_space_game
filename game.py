import asyncio
import curses
import itertools
import random
import time

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


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


async def animate_spaceship(canvas, start_row, start_column, rocket_frames):
    for rocket_frame in itertools.cycle(rocket_frames):
        draw_frame(canvas, start_row, start_column, rocket_frame)
        canvas.refresh()
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, rocket_frame, True)
        canvas.refresh()


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
    max_row, max_column = canvas.getmaxyx()
    max_row -= 2
    max_column -= 2

    rocket_frames = []
    with open('frames/rocket_frame_1.txt', 'r') as frame_file:
        rocket_frames.append(frame_file.read())
    with open('frames/rocket_frame_2.txt', 'r') as frame_file:
        rocket_frames.append(frame_file.read())

    rocket_start_row = max_row // 2 - 4
    rocket_start_column = max_column // 2 - 2
    rocket_coroutine = animate_spaceship(
        canvas,
        rocket_start_row,
        rocket_start_column,
        rocket_frames
    )

    max_symbols = max_row * max_column
    min_stars_number = max_symbols // 70
    max_stars_number = max_symbols // 60
    stars_number = random.randint(min_stars_number, max_stars_number)

    coroutines = []
    for __ in range(stars_number):
        row = random.randint(1, max_row)
        column = random.randint(1, max_column)
        symbol = random.choice('+*.:')
        coroutines.append(blink(canvas, row, column, symbol))

    coroutines.append(rocket_coroutine)
    coroutines.append(fire(canvas, max_row // 2, max_column // 2, -1))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break

        canvas.refresh()

        rows_direction, columns_direction, __ = read_controls(canvas)
        time.sleep(0.1)
        if rows_direction != 0 or columns_direction != 0:
            coroutines.remove(rocket_coroutine)
            for rocket_frame in rocket_frames:
                draw_frame(
                    canvas,
                    rocket_start_row,
                    rocket_start_column,
                    rocket_frame, True
                )
            rocket_start_row += rows_direction
            rocket_start_column += columns_direction
            rocket_coroutine = animate_spaceship(
                canvas,
                rocket_start_row,
                rocket_start_column,
                rocket_frames
            )
            coroutines.append(rocket_coroutine)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
