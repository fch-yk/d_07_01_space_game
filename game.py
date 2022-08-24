import asyncio
import curses
import random
import time


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
    row = 5
    canvas.border()
    curses.curs_set(False)
    max_row, max_column = canvas.getmaxyx()
    max_symbols = max_row * max_column
    min_stars_number = max_symbols // 30
    max_stars_number = max_symbols // 20
    stars_number = random.randint(min_stars_number, max_stars_number)
    max_row -= 2
    max_column -= 2
    coroutines = []
    coroutines.append(fire(canvas, max_row // 2, max_column // 2, -1))
    for __ in range(stars_number):
        row = random.randint(1, max_row)
        column = random.randint(1, max_column)
        symbol = random.choice('+*.:')
        coroutines.append(blink(canvas, row, column, symbol))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
