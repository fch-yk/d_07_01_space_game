import asyncio
import curses
import itertools
import os
import random
import statistics
import time

from physics import update_speed
from curses_tools import get_frame_size, read_controls, draw_frame
from obstacles import Obstacle, show_obstacles

coroutines = []
obstacles = []


async def sleep(tics=1):
    for __ in range(tics):
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, trash_frames, max_column):
    while True:
        column = random.randint(0, max_column)
        frame = random.choice(trash_frames)
        coroutines.append(fly_garbage(canvas, column, frame))
        await sleep(10)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)
    rows_size, columns_size = get_frame_size(garbage_frame)
    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        obstacle = Obstacle(row, column, rows_size, columns_size)
        obstacles.append(obstacle)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        obstacles.remove(obstacle)
        row += speed


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
    rocket_central_column = statistics.median(
        list(range(1, rocket_columns + 1))
    )

    row_speed = column_speed = 0

    for rocket_frame in itertools.cycle(rocket_frames):
        draw_frame(canvas, start_row, start_column, rocket_frame)
        await asyncio.sleep(0)
        rows_direction, columns_direction, space_pressed = read_controls(
            canvas
        )

        draw_frame(canvas, start_row, start_column, rocket_frame, True)

        row_speed, column_speed = update_speed(
            row_speed,
            column_speed,
            rows_direction,
            columns_direction,
            row_speed_limit=4,
            column_speed_limit=4
        )

        start_row = round(start_row + row_speed)
        start_column = round(start_column + column_speed)

        if start_row < 1:
            start_row = max(start_row, 1)
        if start_row > max_rocket_row:
            start_row = min(start_row, max_rocket_row)

        if start_column < 1:
            start_column = max(start_column, 1)
        if start_column > max_rocket_column:
            start_column = min(start_column, max_rocket_column)

        if space_pressed:
            fire_start_column = start_column + rocket_central_column - 1
            coroutines.append(fire(canvas, start_row, fire_start_column, -1))


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


async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)

    '''Method getmaxyx returns height and width:
    https://docs.python.org/2/library/curses.html#curses.window.getmaxyx)'''
    canvas_height, canvas_width = canvas.getmaxyx()
    max_row = canvas_height - 1
    max_column = canvas_width - 1

    rocket_frames = []
    frames_folder_name = 'frames/rocket'
    files_names = os.listdir(frames_folder_name)
    for file_name in files_names:
        file_path = os.path.join(frames_folder_name, file_name)
        with open(file_path, 'r') as frame_file:
            frame = frame_file.read()
            for __ in range(2):
                rocket_frames.append(frame)

    trash_frames = []
    frames_folder_name = 'frames/trash'
    files_names = os.listdir(frames_folder_name)
    for file_name in files_names:
        file_path = os.path.join(frames_folder_name, file_name)
        with open(file_path, 'r') as frame_file:
            frame = frame_file.read()
            trash_frames.append(frame)

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

    min_game_area_row = min_game_area_column = 1
    max_game_area_row = max_row - 1
    max_game_area_column = max_column - 1
    for __ in range(stars_number):
        row = random.randint(min_game_area_row, max_game_area_row)
        column = random.randint(min_game_area_column, max_game_area_column)
        symbol = random.choice('+*.:')
        min_offset_tics = 20
        max_offset_tics = 40
        offset_tics = random.randint(min_offset_tics, max_offset_tics)
        coroutines.append(blink(canvas, row, column, offset_tics, symbol))

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

    coroutines.append(
        fill_orbit_with_garbage(canvas, trash_frames, max_column)
    )

    coroutines.append(show_obstacles(canvas, obstacles))

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
