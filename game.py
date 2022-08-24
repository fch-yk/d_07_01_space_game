import asyncio
import curses
import random
import time


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for __ in range(20):
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
    corutines = []
    for __ in range(stars_number):
        row = random.randint(1, max_row)
        column = random.randint(1, max_column)
        symbol = random.choice('+*.:')
        corutines.append(blink(canvas, row, column, symbol))

    while True:
        for corutine in corutines:
            corutine.send(None)
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
